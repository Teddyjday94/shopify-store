"""Build the Shopify mutation that adds labeled Printify photos to new products and publishes them to Shop.

Reads a progress file written by create_brand.py-style scripts (printify/<name>.json, entries with
"printify", "kind", "title"), records each product's Shopify id in it, checks every photo URL, and writes
one GraphQL mutation to OUT for the Shopify Admin API. Model shots come first so cards show a person.

Usage: python3 printify/photo_mutations.py PROGRESS.json OUT.graphql [KEY_PREFIX ...]
(only entries whose key starts with one of the prefixes, e.g. the new designs' slugs)
"""
import json, sys
import requests
from create_products import Printify

SHOP = 29509655
SHOP_APP = "gid://shopify/Publication/210420138145"
CAMS = {
    "tee": [(102059, "on a model"), (102044, "front print"), (102057, "on a model, second view"), (102047, "hanging")],
    "womens": [(87732, "on a model"), (87728, "front print"), (87730, "hanging")],
    "hoodie": [(98425, "back print"), (98424, "front view")],
    "hoodie-front": [(98428, "on a model"), (98424, "front print"), (98427, "on a model, second view"),
                     (98429, "on a model, third view"), (98430, "on a model, fourth view")],
}


def main(progress, out, *prefixes):
    data = json.load(open(progress))
    api = Printify(None)
    parts = []
    for key, v in data.items():
        if prefixes and not key.startswith(prefixes):
            continue
        x = api.get(f"/shops/{SHOP}/products/{v['printify']}.json")
        sid = (x.get("external") or {}).get("id")
        if not sid:
            print("not on Shopify yet:", v["title"])
            continue
        v["shopify"] = sid
        src = next(im["src"] for im in x["images"] if "/mockup/" in im["src"])
        mock, variant, _, name = src.split("/mockup/")[1].split("/")[:4]
        name = name.split(".jpg")[0]
        media = []
        for cam, desc in CAMS[v["kind"]]:
            url = f"https://images.printify.com/mockup/{mock}/{variant}/{cam}/{name}.jpg?s=2048"
            r = requests.get(url, timeout=120)  # also warms Printify's cache so Shopify's fetch succeeds
            if not r.ok or len(r.content) < 60000:
                print("missing photo:", v["title"], cam)
                continue
            media.append(f'{{originalSource:"{url}",alt:{json.dumps(v["title"] + " in Black, " + desc)},mediaContentType:IMAGE}}')
        parts.append(f'm{sid}: productUpdate(product:{{id:"gid://shopify/Product/{sid}"}}, media:[{",".join(media)}]){{ userErrors{{message}} }} '
                     f's{sid}: publishablePublish(id:"gid://shopify/Product/{sid}", input:[{{publicationId:"{SHOP_APP}"}}]){{ userErrors{{message}} }}')
        print(v["title"], sid, len(media), "photos")
    json.dump(data, open(progress, "w"), indent=2)
    open(out, "w").write("mutation { " + " ".join(parts) + " }")


if __name__ == "__main__":
    main(*sys.argv[1:])
