"""Create drop-2 products (front + back prints) in Printify and publish them to Shopify.

Print files are fetched by Printify from the public GitHub repo at a pinned commit.

Usage:
    python3 printify/create_drop2.py            # dry run
    python3 printify/create_drop2.py --apply    # create + publish
"""

import argparse
import os

from create_products import Printify, TEE_SIZES, XXL_UPCHARGE, pick_provider

RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/{folder}/{name}"
FOLDER = "print-drop2"
COMMIT = "6975476fb478998c96c25b928696813167646f51"

# Files 01-05 are full 3:4 canvases with built-in margins, so they fill most of the print area.
FULL = dict(x=0.5, y=0.5, scale=0.85)
FEATURES = ("<ul><li>Front and back print</li>"
            "<li>Soft, lightweight 100% combed cotton</li>"
            "<li>Retail unisex fit</li>"
            "<li>Printed to order just for you</li></ul>")


def tee(title, colors, front, back, tags, intro, signoff):
    return dict(
        title=title, price=3600, model="3001", colors={c: "x" for c in colors},
        prints={"front": (front, FULL), "back": (back, FULL)},
        tags=["t-shirt", "drop 002"] + tags,
        description=f"{intro}{FEATURES}<p><em>{signoff}</em></p>",
    )


PRODUCTS = [
    dict(
        title="Systems Still Functional Tee",
        price=3600,
        model="3001",
        colors={"Black": "x"},
        prints={
            "front": ("06-front-error-skull.png", FULL),
            "back": ("06-back-systems-still-functional.png", FULL),
        },
        tags=["t-shirt", "glitch", "skull", "error", "tired", "funny", "drop 002"],
        description=(
            "<p>Boot sequence complete. Anomalies detected. Proceeding anyway.</p>"
            "<p>Front: a glitched-out skull mid-crash. Back: the status report nobody asked for. "
            "Status: tired. Function: operational.</p>"
            "<ul><li>Front and back print</li>"
            "<li>Soft, lightweight 100% combed cotton</li>"
            "<li>Retail unisex fit</li>"
            "<li>Printed to order just for you</li></ul>"
            "<p><em>Tired but here anyway.</em></p>"
        ),
    ),
    tee("Same Chaos Different Day Tee", ["White", "Natural", "Ash"],
        "01-front-engraved-moon-miner.png", "01-back-lunar-phases-same-chaos-different-day.png",
        ["moon", "astronaut", "space", "engraved", "minimalist"],
        "<p>Clocking in. Mining the moon. Again.</p>"
        "<p>Front: an astronaut chipping away at a crescent moon, drawn like an old engraving. "
        "Back: the lunar phases, top to bottom, with the only update anyone needs.</p>",
        "Same chaos. Different day."),
    tee("Same Mind Brighter Days Tee", ["Black"],
        "02-front-grunge-samurai-red-sakura-sun.png", "02-back-sakura-moon-same-mind-brighter-days.png",
        ["samurai", "skeleton", "sakura", "japanese", "coffee"],
        "<p>A skeleton samurai, a red sun, a cup of something hot. Composure, achieved.</p>"
        "<p>Front: the samurai on his coffee break under falling sakura. Back: a moonlit cherry tree "
        "panel with 平常心 (a calm, everyday mind).</p>",
        "Same mind. Brighter days."),
    tee("Balance Tee", ["White", "Natural"],
        "03-front-balance-of-mind-and-heart.png", "03-back-process-over-perfection-moons.png",
        ["brain", "heart", "anatomy", "moon", "minimalist"],
        "<p>Mind: overthink, analyze, plan, worry, repeat. Heart: feel, create, risk, trust, live.</p>"
        "<p>Front: brain and heart, split down the middle. Back: a column of moons and orbits for "
        "everyone still working it out.</p>",
        "Process over perfection."),
    tee("Somewhere in a Calmer Place Tee", ["White", "Natural"],
        "04-front-sumi-ink-skull-mountain-landscape.png", "04-back-calmer-place-mountain-landscape.png",
        ["skull", "mountains", "sumi ink", "japanese", "landscape"],
        "<p>Physically here. Mentally in the mountains.</p>"
        "<p>Front: a skull turned ink-wash landscape, with pines, a pagoda and a red sun. "
        "Back: a stepped mountain scroll with どこかでまた (somewhere, again).</p>",
        "Somewhere in a calmer place."),
    tee("A Quieter Mind Tee", ["Black"],
        "05-front-a-quieter-mind-space-cat.png", "05-back-space-cat-helmet-blueprint.png",
        ["cat", "astronaut", "space", "moon", "blueprint"],
        "<p>One cat. One helmet. One very large moon.</p>"
        "<p>Front: an astronaut cat sitting on a rooftop ledge, watching the moon. Back: the "
        "helmet blueprint, with a checklist: explore, adapt, observe, repeat.</p>",
        "A quieter mind. A brighter tomorrow."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    run(PRODUCTS, COMMIT, FOLDER, args.apply)


def run(products, commit, folder, apply):
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")
    existing = {p["title"] for p in api.get(f"/shops/{shop['id']}/products.json?limit=50")["data"]}
    blueprints = api.get("/catalog/blueprints.json")

    for spec in products:
        if spec["title"] in existing:
            print(f"- {spec['title']}: already exists, skipping")
            continue
        bp = next(b for b in blueprints if spec["model"] in (b.get("model") or ""))
        provider, variants, colors = pick_provider(api, bp, spec)
        chosen = [v for v in variants
                  if v["options"].get("color") in colors and v["options"].get("size") in TEE_SIZES]
        positions = set.intersection(*({p["position"] for p in v["placeholders"]} for v in chosen))
        print(f"- {spec['title']}: {bp['title']} via {provider['title']}, {len(chosen)} variants, "
              f"print areas {sorted(positions)}")
        missing = set(spec["prints"]) - positions
        if missing:
            raise SystemExit(f"  provider lacks print areas {missing}")
        if not apply:
            continue

        placeholders = []
        for position, (name, place) in spec["prints"].items():
            image = api.post("/uploads/images.json",
                             {"file_name": name, "url": RAW.format(commit=commit, folder=folder, name=name)})
            placeholders.append({"position": position, "images": [dict(id=image["id"], angle=0, **place)]})
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
        costs = [(v["price"] - v["cost"]) / 100 for v in product["variants"] if v.get("is_enabled")]
        print(f"  created id {product['id']}, profit before shipping ${min(costs):.2f}-${max(costs):.2f}")
        api.post(f"/shops/{shop['id']}/products/{product['id']}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True,
        })
        print("  published to Shopify")


if __name__ == "__main__":
    main()