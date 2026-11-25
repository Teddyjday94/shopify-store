"""Doomsday drop print files: Kittl 4x upscales (up/) keyed to transparent for dark garments.
Black backgrounds: soft luminance key (near-black -> clear). Doom in Our Time: white background keyed out.
Usage: python3 designs/doomsday-2026/print/prep.py"""
import glob, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.join(HERE, "..", "up")
for f in sorted(glob.glob(os.path.join(UP, "*"))):
    slug = os.path.splitext(os.path.basename(f))[0].replace("-final", "")
    a = np.asarray(Image.open(f).convert("RGB")).astype(np.float32)
    if slug == "doom-in-our-time":
        dist = 255 - a.min(axis=2)                       # how far from white
        alpha = np.clip((dist - 25) / 60, 0, 1)
        rgb = a
    else:
        lum = a.max(axis=2)
        alpha = np.clip((lum - 14) / 36, 0, 1)
        rgb = a
    out = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    im = im.crop(im.getbbox())
    im.save(os.path.join(HERE, f"{slug}.png"), optimize=True)
    print(slug, im.size, os.path.getsize(os.path.join(HERE, f"{slug}.png")) // 1024, "KB")
