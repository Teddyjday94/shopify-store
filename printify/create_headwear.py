"""Create the embroidered headwear set (dad hat, trucker, beanie, bucket hat) and publish to Shopify.

Artwork comes from designs/print/ (rendered by designs/src/render_headwear.js), one file per
thread color. Each hat color maps to the thread color that reads on it.

Usage:
    python3 printify/create_headwear.py            # dry run
    python3 printify/create_headwear.py --apply    # create + publish
"""

import argparse
import os

from PIL import Image

from create_products import PRINT_DIR, Printify, pick_provider, upload
from fit import placeholder_sizes

FEATURES = ("<ul><li>Embroidered, not printed</li><li>{fabric}</li>"
            "<li>One size, adjustable</li><li>Made to order just for you</li></ul>")


def hat(title, blueprint, price, art, colors, tags, intro, fabric, signoff):
    return dict(title=title, blueprint=blueprint, price=price, art=art, colors=colors, tags=["hat"] + tags,
                description=f"{intro}{FEATURES.format(fabric=fabric)}<p><em>{signoff}</em></p>")


PRODUCTS = [
    hat("Currently Elsewhere Dad Hat", 5383, 2600, "07-currently-elsewhere-hat",
        {"Black": "white", "Forest Green": "white", "Navy": "white", "Stone": "black", "White": "black"},
        ["dad hat", "embroidered", "elsewhere"],
        "<p>The out-of-office reply, stitched onto a low-profile dad hat.</p>",
        "Unstructured cotton twill with a curved brim", "Will respond upon return."),
    hat("Not AI. Just Tired. Trucker Hat", 1446, 2800, "08-not-ai-just-tired-trucker",
        {"Black": "white", "Evergreen / White": "white", "Navy / White": "white",
         "Charcoal / White": "white", "Heather Grey / White": "black"},
        ["trucker hat", "embroidered", "tired"],
        "<p>For anyone whose last message got called robotic. It wasn't. You were just tired.</p>",
        "Structured foam-front trucker with breathable mesh back and snapback closure",
        "Not AI. Just tired."),
    hat("Elsewhere Cuffed Beanie", 1691, 2400, "09-elsewhere-beanie",
        {"Black": "white", "Spruce": "white", "Navy": "white", "Heather Grey": "black", "Gold": "black"},
        ["beanie", "embroidered", "elsewhere"],
        "<p>The wordmark, stitched across a classic cuffed knit beanie.</p>",
        "Soft acrylic rib knit with a fold-over cuff", "Currently elsewhere."),
    hat("Same Chaos Different Day Bucket Hat", 1698, 2800, "10-same-chaos-bucket",
        {"Black": "white", "Army": "white", "Orchid": "white", "Bone": "black"},
        ["bucket hat", "embroidered", "chaos"],
        "<p>Every day, same chaos. At least the hat's different.</p>",
        "Cotton twill bucket hat with a short all-round brim", "Same chaos. Different day."),
]


def placement(art, area_w, area_h, fill=0.9):
    with Image.open(PRINT_DIR / f"{art}-white.png") as im:
        ar = im.height / im.width
    return dict(x=0.5, y=0.5, scale=round(fill * min(1.0, (area_h / area_w) / ar), 4))


def run(apply):
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")
    existing = {p["title"] for page in (1, 2) for p in
                api.get(f"/shops/{shop['id']}/products.json?limit=50&page={page}")["data"]}
    blueprints = {b["id"]: b for b in api.get("/catalog/blueprints.json")}
    cache = {}

    for spec in PRODUCTS:
        if spec["title"] in existing:
            print(f"- {spec['title']}: already exists, skipping")
            continue
        bp = blueprints[spec["blueprint"]]
        provider, variants, colors = pick_provider(api, bp, spec)
        chosen = [v for v in variants if v["options"].get("color") in colors]
        (position, (w, h)), = placeholder_sizes(api, bp["id"], provider["id"]).items()
        place = placement(spec["art"], w, h)
        missing = [c for c in spec["colors"] if c not in colors]
        print(f"- {spec['title']}: {bp['brand']} {bp['model']} via {provider['title']}, {len(chosen)} colors"
              + (f", missing {missing}" if missing else "") + f"; art {round(place['scale'] * w)}px of {w}px wide")
        if not apply:
            continue

        areas = []
        for ink in sorted({spec["colors"][v["options"]["color"]] for v in chosen}):
            ids = [v["id"] for v in chosen if spec["colors"][v["options"]["color"]] == ink]
            image = dict(id=upload(api, f"{spec['art']}-{ink}.png", cache), angle=0, **place)
            areas.append({"variant_ids": ids, "placeholders": [{"position": position, "images": [image]}]})
        product = api.post(f"/shops/{shop['id']}/products.json", {
            "title": spec["title"],
            "description": spec["description"],
            "tags": spec["tags"],
            "blueprint_id": bp["id"],
            "print_provider_id": provider["id"],
            "variants": [{"id": v["id"], "is_enabled": True, "price": spec["price"]} for v in chosen],
            "print_areas": areas,
        })
        profit = [(v["price"] - v["cost"]) / 100 for v in product["variants"] if v.get("is_enabled")]
        api.post(f"/shops/{shop['id']}/products/{product['id']}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True,
        })
        print(f"  created + published, profit before shipping ${min(profit):.2f}-${max(profit):.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    run(ap.parse_args().apply)
