"""Mugs and ornaments for the second Christmas batch (designs/print-xmas2, already transparent).

Same look as render_home_xmas.py: the art gets a thin black edge that follows its outline so cream
lettering reads on white ceramic; mug = two copies around the wrap, ornament = art over a blur of its colors.
Usage: python3 designs/src/render_home_xmas2.py
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "print-xmas2", ROOT / "print-home"
MUG_W, MUG_H = 4950, 2310
ORN = 2400


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def backed(path, close=40, edge=18):
    """Put a black backing under the art that follows its outline, plus a thin edge."""
    art = Image.open(path).convert("RGBA")
    art = art.crop(art.getchannel("A").getbbox())
    small = 4  # work on a quarter-size mask for speed
    m = np.asarray(art.getchannel("A").resize((art.width // small, art.height // small))) > 30
    pad = close // small + 2
    shape = ndimage.binary_closing(np.pad(m, pad), structure=disk(close // small))[pad:-pad, pad:-pad]
    shape = ndimage.binary_dilation(ndimage.binary_fill_holes(shape), structure=disk(edge // small))
    mask = Image.fromarray((shape * 255).astype(np.uint8)).resize(art.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(2))
    base = Image.new("RGBA", art.size, (12, 11, 14, 0))
    base.putalpha(mask)
    base.alpha_composite(art)
    return base


def mug(art):
    h = int(MUG_H * 0.97)
    a = art.resize((round(art.width * h / art.height), h), Image.LANCZOS)
    if a.width > MUG_W // 2 * 0.97:
        w = int(MUG_W // 2 * 0.97); a = art.resize((w, round(art.height * w / art.width)), Image.LANCZOS)
    canvas = Image.new("RGBA", (MUG_W, MUG_H), (0, 0, 0, 0))
    for cx in (MUG_W // 4, 3 * MUG_W // 4):
        canvas.alpha_composite(a, (cx - a.width // 2, (MUG_H - a.height) // 2))
    return canvas


def blurred_fill(art):
    rgb = Image.new("RGB", art.size, (12, 11, 14))
    rgb.paste(art, (0, 0), art)
    s = ORN / min(rgb.size) * 1.25
    bg = rgb.resize((int(rgb.width * s), int(rgb.height * s)), Image.LANCZOS)
    left, top = (bg.width - ORN) // 2, (bg.height - ORN) // 2
    bg = bg.crop((left, top, left + ORN, top + ORN)).filter(ImageFilter.GaussianBlur(70))
    return ImageEnhance.Color(ImageEnhance.Brightness(bg).enhance(0.6)).enhance(1.15)


def ornament(art):
    small = art.copy(); small.thumbnail((600, 600))
    ys, xs = np.nonzero(np.asarray(small.getchannel("A")) > 40)
    best = 0.5
    for f in np.arange(0.5, 1.25, 0.01):
        w = f * small.width / small.height
        px = xs / small.width * w - w / 2; py = ys / small.height * f - f / 2
        if ((px ** 2 + py ** 2) > 0.485 ** 2).mean() <= 0.004:
            best = f
    best *= 1.08
    h = int(ORN * best)
    a = art.resize((round(art.width * h / art.height), h), Image.LANCZOS)
    canvas = blurred_fill(art).convert("RGBA")
    canvas.alpha_composite(a, ((ORN - a.width) // 2, (ORN - h) // 2))
    return canvas.convert("RGB"), best


if __name__ == "__main__":
    for p in sorted(SRC.glob("*.png")):
        art = backed(p)
        mug(art).save(OUT / f"{p.stem}-mug.png", optimize=True)
        orn, f = ornament(art)
        orn.save(OUT / f"{p.stem}-ornament.png", optimize=True)
        print(p.stem, f"ornament art {f:.0%} of the circle")
