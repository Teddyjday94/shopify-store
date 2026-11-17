"""Build the Shopify mutation that adds one labeled flat photo per shirt color to the products in colors.json.

The product page gallery groups photos by the color in their label ("<Title> in <Color>, front print"), so
each new color needs its own labeled print photo. Products listed in --need-black also get a labeled photo
of their original color (older listings whose photos were not labeled by color).

Usage: python3 printify/color_photos.py OUT.graphql [--need-black "Title" ...]
"""
import argparse, json
from pathlib import Path
import requests
from create_products import Printify

SHOP = 29509655
COLORS = Path(__file__).with_name("colors.json")
CAM = {(12, "front"): 102044, (12, "back"): 102045, (466, "front"): 87728, (466, "back"): 87729,
       (77, "back"): 98425, (77, "front"): 98424}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--need-black", nargs="*", default=[])
    args = ap.parse_args()
    api = Printify(None)
    data = json.loads(COLORS.read_text())
    catalogs, parts = {}, []
    for title, v in data.items():
        x = api.get(f"/shops/{SHOP}/products/{v['printify']}.json")
        bp, pp = x["blueprint_id"], x["print_provider_id"]
        if (bp, pp) not in catalogs:
            catalogs[(bp, pp)] = {c["id"]: c["options"] for c in api.get(f"/catalog/blueprints/{bp}/print_providers/{pp}/variants.json")["variants"]}
        cat = catalogs[(bp, pp)]
        src = next(im["src"] for im in x["images"] if "/mockup/" in im["src"])
        mock, _, _, name = src.split("/mockup/")[1].split("/")[:4]
        name = name.split(".jpg")[0]
        side = "front" if "front" in v["sides"] else "back"
        cam = CAM[(bp, side)]
        colors = list(v["added"]) + ([v["had"]] if title in args.need_black else [])
        media = []
        for color in colors:
            vid = next(vv["id"] for vv in x["variants"] if vv["is_enabled"] and cat[vv["id"]].get("color") == color)
            url = f"https://images.printify.com/mockup/{mock}/{vid}/{cam}/{name}.jpg?s=2048"
            r = requests.get(url, timeout=120)
            if not r.ok or len(r.content) < 40000:
                print("missing:", title, color, r.status_code, len(r.content))
                continue
            media.append(f'{{originalSource:"{url}",alt:{json.dumps(f"{title} in {color}, {side} print")},mediaContentType:IMAGE}}')
        sid = v["shopify"]
        parts.append(f'p{sid}: productUpdate(product:{{id:"gid://shopify/Product/{sid}"}}, media:[{",".join(media)}]){{ userErrors{{message}} }}')
        print(title, len(media), "photos")
    Path(args.out).write_text("mutation { " + " ".join(parts) + " }")


if __name__ == "__main__":
    main()
