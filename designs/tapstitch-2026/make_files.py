"""Tapstitch print files (2026-11-21) for the US fleece set and the denim jacket, per collection.
Sources: designs/pants-2026/<slug>-bold.png (tall art, 2600x5600) and <slug>-subtle.png (emblem), cleaned like
pants-2026/make_print.py (faint pixels cleared, stray fragments dropped, hand trims).
Outputs (designs/tapstitch-2026/<slug>/), trimmed to the art, 300 dpi:
  back-dtf.png    hoodie back  (Oversize Fleeced Hoodie R00286, DTF)   - soft paint flattened onto black, hard edges
  emblem-dtf.png  hoodie front + sweatpants thigh (R00363, DTF)        - same treatment
  back-dtg.png    denim jacket back (UT0142, DTG)                      - original soft painting
  emblem-dtg.png  denim jacket chest (DTG)
DTF needs sharp edges (Tapstitch note); the art's soft painted edges were made for dark fabric, so semi-transparent
pixels are composited over black and kept where alpha >= 0.30. Use these on dark garment colours only."""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "pants-2026")
SLUGS = sys.argv[1:] or ["legends-never-die", "urban-collection", "side-quest"]
TRIM = {'urban-collection-subtle': (400, None), 'born-ready-subtle': (400, None),
        'elsewhere-signature-subtle': (410, (930, 1015))}


def clean(im, name):
    a = np.asarray(im).copy()
    a[a[:, :, 3] < 16, 3] = 0
    if name in TRIM:
        row, keep = TRIM[name]
        band = a[:row, :, 3].copy()
        if keep:
            band[:, :keep[0]] = 0; band[:, keep[1]:] = 0
        else:
            band[:] = 0
        a[:row, :, 3] = band
    mask = a[:, :, 3] > 0
    lab, n = ndimage.label(ndimage.binary_dilation(mask, iterations=8))
    if n > 1:
        objs = ndimage.find_objects(lab)
        sizes = ndimage.sum(mask, lab, range(1, n + 1))
        big = [i for i in range(n) if sizes[i] >= 0.05 * sizes.sum()]
        my, mx = 0.01 * mask.shape[0], 0.01 * mask.shape[1]
        y0 = min(objs[i][0].start for i in big) - my; y1 = max(objs[i][0].stop for i in big) + my
        x0 = min(objs[i][1].start for i in big) - mx; x1 = max(objs[i][1].stop for i in big) + mx
        keep = np.zeros_like(mask)
        for i, sl in enumerate(objs):
            if sl[0].stop > y0 and sl[0].start < y1 and sl[1].stop > x0 and sl[1].start < x1:
                keep |= lab == i + 1
        a[~keep, 3] = 0
    out = Image.fromarray(a)
    return out.crop(out.getbbox())


def dtf(im, cut=0.30):
    a = np.asarray(im).astype(np.float32) / 255.0
    alpha = a[:, :, 3:4]
    rgb = a[:, :, :3] * alpha                      # composite over black
    keep = alpha[:, :, 0] >= cut
    keep = ndimage.binary_opening(keep, iterations=1)  # drop single-pixel specks
    out = np.zeros_like(a)
    out[:, :, :3] = rgb
    out[:, :, 3] = keep.astype(np.float32)
    o = Image.fromarray((out * 255).round().astype(np.uint8))
    return o.crop(o.getbbox())


for slug in SLUGS:
    d = os.path.join(HERE, slug); os.makedirs(d, exist_ok=True)
    bold = clean(Image.open(os.path.join(SRC, f"{slug}-bold.png")).convert("RGBA"), f"{slug}-bold")
    emb = clean(Image.open(os.path.join(SRC, f"{slug}-subtle.png")).convert("RGBA"), f"{slug}-subtle")
    for name, im in (("back-dtg", bold), ("emblem-dtg", emb), ("back-dtf", dtf(bold)), ("emblem-dtf", dtf(emb))):
        im.save(os.path.join(d, f"{name}.png"), dpi=(300, 300))
        print(slug, name, im.size, f"{im.width/300*2.54:.0f}x{im.height/300*2.54:.0f} cm at 300 dpi")
