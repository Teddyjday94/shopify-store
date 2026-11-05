"""Christmas mugs and ornaments, die-cut style: each design is cut out of its black background,
keeping only a thin black edge that follows the art's outline (so cream lettering still reads),
and printed straight on the white mug or ornament. No black band, no box.

Mug: two copies at the wrap's full height. Ornament: the largest size at which the circle cuts off
almost nothing of the art.
Usage: python3 designs/src/render_home_xmas.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "xmas-src", ROOT / "print-home"
NAMES = ["01-on-the-naughty-list-again", "02-suck-it-up-buttercup", "03-dear-santa-bring-bourbon",
         "04-the-gift-is-me", "05-holly-jolly-chaos"]
MUG_W, MUG_H = 4950, 2310   # 2475 x 1155 wrap at 2x
ORN = 2400


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def diecut(path, close=22, edge=9):
    """Cut the art from its black background, keeping a thin black edge around its outline."""
    im = Image.open(path).convert("RGB")
    bright = np.asarray(im).max(axis=2)
    lab, _ = ndimage.label(bright < 38)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    content = ~np.isin(lab, list(border))
    content = ndimage.binary_opening(content, structure=disk(2))          # drop stray specks
    pad = close + 2
    shape = ndimage.binary_closing(np.pad(content, pad), structure=disk(close))[pad:-pad, pad:-pad]
    shape = ndimage.binary_dilation(ndimage.binary_fill_holes(shape), structure=disk(edge))
    alpha = Image.fromarray((shape * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out.crop(alpha.getbbox())


def mug(art):
    h = int(MUG_H * 0.97)
    a = art.resize((round(art.width * h / art.height), h), Image.LANCZOS)
    canvas = Image.new("RGBA", (MUG_W, MUG_H), (0, 0, 0, 0))
    for cx in (MUG_W // 4, 3 * MUG_W // 4):
        canvas.alpha_composite(a, (cx - a.width // 2, (MUG_H - h) // 2))
    return canvas


def ornament(art):
    small = art.copy()
    small.thumbnail((600, 600))
    ys, xs = np.nonzero(np.asarray(small.getchannel("A")) > 40)
    best = 0.5
    for f in np.arange(0.5, 1.25, 0.01):           # art height as a fraction of the diameter
        h = f; w = h * small.width / small.height
        px = xs / small.width * w - w / 2
        py = ys / small.height * h - h / 2
        if ((px ** 2 + py ** 2) > 0.485 ** 2).mean() <= 0.004:   # 3% safety ring at the edge
            best = f
    h = int(ORN * best)
    a = art.resize((round(art.width * h / art.height), h), Image.LANCZOS)
    canvas = Image.new("RGBA", (ORN, ORN), (0, 0, 0, 0))
    canvas.alpha_composite(a, ((ORN - a.width) // 2, (ORN - h) // 2))
    return canvas, best


for n in NAMES:
    art = diecut(SRC / f"{n}.png")
    mug(art).save(OUT / f"{n}-mug.png", optimize=True)
    orn, f = ornament(art)
    orn.save(OUT / f"{n}-ornament.png", optimize=True)
    print(n, f"ornament art height {f:.0%} of the circle")
