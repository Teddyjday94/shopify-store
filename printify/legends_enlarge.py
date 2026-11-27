"""Enlarge the Legends Never Die "natural border" art (2026-11-27): scale each print so the visible (opaque) part of the
art fills TARGET of the print area's height, centered on the visible part. The transparent margin around the art may
extend past the print area (Printify clips it; nothing visible is lost). Art files are measured from Printify's preview
of the upload (same aspect as the 3772x5500-ish originals).

Usage: python3 printify/legends_enlarge.py [--apply] [--only TITLE_SUBSTRING]
Crewneck neck labels: omitted from the PUT; Printify keeps them (seen 2026-11-27).
"""
import argparse, io, json, time
import numpy as np, requests
from PIL import Image
from create_products import Printify

SHOP, TARGET = 29509655, 0.99
PRODUCTS = {  # printify id: position holding the art
    "6ae779f2f9c00c9ec009d8e0": "back", "6ae77a2517932a00ba02a3f6": "back", "6ae77a88d037ed7f1f02b9d9": "back", "6aea941b365c19e4ba07e801": "back",
    "6ae779db48500d698e04256f": "front", "6ae77a0da04ae2f1280aa3cb": "front", "6ae77a715b46121dd6093a8b": "front", "6aea9404365c19e4ba07e79f": "front",
    "6af37481f6491c921e019173": "front", "6af37702cb8adff71a0292aa": "front", "6af3771b45f16ba7160339ee": "front", "6af37772da607b43c50f7859": "front",
    "6afc013d17c004fdc80482d9": "front", "6afc028cfd4d7f230d0ab614": "front", "6afc0280fd4d7f230d0ab606": "front", "6afc0273fd4d7f230d0ab5f8": "front",
}
_bbox, _cat = {}, {}


def bbox(img):
    """Opaque box of the art as fractions: (x0, x1, y0, y1)."""
    if img["id"] not in _bbox:
        im = Image.open(io.BytesIO(requests.get(img["src"], timeout=300).content)).convert("RGBA")
        a = np.asarray(im)[:, :, 3]
        ys, xs = np.where(a > 8)
        _bbox[img["id"]] = (xs.min() / a.shape[1], (xs.max() + 1) / a.shape[1], ys.min() / a.shape[0], (ys.max() + 1) / a.shape[0])
    return _bbox[img["id"]]


def area(api, p, pos):
    key = (p["blueprint_id"], p["print_provider_id"])
    if key not in _cat:
        _cat[key] = api.get(f"/catalog/blueprints/{key[0]}/print_providers/{key[1]}/variants.json")["variants"]
    vid = p["print_areas"][0]["variant_ids"][0]
    ph = next(ph for v in _cat[key] if v["id"] == vid for ph in v["placeholders"] if ph["position"] == pos)
    return ph["width"], ph["height"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--skip")
    args = ap.parse_args()
    api = Printify(None)
    for pid, pos in PRODUCTS.items():
        p = api.get(f"/shops/{SHOP}/products/{pid}.json")
        if args.only and args.only not in p["title"]:
            continue
        if args.skip and args.skip == p["title"]:
            continue
        W, H = area(api, p, pos)
        areas, msg = [], None
        for a in p["print_areas"]:
            phs = []
            for ph in a["placeholders"]:
                imgs = []
                for i in ph["images"]:
                    if i.get("type") == "text/plain" or i["name"].endswith(".svg"):
                        continue  # neck label: omitted, Printify keeps it
                    place = dict(x=i["x"], y=i["y"], scale=i["scale"], angle=i.get("angle", 0))
                    if ph["position"] == pos and "natural-border" in i["name"]:
                        x0, x1, y0, y1 = bbox(i)
                        ar = i["height"] / i["width"]
                        s = TARGET * (H / W) / (ar * (y1 - y0))
                        s = min(s, 0.99 / (x1 - x0))          # visible width must fit too
                        printed_h, printed_w = s * W * ar, s * W  # in area px
                        place.update(scale=round(s, 4),
                                     x=round(0.5 + (0.5 - (x0 + x1) / 2) * printed_w / W, 4),
                                     y=round(0.5 + (0.5 - (y0 + y1) / 2) * printed_h / H, 4))
                        msg = (f"{p['title']}: scale {i['scale']:.4f} -> {s:.4f} ({s / i['scale'] * 100 - 100:+.1f}%), "
                               f"visible art {i['scale'] * (y1 - y0) * W * ar / H * 100:.0f}% -> {TARGET * 100:.0f}% of print height, "
                               f"x {place['x']} y {place['y']}")
                    imgs.append(dict(id=i["id"], **place))
                if imgs:
                    phs.append({"position": ph["position"], "images": imgs})
            areas.append({"variant_ids": a["variant_ids"], "placeholders": phs})
        print(("apply " if args.apply else "plan  ") + (msg or p["title"] + ": art not found"), flush=True)
        if args.apply and msg:
            api.call("PUT", f"/shops/{SHOP}/products/{pid}.json", json={"print_areas": areas})
            for wait in (5, 60, 180):
                time.sleep(wait)
                try:
                    api.post(f"/shops/{SHOP}/products/{pid}/publish.json", {k: False for k in (
                        "title", "description", "images", "variants", "tags", "keyFeatures", "shipping_template")})
                    break
                except Exception as e:
                    print("   publish retry:", str(e)[:100], flush=True)


if __name__ == "__main__":
    main()
