"""Create hoodie versions of the Drop 002 and Own Lane designs (Gildan 18500) and publish to Shopify.

Drop 002 hoodies: front art on the front (sized to fit above the pocket), back art full size on the back.
Own Lane hoodies: art full size on the back plus a small left-chest print.
The first color in each list is the one to feature as the product's main photo.

Usage:
    python3 printify/create_hoodies.py            # dry run
    python3 printify/create_hoodies.py --apply    # create + publish
"""

import argparse
import os

from create_products import Printify, TEE_SIZES, XXL_UPCHARGE, pick_provider
from fit import chest, fill, placeholder_sizes, upload

FEATURES = ("<ul><li>{prints}</li>"
            "<li>Medium-heavy cotton/poly blend, fleece-lined</li>"
            "<li>Double-lined hood, front pouch pocket</li>"
            "<li>Unisex fit, size up for oversized</li>"
            "<li>Printed to order just for you</li></ul>")


def hoodie(title, colors, price, prints, tags, intro, signoff, prints_note):
    return dict(title=title, colors=colors, price=price, prints=prints,
                tags=["hoodie"] + tags,
                description=f"{intro}{FEATURES.format(prints=prints_note)}<p><em>{signoff}</em></p>")


def drop2(title, colors, front, back, tags, intro, signoff):
    return hoodie(title, colors, 5400, [("front", front, fill), ("back", back, fill)],
                  ["drop 002"] + tags, intro, signoff, "Front and back print")


def own_lane(title, colors, art, tags, intro, signoff):
    return hoodie(title, colors, 5200, [("back", art, fill), ("front", art, chest)],
                  ["own lane", "drop 003"] + tags, intro, signoff, "Full-size back print plus a small chest print")


PRODUCTS = [
    drop2("Systems Still Functional Hoodie", ["Black", "Charcoal"],
          "06-front-error-skull.png", "06-back-systems-still-functional.png",
          ["glitch", "skull", "tired"],
          "<p>Boot sequence complete. Anomalies detected. Proceeding anyway, but warmer.</p>",
          "Tired but here anyway."),
    drop2("Same Chaos Different Day Hoodie", ["Sport Grey", "Sand", "Light Blue", "White"],
          "01-front-engraved-moon-miner.png", "01-back-lunar-phases-same-chaos-different-day.png",
          ["moon", "astronaut", "space"],
          "<p>An engraved astronaut mining the moon on the front, the lunar phases down the back.</p>",
          "Same chaos. Different day."),
    drop2("Same Mind Brighter Days Hoodie", ["Black", "Dark Heather"],
          "02-front-grunge-samurai-red-sakura-sun.png", "02-back-sakura-moon-same-mind-brighter-days.png",
          ["samurai", "sakura", "japanese"],
          "<p>The skeleton samurai on his coffee break up front, the moonlit sakura panel on the back.</p>",
          "Same mind. Brighter days."),
    drop2("Balance Hoodie", ["Sport Grey", "Sand", "Light Blue", "White"],
          "03-front-balance-of-mind-and-heart.png", "03-back-process-over-perfection-moons.png",
          ["brain", "heart", "moon"],
          "<p>Brain and heart on the front, a column of moons on the back for everyone still working it out.</p>",
          "Process over perfection."),
    drop2("Somewhere in a Calmer Place Hoodie", ["Sport Grey", "Sand", "Light Blue", "White"],
          "04-front-sumi-ink-skull-mountain-landscape.png", "04-back-calmer-place-mountain-landscape.png",
          ["skull", "mountains", "japanese"],
          "<p>Physically here, mentally in the mountains: the ink-wash skull up front, the mountain scroll "
          "on the back.</p>",
          "Somewhere in a calmer place."),
    drop2("A Quieter Mind Hoodie", ["Black", "Charcoal", "Navy"],
          "05-front-a-quieter-mind-space-cat.png", "05-back-space-cat-helmet-blueprint.png",
          ["cat", "astronaut", "moon"],
          "<p>The astronaut cat watching the moon on the front, the helmet blueprint on the back.</p>",
          "A quieter mind. A brighter tomorrow."),
    own_lane("In My Own Lane Hoodie", ["Black", "Light Pink", "White"], "01-in-my-own-lane.png",
             ["pink", "airbrush", "butterflies"],
             "<p>Airbrush script, butterflies and gold chains, big on the back.</p>", "In my own lane."),
    own_lane("Butterfly Effect Hoodie", ["Carolina Blue", "Light Pink", "Sport Grey", "White"],
             "02-butterfly-effect.png", ["portrait", "butterflies", "pink"],
             "<p>The pink-shades portrait with hot pink butterflies, big on the back.</p>",
             "Small moves. Big energy."),
    own_lane("Lucky Charm Hoodie", ["Black", "Light Pink", "White"], "03-lucky-charm.png",
             ["pink", "dice", "glam"],
             "<p>Gloss, grills, dice and cherries in one glam collage, big on the back.</p>", "Made my own luck."),
    own_lane("Sunflower Soul Hoodie", ["Royal", "Sand", "White"], "04-sunflower-soul.png",
             ["portrait", "sunflowers", "floral"],
             "<p>A portrait crowned with sunflowers and roses, big on the back.</p>", "Always growing."),
    own_lane("Color Me Bold Hoodie", ["Black", "White", "Sport Grey"], "05-color-me-bold.png",
             ["portrait", "afro", "gold"],
             "<p>Big hair, gold hoops and bursts of color, big on the back.</p>", "Bold looks good on you."),
    own_lane("Crown & Curls Hoodie", ["Maroon", "Sand", "White"], "06-crown-and-curls.png",
             ["portrait", "curls", "crown"],
             "<p>Curls, white glasses and a hand-drawn gold crown, big on the back.</p>", "Wear the crown."),
    own_lane("Pink Crown Hoodie", ["Black", "Light Pink", "White"], "07-pink-crown.png",
             ["portrait", "crown", "pink"],
             "<p>The pop-art portrait with gold frames and a pink crown, big on the back.</p>", "Crowned by me."),
    own_lane("Sisterhood Hoodie", ["Military Green", "Sand", "Sport Grey"], "08-sisterhood.png",
             ["portrait", "sisterhood", "gold"],
             "<p>Three queens, one frame, big on the back.</p>", "Better together."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    run(PRODUCTS, "18500", ap.parse_args().apply)


def run(products, model, apply):
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")
    existing = {p["title"] for page in (1, 2) for p in
                api.get(f"/shops/{shop['id']}/products.json?limit=50&page={page}")["data"]}
    bp = next(b for b in api.get("/catalog/blueprints.json") if model == (b.get("model") or "").strip())
    cache = {}

    for spec in products:
        if spec["title"] in existing:
            print(f"- {spec['title']}: already exists, skipping")
            continue
        provider, variants, colors = pick_provider(api, bp, {"colors": dict.fromkeys(spec["colors"])})
        chosen = [v for v in variants
                  if v["options"].get("color") in colors and v["options"].get("size") in TEE_SIZES]
        sizes = placeholder_sizes(api, bp["id"], provider["id"])
        layout = {pos: how(name, *sizes[pos]) for pos, name, how in spec["prints"]}
        missing = [c for c in spec["colors"] if c not in colors]
        print(f"- {spec['title']}: via {provider['title']}, {len(chosen)} variants"
              + (f", missing colors {missing}" if missing else "")
              + "; " + ", ".join(f"{pos} {round(l['scale'] * sizes[pos][0])}px wide" for pos, l in layout.items()))
        if not apply:
            continue

        placeholders = [{"position": pos, "images": [dict(id=upload(api, name, cache), angle=0, **layout[pos])]}
                        for pos, name, _ in spec["prints"]]
        product = api.post(f"/shops/{shop['id']}/products.json", {
            "title": spec["title"],
            "description": spec["description"],
            "tags": spec["tags"],
            "blueprint_id": bp["id"],
            "print_provider_id": provider["id"],
            "variants": [{"id": v["id"], "is_enabled": True,
                          "price": spec["price"] + (XXL_UPCHARGE if v["options"]["size"] == "2XL" else 0)}
                         for v in chosen],
            "print_areas": [{"variant_ids": [v["id"] for v in chosen], "placeholders": placeholders}],
        })
        profit = [(v["price"] - v["cost"]) / 100 for v in product["variants"] if v.get("is_enabled")]
        api.post(f"/shops/{shop['id']}/products/{product['id']}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True,
        })
        print(f"  created + published, profit before shipping ${min(profit):.2f}-${max(profit):.2f}")


if __name__ == "__main__":
    main()
