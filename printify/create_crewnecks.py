"""Crewneck sweatshirts (Gildan 18000, SwiftPOD) for every design that has a unisex tee.

The art is copied from the design's existing hoodie (its back print, layer for layer and color by color, since
SwiftPOD's 18500 back and 18000 front are both 4200 x 4800) and goes on the crewneck's FRONT. Designs with no
hoodie copy the unisex tee's front print instead, with tee colors mapped to the nearest Gildan 18000 color.
Chest prints and back-neck labels are left off. Price $37 every size.

Apparel publishes without photos; labeled photos are added in Shopify afterwards (photo_mutations.py, kind "crew").

Usage: python3 printify/create_crewnecks.py [--only "Design Name" ...] [--draft] [--apply]
Results: printify/crewnecks.json
"""
import argparse, json, os, re, time
from pathlib import Path
from create_products import Printify

SHOP = 29509655
BP, PP = 49, 39
PRICE = 3700
SIZES = ["S", "M", "L", "XL", "2XL"]
OUT = Path(__file__).with_name("crewnecks.json")
TEE_COLORS = {  # Bella+Canvas 3001 -> Gildan 18000
    "White": "White", "Black": "Black", "Gold": "Gold", "Maroon": "Maroon", "Forest": "Forest Green",
    "Athletic Heather": "Sport Grey", "Heather Navy": "Navy", "Navy": "Navy", "Brown": "Dark Chocolate",
    "Natural": "Sand", "Soft Cream": "Sand", "Tan": "Sand", "Heather Ice Blue": "Light Blue",
    "Baby Blue": "Light Blue", "Heather Blue": "Light Blue", "Soft Pink": "Light Pink", "Lilac": "Light Pink",
    "Heather Purple": "Purple", "Heather Team Purple": "Purple", "Deep Heather": "Dark Heather",
    "Dark Grey Heather": "Dark Heather", "Heather Storm": "Dark Heather", "Sage": "Military Green",
}
BULLETS = ["Full-color front print", "Medium-heavy cotton/poly blend, soft fleece inside",
           "Classic crew neck with ribbed cuffs and hem", "Unisex fit, size up for oversized",
           "Printed to order just for you"]


def design_name(title):
    return re.sub(r"( - Bookish Reader)?( T-Shirt| Tee)$", "", title).strip()


def option_titles(p):
    names = {}
    for o in p["options"]:
        for v in o["values"]:
            names[v["id"]] = (o["type"], v["title"])
    return names


def plan(products, catalog):
    by_title = {p["title"]: p for p in products}
    crew = {(v["options"]["color"], v["options"]["size"]): v["id"] for v in catalog}
    for tee in (p for p in products if p["blueprint_id"] == 12):
        name = design_name(tee["title"])
        src = by_title.get(f"{name} Hoodie")
        pos, cmap = ("back", None) if src else ("front", TEE_COLORS)
        src = src or tee
        names = option_titles(src)
        vinfo = {}
        for v in src["variants"]:
            if not v["is_enabled"]:
                continue
            opts = dict(names[i] for i in v["options"])
            color = opts["color"] if cmap is None else cmap.get(opts["color"])
            vinfo[v["id"]] = (color, opts["size"])
        areas, used = [], set()
        for a in src["print_areas"]:
            layers = next((ph["images"] for ph in a["placeholders"] if ph["position"] == pos and ph["images"]), None)
            if not layers:
                continue
            ids = []
            for vid in a["variant_ids"]:
                key = vinfo.get(vid)
                if key and key[1] in SIZES and key in crew and crew[key] not in used:
                    ids.append(crew[key])
                    used.add(crew[key])
            if ids:
                areas.append({"variant_ids": ids, "placeholders": [{"position": "front", "images": [
                    dict(id=im["id"], x=im["x"], y=im["y"], scale=im["scale"], angle=im.get("angle", 0))
                    for im in layers]}]})
        if not areas:
            print("no art found for", name)
            continue
        colors = sorted({c for (c, s), vid in crew.items() if vid in used})
        desc = src["description"]
        intro = "".join(re.findall(r"<p>(?!<em>).*?</p>", desc)[:1]) or f"<p>{name}.</p>"
        line = "".join(re.findall(r"<p><em>.*?</em></p>", desc)[-1:])
        tags = sorted({t for t in src["tags"] if t not in ("hoodie", "tee", "t-shirt")} | {"sweatshirt", "crewneck"})
        yield name, {
            "title": f"{name} Crewneck",
            "description": intro + "<ul>" + "".join(f"<li>{b}</li>" for b in BULLETS) + "</ul>" + line,
            "tags": tags, "blueprint_id": BP, "print_provider_id": PP,
            "variants": [{"id": vid, "price": PRICE, "is_enabled": True} for vid in sorted(used)],
            "print_areas": areas,
        }, colors, src["title"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--draft", action="store_true", help="create but do not publish")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    products, page = [], 1
    while True:
        d = api.get(f"/shops/{SHOP}/products.json?limit=50&page={page}")
        products += d["data"]
        if page >= d["last_page"]:
            break
        page += 1
    catalog = api.get(f"/catalog/blueprints/{BP}/print_providers/{PP}/variants.json")["variants"]
    existing = {p["title"] for p in products}
    done = json.loads(OUT.read_text()) if OUT.exists() else {}
    for name, body, colors, src in plan(products, catalog):
        if args.only and name not in args.only:
            continue
        if body["title"] in existing or name in done:
            print("skip", body["title"])
            continue
        print(f"{'make' if args.apply else 'plan'}  {body['title']}  from {src}  colors={colors}  "
              f"layers={[len(a['placeholders'][0]['images']) for a in body['print_areas']]}", flush=True)
        if not args.apply:
            continue
        p = api.post(f"/shops/{SHOP}/products.json", body)
        cost = sorted({v["cost"] for v in p["variants"] if v["is_enabled"]})
        done[name] = {"printify": p["id"], "title": body["title"], "kind": "crew", "colors": colors, "cost": cost,
                      "published": False}
        OUT.write_text(json.dumps(done, indent=2))
        print("   created, cost", [c / 100 for c in cost], flush=True)
        if args.draft:
            continue
        for wait in (0, 120, 300, 600):
            time.sleep(wait)
            try:
                api.post(f"/shops/{SHOP}/products/{p['id']}/publish.json", {
                    "title": True, "description": True, "images": False, "variants": True,
                    "tags": True, "keyFeatures": True, "shipping_template": True})
                done[name]["published"] = True
                OUT.write_text(json.dumps(done, indent=2))
                break
            except Exception as e:
                print("   publish retry:", str(e)[:100], flush=True)
        time.sleep(10)


if __name__ == "__main__":
    main()
