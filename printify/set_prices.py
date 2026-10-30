"""Reprice Printify products to match the storefront, without re-publishing.

Shopify prices are updated directly (productVariantsBulkUpdate); this keeps
Printify's copy in sync so a later publish doesn't revert them.

    python3 printify/set_prices.py          # dry run
    python3 printify/set_prices.py --apply
"""
import os
import sys

from create_products import Printify

# Old price -> new price, in cents. Per-title overrides win over the defaults.
OVERRIDES = {
    "Currently Elsewhere Hoodie": {5200: 4400, 5500: 4700},
}
DEFAULTS = {
    2800: 2400, 3100: 2700,  # Drop 001 tees
    3200: 2600, 3500: 2900,  # Own Lane tees, Odysseus
    3600: 3000, 3900: 3300,  # Drop 002 tees
    5200: 4600, 5500: 4900,  # Own Lane hoodies
    5400: 4600, 5700: 4900,  # Seasonal Depression hoodie
    6800: 5800, 7100: 6100,  # Drop 002 pocketless hoodies
}


def main(apply):
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = api.get("/shops.json")[0]
    page = 1
    while True:
        res = api.get(f"/shops/{shop['id']}/products.json?limit=50&page={page}")
        for p in res["data"]:
            table = OVERRIDES.get(p["title"], DEFAULTS)
            changes = [{"id": v["id"], "price": table[v["price"]]}
                       for v in p["variants"] if v["price"] in table]
            if not changes:
                print(f"skip  {p['title']}")
                continue
            new = sorted({c["price"] for c in changes})
            print(f"{'set ' if apply else 'plan'}  {p['title']}: {len(changes)} variants -> {new}")
            if apply:
                api.call("PUT", f"/shops/{shop['id']}/products/{p['id']}.json", json={"variants": changes})
        if res["current_page"] >= res["last_page"]:
            break
        page += 1


if __name__ == "__main__":
    main("--apply" in sys.argv)
