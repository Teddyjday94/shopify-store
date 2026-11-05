"""Create home & accessories products: wraparound mugs (11oz/15oz) and round ceramic ornaments.

Print files come from designs/print-home (rendered by designs/src/render_home.js). Products are tagged
"accessory" so they land in the Home & Accessories collection; Christmas ones are also tagged for the
Christmas Collection. Existing products (by title) are skipped, unless --refresh is given: then their
print file is swapped for the current one and the mockups are republished.

Usage:
    python3 printify/create_home.py --commit SHA                      # dry run
    python3 printify/create_home.py --commit SHA --apply
    python3 printify/create_home.py --commit SHA --apply --refresh    # also update existing art
"""

import argparse
import os
import time

from create_products import Printify

RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-home/{name}"

MUG = dict(kind="Mug", blueprint=478, provider=39, prices={"11oz": 1800, "15oz": 2100},
           features=["Glossy white ceramic, design wraps around both sides",
                     "Available in 11oz and 15oz", "Dishwasher and microwave safe, lead and BPA free"])
ORNAMENT = dict(kind="Ornament", blueprint=531, provider=99, prices={"Circle / One Size": 1500},
                features=["Round glossy ceramic, 3mm thick", "Printed on the front",
                          "Gold-toned hanging string included"])

XMAS = [
    ("01-on-the-naughty-list-again", "On the Naughty List Again", "Worth it."),
    ("02-suck-it-up-buttercup", "Suck It Up Buttercup", "It's Christmas. Act like it."),
    ("03-dear-santa-bring-bourbon", "Dear Santa, Bring Bourbon", "Skip the socks."),
    ("04-the-gift-is-me", "The Gift Is Me", "You're welcome."),
    ("05-holly-jolly-chaos", "Holly Jolly Chaos", "Merry and mildly feral."),
]
SLOGANS = [
    ("21-not-ai-just-tired", "Not AI. Just Tired.", "Verified human. Low battery."),
    ("22-same-chaos-different-day", "Same Chaos Different Day", "Refill and repeat."),
    ("23-do-not-perceive-me", "Do Not Perceive Me", "Coffee first. Eye contact later."),
    ("24-currently-elsewhere", "Currently Elsewhere", "Will respond upon return."),
]


def specs():
    for slug, name, line in XMAS:
        tags = ["christmas collection", "christmas", "holiday", "accessory", "home"]
        yield MUG, f"{name} Mug", f"{slug}-mug.png", tags + ["mug"], line, \
            f"The {name} design wrapped around a mug, on black, both sides."
        yield ORNAMENT, f"{name} Ornament", f"{slug}-ornament.png", tags + ["ornament"], line, \
            f"The {name} design on a round ceramic ornament, for a tree with a sense of humor."
    for slug, name, line in SLOGANS:
        yield MUG, f"{name} Mug", f"{slug}-mug.png", ["accessory", "home", "mug", "funny"], line, \
            f"\"{name}\" in bold black type on both sides of a white mug."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    existing = {p["title"]: p for page in (1, 2, 3, 4) for p in
                api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]}
    for spec, title, art, tags, line, intro in specs():
        if title in existing:
            if not (args.refresh and "christmas" in tags):
                print(f"skip  {title}")
                continue
            print(f"{'swap' if args.apply else 'plan'}  {title}: new print file")
            if args.apply:
                pid = existing[title]["id"]
                img = api.post("/uploads/images.json", {"file_name": art, "url": RAW.format(commit=args.commit, name=art)})["id"]
                full = api.get(f"/shops/{shop}/products/{pid}.json")
                areas = [{"variant_ids": a["variant_ids"], "placeholders": [
                    {"position": ph["position"], "images": [dict(id=img, x=0.5, y=0.5, scale=1, angle=0)]}
                    for ph in a["placeholders"] if ph["images"]]} for a in full["print_areas"]]
                api.call("PUT", f"/shops/{shop}/products/{pid}.json", json={"print_areas": areas})
                api.post(f"/shops/{shop}/products/{pid}/publish.json", {
                    "title": False, "description": False, "images": True, "variants": False,
                    "tags": False, "keyFeatures": False, "shipping_template": False})
                time.sleep(20)
            continue
        catalog = api.get(f"/catalog/blueprints/{spec['blueprint']}/print_providers/{spec['provider']}/variants.json")["variants"]
        chosen = [v for v in catalog if v["title"] in spec["prices"]]
        print(f"{'make' if args.apply else 'plan'}  {title}: {[v['title'] for v in chosen]}")
        if not args.apply:
            continue
        img = api.post("/uploads/images.json", {"file_name": art, "url": RAW.format(commit=args.commit, name=art)})["id"]
        features = "".join(f"<li>{f}</li>" for f in [*spec["features"], "Printed to order just for you"])
        product = api.post(f"/shops/{shop}/products.json", {
            "title": title,
            "description": f"<p>{intro}</p><ul>{features}</ul><p><em>{line}</em></p>",
            "tags": tags,
            "blueprint_id": spec["blueprint"],
            "print_provider_id": spec["provider"],
            "variants": [{"id": v["id"], "is_enabled": True, "price": spec["prices"][v["title"]]} for v in chosen],
            "print_areas": [{"variant_ids": [v["id"] for v in chosen], "placeholders": [
                {"position": "front", "images": [dict(id=img, x=0.5, y=0.5, scale=1, angle=0)]}]}],
        })
        api.post(f"/shops/{shop}/products/{product['id']}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True,
        })
        cost = [v["cost"] for v in product["variants"] if v["is_enabled"]]
        print(f"      created, cost ${min(cost) / 100:.2f}-${max(cost) / 100:.2f}")
        time.sleep(20)  # Printify publish rate limit


if __name__ == "__main__":
    main()
