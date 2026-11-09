"""Reprice every published product to a price ending in 7.

Tees $27 and hoodies $37 in every size (2XL included); hats, beanies and phone cases $27; mugs and ornaments
$17. Posters and desk mats keep one price per size, each rounded to a 7 and stepped up when two sizes would
otherwise share a price: posters $17/27/37/47, desk mats $27/37/47.

Updates the price in Printify and publishes only the variants, so Shopify picks up the new prices.

Printify limits how many publishes it accepts in a while, so publishes are paced, a refusal waits and
retries, and every product that reached Shopify is recorded in --done (so a re-run picks up where it stopped,
including a product whose price changed in Printify but was never published).

Usage:
    python3 printify/price_sevens.py            # dry run
    python3 printify/price_sevens.py --apply [--done FILE]
"""

import argparse
import json
import os
import time

from create_products import Printify

FLAT = [("Tee", 2700), ("T-Shirt", 2700), ("Hoodie", 3700), ("Dad Hat", 2700), ("Beanie", 2700),
        ("Trucker Hat", 2700), ("Bucket Hat", 2700), ("Phone Case", 2700), ("Mug", 1700), ("Ornament", 1700)]
BY_SIZE = {"Poster": {2000: 1700, 2400: 2700, 2800: 3700, 3800: 4700},
           "Desk Mat": {2800: 2700, 3000: 3700, 4000: 4700}}


def new_price(title, old):
    for kind, table in BY_SIZE.items():
        if title.endswith(kind):
            return old if old in table.values() else table.get(old)  # already repriced: keep it
    for kind, price in FLAT:
        if title.endswith(kind):
            return price
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--done", default="price_sevens_done.json", help="ids already published at the new price")
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
        if not (p.get("external") or {}).get("id"):
            continue  # never published to the store
        enabled = [v for v in p["variants"] if v["is_enabled"]]
        prices = {v["id"]: new_price(p["title"], v["price"]) for v in enabled}
        # The priciest blanks to print move up a step so they still earn a fair margin: back-printed hoodies
        # (about $29-31 to make) sell for $47, and front-and-back women's tees (about $21-23) for $37.
        top_cost = max(v["cost"] for v in enabled)
        for kind, floor, price in (("Hoodie", 2900, 4700), ("Women's Tee", 2000, 3700)):
            if p["title"].endswith(kind) and top_cost >= floor:
                prices = {i: price for i in prices}
        if None in prices.values():
            print(f"??    {p['title']}: no rule for {sorted({v['price'] for v in enabled})}")
            continue
        priced = all(prices[v["id"]] == v["price"] for v in enabled)
        if priced and (p["id"] in done or not args.apply):
            print(f"same  {p['title']}")
            continue
        low = min(prices[v["id"]] - v["cost"] for v in enabled)
        old = sorted({v["price"] / 100 for v in enabled})
        print(f"{'set ' if args.apply else 'plan'}  {p['title']}: {old} -> {sorted({x / 100 for x in prices.values()})}"
              f"  (min profit ${low / 100:.2f})")
        if not args.apply:
            continue
        if not priced:
            api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json={"variants": [
                {"id": v["id"], "price": prices.get(v["id"], v["price"]), "is_enabled": v["is_enabled"]}
                for v in p["variants"]]})
        for wait in (0, 120, 300, 600, 900):
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
