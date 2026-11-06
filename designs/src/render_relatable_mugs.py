"""Relatable Collection mugs, die-cut style: each design sits on a black backing that follows its
outline (cream type needs a dark ground), printed on both sides of the white mug.
Usage: python3 designs/src/render_relatable_mugs.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "print-relatable", ROOT / "print-home"   # print files: sharpest copies
MUG_W, MUG_H = 4950, 2310   # 2475 x 1155 wrap at 2x


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def diecut(path, close=34, edge=14):
    im = Image.open(path).convert("RGBA")
    im.thumbnail((1600, 1600), Image.LANCZOS)   # source scale the outline was tuned at; still > the mug's 1100px print height
    content = np.asarray(im.getchannel("A")) > 40
    content = ndimage.binary_opening(content, structure=disk(2))
    pad = close + 2
    shape = ndimage.binary_closing(np.pad(content, pad), structure=disk(close))[pad:-pad, pad:-pad]
    lab, n = ndimage.label(shape)                       # drop stray specks from the source file
    if n > 1:
        sizes = ndimage.sum(shape, lab, range(1, n + 1))
        shape = np.isin(lab, 1 + np.nonzero(sizes >= sizes.max() * 0.02)[0])
    shape = ndimage.binary_dilation(ndimage.binary_fill_holes(shape), structure=disk(edge))
    im.putalpha(Image.fromarray(np.where(shape, np.asarray(im.getchannel("A")), 0).astype(np.uint8)))
    alpha = Image.fromarray((shape * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
    backing = Image.new("RGBA", im.size, (14, 14, 14, 255))
    backing.putalpha(alpha)
    backing.alpha_composite(im)
    return backing.crop(alpha.getbbox())


def mug(art):
    h = int(MUG_H * 0.95)
    w = round(art.width * h / art.height)
    if w > MUG_W * 0.46:                       # wide designs: fit the width instead
        w = int(MUG_W * 0.46); h = round(art.height * w / art.width)
    a = art.resize((w, h), Image.LANCZOS)
    canvas = Image.new("RGBA", (MUG_W, MUG_H), (0, 0, 0, 0))
    for cx in (MUG_W // 4, 3 * MUG_W // 4):
        canvas.alpha_composite(a, (cx - w // 2, (MUG_H - h) // 2))
    return canvas


for src in sorted(SRC.glob("*.png")):
    num = int(src.stem[:2]) + 30                # 31-46, after the slogan mugs
    out = OUT / f"{num}-{src.stem[3:]}-mug.png"
    mug(diecut(src)).save(out, optimize=True)
    print(out.name)
