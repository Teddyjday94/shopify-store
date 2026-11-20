"""Painted beanies (2026-11-20): the collection emblems exactly as painted (no thread simplification), DTF-printed on
the Port Authority C939 100% Cotton Beanie (blueprint 5254, Printify Choice 99, print area front_dtf 1500x900,
cost $11.17, US shipping $5.09). Black, Graphite, Navy (all it comes in), $27. Sold alongside the embroidered
beanies from create_hats.py (owner's call). Art: designs/pants-2026/print/<slug>-subtle.png (trimmed), fitted into 1400x820.
Usage: python3 printify/create_painted_beanies.py   (creates + publishes, ids in printify/hats.json; skips done ones)"""
import base64, io, json, os, time
from PIL import Image
from create_products import Printify
from create_hats import COLLECTIONS, DONE, SHOP, PRICE, ROOT

BLUEPRINT, PROVIDER, POSITION = 5254, 99, "front_dtf"
CANVAS, BOX = (1500, 900), (1400, 820)
ART = os.path.join(ROOT, "designs/pants-2026/print")  # trimmed emblems (raw files carry paint flecks)
OUT = os.path.join(ROOT, "designs/hats-2026/print")
FEATURES = ("<ul><li>Port Authority 100% cotton knit beanie, no cuff</li>"
            "<li>Full-colour print of the original painted artwork</li>"
            "<li>One size fits most</li><li>Made to order just for you</li></ul>"
            "<p>Prefer thread? The embroidered version of this beanie comes in seven colours.</p>")


def print_file(slug):
    art = Image.open(os.path.join(ART, f"{slug}-subtle.png")).convert("RGBA")
    art = art.crop(art.getbbox())
    s = min(BOX[0] / art.width, BOX[1] / art.height)
    art = art.resize((round(art.width * s), round(art.height * s)), Image.LANCZOS)
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    canvas.alpha_composite(art, ((CANVAS[0] - art.width) // 2, (CANVAS[1] - art.height) // 2))
    path = os.path.join(OUT, f"{slug}-painted-beanie.png")
    canvas.save(path)
    return path


def main():
    api = Printify(None)
    done = json.load(open(DONE))
    variants = api.get(f"/catalog/blueprints/{BLUEPRINT}/print_providers/{PROVIDER}/variants.json")["variants"]
    for slug, (name, tags, _extra, _blurb) in COLLECTIONS.items():
        title = f"{name} Painted Beanie"
        if title in done:
            continue
        path = print_file(slug)
        up = api.post("/uploads/images.json", {"file_name": os.path.basename(path),
                                               "contents": base64.b64encode(open(path, "rb").read()).decode()})
        desc = (f"<p>The {title} carries our {name} emblem exactly as it was painted, printed in full colour: every "
                f"brushstroke, glow and shadow.</p>" + FEATURES)
        body = {"title": title, "description": desc, "blueprint_id": BLUEPRINT, "print_provider_id": PROVIDER,
                "tags": ["hat", "beanie", "printed", "matching set"] + tags,
                "variants": [{"id": v["id"], "price": PRICE, "is_enabled": True} for v in variants],
                "print_areas": [{"variant_ids": [v["id"] for v in variants], "placeholders": [
                    {"position": POSITION, "images": [{"id": up["id"], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}]}]}
        p = api.post(f"{SHOP}/products.json", body)
        api.post(f"{SHOP}/products/{p['id']}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True})
        done[title] = {"printify": p["id"], "collection": slug, "kind": "Painted Beanie",
                       "colors": sorted({v["options"]["color"] for v in variants})}
        json.dump(done, open(DONE, "w"), indent=1)
        print("created + published", title, p["id"])
        time.sleep(1)


if __name__ == "__main__":
    main()
