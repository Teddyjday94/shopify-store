"""Create the Butterfly Effect all-over-print hoodie (Printify AOP pullover, MWW On Demand).

Every panel is printed, so each one gets a black base; the portrait goes big on the back, the
butterfly from the same artwork sits on each upper sleeve and small on the left chest.

The product is created unpublished so its real cost can be checked; pass --publish with a price
to set it and push it to Shopify.

Usage:
    python3 printify/create_aop_hoodie.py                      # dry run
    python3 printify/create_aop_hoodie.py --apply              # create (unpublished), print costs
    python3 printify/create_aop_hoodie.py --publish 6800       # set price (cents) and publish
"""

import argparse
import base64
import io
import os

from PIL import Image, ImageOps

from create_products import XXL_UPCHARGE, Printify
from fit import FIT_DIR, fill, placeholder_sizes, upload

TITLE = "Butterfly Effect All-Over Hoodie"
BLUEPRINT = 450
PROVIDER = "MWW On Demand"
SIZES = ["S", "M", "L", "XL", "2XL"]
BACK_ART = "02-butterfly-effect.png"
BUTTERFLY = "02-butterfly-only.png"

DESCRIPTION = (
    "<p>The pink-shades portrait printed big across the back, with her butterflies landing on both "
    "sleeves and the chest. Printed edge to edge on a jet-black base.</p>"
    "<ul><li>All-over print: every panel is printed before it's sewn</li>"
    "<li>Soft brushed polyester fleece</li><li>Lined hood, front pouch pocket</li>"
    "<li>Unisex fit, size up for oversized</li><li>Made to order just for you</li></ul>"
    "<p><em>Small moves. Big energy.</em></p>")
TAGS = ["hoodie", "all-over print", "own lane", "portrait", "butterflies", "pink"]


def upload_image(api, name, image, cache):
    if name not in cache:
        buf = io.BytesIO()
        image.save(buf, "PNG", optimize=True)
        cache[name] = api.post("/uploads/images.json", {
            "file_name": name, "contents": base64.b64encode(buf.getvalue()).decode()})["id"]
    return cache[name]


def black(api, w, h, cache):
    # A solid panel in the placeholder's shape, oversized slightly so every size is covered.
    ratio = h / w
    return dict(id=upload_image(api, f"black-{round(ratio, 3)}.png", Image.new("RGB", (200, round(200 * ratio)), "black"),
                                cache), x=0.5, y=0.5, scale=1.05, angle=0)


def layout(api, sizes, cache):
    butterfly = Image.open(FIT_DIR / BUTTERFLY)
    art = {
        "back": [dict(id=upload(api, BACK_ART, cache), angle=0, **back_place(*sizes["back"]))],
        "right_sleeve": [dict(id=upload_image(api, "butterfly-r.png", butterfly, cache), x=0.5, y=0.3, scale=0.5, angle=0)],
        "left_sleeve": [dict(id=upload_image(api, "butterfly-l.png", ImageOps.mirror(butterfly), cache),
                             x=0.5, y=0.3, scale=0.5, angle=0)],
        "front": [dict(id=upload_image(api, "butterfly-r.png", butterfly, cache), x=0.7, y=0.25, scale=0.2, angle=0)],
    }
    return [{"position": pos, "images": [black(api, w, h, cache)] + art.get(pos, [])}
            for pos, (w, h) in sizes.items()]


def back_place(w, h):
    # As large as the panel allows, nudged down so the hood doesn't cover the top of the art.
    place = fill(BACK_ART, w, h)
    place["scale"] = round(place["scale"] * 0.92, 4)
    place["y"] = 0.54
    return place


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--publish", type=int, metavar="PRICE_CENTS")
    args = ap.parse_args()

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")
    products = api.get(f"/shops/{shop['id']}/products.json?limit=50")["data"]
    existing = next((p for p in products if p["title"] == TITLE), None)

    if args.publish:
        path = f"/shops/{shop['id']}/products/{existing['id']}.json"
        variants = [{"id": v["id"], "price": args.publish + (XXL_UPCHARGE if v["title"] == "2XL" else 0)}
                    for v in existing["variants"] if v["is_enabled"]]
        api.call("PUT", path, json={"variants": variants})
        api.post(f"{path[:-5]}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True,
        })
        print(f"published {TITLE} at ${args.publish / 100:.0f}")
        return

    provider = next(p for p in api.get(f"/catalog/blueprints/{BLUEPRINT}/print_providers.json")
                    if p["title"] == PROVIDER)
    variants = [v for v in api.get(f"/catalog/blueprints/{BLUEPRINT}/print_providers/{provider['id']}/variants.json")[
        "variants"] if v["title"] in SIZES]
    sizes = placeholder_sizes(api, BLUEPRINT, provider["id"])
    print(f"{TITLE}: {PROVIDER}, sizes {[v['title'] for v in variants]}, panels {sorted(sizes)}")
    if existing:
        print("already exists")
        return
    if not args.apply:
        return

    cache = {}
    product = api.post(f"/shops/{shop['id']}/products.json", {
        "title": TITLE,
        "description": DESCRIPTION,
        "tags": TAGS,
        "blueprint_id": BLUEPRINT,
        "print_provider_id": provider["id"],
        "variants": [{"id": v["id"], "is_enabled": True, "price": 6800} for v in variants],
        "print_areas": [{"variant_ids": [v["id"] for v in variants], "background": "#000000",
                         "placeholders": layout(api, sizes, cache)}],
    })
    print(f"created {product['id']} (unpublished)")
    for v in product["variants"]:
        if v["is_enabled"]:
            print(f"  {v['title']}: cost ${v['cost'] / 100:.2f}")


if __name__ == "__main__":
    main()
