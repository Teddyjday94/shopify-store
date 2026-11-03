"""Swap rebranded print files (Elsewhere -> Many Worlds) onto existing Printify products and republish.

Every product image whose file name is listed below gets the new file in the same spot (x, y, scale, angle).
The Elsewhere beanie is also renamed. Products already swapped are recorded in rebrand_done.json, so the
script can be re-run after a rate limit.

Usage:
    python3 printify/rebrand_art.py --commit <sha>            # dry run
    python3 printify/rebrand_art.py --commit <sha> --apply
"""

import argparse
import json
import os
import time
from pathlib import Path

from create_products import Printify

RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/{path}"
DONE = Path(__file__).with_name("rebrand_done.json")

SWAPS = {}
for slug in ["01-lead-the-charge", "02-rise-from-ruin", "03-sleep-paralysis-club", "04-one-way-ferry",
             "05-born-ready", "06-fallen-not-finished", "07-above-it-all", "08-going-with-the-flow"]:
    for side in ("back", "front"):
        SWAPS[f"{slug}-{side}.png"] = f"print-drop4/{slug}-{side}.png"
for slug in ["01-on-the-naughty-list-again", "02-suck-it-up-buttercup", "03-dear-santa-bring-bourbon",
             "04-the-gift-is-me", "05-holly-jolly-chaos"]:
    SWAPS[f"{slug}-front.png"] = f"print-xmas/{slug}-front.png"
for slug in ["01-in-my-own-lane", "02-butterfly-effect", "03-lucky-charm", "04-sunflower-soul",
             "05-color-me-bold", "06-crown-and-curls", "07-pink-crown", "08-sisterhood"]:
    for ink in ("black", "white"):
        SWAPS[f"{slug}-back-{ink}.png"] = f"print-back/{slug}-back-{ink}.png"
SWAPS["02-ships-6-7-business-days-black.png"] = "print/02-ships-6-7-business-days-black.png"
for ink in ("black", "white"):
    SWAPS[f"09-elsewhere-beanie-{ink}.png"] = f"print/09-many-worlds-beanie-{ink}.png"

RENAME = {"Elsewhere Cuffed Beanie": dict(
    title="Many Worlds Cuffed Beanie",
    description=("<p>The Many Worlds wordmark, stitched across a classic cuffed knit beanie.</p><ul>"
                 "<li>Embroidered, not printed</li><li>Soft acrylic rib knit with a fold-over cuff</li>"
                 "<li>One size, adjustable</li><li>Made to order just for you</li></ul><p><em>One of many.</em></p>"),
    tags=["beanie", "embroidered", "hat", "many worlds"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    done = json.loads(DONE.read_text()) if DONE.exists() else {}
    uploads = {}

    def upload(path):
        if path not in uploads:
            uploads[path] = api.post("/uploads/images.json", {
                "file_name": Path(path).name, "url": RAW.format(commit=args.commit, path=path)})["id"]
        return uploads[path]

    for page in (1, 2, 3, 4):
        for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]:
            names = {i["name"] for a in p["print_areas"] for ph in a["placeholders"] for i in ph["images"]}
            hits = sorted(names & SWAPS.keys())
            if not hits or p["id"] in done:
                continue
            print(f"{'swap' if args.apply else 'plan'}  {p['title']}: {', '.join(hits)}")
            if not args.apply:
                continue
            areas = [{"variant_ids": a["variant_ids"], "placeholders": [
                {"position": ph["position"], "images": [
                    dict(id=upload(SWAPS[i["name"]]) if i["name"] in SWAPS else i["id"],
                         x=i["x"], y=i["y"], scale=i["scale"], angle=i["angle"]) for i in ph["images"]]}
                for ph in a["placeholders"] if ph["images"]]} for a in p["print_areas"]]
            body = {"print_areas": areas, **RENAME.get(p["title"], {})}
            api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json=body)
            renamed = p["title"] in RENAME
            api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
                "title": renamed, "description": renamed, "images": True, "variants": False,
                "tags": renamed, "keyFeatures": False, "shipping_template": False,
            })
            done[p["id"]] = p["title"]
            DONE.write_text(json.dumps(done, indent=2))
            time.sleep(20)  # Printify publish rate limit


if __name__ == "__main__":
    main()
