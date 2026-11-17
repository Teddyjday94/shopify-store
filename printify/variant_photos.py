"""Give every variant the photo of its own color (2026-11-17), so checkout, order emails and the cart show the
color the shopper picked. For each color, the variant gets the first photo labeled "<Title> in <Color>, ..."
(in gallery order), so the main color keeps its current main photo. Variants that already have a photo (Printify's,
for the original colors) are left alone. Reads the public storefront JSON (/products/<handle>.js), writes batched
productVariantsBulkUpdate mutations.

Usage: python3 printify/variant_photos.py OUT_DIR
"""
import json, re, sys, time
from pathlib import Path
import requests

STORE = "https://elsewhereapparelco.com"
LABEL = re.compile(r"^.* in ([^,]+), (.+)$", re.I)


def get(url):
    for wait in (0, 3, 10, 30):
        time.sleep(wait)
        r = requests.get(url, timeout=60)
        if r.ok and r.text.lstrip().startswith("{"):
            return r.json()
    raise RuntimeError(url)


def main():
    out = Path(sys.argv[1])
    handles, page = [], 1
    while True:
        data = get(f"{STORE}/products.json?limit=250&page={page}")["products"]
        handles += [p["handle"] for p in data]
        if len(data) < 250:
            break
        page += 1
    parts, stats = [], {"products": 0, "variants": 0}
    for h in handles:
        p = get(f"{STORE}/products/{h}.js")
        names = [o["name"] if isinstance(o, dict) else o for o in p["options"]]
        ci = next((i for i, n in enumerate(names) if re.search(r"colou?r", n, re.I)), None)
        if ci is None:
            continue
        first = {}
        for m in p.get("media", []):
            lab = LABEL.match(m.get("alt") or "")
            if m.get("media_type") == "image" and lab:
                first.setdefault(lab.group(1).lower(), m["id"])
        updates = []
        for v in p["variants"]:
            color = (v["options"][ci] or "").lower()
            want = first.get(color)
            if not want:
                continue
            have = (v.get("featured_media") or {}).get("id")
            have_alt = (v.get("featured_media") or {}).get("alt") or ""
            lab = LABEL.match(have_alt)
            # Only variants with no photo: the colors added later and the new crewnecks. Printify already gave
            # the original colors a photo of the right color (unlabeled), so those are left as they are.
            if have:
                continue
            updates.append(f'{{id:"gid://shopify/ProductVariant/{v["id"]}",mediaId:"gid://shopify/MediaImage/{want}"}}')
        if updates:
            stats["products"] += 1
            stats["variants"] += len(updates)
            parts.append(f'p{p["id"]}: productVariantsBulkUpdate(productId:"gid://shopify/Product/{p["id"]}", variants:[{",".join(updates)}]){{ userErrors{{field message}} }}')
    batch, size, n = [], 0, 0
    for part in parts:
        if batch and size + len(part) > 30000:
            (out / f"vm_{n}.graphql").write_text("mutation { " + " ".join(batch) + " }"); n += 1; batch, size = [], 0
        batch.append(part); size += len(part)
    if batch:
        (out / f"vm_{n}.graphql").write_text("mutation { " + " ".join(batch) + " }"); n += 1
    print(len(handles), "products scanned;", stats, ";", n, "batches")


if __name__ == "__main__":
    main()
