"""Brand collection, second batch: two illustrated Elsewhere Apparel Co. pieces.

Each design gets a tee, women's tee, back-print hoodie and front-print hoodie (Black, store prices), using
create_brand.py's product builder. Art: designs/print-brand/<slug>.png (300 DPI, transparent).

Usage: python3 printify/create_brand2.py --commit SHA [--only SLUG]
"""
import create_brand as brand

brand.DESIGNS = [
    ("06-graffiti", "Elsewhere Graffiti", ["graffiti", "skull", "punk", "streetwear"],
     "The Elsewhere Apparel Co. name in dripping graffiti lettering, with a skull in headphones, a busted TV, "
     "a checkered flag, a melting smiley and a beat-up high-top, all in hot pink, teal and gold spray paint.",
     "Tagged, not taken."),
    ("07-dreamscape", "Elsewhere Dreamscape", ["psychedelic", "surreal", "dream", "galaxy"],
     "Neon drip lettering over a dreamscape: a vintage TV swallowing a galaxy, a melting staircase into the clouds "
     "and a cracked stone face asleep in the sky.", "Wake up somewhere else."),
]
brand.KINDS = [k for k in brand.KINDS if k["key"] in ("tee", "womens", "hoodie")] + [
    dict(key="hoodie-front", title="{n} Front Print Hoodie", bp=77, pp=39, price=3700, pos="front", tags=["hoodie", "front print"],
         images=False, bullets=["Full-color front print across the chest", "Medium-heavy cotton/poly blend, fleece-lined",
                                "Unisex fit, size up for oversized"]),
]

if __name__ == "__main__":
    brand.main()
