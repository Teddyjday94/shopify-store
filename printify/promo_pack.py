"""Download a promo pack: Printify's lifestyle and model mockups for every design, full size.

Writes media/promo/<design>/<NN>-<shot>.jpg (2048 px) plus media/promo/README.md.
Tees: model shots (front or back, whichever side carries the print), chair and folded close-up.
Women's tees: lifestyle model shot and styled flat lay (front-printed designs only).
Hoodies: the back print and its alternate angle; front-print hoodies: the front and four model shots.
Usage: python3 printify/promo_pack.py
"""
import json, re, sys, concurrent.futures as cf
from pathlib import Path
import requests
from create_products import Printify

SHOP = 29509655
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "media" / "promo"
TEE_FRONT = [(102052, "two-models"), (102053, "two-models-2"), (102057, "model-woman"), (102059, "model-man"),
             (102061, "model-woman-2"), (102049, "on-chair"), (102046, "folded-closeup")]
TEE_BACK = [(102060, "model-man-back"), (102058, "model-woman-back"), (102054, "model-man-back-2"), (102062, "model-woman-back-2"), (102045, "flat-back")]
WOMENS = [(87732, "womens-lifestyle"), (87731, "womens-flatlay")]
HOODIE = [(98425, "hoodie-back"), (98426, "hoodie-back-2")]
HOODIE_FRONT = [(98424, "hoodie-front"), (98427, "hoodie-model-woman"), (98428, "hoodie-model-man"),
                (98429, "hoodie-model-woman-2"), (98430, "hoodie-model-man-2")]


def design_of(title):
    return re.sub(r"\s+(Front Print Hoodie|Sleeve Edition Hoodie|Long Sleeve Tee|Women's Tee|Hoodie|Tee|T-Shirt)$", "", title).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("&", "and")).strip("-")


def main():
    api = Printify(None)
    jobs, page = [], 1
    while True:
        r = api.get(f"/shops/{SHOP}/products.json?limit=50&page={page}")
        for x in r["data"]:
            bp = x["blueprint_id"]
            if bp not in (12, 466, 77) or not (x.get("external") or {}).get("id"):
                continue
            ims = [im for im in x["images"] if "/mockup/" in im["src"]]
            if not ims:
                continue
            d = next((im for im in ims if im.get("is_default")), ims[0])
            mock, variant, _, name = d["src"].split("/mockup/")[1].split("/")[:4]
            name = name.split(".jpg")[0]
            sides = {ph["position"] for pa in x["print_areas"] for ph in pa["placeholders"] if ph["images"]}
            if bp == 12:
                cams = TEE_FRONT if "front" in sides else TEE_BACK
            elif bp == 466:
                cams = WOMENS if "front" in sides else []
            else:
                cams = HOODIE if "back" in sides else HOODIE_FRONT if "front" in sides else []
            if "Sleeve Edition" in x["title"]:
                cams = [(98425, "sleeve-edition-back")]
            for cam, shot in cams:
                # v= busts Printify's image cache, so a product edited since the last run (e.g. a resized print) renders fresh
                v = re.sub(r"\D", "", x.get("updated_at") or "")
                jobs.append((design_of(x["title"]), shot, f"https://images.printify.com/mockup/{mock}/{variant}/{cam}/{name}.jpg?s=2048&v={v}"))
        if not r.get("next_page_url") or not r["data"]:
            break
        page += 1

    def fetch(job):
        design, shot, url = job
        r = requests.get(url, timeout=120)
        if not r.ok or len(r.content) < 60000:
            return design, shot, None
        dest = OUT / slug(design)
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / f"{shot}.jpg"
        path.write_bytes(r.content)
        return design, shot, path

    done = {}
    with cf.ThreadPoolExecutor(10) as ex:
        for design, shot, path in ex.map(fetch, jobs):
            done.setdefault(design, []).append(shot if path else f"{shot} (missing)")
    lines = ["# Promo pack", "", "Printify lifestyle and model mockups for every design, 2048 px, ready for social posts and ads.",
             "Regenerate with `python3 printify/promo_pack.py`.", ""]
    for design in sorted(done):
        lines.append(f"- **{design}** (`{slug(design)}/`): {', '.join(sorted(done[design]))}")
    (OUT / "README.md").write_text("\n".join(lines) + "\n")
    print(len(jobs), "shots,", len(done), "designs,", sum(s.endswith("(missing)") for v in done.values() for s in v), "missing")


if __name__ == "__main__":
    sys.exit(main())
