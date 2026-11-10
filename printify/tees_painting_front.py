"""Make the Legends Never Die (Immortalized) tees front-print only.

These tees carried the painting on the back and a small emblem on the front, which costs a second
print (women's $21.10 vs about $15 one-sided). This moves the painting to the front at the same size
and position it had on the back, drops the emblem, and keeps the price ($27). Shopify photos are
replaced afterwards from the new front mockups (see media_plan.py).

Usage:
    python3 printify/tees_painting_front.py            # dry run
    python3 printify/tees_painting_front.py --apply [--done FILE]
"""

import argparse
import json
import os
import time

from create_products import Printify


def targets(api, shop):
    page, last = 1, 1
    while page <= last:
        data = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        last, page = data["last_page"], page + 1
        for p in data["data"]:
            if not p["title"].endswith("Tee"):
                continue
            pos = {ph["position"] for a in p["print_areas"] for ph in a["placeholders"] if ph["images"]}
            if {"front", "back"} <= pos:
                yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--done", default="tees_front_done.json")
    ap.add_argument("--only", help="title of a single product to do")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    done = set(json.load(open(args.done))) if os.path.exists(args.done) else set()
    for p in targets(api, shop):
        if p["id"] in done or (args.only and p["title"] != args.only):
            continue
        areas = []
        for a in p["print_areas"]:
            back = next(ph for ph in a["placeholders"] if ph["position"] == "back")
            imgs = [dict(id=i["id"], x=i["x"], y=i["y"], scale=i["scale"], angle=i["angle"]) for i in back["images"]]
            areas.append({"variant_ids": a["variant_ids"], "placeholders": [{"position": "front", "images": imgs}]})
        prices = sorted({v["price"] for v in p["variants"] if v["is_enabled"]})
        print(f"{'apply' if args.apply else 'plan '} {p['title']}: painting to front, prices {[x / 100 for x in prices]}", flush=True)
        if not args.apply:
            continue
        api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json={"print_areas": areas})
        for wait in (0, 120, 300, 600):
            time.sleep(wait)
            try:
                api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
                    "title": False, "description": False, "images": False, "variants": False,
                    "tags": False, "keyFeatures": False, "shipping_template": False})
                break
            except Exception as e:  # rate limit: wait and retry
                print("  publish retry:", str(e)[:120], flush=True)
        done.add(p["id"])
        json.dump(sorted(done), open(args.done, "w"))
        time.sleep(15)


if __name__ == "__main__":
    main()
