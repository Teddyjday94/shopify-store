"""Create Drop 004 (Old Gods, New Problems): a tee and a hoodie for each of four paintings.

The back is the painting framed like a vintage poster with its title (designs/print-drop4/*-back.png);
the front is a small chest mark. White type, so only dark garment colors.

Usage:
    python3 printify/create_drop4.py            # dry run
    python3 printify/create_drop4.py --apply    # create + publish
"""

import argparse
import os
import time

from PIL import Image

from create_products import TEE_SIZES, XXL_UPCHARGE, Printify
from fit import MARGIN, ROOT, placeholder_sizes

COMMIT = "b9bf46af1b6ba27c9aec76ae30743b8769a86e78"
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-drop4/{name}"
ART = ROOT / "designs" / "print-drop4"

TEE = dict(kind="Tee", blueprint=12, provider=29, price=3000,
           features=["Soft, lightweight 100% combed cotton", "Retail unisex fit"])
HOODIE = dict(kind="Hoodie", blueprint=77, provider=39, price=4500,
              features=["Medium-heavy cotton/poly blend, fleece-lined", "Double-lined hood, front pouch pocket",
                        "Unisex fit, size up for oversized"])

DESIGNS = [
    ("01-lead-the-charge", "Lead the Charge", "Maroon", ["general", "horse", "army"],
     "A general on a rearing white horse points the whole army up the mountain.", "Someone has to go first."),
    ("02-rise-from-ruin", "Rise From Ruin", "Maroon", ["underworld", "fire", "fighters"],
     "Two fighters claw their way out of a burning underworld.", "Down bad. Getting up anyway."),
    ("03-sleep-paralysis-club", "Sleep Paralysis Club", "Maroon", ["gothic", "demon", "sleep"],
     "A sleeping beauty, a tiny demon, and a horse that should not be in the bedroom.",
     "Members only. Meetings at 3 a.m."),
    ("04-one-way-ferry", "One Way Ferry", "Navy", ["ferryman", "moon", "island"],
     "A cloaked ferryman crosses a still black lake toward an island of cypress and marble.",
     "No return ticket required."),
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    apply = ap.parse_args().apply

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    existing = {p["title"] for page in (1, 2, 3) for p in
                api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]}
    uploads = {}

    def image(name):
        if name not in uploads:
            uploads[name] = api.post("/uploads/images.json", {"file_name": name, "url": RAW.format(commit=COMMIT, name=name)})["id"]
        return uploads[name]

    for slug, name, alt, tags, intro, line in DESIGNS:
        for spec in (TEE, HOODIE):
            title = f"{name} {spec['kind']}"
            if title in existing:
                print(f"skip  {title}")
                continue
            catalog = api.get(f"/catalog/blueprints/{spec['blueprint']}/print_providers/{spec['provider']}/variants.json")["variants"]
            colors = ["Black", alt]
            chosen = [v for v in catalog if v["options"].get("color") in colors and v["options"].get("size") in TEE_SIZES]
            sizes = placeholder_sizes(api, spec["blueprint"], spec["provider"])
            back, front = f"{slug}-back.png", f"{slug}-front.png"
            bp, fp = back_place(back, *sizes["back"]), chest_place(front, *sizes["front"])
            print(f"{'make' if apply else 'plan'}  {title}: {sorted({v['options']['color'] for v in chosen})}, "
                  f"{len(chosen)} variants, back {bp['scale']:.0%} wide")
            if not apply:
                continue
            features = "".join(f"<li>{f}</li>" for f in
                               ["Full-color back print, framed like a vintage poster", "Small chest print up front",
                                *spec["features"], "Printed to order just for you"])
            product = api.post(f"/shops/{shop}/products.json", {
                "title": title,
                "description": f"<p>{intro}</p><ul>{features}</ul><p><em>{line}</em></p>",
                "tags": [spec["kind"].lower(), "drop 004", "old gods new problems"] + tags,
                "blueprint_id": spec["blueprint"],
                "print_provider_id": spec["provider"],
                "variants": [{"id": v["id"], "is_enabled": True,
                              "price": spec["price"] + (XXL_UPCHARGE if v["options"]["size"] == "2XL" else 0)}
                             for v in chosen],
                "print_areas": [{"variant_ids": [v["id"] for v in chosen], "placeholders": [
                    {"position": "back", "images": [dict(id=image(back), angle=0, **bp)]},
                    {"position": "front", "images": [dict(id=image(front), angle=0, **fp)]},
                ]}],
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
