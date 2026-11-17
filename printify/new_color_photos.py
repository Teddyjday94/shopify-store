"""Labeled flat photo for every colour added by apply_color_plan.py (2026-11-17), as GraphQL-variable batches
(this connection caps the query text at 16KB). Hoodies show the back print, everything else the front.
Usage: python3 printify/new_color_photos.py OUT_DIR   -> OUT_DIR/ph_N.json  {"q": query, "v": variables}
"""
import json, sys
from pathlib import Path
import requests
from create_products import Printify

SHOP = 29509655
DONE = Path(__file__).with_name("color_plan_done.json")
CAM = {(12, "front"): 102044, (12, "back"): 102045, (466, "front"): 87728, (466, "back"): 87729,
       (77, "back"): 98425, (77, "front"): 98424, (49, "front"): 98502, (49, "back"): 98503}


def main():
    out = Path(sys.argv[1]); out.mkdir(exist_ok=True)
    api = Printify(None)
    done = json.loads(DONE.read_text())
    cats, items = {}, []
    for title, v in done.items():
        x = api.get(f"/shops/{SHOP}/products/{v['printify']}.json")
        bp, pp = x["blueprint_id"], x["print_provider_id"]
        if (bp, pp) not in cats:
            cats[(bp, pp)] = {c["id"]: c["options"] for c in api.get(f"/catalog/blueprints/{bp}/print_providers/{pp}/variants.json")["variants"]}
        cat = cats[(bp, pp)]
        src = next(im["src"] for im in x["images"] if "/mockup/" in im["src"])
        mock, _, _, name = src.split("/mockup/")[1].split("/")[:4]
        name = name.split(".jpg")[0]
        side = "back" if (bp == 77 and "back" in v["sides"]) or "front" not in v["sides"] else "front"
        cam = CAM.get((bp, side))
        if not cam:   # e.g. long sleeve: take the camera of an existing photo of that side
            cam = next((int(im["src"].split("/mockup/")[1].split("/")[2]) for im in x["images"]
                        if "/mockup/" in im["src"] and im.get("position") == side), None)
        media = []
        for color in v["added"]:
            vid = next((vv["id"] for vv in x["variants"] if vv["is_enabled"] and color in vv["title"].split(" / ")), None)
            if not vid:
                print("not enabled:", title, color); continue
            url = f"https://images.printify.com/mockup/{mock}/{vid}/{cam}/{name}.jpg?s=2048"
            r = requests.get(url, timeout=120)
            if not r.ok or len(r.content) < 40000:
                print("missing:", title, color, r.status_code, len(r.content)); continue
            media.append({"originalSource": url, "alt": f"{title} in {color}, {side} print", "mediaContentType": "IMAGE"})
        if media:
            items.append((v["shopify"], media))
        print(title, len(media), "photos", flush=True)
    batches, cur, size = [], [], 0
    for sid, media in items:
        n = len(json.dumps(media))
        if cur and size + n > 26000:
            batches.append(cur); cur, size = [], 0
        cur.append((sid, media)); size += n
    if cur:
        batches.append(cur)
    for i, b in enumerate(batches):
        q = "mutation(" + ",".join(f"$m{k}:[CreateMediaInput!]" for k in range(len(b))) + "){" + " ".join(
            f'a{k}:productUpdate(product:{{id:"gid://shopify/Product/{sid}"}},media:$m{k}){{userErrors{{message}}}}'
            for k, (sid, _) in enumerate(b)) + "}"
        (out / f"ph_{i}.json").write_text(json.dumps({"q": q, "v": {f"m{k}": m for k, (_, m) in enumerate(b)}}))
    print(len(items), "products,", sum(len(m) for _, m in items), "photos,", len(batches), "batches")


if __name__ == "__main__":
    main()
