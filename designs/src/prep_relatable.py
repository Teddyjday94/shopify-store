"""Relatable Collection print files: the uploads already have transparent backgrounds; this drops the
faint near-black edge pixels left over from the old black background, crops to the art and enlarges
3x for DTG.  Output: designs/print-relatable/<name>.png
Usage: python3 designs/src/prep_relatable.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "relatable-src", ROOT / "print-relatable"

for src in sorted(SRC.glob("*.png")):
    a = np.asarray(Image.open(src).convert("RGBA")).copy()
    bright = a[..., :3].max(axis=2)
    a[(a[..., 3] < 250) & (bright < 35), 3] = 0          # leftover background halo
    a[a[..., 3] < 12, 3] = 0                              # invisible dust
    im = Image.fromarray(a, "RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    big = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
    rgb = big.convert("RGB").filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
    big = Image.merge("RGBA", (*rgb.split(), big.getchannel("A")))
    big.save(OUT / src.name, optimize=True)
    print(src.stem, im.size, "->", big.size)
