"""Round ceramic ornament print files (Printify blueprint 531, Circle, 954 px print area) from existing art.

Paintings (Legends Never Die) are cropped square around their subject and printed edge to edge.
Transparent art (Here Be Dragons, Post-Credits, Elsewhere logos, slogans) sits on black, sized to stay
inside the circle. Output: designs/print-ornament/<slug>.jpg at 1908 px (2x the print area).

Usage: python3 designs/src/render_ornaments.py [--preview OUT.jpg]
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "print-ornament"
SIZE = 1908
BLACK = (12, 12, 12)

# slug, source, mode, arg: crop -> (center y as a fraction of the painting height, side as a fraction of width);
# fit -> art height as a fraction of the circle diameter
ORNAMENTS = [
    ("born-ready", "print-drop4/05-born-ready-back.png", "crop", (0.33, 1.0)),
    ("fallen-not-finished", "print-drop4/06-fallen-not-finished-back.png", "crop", (0.36, 0.92)),
    ("going-with-the-flow", "print-drop4/08-going-with-the-flow-back.png", "crop", (0.42, 0.92)),
    ("queen-forever", "print-drop4/10-queen-forever-back.png", "crop", (0.33, 1.0)),
    ("dragonfall", "realms-src/04-dragon-wanderer-4x.png", "fit", 0.80),
    ("lantern-witch", "realms-src/06-lantern-witch-4x.png", "fit", 0.80),
    ("moonwood-druid", "realms-src/08-antler-druid.png", "fit", 0.80),
    ("post-credits-scene", "realms-src/01-post-credits-scene-4x.png", "fit", 0.70),
    ("elsewhere-psychedelic-drip", "print-brand/01-psychedelic-drip.png", "fit", 0.72),
    ("elsewhere-groovy-retro", "print-brand/02-groovy-retro.png", "fit", 0.60),
    ("elsewhere-chrome-globe", "print-brand/03-chrome-globe.png", "fit", 0.64),
    ("elsewhere-dreamscape", "print-brand/07-dreamscape.png", "fit", 0.76),
    ("not-ai-just-tired", "print/03-not-ai-just-tired-white.png", "fit", 0.40),
]
PAINTING_FRACTION = 0.82  # the painting's share of the poster height (title band below it)


def render(src, mode, arg):
    art = Image.open(ROOT / src).convert("RGBA")
    canvas = Image.new("RGBA", (SIZE, SIZE), BLACK + (255,))
    if mode == "crop":
        cy, side = arg
        w, h = art.size
        s = int(w * side)
        y = int(h * PAINTING_FRACTION * cy) - s // 2
        y = max(0, min(y, int(h * PAINTING_FRACTION) - s))
        x = (w - s) // 2
        canvas.alpha_composite(art.crop((x, y, x + s, y + s)).resize((SIZE, SIZE), Image.LANCZOS))
    else:
        art = art.crop(art.getbbox())
        w, h = art.size
        scale = min(SIZE * arg / h, SIZE * 0.86 / w)
        art = art.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        canvas.alpha_composite(art, ((SIZE - art.width) // 2, (SIZE - art.height) // 2))
    return canvas.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    tiles = []
    for slug, src, mode, arg in ORNAMENTS:
        img = render(src, mode, arg)
        img.save(OUT / f"{slug}.jpg", quality=95)
        t = img.resize((300, 300))
        mask = Image.new("L", (300, 300), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 299, 299), fill=255)
        tile = Image.new("RGB", (300, 300), "white")
        tile.paste(t, (0, 0), mask)
        tiles.append(tile)
        print("wrote", slug)
    if args.preview:
        cols = 5
        sheet = Image.new("RGB", (cols * 310, -(-len(tiles) // cols) * 310), "white")
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % cols) * 310, (i // cols) * 310))
        sheet.save(args.preview)


if __name__ == "__main__":
    main()
