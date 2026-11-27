"""Put the new Legends Never Die art (the "natural border" files the owner uploaded for the hoodie backs on 2026-11-27)
on the Legends tees and women's tees, keeping each product's printed height and position, then republish to Shopify
WITHOUT images (Shopify photos keep their ids, labels, order and variant links; their pictures are swapped afterwards
with fileUpdate originalSource from the regenerated Printify mockups, see --media).

Crewnecks (--crew HANDLE) carry a neck-label text layer. Printify rejects it when sent back ("Provided images do not
exist", 2026-11-27), so the owner chose to drop the neck label: --crew removes it. Re-add it in the Printify editor if wanted.

Usage:
    python3 printify/legends_natural_border_swap.py              # dry run
    python3 printify/legends_natural_border_swap.py --apply
    python3 printify/legends_natural_border_swap.py --media PREMATCH_JSON OUT_JSON   # after mockups regenerate
"""
import argparse
import json
import time
from pathlib import Path

from create_products import Printify

SHOP = 29509655
# design -> the hoodie that already carries the new art (its "back" image is reused, no new upload)
HOODIES = {"born-ready": "6ae779f2f9c00c9ec009d8e0", "fallen-not-finished": "6ae77a2517932a00ba02a3f6",
           "going-with-the-flow": "6ae77a88d037ed7f1f02b9d9", "queen-forever": "6aea941b365c19e4ba07e801"}
TARGETS = {"born-ready-tee": "6ae779db48500d698e04256f", "fallen-not-finished-tee": "6ae77a0da04ae2f1280aa3cb",
           "going-with-the-flow-tee": "6ae77a715b46121dd6093a8b", "queen-forever-tee": "6aea9404365c19e4ba07e79f",
           "born-ready-womens-tee": "6af37481f6491c921e019173", "fallen-not-finished-womens-tee": "6af37702cb8adff71a0292aa",
           "going-with-the-flow-womens-tee": "6af3771b45f16ba7160339ee", "queen-forever-womens-tee": "6af37772da607b43c50f7859"}
CREW = {"born-ready-crewneck": "6afc013d17c004fdc80482d9", "fallen-not-finished-crewneck": "6afc028cfd4d7f230d0ab614",
        "going-with-the-flow-crewneck": "6afc0280fd4d7f230d0ab606", "queen-forever-crewneck": "6afc0273fd4d7f230d0ab5f8"}
DONE = Path(__file__).with_name("legends_natural_border_done.json")


def new_art(api):
    art = {}
    for design, pid in HOODIES.items():
        p = api.get(f"/shops/{SHOP}/products/{pid}.json")
        img = next(i for a in p["print_areas"] for ph in a["placeholders"] if ph["position"] == "back" for i in ph["images"])
        assert "natural-border" in img["name"], img["name"]
        art[design] = img
    return art


def swap(api, apply, targets=TARGETS, allow_text=False):
    art = new_art(api)
    done = json.loads(DONE.read_text()) if DONE.exists() else []
    for handle, pid in targets.items():
        if pid in done:
            print("done  ", handle); continue
        design = next(d for d in HOODIES if handle.startswith(d))
        new = art[design]
        p = api.get(f"/shops/{SHOP}/products/{pid}.json")
        areas, changed = [], 0
        for a in p["print_areas"]:
            phs = []
            for ph in a["placeholders"]:
                imgs = []
                for i in ph["images"]:
                    if i.get("type") == "text/plain" or i["name"].endswith(".svg"):
                        if not allow_text:
                            raise SystemExit(f"{p['title']} has a text layer ({ph['position']}); not safe to PUT")
                        print(f"   dropping text layer on {ph['position']}")
                        continue
                    place = dict(x=i["x"], y=i["y"], scale=i["scale"], angle=i.get("angle", 0))
                    if ph["position"] == "front" and i["name"].endswith("-back.png"):
                        # same printed height: scale is relative to width, so adjust for the new aspect ratio
                        place["scale"] = round(i["scale"] * (i["height"] / i["width"]) / (new["height"] / new["width"]), 4)
                        if not changed:
                            print(f"{'apply ' if apply else 'plan  '}{p['title']}: {i['name']} scale {i['scale']} -> "
                                  f"{new['name']} scale {place['scale']} at x={i['x']} y={i['y']}")
                        changed += 1
                        imgs.append(dict(id=new["id"], **place))
                    else:
                        imgs.append(dict(id=i["id"], **place))
                if imgs:
                    phs.append({"position": ph["position"], "images": imgs})
            areas.append({"variant_ids": a["variant_ids"], "placeholders": phs})
        if not changed:
            raise SystemExit(f"{p['title']}: old art not found")
        if not apply:
            continue
        api.call("PUT", f"/shops/{SHOP}/products/{pid}.json", json={"print_areas": areas})
        for wait in (5, 60, 180, 400):
            time.sleep(wait)
            try:
                api.post(f"/shops/{SHOP}/products/{pid}/publish.json", {
                    "title": False, "description": False, "images": False, "variants": False,
                    "tags": False, "keyFeatures": False, "shipping_template": False})
                break
            except Exception as e:
                print("   publish retry:", str(e)[:100], flush=True)
        done.append(pid)
        DONE.write_text(json.dumps(done, indent=1))


def media(prematch_path, out_path):
    """fileUpdate inputs that point every Shopify photo at its regenerated mockup (same variant + camera)."""
    pre = json.loads(Path(prematch_path).read_text())
    out = {}
    for handle, v in pre.items():
        out[handle] = [{"id": f"gid://shopify/MediaImage/{r['id']}", "originalSource": r["url"] + "?s=2048"}
                       for r in v["rows"] if "url" in r]
    Path(out_path).write_text(json.dumps(out, indent=1))
    print({h: len(x) for h, x in out.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--media", nargs=2)
    ap.add_argument("--crew")
    a = ap.parse_args()
    if a.media:
        media(*a.media)
    elif a.crew:
        swap(Printify(None), a.apply, {a.crew: CREW[a.crew]}, allow_text=True)
    else:
        swap(Printify(None), a.apply)
