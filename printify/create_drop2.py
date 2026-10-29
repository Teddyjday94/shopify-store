"""Create drop-2 products (front + back prints) in Printify and publish them to Shopify.

Print files are fetched by Printify from the public GitHub repo at a pinned commit.

Usage:
    python3 printify/create_drop2.py            # dry run
    python3 printify/create_drop2.py --apply    # create + publish
"""

import argparse
import os

from create_products import Printify, TEE_SIZES, XXL_UPCHARGE, pick_provider

RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-drop2/{name}"
COMMIT = "ec7a985f4dec29f474179241bb0c5050029e7ee6"

PRODUCTS = [
    dict(
        title="Systems Still Functional Tee",
        price=3600,
        model="3001",
        colors={"Black": "x"},
        prints={
            "front": ("06-front-error-skull.png", dict(x=0.5, y=0.5, scale=0.78)),
            "back": ("06-back-systems-still-functional.png", dict(x=0.5, y=0.5, scale=0.82)),
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
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")
    existing = {p["title"] for p in api.get(f"/shops/{shop['id']}/products.json?limit=50")["data"]}
    blueprints = api.get("/catalog/blueprints.json")

    for spec in PRODUCTS:
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
        if not args.apply:
            continue

        placeholders = []
        for position, (name, place) in spec["prints"].items():
            image = api.post("/uploads/images.json",
                             {"file_name": name, "url": RAW.format(commit=COMMIT, name=name)})
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
