"""Brand collection: front-print versions of the five logo hoodies (Gildan 18500, Black, $37).

The original Brand hoodies print the logo on the back; these print it across the chest, so Printify's
hoodie model mockups (front views) show the design. Same art and settings as create_brand.py.

Usage: python3 printify/create_brand_front.py --commit SHA [--only SLUG]
"""
import create_brand as brand

brand.MARGIN = 0.85
brand.KINDS = [
    dict(key="hoodie-front", title="{n} Front Print Hoodie", bp=77, pp=39, price=3700, pos="front", tags=["hoodie", "front print"],
         images=False, bullets=["Full-color front print across the chest", "Medium-heavy cotton/poly blend, fleece-lined",
                                "Unisex fit, size up for oversized"]),
]

if __name__ == "__main__":
    brand.main()
