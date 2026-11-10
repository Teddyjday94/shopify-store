"""Swap the re-rendered Legends Never Die art (caption and chest mark now read LEGENDS NEVER DIE
instead of IMMORTALIZED) onto the tees, women's tees and hoodies.

Paintings keep their width, so their placement is unchanged. The hoodie chest mark got wider, so its
scale is reduced to keep the same printed height. Products are republished without images; the shop
photos are rebuilt afterwards from the new mockups (--media writes those Shopify mutations).

Usage:
    python3 printify/legends_caption_swap.py --commit SHA            # dry run
    python3 printify/legends_caption_swap.py --commit SHA --apply
    python3 printify/legends_caption_swap.py --media OUT_PREFIX      # after mockups regenerate
"""

import argparse
import json
import os
import time
from pathlib import Path

from PIL import Image

from create_products import Printify

DESIGNS = Path(__file__).resolve().parent.parent / "designs" / "print-drop4"
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-drop4/{name}"
SLUGS = ["01-lead-the-charge", "02-rise-from-ruin", "03-sleep-paralysis-club", "04-one-way-ferry",
         "05-born-ready", "06-fallen-not-finished", "07-above-it-all", "08-going-with-the-flow",
         "09-long-live-the-king", "10-queen-forever", "12-masterless"]
PRINTS = {f"{s}-{side}.png" for s in SLUGS for side in ("back", "front")}
DONE = Path(__file__).with_name("legends_caption_done.json")
SIZES = {"XS", "S", "M", "L", "XL", "2XL", "3XL"}


def products(api, shop):
    page, last = 1, 1
    while page <= last:
        d = api.get(f"/shops/{shop}/products.json?limit=50&page={page}")
        last, page = d["last_page"], page + 1
        for p in d["data"]:
            names = {i["name"] for a in p["print_areas"] for ph in a["placeholders"] for i in ph["images"]}
            if names & PRINTS:
                yield p


def media(api, shop, prefix):
    parts = []
    for pid in json.loads(DONE.read_text()):
        p = api.get(f"/shops/{shop}/products/{pid}.json")
        sid = p["external"]["id"]
        side = "back" if p["title"].endswith("Hoodie") else "front"
        colors = {}
        for v in p["variants"]:
            if v["is_enabled"]:
                c = next(x for x in v["title"].split(" / ") if x not in SIZES)
                colors.setdefault(c, set()).add(v["id"])
        order = sorted(colors, key=lambda c: c not in ("Black", "Solid Black"))
        items = []
        for c in order:
            imgs = [i["src"] for i in p["images"] if set(i["variant_ids"]) & colors[c]]
            src = next((s for s in imgs if s.endswith("camera_label=" + side)), None) or \
                next((s for s in imgs if ("camera_label=" + side) in s), None)
            if src:
                items.append('{originalSource:%s,alt:%s,mediaContentType:IMAGE}' % (
                    json.dumps(src + "&s=2048"), json.dumps(f"{p['title']} in {c}, {side} print")))
            else:
                print("no mockup:", p["title"], c)
        parts.append('a%s: productUpdate(product:{id:"gid://shopify/Product/%s"}, media:[%s]){ userErrors{message} }'
                     % (sid, sid, ",".join(items)))
    for b in range(0, len(parts), 8):
        Path(f"{prefix}{b // 8}.graphql").write_text("mutation { " + " ".join(parts[b:b + 8]) + " }")
    print(len(parts), "products")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--media")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    if args.media:
        return media(api, shop, args.media)
    done = json.loads(DONE.read_text()) if DONE.exists() else []
    uploads = {}
    for p in products(api, shop):
        if p["id"] in done:
            continue
        areas = []
        for a in p["print_areas"]:
            phs = []
            for ph in a["placeholders"]:
                imgs = []
                for i in ph["images"]:
                    place = dict(x=i["x"], y=i["y"], scale=i["scale"], angle=i.get("angle", 0))
                    name = i["name"]
                    if name in PRINTS:
                        nw, nh = Image.open(DESIGNS / name).size
                        if name.endswith("-front.png"):  # chest mark: keep printed height
                            place["scale"] = round(i["scale"] * (i["width"] / nw) * (nh / i["height"]), 4)
                        if args.apply and name not in uploads:
                            uploads[name] = api.post("/uploads/images.json", {
                                "file_name": name, "url": RAW.format(commit=args.commit, name=name)})["id"]
                        imgs.append(dict(id=uploads.get(name, "?"), **place))
                    else:
                        imgs.append(dict(id=i["id"], **place))
                if imgs:
                    phs.append({"position": ph["position"], "images": imgs})
            areas.append({"variant_ids": a["variant_ids"], "placeholders": phs})
        print(("apply " if args.apply else "plan  ") + p["title"], flush=True)
        if not args.apply:
            continue
        api.call("PUT", f"/shops/{shop}/products/{p['id']}.json", json={"print_areas": areas})
        for wait in (0, 120, 300, 600, 900):
            time.sleep(wait)
            try:
                api.post(f"/shops/{shop}/products/{p['id']}/publish.json", {
                    "title": False, "description": False, "images": False, "variants": False,
                    "tags": False, "keyFeatures": False, "shipping_template": False})
                break
            except Exception as e:
                print("   publish retry:", str(e)[:100], flush=True)
        done.append(p["id"])
        DONE.write_text(json.dumps(done, indent=1))
        time.sleep(8)


if __name__ == "__main__":
    main()
