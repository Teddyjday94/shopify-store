"""Create the Drop 002 hoodies on the pocketless Comfort Colors 1467, so the front art prints full size.

Usage:
    python3 printify/create_pocketless.py            # dry run
    python3 printify/create_pocketless.py --apply    # create + publish
"""

import argparse

import create_products
from create_hoodies import run
from fit import fill

# Monster Digital prints this blank with a short front area; SwiftPOD gives the full 3461x3955.
create_products.PREFERRED_PROVIDERS = ["SwiftPOD", "Printify Choice"]

FEATURES = ("<ul><li>Full-size front and back print (no front pocket, so the art gets the whole front)</li>"
            "<li>Lightweight 100% ring-spun cotton, garment-dyed for a soft, lived-in feel</li>"
            "<li>Jersey-lined hood, relaxed fit</li>"
            "<li>Printed to order just for you</li></ul>")


def pocketless(title, colors, front, back, tags, intro, signoff):
    return dict(title=title, colors=colors, price=6800,
                prints=[("front", front, fill), ("back", back, fill)],
                tags=["hoodie", "drop 002"] + tags,
                description=f"{intro}{FEATURES}<p><em>{signoff}</em></p>")


PRODUCTS = [
    pocketless("Systems Still Functional Hoodie", ["Black", "Pepper"],
               "06-front-error-skull.png", "06-back-systems-still-functional.png",
               ["glitch", "skull", "tired"],
               "<p>Boot sequence complete. Anomalies detected. Proceeding anyway, but warmer.</p>",
               "Tired but here anyway."),
    pocketless("Same Chaos Different Day Hoodie", ["Grey", "Ivory", "Hydrangea", "Blue Jean"],
               "01-front-engraved-moon-miner.png", "01-back-lunar-phases-same-chaos-different-day.png",
               ["moon", "astronaut", "space"],
               "<p>An engraved astronaut mining the moon on the front, the lunar phases down the back.</p>",
               "Same chaos. Different day."),
    pocketless("Same Mind Brighter Days Hoodie", ["Black", "Pepper"],
               "02-front-grunge-samurai-red-sakura-sun.png", "02-back-sakura-moon-same-mind-brighter-days.png",
               ["samurai", "sakura", "japanese"],
               "<p>The skeleton samurai on his coffee break up front, the moonlit sakura panel on the back.</p>",
               "Same mind. Brighter days."),
    pocketless("Balance Hoodie", ["Grey", "Ivory", "Hydrangea", "White"],
               "03-front-balance-of-mind-and-heart.png", "03-back-process-over-perfection-moons.png",
               ["brain", "heart", "moon"],
               "<p>Brain and heart on the front, a column of moons on the back for everyone still working it out.</p>",
               "Process over perfection."),
    pocketless("Somewhere in a Calmer Place Hoodie", ["Grey", "Ivory", "Hydrangea", "White"],
               "04-front-sumi-ink-skull-mountain-landscape.png", "04-back-calmer-place-mountain-landscape.png",
               ["skull", "mountains", "japanese"],
               "<p>Physically here, mentally in the mountains: the ink-wash skull up front, the mountain scroll "
               "on the back.</p>",
               "Somewhere in a calmer place."),
    pocketless("A Quieter Mind Hoodie", ["Black", "Pepper", "Blue Jean"],
               "05-front-a-quieter-mind-space-cat.png", "05-back-space-cat-helmet-blueprint.png",
               ["cat", "astronaut", "moon"],
               "<p>The astronaut cat watching the moon on the front, the helmet blueprint on the back.</p>",
               "A quieter mind. A brighter tomorrow."),
]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    run(PRODUCTS, "1467", ap.parse_args().apply)
