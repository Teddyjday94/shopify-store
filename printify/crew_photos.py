"""Build Shopify mutations that add labeled photos to the crewnecks in crewnecks.json.

Each color gets "<Title> in <Color>, front print" (Printify camera 98502) so the product gallery switches with the
color picker; the main color (Black when offered) comes first and also gets a folded shot (camera 100648).
Writes one mutation file per chunk: OUT_PREFIX-1.graphql, -2, ... Also records Shopify ids in crewnecks.json.

Usage: python3 printify/crew_photos.py OUT_PREFIX [--chunk 6]
"""
import argparse, json
from pathlib import Path
import requests
from create_products import Printify

SHOP = 29509655
DATA = Path(__file__).with_name("crewnecks.json")
CAM_FRONT, CAM_FOLDED = 98502, 100648
SHOP_APP = "gid://shopify/Publication/210420138145"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_prefix")
    ap.add_argument("--chunk", type=int, default=6)
    args = ap.parse_args()
    api = Printify(None)
    data = json.loads(DATA.read_text())
    cat = {c["id"]: c["options"] for c in api.get("/catalog/blueprints/49/print_providers/39/variants.json")["variants"]}
    parts = []
    for name, v in data.items():
        if v.get("photos"):
            continue
        x = api.get(f"/shops/{SHOP}/products/{v['printify']}.json")
        sid = (x.get("external") or {}).get("id")
        if not sid:
            print("not on Shopify yet:", v["title"])
            continue
        v["shopify"] = sid
        src = next(im["src"] for im in x["images"] if "/mockup/" in im["src"])
        mock, _, _, fname = src.split("/mockup/")[1].split("/")[:4]
        fname = fname.split(".jpg")[0]
        colors = v["colors"]
        main_color = "Black" if "Black" in colors else colors[0]
        shots = [(main_color, CAM_FRONT, "front print"), (main_color, CAM_FOLDED, "folded")] + \
                [(c, CAM_FRONT, "front print") for c in colors if c != main_color]
        media = []
        for color, cam, desc in shots:
            vid = next(vv["id"] for vv in x["variants"] if vv["is_enabled"] and cat[vv["id"]]["color"] == color
                       and cat[vv["id"]]["size"] == "L")
            url = f"https://images.printify.com/mockup/{mock}/{vid}/{cam}/{fname}.jpg?s=2048"
            r = requests.get(url, timeout=120)  # also warms Printify's cache so Shopify's fetch succeeds
            if not r.ok or len(r.content) < 40000:
                print("missing:", v["title"], color, cam, r.status_code, len(r.content))
                continue
            media.append(f'{{originalSource:"{url}",alt:{json.dumps(f"{v["title"]} in {color}, {desc}")},mediaContentType:IMAGE}}')
        parts.append(f'p{sid}: productUpdate(product:{{id:"gid://shopify/Product/{sid}"}}, media:[{",".join(media)}])'
                     f'{{ userErrors{{message}} }} '
                     f's{sid}: publishablePublish(id:"gid://shopify/Product/{sid}", input:[{{publicationId:"{SHOP_APP}"}}])'
                     f'{{ userErrors{{message}} }}')
        v["photos"] = len(media)
        print(v["title"], sid, len(media), "photos", flush=True)
    DATA.write_text(json.dumps(data, indent=2))
    for i in range(0, len(parts), args.chunk):
        Path(f"{args.out_prefix}-{i // args.chunk + 1}.graphql").write_text("mutation { " + " ".join(parts[i:i + args.chunk]) + " }")
    print(-(-len(parts) // args.chunk), "files")


if __name__ == "__main__":
    main()
