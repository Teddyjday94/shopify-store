"""Collection sweatpants (2026-11-20): Gildan 18200 at SwiftPOD (blueprint 1398, provider 39), the same maker as
our hoodies. Two per collection: "<Name> Sweatpants" (Bold: the tall collection art down the left thigh) and
"<Name> Emblem Sweatpants" (Subtle: the small emblem on the upper left thigh). Black and Navy only: the art has
dark painted edges made for dark fabric. Print files: designs/pants-2026/print (designs/pants-2026/make_print.py).
Usage: python3 printify/create_pants.py  (creates + publishes, records ids in printify/pants.json; skips done ones)"""
import base64, json, os, time
from create_products import Printify

SHOP = "/shops/29509655"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRINT = os.path.join(ROOT, "designs/pants-2026/print")
DONE = os.path.join(ROOT, "printify/pants.json")
COLORS = ("Black", "Navy")
PRICES = {"S": 3700, "M": 3700, "L": 3700, "XL": 3700, "2XL": 4100, "3XL": 4300}
FEATURES = ("<ul><li>Gildan Heavy Blend fleece, 50% cotton / 50% polyester</li>"
            "<li>Elastic waistband with drawcord, ribbed cuffs</li>"
            "<li>Same maker as our hoodies, so a matching set usually ships together</li>"
            "<li>Printed to order just for you</li></ul>"
            "<h3>Size &amp; fit</h3><p>Available sizes: S, M, L, XL, 2XL, 3XL. Unisex fit.</p>")

COLLECTIONS = {
    "side-quest": ("Side Quest", ["player two", "side quest", "gaming", "nerdy"],
                   "Floating island, winding path, three hearts left. For the days the main story can wait.",
                   "Three pixel hearts in the clouds, small on the upper thigh."),
    "elsewhere-signature": ("Elsewhere Signature", ["brand", "brand collection", "elsewhere apparel co", "logo"],
                            "Our signature: Elsewhere Apparel Co. in flowing script with a compass star and lilies.",
                            "The Elsewhere compass star, small on the upper thigh."),
    "legends-never-die": ("Legends Never Die", ["immortalized", "drop 004", "legends never die", "wings"],
                          "Blackletter Legends Never Die, a feathered wing and an eclipse sun.",
                          "The LND laurel crest, small on the upper thigh."),
    "born-ready": ("Born Ready", ["immortalized", "drop 004", "born ready", "racing"],
                   "Born Ready 01 between two chequered flags. Racing stripe energy for rest days.",
                   "The BR star badge, small on the upper thigh."),
    "urban-collection": ("Urban Collection", ["urban", "urban collection", "street", "graffiti"],
                         "A lamplit brick stoop with a fire escape and fresh graffiti, under the Urban Collection tag.",
                         "The Urban drip tag, small on the upper thigh."),
    "female-lead": ("Female Lead", ["own lane", "drop 003", "female lead", "floral"],
                    "Female Lead in painted script with a rose, a lily and gold stars.",
                    "The FL rose badge, small on the upper thigh."),
}


def main():
    api = Printify(None)
    done = json.load(open(DONE)) if os.path.exists(DONE) else {}
    variants = api.get("/catalog/blueprints/1398/print_providers/39/variants.json")["variants"]
    use = [v for v in variants if v["options"]["color"] in COLORS]
    for slug, (name, tags, bold_desc, subtle_desc) in COLLECTIONS.items():
        for style in ("bold", "subtle"):
            title = f"{name} Sweatpants" if style == "bold" else f"{name} Emblem Sweatpants"
            if title in done:
                continue
            path = os.path.join(PRINT, f"{slug}-{style}.png")
            up = api.post("/uploads/images.json", {"file_name": os.path.basename(path),
                                                   "contents": base64.b64encode(open(path, "rb").read()).decode()})
            lead = bold_desc if style == "bold" else subtle_desc
            what = ("the full design down the left leg" if style == "bold" else "a small emblem on the upper left thigh")
            desc = (f"<p>The {title} are fleece sweatpants with {what}, made to match our {name} hoodies, tees "
                    f"and crewnecks.</p><p>{lead}</p>" + FEATURES)
            body = {"title": title, "description": desc, "blueprint_id": 1398, "print_provider_id": 39,
                    "tags": ["sweatpants", "bottoms", "joggers", "unisex", "matching set", style] + tags,
                    "variants": [{"id": v["id"], "price": PRICES[v["options"]["size"]], "is_enabled": True} for v in use],
                    "print_areas": [{"variant_ids": [v["id"] for v in use], "placeholders": [
                        {"position": "left_leg_front", "images": [{"id": up["id"], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}]}]}
            p = api.post(f"{SHOP}/products.json", body)
            api.post(f"{SHOP}/products/{p['id']}/publish.json", {
                "title": True, "description": True, "images": True, "variants": True,
                "tags": True, "keyFeatures": True, "shipping_template": True})
            done[title] = {"printify": p["id"], "collection": slug, "style": style}
            json.dump(done, open(DONE, "w"), indent=1)
            print("created + published", title, p["id"])
            time.sleep(1)


if __name__ == "__main__":
    main()
