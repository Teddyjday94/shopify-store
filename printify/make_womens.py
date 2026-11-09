"""Create a women's-fit version of every tee (Next Level 3900 boyfriend tee, Monster Digital).

Each copies the unisex tee's artwork and price, and gets colors that suit its art. Listings are titled
"<Name> Women's Tee" and tagged "womens" for the Women's collection.

Usage:
    python3 printify/make_womens.py            # dry run
    python3 printify/make_womens.py --apply
"""

import argparse
import os
import time

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

DARK_GREY = {"Solid Black": None, "Solid Heavy Metal": None}
BLACK = {"Solid Black": None}
WITH_NAVY = {"Solid Black": None, "Solid Midnight Navy": None}
WITH_RED = {"Solid Black": None, "Solid Cardinal Red": None}
WITH_BROWN = {"Solid Black": None, "Solid Dark Chocolate": None}

RELATABLE = ["People: One Star", "Emotional Support Snacks", "The Internet Is Broken", "Not My Department",
             "Built on Bad Decisions", "50% IDK 50% IDC", "One Drink Was a Working Title", "Emotional Support Husband",
             "I Don't Start Drama", "Making Plans I'll Probably Cancel", "My Social Battery", "I Have No Filter",
             "Things I Do in My Spare Time"]
PLAYER_TWO = ["Respawn Pending", "Final Boss Energy", "Out of Orbit", "Forbidden Knowledge",
              "My Other Outfit Is Also Black", "I Paused My Game to Be Here", "Talk Nerdy to Me", "PhD in Overthinking",
              "Main Character Syndrome", "Critical Failure", "No Signal"]
CHRISTMAS = ["Holly Jolly Chaos", "The Gift Is Me", "Dear Santa, Bring Bourbon", "Suck It Up Buttercup",
             "On the Naughty List Again"]
IMMORTALIZED = {"Masterless": WITH_RED, "Queen Forever": WITH_NAVY,
                "Long Live the King": WITH_RED, "Going With the Flow": BLACK, "Above It All": WITH_BROWN,
                "Fallen, Not Finished": WITH_RED, "Born Ready": WITH_NAVY, "One Way Ferry": WITH_NAVY,
                "Sleep Paralysis Club": WITH_RED, "Rise From Ruin": WITH_RED, "Lead the Charge": WITH_RED}
# Front-and-back prints cost about $6.50 more on this blank, so those sell for $29 (2XL $32) instead of the
# unisex $26; everything else keeps the unisex price.
PRICE = {f"{n} Tee": 2900 for n in IMMORTALIZED}

COLORS = {
    "In My Own Lane Tee": OWN_LANE, "Butterfly Effect Tee": OWN_LANE, "Lucky Charm Tee": OWN_LANE,
    "Sunflower Soul Tee": OWN_LANE, "Color Me Bold Tee": OWN_LANE, "Crown & Curls Tee": OWN_LANE,
    "Pink Crown Tee": OWN_LANE, "Sisterhood Tee": OWN_LANE,
    "A Quieter Mind Tee": DARK, "Same Mind Brighter Days Tee": DARK, "Systems Still Functional Tee": DARK,
    "Somewhere in a Calmer Place Tee": LIGHT, "Balance Tee": LIGHT, "Same Chaos Different Day Tee": LIGHT,
    "Ships in 6–7 Business Days Tee": LIGHT,
    "Not AI. Just Tired. Tee": DROP1_TWO_INK, "Odysseus Layover Tee": DROP1_TWO_INK,
    **{f"{n} Tee": DARK_GREY for n in RELATABLE + PLAYER_TWO},
    **{f"{n} Tee": BLACK for n in CHRISTMAS},
    **{f"{n} Tee": c for n, c in IMMORTALIZED.items()},
}


def womens_title(title):
    return title[: -len(" Tee")] + " Women's Tee"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", help="only the unisex tee with this exact title")
    args = ap.parse_args()
    apply = args.apply

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    products, page = [], 1
    while True:
        d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        products += d["data"]
        if page >= d["last_page"]:
            break
        page += 1
    existing = {p["title"]: p for p in products}

    for p in products:
        if p["title"] not in COLORS or not (p.get("external") or {}).get("id") or args.only and p["title"] != args.only:
            continue
        title = womens_title(p["title"])
        if title in existing:
            done = existing[title]
            if apply and not (done.get("external") or {}).get("id") and not done["is_locked"]:
                api.post(f"/shops/{shop}/products/{done['id']}/publish.json", {
                    "title": True, "description": True, "images": True, "variants": True,
                    "tags": True, "keyFeatures": True, "shipping_template": True,
                })
                print(f"publish  {title}: created earlier, publishing now")
            else:
                print(f"skip  {title}: already exists")
            continue
        src = api.get(f"/shops/{shop}/products/{p['id']}.json")
        sizes = {v["title"].split(" / ")[-1] if p["blueprint_id"] == 12 else v["title"].split(" / ")[0]
                 for v in src["variants"]}
        base = PRICE.get(p["title"]) or min(v["price"] for v in src["variants"] if v["is_enabled"] and "2XL" not in v["title"])
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
        time.sleep(20)  # stay under Printify's publish rate limit
        print(f"      created {new['id']}, cost ${min(cost) / 100:.2f}-${max(cost) / 100:.2f}")


if __name__ == "__main__":
    main()
