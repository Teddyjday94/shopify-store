"""Second Christmas batch (Naughty List): tee, women's tee, hoodie, mug and ornament per design.

Art: designs/print-xmas2/<slug>.png (transparent, upscaled 4x), mugs/ornaments from
designs/print-home/<slug>-{mug,ornament}.png (designs/src/render_home_xmas2.py).
Apparel is Black only (cream lettering), front print on tees, back print on hoodies, at the store's prices.
Apparel publishes without photos; labeled photos are added in Shopify afterwards.

Usage: python3 printify/create_xmas2.py --commit SHA [--only SLUG]
"""
import argparse, json, os, time
from pathlib import Path
from PIL import Image
from create_products import Printify

SHOP = 29509655
ROOT = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{c}/designs/{d}/{n}"
OUT = Path(__file__).with_name("xmas2.json")
SIZES = ["S", "M", "L", "XL", "2XL"]
MARGIN = 0.97
BASE_TAGS = ["christmas", "christmas collection", "holiday", "christmas gift"]

DESIGNS = [
    ("06-santa-knows", "Santa Knows (And So Do I)", ["santa", "funny"],
     "Retro lettering under a Santa hat, with holly and a little sparkle.", "Everyone's on a list."),
    ("07-christmas-calories-dont-count", "Christmas Calories Don't Count", ["cookies", "gingerbread", "funny"],
     "Groovy red, cream and green lettering and one very confident gingerbread man.", "Seconds, then thirds."),
    ("08-may-your-days-be-merry", "May Your Days Be Merry", ["merry", "holly"],
     "Vintage holiday lettering with holly berries: may your days be merry (and your to-do list be short).",
     "Merry, with fewer errands."),
    ("09-hot-cocoa-fixes-almost-everything", "Hot Cocoa Fixes (Almost) Everything", ["hot cocoa", "cozy"],
     "Bubbly retro lettering and a steaming mug of cocoa with marshmallows and a candy cane.",
     "Extra marshmallows, please."),
    ("10-dear-santa-i-can-explain", "Dear Santa, I Can Explain", ["santa", "naughty", "funny"],
     "Script lettering, a Santa hat and a confession in progress: Dear Santa... I can explain...",
     "It was like that when I got here."),
    ("11-its-fine-im-fine", "It's Fine, I'm Fine, Everything Is Fine", ["funny", "christmas lights"],
     "Groovy red, cream and green lettering strung with Christmas lights: it's fine, I'm fine, everything is fine.",
     "Totally fine. Ask again in January."),
]
KINDS = [
    dict(key="tee", title="{n} Tee", bp=12, pp=29, price=2700, pos="front", tags=["tee"], images=False,
         bullets=["Full-color front print", "Soft, lightweight 100% combed cotton", "Retail unisex fit"]),
    dict(key="womens", title="{n} Women's Tee", bp=466, pp=39, price=2700, pos="front", tags=["tee", "womens"], images=False,
         bullets=["Full-color front print", "Midweight 100% cotton that holds its shape", "Classic women's fit"]),
    dict(key="hoodie", title="{n} Hoodie", bp=77, pp=39, price=3700, pos="back", tags=["hoodie"], images=False,
         bullets=["Full-color back print", "Medium-heavy cotton/poly blend, fleece-lined", "Unisex fit, size up for oversized"]),
    dict(key="mug", title="{n} Mug", bp=478, pp=39, prices={"11oz": 1700, "15oz": 1700}, tags=["accessory", "home", "mug"], images=True,
         bullets=["Glossy white ceramic, design wraps around both sides", "Available in 11oz and 15oz",
                  "Dishwasher and microwave safe, lead and BPA free"]),
    dict(key="ornament", title="{n} Ornament", bp=531, pp=99, prices={"Circle / One Size": 1700}, tags=["accessory", "home", "ornament"], images=True,
         bullets=["Round glossy ceramic, 3mm thick", "Printed on the front", "Gold-toned hanging string included"]),
]


def fill(iid, w, h, area):
    aw, ah = area
    scale = MARGIN * min(1.0, (ah / aw) / (h / w))
    hf = scale * (h / w) / (ah / aw)
    return dict(id=iid, x=0.5, y=round((1 - MARGIN) / 2 + hf / 2, 4), scale=round(scale, 4), angle=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--only")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    done = json.loads(OUT.read_text()) if OUT.exists() else {}
    for slug, name, tags, intro, line in DESIGNS:
        if args.only and args.only != slug:
            continue
        art_name = f"{slug}.png"
        w, h = Image.open(ROOT / "designs" / "print-xmas2" / art_name).size
        art_id = None
        for k in KINDS:
            pkey = f"{slug}-{k['key']}"
            if pkey in done:
                continue
            title = k["title"].format(n=name)
            catalog = api.get(f"/catalog/blueprints/{k['bp']}/print_providers/{k['pp']}/variants.json")["variants"]
            if "prices" in k:
                chosen = [v for v in catalog if v["title"] in k["prices"]]
                variants = [{"id": v["id"], "price": k["prices"][v["title"]], "is_enabled": True} for v in chosen]
                fname = f"{slug}-{k['key']}.png"
                img = api.post("/uploads/images.json", {"file_name": fname, "url": RAW.format(c=args.commit, d="print-home", n=fname)})["id"]
                placement = dict(id=img, x=0.5, y=0.5, scale=1, angle=0)
                pos = "front"
            else:
                chosen = [v for v in catalog if v["options"].get("color") == "Black" and v["options"].get("size") in SIZES]
                variants = [{"id": v["id"], "price": k["price"], "is_enabled": True} for v in chosen]
                area = max(((p["width"], p["height"]) for v in chosen for p in v["placeholders"] if p["position"] == k["pos"]))
                if art_id is None:
                    art_id = api.post("/uploads/images.json", {"file_name": art_name, "url": RAW.format(c=args.commit, d="print-xmas2", n=art_name)})["id"]
                placement = fill(art_id, w, h, area)
                pos = k["pos"]
            bullets = "".join(f"<li>{b}</li>" for b in [*k["bullets"], "Printed to order just for you"])
            extra = ("<p><strong>Women's fit:</strong> a classic women's cut in midweight cotton. Prefer it roomier? "
                     "Grab the unisex version.</p>") if k["key"] == "womens" else ""
            body = {"title": title, "description": f"<p>{intro}</p><ul>{bullets}</ul><p><em>{line}</em></p>{extra}",
                    "tags": sorted(set(BASE_TAGS + tags + k["tags"])), "blueprint_id": k["bp"], "print_provider_id": k["pp"],
                    "variants": variants,
                    "print_areas": [{"variant_ids": [v["id"] for v in chosen], "placeholders": [{"position": pos, "images": [placement]}]}]}
            p = api.post(f"/shops/{SHOP}/products.json", body)
            for wait in (0, 120, 300, 600):
                time.sleep(wait)
                try:
                    api.post(f"/shops/{SHOP}/products/{p['id']}/publish.json", {
                        "title": True, "description": True, "images": k["images"], "variants": True,
                        "tags": True, "keyFeatures": True, "shipping_template": True})
                    break
                except Exception as e:
                    print("  publish retry:", str(e)[:100], flush=True)
            cost = sorted({v["cost"] for v in p["variants"] if v["is_enabled"]})
            done[pkey] = {"printify": p["id"], "title": title, "kind": k["key"], "cost": cost}
            OUT.write_text(json.dumps(done, indent=2))
            print("created", title, [c / 100 for c in cost], flush=True)
            time.sleep(10)


if __name__ == "__main__":
    main()
