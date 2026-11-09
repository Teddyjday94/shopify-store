"""Christmas hoodies in Maroon and Forest Green: swap in the shading-restored back print and enable the colors.

The original back prints had every near-black pixel keyed out, so on colored fabric the shadows showed the
fabric through. designs/print-xmas/<slug>-back-shaded.png fills the inside of the art with black again (no
visible change on Black). The new print keeps each hoodie's current placement. Variants are published; images
are not, so the labeled back-first photos stay (photos for the new colors are added after).

Usage: python3 printify/xmas_hoodie_colors.py [--apply] [--commit SHA]
"""

import argparse
import os
import time

from create_products import Printify

RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-xmas/{name}"
SLUGS = {"On the Naughty List Again": "01-on-the-naughty-list-again", "Suck It Up Buttercup": "02-suck-it-up-buttercup",
         "Dear Santa, Bring Bourbon": "03-dear-santa-bring-bourbon", "The Gift Is Me": "04-the-gift-is-me",
         "Holly Jolly Chaos": "05-holly-jolly-chaos"}
ADD, SIZES = ("Maroon", "Forest Green"), {"S", "M", "L", "XL", "2XL"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--commit", default="d6ea11a")
    ap.add_argument("--from", dest="start", default="", help="skip designs before this name")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    products, page = [], 1
    while True:
        d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        products += d["data"]
        if page >= d["last_page"]:
            break
        page += 1
    names = list(SLUGS)
    for name in names[names.index(args.start) if args.start else 0:]:
        slug = SLUGS[name]
        p = next(x for x in products if x["title"] == f"{name} Hoodie")
        print(f"{'swap' if args.apply else 'plan'}  {p['title']}: shaded back print + {list(ADD)}", flush=True)
        if not args.apply:
            continue
        img = api.post("/uploads/images.json", {"file_name": f"{slug}-back-shaded.png",
                                                "url": RAW.format(commit=args.commit, name=f"{slug}-back-shaded.png")})
        full = api.get(f"/shops/{shop}/products/{p['id']}.json")
        areas = []
        for a in full["print_areas"]:
            phs = []
            for ph in a["placeholders"]:
                if not ph["images"]:
                    continue
                i = ph["images"][0]
                new = dict(id=img["id"], x=i["x"], y=i["y"], scale=i["scale"], angle=i["angle"]) if ph["position"] == "back" \
                    else dict(id=i["id"], x=i["x"], y=i["y"], scale=i["scale"], angle=i["angle"])
                phs.append({"position": ph["position"], "images": [new]})
            areas.append({"variant_ids": a["variant_ids"], "placeholders": phs})
        price = max(v["price"] for v in full["variants"] if v["is_enabled"])
        variants = []
        for v in full["variants"]:
            color, size = v["title"].split(" / ")[0], v["title"].split(" / ")[-1]
            on = v["is_enabled"] or (color in ADD and size in SIZES)
            variants.append({"id": v["id"], "is_enabled": on, "price": price if on else v["price"]})
        api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json={"print_areas": areas, "variants": variants})
        for wait in (0, 120, 300, 600):
            time.sleep(wait)
            try:
                api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
                    "title": False, "description": False, "images": False, "variants": True,
                    "tags": False, "keyFeatures": False, "shipping_template": False})
                break
            except RuntimeError as e:
                print(f"      publish refused ({e}); waiting", flush=True)
        time.sleep(15)


if __name__ == "__main__":
    main()
