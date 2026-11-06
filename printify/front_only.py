"""Make the Own Lane and Drop 002 tees front-print only, and lower their prices by what the back print cost.

Removing the back print saves about $6.15 (unisex) / $6.57 (women's) per shirt at Printify, so the unisex
tee drops $6 ($30 -> $24, 2XL $33 -> $27) and the women's tee $4 ($30 -> $26, 2XL $33 -> $29), keeping the
profit per shirt about the same. Immortalized, Christmas and all hoodies are left alone.

Usage:
    python3 printify/front_only.py            # dry run
    python3 printify/front_only.py --apply
"""

import argparse
import os
import time

from create_products import Printify

SKIP_TAGS = {"immortalized", "drop 004", "christmas collection"}
DROP = {12: 600, 14: 400}  # blueprint -> price cut in cents (12 unisex Bella 3001, 14 women's)


def targets(api, shop):
    for page in range(1, 8):
        for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]:
            if not p["title"].endswith("Tee") or SKIP_TAGS & set(p["tags"]) or p["blueprint_id"] not in DROP:
                continue
            if any(ph["position"] == "back" and ph["images"] for a in p["print_areas"] for ph in a["placeholders"]):
                yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    for p in targets(api, shop):
        cut = DROP[p["blueprint_id"]]
        areas = [{"variant_ids": a["variant_ids"], "placeholders": [
            {"position": ph["position"], "images": [
                dict(id=i["id"], x=i["x"], y=i["y"], scale=i["scale"], angle=i["angle"]) for i in ph["images"]]}
            for ph in a["placeholders"] if ph["images"] and ph["position"] != "back"]} for a in p["print_areas"]]
        variants = [{"id": v["id"], "is_enabled": v["is_enabled"], "price": v["price"] - cut if v["is_enabled"] else v["price"]}
                    for v in p["variants"]]
        prices = sorted({v["price"] for v in variants if v["is_enabled"]})
        print(f"{'apply' if args.apply else 'plan '} {p['title']}: front only, prices {[x / 100 for x in prices]}")
        if not args.apply:
            continue
        api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json={"print_areas": areas, "variants": variants})
        api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
            "title": False, "description": False, "images": True, "variants": True,
            "tags": False, "keyFeatures": False, "shipping_template": False})
        time.sleep(20)  # stay under Printify's publish rate limit


if __name__ == "__main__":
    main()
