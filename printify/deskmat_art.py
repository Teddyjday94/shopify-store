"""Swap desk mat print files for the AI-extended (outpainted) panoramas in designs/mat-hd/<slug>.jpg.

The panoramas were extended to 2:1 in Canva from the original art, then upscaled 4x with Real-ESRGAN.
Each size gets a cover scale so the art fills the mat edge to edge. Products are matched by title.
Usage: python3 printify/deskmat_art.py [--apply] SLUG ...
"""

import argparse
import base64
import os
import time

from PIL import Image

from create_extras import IMMORTALIZED, XMAS, cover_scale
from create_products import Printify

HD = os.path.join(os.path.dirname(__file__), "..", "designs", "mat-hd")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    names = dict(IMMORTALIZED + XMAS)
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    products, page = {}, 1
    while True:
        d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        products.update({p["title"]: p for p in d["data"]})
        if page >= d["last_page"]:
            break
        page += 1
    for slug in args.slugs:
        title = f"{names[slug]} Desk Mat"
        path = os.path.join(HD, f"{slug}.jpg")
        w, h = Image.open(path).size
        p = products.get(title)
        print(f"{'swap' if args.apply else 'plan'}  {title}: {w}x{h} {'(missing product)' if not p else ''}")
        if not args.apply or not p:
            continue
        with open(path, "rb") as f:
            img = api.post("/uploads/images.json", {"file_name": os.path.basename(path),
                                                    "contents": base64.b64encode(f.read()).decode()})["id"]
        catalog = {v["id"]: v for v in api.get(
            f"/catalog/blueprints/{p['blueprint_id']}/print_providers/{p['print_provider_id']}/variants.json")["variants"]}
        groups = {}
        for v in p["variants"]:
            if v["is_enabled"]:
                ph = catalog[v["id"]]["placeholders"][0]
                groups.setdefault(round(cover_scale(w / h, ph["width"], ph["height"]), 4), []).append(v["id"])
        areas = [{"variant_ids": ids, "placeholders": [{"position": "front", "images": [
            dict(id=img, x=0.5, y=0.5, scale=s, angle=0)]}]} for s, ids in groups.items()]
        api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json={"print_areas": areas})
        api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
            "title": False, "description": False, "images": True, "variants": False,
            "tags": False, "keyFeatures": False, "shipping_template": False})
        print("      updated and republished")
        time.sleep(20)


if __name__ == "__main__":
    main()
