"""Doomsday Drop (limited, 2026-11-25 to 2026-12-18): the owner's cleaned designs (Doomsday Mask, Tree Spirit, Doomsday Incursion dropped; A Stolen Life added) as a Black front-print tee
(Bella+Canvas 3001, provider 29, $27) and a Black back-print hoodie (Gildan 18500 at SwiftPOD, provider 39, $37).
Print files: designs/doomsday-2026/print/<slug>.png (Kittl 4x upscales, background keyed out; see prep.py).
Tags "doomsday drop" + "limited drop" feed the Doomsday Drop collection. No franchise names anywhere.
Usage: python3 printify/create_doomsday.py [--apply] [--only SLUG] --commit SHA   (ids -> printify/doomsday.json)"""
import argparse, json, os, time
from PIL import Image
from create_products import Printify
from fit import placeholder_sizes

RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/doomsday-2026/print/{name}"
SRC = os.path.join(os.path.dirname(__file__), "..", "designs", "doomsday-2026", "print")
DONE = os.path.join(os.path.dirname(__file__), "doomsday.json")
SIZES = {"S", "M", "L", "XL", "2XL"}
EDGE, TOP = 0.97, 0.03
NOTE = "<p><strong>Doomsday Drop: limited run, available until December 18.</strong></p>"

DESIGNS = [
    ("crest-L", "L Crest", "A silver L on a green-and-black shield, laurels below and steel finials above. Swear allegiance.", ["crest", "heraldry"]),
    ("doom-in-our-time", "Doom in Our Time", "Jagged acid-green lettering, about as subtle as a prophecy.", ["typography", "lettering"]),
    ("inevitable-throne-hood", "The Inevitable Doomsday", "A hooded ruler on a throne of conquered crowns and helmets. The decree is final.", ["villain", "throne"]),
    ("king-of-3-realms", "King of the 3 Realms", "A hooded king on a throne forged from swords, three moons behind him and green lightning splitting the sky.", ["villain", "throne", "moons"]),
    ("no-gods-only-doom", "No Gods, Only Doom", "An iron gauntlet shattering a golden halo, framed by roses and a banner.", ["villain", "roses", "tattoo"]),
    ("a-stolen-life", "A Stolen Life", "A vintage-poster sunset: a boy in suspenders holding up a dented trash-can lid like a shield, a couple silhouetted in a glowing doorway. A chance at peace.", ["vintage", "retro poster", "americana"]),
]
TEE = dict(kind="Tee", blueprint=12, provider=29, price=2700, position="front", colors={"Black"},
           features=["Full-color front print", "Soft, lightweight 100% combed cotton", "Retail unisex fit"])
HOODIE = dict(kind="Hoodie", blueprint=77, provider=39, price=3700, position="back", colors={"Black"},
              features=["Big back print", "Medium-heavy cotton/poly blend, fleece-lined",
                        "Double-lined hood, front pouch pocket", "Unisex fit, size up for oversized"])


def place(img_w, img_h, area_w, area_h):
    ratio = (img_h / img_w) * (area_w / area_h)
    scale = round(min(EDGE, (1 - TOP - 0.01) / ratio), 4)
    return dict(x=0.5, y=round(TOP + scale * ratio / 2, 4), scale=scale, angle=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--commit", required=True)
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = 29509655
    done = json.load(open(DONE)) if os.path.exists(DONE) else {}
    uploads = {}
    for slug, name, intro, extra in DESIGNS:
        if args.only and slug != args.only:
            continue
        w, h = Image.open(os.path.join(SRC, f"{slug}.png")).size
        for spec in (TEE, HOODIE):
            title = f"{name} {spec['kind']}"
            if title in done:
                print("skip", title)
                continue
            catalog = api.get(f"/catalog/blueprints/{spec['blueprint']}/print_providers/{spec['provider']}/variants.json")["variants"]
            chosen = [v for v in catalog if v["options"].get("color") in spec["colors"] and v["options"].get("size") in SIZES]
            aw, ah = placeholder_sizes(api, spec["blueprint"], spec["provider"])[spec["position"]]
            spot = place(w, h, aw, ah)
            print(f"{'make' if args.apply else 'plan'}  {title}: {len(chosen)} variants, art {spot['scale']:.0%} wide, "
                  f"{w / (spot['scale'] * aw / 300):.0f} DPI", flush=True)
            if not args.apply:
                continue
            if slug not in uploads:
                uploads[slug] = api.post("/uploads/images.json", {
                    "file_name": f"doomsday-{slug}.png", "url": RAW.format(commit=args.commit, name=f"{slug}.png")})["id"]
            features = "".join(f"<li>{x}</li>" for x in [*spec["features"], "Printed to order just for you"])
            product = api.post(f"/shops/{shop}/products.json", {
                "title": title,
                "description": f"<p>{intro}</p>{NOTE}<ul>{features}</ul>",
                "tags": [spec["kind"].lower(), "doomsday drop", "limited drop", "dark fantasy", *extra],
                "blueprint_id": spec["blueprint"], "print_provider_id": spec["provider"],
                "variants": [{"id": v["id"], "is_enabled": True, "price": spec["price"]} for v in chosen],
                "print_areas": [{"variant_ids": [v["id"] for v in chosen], "placeholders": [
                    {"position": spec["position"], "images": [dict(id=uploads[slug], **spot)]}]}],
            })
            api.post(f"/shops/{shop}/products/{product['id']}/publish.json", {
                "title": True, "description": True, "images": True, "variants": True,
                "tags": True, "keyFeatures": True, "shipping_template": True})
            cost = [v["cost"] for v in product["variants"] if v["is_enabled"]]
            done[title] = {"printify": product["id"], "design": slug, "cost": [min(cost), max(cost)]}
            json.dump(done, open(DONE, "w"), indent=1)
            print(f"      created {product['id']}, cost ${min(cost) / 100:.2f}-${max(cost) / 100:.2f}", flush=True)
            time.sleep(15)


if __name__ == "__main__":
    main()
