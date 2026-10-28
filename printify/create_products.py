"""Create the Elsewhere Supply Co. launch products in Printify and publish them to Shopify.

Titles, prices, descriptions and tags come from launch-listings.md; print files come from
designs/print/. Blanks, colors and print placement are configured in PRODUCTS below.

Usage:
    PRINTIFY_API_TOKEN=... python3 printify/create_products.py            # dry run: look up and print the plan
    PRINTIFY_API_TOKEN=... python3 printify/create_products.py --apply    # create + publish

Products whose title already exists in the Printify shop are skipped, so re-running is safe.
"""

import argparse
import base64
import html
import os
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
LISTINGS = ROOT / "launch-listings.md"
PRINT_DIR = ROOT / "designs" / "print"
API = "https://api.printify.com/v1"

TEE_SIZES = ["S", "M", "L", "XL", "2XL"]
XXL_UPCHARGE = 300  # cents added to 2XL variants

# Preferred US print providers, best first. Falls back to any provider with the colors.
PREFERRED_PROVIDERS = ["Monster Digital", "SwiftPOD", "Printify Choice", "Print Geek", "District Photo", "Fulfill Engine"]

# Placement: x/y are the artwork's center as a fraction of the print area, scale is
# artwork width as a fraction of the print-area width.
LEFT_CHEST = dict(x=0.70, y=0.24, scale=0.27)
FULL_FRONT = dict(x=0.5, y=0.38, scale=0.80)
FULL_BACK = dict(x=0.5, y=0.42, scale=0.85)

# key = listing number in launch-listings.md. colors map shirt color -> ink file suffix.
PRODUCTS = {
    1: dict(model="18500", sizes=TEE_SIZES,
            colors={"Black": "white", "Sand": "black", "Military Green": "white", "Light Pink": "black"},
            prints={"front": ("01-currently-elsewhere-chest-{ink}.png", LEFT_CHEST)}),
    2: dict(model="3001", sizes=TEE_SIZES,
            colors={"White": "black", "Natural": "black", "Tan": "black", "Heather Dust": "black"},
            prints={"front": ("02-ships-6-7-business-days-black.png", FULL_FRONT)}),
    3: dict(model="3001", sizes=TEE_SIZES,
            colors={"Black": "white", "Athletic Heather": "black", "White": "black", "Heather Navy": "white"},
            prints={"front": ("03-not-ai-just-tired-{ink}.png", FULL_FRONT)}),
    4: dict(model="1717", sizes=TEE_SIZES,
            colors={"Ivory": "black", "Pepper": "white", "Blue Jean": "white", "Butter": "black"},
            prints={"front": ("04-odysseus-layover-{ink}.png", FULL_FRONT)}),
    5: dict(model="18500", sizes=TEE_SIZES,
            colors={"Black": "white", "Dark Heather": "white", "Maroon": "white", "Forest Green": "white"},
            prints={"front": ("05-seasonal-depression-chest-white.png", LEFT_CHEST),
                    "back": ("05-seasonal-depression-tour-back-white.png", FULL_BACK)}),
    6: dict(title_match="beanie", sizes=None,
            colors={"Black": "white", "Heather Grey": "black", "Forest Green": "white", "Mustard": "black"},
            prints={"front": ("06-do-not-perceive-me-beanie-{ink}.png", dict(x=0.5, y=0.5, scale=0.9))}),
}


class Printify:
    def __init__(self, token):
        self.s = requests.Session()
        self.s.headers.update({"Authorization": f"Bearer {token}", "User-Agent": "elsewhere-supply-setup"})

    def call(self, method, path, **kw):
        for attempt in range(4):
            r = self.s.request(method, f"{API}{path}", timeout=60, **kw)
            if r.status_code == 429:
                time.sleep(2 ** attempt * 5)
                continue
            if not r.ok:
                raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:500]}")
            return r.json()
        raise RuntimeError(f"{method} {path} rate-limited")

    def get(self, path):
        return self.call("GET", path)

    def post(self, path, body):
        return self.call("POST", path, json=body)


def parse_listings():
    """Return {n: {title, price_cents, description_html, tags}} from launch-listings.md."""
    text = LISTINGS.read_text()
    out = {}
    for m in re.finditer(r"^## (\d+)\. .*?(?=^## |\Z)", text, re.M | re.S):
        n, block = int(m.group(1)), m.group(0)
        if n not in PRODUCTS:
            continue
        title = re.search(r"^\*\*Title:\*\* (.+)$", block, re.M).group(1).strip()
        price = re.search(r"^\*\*Price:\*\* \$(\d+)", block, re.M).group(1)
        tags = re.findall(r"`([^`]+)`", re.search(r"^\*\*Tags:\*\* (.+)$", block, re.M).group(1))
        quoted = [l[1:].strip() for l in block.splitlines() if l.startswith(">")]
        out[n] = dict(title=title, price_cents=int(price) * 100, tags=tags, description_html=quote_to_html(quoted))
    missing = set(PRODUCTS) - set(out)
    if missing:
        sys.exit(f"launch-listings.md is missing listings {sorted(missing)}")
    return out


def quote_to_html(lines):
    def inline(s):
        s = html.escape(s)
        return re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)

    parts, para, bullets = [], [], []
    for line in lines + [""]:
        if line.startswith("- "):
            bullets.append(f"<li>{inline(line[2:])}</li>")
            continue
        if bullets:
            parts.append("<ul>" + "".join(bullets) + "</ul>")
            bullets = []
        if line:
            para.append(inline(line))
        elif para:
            parts.append("<p>" + " ".join(para) + "</p>")
            para = []
    return "".join(parts)


def find_blueprint(api, spec, blueprints):
    if "model" in spec:
        hits = [b for b in blueprints if spec["model"] in (b.get("model") or "")]
    else:
        hits = [b for b in blueprints if spec["title_match"] in b["title"].lower()]
        # Prefer embroidered cuffed beanies.
        hits.sort(key=lambda b: ("embroid" not in b["title"].lower(), "cuff" not in b["title"].lower()))
    if not hits:
        raise RuntimeError(f"no blueprint for {spec.get('model') or spec.get('title_match')}")
    return hits[0]


def pick_provider(api, blueprint, spec):
    providers = api.get(f"/catalog/blueprints/{blueprint['id']}/print_providers.json")
    rank = {name: i for i, name in enumerate(PREFERRED_PROVIDERS)}
    providers.sort(key=lambda p: rank.get(p["title"], len(rank)))
    best = None
    for p in providers:
        variants = api.get(f"/catalog/blueprints/{blueprint['id']}/print_providers/{p['id']}/variants.json")["variants"]
        colors = {v["options"].get("color", "").lower() for v in variants}
        have = [c for c in spec["colors"] if c.lower() in colors]
        if best is None or len(have) > len(best[2]):
            best = (p, variants, have)
        if len(have) == len(spec["colors"]):
            break
    if not best or not best[2]:
        raise RuntimeError(f"no provider for blueprint {blueprint['title']} has any of {list(spec['colors'])}")
    return best


def plan_product(api, n, listing, spec, blueprints):
    bp = find_blueprint(api, spec, blueprints)
    provider, variants, colors = pick_provider(api, bp, spec)
    chosen = []
    for v in variants:
        color = v["options"].get("color", "")
        size = v["options"].get("size", "")
        match = next((c for c in colors if c.lower() == color.lower()), None)
        if not match or (spec["sizes"] and size not in spec["sizes"]):
            continue
        price = listing["price_cents"] + (XXL_UPCHARGE if size == "2XL" else 0)
        chosen.append(dict(id=v["id"], color=match, size=size, price=price,
                           positions={p["position"] for p in v.get("placeholders", [])}))
    if not chosen:
        raise RuntimeError(f"listing {n}: no variants matched")
    skipped = [c for c in spec["colors"] if c not in colors]
    return dict(n=n, listing=listing, spec=spec, blueprint=bp, provider=provider, variants=chosen, skipped_colors=skipped)


def upload(api, filename, cache):
    if filename not in cache:
        data = base64.b64encode((PRINT_DIR / filename).read_bytes()).decode()
        cache[filename] = api.post("/uploads/images.json", {"file_name": filename, "contents": data})["id"]
    return cache[filename]


def build_print_areas(api, plan, cache):
    areas = []
    for ink in sorted({plan["spec"]["colors"][v["color"]] for v in plan["variants"]}):
        ids = [v["id"] for v in plan["variants"] if plan["spec"]["colors"][v["color"]] == ink]
        positions = set.intersection(*(v["positions"] for v in plan["variants"] if v["id"] in ids))
        placeholders = []
        for position, (pattern, place) in plan["spec"]["prints"].items():
            if position not in positions:
                # e.g. embroidery blueprints name their area differently; use the only one there is.
                if len(positions) == 1 and len(plan["spec"]["prints"]) == 1:
                    position = next(iter(positions))
                else:
                    raise RuntimeError(f"{plan['listing']['title']}: no '{position}' print area (has {sorted(positions)})")
            image_id = upload(api, pattern.format(ink=ink), cache)
            placeholders.append({"position": position, "images": [dict(id=image_id, angle=0, **place)]})
        areas.append({"variant_ids": ids, "placeholders": placeholders})
    return areas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="create and publish (default is a dry run)")
    args = ap.parse_args()

    token = os.environ.get("PRINTIFY_API_TOKEN")
    if not token:
        sys.exit("Set PRINTIFY_API_TOKEN in the environment.")
    api = Printify(token)
    listings = parse_listings()

    shops = api.get("/shops.json")
    shopify = [s for s in shops if s.get("sales_channel") == "shopify"]
    if len(shopify) != 1:
        sys.exit(f"Expected exactly one Shopify-connected Printify shop, found: {[s['title'] for s in shops]}")
    shop = shopify[0]
    print(f"Shop: {shop['title']} (id {shop['id']})")

    existing = {p["title"] for p in api.get(f"/shops/{shop['id']}/products.json?limit=50")["data"]}
    blueprints = api.get("/catalog/blueprints.json")

    plans = []
    for n in sorted(PRODUCTS):
        listing = listings[n]
        if listing["title"] in existing:
            print(f"- {listing['title']}: already exists, skipping")
            continue
        plan = plan_product(api, n, listing, PRODUCTS[n], blueprints)
        plans.append(plan)
        colors = sorted({v["color"] for v in plan["variants"]})
        print(f"- {listing['title']}: {plan['blueprint']['title']} ({plan['blueprint'].get('brand')} "
              f"{plan['blueprint'].get('model')}) via {plan['provider']['title']}; "
              f"{len(plan['variants'])} variants, colors {colors}, ${listing['price_cents'] / 100:.0f}")
        if plan["skipped_colors"]:
            print(f"    colors not offered by this provider, left out: {plan['skipped_colors']}")

    if not args.apply:
        print("\nDry run only. Re-run with --apply to create and publish.")
        return

    cache = {}
    for plan in plans:
        listing = plan["listing"]
        body = {
            "title": listing["title"],
            "description": listing["description_html"],
            "tags": listing["tags"],
            "blueprint_id": plan["blueprint"]["id"],
            "print_provider_id": plan["provider"]["id"],
            "variants": [{"id": v["id"], "price": v["price"], "is_enabled": True} for v in plan["variants"]],
            "print_areas": build_print_areas(api, plan, cache),
        }
        product = api.post(f"/shops/{shop['id']}/products.json", body)
        enabled = [v for v in product["variants"] if v.get("is_enabled")]
        margins = [(v["price"] - v["cost"]) / 100 for v in enabled if v.get("cost")]
        margin = f", profit before shipping ${min(margins):.2f}-${max(margins):.2f}" if margins else ""
        print(f"created {listing['title']} (id {product['id']}){margin}")
        api.post(f"/shops/{shop['id']}/products/{product['id']}/publish.json", {
            "title": True, "description": True, "images": True, "variants": True,
            "tags": True, "keyFeatures": True, "shipping_template": True,
        })
        print("  published to Shopify")


if __name__ == "__main__":
    main()
