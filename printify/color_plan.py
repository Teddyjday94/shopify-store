"""Plan extra shirt colours per product (2026-11-17): every design gets a light/neutral option and a colour pop
where its art stays readable, and at least 4 colours in all. Readability = share of the art's visible pixels whose
WCAG contrast against the shirt colour is >= 1.6 (art pixels that sit on a painted backdrop count too).
Writes color_plan.json. Usage: python3 printify/color_plan.py ART_CACHE_DIR
"""
import io, json, sys, hashlib
from pathlib import Path
import requests
from PIL import Image

PRODS = json.load(open('/tmp/pfy_products.json'))
CAT = json.load(open('/tmp/pfy_cat.json'))
SKIP_PREFIX = ("My Other Outfit Is Also Black",)
# Designs with a thin white caption/title that vanishes on light shirts (checked by eye on a contact sheet):
# they get mid-tone neutrals and deeper colour pops instead.
WHITE_TEXT = ("Fallen, Not Finished", "Going With the Flow", "Queen Forever", "Born Ready", "No Signal",
              "Seasonal Depression")
LIGHT_WT = {12: ["Deep Heather"], 466: [], 77: ["Military Green", "Dark Heather"],
            49: ["Graphite Heather", "Charcoal"], 80: []}
POP_WT = {12: ["Heather Team Purple", "True Royal", "Autumn", "Red"], 466: ["Purple", "Red"],
          77: ["Purple", "Royal", "Red"], 49: ["Purple", "Royal", "Red"], 80: ["Purple", "Royal", "Red"]}
LIGHT = {12: ["Athletic Heather", "Natural", "Soft Cream", "Deep Heather"],
         466: ["White", "Light Pink"],
         77: ["Sport Grey", "Sand", "Charcoal", "White"],
         49: ["Sport Grey", "Sand", "Graphite Heather", "Charcoal", "White"],
         80: ["Sport Grey", "Gold", "White"]}
POP = {12: ["Heather Mauve", "Heather Columbia Blue", "Autumn", "Heather Team Purple", "Gold", "True Royal", "Red"],
       466: ["Purple", "Red", "Azalea", "Heliconia", "Irish Green"],
       77: ["Gold", "Purple", "Light Blue", "Red", "Royal", "Carolina Blue", "Light Pink"],
       49: ["Gold", "Purple", "Light Blue", "Red", "Royal", "Heather Sport Royal", "Light Pink"],
       80: ["Purple", "Red", "Royal", "Light Blue"]}
DARK = {12: ["Navy", "Maroon", "Forest", "Dark Grey Heather", "Military Green", "Black"],
        466: ["Navy", "Black", "Purple"],
        77: ["Navy", "Maroon", "Forest Green", "Dark Chocolate", "Dark Heather", "Black"],
        49: ["Navy", "Maroon", "Forest Green", "Dark Chocolate", "Dark Heather", "Black"],
        80: ["Navy", "Maroon", "Forest Green", "Dark Chocolate", "Black"]}
THRESH = 0.80
# Hand-picked (checked by eye): white-caption designs get deep pops; dark-ink light designs get mid pinks/greens.
_WT_CREW = ["Purple", "Royal"]
MANUAL = {
    "Fallen, Not Finished Tee": ["Navy", "Team Purple"], "Going With the Flow Tee": ["Navy", "Team Purple"],
    "No Signal Tee": ["Navy", "True Royal"], "Queen Forever Tee": ["Maroon", "Team Purple"],
    "Born Ready Tee": ["Maroon", "Team Purple"],
    "Fallen, Not Finished Women's Tee": ["Navy", "Purple"], "Going With the Flow Women's Tee": ["Red"],
    "No Signal Women's Tee": ["Purple", "Red"], "Queen Forever Women's Tee": ["Purple", "Red"],
    "Born Ready Women's Tee": ["Purple", "Red"],
    "No Signal Sleeve Edition Hoodie": ["Navy", "Maroon", "Purple"], "No Signal Long Sleeve Tee": ["Navy", "Maroon", "Purple"],
    "I Paused My Game to Be Here Women's Tee": ["White", "Purple"],
    "Same Chaos Different Day Women's Tee": ["Azalea", "Irish Green"],
    "Somewhere in a Calmer Place Women's Tee": ["Azalea", "Irish Green"],
}
for _d in ("Fallen, Not Finished", "Going With the Flow", "No Signal", "Queen Forever", "Born Ready"):
    MANUAL[f"{_d} Crewneck"] = _WT_CREW
    MANUAL[f"{_d} Hoodie"] = _WT_CREW
MANUAL["Elsewhere Ransom Note Crewneck"] = ["Graphite Heather", "Royal"]   # red letters fade on Red
MANUAL["Elsewhere Ransom Note Hoodie"] = ["Royal"]
MANUAL["Elsewhere Ransom Note Women's Tee"] = ["Azalea"]
MANUAL["Seasonal Depression World Tour Hoodie"] = ["Navy", "Purple", "Royal"]


def lum(rgb):
    def c(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b)


def art_pixels(src, cache):
    f = cache / (hashlib.md5(src.encode()).hexdigest() + ".png")
    if not f.exists():
        im = Image.open(io.BytesIO(requests.get(src, timeout=120).content)).convert("RGBA")
        im.thumbnail((160, 160))
        im.save(f)
    im = Image.open(f).convert("RGBA")
    return [lum(p[:3]) for p in im.getdata() if p[3] > 160]


def score(lums, hexcol):
    h = hexcol.lstrip("#")
    L = lum(tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)))
    ok = sum(1 for a in lums if (max(a, L) + .05) / (min(a, L) + .05) >= 1.6)
    return ok / max(1, len(lums))


def main():
    cache = Path(sys.argv[1])
    plan = {}
    for x in PRODS:
        bp, pp = x["blueprint_id"], x["print_provider_id"]
        if bp not in LIGHT or not (x.get("external") or {}).get("id") or x["title"].startswith(SKIP_PREFIX):
            continue
        catalog = dict(CAT.get(f"{bp}|{pp}", []))
        by_id = {v["id"]: v["title"] for o in x["options"] if o["type"] == "color" for v in o["values"]}
        enabled = [v for v in x["variants"] if v["is_enabled"]]
        have = sorted({by_id[o] for v in enabled for o in v["options"] if o in by_id})
        lums = []
        for pa in x["print_areas"]:
            for ph in pa["placeholders"]:
                for im in ph["images"]:
                    if im.get("src"):
                        lums += art_pixels(im["src"], cache)
                break
            break
        sc = lambda c: score(lums, catalog[c]) if c in catalog and catalog[c] else 0
        wt = x["title"].startswith(WHITE_TEXT)
        light_l, pop_l = (LIGHT_WT[bp], POP_WT[bp]) if wt else (LIGHT[bp], POP[bp])
        add = []
        def pick(lst):
            for c in lst:
                if c in catalog and c not in have and c not in add and sc(c) >= THRESH:
                    return c
        has_light = any(c in LIGHT[bp] or c in ("White", "Natural", "Sand", "Ash", "Light Pink") for c in have)
        has_pop = any(c in POP[bp] for c in have)
        if wt:
            has_light = any(c in light_l for c in have)
            has_pop = any(c in pop_l for c in have)
        if not has_light:
            c = pick(light_l); c and add.append(c)
        if not has_pop:
            c = pick(pop_l); c and add.append(c)
        while len(have) + len(add) < 4:
            c = pick(DARK[bp]) or pick(pop_l) or pick(light_l)
            if not c:
                break
            add.append(c)
        plan[x["title"]] = {"printify": x["id"], "shopify": x["external"]["id"], "blueprint": bp, "provider": pp,
                            "have": have, "add": add,
                            "scores": {c: round(sc(c), 2) for c in LIGHT[bp] + POP[bp] if c in catalog}}
    for t, add in MANUAL.items():
        if t in plan:
            cat = dict(CAT[f"{plan[t]['blueprint']}|{plan[t]['provider']}"])
            plan[t]["add"] = [c for c in add if c in cat and c not in plan[t]["have"]]
            plan[t]["manual"] = True
    Path(__file__).with_name("color_plan.json").write_text(json.dumps(plan, indent=1))
    n = sum(len(v["add"]) for v in plan.values())
    print(len(plan), "products;", sum(1 for v in plan.values() if v["add"]), "get new colours;", n, "colours added")


if __name__ == "__main__":
    main()
