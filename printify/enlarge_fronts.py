"""Make front prints bigger by re-placing the artwork already on each product (no new uploads).

- Own Lane hoodies: the small chest print becomes the full art, as big as the area above the pocket allows.
- Drop 001 hoodies: the chest wordmark becomes a large centered front print.
- Drop 001 tees: the front grows from 80% to 97% of the print-area width, keeping its top edge.

Usage:
    python3 printify/enlarge_fronts.py            # dry run
    python3 printify/enlarge_fronts.py --apply    # update + republish images
"""

import argparse
import os

from create_products import Printify
from fit import MARGIN, placeholder_sizes

DROP1_HOODIES = {"Currently Elsewhere Hoodie", "Seasonal Depression World Tour Hoodie"}
DROP1_TEES = {"Ships in 6–7 Business Days Tee", "Not AI. Just Tired. Tee", "Odysseus Layover Tee"}


def height_frac(img, scale, area_w, area_h):
    return scale * (img["height"] / img["width"]) * (area_w / area_h)


def new_place(title, tags, img, area_w, area_h):
    ratio = (img["height"] / img["width"]) * (area_w / area_h)  # height fraction per unit of scale
    if "own lane" in tags and "hoodie" in tags:
        scale = MARGIN * min(1.0, 1 / ratio)
        return dict(x=0.5, y=(1 - MARGIN) / 2 + scale * ratio / 2, scale=round(scale, 4))
    if title in DROP1_HOODIES:
        return dict(x=0.5, y=0.3, scale=0.8)
    if title in DROP1_TEES:
        top = img["y"] - height_frac(img, img["scale"], area_w, area_h) / 2
        scale = min(0.97, (MARGIN - top) / ratio)
        return dict(x=0.5, y=round(top + scale * ratio / 2, 4), scale=round(scale, 4))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    apply = ap.parse_args().apply

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    sizes = {}
    for page in (1, 2):
        for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]:
            if not (p.get("external") or {}).get("id"):
                continue
            key = (p["blueprint_id"], p["print_provider_id"])
            sizes.setdefault(key, placeholder_sizes(api, *key))
            area_w, area_h = sizes[key]["front"]
            changed = None
            for area in p["print_areas"]:
                for ph in area["placeholders"]:
                    if ph["position"] != "front" or not ph["images"]:
                        continue
                    img = ph["images"][0]
                    place = new_place(p["title"], p["tags"], img, area_w, area_h)
                    if place:
                        before = img["scale"]
                        img.update(place)
                        changed = (before, place["scale"], height_frac(img, place["scale"], area_w, area_h))
            if not changed:
                continue
            before, after, h = changed
            print(f"{'set ' if apply else 'plan'}  {p['title']}: width {before:.0%} -> {after:.0%} (height {h:.0%})")
            if not apply:
                continue
            areas = [{"variant_ids": a["variant_ids"],
                      "placeholders": [ph for ph in a["placeholders"] if ph["images"]]} for a in p["print_areas"]]
            path = f"/shops/{shop}/products/{p['id']}.json"
            api.call("PUT", path, json={"print_areas": areas})
            api.post(f"{path[:-5]}/publish.json", {
                "title": False, "description": False, "images": True, "variants": False,
                "tags": False, "keyFeatures": False, "shipping_template": False,
            })


if __name__ == "__main__":
    main()
