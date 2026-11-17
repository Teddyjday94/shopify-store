"""Rebuild the fileUpdate mutations that swap each hoodie's labeled back-print photos for fresh Printify mockups
(same Shopify media id, so order and labels stay). Input: hoodie_back_media.txt (shopify id, media id:color).
Usage: python3 printify/hoodie_back_photos.py OUT_DIR (reads OUT_DIR/backmedia.txt, writes OUT_DIR/bk_N.graphql)
"""
import json, sys, requests
sys.path.insert(0, "/home/user/shopify-store/printify")
from create_products import Printify
SP = sys.argv[1]
api = Printify(None)
hb = json.load(open("/home/user/shopify-store/printify/hoodie_backs.json"))
by_shop = {str(v["shopify"]): v["printify"] for v in hb.values()}
cat = {}
parts, n, bad = [], 0, []
for line in open(f"{SP}/backmedia.txt"):
    sid, *items = line.split(" ", 1)[0], *line.strip().split(" ", 1)[1:]
    items = [tuple(x.split(":")) for x in line.strip().split(" ")[1:]]
    # colors may contain spaces: re-split on ' 3' ids
    import re
    items = re.findall(r"(\d+):([A-Za-z ]+?)(?= \d+:|$)", line.strip().split(" ", 1)[1])
    x = api.get(f"/shops/29509655/products/{by_shop[sid]}.json")
    key = (x["blueprint_id"], x["print_provider_id"])
    if key not in cat:
        cat[key] = {c["id"]: c["options"] for c in api.get(f"/catalog/blueprints/{key[0]}/print_providers/{key[1]}/variants.json")["variants"]}
    src = next(im["src"] for im in x["images"] if "/mockup/" in im["src"])
    mock, _, _, name = src.split("/mockup/")[1].split("/")[:4]
    name = name.split(".jpg")[0]
    seen = set()
    for mid, color in items:
        vid = next((v["id"] for v in x["variants"] if v["is_enabled"] and cat[key].get(v["id"], {}).get("color") == color), None)
        if vid is None:
            bad.append((x["title"], color, "no variant")); continue
        cam = 98426 if color in seen else 98425
        seen.add(color)
        url = f"https://images.printify.com/mockup/{mock}/{vid}/{cam}/{name}.jpg?s=2048&v=big"
        r = requests.get(url, timeout=120)
        if not r.ok or len(r.content) < 40000:
            bad.append((x["title"], color, r.status_code, len(r.content))); continue
        parts.append(f'{{id:"gid://shopify/MediaImage/{mid}",originalSource:"{url}"}}')
    print(x["title"], len(items), flush=True)
B = 40
for i in range(0, len(parts), B):
    open(f"{SP}/bk_{i//B}.graphql", "w").write("mutation { fileUpdate(files:[" + ",".join(parts[i:i+B]) + "]){ files{id fileStatus} userErrors{field message} } }")
print("total", len(parts), "bad", bad)
