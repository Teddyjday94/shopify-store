"""Create the Immortalized Collection: a tee and a hoodie for each painting.

The back is the painting framed like a vintage poster with its title (designs/print-drop4/*-back.png);
the front is a small chest mark. White type, so only dark garment colors.

Products that already exist are skipped, unless --refresh is given: then their artwork is swapped
for the current print files. A refresh republishes their mockups, which resets the back-first
product photos in Shopify (redo them with media_plan.py).

Usage:
    python3 printify/create_drop4.py --commit SHA                     # dry run
    python3 printify/create_drop4.py --commit SHA --apply             # create + publish new designs
    python3 printify/create_drop4.py --commit SHA --apply --refresh   # also refresh existing artwork
"""

import argparse
import os
import time

from PIL import Image

from create_products import TEE_SIZES, XXL_UPCHARGE, Printify
from fit import MARGIN, ROOT, placeholder_sizes

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
    ("05-born-ready", "Born Ready", "Navy", ["goddess", "shell", "ocean"],
     "A goddess rises from the sea on a shell, hair and silk everywhere, sunlight on cue.",
     "Arrived fashionably late. On a shell."),
    ("06-fallen-not-finished", "Fallen, Not Finished", "Maroon", ["angel", "wings", "ruins"],
     "A fallen angel sits in the ruins of heaven, wings still attached, pride slightly less so.",
     "Heaven can wait. So can I."),
    ("07-above-it-all", "Above It All", "Brown", ["wanderer", "mountains", "clouds"],
     "A wanderer in a long coat stands over a sea of clouds at sunrise.",
     "Physically here. Mentally up there."),
    ("08-going-with-the-flow", "Going With the Flow", "Forest", ["flowers", "river", "dreamy"],
     "A dreamer floats down a quiet stream through lilies, roses and golden light.",
     "Floating through it."),
    ("09-long-live-the-king", "Long Live the King", "Maroon", ["skeleton", "king", "castle"],
     "A skeleton king rests on his sword in a field of poppies while his castle burns under a blood moon.",
     "Crowns don't retire."),
    ("10-queen-forever", "Queen Forever", "Navy", ["skeleton", "queen", "jewels"],
     "A skeleton queen in sapphires, pearls and lace, still holding court long after the funeral.",
     "Death is no reason to dress down."),
    ("11-nine-tails", "Nine Tails", "Navy", ["kitsune", "fox", "spirit"],
     "A nine-tailed fox spirit under a blood moon, with bells, a blade and falling cherry blossoms.",
     "Protector or punisher. Your call."),
    ("12-masterless", "Masterless", "Maroon", ["ronin", "samurai", "blood moon"],
     "A masterless ronin in a torn red cloak looks out over a cliffside castle under a blood moon.",
     "No lord. No rush."),
]
# Hoodie names for the same colors on the Gildan 18500 at SwiftPOD.
HOODIE_COLOR = {"Brown": "Dark Chocolate", "Forest": "Forest Green"}


def aspect(name):
    with Image.open(ART / name) as im:
        return im.height / im.width


def back_place(name, w, h):
    ratio = aspect(name) * w / h
    scale = MARGIN * min(1.0, 1 / ratio)
    return dict(x=0.5, y=round(0.02 + scale * ratio / 2, 4), scale=round(scale, 4))


def chest_place(name, w, h, width=0.27):
    return dict(x=0.72, y=round(0.06 + width * aspect(name) * w / h / 2, 4), scale=width)


def refresh(api, shop, product, back_id, front_id):
    """Point an existing product's back and front prints at new artwork, keeping placement."""
    path = f"/shops/{shop}/products/{product['id']}.json"
    p = api.get(path)
    areas = []
    for area in p["print_areas"]:
        placeholders = []
        for ph in area["placeholders"]:
            if not ph["images"]:
                continue
            img = ph["images"][0]
            new_id = back_id if ph["position"] == "back" else front_id
            placeholders.append({"position": ph["position"], "images": [
                dict(id=new_id, x=img["x"], y=img["y"], scale=img["scale"], angle=img["angle"])]})
        areas.append({"variant_ids": area["variant_ids"], "placeholders": placeholders})
    api.call("PUT", path, json={"print_areas": areas})
    api.post(f"{path[:-5]}/publish.json", {
        "title": False, "description": False, "images": True, "variants": False,
        "tags": False, "keyFeatures": False, "shipping_template": False,
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--commit", required=True, help="pushed commit holding designs/print-drop4")
    args = ap.parse_args()
    apply = args.apply

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    existing = {p["title"]: p for page in (1, 2, 3) for p in
                api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]}
    uploads = {}

    def image(name):
        if name not in uploads:
            uploads[name] = api.post("/uploads/images.json", {"file_name": name, "url": RAW.format(commit=args.commit, name=name)})["id"]
        return uploads[name]

    for slug, name, alt, tags, intro, line in DESIGNS:
        for spec in (TEE, HOODIE):
            title = f"{name} {spec['kind']}"
            back, front = f"{slug}-back.png", f"{slug}-front.png"
            if title in existing:
                if not args.refresh:
                    print(f"skip  {title}: already exists")
                    continue
                print(f"{'swap' if apply else 'plan'}  {title}: refresh artwork")
                if apply:
                    refresh(api, shop, existing[title], image(back), image(front))
                    time.sleep(20)
                continue
            catalog = api.get(f"/catalog/blueprints/{spec['blueprint']}/print_providers/{spec['provider']}/variants.json")["variants"]
            colors = ["Black", HOODIE_COLOR.get(alt, alt) if spec is HOODIE else alt]
            chosen = [v for v in catalog if v["options"].get("color") in colors and v["options"].get("size") in TEE_SIZES]
            sizes = placeholder_sizes(api, spec["blueprint"], spec["provider"])
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
                "tags": [spec["kind"].lower(), "drop 004", "immortalized"] + tags,
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
