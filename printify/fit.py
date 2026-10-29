"""Size trimmed artwork (designs/print-fit) to fill Printify print areas, and swap it onto products.

Printify places an image by its center (x, y as fractions of the print area) and its width as a
fraction of the print-area width (scale). `fill` makes the art as large as the area's shape allows,
top-aligned; `chest` makes a small left-chest print.

Usage (refit existing products):
    python3 printify/fit.py <product_id> <position>=<file> [<position>=<file> ...]
"""

import os
import sys
from pathlib import Path

from PIL import Image

from create_products import Printify

ROOT = Path(__file__).resolve().parent.parent
FIT_DIR = ROOT / "designs" / "print-fit"
COMMIT = "7ca55caf51134bb436bc7113f4ab090fcf5efb65"
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-fit/{name}"
MARGIN = 0.97  # leave a sliver of the print area free on the limiting side


def aspect(name):
    with Image.open(FIT_DIR / name) as im:
        return im.height / im.width


def fill(name, area_w, area_h):
    ar, area_ar = aspect(name), area_h / area_w
    scale = MARGIN * min(1.0, area_ar / ar)
    height_frac = scale * ar / area_ar
    return dict(x=0.5, y=(1 - MARGIN) / 2 + height_frac / 2, scale=round(scale, 4))


def chest(name, area_w, area_h, width_frac=0.27):
    height_frac = width_frac * aspect(name) / (area_h / area_w)
    return dict(x=0.72, y=0.06 + height_frac / 2, scale=width_frac)


def placeholder_sizes(api, blueprint_id, provider_id):
    variants = api.get(f"/catalog/blueprints/{blueprint_id}/print_providers/{provider_id}/variants.json")["variants"]
    return {p["position"]: (p["width"], p["height"]) for p in variants[0]["placeholders"]}


def upload(api, name, cache):
    if name not in cache:
        cache[name] = api.post("/uploads/images.json",
                               {"file_name": name, "url": RAW.format(commit=COMMIT, name=name)})["id"]
    return cache[name]


def refit(api, shop_id, product_id, files, cache):
    """Replace artwork on an existing single-print-area product with full-size fitted art."""
    path = f"/shops/{shop_id}/products/{product_id}.json"
    p = api.get(path)
    sizes = placeholder_sizes(api, p["blueprint_id"], p["print_provider_id"])
    areas = []
    for area in p["print_areas"]:
        placeholders = [ph for ph in area["placeholders"] if ph.get("images") and ph["position"] not in files]
        for position, name in files.items():
            place = fill(name, *sizes[position])
            placeholders.append({"position": position,
                                 "images": [dict(id=upload(api, name, cache), angle=0, **place)]})
        areas.append({"variant_ids": area["variant_ids"], "placeholders": placeholders})
    api.call("PUT", path, json={"print_areas": areas})
    api.post(f"{path[:-5]}/publish.json", {
        "title": False, "description": False, "images": True, "variants": False,
        "tags": False, "keyFeatures": False, "shipping_template": False,
    })
    return p["title"], {pos: fill(name, *sizes[pos])["scale"] for pos, name in files.items()}


def main():
    product_id, *pairs = sys.argv[1:]
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")
    title, scales = refit(api, shop["id"], product_id, dict(p.split("=", 1) for p in pairs), {})
    print(f"{title}: refit {scales}")


if __name__ == "__main__":
    main()
