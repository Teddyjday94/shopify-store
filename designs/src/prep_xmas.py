"""Christmas Collection back prints: key out the black background and upscale 3x for DTG.

With --hd DIR, DIR holds AI-upscaled (Real-ESRGAN x4) copies named xmas-<name>.png; those are keyed
as they are (capped at 4800px) instead of the Lanczos enlargement.
Near-black becomes transparent (a soft ramp, so glow and smoke fade instead of cutting off) and
the art is cropped to its edges. Output: designs/print-xmas/<name>-back.png
Usage: python3 designs/src/prep_xmas.py [--hd DIR]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "xmas-src", ROOT / "print-xmas"
LO, HI = 14, 46  # brightness where alpha ramps from 0 to full
HD = Path(sys.argv[sys.argv.index("--hd") + 1]) if "--hd" in sys.argv else None


def key(im):
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    alpha = np.clip((rgb.max(axis=2) - LO) / (HI - LO), 0, 1)
    out = Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), "RGBA")
    a = out.getchannel("A").point(lambda v: 255 if v > 60 else 0)
    return out.crop(a.getbbox())


def upscale(im, f=3):
    big = im.resize((im.width * f, im.height * f), Image.LANCZOS)
    rgb = big.convert("RGB").filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
    return Image.merge("RGBA", (*rgb.split(), big.getchannel("A")))


def cap(im, n=4800):  # 4800px is >300 DPI at the biggest print size
    f = n / max(im.size)
    return im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS) if f < 1 else im


for src in sorted(SRC.glob("*.png")):
    hd = HD and HD / f"xmas-{src.name}"
    if hd and hd.exists():
        art, how = cap(key(Image.open(hd))), "AI x4"
    else:
        art, how = upscale(key(Image.open(src))), "lanczos x3"
    art.save(OUT / f"{src.stem}-back.png", optimize=True)
    print(src.stem, how, art.size)
