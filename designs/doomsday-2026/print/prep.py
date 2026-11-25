"""Doomsday drop print files: Kittl 4x upscales (up/) keyed to transparent for dark garments.
Black backgrounds: soft luminance key (near-black -> clear). Doom in Our Time: white background keyed out. A Stolen Life: kept as a full poster.
Usage: python3 designs/doomsday-2026/print/prep.py"""
import glob, os
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.join(HERE, "..", "up")
for f in sorted(glob.glob(os.path.join(UP, "*"))):
    slug = os.path.splitext(os.path.basename(f))[0].replace("-final", "")
    a = np.asarray(Image.open(f).convert("RGB")).astype(np.float32)
    if slug == "a-stolen-life":                         # full vintage poster: print as-is, but clear the light corners
        dist = 255 - a.min(axis=2)
        alpha = np.ones(a.shape[:2], np.float32)
        h, w = alpha.shape
        for ys, xs in ((slice(0, h // 12), slice(0, w // 12)), (slice(0, h // 12), slice(-w // 12, None)),
                       (slice(-h // 12, None), slice(0, w // 12)), (slice(-h // 12, None), slice(-w // 12, None))):
            c = a[ys, xs]
            chroma = c.max(axis=2) - c.min(axis=2)          # backdrop is neutral white/grey, the paper is warm cream
            alpha[ys, xs] = np.where((chroma < 16) & (c.min(axis=2) > 190), 0.0, 1.0)
        rgb = a
    elif slug == "doom-in-our-time":
        dist = 255 - a.min(axis=2)                       # how far from white
        alpha = np.clip((dist - 25) / 60, 0, 1)
        rgb = a
    else:
        lum = a.max(axis=2)
        alpha = np.clip((lum - 14) / 36, 0, 1)
        rgb = a
    out = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    if slug == "a-stolen-life":                            # soften the cut corners
        im.putalpha(im.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.5)))
    im = im.crop(im.getbbox())
    im.save(os.path.join(HERE, f"{slug}.png"), optimize=True)
    print(slug, im.size, os.path.getsize(os.path.join(HERE, f"{slug}.png")) // 1024, "KB")
