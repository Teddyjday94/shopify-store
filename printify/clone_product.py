"""Clone a Printify product onto another blank or print provider, keeping its artwork and placement.

Used to move hoodies to a provider that stocks Dark Chocolate (brown), and to make women's-fit
versions of the tees. Colors are given as {target color: ink}, where ink names the source print area
to copy ("white"/"black" for products printed in two text colors, None for single-area products).
Placements keep each print's physical size and top edge, shrinking only if it would overflow the
new print area.
"""

from functools import lru_cache

from create_products import XXL_UPCHARGE
from fit import placeholder_sizes as _placeholder_sizes

SIZES = ["XS", "S", "M", "L", "XL", "2XL"]


@lru_cache(maxsize=None)
def placeholder_sizes(api, blueprint_id, provider_id):
    return _placeholder_sizes(api, blueprint_id, provider_id)


@lru_cache(maxsize=None)
def catalog_variants(api, blueprint_id, provider_id):
    return api.get(f"/catalog/blueprints/{blueprint_id}/print_providers/{provider_id}/variants.json")["variants"]


def source_area(src, ink):
    if len(src["print_areas"]) == 1 or ink is None:
        return src["print_areas"][0]
    names = lambda a: " ".join(i["name"] for ph in a["placeholders"] for i in ph["images"])
    return next(a for a in src["print_areas"] if f"-{ink}" in names(a))


def ink_of(src, variant_id):
    """Which ink a source variant prints with: 'white', 'black' or None for single-area products."""
    if len(src["print_areas"]) == 1:
        return None
    names = lambda a: " ".join(i["name"] for ph in a["placeholders"] for i in ph["images"])
    area = next(a for a in src["print_areas"] if variant_id in a["variant_ids"])
    return "white" if "-white" in names(area) else "black"


def refit(img, old, new, limit=0.97):
    """Re-place an image from an old print area size to a new one, keeping physical size and top edge."""
    (ow, oh), (nw, nh) = old, new
    ratio = img["height"] / img["width"]
    width_px = img["scale"] * ow
    top_px = (img["y"] - img["scale"] * ratio * ow / oh / 2) * oh
    scale = min(width_px / nw, limit, limit * nh / (ratio * nw))
    height_frac = scale * ratio * nw / nh
    top = min(max(top_px / nh, 0.0), 1 - height_frac)
    return dict(id=img["id"], angle=img.get("angle", 0), x=img["x"], y=round(top + height_frac / 2, 4),
                scale=round(scale, 4))


def build(api, src, blueprint_id, provider_id, colors, base_price, price_of=None, sizes=SIZES):
    """Return the create-product body for a clone of src. price_of(color, size) may return a price."""
    old_sizes = placeholder_sizes(api, src["blueprint_id"], src["print_provider_id"])
    new_sizes = placeholder_sizes(api, blueprint_id, provider_id)
    catalog = catalog_variants(api, blueprint_id, provider_id)
    by_ink = {}
    variants = []
    for v in catalog:
        color, size = v["options"].get("color"), v["options"].get("size")
        if color not in colors or size not in sizes:
            continue
        price = (price_of and price_of(color, size)) or base_price + (XXL_UPCHARGE if size == "2XL" else 0)
        variants.append({"id": v["id"], "price": price, "is_enabled": True})
        by_ink.setdefault(colors[color], []).append(v["id"])
    areas = []
    for ink, ids in by_ink.items():
        area = source_area(src, ink)
        placeholders = [{"position": ph["position"],
                         "images": [refit(i, old_sizes[ph["position"]], new_sizes[ph["position"]]) for i in ph["images"]]}
                        for ph in area["placeholders"] if ph["images"] and ph["position"] in new_sizes]
        areas.append({"variant_ids": ids, "placeholders": placeholders})
    missing = sorted(set(colors) - {v["options"].get("color") for v in catalog})
    return {"blueprint_id": blueprint_id, "print_provider_id": provider_id,
            "variants": variants, "print_areas": areas}, missing
