"""Realms collection: fantasy art and fantasy-flavored slogans as a front-print tee and a back-print hoodie.

Same setup as the Horror collection: Black tee (Bella+Canvas 3001, provider 29) with the art big on the front,
Black hoodie (Gildan 18500 on Print Geek, provider 27, the largest back area for that hoodie) with the art
filling the back. Tees $27, hoodies $37, one price for every size. Print files are the 4x upscales in
designs/realms-src (<slug>-4x.png, about 4,500 px wide).

Usage: python3 printify/create_realms.py [--apply] [--only SLUG]
"""

import argparse
import base64
import os
import time

from PIL import Image

from create_products import Printify
from fit import placeholder_sizes

SRC = os.path.join(os.path.dirname(__file__), "..", "designs", "realms-src")
SIZES = {"S", "M", "L", "XL", "2XL"}
EDGE, TOP = 0.97, 0.03

DESIGNS = [
    ("01-post-credits-scene", "I'm Only Here for the Post-Credits Scene", "Stay seated. Something's coming.",
     "Chrome lettering, a ringed planet and a meteor shower, for the one who never leaves before the end.",
     ["movies", "sci-fi", "funny", "space"]),
    ("02-happily-ever-after-hard-pass", "Happily Ever After? Hard Pass.", "The dragon was better company.",
     "Gilded gothic lettering, thorned roses and a far-off castle, for anyone skipping the fairy-tale ending.",
     ["fairy tale", "gothic", "roses", "funny"]),
    ("03-origin-story-bad-decisions", "My Origin Story Is Mostly Bad Decisions", "Every hero starts somewhere.",
     "Comic-book lettering and halftone explosions, for the character arc still in progress.",
     ["comic", "pop art", "funny"]),
    ("04-dragon-wanderer", "Dragonfall", "Some roads only go one way.",
     "A red-cloaked wanderer with a burning blade, a bone dragon overhead and a blood moon over ruined spires.",
     ["dragon", "knight", "dark fantasy", "blood moon"]),
    ("05-gargoyle-watch", "Rain on the Gargoyle", "The city sleeps. Someone has to watch.",
     "A hooded watcher in tattered armor, crouched on a gargoyle in the rain over a gothic skyline.",
     ["gothic", "gargoyle", "dark fantasy", "moon"]),
    ("06-lantern-witch", "Lantern Witch", "Follow the light. Mind the mushrooms.",
     "A young witch with a lantern and a winged cat, stepping through a glowing archway into a floating kingdom.",
     ["witch", "fairy tale", "magic", "cottagecore"]),
    ("07-rooftop-leap", "Midnight Leap", "No one sees you coming.",
     "A masked rooftop runner in a red cape, leaping across a moonlit skyline, drawn in vintage comic ink.",
     ["comic", "vigilante", "city", "moon"]),
    ("08-antler-druid", "Moonwood Druid", "The forest keeps its own time.",
     "An antlered druid with a glowing staff and a fire-tailed spirit fox, under a full moon and waterfalls.",
     ["druid", "forest", "magic", "moon"]),
]

TEE = dict(kind="Tee", blueprint=12, provider=29, price=2700, position="front", colors={"Black"},
           features=["Full-color front print", "Soft, lightweight 100% combed cotton", "Retail unisex fit"])
HOODIE = dict(kind="Hoodie", blueprint=77, provider=27, price=3700, position="back", colors={"Black"},
              features=["Big back print", "Medium-heavy cotton/poly blend, fleece-lined",
                        "Double-lined hood, front pouch pocket", "Unisex fit, size up for oversized"])


def place(img_w, img_h, area_w, area_h):
    ratio = (img_h / img_w) * (area_w / area_h)
    scale = round(min(EDGE, (1 - TOP - 0.01) / ratio), 4)
    return dict(x=0.5, y=round(TOP + scale * ratio / 2, 4), scale=scale, angle=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    existing, page = set(), 1
    while True:
        d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        existing |= {p["title"] for p in d["data"]}
        if page >= d["last_page"]:
            break
        page += 1
    uploads = {}
    for slug, name, line, intro, extra_tags in DESIGNS:
        if args.only and not slug.startswith(args.only):
            continue
        path = os.path.join(SRC, f"{slug}-4x.png")
        w, h = Image.open(path).size
        for spec in (TEE, HOODIE):
            title = f"{name} {spec['kind']}"
            if title in existing:
                print(f"skip  {title}")
                continue
            catalog = api.get(f"/catalog/blueprints/{spec['blueprint']}/print_providers/{spec['provider']}/variants.json")["variants"]
            chosen = [v for v in catalog if v["options"].get("color") in spec["colors"] and v["options"].get("size") in SIZES]
            aw, ah = placeholder_sizes(api, spec["blueprint"], spec["provider"])[spec["position"]]
            spot = place(w, h, aw, ah)
            dpi = w / (spot["scale"] * aw / 300)
            print(f"{'make' if args.apply else 'plan'}  {title}: {len(chosen)} variants, art {spot['scale']:.0%} wide, "
                  f"{dpi:.0f} DPI", flush=True)
            if not args.apply:
                continue
            if path not in uploads:
                with open(path, "rb") as f:
                    uploads[path] = api.post("/uploads/images.json", {
                        "file_name": f"{slug}.png", "contents": base64.b64encode(f.read()).decode()})["id"]
            features = "".join(f"<li>{x}</li>" for x in [*spec["features"], "Printed to order just for you"])
            product = api.post(f"/shops/{shop}/products.json", {
                "title": title,
                "description": f"<p>{intro}</p><ul>{features}</ul><p><em>{line}</em></p>",
                "tags": [spec["kind"].lower(), "realms", "fantasy", *extra_tags],
                "blueprint_id": spec["blueprint"],
                "print_provider_id": spec["provider"],
                "variants": [{"id": v["id"], "is_enabled": True, "price": spec["price"]} for v in chosen],
                "print_areas": [{"variant_ids": [v["id"] for v in chosen], "placeholders": [
                    {"position": spec["position"], "images": [dict(id=uploads[path], **spot)]}]}],
            })
            api.post(f"/shops/{shop}/products/{product['id']}/publish.json", {
                "title": True, "description": True, "images": True, "variants": True,
                "tags": True, "keyFeatures": True, "shipping_template": True})
            cost = [v["cost"] for v in product["variants"] if v["is_enabled"]]
            print(f"      created {product['id']}, cost ${min(cost) / 100:.2f}-${max(cost) / 100:.2f}", flush=True)
            time.sleep(20)


if __name__ == "__main__":
    main()
