"""Plan back-first product photos for the Immortalized and Christmas collections.

For each product: the Black back mockup, the other color's back, then the fronts, each labeled by
color and view. Writes scratch JSON for the Shopify media mutations (Shopify's own media order does
not match Printify's, so mockups are re-added by URL with labeled alt text).

Usage: python3 printify/media_plan.py OUT.json ["Title prefix" ...]   (prefixes limit it to those products)
"""

import json
import os
import sys

from create_products import Printify

TAGS = ("immortalized", "drop 004", "christmas collection", "player two")
SIZES = {"XS", "S", "M", "L", "XL", "2XL", "3XL"}


def color_of(product, variant):
    return next(part for part in variant["title"].split(" / ") if part not in SIZES)


def pick(product, ids, side):
    imgs = [i for i in product["images"] if set(i["variant_ids"]) & ids]
    for exact in (True, False):
        for i in imgs:
            label = i["src"].split("camera_label=")[-1]
            if (label == side) if exact else label.startswith(side):
                return i["src"]


def main(out, prefixes=()):
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    plan = {}
    for page in (1, 2, 3, 4):
        for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]:
            if not any(t in p["tags"] for t in TAGS) or "dad hat" in p["tags"]:
                continue
            if prefixes and not p["title"].startswith(tuple(prefixes)):
                continue
            colors = {}
            for v in p["variants"]:
                if v["is_enabled"]:
                    colors.setdefault(color_of(p, v), set()).add(v["id"])
            order = sorted(colors, key=lambda c: c != "Black")
            media = [(c, side, pick(p, colors[c], side)) for side in ("back", "front") for c in order]
            plan[p["external"]["id"]] = {"title": p["title"], "media": [
                {"color": c, "side": s, "url": u, "alt": f"{p['title']} in {c}, {s} print"} for c, s, u in media]}
            missing = [f"{c} {s}" for c, s, u in media if not u]
            print(p["title"], len(media), "missing: " + ", ".join(missing) if missing else "")
    json.dump(plan, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
