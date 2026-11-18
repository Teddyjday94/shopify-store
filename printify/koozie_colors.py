"""Extra colour listings for the three koozies (2026-11-18). Printify's can cooler (bp951) is white-only with
Regular/Slim as its only variants, so each colour is its own product, cloned from the original listing.
Usage: python3 printify/koozie_colors.py ART_DIR   (ART_DIR holds whadid.png, notai_white.png, groovy.png)
Writes media/koozies/<slug>-<colour>-{regular,slim}.png, creates + publishes on Printify, records in koozies.json."""
import base64, json, subprocess, sys
from pathlib import Path
from PIL import Image
from create_products import Printify

SHOP = "/shops/29509655"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "media/koozies"
ART = Path(sys.argv[1])

# design: (source product, art file, slug, [(colour name, bg hex, ink or None)])
PLAN = {
    "WHADID I DO?! Koozie": ("6afe2f9f0ef5a611d100b21e", "whadid.png", "whadid",
                             [("Black", "#141414", None), ("Navy", "#1f2a44", None), ("Red", "#a8222b", None)]),
    "Not AI. Just Tired. Koozie": ("6afe2fa6db330dd69c09cd15", "notai_white.png", "not-ai",
                                   [("Black", "#141414", None), ("White", "#ffffff", (26, 26, 26)),
                                    ("Red", "#a8222b", None)]),
    "Elsewhere Groovy Retro Koozie": ("6afe2faee1b90d86aa0a944e", "groovy.png", "groovy-retro",
                                      [("Black", "#141414", None), ("Navy", "#1f2a44", None),
                                       ("Cream", "#f3e6cc", None)]),
}
SIZE_VARIANT = {"regular": 78460, "slim": 78461}

api = Printify(None)
done = json.loads((ROOT / "printify/koozies.json").read_text())

for design, (src_id, art_file, slug, colours) in PLAN.items():
    src = api.get(f"{SHOP}/products/{src_id}.json")
    for name, bg, ink in colours:
        title = f"{design} – {name}"
        if title in done:
            continue
        art = ART / art_file
        if ink:
            im = Image.open(art).convert("RGBA")
            solid = Image.new("RGBA", im.size, ink + (255,))
            solid.putalpha(im.getchannel("A"))
            art = OUT / f"_{slug}-{name.lower()}-art.png"
            solid.save(art)
        prefix = OUT / f"{slug}-{name.lower()}"
        subprocess.run([sys.executable, str(ROOT / "printify/koozie_art.py"), str(art), bg, str(prefix)], check=True)
        if ink:
            art.unlink()
        areas = []
        for size, vid in SIZE_VARIANT.items():
            f = Path(f"{prefix}-{size}.png")
            up = api.post("/uploads/images.json", {"file_name": f.name,
                                                   "contents": base64.b64encode(f.read_bytes()).decode()})
            areas.append({"variant_ids": [vid], "placeholders": [{"position": "front", "images": [
                {"id": up["id"], "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}], "background": bg})
        body = {"title": title, "description": src["description"],
                "blueprint_id": 951, "print_provider_id": 92,
                "tags": src["tags"] + [name.lower()],
                "variants": [{"id": v["id"], "price": v["price"], "is_enabled": True} for v in src["variants"]],
                "print_areas": areas}
        p = api.post(f"{SHOP}/products.json", body)
        api.post(f"{SHOP}/products/{p['id']}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True})
        done[title] = {"printify": p["id"], "design": design, "colour": name, "bg": bg}
        (ROOT / "printify/koozies.json").write_text(json.dumps(done, indent=1, ensure_ascii=False))
        print("created", title, p["id"])
