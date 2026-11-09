"""Build Shopify media mutations: labeled photos for hoodie colors that don't have them yet.
usage: color_media.py PLAN.json EXISTING.json OUTPREFIX
EXISTING.json: {shopify_id: [alt, ...]} as currently in Shopify."""
import json, sys
plan = json.load(open(sys.argv[1])); have = json.load(open(sys.argv[2])); out = sys.argv[3]
parts = []
for sid, d in plan.items():
    if not d["title"].endswith("Hoodie") or sid not in have: continue
    alts = set(have[sid])
    sides = {"back"}   # new colors: the back view, where the design is
    add = [m for m in d["media"] if m["url"] and m["side"] in sides and m["alt"] not in alts]
    if not add: continue
    med = ",".join(f'{{originalSource:"{m["url"]}&s=2048",alt:"{m["alt"]}",mediaContentType:IMAGE}}' for m in add)
    parts.append(f'p{sid}: productUpdate(product:{{id:"gid://shopify/Product/{sid}"}}, media:[{med}]){{ userErrors{{message}} }}')
for i in range(0, len(parts), 10):
    open(f"{out}{i // 10}.graphql", "w").write("mutation { " + " ".join(parts[i:i + 10]) + " }")
print(len(parts), "products,", sum(p.count("originalSource") for p in parts), "photos,", (len(parts) + 9) // 10, "batches")
