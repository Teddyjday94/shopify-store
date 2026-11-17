"""Apply printify/color_plan.json (2026-11-17): enable the planned colours in the sizes each product already sells,
at the same price per size, on the same print areas, then publish ONLY variants to Shopify (titles, descriptions
and photos on Shopify stay as they are). Progress in color_plan_done.json. Usage: python3 printify/apply_color_plan.py
"""
import json, time, sys
from pathlib import Path
from create_products import Printify

SHOP = 29509655
PLAN = Path(__file__).with_name("color_plan.json")
DONE = Path(__file__).with_name("color_plan_done.json")


def main():
    api = Printify(None)
    plan = json.loads(PLAN.read_text())
    done = json.loads(DONE.read_text()) if DONE.exists() else {}
    catalogs = {}
    for title, p in plan.items():
        if not p["add"] or title in done:
            continue
        x = api.get(f"/shops/{SHOP}/products/{p['printify']}.json")
        bp, pp = x["blueprint_id"], x["print_provider_id"]
        if (bp, pp) not in catalogs:
            catalogs[(bp, pp)] = api.get(f"/catalog/blueprints/{bp}/print_providers/{pp}/variants.json")["variants"]
        # Colour and size from the product's own variant titles ("Navy / M"): the catalog can drop retired variants.
        cs = {v["id"]: (v["title"].split(" / ")[0], v["title"].split(" / ")[-1]) for v in x["variants"]}
        enabled = [v for v in x["variants"] if v["is_enabled"]]
        size_price = {}
        for v in enabled:
            size_price.setdefault(cs[v["id"]][1], v["price"])
        new_ids = {i for i, (c, sz) in cs.items() if c in p["add"] and sz in size_price}
        present = {v["id"] for v in x["variants"]}
        if not new_ids <= present:
            print("  catalog variants missing from product:", title, len(new_ids - present))
            new_ids &= present
        variants = []
        for v in x["variants"]:
            if v["id"] in new_ids:
                variants.append({"id": v["id"], "price": size_price[cs[v["id"]][1]], "is_enabled": True})
            else:
                variants.append({"id": v["id"], "price": v["price"], "is_enabled": v["is_enabled"]})
        enabled_ids = {v["id"] for v in enabled}
        print_areas = []
        for pa in x["print_areas"]:
            ids = list(pa["variant_ids"])
            if enabled_ids & set(ids):
                ids += [i for i in new_ids if i not in ids]
            else:
                ids = [i for i in ids if i not in new_ids]
            print_areas.append({"variant_ids": ids, "placeholders": [
                {"position": ph["position"], "images": [dict({k: im[k] for k in ("id", "x", "y", "scale", "angle")}, _src=im.get("src"), _name=im.get("name"))
                                                        for im in ph["images"]]}
                for ph in pa["placeholders"] if ph["images"]]})
        print(title, "+", p["add"], len(new_ids), "variants", flush=True)
        # Variants only: Printify keeps the print areas (incl. neck-label text layers the API can't send back) and
        # files new variants under the same art. Then check every new variant sits in a print area that has art.
        api.call("PUT", f"/shops/{SHOP}/products/{x['id']}.json", json={"variants": variants})
        y = api.get(f"/shops/{SHOP}/products/{x['id']}.json")
        with_art = {i for pa in y["print_areas"] if any(ph["images"] for ph in pa["placeholders"]) for i in pa["variant_ids"]}
        if not new_ids <= with_art:
            print("  !! new variants without art:", title, len(new_ids - with_art), flush=True)
            continue
        for wait in (5, 60, 180, 300):
            time.sleep(wait)
            try:
                api.post(f"/shops/{SHOP}/products/{x['id']}/publish.json", {
                    "title": False, "description": False, "images": False, "variants": True,
                    "tags": False, "keyFeatures": False, "shipping_template": False})
                break
            except Exception as e:
                print("  publish retry:", str(e)[:150], flush=True)
        done[title] = {"printify": x["id"], "shopify": p["shopify"], "blueprint": bp, "added": p["add"],
                       "sides": sorted({ph["position"] for pa in x["print_areas"] for ph in pa["placeholders"] if ph["images"]})}
        DONE.write_text(json.dumps(done, indent=1))
        time.sleep(8)


if __name__ == "__main__":
    main()
