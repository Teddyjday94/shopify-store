"""Offer more dark colors on the hoodies whose art is made for dark fabric.

Every color is already listed on a Printify product and covered by its print area, so adding one only means
enabling its S-2XL variants (at the hoodie's current price) and publishing the variants to Shopify. Images are
not republished, so the labeled back-first photos in Shopify stay; photos for the new colors are added after
with media_plan.py.

Usage: python3 printify/add_hoodie_colors.py [--apply] [--only TITLE] [--done FILE]
"""

import argparse
import json
import os
import time

from create_products import Printify

SIZES = {"S", "M", "L", "XL", "2XL"}
# tag -> colors to offer (on top of what each hoodie already has)
PLAN = {
    "horror collection": ["Navy", "Maroon", "Dark Chocolate", "Charcoal"],
    "realms": ["Navy", "Maroon", "Dark Chocolate", "Charcoal"],
    "relatable collection": ["Navy", "Maroon", "Forest Green", "Dark Chocolate"],
    "player two": ["Navy", "Maroon", "Forest Green", "Dark Chocolate"],
    "immortalized": ["Navy", "Maroon", "Forest Green", "Dark Chocolate", "Dark Heather"],
    "drop 004": ["Navy", "Maroon", "Forest Green", "Dark Chocolate", "Dark Heather"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--done", default="add_hoodie_colors_done.json")
    args = ap.parse_args()
    done = set(json.load(open(args.done))) if os.path.exists(args.done) else set()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    products, page = [], 1
    while True:
        d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        products += d["data"]
        if page >= d["last_page"]:
            break
        page += 1
    for p in products:
        if not p["title"].endswith("Hoodie") or not (p.get("external") or {}).get("id"):
            continue
        if args.only and p["title"] != args.only:
            continue
        tag = next((t for t in PLAN if t in p["tags"]), None)
        if not tag or p["id"] in done:
            continue
        enabled = [v for v in p["variants"] if v["is_enabled"]]
        price = max(v["price"] for v in enabled)
        have = {v["title"].split(" / ")[0] for v in enabled}
        offered = {v["title"].split(" / ")[0] for v in p["variants"]}
        add = [c for c in PLAN[tag] if c not in have and c in offered]
        missing = [c for c in PLAN[tag] if c not in offered]
        if not add:
            continue
        print(f"{'add ' if args.apply else 'plan'}  {p['title']}: {sorted(have)} + {add}"
              + (f"  (not offered: {missing})" if missing else ""), flush=True)
        if not args.apply:
            continue
        variants = []
        for v in p["variants"]:
            color, size = v["title"].split(" / ")[0], v["title"].split(" / ")[-1]
            on = v["is_enabled"] or (color in add and size in SIZES)
            variants.append({"id": v["id"], "is_enabled": on, "price": price if on and not v["is_enabled"] else v["price"]})
        api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json={"variants": variants})
        for wait in (0, 120, 300, 600):
            time.sleep(wait)
            try:
                api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
                    "title": False, "description": False, "images": False, "variants": True,
                    "tags": False, "keyFeatures": False, "shipping_template": False})
                break
            except RuntimeError as e:
                print(f"      publish refused ({e}); waiting", flush=True)
        else:
            raise SystemExit(f"Printify keeps refusing publishes; stopped at {p['title']}")
        done.add(p["id"])
        json.dump(sorted(done), open(args.done, "w"))
        time.sleep(15)


if __name__ == "__main__":
    main()
