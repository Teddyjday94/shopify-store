"""Plan side-view-first photos for the mugs.

Mug designs print twice, a quarter of the way in from each edge of the wrap. Printify's "front" mockup
faces the middle of the wrap (the gap between the copies); its "left" mockup faces one full copy.
This lists, per Shopify product, the left mockup of each size so it can be added and put first, and
each size's variant pointed at its own left view (Shopify's media order does not follow Printify's).

Usage: python3 printify/mug_photos.py OUT.json
"""

import json
import os
import sys

from create_products import Printify


def main(out):
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    plan = {}
    for page in (1, 2, 3, 4):
        for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]:
            if not p["title"].endswith(" Mug") or not (p.get("external") or {}).get("id"):
                continue
            sizes = {v["id"]: v["title"] for v in p["variants"] if v["is_enabled"]}
            views = []
            for vid, size in sorted(sizes.items(), key=lambda kv: kv[1]):
                src = next((i["src"] for i in p["images"]
                            if vid in i["variant_ids"] and i["src"].endswith("camera_label=left")), None)
                if src:
                    views.append({"size": size, "url": src, "alt": f"{p['title']}, {size}, design facing"})
            plan[p["external"]["id"]] = {"title": p["title"], "views": views}
    json.dump(plan, open(out, "w"), indent=1)
    print(len(plan), "mugs;", sum(len(v["views"]) for v in plan.values()), "side views")


if __name__ == "__main__":
    main(sys.argv[1])
