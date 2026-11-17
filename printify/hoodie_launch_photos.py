"""Refresh the older hoodies' launch photos (unlabeled, or labeled only with a description) after the back
prints were enlarged (2026-11-17).

Shopify keeps a copy of each photo, so these still showed the old print size. For each such photo, find the
Printify mockup it was made from (same garment color and camera) by comparing small thumbnails against the
product's current Printify mockups, then swap the file in place with fileUpdate (same media id, position and alt).

Usage: python3 printify/hoodie_launch_photos.py OUT_DIR   (writes OUT_DIR/lp_N.graphql and OUT_DIR/lp_matches.json)
"""
import io, json, re, sys, time
from pathlib import Path
import numpy as np, requests
from PIL import Image
from create_products import Printify

SHOP = 29509655
STORE = "https://elsewhereapparelco.com"
LABELED = re.compile(r"^.* in ([^,]+), (back print|front view|front print|sleeve print|on a model.*|hanging.*)$", re.I)


def thumb(url):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    im = Image.open(io.BytesIO(r.content)).convert("RGB").resize((48, 48), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32) / 255.0


def store_media(handle):
    for wait in (0, 5, 20, 60):
        time.sleep(wait)
        r = requests.get(f"{STORE}/products/{handle}.js", timeout=60)
        if r.status_code == 404:  # Printify keeps the handle it published with; Shopify's may have lost a "-1"
            handle = re.sub(r"-\d+$", "", handle)
            r = requests.get(f"{STORE}/products/{handle}.js", timeout=60)
        if r.ok and r.text.startswith("{"):
            return r.json()["media"]
    raise RuntimeError(f"no media for {handle}: {r.status_code}")


def main():
    out = Path(sys.argv[1])
    api = Printify(None)
    hb = json.loads(Path(__file__).with_name("hoodie_backs.json").read_text())
    parts, report = [], []
    for title, v in hb.items():
        x = api.get(f"/shops/{SHOP}/products/{v['printify']}.json")
        handle = x["external"]["handle"].rstrip("/").split("/")[-1]
        media = store_media(handle)
        targets = [m for m in media if m.get("media_type") == "image" and not LABELED.match(m.get("alt") or "")]
        if not targets:
            continue
        cands = [im["src"].split("?")[0] + "?s=2048&v=big" for im in x["images"]]
        cthumbs = [thumb(c.replace("s=2048", "s=400")) for c in cands]
        for m in targets:
            t = thumb(m["src"] + ("&" if "?" in m["src"] else "?") + "width=400")
            d = [float(np.abs(t - c).mean()) for c in cthumbs]
            i = int(np.argmin(d))
            second = sorted(d)[1] if len(d) > 1 else 1
            report.append(dict(title=title, media=m["id"], alt=m.get("alt"), match=cands[i], dist=round(d[i], 4), second=round(second, 4)))
            parts.append(f'{{id:"gid://shopify/MediaImage/{m["id"]}",originalSource:"{cands[i]}"}}')
        print(title, len(targets), "photos", flush=True)
    (out / "lp_matches.json").write_text(json.dumps(report, indent=1))
    for i in range(0, len(parts), 40):
        (out / f"lp_{i // 40}.graphql").write_text(
            "mutation { fileUpdate(files:[" + ",".join(parts[i:i + 40]) + "]){ files{id fileStatus} userErrors{field message} } }")
    print("total", len(parts))


if __name__ == "__main__":
    main()
