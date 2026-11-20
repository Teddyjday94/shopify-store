"""Sweatpant print files (2026-11-20) for Gildan 18200 left_leg_front (1200x4800 px).
Bold: the tall collection art, 1140 px wide, from 120 px below the waistband down the thigh.
Subtle: the emblem, 860 px wide, centred on the upper thigh (top at 300 px).
Stray fragments (left over from a source crop) are dropped: pieces lying wholly outside the box around the main
pieces (each >=5% of the art), padded by 1%, are removed. Faint pixels (alpha < 16) are cleared.
Usage: python3 make_print.py [pocket]   -> print/<name>.png or print-pocket/<name>.png"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

import sys
# Default: Gildan 18200 left/right_leg_front (1200x4800). "pocket": Gildan 18100 front_*_leg_dtf (1200x4200), used
# since 2026-11-20 with the emblem at full width (owner asked for a bigger print).
POCKET = 'pocket' in sys.argv[1:]
W, H = (1200, 4200) if POCKET else (1200, 4800)
OUT = 'print-pocket' if POCKET else 'print'
EMBLEM_W = 1140 if POCKET else 860
os.makedirs(OUT, exist_ok=True)


# Hand trims for smudges that touch or sit just above an emblem in its source file:
# name -> (rows above which to clear, (x0, x1) columns to keep in those rows, or None to clear the whole band)
TRIM = {'urban-collection-subtle': (400, None), 'born-ready-subtle': (400, None),
        'elsewhere-signature-subtle': (410, (930, 1015))}


def clean(im, name=''):
    a = np.asarray(im).copy()
    a[a[:, :, 3] < 16, 3] = 0
    if name in TRIM:
        row, keep = TRIM[name]
        band = a[:row, :, 3].copy()
        if keep:
            band[:, keep[0]:keep[1]] = a[:row, keep[0]:keep[1], 3]
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


for f in sorted(os.listdir('.')):
    if not f.endswith('.png') or f.startswith('female-lead-original'):
        continue
    name = f[:-4]
    art = clean(Image.open(f).convert('RGBA'), name)
    bold = name.endswith('-bold')
    w = 1140 if bold else EMBLEM_W
    h = round(art.height * w / art.width)
    if h > H - 240:
        h = H - 240; w = round(art.width * h / art.height)
    art = art.resize((w, h), Image.LANCZOS)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(art, ((W - w) // 2, 120 if bold else 300))
    canvas.save(f'{OUT}/{name}.png', dpi=(300, 300))
    print(name, (w, h))
