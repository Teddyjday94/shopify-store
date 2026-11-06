"""Create the higher-margin extras: posters and desk mats (Immortalized + Christmas art), phone cases
(Relatable slogans) and collection sweatpants.

Print files come from designs/print-wall, print-case (designs/src/render_wallart.py) and print-pants
(designs/src/render_sweatpants.js); they are uploaded to Printify as base64. Each variant gets a print
area whose scale makes the art cover that size, so smaller sizes crop only background.
Existing products (by title) are skipped.

Usage:
    python3 printify/create_extras.py                 # dry run
    python3 printify/create_extras.py --apply [--only posters deskmats cases pants]
"""

import argparse
import base64
import os
import time

from PIL import Image

from create_products import Printify
from create_relatable import DESIGNS as RELATABLE

DESIGNS = os.path.join(os.path.dirname(__file__), "..", "designs")

IMMORTALIZED = [
    ("01-lead-the-charge", "Lead the Charge"), ("02-rise-from-ruin", "Rise From Ruin"),
    ("03-sleep-paralysis-club", "Sleep Paralysis Club"), ("04-one-way-ferry", "One Way Ferry"),
    ("05-born-ready", "Born Ready"), ("06-fallen-not-finished", "Fallen, Not Finished"),
    ("07-above-it-all", "Above It All"), ("08-going-with-the-flow", "Going With the Flow"),
    ("09-long-live-the-king", "Long Live the King"), ("10-queen-forever", "Queen Forever"),
    ("11-nine-tails", "Nine Tails"), ("12-masterless", "Masterless"),
]
XMAS = [
    ("01-on-the-naughty-list-again", "On the Naughty List Again"), ("02-suck-it-up-buttercup", "Suck It Up Buttercup"),
    ("03-dear-santa-bring-bourbon", "Dear Santa, Bring Bourbon"), ("04-the-gift-is-me", "The Gift Is Me"),
    ("05-holly-jolly-chaos", "Holly Jolly Chaos"),
]

POSTER = dict(blueprint=282, provider=234, ratio=0.75,
              prices={'11″ x 14″ / Matte': 2000, '12″ x 18″ / Matte': 2400,
                      '18″ x 24″ / Matte': 2800, '24″ x 36″ / Matte': 3800},
              features=["Museum-grade matte paper, 175gsm", "Archival inks, no glare",
                        "Ships rolled in a protective tube", "Frame not included"])
DESKMAT = dict(blueprint=488, provider=1, ratio=9921 / 5197,
               prices={'12" × 18"': 2800, '12" × 22"': 3000, '16" × 32"': 4000},
               features=["Smooth polyester top for mouse and pen", "Non-slip natural rubber base, 4mm",
                         "Stitched edges that will not fray", "Sized for laptop, keyboard or full setup"])
CASE = dict(blueprint=269, provider=99, ratio=1500 / 2700, prices=None, price=2800,
            features=["Two-layer tough case: hard shell over an impact-absorbing lining",
                      "Glossy finish, full-wrap print", "Wireless charging compatible",
                      "iPhone 11 through 18 and Samsung Galaxy S21 through S26"])
PANTS = dict(blueprint=1398, provider=39,
             prices={"S": 4200, "M": 4200, "L": 4200, "XL": 4200, "2XL": 4800, "3XL": 5000},
             colors={"Black": "white", "Navy": "white", "Sport Grey": "black", "Sand": "black", "Ash": "black"},
             features=["Gildan Heavy Blend fleece, 50% cotton / 50% polyester",
                       "Elastic waistband with drawcord, elastic cuffs", "Side pockets",
                       "Same maker as our hoodies, so a set ships together"])
PANT_SETS = [
    ("core", "Elsewhere Sweatpants", ["drop 002", "elsewhere"], "Matches anything in the Drop 002 and Currently Elsewhere hoodies."),
    ("relatable", "Relatable Sweatpants", ["relatable collection", "relatable"], "Built for the Relatable hoodies. Comfort first, plans later."),
    ("own-lane", "Own Lane Sweatpants", ["own lane"], "The bottom half of an Own Lane set."),
    ("immortalized", "Immortalized Sweatpants", ["drop 004", "immortalized"], "The bottom half of an Immortalized set."),
    ("christmas", "Christmas Sweatpants", ["christmas collection", "christmas", "holiday"], "Pair them with a Christmas hoodie for the full holiday fit."),
]


def cover_scale(img_ratio, area_w, area_h):
    """Printify scale (art width / area width) that makes the art cover the area."""
    return max(1.0, img_ratio / (area_w / area_h))


def upload(api, path, cache={}):
    if path not in cache:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        cache[path] = api.post("/uploads/images.json", {"file_name": os.path.basename(path), "contents": data})["id"]
    return cache[path]


def cover_areas(chosen, img, ratio):
    groups = {}
    for v in chosen:
        ph = v["placeholders"][0]
        s = round(cover_scale(ratio, ph["width"], ph["height"]), 4)
        groups.setdefault((ph["position"], s), []).append(v["id"])
    return [{"variant_ids": ids, "placeholders": [{"position": pos, "images": [
        dict(id=img, x=0.5, y=0.5, scale=s, angle=0)]}]} for (pos, s), ids in groups.items()]


def specs():
    for group, art, coll in ((IMMORTALIZED, "immortalized", ["immortalized", "drop 004"]),
                             (XMAS, "christmas", ["christmas collection", "christmas", "holiday"])):
        for slug, name in group:
            yield "posters", POSTER, f"{name} Poster", f"print-wall/{slug}-poster.jpg", \
                coll + ["accessory", "home", "poster", "wall art"], \
                f"The {name} artwork as a matte art print, in four sizes from 11×14 to 24×36."
            yield "deskmats", DESKMAT, f"{name} Desk Mat", f"print-wall/{slug}-deskmat.jpg", \
                coll + ["accessory", "home", "desk mat"], \
                f"The {name} artwork across a full desk mat, in three sizes."
    for slug, name, _, line in RELATABLE:
        yield "cases", CASE, f"{name} Phone Case", f"print-case/{slug}-case.jpg", \
            ["relatable collection", "relatable", "accessory", "phone case", "funny"], \
            f"The {name} design on a tough phone case. {line}"
    for slug, title, tags, intro in PANT_SETS:
        yield "pants", PANTS, title, slug, tags + ["sweatpants", "bottoms", "unisex"], \
            f"Fleece sweatpants with ELSEWHERE running down the left leg. {intro}"


def build(api, kind, spec, art, catalog):
    if kind == "pants":
        chosen = [v for v in catalog if v["options"]["color"] in spec["colors"] and v["options"]["size"] in spec["prices"]]
        variants = [{"id": v["id"], "is_enabled": True, "price": spec["prices"][v["options"]["size"]]} for v in chosen]
        areas = []
        for ink in ("white", "black"):
            ids = [v["id"] for v in chosen if spec["colors"][v["options"]["color"]] == ink]
            path = os.path.join(DESIGNS, "print-pants", f"{art}-{ink}.png")
            w, h = Image.open(path).size
            ph = chosen[0]["placeholders"][0]  # left_leg_front, 1200 x 4800
            scale = (0.80 * 4800 * w / h) / 1200
            img = upload(api, path)
            areas.append({"variant_ids": ids, "placeholders": [{"position": "left_leg_front", "images": [
                dict(id=img, x=0.5, y=0.46, scale=round(scale, 4), angle=0)]}]})
        return variants, areas
    if spec["prices"]:
        chosen = [v for v in catalog if v["title"] in spec["prices"]]
        variants = [{"id": v["id"], "is_enabled": True, "price": spec["prices"][v["title"]]} for v in chosen]
    else:
        chosen = catalog
        variants = [{"id": v["id"], "is_enabled": True, "price": spec["price"]} for v in chosen]
    img = upload(api, os.path.join(DESIGNS, art))
    return variants, cover_areas(chosen, img, spec["ratio"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", nargs="+", choices=["posters", "deskmats", "cases", "pants"])
    ap.add_argument("--title", nargs="+", help="limit to these exact titles")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    existing = set()
    page = 1
    while True:
        d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        existing |= {p["title"] for p in d["data"]}
        if page >= d["last_page"]:
            break
        page += 1
    catalogs = {}
    for kind, spec, title, art, tags, intro in specs():
        if args.only and kind not in args.only:
            continue
        if args.title and title not in args.title:
            continue
        if title in existing:
            print(f"skip  {title}")
            continue
        key = (spec["blueprint"], spec["provider"])
        if key not in catalogs:
            catalogs[key] = api.get(f"/catalog/blueprints/{key[0]}/print_providers/{key[1]}/variants.json")["variants"]
        print(f"{'make' if args.apply else 'plan'}  {title}")
        if not args.apply:
            continue
        variants, areas = build(api, kind, spec, art, catalogs[key])
        features = "".join(f"<li>{f}</li>" for f in [*spec["features"], "Printed to order just for you"])
        product = api.post(f"/shops/{shop}/products.json", {
            "title": title, "description": f"<p>{intro}</p><ul>{features}</ul>", "tags": tags,
            "blueprint_id": spec["blueprint"], "print_provider_id": spec["provider"],
            "variants": variants, "print_areas": areas,
        })
        api.post(f"/shops/{shop}/products/{product['id']}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True,
        })
        cost = [v["cost"] for v in product["variants"] if v["is_enabled"]]
        print(f"      created {product['id']}, {len(cost)} variants, cost ${min(cost) / 100:.2f}-${max(cost) / 100:.2f}")
        time.sleep(20)  # Printify publish rate limit


if __name__ == "__main__":
    main()
