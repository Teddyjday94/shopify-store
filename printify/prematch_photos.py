"""Match each Shopify photo to a Printify mockup (variant + camera), candidates = every mockup Printify lists for that
photo's color. Usage: prematch_any.py OUT.json handle=printify_id ..."""
import json, sys, io, time, re, concurrent.futures as cf
import requests, numpy as np
from PIL import Image
out_path, pairs = sys.argv[1], dict(a.split("=") for a in sys.argv[2:])
SIZES = {"XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL"}
s = requests.Session()
def get(url, **kw):
    for k in range(5):
        r = s.get(url, timeout=120, **kw)
        if r.status_code == 200 and r.content: return r
        time.sleep(3 + 4 * k)
    r.raise_for_status()
def thumb(url):
    return np.asarray(Image.open(io.BytesIO(get(url).content)).convert("RGB").resize((96, 96)), np.float32)
out = {}
for h, pid in pairs.items():
    prod = get(f"https://elsewhereapparelco.com/products/{h}.js").json()
    px = get(f"https://api.printify.com/v1/shops/29509655/products/{pid}.json", headers={"Authorization": "Bearer x"}).json()
    color_of = {v["id"]: next(x for x in v["title"].split(" / ") if x not in SIZES) for v in px["variants"]}
    cands = {}
    for im in px["images"]:
        vid, cam, fn = im["src"].split("/mockup/")[1].split("/")[1:4]
        cands.setdefault(color_of.get(int(vid)), []).append(f"https://images.printify.com/mockup/{pid}/{vid}/{cam}/{fn.split('?')[0]}")
    rows = []
    for m in prod["media"]:
        mm = re.match(re.escape(prod["title"]) + r" in (.+?), (.+)$", m["alt"] or "")
        if not mm or mm.group(1) not in cands:
            rows.append({"id": m["id"], "alt": m["alt"], "skip": "no color label / no mockups"}); continue
        cs = cands[mm.group(1)]
        with cf.ThreadPoolExecutor(6) as ex:
            T = list(ex.map(lambda u: thumb(u + "?s=256"), cs))
        mine = thumb((("https:" + m["src"]) if m["src"].startswith("//") else m["src"]) + "&width=256")
        d = [float(np.abs(mine - t).mean()) for t in T]
        j = int(np.argmin(d))
        rows.append({"id": m["id"], "alt": m["alt"], "url": cs[j], "d": round(d[j], 2),
                     "next": round(sorted(d)[1], 2) if len(d) > 1 else None})
    out[h] = {"pid": pid, "title": prod["title"], "rows": rows}
    print(h, [(r["alt"].split(", ", 1)[-1][:14], r.get("d"), r.get("next")) if "url" in r else r["skip"] for r in rows], flush=True)
json.dump(out, open(out_path, "w"), indent=1)
