"""Emit the Shopify mutations that finish a women's tee move (see move_womens.py).

For each moved product whose new Shopify listing exists: take over the old handle, set the cleaned
description, add one labeled photo per color ("<Title> in <Color>, <side> print", Black first) and
put Color before Size with Black first.

Usage: python3 printify/womens_shopify_swap.py OUT_PREFIX "Title" ...   (no titles = all not yet swapped)
Writes OUT_PREFIX0.graphql, OUT_PREFIX1.graphql, ... (8 products each) and marks nothing; run
--mark "Title" ... after the mutations succeed.
"""

import json
import os
import sys
from pathlib import Path

from create_products import Printify

OUT = Path(__file__).with_name("moved_womens.json")
SIZES = ["S", "M", "L", "XL", "2XL"]


def main():
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    moved = json.loads(OUT.read_text())
    if sys.argv[1] == "--mark":
        for m in moved.values():
            if m["title"] in sys.argv[2:]:
                m["swapped"] = True
        OUT.write_text(json.dumps(moved, indent=2))
        return
    prefix, titles = sys.argv[1], set(sys.argv[2:])
    parts = []
    for m in moved.values():
        if m.get("swapped") or (titles and m["title"] not in titles):
            continue
        p = api.get(f"/shops/{shop}/products/{m['new_printify']}.json")
        sid = (p.get("external") or {}).get("id")
        if not sid:
            print("not in Shopify yet:", m["title"])
            continue
        side = m["sides"][0]
        colors = {}
        for v in p["variants"]:
            if v["is_enabled"]:
                colors.setdefault(v["title"].split(" / ")[1], set()).add(v["id"])
        order = sorted(colors, key=lambda c: c != "Black")
        media = []
        for c in order:
            src = next((i["src"] for i in p["images"] if set(i["variant_ids"]) & colors[c]
                        and i["src"].endswith("camera_label=" + side)), None)
            if src:
                media.append('{originalSource:%s,alt:%s,mediaContentType:IMAGE}' % (
                    json.dumps(src + "&s=2048"), json.dumps(f"{m['title']} in {c}, {side} print")))
            else:
                print("no mockup:", m["title"], c)
        gid = f"gid://shopify/Product/{sid}"
        parts.append('u%s: productUpdate(product:{id:"%s", handle:%s, descriptionHtml:%s}, media:[%s]){ product{handle} userErrors{message} }'
                     % (sid, gid, json.dumps(m["old_handle"]), json.dumps(p["description"]), ",".join(media)))
        opts = ",".join('{name:%s}' % json.dumps(c) for c in order)
        parts.append('o%s: productOptionsReorder(productId:"%s", options:[{name:"Color", values:[%s]},{name:"Size", values:[%s]}]){ userErrors{message} }'
                     % (sid, gid, opts, ",".join('{name:"%s"}' % s for s in SIZES)))
    for b in range(0, len(parts), 16):
        Path(f"{prefix}{b // 16}.graphql").write_text("mutation { " + " ".join(parts[b:b + 16]) + " }")
    print(len(parts) // 2, "products,", (len(parts) + 15) // 16, "files")


if __name__ == "__main__":
    main()
