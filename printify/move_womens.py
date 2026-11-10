"""Rebuild the women's tees on the Gildan 5000L (SwiftPOD) so the art can print bigger.

The Next Level 3900 women's tee (Monster Digital) has a ~10x12 in print area and the art already
fills its height. The Gildan 5000L at SwiftPOD allows ~14x16 in (M and up) and costs less ($10.82 vs
$14.53). Each design is re-placed to fill the new area (top-aligned, 97% of the limiting side), on
the same side(s) it printed before. Price stays $27 for every size.

New products are created and published next to the old ones; the Shopify listing swap (handle,
photos) and deleting the old products happen afterwards. Pairs go to printify/moved_womens.json.

Usage:
    python3 printify/move_womens.py                      # dry run
    python3 printify/move_womens.py --apply [--only "Title" ...]
    python3 printify/move_womens.py --delete-old "Title" ...   # after the Shopify swap
"""

import argparse
import re
import json
import os
import time
from pathlib import Path

from create_products import Printify

OLD_BP, OLD_PP, NEW_BP, NEW_PP = 14, 29, 466, 39
COLOR = {"Solid Black": "Black", "Solid Midnight Navy": "Navy", "Solid Cardinal Red": "Red",
         "Solid Light Pink": "Light Pink", "Solid White": "White",
         "Solid Heavy Metal": "Navy", "Solid Dark Chocolate": "Navy",
         "Solid Natural": "White", "Heather Grey": "White", "Solid Light Olive": "White"}
SIZES = ["S", "M", "L", "XL", "2XL"]
PRICE = 2700
MARGIN = 0.97
OUT = Path(__file__).with_name("moved_womens.json")


def clean_desc(html, sides):
    """Update the copy for the new blank: one print side, Gildan 5000L fabric and fit."""
    side = "Back print" if sides == ["back"] else "Front print"
    html = re.sub(r"<li>Small chest print up front</li>\s*", "", html)
    html = re.sub(r"<li>Optional back-neck print:[^<]*</li>\s*", "", html)
    html = html.replace("Full-color back print, framed like a vintage poster", "Full-color front print, framed like a vintage poster")
    html = html.replace("<li>Front and back print</li>", f"<li>{side}</li>")
    html = re.sub(r"<li>(Retail|Relaxed) unisex fit</li>", "<li>Classic women's fit</li>", html)
    html = re.sub(r"<li>(Soft, lightweight 100% combed cotton[^<]*|Heavyweight, garment-dyed[^<]*)</li>",
                  "<li>Midweight 100% cotton that holds its shape</li>", html)
    html = html.replace("a relaxed boyfriend cut in soft cotton.", "a classic women's cut in midweight cotton.")
    return html


def max_area(api):
    vs = api.get(f"/catalog/blueprints/{NEW_BP}/print_providers/{NEW_PP}/variants.json")["variants"]
    sizes = {}
    for v in vs:
        for ph in v["placeholders"]:
            w, h = sizes.get(ph["position"], (0, 0))
            if ph["width"] > w:
                sizes[ph["position"]] = (ph["width"], ph["height"])
    return vs, sizes


def fill(img, area):
    """Place img as large as the area allows, centered, top-aligned with a small margin."""
    aw, ah = area
    ratio, area_ratio = img["height"] / img["width"], ah / aw
    scale = MARGIN * min(1.0, area_ratio / ratio)
    height_frac = scale * ratio / area_ratio
    return dict(id=img["id"], x=0.5, y=round((1 - MARGIN) / 2 + height_frac / 2, 4), scale=round(scale, 4), angle=0)


def build(src, catalog, areas_px):
    # Each new color takes the print setup (ink/art variant) of the old color it replaces.
    area_of = {}
    for i, a in enumerate(src["print_areas"]):
        for vid in a["variant_ids"]:
            area_of[vid] = i
    colors = {}  # new color -> index of the source print area
    for v in src["variants"]:
        if v["is_enabled"]:
            old = v["title"].split(" / ")[0]
            new = COLOR[old]
            if new not in colors or old.replace("Solid ", "").replace("Midnight ", "").replace("Cardinal ", "") == new:
                colors[new] = area_of[v["id"]]
    by_area = {}
    variants = []
    for v in catalog:
        c, s = v["options"]["color"], v["options"]["size"]
        if c in colors and s in SIZES:
            variants.append({"id": v["id"], "price": PRICE, "is_enabled": True})
            by_area.setdefault(colors[c], []).append(v["id"])
    print_areas = []
    for idx, ids in by_area.items():
        area = src["print_areas"][idx]
        phs = [{"position": ph["position"], "images": [fill(i, areas_px[ph["position"]]) for i in ph["images"]]}
               for ph in area["placeholders"] if ph["images"] and ph["position"] in ("front", "back")]
        print_areas.append({"variant_ids": ids, "placeholders": phs})
    return {"blueprint_id": NEW_BP, "print_provider_id": NEW_PP, "variants": variants, "print_areas": print_areas}, colors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--delete-old", nargs="*")
    ap.add_argument("--fix-desc", action="store_true", help="re-clean descriptions of products already moved")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    moved = json.loads(OUT.read_text()) if OUT.exists() else {}

    if args.fix_desc:
        for old, m in moved.items():
            new = api.get(f"/shops/{shop}/products/{m['new_printify']}.json")
            fixed = clean_desc(new["description"], m["sides"])
            if fixed != new["description"]:
                api.call("PUT", f"/shops/{shop}/products/{m['new_printify']}.json", json={"description": fixed})
                print("fixed description", m["title"])
        return

    if args.delete_old is not None:
        for old, m in moved.items():
            if m["title"] in args.delete_old and not m.get("old_deleted"):
                p = api.get(f"/shops/{shop}/products/{old}.json")
                assert p["blueprint_id"] == OLD_BP and p["title"] == m["title"], p["title"]
                api.call("DELETE", f"/shops/{shop}/products/{old}.json")
                m["old_deleted"] = True
                print("deleted old", m["title"])
        OUT.write_text(json.dumps(moved, indent=2))
        return

    catalog, areas_px = max_area(api)
    page, last = 1, 1
    while page <= last:
        data = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        last, page = data["last_page"], page + 1
        for p in data["data"]:
            if p["blueprint_id"] != OLD_BP or p["print_provider_id"] != OLD_PP or p["id"] in moved:
                continue
            if args.only and p["title"] not in args.only:
                continue
            body, colors = build(p, catalog, areas_px)
            sides = sorted({ph["position"] for a in body["print_areas"] for ph in a["placeholders"]})
            print(f"{'make' if args.apply else 'plan'}  {p['title']}: {sorted(colors)} {sides}", flush=True)
            if not args.apply:
                continue
            body.update(title=p["title"], description=clean_desc(p["description"], sides), tags=p["tags"])
            new = api.post(f"/shops/{shop}/products.json", body)
            for wait in (0, 120, 300, 600, 900):
                time.sleep(wait)
                try:
                    api.post(f"/shops/{shop}/products/{new['id']}/publish.json", {
                        "title": True, "description": True, "images": False, "variants": True,
                        "tags": True, "keyFeatures": True, "shipping_template": True})  # photos added labeled later
                    break
                except Exception as e:
                    print("   publish retry:", str(e)[:100], flush=True)
            cost = [v["cost"] for v in new["variants"] if v["is_enabled"]]
            moved[p["id"]] = {"title": p["title"], "old_shopify": (p.get("external") or {}).get("id"),
                              "old_handle": ((p.get("external") or {}).get("handle") or "").rsplit("/", 1)[-1],
                              "new_printify": new["id"], "colors": sorted(colors), "sides": sides}
            OUT.write_text(json.dumps(moved, indent=2))
            print(f"   created {new['id']}, cost ${min(cost) / 100:.2f}-${max(cost) / 100:.2f}", flush=True)
            time.sleep(10)


if __name__ == "__main__":
    main()
