"""Rebuild the Drop 002 hoodies on the Gildan 18500 at $45, replacing the pocketless Comfort Colors versions.

Creates new products alongside the old ones; the old Shopify listings are deleted afterwards and the
new ones take over their handles and SEO.

Usage:
    python3 printify/create_drop2_gildan.py            # dry run
    python3 printify/create_drop2_gildan.py --apply    # create + publish
"""

import argparse

from create_hoodies import PRODUCTS, run

DROP2 = [dict(spec, price=4500) for spec in PRODUCTS if "drop 002" in spec["tags"]]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    run(DROP2, "18500", ap.parse_args().apply, replace=True)
