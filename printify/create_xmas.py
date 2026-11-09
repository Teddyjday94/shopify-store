"""Create the Christmas Collection: a tee, a hoodie and a dad hat for each design.

Tees carry the full art on the front only (designs/print-xmas/*-back.png, black keyed out).
Hoodies carry it on the back with a small chest mark up front. Both come on Black only: the art is painted on black and dark details
would pick up any other garment color. Hats get the slogan in white on the front panel.

Usage:
    python3 printify/create_xmas.py            # dry run
    python3 printify/create_xmas.py --apply    # create + publish
    python3 printify/create_xmas.py --apply --refresh   # existing tees/hoodies: swap in the current back print
"""

import argparse
import os
import sys
import time

from PIL import Image

from create_products import TEE_SIZES, XXL_UPCHARGE, Printify
from fit import MARGIN, ROOT, placeholder_sizes


RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-xmas/{name}"
ART = ROOT / "designs" / "print-xmas"
TAGS = ["christmas", "holiday"]

TEE = dict(kind="Tee", blueprint=12, provider=29, price=2700, colors=["Black"], sizes=TEE_SIZES,
           features=["Full-color front print",
                     "Soft, lightweight 100% combed cotton", "Retail unisex fit"])
HOODIE = dict(kind="Hoodie", blueprint=77, provider=39, price=3700, colors=["Black"], sizes=TEE_SIZES,
              features=["Full-color back print, small chest print up front",
                        "Medium-heavy cotton/poly blend, fleece-lined", "Double-lined hood, front pouch pocket",
                        "Unisex fit, size up for oversized"])
HAT = dict(kind="Dad Hat", blueprint=5383, provider=41, price=2700, colors=["Black", "Red", "Forest Green"],
           sizes=None, features=["Printed front panel", "Unstructured cotton twill, curved brim",
                                  "One size, adjustable strap"])

DESIGNS = [
    ("01-on-the-naughty-list-again", "On the Naughty List Again", ["naughty", "pin-up"],
     "A pin-up in a Santa hat, fishnets and red bows, surrounded by presents she did not earn.", "Worth it."),
    ("02-suck-it-up-buttercup", "Suck It Up Buttercup", ["santa", "funny"],
     "Santa, cigar lit, giving you his honest review of your attitude this year.", "It's Christmas. Act like it."),
    ("03-dear-santa-bring-bourbon", "Dear Santa, Bring Bourbon", ["bourbon", "whiskey"],
     "A crystal glass of bourbon on the rocks, wearing the Santa hat. The only list that matters.",
     "Skip the socks."),
    ("04-the-gift-is-me", "The Gift Is Me", ["gift", "funny"],
     "A gold-and-red present with a bow the size of your ego.", "You're welcome."),
    ("05-holly-jolly-chaos", "Holly Jolly Chaos", ["snowman", "chaos"],
     "A snowman in shades, arms crossed, grinning like he knows what happened at the party.",
     "Merry and mildly feral."),
]


def aspect(name):
    with Image.open(ART / name) as im:
        return im.height / im.width


def back_place(name, w, h):
    ratio = aspect(name) * w / h
    scale = MARGIN * min(1.0, 1 / ratio)
    return dict(x=0.5, y=round(0.02 + scale * ratio / 2, 4), scale=round(scale, 4))


def chest_place(name, w, h, width=0.27):
    return dict(x=0.72, y=round(0.06 + width * aspect(name) * w / h / 2, 4), scale=width)


def hat_place(name, w, h, fill=0.85):
    return dict(x=0.5, y=0.5, scale=round(fill * min(1.0, (h / w) / aspect(name)), 4))


def refresh(api, shop, pid, back_id, name):
    """Point an existing product's back print at new artwork, re-placed for its aspect; the front stays."""
    path = f"/shops/{shop}/products/{pid}.json"
    p = api.get(path)
    w, h = placeholder_sizes(api, p["blueprint_id"], p["print_provider_id"])["back"]
    areas = []
    for area in p["print_areas"]:
        phs = []
        for ph in area["placeholders"]:
            if not ph["images"]:
                continue
            i = ph["images"][0]
            img = dict(id=back_id, angle=0, **back_place(name, w, h)) if ph["position"] == "back" else \
                dict(id=i["id"], x=i["x"], y=i["y"], scale=i["scale"], angle=i["angle"])
            phs.append({"position": ph["position"], "images": [img]})
        areas.append({"variant_ids": area["variant_ids"], "placeholders": phs})
    api.call("PUT", path, json={"print_areas": areas})
    api.post(f"{path[:-5]}/publish.json", {
        "title": False, "description": False, "images": True, "variants": False,
        "tags": False, "keyFeatures": False, "shipping_template": False})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--refresh", action="store_true", help="swap the back print on existing tees and hoodies")
    ap.add_argument("--only", nargs="+", metavar="SLUG", help="limit to these design slugs, e.g. 01 03")
    ap.add_argument("--commit", help="git commit holding designs/print-xmas (pushed to GitHub)")
    args = ap.parse_args()
    if args.apply and not args.commit:
        sys.exit("--apply needs --commit")

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    existing = {p["title"]: p["id"] for page in (1, 2, 3, 4) for p in
                api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]}
    uploads = {}

    def image(name):
        if name not in uploads:
            uploads[name] = api.post("/uploads/images.json", {
                "file_name": name, "url": RAW.format(commit=args.commit, name=name)})["id"]
        return uploads[name]

    for slug, name, tags, intro, line in DESIGNS:
        if args.only and not slug.startswith(tuple(args.only)):
            continue
        for spec in (TEE, HOODIE, HAT):
            title = f"{name} {spec['kind']}"
            if title in existing:
                if args.refresh and spec is HOODIE:
                    print(f"{'swap' if args.apply else 'plan'}  {title}: new back print")
                    if args.apply:
                        refresh(api, shop, existing[title], image(f"{slug}-back.png"), f"{slug}-back.png")
                        time.sleep(20)
                else:
                    print(f"skip  {title}: already exists")
                continue
            catalog = api.get(f"/catalog/blueprints/{spec['blueprint']}/print_providers/{spec['provider']}/variants.json")["variants"]
            chosen = [v for v in catalog if v["options"].get("color") in spec["colors"]
                      and (spec["sizes"] is None or v["options"].get("size") in spec["sizes"])]
            sizes = placeholder_sizes(api, spec["blueprint"], spec["provider"])
            if spec is HAT:
                (pos, (w, h)), = sizes.items()
                art = [(pos, f"{slug}-hat.png", hat_place(f"{slug}-hat.png", w, h))]
            elif spec is TEE:
                art = [("front", f"{slug}-back.png", back_place(f"{slug}-back.png", *sizes["front"]))]
            else:
                art = [("back", f"{slug}-back.png", back_place(f"{slug}-back.png", *sizes["back"])),
                       ("front", f"{slug}-front.png", chest_place(f"{slug}-front.png", *sizes["front"]))]
            print(f"{'make' if args.apply else 'plan'}  {title}: {sorted({v['options']['color'] for v in chosen})}, "
                  f"{len(chosen)} variants")
            if not args.apply:
                continue
            features = "".join(f"<li>{f}</li>" for f in [*spec["features"], "Printed to order just for you"])
            product = api.post(f"/shops/{shop}/products.json", {
                "title": title,
                "description": f"<p>{intro}</p><ul>{features}</ul><p><em>{line}</em></p>",
                "tags": [spec["kind"].lower(), "christmas collection"] + TAGS + tags,
                "blueprint_id": spec["blueprint"],
                "print_provider_id": spec["provider"],
                "variants": [{"id": v["id"], "is_enabled": True,
                              "price": spec["price"] + (XXL_UPCHARGE if v["options"].get("size") == "2XL" else 0)}
                             for v in chosen],
                "print_areas": [{"variant_ids": [v["id"] for v in chosen], "placeholders": [
                    {"position": pos, "images": [dict(id=image(file), angle=0, **place)]} for pos, file, place in art]}],
            })
            api.post(f"/shops/{shop}/products/{product['id']}/publish.json", {
                "title": True, "description": True, "images": True, "variants": True,
                "tags": True, "keyFeatures": True, "shipping_template": True,
            })
            cost = [v["cost"] for v in product["variants"] if v["is_enabled"]]
            print(f"      created, cost ${min(cost) / 100:.2f}-${max(cost) / 100:.2f}")
            time.sleep(20)  # stay under Printify's publish rate limit


if __name__ == "__main__":
    main()
