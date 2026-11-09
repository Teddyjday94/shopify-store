"""Player Two collection: nerdy designs as back-print tees and hoodies.

Same blanks, colors and prices as the Relatable line (tee: Bella+Canvas 3001 via provider 29, Black and
Dark Grey Heather, $24; hoodie: Gildan 18500 via provider 39, Black and Dark Heather, $40; 2XL +$3).
The art is a transparent PNG from designs/player-two-src, printed large on the back, top-aligned.
Monster of the Week is held back (resembles a trademarked character).

Usage: python3 printify/create_player_two.py [--apply] [--only SLUG]
"""

import argparse
import base64
import os
import time

from PIL import Image

from create_products import XXL_UPCHARGE, Printify
from fit import placeholder_sizes

SRC = os.path.join(os.path.dirname(__file__), "..", "designs", "player-two-src")
SIZES = {"S", "M", "L", "XL", "2XL"}

DESIGNS = [
    ("01-main-character-syndrome", "Main Character Syndrome", "Plot armor sold separately.",
     "A battle-worn hero, a red cape and a mechanical hand reaching out of the panel.",
     ["anime", "manga", "main character"]),
    ("02-no-signal", "No Signal", "No signal in this universe.",
     "A lone astronaut, a glowing vending machine and a planet that doesn't answer back.",
     ["space", "astronaut", "anime", "sci-fi"]),
    ("03-critical-failure", "Critical Failure", "Rolled a natural 1. Again.",
     "A shattered d20 landing on a 1, wrapped in smoke, gold filigree and a skull.",
     ["dnd", "d20", "tabletop", "dice", "rpg"]),
    ("04-phd-in-overthinking", "PhD in Overthinking", "Thesis pending. Forever.",
     "Varsity letters for the most advanced degree in thinking about it one more time.",
     ["overthinking", "varsity", "funny"]),
    ("05-talk-nerdy-to-me", "Talk Nerdy to Me", "Footnotes welcome.",
     "Script lettering and a varsity NERDY, for people who light up at a good fun fact.",
     ["nerd", "varsity", "funny"]),
    ("06-i-paused-my-game", "I Paused My Game to Be Here", "Unsaved progress. You're welcome.",
     "Pixel lettering and arcade colors for the ultimate act of love: hitting pause.",
     ["gaming", "gamer", "arcade", "funny"]),
    ("07-my-other-outfit-is-also-black", "My Other Outfit Is Also Black", "Wardrobe: solved.",
     "Distressed cream lettering for anyone whose entire closet is one color.",
     ["goth", "black", "funny"]),
    ("08-forbidden-knowledge", "Forbidden Knowledge", "Some books read you back.",
     "A hooded sorceress, a burning spellbook and gothic gold lettering.",
     ["fantasy", "witch", "magic", "gothic"]),
    ("09-out-of-orbit", "Out of Orbit", "Currently unreachable.",
     "A lone traveler on a cliff, a red planet and a floating city overhead.",
     ["space", "astronaut", "anime", "sci-fi"]),
    ("10-final-boss-energy", "Final Boss Energy", "Phase two loading.",
     "A battle-scarred giant mech under a blood moon.",
     ["mech", "anime", "gaming", "robot"]),
    ("11-respawn-pending", "Respawn Pending", "Two hearts left. Probably fine.",
     "An adventurer at a glowing save crystal in moonlit ruins, with pixel hearts below.",
     ["gaming", "rpg", "fantasy", "pixel"]),
]

TEE = dict(kind="Tee", blueprint=12, provider=29, price=2700, colors={"Black", "Dark Grey Heather"},
           features=["Big back print", "Soft, lightweight 100% combed cotton", "Retail unisex fit"])
HOODIE = dict(kind="Hoodie", blueprint=77, provider=39, price=3700, colors={"Black", "Dark Heather"},
              features=["Big back print", "Medium-heavy cotton/poly blend, fleece-lined",
                        "Double-lined hood, front pouch pocket", "Unisex fit, size up for oversized"])
EDGE, TOP = 0.92, 0.03   # art fills at most 92% of the back's width or height, starting 3% from the top


def place(img_w, img_h, area_w, area_h):
    ratio = (img_h / img_w) * (area_w / area_h)     # art height as a fraction of area height, per unit width
    scale = round(min(EDGE, (1 - TOP - 0.02) / ratio), 4)
    return dict(x=0.5, y=round(TOP + scale * ratio / 2, 4), scale=scale, angle=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    existing, page = set(), 1
    while True:
        d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        existing |= {p["title"] for p in d["data"]}
        if page >= d["last_page"]:
            break
        page += 1
    uploads = {}
    for slug, name, line, intro, extra_tags in DESIGNS:
        if args.only and args.only != slug:
            continue
        path = os.path.join(SRC, f"{slug}.png")
        w, h = Image.open(path).size
        for spec in (TEE, HOODIE):
            title = f"{name} {spec['kind']}"
            if title in existing:
                print(f"skip  {title}")
                continue
            catalog = api.get(f"/catalog/blueprints/{spec['blueprint']}/print_providers/{spec['provider']}/variants.json")["variants"]
            chosen = [v for v in catalog if v["options"].get("color") in spec["colors"] and v["options"].get("size") in SIZES]
            aw, ah = placeholder_sizes(api, spec["blueprint"], spec["provider"])["back"]
            spot = place(w, h, aw, ah)
            print(f"{'make' if args.apply else 'plan'}  {title}: {len(chosen)} variants, art {spot['scale']:.0%} of back width, {w}x{h}")
            if not args.apply:
                continue
            if path not in uploads:
                with open(path, "rb") as f:
                    uploads[path] = api.post("/uploads/images.json", {
                        "file_name": os.path.basename(path), "contents": base64.b64encode(f.read()).decode()})["id"]
            features = "".join(f"<li>{x}</li>" for x in [*spec["features"], "Printed to order just for you"])
            product = api.post(f"/shops/{shop}/products.json", {
                "title": title,
                "description": f"<p>{intro}</p><ul>{features}</ul><p><em>{line}</em></p>",
                "tags": [spec["kind"].lower(), "player two", "nerdy", *extra_tags],
                "blueprint_id": spec["blueprint"],
                "print_provider_id": spec["provider"],
                "variants": [{"id": v["id"], "is_enabled": True,
                              "price": spec["price"] + (XXL_UPCHARGE if v["options"]["size"] == "2XL" else 0)} for v in chosen],
                "print_areas": [{"variant_ids": [v["id"] for v in chosen], "placeholders": [
                    {"position": "back", "images": [dict(id=uploads[path], **spot)]}]}],
            })
            api.post(f"/shops/{shop}/products/{product['id']}/publish.json", {
                "title": True, "description": True, "images": True, "variants": True,
                "tags": True, "keyFeatures": True, "shipping_template": True})
            cost = [v["cost"] for v in product["variants"] if v["is_enabled"]]
            print(f"      created {product['id']}, cost ${min(cost) / 100:.2f}-${max(cost) / 100:.2f}")
            time.sleep(20)


if __name__ == "__main__":
    main()
