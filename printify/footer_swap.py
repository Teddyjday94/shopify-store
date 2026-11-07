"""Put the Immortalized prints with the larger footer onto the tees, hoodies and posters.

Apparel: the back and front print files are replaced in place. The new back is taller (bigger footer), so its
scale is reduced to keep the same printed height and center; the front keeps its scale. Apparel is NOT
republished to Shopify: its photos are rebuilt with labeled mockups afterwards (media_plan.py), which also
covers products whose Printify sync is stuck.
Posters: the poster file is replaced at the same placement and republished with new mockups.

Usage: python3 printify/footer_swap.py --commit SHA [--apply]
"""

import argparse
import base64
import os
import time

from PIL import Image

from create_products import Printify

DESIGNS = os.path.join(os.path.dirname(__file__), "..", "designs")
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-drop4/{name}"
SLUGS = ["01-lead-the-charge", "02-rise-from-ruin", "03-sleep-paralysis-club", "04-one-way-ferry",
         "05-born-ready", "06-fallen-not-finished", "07-above-it-all", "08-going-with-the-flow",
         "09-long-live-the-king", "10-queen-forever", "11-nine-tails", "12-masterless"]
PRINTS = {f"{s}-{side}.png" for s in SLUGS for side in ("back", "front")}
POSTERS = {f"{s}-poster.jpg": s for s in SLUGS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    uploads = {}

    def upload_url(name):
        if name not in uploads:
            uploads[name] = api.post("/uploads/images.json", {"file_name": name, "url": RAW.format(commit=args.commit, name=name)})["id"]
        return uploads[name]

    def upload_file(path):
        if path not in uploads:
            with open(path, "rb") as f:
                uploads[path] = api.post("/uploads/images.json", {"file_name": os.path.basename(path),
                                                                  "contents": base64.b64encode(f.read()).decode()})["id"]
        return uploads[path]

    products, page = [], 1
    while True:
        d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        products += d["data"]
        if page >= d["last_page"]:
            break
        page += 1

    for p in products:
        names = {i["name"] for a in p["print_areas"] for ph in a["placeholders"] for i in ph["images"]}
        apparel = sorted(names & PRINTS)
        poster = sorted(names & POSTERS.keys())
        if not apparel and not poster:
            continue
        areas, notes = [], []
        for a in p["print_areas"]:
            phs = []
            for ph in a["placeholders"]:
                if not ph["images"]:
                    continue
                imgs = []
                for i in ph["images"]:
                    place = dict(x=i["x"], y=i["y"], scale=i["scale"], angle=i["angle"])
                    if i["name"] in PRINTS:
                        nw, nh = Image.open(os.path.join(DESIGNS, "print-drop4", i["name"])).size
                        if i["name"].endswith("-back.png"):
                            place["scale"] = round(i["scale"] * (i["height"] / i["width"]) / (nh / nw), 4)
                            notes.append(f"back {i['scale']:.3f}->{place['scale']:.3f}")
                        imgs.append(dict(id=upload_url(i["name"]) if args.apply else "?", **place))
                    elif i["name"] in POSTERS:
                        path = os.path.join(DESIGNS, "print-wall", i["name"])
                        imgs.append(dict(id=upload_file(path) if args.apply else "?", **place))
                    else:
                        imgs.append(dict(id=i["id"], **place))
                phs.append({"position": ph["position"], "images": imgs})
            areas.append({"variant_ids": a["variant_ids"], "placeholders": phs})
        print(f"{'swap' if args.apply else 'plan'}  {p['title']}: {', '.join(apparel + poster)} {sorted(set(notes))}")
        if not args.apply:
            continue
        api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json={"print_areas": areas})
        if poster:
            api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
                "title": False, "description": False, "images": True, "variants": False,
                "tags": False, "keyFeatures": False, "shipping_template": False})
            time.sleep(20)  # Printify publish rate limit
        else:
            time.sleep(2)


if __name__ == "__main__":
    main()
