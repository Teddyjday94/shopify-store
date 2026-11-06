"""Relatable Collection print files: the uploads already have transparent backgrounds; this drops the
faint near-black edge pixels left over from the old black background and crops to the art.
With --hd DIR, DIR holds AI-upscaled (Real-ESRGAN x4) copies of the sources, used as they are;
otherwise the sources are enlarged 3x with Lanczos.  Output: designs/print-relatable/<name>.png
Usage: python3 designs/src/prep_relatable.py [--hd DIR]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "relatable-src", ROOT / "print-relatable"

HD = Path(sys.argv[sys.argv.index("--hd") + 1]) if "--hd" in sys.argv else None

for src in sorted(SRC.glob("*.png")):
    hd = HD and (HD / src.name).exists()
    a = np.asarray(Image.open(HD / src.name if hd else src).convert("RGBA")).copy()
    bright = a[..., :3].max(axis=2)
    a[(a[..., 3] < 250) & (bright < 35), 3] = 0          # leftover background halo
    a[a[..., 3] < 12, 3] = 0                              # invisible dust
    im = Image.fromarray(a, "RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    if hd and max(im.size) > 4800:                     # 4800px tall is >300 DPI at the biggest print size
        im = im.resize((round(im.width * 4800 / max(im.size)), round(im.height * 4800 / max(im.size))), Image.LANCZOS)
    if not hd:
        big = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
        rgb = big.convert("RGB").filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
        im = Image.merge("RGBA", (*rgb.split(), big.getchannel("A")))
    im.save(OUT / src.name, optimize=True)
    print(src.stem, "AI x4" if hd else "lanczos x3", im.size)
