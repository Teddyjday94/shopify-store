"""Make hoodie back prints as big as the print area allows (2026-11-17, owner's request).

Gildan 18500 / SwiftPOD back area is 14 x 16 in (4200 x 4800 px). Earlier products left a margin
(0.92 or 0.97 of the limiting side); this re-places the art already on each hoodie to fill the whole
limiting side, top-aligned, centered. No new uploads. Shopify photos are refreshed separately.

Usage: python3 printify/enlarge_hoodie_backs.py [--apply]
"""
import argparse, json
from pathlib import Path
from create_products import Printify

SHOP = 29509655
AREA_W, AREA_H = 4200, 4800
OUT = Path(__file__).with_name("hoodie_backs.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    apply = ap.parse_args().apply
    api = Printify(None)
    done = json.loads(OUT.read_text()) if OUT.exists() else {}
    page = 1
    while True:
        r = api.get(f"/shops/{SHOP}/products.json?limit=50&page={page}")
        for p in r["data"]:
            if p["blueprint_id"] != 77 or not (p.get("external") or {}).get("id") or p["title"] in done:
                continue
            changed = None
            for pa in p["print_areas"]:
                for ph in pa["placeholders"]:
                    if ph["position"] != "back" or len(ph["images"]) != 1:
                        continue
                    img = ph["images"][0]
                    ratio = (img["height"] / img["width"]) * (AREA_W / AREA_H)
                    scale = round(min(1.0, 1 / ratio), 4)
                    y = round(scale * ratio / 2, 4)
                    if scale <= img["scale"] + 0.002:
                        continue
                    changed = (img["scale"], scale, scale * ratio)
                    img.update(x=0.5, y=y, scale=scale)
            if not changed:
                continue
            print(f"{'set ' if apply else 'plan'} {p['title']}: width {changed[0]:.1%} -> {changed[1]:.1%}, height {changed[2]:.1%}", flush=True)
            if not apply:
                continue
            areas = [{"variant_ids": a["variant_ids"], "placeholders": [
                {"position": ph["position"], "images": [{k: im[k] for k in ("id", "x", "y", "scale", "angle")} for im in ph["images"]]}
                for ph in a["placeholders"] if ph["images"]]} for a in p["print_areas"]]
            api.call("PUT", f"/shops/{SHOP}/products/{p['id']}.json", json={"print_areas": areas})
            done[p["title"]] = {"printify": p["id"], "shopify": p["external"]["id"], "before": changed[0], "after": changed[1]}
            OUT.write_text(json.dumps(done, indent=2))
        if not r.get("next_page_url") or not r["data"]:
            break
        page += 1


if __name__ == "__main__":
    main()
