"""Create the "Own Lane" drop (front-print tees) in Printify and publish them to Shopify.

Usage:
    python3 printify/create_drop3.py            # dry run
    python3 printify/create_drop3.py --apply    # create + publish
"""

import argparse

from create_drop2 import FULL, run

COMMIT = "f004e4e7df1a0a3b0672ab31244ff589f7472570"
FOLDER = "print-drop3"
FEATURES = ("<ul><li>Full-color front print</li>"
            "<li>Soft, lightweight 100% combed cotton</li>"
            "<li>Retail unisex fit</li>"
            "<li>Printed to order just for you</li></ul>")


def tee(title, colors, front, tags, intro, signoff):
    return dict(
        title=title, price=3200, model="3001", colors={c: "x" for c in colors},
        prints={"front": (front, FULL)},
        tags=["t-shirt", "own lane", "drop 003"] + tags,
        description=f"{intro}{FEATURES}<p><em>{signoff}</em></p>",
    )


PRODUCTS = [
    tee("In My Own Lane Tee", ["Soft Pink", "White", "Soft Cream", "Black"], "01-in-my-own-lane.png",
        ["pink", "airbrush", "butterflies", "glam"],
        "<p>Diploma in one hand, lip gloss in the other. Not competing, just cruising.</p>"
        "<p>Airbrush-style script wrapped in butterflies, gold chains and a whole lot of pink.</p>",
        "In my own lane."),
    tee("Butterfly Effect Tee", ["Soft Pink", "White", "Athletic Heather"], "02-butterfly-effect.png",
        ["portrait", "butterflies", "pink", "graffiti"],
        "<p>Pink shades on, chin up, unbothered.</p>"
        "<p>A spray-paint portrait with hot pink butterflies, stars and drips.</p>",
        "Small moves. Big energy."),
    tee("Lucky Charm Tee", ["Soft Pink", "White", "Soft Cream", "Black"], "03-lucky-charm.png",
        ["pink", "dice", "cherries", "glam"],
        "<p>Gloss, grills, a diploma and a roll of the dice. Luck had help.</p>"
        "<p>A glam collage of pink lips, gold chains, cherries, an 8-ball and leopard stars.</p>",
        "Made my own luck."),
    tee("Sunflower Soul Tee", ["Athletic Heather", "White", "Natural", "Soft Cream"], "04-sunflower-soul.png",
        ["portrait", "sunflowers", "floral", "colorful"],
        "<p>Face to the sun, crown of flowers.</p>"
        "<p>A painted portrait with sunflowers and roses, gold hoops and colors that drip into "
        "the hem.</p>",
        "Always growing."),
    tee("Color Me Bold Tee", ["Black", "White", "Natural", "Athletic Heather"], "05-color-me-bold.png",
        ["portrait", "afro", "gold", "colorful"],
        "<p>Big hair, gold hoops, zero apologies.</p>"
        "<p>A graphic portrait set against bursts of red, orange and blue.</p>",
        "Bold looks good on you."),
    tee("Crown & Curls Tee", ["Soft Cream", "White", "Natural", "Athletic Heather"], "06-crown-and-curls.png",
        ["portrait", "curls", "crown", "gold"],
        "<p>Curls up, glasses on, crown optional (but included).</p>"
        "<p>A painted portrait with gold brush strokes, hoops and a hand-drawn crown.</p>",
        "Wear the crown."),
    tee("Pink Crown Tee", ["Soft Pink", "White", "Black", "Athletic Heather"], "07-pink-crown.png",
        ["portrait", "crown", "pink", "colorful"],
        "<p>Gold frames, glossy lips and a pink crown, drawn on just in case anyone forgot.</p>"
        "<p>A vivid pop-art portrait in pink, orange and blue.</p>",
        "Crowned by me."),
    tee("Sisterhood Tee", ["Athletic Heather", "Natural", "Soft Cream"], "08-sisterhood.png",
        ["portrait", "sisterhood", "gold", "colorful"],
        "<p>Three queens, one frame.</p>"
        "<p>A painted portrait of three women in shades, gold earrings and a headwrap, over "
        "blocks of green, gold, blue and orange.</p>",
        "Better together."),
]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    run(PRODUCTS, COMMIT, FOLDER, ap.parse_args().apply)
