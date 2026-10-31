"""Create a women's-fit version of every tee (Next Level 3900 boyfriend tee, Monster Digital).

Each copies the unisex tee's artwork and price, and gets colors that suit its art. Listings are titled
"<Name> Women's Tee" and tagged "womens" for the Women's collection.

Usage:
    python3 printify/make_womens.py            # dry run
    python3 printify/make_womens.py --apply
"""

import argparse
import os

from clone_product import build
from create_products import Printify

BLUEPRINT, PROVIDER = 14, 29
FIT_NOTE = "<p><strong>Women's fit:</strong> a relaxed boyfriend cut in soft cotton. Prefer it roomier? Grab the unisex version.</p>"

TWO_INK = {"Solid Black": "white", "Solid Dark Chocolate": "white", "Solid Cardinal Red": "white",
           "Solid White": "black", "Solid Natural": "black"}
OWN_LANE = dict(TWO_INK, **{"Solid Light Pink": "black"})
DROP1_TWO_INK = dict(TWO_INK, **{"Heather Grey": "black"})
DARK = {"Solid Black": None, "Solid Dark Chocolate": None, "Solid Cardinal Red": None}
LIGHT = {"Solid White": None, "Solid Natural": None, "Heather Grey": None, "Solid Light Olive": None}

COLORS = {
    "In My Own Lane Tee": OWN_LANE, "Butterfly Effect Tee": OWN_LANE, "Lucky Charm Tee": OWN_LANE,
    "Sunflower Soul Tee": OWN_LANE, "Color Me Bold Tee": OWN_LANE, "Crown & Curls Tee": OWN_LANE,
    "Pink Crown Tee": OWN_LANE, "Sisterhood Tee": OWN_LANE,
    "A Quieter Mind Tee": DARK, "Same Mind Brighter Days Tee": DARK, "Systems Still Functional Tee": DARK,
    "Somewhere in a Calmer Place Tee": LIGHT, "Balance Tee": LIGHT, "Same Chaos Different Day Tee": LIGHT,
    "Ships in 6–7 Business Days Tee": LIGHT,
    "Not AI. Just Tired. Tee": DROP1_TWO_INK, "Odysseus Layover Tee": DROP1_TWO_INK,
}


def womens_title(title):
    return title[: -len(" Tee")] + " Women's Tee"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    apply = ap.parse_args().apply

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    products = [p for page in (1, 2) for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]]
    existing = {p["title"] for p in products}

    for p in products:
        if p["title"] not in COLORS or not (p.get("external") or {}).get("id"):
            continue
        title = womens_title(p["title"])
        if title in existing:
            print(f"skip  {title}: already exists")
            continue
        src = api.get(f"/shops/{shop}/products/{p['id']}.json")
        sizes = {v["title"].split(" / ")[-1] if p["blueprint_id"] == 12 else v["title"].split(" / ")[0]
                 for v in src["variants"]}
        base = min(v["price"] for v in src["variants"] if v["is_enabled"] and "2XL" not in v["title"])
        body, missing = build(api, src, BLUEPRINT, PROVIDER, COLORS[p["title"]], base)
        print(f"{'make' if apply else 'plan'}  {title}: {sorted(COLORS[p['title']])}, ${base / 100:.0f}, "
              f"{len(body['variants'])} variants" + (f" (missing {missing})" if missing else ""))
        if not apply:
            continue
        body.update(title=title, description=src["description"] + FIT_NOTE, tags=src["tags"] + ["womens"])
        new = api.post(f"/shops/{shop}/products.json", body)
        api.post(f"/shops/{shop}/products/{new['id']}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True,
        })
        cost = [v["cost"] for v in new["variants"] if v["is_enabled"]]
        print(f"      created {new['id']}, cost ${min(cost) / 100:.2f}-${max(cost) / 100:.2f}")


if __name__ == "__main__":
    main()
