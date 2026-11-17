"""Add more shirt colors to single-color tees, women's tees and hoodies (2026-11-17).

For each product: enable the palette colors in the sizes the product already sells, at the same price per
size, add them to the existing print area (same art and placement), then publish ONLY the variants to Shopify
so Shopify-side titles, descriptions and photos stay as they are. Results go to printify/colors.json.

Palettes (dark colors suit the art; the four light-art women's tees get Light Pink):
  tee (Bella+Canvas 3001):   Navy, Dark Grey Heather, Maroon, Forest, Military Green
  women's (Gildan 5000L):    Navy, Purple   | White-only women's tees: Light Pink
  hoodie (Gildan 18500):     Navy, Dark Heather, Maroon, Forest Green, Dark Chocolate
Sleeve Edition hoodies stay Black (their sleeve lettering was made for black).

Usage: python3 printify/add_colors.py [--only "Exact Title"] [--dry-run]
"""
import argparse, json, time
from pathlib import Path
from create_products import Printify

SHOP = 29509655
OUT = Path(__file__).with_name("colors.json")
PALETTE = {
    12: ["Navy", "Dark Grey Heather", "Maroon", "Forest", "Military Green"],
    466: ["Navy", "Purple"],
    77: ["Navy", "Dark Heather", "Maroon", "Forest Green", "Dark Chocolate"],
}
LIGHT_WOMENS = ["Light Pink"]


def color_of(product, variant):
    by_id = {v["id"]: v["title"] for opt in product["options"] if opt["type"] == "color" for v in opt["values"]}
    return next((by_id[o] for o in variant["options"] if o in by_id), None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    api = Printify(None)
    done = json.loads(OUT.read_text()) if OUT.exists() else {}
    catalogs = {}

    products, page = [], 1
    while True:
        r = api.get(f"/shops/{SHOP}/products.json?limit=50&page={page}")
        products += [x for x in r["data"] if x["blueprint_id"] in PALETTE and (x.get("external") or {}).get("id")]
        if not r.get("next_page_url") or not r["data"]:
            break
        page += 1

    for x in products:
        title = x["title"]
        if args.only and title != args.only:
            continue
        if title in done or "Sleeve Edition" in title:
            continue
        enabled = [v for v in x["variants"] if v["is_enabled"]]
        colors = {color_of(x, v) for v in enabled}
        if len(colors) != 1:
            continue
        (current,) = colors
        bp, pp = x["blueprint_id"], x["print_provider_id"]
        palette = LIGHT_WOMENS if (bp == 466 and current == "White") else PALETTE[bp]
        if (bp, pp) not in catalogs:
            catalogs[(bp, pp)] = api.get(f"/catalog/blueprints/{bp}/print_providers/{pp}/variants.json")["variants"]
        catalog = catalogs[(bp, pp)]
        size_price = {}
        for v in enabled:
            size = next(c["options"]["size"] for c in catalog if c["id"] == v["id"])
            size_price[size] = v["price"]
        new = [c for c in catalog if c["options"].get("color") in palette and c["options"].get("size") in size_price]
        new_ids = {c["id"] for c in new}
        if not new:
            print("no new variants for", title)
            continue
        variants = []
        for v in x["variants"]:
            if v["id"] in new_ids:
                size = next(c["options"]["size"] for c in new if c["id"] == v["id"])
                variants.append({"id": v["id"], "price": size_price[size], "is_enabled": True})
            else:
                variants.append({"id": v["id"], "price": v["price"], "is_enabled": v["is_enabled"]})
        enabled_ids = {v["id"] for v in enabled}
        print_areas = []
        for pa in x["print_areas"]:
            ids = list(pa["variant_ids"])
            if enabled_ids & set(ids):
                ids += [i for i in new_ids if i not in ids]
            else:
                ids = [i for i in ids if i not in new_ids]
            print_areas.append({"variant_ids": ids, "placeholders": [
                {"position": ph["position"], "images": [{k: im[k] for k in ("id", "x", "y", "scale", "angle")} for im in ph["images"]]}
                for ph in pa["placeholders"] if ph["images"]]})
        added = sorted({c["options"]["color"] for c in new})
        print(title, current, "+", added, len(new_ids), "variants")
        if args.dry_run:
            continue
        api.call("PUT", f"/shops/{SHOP}/products/{x['id']}.json", json={"variants": variants, "print_areas": print_areas})
        for wait in (5, 60, 180):
            time.sleep(wait)
            try:
                api.post(f"/shops/{SHOP}/products/{x['id']}/publish.json", {
                    "title": False, "description": False, "images": False, "variants": True,
                    "tags": False, "keyFeatures": False, "shipping_template": False})
                break
            except Exception as e:
                print("  publish retry:", str(e)[:120], flush=True)
        done[title] = {"printify": x["id"], "shopify": x["external"]["id"], "blueprint": bp, "had": current,
                       "added": added, "sides": sorted({ph["position"] for pa in x["print_areas"] for ph in pa["placeholders"] if ph["images"]})}
        OUT.write_text(json.dumps(done, indent=2))
        time.sleep(3)


if __name__ == "__main__":
    main()
