"""Sleeve test drop: long-sleeve tees (front + both sleeves) and sleeve-edition hoodies (back + both
sleeves) for Rise From Ruin, Horror Club and No Signal, on SwiftPOD.

Costs (size M): long sleeve $26.63, hoodie $35.79; Printify shipping $4.49 / $7.99. Priced $37 / $47.
Sleeve art: designs/sleeves/*.png (designs/src/render_sleeves.js), reads shoulder to cuff.

Usage:
    python3 printify/create_sleeve_drop.py --commit SHA [--only KEY] [--publish]
    (without --publish the products are created as drafts in Printify only, for checking mockups)
"""
import argparse, json, os, time
from pathlib import Path
from create_products import Printify

SHOP = 29509655
PP = 39  # SwiftPOD
RAW = "https://raw.githubusercontent.com/Teddyjday94/shopify-store/{c}/designs/sleeves/{n}"
OUT = Path(__file__).with_name("sleeve_drop.json")
SIZES = ["S", "M", "L", "XL", "2XL"]
MARGIN = 0.97
DESIGNS = {
    "rise-from-ruin": dict(name="Rise From Ruin", art=("6af37fd36d784ff9e21792ed", 4487, 6723), source="Rise From Ruin Tee",
        line="Two fighters claw their way out of a burning underworld.", tag="Down bad. Getting up anyway.",
        sleeves="RISE FROM RUIN down one sleeve, LEGENDS NEVER DIE down the other"),
    "horror-club": dict(name="Horror Club", art=("6af22ba5ee0bcaece4a095d4", 4199, 4200), source="Horror Club Tee",
        line="A skeleton and a monster shake on it inside a varsity-patch crest.", tag="Members only. Est. Elsewhere.",
        sleeves="HORROR CLUB down one sleeve, CREATURE FEATURE down the other"),
    "no-signal": dict(name="No Signal", art=("6aefc1c50e9d90cc9b63bda3", 4082, 4328), source="No Signal Tee",
        line="A lone astronaut, a glowing vending machine and a planet that doesn't answer back.", tag="No signal in this universe.",
        sleeves="NO SIGNAL down one sleeve, IN THIS UNIVERSE down the other"),
}
KINDS = {
    "longsleeve": dict(bp=80, title="{name} Long Sleeve Tee", price=3700, main="front", tags=["tee", "long sleeve", "sleeve print"],
        bullets=["Full-color front print", "Lettering down both sleeves", "Classic-fit 100% cotton long sleeve", "Printed to order just for you"]),
    "hoodie": dict(bp=77, title="{name} Sleeve Edition Hoodie", price=4700, main="back", tags=["hoodie", "sleeve print"],
        bullets=["Big back print", "Lettering down both sleeves", "Heavy blend fleece hoodie", "Printed to order just for you"]),
}


def fill(img, area, top=True):
    iid, w, h = img
    aw, ah = area
    ratio, area_ratio = h / w, ah / aw
    scale = MARGIN * min(1.0, area_ratio / ratio)
    hf = scale * ratio / area_ratio
    y = (1 - MARGIN) / 2 + hf / 2 if top else 0.5
    return dict(id=iid, x=0.5, y=round(y, 4), scale=round(scale, 4), angle=0)


def publish(api, done, pkey):
    pid = done[pkey]["printify"]
    for wait in (0, 120, 300, 600):
        time.sleep(wait)
        try:
            api.post(f"/shops/{SHOP}/products/{pid}/publish.json", {
                "title": True, "description": True, "images": False, "variants": True,
                "tags": True, "keyFeatures": True, "shipping_template": True})
            done[pkey]["published"] = True
            print("published", done[pkey]["title"], flush=True)
            return
        except Exception as e:
            print("  publish retry:", str(e)[:100], flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--only")
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    done = json.loads(OUT.read_text()) if OUT.exists() else {}
    shop_products = []
    for page in range(1, 8):
        d = api.get(f"/shops/{SHOP}/products.json?limit=50&page={page}")
        shop_products += d["data"]
        if page >= d["last_page"]:
            break
    uploads = {}

    def up(n):
        if n not in uploads:
            r = api.post("/uploads/images.json", {"file_name": n, "url": RAW.format(c=args.commit, n=n)})
            uploads[n] = (r["id"], r["width"], r["height"])
        return uploads[n]

    for key, d in DESIGNS.items():
        for kind, k in KINDS.items():
            pkey = f"{key}-{kind}"
            if args.only and args.only not in pkey:
                continue
            if pkey in done:
                if args.publish and not done[pkey].get("published"):
                    publish(api, done, pkey)
                    OUT.write_text(json.dumps(done, indent=2))
                continue
            vs = api.get(f"/catalog/blueprints/{k['bp']}/print_providers/{PP}/variants.json")["variants"]
            areas = {}
            for v in vs:
                for ph in v["placeholders"]:
                    if ph["width"] > areas.get(ph["position"], (0, 0))[0]:
                        areas[ph["position"]] = (ph["width"], ph["height"])
            ids = [v["id"] for v in vs if v["options"].get("color") == "Black" and v["options"].get("size") in SIZES]
            src = next(p for p in shop_products if p["title"] == d["source"])
            tags = sorted({t for t in src["tags"] if t not in ("tee", "womens", "hoodie")} | set(k["tags"]))
            placeholders = [{"position": k["main"], "images": [fill(d["art"], areas[k["main"]])]}]
            for side in ("left", "right"):
                placeholders.append({"position": f"{side}_sleeve",
                                     "images": [fill(up(f"{key}-{side}.png"), areas[f"{side}_sleeve"], top=False)]})
            desc = (f"<p>{d['line']}</p><ul>\n" + "".join(f"<li>{b}</li>\n" for b in k["bullets"]) +
                    f"</ul><p>Sleeves: {d['sleeves']}.</p><p><em>{d['tag']}</em></p>")
            body = {"title": k["title"].format(name=d["name"]), "description": desc, "tags": tags,
                    "blueprint_id": k["bp"], "print_provider_id": PP,
                    "variants": [{"id": i, "price": k["price"], "is_enabled": True} for i in ids],
                    "print_areas": [{"variant_ids": ids, "placeholders": placeholders}]}
            p = api.post(f"/shops/{SHOP}/products.json", body)
            cost = sorted({v["cost"] for v in p["variants"] if v["is_enabled"]})
            done[pkey] = {"printify": p["id"], "title": body["title"], "cost": cost}
            OUT.write_text(json.dumps(done, indent=2))
            print("created", body["title"], p["id"], "cost", [c / 100 for c in cost], flush=True)
            if args.publish:
                publish(api, done, pkey)
                OUT.write_text(json.dumps(done, indent=2))


if __name__ == "__main__":
    main()
