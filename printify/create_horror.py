"""Horror Collection: a tee and a hoodie for each design in designs/print-horror.

Tee: Bella+Canvas 3001 (provider 29), full art on the front. Hoodie: Gildan 18500 (provider 39), full art on
the back. Black only: the art has dark outlines and shading made for a black garment. Tees $27, hoodies $37.
Every product is tagged "Horror", which is the rule of the Shopify smart collection "Horror Collection".

Products are created in Printify as drafts. Publishing to Shopify is a separate step so the mockups can be
checked first.

Usage:
    python3 printify/create_horror.py                                # dry run
    python3 printify/create_horror.py --apply --commit SHA           # create drafts in Printify
    python3 printify/create_horror.py --publish                      # publish the existing drafts to Shopify
"""

import argparse
import os
import sys
import time

from PIL import Image

from create_products import TEE_SIZES, XXL_UPCHARGE, Printify
from fit import MARGIN, ROOT, placeholder_sizes

Image.MAX_IMAGE_PIXELS = None
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-horror/{name}"
ART = ROOT / "designs" / "print-horror"
TAGS = ["Horror", "horror collection", "halloween", "spooky"]

TEE = dict(kind="Tee", blueprint=12, provider=29, price=2700, position="front",
           features=["Full-color front print", "Soft, lightweight 100% combed cotton", "Retail unisex fit"])
HOODIE = dict(kind="Hoodie", blueprint=77, provider=39, price=3700, position="back",
              features=["Full-color back print", "Medium-heavy cotton/poly blend, fleece-lined",
                        "Double-lined hood, front pouch pocket", "Unisex fit, size up for oversized"])
COLORS = ["Black"]

DESIGNS = [
    ("01-dead-tired", "Dead Tired", ["skeleton", "coffee", "funny"],
     "A skeleton slumped over a diner counter, coffee in hand, alarm clock screaming under a blood moon.",
     "Running on caffeine and spite."),
    ("02-this-house-eats-people", "This House Eats People", ["haunted house", "monster"],
     "A haunted house with a mouth full of fangs and a tongue for a welcome mat.", "No refunds on the tour."),
    ("03-dont-open-the-basement", "Don't Open the Basement", ["basement", "slasher"],
     "A chained, bloodstained door, caution tape and an evidence tag. You were warned.", "Seriously. Don't."),
    ("04-sweet-dreams-dont-live-here", "Sweet Dreams Don't Live Here", ["gothic", "victorian", "ghost"],
     "A moonlit Victorian bedroom behind lace curtains, framed in gothic filigree and roses.",
     "Something else does."),
    ("05-resting-witch-face", "Resting Witch Face", ["witch", "black cat", "funny"],
     "A black cat in a witch hat, perched on a crescent moon with a crystal ball and lavender.",
     "It's not a mood. It's a craft."),
    ("06-i-came-i-screamed-i-left", "I Came. I Screamed. I Left.", ["motel", "slasher", "funny"],
     "Three comic panels: a roadside motel, one very open mouth, and taillights in the rearview.",
     "Checkout was early."),
    ("07-sweet-dreams-are-cancelled", "Sweet Dreams Are Cancelled", ["insomnia", "moon", "funny"],
     "A crying crescent moon, a cut cord and a hot-pink CANCELLED stamp across the night.",
     "Rescheduled to never."),
    ("08-dead-inside-dressed-to-kill", "Dead Inside, Dressed to Kill", ["skeleton", "fashion", "goth"],
     "A skeleton in a pinstripe suit and red heels, working the runway past the paparazzi.",
     "Emotionally unavailable. Visually unforgettable."),
    ("09-horror-club", "Horror Club", ["vintage", "skeleton", "werewolf"],
     "A vintage club badge: a skeleton hand and a werewolf claw shaking on it.", "Members only. Membership is forever."),
    ("10-horror-movies-raised-me", "Horror Movies Raised Me", ["retro", "vhs", "monster", "80s"],
     "A furry monster babysitting a kid in front of a glowing TV, VHS tapes and popcorn included.",
     "And honestly? I turned out fine."),
    ("11-sleep-deprived-horror-obsessed", "Sleep Deprived & Horror Obsessed", ["insomnia", "coffee", "movies"],
     "A bloodshot eye with a film reel for a pupil, over a cracked mug of coffee and a midnight forest.",
     "One more movie."),
    ("12-sleep-is-for-people-without-nightmares", "Sleep Is for People Without Nightmares",
     ["insomnia", "psychedelic", "70s"],
     "A trippy 70s bedroom melting into neon swirls under a lamp that's seen too much.", "Lights stay on."),
]


def place(name, area_w, area_h, top=0.02):
    """Largest size that fits the print area, centered horizontally, starting near the top."""
    with Image.open(ART / f"{name}.png") as im:
        ratio = im.height / im.width * area_w / area_h   # art height as a fraction of area height at full width
    scale = MARGIN * min(1.0, (1 - top) / ratio)
    return dict(x=0.5, y=round(top + scale * ratio / 2, 4), scale=round(scale, 4), angle=0)


def all_products(api, shop):
    out, page = {}, 1
    while True:
        d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        out.update({p["title"]: p for p in d["data"]})
        if page >= d["last_page"]:
            return out
        page += 1


def titles():
    return [(slug, name, f"{name} {spec['kind']}", spec, tags, intro, line)
            for slug, name, tags, intro, line in DESIGNS for spec in (TEE, HOODIE)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="create the products in Printify (unpublished)")
    ap.add_argument("--publish", action="store_true", help="publish the created products to Shopify")
    ap.add_argument("--only", nargs="+", metavar="SLUG", help="limit to these design slugs, e.g. 01 03")
    ap.add_argument("--commit", help="git commit holding designs/print-horror (pushed to GitHub)")
    args = ap.parse_args()
    if args.apply and not args.commit:
        sys.exit("--apply needs --commit")

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    existing = all_products(api, shop)
    uploads = {}

    for slug, name, title, spec, tags, intro, line in titles():
        if args.only and not slug.startswith(tuple(args.only)):
            continue
        if args.publish:
            p = existing.get(title)
            if not p:
                print(f"miss  {title}: not created yet")
                continue
            api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
                "title": True, "description": True, "images": True, "variants": True,
                "tags": True, "keyFeatures": True, "shipping_template": True})
            print(f"pub   {title}")
            time.sleep(20)  # Printify publish rate limit
            continue
        if title in existing:
            print(f"skip  {title}: already exists ({existing[title]['id']})")
            continue
        catalog = api.get(f"/catalog/blueprints/{spec['blueprint']}/print_providers/{spec['provider']}/variants.json")["variants"]
        chosen = [v for v in catalog if v["options"].get("color") in COLORS and v["options"].get("size") in TEE_SIZES]
        spot = place(slug, *placeholder_sizes(api, spec["blueprint"], spec["provider"])[spec["position"]])
        print(f"{'make' if args.apply else 'plan'}  {title}: {len(chosen)} variants, {spec['position']} "
              f"art {spot['scale']:.0%} wide, ${spec['price'] / 100:.0f}")
        if not args.apply:
            continue
        if slug not in uploads:
            uploads[slug] = api.post("/uploads/images.json", {
                "file_name": f"{slug}.png", "url": RAW.format(commit=args.commit, name=f"{slug}.png")})["id"]
        features = "".join(f"<li>{f}</li>" for f in [*spec["features"], "Printed to order just for you"])
        product = api.post(f"/shops/{shop}/products.json", {
            "title": title,
            "description": f"<p>{intro}</p><ul>{features}</ul><p><em>{line}</em></p>",
            "tags": [spec["kind"].lower(), *TAGS, *tags],
            "blueprint_id": spec["blueprint"],
            "print_provider_id": spec["provider"],
            "variants": [{"id": v["id"], "is_enabled": True,
                          "price": spec["price"] + (XXL_UPCHARGE if v["options"]["size"] == "2XL" else 0)}
                         for v in chosen],
            "print_areas": [{"variant_ids": [v["id"] for v in chosen], "placeholders": [
                {"position": spec["position"], "images": [dict(id=uploads[slug], **spot)]}]}],
        })
        cost = [v["cost"] for v in product["variants"] if v["is_enabled"]]
        print(f"      created {product['id']}, cost ${min(cost) / 100:.2f}-${max(cost) / 100:.2f}")


if __name__ == "__main__":
    main()
