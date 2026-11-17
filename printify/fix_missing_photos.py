"""Add photos to Shopify for Printify products whose images never arrived (2026-11-17: the new crewnecks and
some ornaments were published to Shopify with no photos, although Printify had mockups selected).

Crewnecks: one labeled photo per enabled color ("<Title> in <Color>, front print", or back print for
back-printed ones), plus back/folded views of the main color (Black when offered). Ornaments: their three
Printify shots. Writes a JSONL file for Shopify's bulk mutation (productUpdate with media).

Usage: python3 printify/fix_missing_photos.py OUT.jsonl SHOPIFY_COUNTS.json
  SHOPIFY_COUNTS.json: {"<shopify product id>": <current media count>, ...}
"""
import json, sys, requests, concurrent.futures as cf
from create_products import Printify

SHOP = 29509655
FRONT, BACK, FOLDED = 98502, 98503, 100648


def warm(url):
    try:
        r = requests.get(url, timeout=120)
        return r.ok and len(r.content) > 30000
    except Exception:
        return False


def main():
    out, counts = sys.argv[1], json.load(open(sys.argv[2]))
    api = Printify(None)
    catalogs, items, page = {}, [], 1
    while True:
        r = api.get(f"/shops/{SHOP}/products.json?limit=50&page={page}")
        items += [x for x in r["data"] if ("Crewneck" in x["title"] or "Ornament" in x["title"]) and (x.get("external") or {}).get("id")]
        if not r.get("next_page_url") or not r["data"]:
            break
        page += 1
    lines, jobs = [], []
    for x in items:
        sid = str(x["external"]["id"])
        have = counts.get(sid, 0)
        media = []
        if "Crewneck" in x["title"]:
            if have:
                continue
            key = (x["blueprint_id"], x["print_provider_id"])
            if key not in catalogs:
                catalogs[key] = {c["id"]: c["options"] for c in api.get(f"/catalog/blueprints/{key[0]}/print_providers/{key[1]}/variants.json")["variants"]}
            cat = catalogs[key]
            sides = {ph["position"] for pa in x["print_areas"] for ph in pa["placeholders"] if ph["images"]}
            back = "back" in sides and "front" not in sides
            src = x["images"][0]["src"]
            mock, _, _, name = src.split("/mockup/")[1].split("/")[:4]
            name = name.split(".jpg")[0]
            by_color = {}
            for v in x["variants"]:
                if v["is_enabled"]:
                    by_color.setdefault(cat[v["id"]]["color"], v["id"])
            colors = sorted(by_color, key=lambda c: (c != "Black", list(by_color).index(c)))
            url = lambda vid, cam: f"https://images.printify.com/mockup/{mock}/{vid}/{cam}/{name}.jpg?s=2048"
            for i, color in enumerate(colors):
                vid = by_color[color]
                media.append((url(vid, BACK if back else FRONT), f"{x['title']} in {color}, {'back' if back else 'front'} print"))
                if i == 0:
                    media.append((url(vid, FRONT if back else BACK), f"{x['title']} in {color}, {'front' if back else 'back'} view"))
                    media.append((url(vid, FOLDED), f"{x['title']} in {color}, folded"))
        else:
            if have >= len(x["images"]):
                continue
            shots = [(im["src"].split("?")[0] + "?s=2048", im["src"].split("camera_label=")[-1]) for im in x["images"]]
            desc = {"front": "front", "context-1": "hanging on a tree", "context-2": "in a gift setting"}
            shots = shots[have:]  # what's there already is Printify's first shot(s)
            media = [(u, f"{x['title']}, {desc.get(c, c)}") for u, c in shots]
        jobs += [m[0] for m in media]
        lines.append({"product": {"id": f"gid://shopify/Product/{sid}"},
                      "media": [{"originalSource": u, "alt": a, "mediaContentType": "IMAGE"} for u, a in media]})
        print(x["title"], len(media), flush=True)
    with cf.ThreadPoolExecutor(12) as ex:
        ok = list(ex.map(warm, jobs))
    bad = [u for u, k in zip(jobs, ok) if not k]
    print("photos", len(jobs), "not ready", len(bad), bad[:5])
    with open(out, "w") as f:
        for l in lines:
            f.write(json.dumps(l) + "\n")


if __name__ == "__main__":
    main()
