"""Move the Horror hoodies to Print Geek (largest Gildan 18500 back area, 12.4 x 14 in) with the art filling it.

Each hoodie is recreated on provider 27 with the same title, description, tags, colors and price; its back art
is scaled to fill 97% of the back area (width or height, whichever runs out first) from 3% below the top. The
new product is published, then the old one is deleted (Printify can't change a product's provider in place).

Usage: python3 printify/horror_hoodies_big.py [--apply] [--only TITLE]
"""

import argparse
import os
import time

from create_products import Printify
from fit import placeholder_sizes

BLUEPRINT, PROVIDER = 77, 27
EDGE, TOP = 0.97, 0.03


def place(img, w, h):
    ratio = (img["height"] / img["width"]) * (w / h)   # art height as a fraction of area height, per unit width
    scale = round(min(EDGE, (1 - TOP - 0.01) / ratio), 4)
    return dict(id=img["id"], x=0.5, y=round(TOP + scale * ratio / 2, 4), scale=scale, angle=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    products, page = [], 1
    while True:
        d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        products += d["data"]
        if page >= d["last_page"]:
            break
        page += 1
    w, h = placeholder_sizes(api, BLUEPRINT, PROVIDER)["back"]
    catalog = api.get(f"/catalog/blueprints/{BLUEPRINT}/print_providers/{PROVIDER}/variants.json")["variants"]
    for p in products:
        if not (p["title"].endswith("Hoodie") and "horror collection" in p["tags"]) or p["print_provider_id"] == PROVIDER:
            continue
        if args.only and p["title"] != args.only:
            continue
        old = {(v["title"].split(" / ")[0], v["title"].split(" / ")[-1]): v["price"] for v in p["variants"] if v["is_enabled"]}
        chosen = [v for v in catalog if (v["options"]["color"], v["options"]["size"]) in old]
        back = next(i for a in p["print_areas"] for ph in a["placeholders"] if ph["position"] == "back" for i in ph["images"])
        spot = place(back, w, h)
        print(f"{'make' if args.apply else 'plan'}  {p['title']}: {len(chosen)}/{len(old)} variants, "
              f"art {spot['scale']:.0%} of a {w / 300:.1f}in-wide back", flush=True)
        if not args.apply:
            continue
        new = api.post(f"/shops/{shop}/products.json", {
            "title": p["title"], "description": p["description"], "tags": p["tags"],
            "blueprint_id": BLUEPRINT, "print_provider_id": PROVIDER,
            "variants": [{"id": v["id"], "is_enabled": True,
                          "price": old[(v["options"]["color"], v["options"]["size"])]} for v in chosen],
            "print_areas": [{"variant_ids": [v["id"] for v in chosen],
                             "placeholders": [{"position": "back", "images": [spot]}]}],
        })
        cost = sorted({v["cost"] for v in new["variants"] if v["is_enabled"]})
        print(f"      created {new['id']}, cost ${cost[0] / 100:.2f}-${cost[-1] / 100:.2f}", flush=True)
        api.post(f"/shops/{shop}/products/{new['id']}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True})
        api.call("DELETE", f"/shops/{shop}/products/{p['id']}.json")
        print(f"      deleted old {p['id']}", flush=True)
        time.sleep(20)


if __name__ == "__main__":
    main()
