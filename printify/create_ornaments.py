"""Round ceramic ornaments (blueprint 531, Printify Choice, Circle) from existing designs, $17, gift line.

Print files: designs/print-ornament/<slug>.jpg (designs/src/render_ornaments.py), uploaded as base64.
Tagged "accessory"/"home" (Home & Accessories collection) and "gift" (Gifts Under $30 collection).
Published with Printify's mockups (ornaments have no color options, so no labeled photos are needed).

Usage: python3 printify/create_ornaments.py [--only SLUG ...] [--apply]
Results: printify/ornaments.json
"""
import argparse, base64, json, os, time
from pathlib import Path
from create_products import Printify

SHOP = 29509655
BP, PP, VARIANT = 531, 99, "Circle / One Size"
PRICE = 1700
ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).with_name("ornaments.json")
FEATURES = ["Round glossy ceramic, about 2.9 in across", "Printed edge to edge on the front",
            "Gold-toned hanging string included", "Printed to order just for you"]

# slug, name, collection tags, intro, closing line
ORNAMENTS = [
    ("born-ready", "Born Ready", ["immortalized", "drop 004", "goddess"],
     "The Born Ready painting: a goddess rising from the sea on a shell, sunlight on cue.",
     "Arrived fashionably late. On a shell."),
    ("fallen-not-finished", "Fallen, Not Finished", ["immortalized", "drop 004", "angel"],
     "The Fallen, Not Finished painting: a winged hero catching his breath among the ruins.",
     "Heaven can wait. So can I."),
    ("going-with-the-flow", "Going With the Flow", ["immortalized", "drop 004", "river"],
     "The Going With the Flow painting: a dreamer drifting downstream through flowers and light.",
     "Floating through it."),
    ("queen-forever", "Queen Forever", ["immortalized", "drop 004", "skull", "crown"],
     "The Queen Forever painting: a jeweled skeleton queen in lace, sapphires and a towering crown.",
     "Death is no reason to dress down."),
    ("dragonfall", "Dragonfall", ["realms", "fantasy", "dragon"],
     "The Dragonfall art: a lone knight with a burning blade beneath a dragon-torn red sky.", "Here be dragons."),
    ("lantern-witch", "Lantern Witch", ["realms", "fantasy", "witch"],
     "The Lantern Witch art: a young witch, her lantern and a winged fox in an overgrown arch.", "Lights the way."),
    ("moonwood-druid", "Moonwood Druid", ["realms", "fantasy", "druid"],
     "The Moonwood Druid art: an antlered druid under a full moon, wrapped in vines and mushrooms.",
     "Rooted somewhere else."),
    ("post-credits-scene", "I'm Only Here for the Post-Credits Scene", ["player two", "nerdy", "movies"],
     "\"I'm Only Here for the Post-Credits Scene\" in chrome sci-fi lettering.", "Stay seated."),
    ("elsewhere-psychedelic-drip", "Elsewhere Psychedelic Drip", ["brand", "brand collection", "psychedelic"],
     "The Elsewhere Apparel Co. logo melting in rainbow drip, with a smiley, a moon and a red-capped mushroom.",
     "Reality is optional."),
    ("elsewhere-groovy-retro", "Elsewhere Groovy Retro", ["brand", "brand collection", "groovy", "retro"],
     "Bubbly 70s Elsewhere lettering wrapped in rainbow ribbons and daisies.", "Peace, love and somewhere else."),
    ("elsewhere-chrome-globe", "Elsewhere Chrome Globe", ["brand", "brand collection", "chrome", "y2k"],
     "Liquid-chrome Elsewhere lettering dripping over a wireframe globe.", "Worldwide, and then some."),
    ("elsewhere-dreamscape", "Elsewhere Dreamscape", ["brand", "brand collection", "dreamscape"],
     "The Elsewhere Dreamscape logo: neon lettering, a stairway into the clouds and a dreaming stone face.",
     "Wear the destination."),
    ("not-ai-just-tired", "Not AI. Just Tired.", ["funny", "ai", "tired"],
     "\"Not AI. Just Tired.\" in bold white type on black.", "Verified human. Low battery."),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    variant = next(v for v in api.get(f"/catalog/blueprints/{BP}/print_providers/{PP}/variants.json")["variants"]
                   if v["title"] == VARIANT)
    done = json.loads(OUT.read_text()) if OUT.exists() else {}
    for slug, name, tags, intro, line in ORNAMENTS:
        if (args.only and slug not in args.only) or slug in done:
            continue
        title = f"{name} Ornament"
        print(("make " if args.apply else "plan ") + title, flush=True)
        if not args.apply:
            continue
        fname = f"ornament-{slug}.jpg"
        data = base64.b64encode((ROOT / "designs" / "print-ornament" / f"{slug}.jpg").read_bytes()).decode()
        img = api.post("/uploads/images.json", {"file_name": fname, "contents": data})["id"]
        body = {
            "title": title,
            "description": f"<p>{intro}</p><ul>" + "".join(f"<li>{f}</li>" for f in FEATURES) + f"</ul><p><em>{line}</em></p>",
            "tags": sorted(set(tags) | {"ornament", "accessory", "home", "gift"}),
            "blueprint_id": BP, "print_provider_id": PP,
            "variants": [{"id": variant["id"], "price": PRICE, "is_enabled": True}],
            "print_areas": [{"variant_ids": [variant["id"]], "placeholders": [
                {"position": "front", "images": [dict(id=img, x=0.5, y=0.5, scale=1, angle=0)]}]}],
        }
        p = api.post(f"/shops/{SHOP}/products.json", body)
        cost = p["variants"][0]["cost"] if p["variants"][0]["id"] == variant["id"] else \
            next(v["cost"] for v in p["variants"] if v["is_enabled"])
        done[slug] = {"printify": p["id"], "title": title, "kind": "ornament", "cost": cost, "published": False}
        OUT.write_text(json.dumps(done, indent=2))
        for wait in (0, 120, 300, 600):
            time.sleep(wait)
            try:
                api.post(f"/shops/{SHOP}/products/{p['id']}/publish.json", {
                    "title": True, "description": True, "images": True, "variants": True,
                    "tags": True, "keyFeatures": True, "shipping_template": True})
                done[slug]["published"] = True
                OUT.write_text(json.dumps(done, indent=2))
                break
            except Exception as e:
                print("   publish retry:", str(e)[:100], flush=True)
        print(f"   created, cost ${cost / 100:.2f}", flush=True)
        time.sleep(15)


if __name__ == "__main__":
    main()
