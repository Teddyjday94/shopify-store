"""Swap the artwork on existing Printify products and re-publish them to Shopify.

Usage:
    python3 printify/update_artwork.py <commit> <product_id> <position>=<file> [<position>=<file> ...]

Files are paths under designs/print-drop2 at the given commit of the public GitHub repo.
"""

import os
import sys

from create_products import Printify
from create_drop2 import FULL, RAW


def main():
    commit, product_id, *pairs = sys.argv[1:]
    files = dict(pair.split("=", 1) for pair in pairs)
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")
    path = f"/shops/{shop['id']}/products/{product_id}.json"
    product = api.get(path)

    new_ids = {}
    for position, name in files.items():
        image = api.post("/uploads/images.json", {"file_name": name, "url": RAW.format(commit=commit, name=name)})
        new_ids[position] = image["id"]

    print_areas = []
    for area in product["print_areas"]:
        placeholders = []
        for ph in area["placeholders"]:
            if ph["position"] in new_ids:
                ph = {"position": ph["position"], "images": [dict(id=new_ids[ph["position"]], angle=0, **FULL)]}
            placeholders.append(ph)
        print_areas.append({"variant_ids": area["variant_ids"], "placeholders": placeholders})

    api.call("PUT", path, json={"print_areas": print_areas})
    api.post(f"{path[:-5]}/publish.json", {
        "title": False, "description": False, "images": True, "variants": False,
        "tags": False, "keyFeatures": False, "shipping_template": False,
    })
    print(f"{product['title']}: replaced {sorted(new_ids)} and re-published images")


if __name__ == "__main__":
    main()
