"""Change prices on a group of products by a fixed amount, without touching artwork or photos.

Selects products whose tags include TAG and whose title ends with SUFFIX, then moves every enabled
variant's price by DELTA cents. Republishes variants only (images: False), so Shopify keeps its media.

Usage:
    python3 printify/reprice.py --tag relatable --suffix Tee --delta -600            # dry run
    python3 printify/reprice.py --tag relatable --suffix Tee --delta -600 --apply
"""

import argparse
import os
import time

from create_products import Printify


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--suffix", required=True)
    ap.add_argument("--delta", type=int, required=True, help="price change in cents, e.g. -600")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    for page in range(1, 8):
        for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]:
            if args.tag not in p["tags"] or not p["title"].endswith(args.suffix):
                continue
            variants = [{"id": v["id"], "is_enabled": v["is_enabled"],
                         "price": v["price"] + args.delta if v["is_enabled"] else v["price"]} for v in p["variants"]]
            before = sorted({v["price"] / 100 for v in p["variants"] if v["is_enabled"]})
            after = sorted({v["price"] / 100 for v in variants if v["is_enabled"]})
            print(f"{'apply' if args.apply else 'plan '} {p['title']}: {before} -> {after}")
            if not args.apply:
                continue
            api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json={"variants": variants})
            api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
                "title": False, "description": False, "images": False, "variants": True,
                "tags": False, "keyFeatures": False, "shipping_template": False})
            time.sleep(20)  # stay under Printify's publish rate limit


if __name__ == "__main__":
    main()
