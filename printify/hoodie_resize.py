"""Make hoodie back prints as big as the printable back area allows, and move Own Lane art to the back.

The Gildan 18500 back print area (provider 39) is 3461 x 3955 px, about 11.5 x 13.2 in. Art cannot extend past
it without being cut off, so "bigger" means filling it:

- Relatable and Drop 002 hoodies: the existing back art is re-placed to fill the area (up to 97% of its height
  and width, from 1.5% below the top edge). Immortalized backs already fill it, so they are left alone.
- Own Lane hoodies: back-only. The front art moves to the back, enlarged (target 1.4x its front size, capped by
  the area height), with a one-line name + tagline strip under it (designs/print-back/*-strip-<ink>.png,
  white text on dark garments, black on light ones). The old front print and back name block are removed.

Usage:
    python3 printify/hoodie_resize.py --commit SHA            # dry run
    python3 printify/hoodie_resize.py --commit SHA --apply
"""

import argparse
import os
import time
from pathlib import Path

from PIL import Image

from create_products import Printify
from fit import placeholder_sizes
from ownlane_backs import ART as OWNLANE, WHITE_TEXT

ROOT = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-back/{name}"
FILL_TAGS = {"relatable", "drop 002"}  # Immortalized backs already fill the area
EDGE, TOP = 0.97, 0.015
STRIP_H, GAP, GROW = 0.11, 0.02, 1.4


def fill_place(img, area_ratio):
    ratio = img["height"] / img["width"] / area_ratio  # print height (fraction of area) per unit width
    scale = round(min(EDGE, EDGE / ratio), 4)
    return dict(x=0.5, y=round(TOP + scale * ratio / 2, 4), scale=scale)


def strip_name(prefix, colors):
    return f"{prefix}-strip-{'white' if set(colors) & WHITE_TEXT else 'black'}.png"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True, help="pushed commit holding designs/print-back strips")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    w, h = placeholder_sizes(api, 77, 39)["back"]
    area_ratio = h / w
    uploads = {}

    def upload(name):
        if name not in uploads:
            uploads[name] = api.post("/uploads/images.json", {
                "file_name": name, "url": RAW.format(commit=args.commit, name=name)})["id"]
        return uploads[name]

    for page in range(1, 8):
        for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]:
            if not p["title"].endswith(" Hoodie") or p["blueprint_id"] != 77:
                continue
            tags = set(p["tags"])
            colors = {v["id"]: v["title"].split(" / ")[0] for v in p["variants"] if v["is_enabled"]}
            areas, notes = [], []
            if "own lane" in tags:
                prefix = OWNLANE[p["title"][: -len(" Hoodie")]]
                for a in p["print_areas"]:
                    front = next(i for ph in a["placeholders"] if ph["position"] == "front" for i in ph["images"])
                    art_ratio = front["height"] / front["width"] / area_ratio
                    strip_file = strip_name(prefix, [colors[v] for v in a["variant_ids"] if v in colors])
                    with Image.open(ROOT / "designs" / "print-back" / strip_file) as im:
                        strip_ratio = im.height / im.width / area_ratio
                    strip_w = min(0.8, STRIP_H / strip_ratio)
                    room = EDGE - TOP - strip_w * strip_ratio - GAP
                    art_w = round(min(front["scale"] * GROW, EDGE, room / art_ratio), 4)
                    art_h = art_w * art_ratio
                    strip_y = TOP + art_h + GAP + strip_w * strip_ratio / 2
                    notes.append(f"art {front['scale']:.0%}->{art_w:.0%} wide (+{art_w / front['scale'] - 1:.0%}), {strip_file}")
                    images = [dict(id=front["id"], x=0.5, y=round(TOP + art_h / 2, 4), scale=art_w, angle=0)]
                    if args.apply:
                        images.append(dict(id=upload(strip_file), x=0.5, y=round(strip_y, 4), scale=round(strip_w, 4), angle=0))
                    areas.append({"variant_ids": a["variant_ids"], "placeholders": [{"position": "back", "images": images}]})
            elif FILL_TAGS & tags:
                for a in p["print_areas"]:
                    phs = []
                    for ph in a["placeholders"]:
                        if not ph["images"]:
                            continue
                        imgs = []
                        for i in ph["images"]:
                            place = fill_place(i, area_ratio) if ph["position"] == "back" else \
                                dict(x=i["x"], y=i["y"], scale=i["scale"])
                            if ph["position"] == "back":
                                notes.append(f"back {i['scale']:.0%}->{place['scale']:.0%} wide")
                            imgs.append(dict(id=i["id"], angle=i["angle"], **place))
                        phs.append({"position": ph["position"], "images": imgs})
                    areas.append({"variant_ids": a["variant_ids"], "placeholders": phs})
            else:
                continue
            print(f"{'apply' if args.apply else 'plan '} {p['title']}: {'; '.join(sorted(set(notes)))}")
            if not args.apply:
                continue
            api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json={"print_areas": areas})
            api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
                "title": False, "description": False, "images": True, "variants": False,
                "tags": False, "keyFeatures": False, "shipping_template": False})
            time.sleep(20)  # stay under Printify's publish rate limit


if __name__ == "__main__":
    main()
