"""Delete the old Monster Digital hoodie from Printify once its SwiftPOD replacement has taken over the listing.

Usage: python3 printify/swap_cleanup.py "<title>" ["<title>" ...]
"""
import json
import os
import sys
from pathlib import Path

from create_products import Printify

OUT = Path(__file__).with_name("moved_hoodies.json")


def main():
    titles = set(sys.argv[1:])
    api = Printify(os.environ.get("PRINTIFY_API_TOKEN"))
    shop = next(s for s in api.get("/shops.json") if s.get("sales_channel") == "shopify")["id"]
    moved = json.loads(OUT.read_text())
    for old, m in moved.items():
        if m["title"] in titles and not m.get("swapped"):
            p = api.get(f"/shops/{shop}/products/{old}.json")
            assert p["print_provider_id"] == 29 and p["title"] == m["title"]
            api.call("DELETE", f"/shops/{shop}/products/{old}.json")
            m["swapped"] = True
            print("deleted old", m["title"])
    OUT.write_text(json.dumps(moved, indent=2))


if __name__ == "__main__":
    main()
