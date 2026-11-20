"""Social Club hats (2026-11-20): the owner's 7 full-colour party designs (designs/party-2026/src, 2400px) as
"<Design> Trucker Hat" (OTTO 39-169 foam trucker, blueprint 1735, Printify Choice 99, DTF front 1650x750, cost $11.50,
8 colours) and "<Design> Beanie" (Port Authority C939 cotton beanie, blueprint 5254, pp 99, DTF 1500x900, cost $11.17,
Black/Graphite/Navy). $27 each. Tag "social club" feeds the Social Club collection.
Usage: python3 printify/create_party_hats.py   (creates + publishes, ids in printify/party_hats.json; skips done ones)"""
import base64, json, os, time
from PIL import Image
from create_products import Printify

SHOP = "/shops/29509655"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "designs/party-2026/src")
OUT = os.path.join(ROOT, "designs/party-2026/print")
DONE = os.path.join(ROOT, "printify/party_hats.json")
PRICE = 2700

TRUCKER = dict(blueprint=1735, provider=99, position="front_dtf", canvas=(1650, 750), box=(1500, 720), kind="Trucker Hat",
               colors=["Black", "Dark Navy", "Black/White", "Navy / White / Navy", "Red", "Royal / White / Royal",
                       "Hot Pink/ White/ Hot Pink", "Kelly/ White/ Kelly"],
               features="<ul><li>OTTO foam-front trucker: high crown, mesh back, snapback</li>"
                        "<li>Full-colour printed front</li><li>One size, adjustable</li><li>Made to order just for you</li></ul>")
BEANIE = dict(blueprint=5254, provider=99, position="front_dtf", canvas=(1500, 900), box=(1400, 840), kind="Beanie",
              colors=None,  # all three
              features="<ul><li>Port Authority 100% cotton knit beanie, no cuff</li><li>Full-colour print</li>"
                       "<li>One size fits most</li><li>Made to order just for you</li></ul>")

DESIGNS = {
    "cheers-from-elsewhere": ("Cheers From Elsewhere", "Two glasses, one toast, bubbles everywhere. Raise one to wherever you are."),
    "weekend-ritual": ("Weekend Ritual", "An old fashioned, an orange slice and a pair of dice. Some traditions are sacred."),
    "pour-decisions-club": ("Pour Decisions Club", "A disco ball, a tipped red cup and a membership you never regret. Mostly."),
    "side-quest-social-club": ("Side Quest Social Club", "A cocktail, two dice and a dotted path off the main story."),
    "after-hours-only": ("After Hours Only", "A red cup, a splash of teal and a checkered flag. The night shift starts late."),
    "night-shift-social": ("Night Shift Social", "A grinning glass in shades under a crescent moon. Clocked in for fun."),
    "midnight-mischief": ("Midnight Mischief", "A disco ball, a moon and a cup that's absolutely up to something."),
}


def print_file(slug, spec):
    os.makedirs(OUT, exist_ok=True)
    art = Image.open(os.path.join(SRC, f"{slug}.png")).convert("RGBA")
    art = art.crop(art.getbbox())
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
    for slug, (name, blurb) in DESIGNS.items():
        for spec in (TRUCKER, BEANIE):
            title = f"{name} {spec['kind']}"
            if title in done:
                continue
            variants = api.get(f"/catalog/blueprints/{spec['blueprint']}/print_providers/{spec['provider']}/variants.json")["variants"]
            colors = spec["colors"] or sorted({v["options"]["color"] for v in variants})
            missing = [c for c in colors if c not in {v["options"]["color"] for v in variants}]
            assert not missing, (title, missing)
            path = print_file(slug, spec)
            up = api.post("/uploads/images.json", {"file_name": os.path.basename(path),
                                                   "contents": base64.b64encode(open(path, "rb").read()).decode()})
            desc = f"<p>{blurb}</p><p>Part of the Social Club collection.</p>" + spec["features"]
            kind_tag = "trucker hat" if spec["kind"] == "Trucker Hat" else "beanie"
            body = {"title": title, "description": desc, "blueprint_id": spec["blueprint"], "print_provider_id": spec["provider"],
                    "tags": ["hat", kind_tag, "printed", "social club", "party", "drinking", slug.replace("-", " ")],
                    "variants": [{"id": v["id"], "price": PRICE, "is_enabled": v["options"]["color"] in colors} for v in variants],
                    "print_areas": [{"variant_ids": [v["id"] for v in variants], "placeholders": [
                        {"position": spec["position"], "images": [{"id": up["id"], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}]}]}
            p = api.post(f"{SHOP}/products.json", body)
            api.post(f"{SHOP}/products/{p['id']}/publish.json", {
                "title": True, "description": True, "images": True, "variants": True,
                "tags": True, "keyFeatures": True, "shipping_template": True})
            done[title] = {"printify": p["id"], "design": slug, "kind": spec["kind"], "colors": colors}
            json.dump(done, open(DONE, "w"), indent=1)
            print("created + published", title, p["id"])
            time.sleep(1)


if __name__ == "__main__":
    main()
