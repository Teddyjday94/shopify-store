"""Brand collection: Elsewhere Apparel Co. logo designs on tee, women's tee and hoodie.

Art: designs/print-brand/<slug>.png (transparent, upscaled 4x, 300 DPI; designs/src/logo_cutout.py).
Apparel is Black only, front print on tees, back print on hoodies, at the store's prices.
Apparel publishes without photos; labeled photos are added in Shopify afterwards.

Usage: python3 printify/create_brand.py --commit SHA [--only SLUG]
"""
import argparse, json, os, time
from pathlib import Path
from PIL import Image
from create_products import Printify

SHOP = 29509655
ROOT = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{c}/designs/{d}/{n}"
OUT = Path(__file__).with_name("brand.json")
SIZES = ["S", "M", "L", "XL", "2XL"]
MARGIN = 0.92
BASE_TAGS = ["brand", "brand collection", "logo", "elsewhere apparel co"]

DESIGNS = [
    ("01-psychedelic-drip", "Elsewhere Psychedelic Drip", ["psychedelic", "trippy", "smiley", "mushroom"],
     "The Elsewhere Apparel Co. logo melting in full rainbow drip, with a grinning smiley, a moon, a ringed planet, "
     "a drippy skull and a red-capped mushroom.", "Reality is optional."),
    ("02-groovy-retro", "Elsewhere Groovy Retro", ["groovy", "retro", "70s", "flowers"],
     "Bubbly 70s lettering in teal, pink and sunshine orange, wrapped in rainbow ribbons and daisies.",
     "Peace, love and somewhere else."),
    ("03-chrome-globe", "Elsewhere Chrome Globe", ["chrome", "y2k", "globe"],
     "Liquid-chrome lettering in pink and electric blue, dripping over a wireframe globe with orbit rings and sparkles.",
     "Worldwide, and then some."),
    ("04-ransom-note", "Elsewhere Ransom Note", ["punk", "grunge", "ransom note"],
     "Torn-paper, ransom-note lettering with taped corners, halftone dots and acid-green paint drips.",
     "Cut, paste, leave."),
    ("05-chrome-script", "Elsewhere Chrome Script", ["chrome", "y2k", "script"],
     "Sharp liquid-chrome script with violet and blue reflections, an orbit swoosh and starbursts.",
     "Shine somewhere else."),
]
KINDS = [
    dict(key="tee", title="{n} Tee", bp=12, pp=29, price=2700, pos="front", tags=["tee"], images=False,
         bullets=["Full-color front print", "Soft, lightweight 100% combed cotton", "Retail unisex fit"]),
    dict(key="womens", title="{n} Women's Tee", bp=466, pp=39, price=2700, pos="front", tags=["tee", "womens"], images=False,
         bullets=["Full-color front print", "Midweight 100% cotton that holds its shape", "Classic women's fit"]),
    dict(key="hoodie", title="{n} Hoodie", bp=77, pp=39, price=3700, pos="back", tags=["hoodie"], images=False,
         bullets=["Full-color back print", "Medium-heavy cotton/poly blend, fleece-lined", "Unisex fit, size up for oversized"]),
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
        w, h = Image.open(ROOT / "designs" / "print-brand" / art_name).size
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
                    art_id = api.post("/uploads/images.json", {"file_name": art_name, "url": RAW.format(c=args.commit, d="print-brand", n=art_name)})["id"]
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
