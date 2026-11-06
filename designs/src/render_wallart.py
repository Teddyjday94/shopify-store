"""Render print files for posters, desk mats and phone cases.

Posters and desk mats: the Immortalized poster art (print-drop4/*-back.png) and the Christmas art
(print-xmas/*-back.png) on a blurred, darkened fill of the same art, so any crop Printify makes for a
smaller size only trims background. Phone cases: the Relatable slogans (print-relatable/*.png, light ink)
on a dark solid color, sitting low enough to clear the camera bump.

Output: designs/print-wall/<slug>-poster.jpg (3:4), <slug>-deskmat.jpg (32:16.8),
        designs/print-case/<slug>-case.jpg (1:1.8)
Usage:  python3 designs/src/render_wallart.py
"""

import glob
import os

from PIL import Image, ImageEnhance, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), "..")
WALL = os.path.join(ROOT, "print-wall")
CASE = os.path.join(ROOT, "print-case")


def blurred_fill(art, w, h, dark=0.32):
    """Cover (w, h) with a heavily blurred, darkened copy of the art."""
    flat = Image.new("RGB", art.size, (12, 11, 14))
    flat.paste(art, mask=art.split()[-1])
    s = max(w / flat.width, h / flat.height)
    small = flat.resize((max(1, int(flat.width * s / 8)), max(1, int(flat.height * s / 8))), Image.LANCZOS)
    small = small.filter(ImageFilter.GaussianBlur(14))
    small = ImageEnhance.Brightness(small).enhance(dark)
    big = small.resize((int(small.width * 8), int(small.height * 8)), Image.BICUBIC)
    return big.crop(((big.width - w) // 2, (big.height - h) // 2, (big.width - w) // 2 + w, (big.height - h) // 2 + h))


def place(canvas, art, box_h, cx, cy, max_w=None):
    s = box_h / art.height
    if max_w and art.width * s > max_w:
        s = max_w / art.width
    a = art.resize((int(art.width * s), int(art.height * s)), Image.LANCZOS)
    canvas.paste(a, (int(cx - a.width / 2), int(cy - a.height / 2)), a)


def wall(src, slug):
    art = Image.open(src).convert("RGBA")
    # Poster 3:4. Art keeps 8% side and 5% top/bottom margins so 2:3 and 11x14 crops stay clean.
    W, H = 5400, 7200
    c = blurred_fill(art, W, H)
    place(c, art, H * 0.86, W / 2, H / 2, max_w=W * 0.84)
    c.save(os.path.join(WALL, f"{slug}-poster.jpg"), quality=92)
    # Desk mat 16x32 ratio; the 12x18 crop keeps the middle 76% of the width.
    W, H = 9921, 5197
    c = blurred_fill(art, W, H, dark=0.28)
    place(c, art, H * 0.88, W / 2, H / 2)
    c.save(os.path.join(WALL, f"{slug}-deskmat.jpg"), quality=90)


CASE_COLORS = ["#141414", "#1c2340", "#3a1824", "#1d3a2f", "#2b2141", "#3b2414", "#14303a", "#2a2a2a"]


def case(src, slug, color):
    art = Image.open(src).convert("RGBA")
    art = art.crop(art.getbbox())
    W, H = 1500, 2700
    c = Image.new("RGBA", (W, H), color)
    place(c, art, H * 0.52, W / 2, H * 0.60, max_w=W * 0.80)
    c.convert("RGB").save(os.path.join(CASE, f"{slug}-case.jpg"), quality=93)


def main():
    os.makedirs(WALL, exist_ok=True)
    os.makedirs(CASE, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(ROOT, "print-drop4", "*-back.png"))) + \
            sorted(glob.glob(os.path.join(ROOT, "print-xmas", "*-back.png"))):
        slug = os.path.basename(f)[:-len("-back.png")]
        wall(f, slug)
        print("wall", slug)
    for i, f in enumerate(sorted(glob.glob(os.path.join(ROOT, "print-relatable", "*.png")))):
        slug = os.path.basename(f)[:-4]
        case(f, slug, CASE_COLORS[i % len(CASE_COLORS)])
        print("case", slug)


if __name__ == "__main__":
    main()
