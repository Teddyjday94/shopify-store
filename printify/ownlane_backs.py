"""Own Lane: swap the hoodie back picture for the name in type, add the same back to the tees, and add burgundy.

The back design (designs/print-back/, rendered by designs/src/render_ownlane_backs.js) comes in white
text for dark garments and black text for light ones, so each product gets one print area per text
color. The front art and its placement are kept as they are. Tees gain a back print, so they move to
the front-and-back tee price.

Usage:
    python3 printify/ownlane_backs.py            # dry run
    python3 printify/ownlane_backs.py --apply
"""

import argparse
import os

from PIL import Image

from create_products import TEE_SIZES, XXL_UPCHARGE, Printify
from fit import ROOT

COMMIT = "0805d780bfa4496e423aeff8a96e7b8b6c3700ee"
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{commit}/designs/print-back/{name}"
BACK_DIR = ROOT / "designs" / "print-back"
BURGUNDY = {77: "Maroon", 12: "Maroon"}
TEE_PRICE = 3000  # front + back, same as the Drop 002 tees
WHITE_TEXT = {"Black", "Forest Green", "Forest", "Maroon", "Military Green", "Royal", "Charcoal", "Navy", "Heather Olive"}
ART = {  # product title (without the Tee/Hoodie suffix) -> art file prefix
    "In My Own Lane": "01-in-my-own-lane",
    "Butterfly Effect": "02-butterfly-effect",
    "Lucky Charm": "03-lucky-charm",
    "Sunflower Soul": "04-sunflower-soul",
    "Color Me Bold": "05-color-me-bold",
    "Crown & Curls": "06-crown-and-curls",
    "Pink Crown": "07-pink-crown",
    "Sisterhood": "08-sisterhood",
}


def back_place(name, area_w, area_h, width=0.8, max_height=0.62, top=0.05):
    with Image.open(BACK_DIR / name) as im:
        ratio = (im.height / im.width) * (area_w / area_h)
    scale = min(width, max_height / ratio)
    return dict(x=0.5, y=round(top + scale * ratio / 2, 4), scale=round(scale, 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    apply = ap.parse_args().apply

    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    uploads = {}

    def image_id(name):
        if name not in uploads:
            uploads[name] = api.post("/uploads/images.json", {"file_name": name, "url": RAW.format(commit=COMMIT, name=name)})["id"]
        return uploads[name]

    for page in (1, 2):
        for p in api.get(f"/shops/{shop}/products.json?limit=50&page={page}")["data"]:
            base_title = p["title"].rsplit(" ", 1)[0]
            if base_title not in ART or p["blueprint_id"] not in BURGUNDY or not (p.get("external") or {}).get("id"):
                continue
            path = f"/shops/{shop}/products/{p['id']}.json"
            catalog = api.get(f"/catalog/blueprints/{p['blueprint_id']}/print_providers/{p['print_provider_id']}/variants.json")
            options = {v["id"]: v["options"] for v in catalog["variants"]}
            sizes = {ph["position"]: (ph["width"], ph["height"]) for ph in catalog["variants"][0]["placeholders"]}
            is_tee = p["blueprint_id"] == 12

            front = next(ph["images"][0] for a in p["print_areas"] for ph in a["placeholders"]
                         if ph["position"] == "front" and ph["images"])
            burgundy = BURGUNDY[p["blueprint_id"]]
            enabled = {v["id"] for v in p["variants"] if v["is_enabled"]}
            enabled |= {vid for vid, o in options.items() if o.get("color") == burgundy and o.get("size") in TEE_SIZES}
            base = TEE_PRICE if is_tee else min(v["price"] for v in p["variants"]
                                                if v["is_enabled"] and options[v["id"]].get("size") != "2XL")

            groups = {}
            for vid in enabled:
                groups.setdefault("white" if options[vid].get("color") in WHITE_TEXT else "black", []).append(vid)
            areas = []
            for ink, ids in sorted(groups.items()):
                name = f"{ART[base_title]}-back-{ink}.png"
                place = back_place(name, *sizes["back"])
                back = dict(id=image_id(name) if apply else name, angle=0, **place)
                areas.append({"variant_ids": sorted(ids), "placeholders": [
                    {"position": "front", "images": [dict(id=front["id"], x=front["x"], y=front["y"],
                                                          scale=front["scale"], angle=front["angle"])]},
                    {"position": "back", "images": [back]},
                ]})
            colors = sorted({options[v]["color"] for v in enabled})
            print(f"{'set ' if apply else 'plan'}  {p['title']}: colors {colors}; "
                  f"white text on {sorted({options[v]['color'] for v in groups.get('white', [])})}; "
                  f"back {place['scale']:.0%} wide" + (f"; price ${base / 100:.0f}" if is_tee else ""))
            if not apply:
                continue
            variants = [{"id": v["id"], "is_enabled": v["id"] in enabled,
                         "price": base + (XXL_UPCHARGE if options[v["id"]].get("size") == "2XL" else 0)}
                        for v in p["variants"] if v["id"] in options]
            updated = api.call("PUT", path, json={"variants": variants, "print_areas": areas})
            costs = [v["cost"] for v in updated["variants"] if v["is_enabled"]]
            api.post(f"{path[:-5]}/publish.json", {
                "title": False, "description": False, "images": True, "variants": True,
                "tags": False, "keyFeatures": False, "shipping_template": False,
            })
            print(f"      cost ${min(costs) / 100:.2f}-${max(costs) / 100:.2f}")


if __name__ == "__main__":
    main()
