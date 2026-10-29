"""Add shirt colors to an existing Printify product and re-publish it to Shopify.

Usage:
    python3 printify/add_colors.py <product_id> <color>[:<ink>] [<color>[:<ink>] ...]

<ink> picks the print area whose artwork file name contains "-<ink>" (e.g. "Moss:white" uses
the area printing 04-odysseus-layover-white.png). Without it, the product must have a single
print area. New colors get the product's base price, plus the 2XL upcharge.
"""

import os
import sys

from create_products import Printify, TEE_SIZES, XXL_UPCHARGE


def main():
    product_id, *specs = sys.argv[1:]
    wanted = dict((s.split(":") + [None])[:2] for s in specs)
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")
    path = f"/shops/{shop['id']}/products/{product_id}.json"
    p = api.get(path)
    catalog = api.get(f"/catalog/blueprints/{p['blueprint_id']}/print_providers/{p['print_provider_id']}/variants.json")
    options = {v["id"]: v["options"] for v in catalog["variants"]}

    missing = set(wanted) - {o.get("color") for o in options.values()}
    if missing:
        sys.exit(f"Not offered by this provider: {sorted(missing)}")
    base = min(v["price"] for v in p["variants"] if v["is_enabled"] and options[v["id"]].get("size") != "2XL")

    def area_for(ink):
        if ink is None:
            if len(p["print_areas"]) != 1:
                sys.exit("Product has several print areas; give each color an :<ink>")
            return p["print_areas"][0]
        names = lambda a: " ".join(i["name"] for ph in a["placeholders"] for i in ph["images"])
        return next(a for a in p["print_areas"] if f"-{ink}" in names(a))

    added = {}
    for vid, opt in options.items():
        color, size = opt.get("color"), opt.get("size")
        if color in wanted and (size in TEE_SIZES or not size):
            added[vid] = area_for(wanted[color])
    for area in p["print_areas"]:
        area["variant_ids"] = [v for v in area["variant_ids"] if v not in added]
    for vid, area in added.items():
        area["variant_ids"].append(vid)

    variants = [{
        "id": v["id"],
        "is_enabled": v["is_enabled"] or v["id"] in added,
        "price": (base + (XXL_UPCHARGE if options[v["id"]].get("size") == "2XL" else 0)) if v["id"] in added else v["price"],
    } for v in p["variants"]]
    areas = [{"variant_ids": a["variant_ids"],
              "placeholders": [ph for ph in a["placeholders"] if ph.get("images")]}
             for a in p["print_areas"]]
    api.call("PUT", path, json={"variants": variants, "print_areas": areas})
    api.post(f"{path[:-5]}/publish.json", {
        "title": False, "description": False, "images": True, "variants": True,
        "tags": False, "keyFeatures": False, "shipping_template": False,
    })

    p = api.get(path)
    enabled = [v for v in p["variants"] if v["is_enabled"]]
    colors = sorted({options[v["id"]]["color"] for v in enabled})
    profit = [(v["price"] - v["cost"]) / 100 for v in enabled]
    print(f"{p['title']}: {len(enabled)} variants, colors {colors}, profit ${min(profit):.2f}-${max(profit):.2f}")


if __name__ == "__main__":
    main()
