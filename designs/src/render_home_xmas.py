"""Christmas mugs and ornaments: the keyed art (black already removed, cropped to the art's edges)
on solid black, as large as the print area allows.

Mug: two copies filling the wrap's full height. Ornament: the largest size at which the circle cuts off
almost nothing of the art (it may trim empty corners, never lettering).
Usage: python3 designs/src/render_home_xmas.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "print-xmas", ROOT / "print-home"
NAMES = ["01-on-the-naughty-list-again", "02-suck-it-up-buttercup", "03-dear-santa-bring-bourbon",
         "04-the-gift-is-me", "05-holly-jolly-chaos"]
MUG_W, MUG_H = 4950, 2310   # 2475 x 1155 wrap at 2x
ORN = 2400


def mug(art):
    h = int(MUG_H * 0.98)
    a = art.resize((round(art.width * h / art.height), h), Image.LANCZOS)
    canvas = Image.new("RGB", (MUG_W, MUG_H), "black")
    for cx in (MUG_W // 4, 3 * MUG_W // 4):
        canvas.paste(a, (cx - a.width // 2, (MUG_H - h) // 2), a)
    return canvas


def ornament(art):
    small = art.copy()
    small.thumbnail((600, 600))
    alpha = np.asarray(small.getchannel("A")) > 40
    total = alpha.sum()
    best = 0.5
    for f in np.arange(0.5, 1.25, 0.01):           # art height as a fraction of the diameter
        D = 1000
        h = int(D * f); w = int(h * small.width / small.height)
        ys, xs = np.nonzero(alpha)
        px = (xs / small.width) * w - w / 2
        py = (ys / small.height) * h - h / 2
        outside = (px ** 2 + py ** 2) > (D * 0.485) ** 2   # 3% safety ring for the ornament's edge
        if outside.sum() / total <= 0.004:
            best = f
    h = int(ORN * best)
    a = art.resize((round(art.width * h / art.height), h), Image.LANCZOS)
    canvas = Image.new("RGB", (ORN, ORN), "black")
    canvas.paste(a, ((ORN - a.width) // 2, (ORN - h) // 2), a)
    return canvas, best


for n in NAMES:
    art = Image.open(SRC / f"{n}-back.png").convert("RGBA")
    mug(art).save(OUT / f"{n}-mug.png", optimize=True)
    orn, f = ornament(art)
    orn.save(OUT / f"{n}-ornament.png", optimize=True)
    print(n, f"ornament art height {f:.0%} of the circle")
