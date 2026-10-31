"""Rebuild every hoodie on SwiftPOD so it can come in Dark Chocolate (brown); Monster Digital doesn't stock it.

New products are created and published next to the old ones; swapping the Shopify listings over
(handle, SEO, description) and deleting the old products happens afterwards. Pairs are saved to
printify/moved_hoodies.json.

Usage:
    python3 printify/move_hoodies.py            # dry run
    python3 printify/move_hoodies.py --apply
"""

import argparse
import json
import os
from pathlib import Path

from clone_product import build, ink_of
from create_products import Printify

BLUEPRINT, OLD_PROVIDER, NEW_PROVIDER = 77, 29, 39
RENAMED = {"Charcoal": "Dark Heather"}  # SwiftPOD has no Charcoal
BROWN = "Dark Chocolate"
NO_BROWN = {  # black-ink art that wouldn't read on brown
    "Somewhere in a Calmer Place Hoodie", "Balance Hoodie", "Same Chaos Different Day Hoodie"}
OUT = Path(__file__).with_name("moved_hoodies.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    apply = ap.parse_args().apply

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    old_catalog = {v["id"]: v["options"] for v in
                   api.get(f"/catalog/blueprints/{BLUEPRINT}/print_providers/{OLD_PROVIDER}/variants.json")["variants"]}
    moved = json.loads(OUT.read_text()) if OUT.exists() else {}

    for page in (1, 2):
        for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]:
            if p["blueprint_id"] != BLUEPRINT or p["print_provider_id"] != OLD_PROVIDER:
                continue
            if not (p.get("external") or {}).get("id") or p["id"] in moved:
                continue
            src = api.get(f"/shops/{shop}/products/{p['id']}.json")
            colors, prices = {}, {}
            for v in src["variants"]:
                if not v["is_enabled"] or v["id"] not in old_catalog:
                    continue
                color = RENAMED.get(old_catalog[v["id"]]["color"], old_catalog[v["id"]]["color"])
                colors.setdefault(color, ink_of(src, v["id"]))
                prices[(color, old_catalog[v["id"]]["size"])] = v["price"]
            if p["title"] not in NO_BROWN:
                colors[BROWN] = "white" if len(src["print_areas"]) > 1 else None
            base = min(price for (c, s), price in prices.items() if s != "2XL")
            body, missing = build(api, src, BLUEPRINT, NEW_PROVIDER, colors, base,
                                  price_of=lambda c, s: prices.get((c, s)), sizes=["S", "M", "L", "XL", "2XL"])
            print(f"{'make' if apply else 'plan'}  {p['title']}: {sorted(colors)}"
                  + (f" (missing {missing})" if missing else ""))
            if not apply:
                continue
            body.update(title=src["title"], description=src["description"], tags=src["tags"])
            new = api.post(f"/shops/{shop}/products.json", body)
            api.post(f"/shops/{shop}/products/{new['id']}/publish.json", {
                "title": True, "description": True, "images": True, "variants": True,
                "tags": True, "keyFeatures": True, "shipping_template": True,
            })
            cost = [v["cost"] for v in new["variants"] if v["is_enabled"]]
            moved[p["id"]] = {"title": p["title"], "old_shopify": p["external"]["id"], "new_printify": new["id"]}
            OUT.write_text(json.dumps(moved, indent=2))
            print(f"      created {new['id']}, cost ${min(cost) / 100:.2f}-${max(cost) / 100:.2f}")


if __name__ == "__main__":
    main()
