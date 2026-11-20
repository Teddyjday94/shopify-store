"""Collection sweatpants (2026-11-20): Gildan 18200 at SwiftPOD (blueprint 1398, provider 39), the same maker as
our hoodies. One per collection, "<Name> Sweatpants": the Bold collection art down the left thigh and the Subtle
emblem on the right thigh (left sleeve / right sleeve style, owner's call). First built as 12 listings (bold and
emblem separately); the emblem listings were deleted the same day and the emblem moved onto the right leg. Black and Navy only: the art has
dark painted edges made for dark fabric. Print files: designs/pants-2026/print (designs/pants-2026/make_print.py).
Usage: python3 printify/create_pants.py  (creates + publishes, records ids in printify/pants.json; skips done ones)"""
import base64, json, os, time
from create_products import Printify

SHOP = "/shops/29509655"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRINT = os.path.join(ROOT, "designs/pants-2026/print")
DONE = os.path.join(ROOT, "printify/pants.json")
COLORS = ("Black", "Navy")
PRICES = {"S": 4200, "M": 4200, "L": 4200, "XL": 4200, "2XL": 4600, "3XL": 4800}  # two print spots
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
    for slug, (name, tags, bold_desc, subtle_desc) in COLLECTIONS.items():
        title = f"{name} Sweatpants"
        if True:
            if title in done:
                continue
            ups = {}
            for style in ("bold", "subtle"):
                path = os.path.join(PRINT, f"{slug}-{style}.png")
                ups[style] = api.post("/uploads/images.json", {"file_name": os.path.basename(path),
                                      "contents": base64.b64encode(open(path, "rb").read()).decode()})["id"]
            desc = (f"<p>The {title} are fleece sweatpants made to match our {name} hoodies, tees and crewnecks: "
                    f"the full design down the left leg and its emblem on the right thigh.</p><p>{bold_desc}</p>" + FEATURES)
            vids = [v["id"] for v in variants]
            body = {"title": title, "description": desc, "blueprint_id": 1398, "print_provider_id": 39,
                    "tags": ["sweatpants", "bottoms", "joggers", "unisex", "matching set"] + tags,
                    "variants": [{"id": v["id"], "price": PRICES[v["options"]["size"]],
                                  "is_enabled": v["options"]["color"] in COLORS} for v in variants],
                    "print_areas": [{"variant_ids": vids, "placeholders": [
                        {"position": "left_leg_front", "images": [{"id": ups["bold"], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]},
                        {"position": "right_leg_front", "images": [{"id": ups["subtle"], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}]}]}
            p = api.post(f"{SHOP}/products.json", body)
            api.post(f"{SHOP}/products/{p['id']}/publish.json", {
                "title": True, "description": True, "images": True, "variants": True,
                "tags": True, "keyFeatures": True, "shipping_template": True})
            done[title] = {"printify": p["id"], "collection": slug, "style": "bold left + emblem right"}
            json.dump(done, open(DONE, "w"), indent=1)
            print("created + published", title, p["id"])
            time.sleep(1)


if __name__ == "__main__":
    main()
