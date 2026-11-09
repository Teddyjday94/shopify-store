"""Create the Relatable Collection: a tee and a hoodie for each design, big print on the front.

Print files: designs/print-relatable (prep_relatable.py). Cream/white type with dark outlines, so dark
garments only. Existing products (by title) are skipped, unless --refresh: then their print file is swapped for
the current one (same placement) and the mockups republished.

Usage:
    python3 printify/create_relatable.py --commit SHA                      # dry run
    python3 printify/create_relatable.py --commit SHA --apply
    python3 printify/create_relatable.py --commit SHA --apply --refresh
"""

import argparse
import os
import time

from PIL import Image

from create_products import TEE_SIZES, XXL_UPCHARGE, Printify
from fit import ROOT, placeholder_sizes

RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-relatable/{name}"
ART = ROOT / "designs" / "print-relatable"
TAGS = ["relatable collection", "relatable", "funny"]

TEE = dict(kind="Tee", blueprint=12, provider=29, price=3000, colors=["Black", "Dark Grey Heather"],
           features=["Big front print", "Soft, lightweight 100% combed cotton", "Retail unisex fit"])
HOODIE = dict(kind="Hoodie", blueprint=77, provider=39, price=4500, colors=["Black", "Dark Heather"],
              features=["Big front print", "Medium-heavy cotton/poly blend, fleece-lined",
                        "Double-lined hood, front pouch pocket", "Unisex fit, size up for oversized"])

DESIGNS = [
    ("01-things-i-do-in-my-spare-time", "Things I Do in My Spare Time",
     "A checklist of hobbies: overthink, procrastinate, find new hobbies, add to cart.", "All of the above."),
    ("02-i-have-no-filter", "I Have No Filter", "A rusted warning sign for the honest friend.", "Proceed at your own risk."),
    ("03-social-battery", "My Social Battery", "Social battery at 1%, rendered as a very tired battery icon.", "Please charge later."),
    ("04-my-kind-of-leg-day", "My Kind of Leg Day", "A basket of fried drumsticks in college-varsity lettering.", "Fried, not squatted."),
    ("05-making-plans-ill-cancel", "Making Plans I'll Probably Cancel", "Vintage banner lettering for the optimistic flake.", "Rain check pending."),
    ("06-i-dont-start-drama", "I Don't Start Drama", "Brush lettering and a little crown for the group chat historian.", "I just recap it."),
    ("07-emotional-support-husband", "Emotional Support Husband", "A cold one, a laurel wreath and a job title.", "Reporting for duty."),
    ("08-one-drink-working-title", "One Drink Was a Working Title", "A whiskey glass and a plan that changed.", "Subject to revision."),
    ("09-built-character", "Built Character", "Mountains, a red sun and an honest footnote.", "Trauma helped."),
    ("10-currently-avoiding", "Currently Avoiding", "A coffee-stained checklist: people, responsibilities, phone calls, my inbox.", "All of it."),
    ("11-idk-idc", "50% IDK 50% IDC", "Varsity numbers for a perfectly balanced attitude.", "The math checks out."),
    ("12-built-on-bad-decisions", "Built on Bad Decisions", "Script lettering over a globe, for the self-made.", "And some questionable luck."),
    ("13-not-my-department", "Not My Department", "Distressed lettering for anyone who knows their job description.", "But I'll still judge it."),
    ("14-internet-is-broken", "The Internet Is Broken", "A glitching monitor with x-ed out eyes.", "So I'm outside today."),
    ("15-emotional-support-snacks", "Emotional Support Snacks", "A fully stocked vending machine, open all hours.", "Always available."),
    ("16-people-one-star", "People: One Star", "A one-star review of humanity.", "Very bad. Would not recommend."),
]

# Designs pulled from the store; scripts skip them so they are never recreated.
RETIRED = {"04-my-kind-of-leg-day", "09-built-character", "10-currently-avoiding"}
DESIGNS = [d for d in DESIGNS if d[0] not in RETIRED]


def front_place(name, w, h, max_w=0.80, max_h=0.92):
    with Image.open(ART / name) as im:
        ratio = im.height / im.width * w / h     # print height (as a fraction of the area) per unit width
    scale = round(min(max_w, max_h / ratio), 4)
    return dict(x=0.5, y=round(0.03 + scale * ratio / 2, 4), scale=scale)


def swap(api, shop, pid, image_id):
    """Point every placed image at image_id, keeping position and size, then republish the mockups."""
    full = api.get(f"/shops/{shop}/products/{pid}.json")
    areas = [{"variant_ids": a["variant_ids"], "placeholders": [
        {"position": ph["position"], "images": [dict(id=image_id, x=i["x"], y=i["y"], scale=i["scale"], angle=i["angle"])
                                                for i in ph["images"]]}
        for ph in a["placeholders"] if ph["images"]]} for a in full["print_areas"]]
    api.call("PUT", f"/shops/{shop}/products/{pid}.json", json={"print_areas": areas})
    api.post(f"/shops/{shop}/products/{pid}/publish.json", {
        "title": False, "description": False, "images": True, "variants": False,
        "tags": False, "keyFeatures": False, "shipping_template": False})
    time.sleep(20)


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
    uploads = {}
    for slug, name, intro, line in DESIGNS:
        art = f"{slug}.png"
        for spec in (TEE, HOODIE):
            title = f"{name} {spec['kind']}"
            if title in existing:
                if not args.refresh:
                    print(f"skip  {title}")
                    continue
                print(f"{'swap' if args.apply else 'plan'}  {title}: new print file")
                if args.apply:
                    if art not in uploads:
                        uploads[art] = api.post("/uploads/images.json", {"file_name": art, "url": RAW.format(commit=args.commit, name=art)})["id"]
                    swap(api, shop, existing[title]["id"], uploads[art])
                continue
            catalog = api.get(f"/catalog/blueprints/{spec['blueprint']}/print_providers/{spec['provider']}/variants.json")["variants"]
            chosen = [v for v in catalog if v["options"].get("color") in spec["colors"] and v["options"].get("size") in TEE_SIZES]
            w, h = placeholder_sizes(api, spec["blueprint"], spec["provider"])["front"]
            place = front_place(art, w, h)
            print(f"{'make' if args.apply else 'plan'}  {title}: {len(chosen)} variants, print {place['scale']:.0%} of front width")
            if not args.apply:
                continue
            if art not in uploads:
                uploads[art] = api.post("/uploads/images.json", {"file_name": art, "url": RAW.format(commit=args.commit, name=art)})["id"]
            features = "".join(f"<li>{f}</li>" for f in [*spec["features"], "Printed to order just for you"])
            product = api.post(f"/shops/{shop}/products.json", {
                "title": title,
                "description": f"<p>{intro}</p><ul>{features}</ul><p><em>{line}</em></p>",
                "tags": [spec["kind"].lower()] + TAGS,
                "blueprint_id": spec["blueprint"],
                "print_provider_id": spec["provider"],
                "variants": [{"id": v["id"], "is_enabled": True,
                              "price": spec["price"] + (XXL_UPCHARGE if v["options"]["size"] == "2XL" else 0)} for v in chosen],
                "print_areas": [{"variant_ids": [v["id"] for v in chosen], "placeholders": [
                    {"position": "front", "images": [dict(id=uploads[art], angle=0, **place)]}]}],
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
