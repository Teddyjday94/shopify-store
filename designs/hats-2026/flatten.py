"""Flat, embroidery-friendly versions of the six collection emblems (2026-11-20).
Source: designs/pants-2026/print/<slug>-subtle.png (cleaned emblems). Each emblem gets a short list of thread colours
(THREADS); every pixel is mapped to the nearest thread colour or to "drop" (shading, clouds), then each colour region is
smoothed into solid fills (mode filter) and specks/holes too small to sew are removed. Output: flat/<slug>.png."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = '../pants-2026/print'
CREAM, GOLD, RED, TEAL, PINK, ROSE, LEAF, LAV = (240, 222, 190), (222, 170, 95), (215, 60, 45), (95, 165, 140), (205, 95, 120), (150, 40, 60), (110, 130, 80), (150, 120, 175)
# (thread colours kept, colours treated as background/drop)
THREADS = {
    'side-quest': ([RED, (250, 225, 200), GOLD], [(150, 140, 135), (110, 100, 100), (60, 55, 60), (200, 185, 165)]),
    'elsewhere-signature': ([GOLD, LAV], [(90, 70, 70), (60, 50, 60)]),
    'legends-never-die': ([GOLD], [(110, 85, 65), (60, 50, 45)]),
    'born-ready': ([CREAM, RED, GOLD], [(90, 60, 50), (50, 40, 40)]),
    'urban-collection': ([TEAL], [(60, 80, 75), (40, 45, 45)]),
    'female-lead': ([CREAM, PINK, ROSE, LEAF, GOLD], [(80, 50, 55), (50, 40, 45)]),
}
# per-emblem tweaks: colour groups whose connected shapes get one solid colour (their majority), extra smoothing,
# and the smallest piece kept (fraction of the emblem's area; smaller pieces can't be sewn cleanly)
UNIFY = {'born-ready': [[0, 2]], 'female-lead': [[0, 1]], 'side-quest': [[0, 2]]}
SMOOTH = {'female-lead': (13, 11, 9), 'born-ready': (11, 9, 7)}
MIN_PIECE = {'side-quest': 0.006, 'elsewhere-signature': 0.0002, 'legends-never-die': 0.0002, 'born-ready': 0.004,
             'urban-collection': 0.004, 'female-lead': 0.003}
SPECK = {'born-ready': 900, 'side-quest': 600, 'female-lead': 500}   # colour islands smaller than this merge into their surroundings
os.makedirs('flat', exist_ok=True)


def mode_filter(idx, k, size):
    votes = np.stack([ndimage.uniform_filter((idx == i).astype(float), size) for i in range(k)])
    return votes.argmax(0)


def flatten(slug):
    im = Image.open(f'{SRC}/{slug}-subtle.png').convert('RGBA')
    im = im.crop(im.getbbox())
    a = np.asarray(im).astype(float)
    rgb, alpha = a[..., :3], a[..., 3]
    keep_cols, drop_cols = THREADS[slug]
    pal = np.array(keep_cols + drop_cols, float)
    k = len(pal) + 1                                   # last index = transparent
    idx = ((rgb[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
    idx[idx >= len(keep_cols)] = k - 1                 # drop colours -> transparent
    lum = rgb @ [0.299, 0.587, 0.114]
    idx[(alpha < 140) | (lum < 50)] = k - 1
    for size in SMOOTH.get(slug, (9, 9, 7)):          # solid fills
        idx = mode_filter(idx, k, size)
    for group in UNIFY.get(slug, []):                  # one colour per connected shape within a group
        m = np.isin(idx, group)
        lab, n = ndimage.label(m)
        for i in range(1, n + 1):
            sel = lab == i
            counts = [(idx[sel] == g).sum() for g in group]
            idx[sel] = group[int(np.argmax(counts))]
    # remove regions too small to sew (merge into the surrounding majority)
    for c in range(k):
        lab, n = ndimage.label(idx == c)
        if n:
            sizes = ndimage.sum(idx == c, lab, range(1, n + 1))
            small = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s < SPECK.get(slug, 250)])
            if c < len(keep_cols):
                # whole pieces (all thread colours together) below MIN_PIECE are dropped
                pass
            if small.any():
                idx[small] = -1
    while (idx == -1).any():
        filled = mode_filter(np.where(idx == -1, k - 1, idx), k, 5)
        idx = np.where(idx == -1, filled, idx)
        break
    solid = (idx >= 0) & (idx < len(keep_cols))
    lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=2))
    if n:
        sizes = ndimage.sum(solid, lab, range(1, n + 1))
        tiny = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s < MIN_PIECE[slug] * solid.size])
        idx[tiny & solid] = k - 1
    out = np.zeros(a.shape, np.uint8)
    cols = np.vstack([np.array(keep_cols), np.zeros((k - len(keep_cols), 3))]).astype(np.uint8)
    out[..., :3] = cols[np.clip(idx, 0, k - 1)]
    out[..., 3] = np.where(idx < len(keep_cols), 255, 0)
    img = Image.fromarray(out)
    img = img.crop(img.getbbox())
    img.save(f'flat/{slug}.png')
    return img


if __name__ == '__main__':
    for s in THREADS:
        print(s, flatten(s).size, len(THREADS[s][0]), 'thread colours')
