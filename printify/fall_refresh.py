"""Fall refresh: add fall colors and, on hoodies, swap in tighter front crops so the front prints bigger.

Each product gets one update and one re-publish. Fronts use designs/print-front/ (cropped from
designs/print-fit/ to drop drips or filler at the bottom); the back print is untouched.

Usage:
    python3 printify/fall_refresh.py            # dry run
    python3 printify/fall_refresh.py --apply
"""

import argparse
import os

from create_products import TEE_SIZES, XXL_UPCHARGE, Printify
from fit import MARGIN

COMMIT = "4cefb9816472d6cd0591d4fa3061bf3a7a0a463a"
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-front/{name}"
CROPPED = {  # file name -> size (w, h) of the cropped art
    "03-front-balance-of-mind-and-heart.png": (3597, 3983),
    "02-front-grunge-samurai-red-sakura-sun.png": (3605, 3730),
    "08-sisterhood.png": (3401, 3649),
    "07-pink-crown.png": (3413, 3807),
    "06-crown-and-curls.png": (3126, 3664),
    "05-color-me-bold.png": (3663, 3779),
    "04-sunflower-soul.png": None,
    "02-butterfly-effect.png": None,
}
TEXT_HOODIES = {"Currently Elsewhere Hoodie", "Seasonal Depression World Tour Hoodie"}

HOODIE_DARK = ["Forest Green", "Maroon"]
HOODIE_LIGHT = ["Gold"]
HOODIE_ART = ["Forest Green", "Gold"]
TEE_DARK = ["Forest", "Maroon", "Brown"]
TEE_LIGHT = ["Gold", "Autumn"]
TEE_ART = ["Forest", "Gold"]

# title -> colors to add; "Color:ink" picks the print area for two-ink products.
FALL = {
    "A Quieter Mind Hoodie": HOODIE_DARK,
    "Same Mind Brighter Days Hoodie": HOODIE_DARK,
    "Systems Still Functional Hoodie": HOODIE_DARK,
    "Somewhere in a Calmer Place Hoodie": HOODIE_LIGHT,
    "Balance Hoodie": HOODIE_LIGHT,
    "Same Chaos Different Day Hoodie": HOODIE_LIGHT,
    "Sisterhood Hoodie": HOODIE_ART,
    "Pink Crown Hoodie": HOODIE_ART,
    "Crown & Curls Hoodie": HOODIE_ART,
    "Color Me Bold Hoodie": HOODIE_ART,
    "Sunflower Soul Hoodie": HOODIE_ART,
    "Lucky Charm Hoodie": HOODIE_ART,
    "Butterfly Effect Hoodie": HOODIE_ART,
    "In My Own Lane Hoodie": HOODIE_ART,
    "Seasonal Depression World Tour Hoodie": [],
    "Currently Elsewhere Hoodie": ["Forest Green:white", "Maroon:white", "Gold:black"],
    "A Quieter Mind Tee": TEE_DARK,
    "Same Mind Brighter Days Tee": TEE_DARK,
    "Systems Still Functional Tee": TEE_DARK,
    "Somewhere in a Calmer Place Tee": TEE_LIGHT,
    "Balance Tee": TEE_LIGHT,
    "Same Chaos Different Day Tee": TEE_LIGHT,
    "Sisterhood Tee": TEE_ART,
    "Pink Crown Tee": TEE_ART,
    "Crown & Curls Tee": TEE_ART,
    "Color Me Bold Tee": TEE_ART,
    "Sunflower Soul Tee": TEE_ART,
    "Lucky Charm Tee": TEE_ART,
    "Butterfly Effect Tee": TEE_ART,
    "In My Own Lane Tee": TEE_ART,
    "Not AI. Just Tired. Tee": ["Forest:white", "Maroon:white", "Gold:black"],
    "Ships in 6–7 Business Days Tee": TEE_LIGHT,
    "Odysseus Layover Tee": ["Mustard:black", "Espresso:white", "Yam:black"],
}


def color_of(options):
    return options.get("color")


def front_place(w, h, area_w, area_h):
    ratio = (h / w) * (area_w / area_h)
    scale = MARGIN * min(1.0, 1 / ratio)
    return dict(x=0.5, y=(1 - MARGIN) / 2 + scale * ratio / 2, scale=round(scale, 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    apply = ap.parse_args().apply

    from PIL import Image
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / "designs" / "print-front"
    for name in CROPPED:
        with Image.open(root / name) as im:
            CROPPED[name] = im.size

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    products = [p for page in (1, 2) for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]
                if p["title"] in FALL and (p.get("external") or {}).get("id")]
    uploads = {}

    for p in products:
        path = f"/shops/{shop}/products/{p['id']}.json"
        catalog = api.get(f"/catalog/blueprints/{p['blueprint_id']}/print_providers/{p['print_provider_id']}/variants.json")
        options = {v["id"]: v["options"] for v in catalog["variants"]}
        sizes = {ph["position"]: (ph["width"], ph["height"]) for ph in catalog["variants"][0]["placeholders"]}
        wanted = dict((s.split(":") + [None])[:2] for s in FALL[p["title"]])
        offered = {color_of(o) for o in options.values()}
        have = {color_of(options[v["id"]]) for v in p["variants"] if v["is_enabled"]}
        missing = sorted(set(wanted) - offered)
        wanted = {c: ink for c, ink in wanted.items() if c in offered and c not in have}
        base = min(v["price"] for v in p["variants"] if v["is_enabled"] and options[v["id"]].get("size") != "2XL")

        def area_for(ink):
            if ink is None:
                return p["print_areas"][0]
            names = lambda a: " ".join(i["name"] for ph in a["placeholders"] for i in ph["images"])
            return next(a for a in p["print_areas"] if f"-{ink}" in names(a))

        added = {vid: area_for(wanted[color_of(o)]) for vid, o in options.items()
                 if color_of(o) in wanted and o.get("size") in TEE_SIZES}
        for area in p["print_areas"]:
            area["variant_ids"] = [v for v in area["variant_ids"] if v not in added]
        for vid, area in added.items():
            area["variant_ids"].append(vid)

        front_note = ""
        for area in p["print_areas"]:
            for ph in area["placeholders"]:
                if ph["position"] != "front" or not ph["images"]:
                    continue
                img = ph["images"][0]
                if p["blueprint_id"] == 77 and img["name"] in CROPPED:
                    name = img["name"]
                    if apply and name not in uploads:
                        uploads[name] = api.post("/uploads/images.json", {
                            "file_name": f"front-{name}", "url": RAW.format(commit=COMMIT, name=name)})["id"]
                    place = front_place(*CROPPED[name], *sizes["front"])
                    front_note = f", front {img['scale']:.0%} -> {place['scale']:.0%} wide"
                    ph["images"] = [dict(id=uploads.get(name, img["id"]), angle=0, **place)]
                elif p["title"] in TEXT_HOODIES:
                    front_note = f", front {img['scale']:.0%} -> 95% wide"
                    img.update(scale=0.95)

        if not added and not front_note:
            print(f"skip  {p['title']}" + (f" (not offered: {missing})" if missing else ""))
            continue
        print(f"{'set ' if apply else 'plan'}  {p['title']}: +{sorted(wanted) or 'no colors'}{front_note}"
              + (f" (not offered: {missing})" if missing else ""))
        if not apply:
            continue
        variants = [{"id": v["id"], "is_enabled": v["is_enabled"] or v["id"] in added,
                     "price": (base + (XXL_UPCHARGE if options[v["id"]].get("size") == "2XL" else 0))
                     if v["id"] in added else v["price"]} for v in p["variants"]]
        areas = [{"variant_ids": a["variant_ids"], "placeholders": [ph for ph in a["placeholders"] if ph["images"]]}
                 for a in p["print_areas"]]
        api.call("PUT", path, json={"variants": variants, "print_areas": areas})
        api.post(f"{path[:-5]}/publish.json", {
            "title": False, "description": False, "images": True, "variants": True,
            "tags": False, "keyFeatures": False, "shipping_template": False,
        })


if __name__ == "__main__":
    main()
