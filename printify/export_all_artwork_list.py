"""List every Printify product with its print-file names and URLs (for rebuilding designs/all-artwork).

Usage: python3 printify/export_all_artwork_list.py OUT.json
"""
import json, os, sys
sys.path.insert(0, "/home/user/shopify-store/printify")
from create_products import Printify
api = Printify(os.environ.get("PRINTIFY_API_TOKEN") or "x")
shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
out, page = [], 1
while True:
    d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
    for p in d["data"]:
        imgs = [dict(position=ph["position"], id=i["id"], name=i.get("name"), src=i.get("src"), w=i.get("width"), h=i.get("height"), type=i.get("type"))
                for a in p["print_areas"] for ph in a["placeholders"] for i in ph["images"]]
        out.append({"title": p["title"], "tags": p["tags"], "visible": p.get("visible"), "images": imgs})
    if page >= d["last_page"]: break
    page += 1
json.dump(out, open(sys.argv[1], "w"), indent=1)
ids = {i["id"] for p in out for i in p["images"]}
print(len(out), "products", len(ids), "unique images")
