"""Collection trucker hats and beanies (2026-11-20). Embroidered emblems from designs/hats-2026/flat (flatten.py turns
the painted sweatpants emblems into solid thread colours). Per collection: "<Name> Trucker Hat" (Yupoong 6606, blueprint
1446, Printify Choice 99, front 1200x675) and "<Name> Beanie" (Yupoong 1501KC cuffed, blueprint 1691, Printify Choice
99, front 1500x525), 7 dark colours each (cream/gold thread vanishes on light crowns), $27.
Usage: python3 printify/create_hats.py   (creates + publishes, ids in printify/hats.json; skips done ones)"""
import base64, io, json, os, time
from PIL import Image
from create_products import Printify

SHOP = "/shops/29509655"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLAT = os.path.join(ROOT, "designs/hats-2026/flat")
OUT = os.path.join(ROOT, "designs/hats-2026/print")
DONE = os.path.join(ROOT, "printify/hats.json")
PRICE = 2700

TRUCKER = dict(blueprint=1446, provider=99, position="front", canvas=(1200, 675), box=(1100, 600), kind="Trucker Hat")
BEANIE = dict(blueprint=1691, provider=99, position="front", canvas=(1500, 525), box=(1300, 480), kind="Beanie")
BEANIE_COLORS = ["Black", "Navy", "Dark Grey", "Spruce", "Olive", "Brown", "Royal"]
TRUCKER_BASE = ["Black", "Black / White", "Navy / White", "Charcoal / White", "Evergreen / White", "Dark Heather Grey"]

COLLECTIONS = {
    "side-quest": ("Side Quest", ["player two", "side quest", "gaming", "nerdy"], "Steel Blue / Silver",
                   "Three pixel hearts and a gold star: full health, side quest pending."),
    "elsewhere-signature": ("Elsewhere Signature", ["brand", "brand collection", "elsewhere apparel co", "logo"], "Coyote Brown / Black",
                            "The Elsewhere compass star in gold thread with lavender swirls."),
    "legends-never-die": ("Legends Never Die", ["immortalized", "drop 004", "legends never die"], "Maroon / Grey",
                          "The LND laurel crest in gold thread."),
    "born-ready": ("Born Ready", ["immortalized", "drop 004", "born ready", "racing"], "Royal / White",
                   "The BR star badge: cream letters, a red racing swoosh and a gold star."),
    "urban-collection": ("Urban Collection", ["urban", "urban collection", "street", "graffiti"], "Brown / Khaki",
                         "The Urban drip tag in teal thread."),
    "female-lead": ("Female Lead", ["own lane", "drop 003", "female lead", "floral"], "Maroon / Grey",
                    "The FL monogram with a rose, a pink ribbon and a gold star."),
}
FEATURES = {
    "Trucker Hat": ("<ul><li>Yupoong 6606 retro trucker: structured mid-profile, mesh back, snapback</li>"
                    "<li>Embroidered front design</li><li>One size, adjustable</li><li>Made to order just for you</li></ul>"),
    "Beanie": ("<ul><li>Yupoong 1501KC classic cuffed knit beanie, 100% acrylic</li>"
               "<li>Embroidered on the cuff</li><li>One size fits most</li><li>Made to order just for you</li></ul>"),
}


def print_file(slug, spec):
    os.makedirs(OUT, exist_ok=True)
    art = Image.open(os.path.join(FLAT, f"{slug}.png")).convert("RGBA")
    bw, bh = spec["box"]
    s = min(bw / art.width, bh / art.height)
    art = art.resize((round(art.width * s), round(art.height * s)), Image.LANCZOS)
    cw, ch = spec["canvas"]
    canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    canvas.alpha_composite(art, ((cw - art.width) // 2, (ch - art.height) // 2))
    path = os.path.join(OUT, f"{slug}-{spec['kind'].split()[0].lower()}.png")
    canvas.save(path)
    return path


def main():
    api = Printify(None)
    done = json.load(open(DONE)) if os.path.exists(DONE) else {}
    for slug, (name, tags, extra_trucker, blurb) in COLLECTIONS.items():
        for spec, colors in ((TRUCKER, TRUCKER_BASE + [extra_trucker]), (BEANIE, BEANIE_COLORS)):
            title = f"{name} {spec['kind']}"
            if title in done:
                continue
            variants = api.get(f"/catalog/blueprints/{spec['blueprint']}/print_providers/{spec['provider']}/variants.json")["variants"]
            missing = [c for c in colors if c not in {v["options"]["color"] for v in variants}]
            assert not missing, (title, missing)
            path = print_file(slug, spec)
            up = api.post("/uploads/images.json", {"file_name": os.path.basename(path),
                                                   "contents": base64.b64encode(open(path, "rb").read()).decode()})
            desc = (f"<p>The {title} carries our {name} emblem, embroidered in thread.</p><p>{blurb}</p>"
                    + FEATURES[spec["kind"]])
            kind_tag = "trucker hat" if spec["kind"] == "Trucker Hat" else "beanie"
            body = {"title": title, "description": desc, "blueprint_id": spec["blueprint"], "print_provider_id": spec["provider"],
                    "tags": ["hat", kind_tag, "embroidered", "matching set"] + tags,
                    "variants": [{"id": v["id"], "price": PRICE, "is_enabled": v["options"]["color"] in colors} for v in variants],
                    "print_areas": [{"variant_ids": [v["id"] for v in variants], "placeholders": [
                        {"position": spec["position"], "images": [{"id": up["id"], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}]}]}
            p = api.post(f"{SHOP}/products.json", body)
            api.post(f"{SHOP}/products/{p['id']}/publish.json", {
                "title": True, "description": True, "images": True, "variants": True,
                "tags": True, "keyFeatures": True, "shipping_template": True})
            done[title] = {"printify": p["id"], "collection": slug, "kind": spec["kind"], "colors": colors}
            json.dump(done, open(DONE, "w"), indent=1)
            print("created + published", title, p["id"])
            time.sleep(1)


if __name__ == "__main__":
    main()
