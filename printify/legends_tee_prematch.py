"""(2026-11-27) Before swapping art: work out which Printify mockup (variant + camera) each Shopify photo of the Legends tees /
women's tees is, by comparing against the current (old-art) mockups. Writes WORK/prematch.json."""
import json, sys, io, time, re, concurrent.futures as cf
import requests, numpy as np
from PIL import Image
W = sys.argv[1]
PF = {"born-ready-tee": "6ae779db48500d698e04256f", "fallen-not-finished-tee": "6ae77a0da04ae2f1280aa3cb",
      "going-with-the-flow-tee": "6ae77a715b46121dd6093a8b", "queen-forever-tee": "6aea9404365c19e4ba07e79f",
      "born-ready-womens-tee": "6af37481f6491c921e019173", "fallen-not-finished-womens-tee": "6af37702cb8adff71a0292aa",
      "going-with-the-flow-womens-tee": "6af3771b45f16ba7160339ee", "queen-forever-womens-tee": "6af37772da607b43c50f7859"}
TEE = {"front print": ["102044"], "hanging": ["102047"], "folded": ["102046"], "back": ["102045"],
       "model": ["102057", "102059", "102061", "102054", "102058", "102060", "102062", "102048", "102049", "102050"]}
WOM = {"front print": ["87728"], "hanging": ["87730"], "flat lay": ["87731"], "back": ["87729"], "model": ["87732"]}
s = requests.Session()
H = {"Authorization": "Bearer x"}
def get(url, **kw):
    for k in range(5):
        r = s.get(url, timeout=120, **kw)
        if r.status_code == 200 and r.content: return r
        time.sleep(3 + 4 * k)
    r.raise_for_status(); return r
def thumb(url):
    im = Image.open(io.BytesIO(get(url).content)).convert("RGB").resize((96, 96), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32)
out = {}
for h, pid in PF.items():
    prod = get(f"https://elsewhereapparelco.com/products/{h}.js").json()
    px = get(f"https://api.printify.com/v1/shops/29509655/products/{pid}.json", headers=H).json()
    name = px["images"][0]["src"].split("/mockup/")[1].split("/")[3].split(".jpg")[0]
    vid_by_color = {}
    for v in px["variants"]:
        if v["is_enabled"]:
            c = next(x for x in v["title"].split(" / ") if x not in {"XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"})
            vid_by_color.setdefault(c, v["id"])
    cams = WOM if "womens" in h else TEE
    rows = []
    for m in prod["media"]:
        alt = m["alt"] or ""
        mm = re.match(re.escape(prod["title"]) + r" in (.+?), (.+)$", alt)
        if not mm:
            rows.append({"id": m["id"], "alt": alt, "skip": "no color label"}); continue
        color, kind = mm.group(1), mm.group(2)
        key = "model" if "model" in kind else next((k for k in cams if kind.startswith(k)), None)
        if key is None or color not in vid_by_color:
            rows.append({"id": m["id"], "alt": alt, "skip": f"unknown kind/color {kind}/{color}"}); continue
        vid = vid_by_color[color]
        cands = [f"https://images.printify.com/mockup/{pid}/{vid}/{c}/{name}.jpg" for c in cams[key]]
        with cf.ThreadPoolExecutor(6) as ex:
            T = list(ex.map(lambda u: thumb(u + "?s=256"), cands))
        mine = thumb(m["src"].split("?")[0] + "?width=256")
        d = [float(np.abs(mine - t).mean()) for t in T]
        j = int(np.argmin(d))
        rows.append({"id": m["id"], "alt": alt, "color": color, "vid": vid, "cam": cams[key][j],
                     "d": round(d[j], 2), "next": round(sorted(d)[1], 2) if len(d) > 1 else None,
                     "url": cands[j]})
    out[h] = {"pid": pid, "title": prod["title"], "rows": rows}
    print(h, [(r.get("cam"), r.get("d"), r.get("next")) if "cam" in r else r["skip"] for r in rows], flush=True)
json.dump(out, open(f"{W}/prematch.json", "w"), indent=1)
