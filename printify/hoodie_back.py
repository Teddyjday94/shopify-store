"""Turn the Relatable and Drop 002 hoodies into big back-print-only hoodies at $40.

Relatable hoodies: their front art moves to the back. Drop 002 hoodies: the main front art moves to the back
(the old back panels were already as big as their tall, narrow shapes allow, so they could not cover more of
the back); the front and the old panel are removed. The art is sized as large as the back allows, up to 90%
of the width and 88% of the height, starting just below the collar.

A back-only print costs the same at Printify as a front-only one ($22.67 for M/L), so $40 keeps about $15.90
per hoodie after card fees. 2XL keeps its existing upcharge over the base price.

Usage:
    python3 printify/hoodie_back.py --commit SHA            # dry run
    python3 printify/hoodie_back.py --commit SHA --apply
"""

import argparse
import os
import time
from pathlib import Path

from PIL import Image

from create_products import Printify
from create_relatable import DESIGNS as RELATABLE
from fit import placeholder_sizes

ROOT = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/{path}"
DROP2 = {  # hoodie title prefix -> main artwork
    "Same Chaos Different Day": "print-fit/01-front-engraved-moon-miner.png",
    "Same Mind Brighter Days": "print-fit/02-front-grunge-samurai-red-sakura-sun.png",
    "Balance": "print-fit/03-front-balance-of-mind-and-heart.png",
    "Somewhere in a Calmer Place": "print-fit/04-front-sumi-ink-skull-mountain-landscape.png",
    "A Quieter Mind": "print-fit/05-front-a-quieter-mind-space-cat.png",
    "Systems Still Functional": "print-fit/06-front-error-skull.png",
}
ART = {name: f"print-relatable/{slug}.png" for slug, name, *_ in RELATABLE} | DROP2
BASE_PRICE = 4000


def back_place(path, w, h, max_w=0.90, max_h=0.88, top=0.04):
    with Image.open(ROOT / "designs" / path) as im:
        ratio = im.height / im.width * w / h  # print height (fraction of area) per unit width
    scale = round(min(max_w, max_h / ratio), 4)
    return dict(x=0.5, y=round(top + scale * ratio / 2, 4), scale=scale)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="pushed commit holding the artwork")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    w, h = placeholder_sizes(api, 77, 39)["back"]
    uploads = {}
    for page in range(1, 8):
        for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]:
            if not p["title"].endswith(" Hoodie") or not ({"relatable", "drop 002"} & set(p["tags"])):
                continue
            path = ART.get(p["title"][: -len(" Hoodie")])
            if not path:
                print(f"skip  {p['title']}: no artwork mapped")
                continue
            place = back_place(path, w, h)
            enabled = [v for v in p["variants"] if v["is_enabled"]]
            base = min(v["price"] for v in enabled)
            variants = [{"id": v["id"], "is_enabled": v["is_enabled"],
                         "price": v["price"] - base + BASE_PRICE if v["is_enabled"] else v["price"]} for v in p["variants"]]
            prices = sorted({v["price"] / 100 for v in variants if v["is_enabled"]})
            print(f"{'apply' if args.apply else 'plan '} {p['title']}: back only, {place['scale']:.0%} wide, {prices}")
            if not args.apply:
                continue
            if path not in uploads:
                uploads[path] = api.post("/uploads/images.json", {
                    "file_name": Path(path).name, "url": RAW.format(commit=args.commit, path=path)})["id"]
            areas = [{"variant_ids": a["variant_ids"], "placeholders": [
                {"position": "back", "images": [dict(id=uploads[path], angle=0, **place)]}]} for a in p["print_areas"]]
            api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json={"print_areas": areas, "variants": variants})
            api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
                "title": False, "description": False, "images": True, "variants": True,
                "tags": False, "keyFeatures": False, "shipping_template": False})
            time.sleep(20)  # stay under Printify's publish rate limit


if __name__ == "__main__":
    main()
