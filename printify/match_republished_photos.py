"""After a Printify republish replaces a product's Shopify photos (unlabeled, random order), match each Shopify
photo to its Printify mockup (color + camera) by image comparison, and find duplicate imports.
Usage: python3 -I printify/match_republished_photos.py WORKDIR   (WORKDIR holds <handle>.js from
https://elsewhereapparelco.com/products/<handle>.js; writes WORKDIR/match.json). Edit PF for the products.
Hoodie (Gildan 18500) cameras: 98424 front, 98425 back, 98426 back 2nd view, 98432 folded, 110151 size chart.
Used 2026-11-27 for the four Legends Never Die hoodies (labels, order, variant photos, duplicates detached).
"""
import json, re, sys, os, io, concurrent.futures as cf
import requests, numpy as np
from PIL import Image
S = sys.argv[1]
PF = {"born-ready-hoodie": "6ae779f2f9c00c9ec009d8e0", "fallen-not-finished-hoodie": "6ae77a2517932a00ba02a3f6",
      "going-with-the-flow-hoodie": "6ae77a88d037ed7f1f02b9d9", "queen-forever-hoodie": "6aea941b365c19e4ba07e801"}
CAM = {"98424": "front print", "98425": "back print", "98426": "back print, second view", "98432": "side view"}
sess = requests.Session()
def thumb(url):
    for _ in range(3):
        try:
            r = sess.get(url, timeout=90); r.raise_for_status()
            im = Image.open(io.BytesIO(r.content)).convert("RGB").resize((64, 64), Image.BILINEAR)
            return np.asarray(im, dtype=np.float32)
        except Exception as e: err = e
    raise err
out = {}
for handle, pid in PF.items():
    prod = json.load(open(f"{S}/{handle}.js"))
    px = sess.get(f"https://api.printify.com/v1/shops/29509655/products/{pid}.json", headers={"Authorization": "Bearer x"}, timeout=60).json()
    vmap = {v["id"]: v["title"].split(" / ")[0] for v in px["variants"]}
    pims = []
    for im in px["images"]:
        vid, cam = im["src"].split("/mockup/")[1].split("/")[1:3]
        pims.append({"color": vmap.get(int(vid), "?"), "cam": cam, "src": im["src"]})
    media = [{"id": m["id"], "src": m["src"]} for m in prod["media"]]
    base = lambda u: re.sub(r"_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "", u.split("?")[0].rsplit("/", 1)[-1])
    seen, originals, dupes = {}, [], []
    for m in media:
        b = base(m["src"])
        if b in seen: dupes.append((m["id"], seen[b]))
        else: seen[b] = m["id"]; originals.append(m)
    with cf.ThreadPoolExecutor(12) as ex:
        P = list(ex.map(lambda p: thumb(re.sub(r"\?.*$", "", p["src"]) + "?s=256"), pims))
        M = list(ex.map(lambda m: thumb(m["src"].split("?")[0] + "?width=256"), originals))
        D = list(ex.map(lambda d: thumb(next(x["src"] for x in media if x["id"] == d[0]).split("?")[0] + "?width=256"), dupes))
    dist = np.array([[np.abs(m - p).mean() for p in P] for m in M])
    pairs = sorted((dist[i, j], i, j) for i in range(len(M)) for j in range(len(P)))
    ui, uj, match = set(), set(), {}
    for d, i, j in pairs:
        if i in ui or j in uj: continue
        ui.add(i); uj.add(j); match[i] = (j, float(d))
    rows = []
    for i, m in enumerate(originals):
        j, d = match.get(i, (None, None))
        second = sorted(dist[i])[1] if len(P) > 1 else None
        rows.append({"id": m["id"], "color": pims[j]["color"] if j is not None else None, "cam": pims[j]["cam"] if j is not None else None, "d": round(d, 2) if d is not None else None, "next": round(float(second), 2)})
    dd = [{"id": a, "of": b, "d": round(float(np.abs(D[k] - M[[o["id"] for o in originals].index(b)]).mean()), 2)} for k, (a, b) in enumerate(dupes)]
    variants = {v["option1"]: (v["featured_media"] or {}).get("id") for v in prod["variants"]}
    out[handle] = {"title": prod["title"], "rows": rows, "dupes": dd, "variant_media": variants}
    print(handle, len(originals), "orig", len(dupes), "dupes", "maxd", max(r["d"] for r in rows), "unmatched", sum(r["color"] is None for r in rows), flush=True)
json.dump(out, open(f"{S}/match.json", "w"), indent=1)
