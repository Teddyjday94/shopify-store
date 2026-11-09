"""Remove a baked-in transparency checkerboard (white and light-grey squares) that touches the image edges.
usage: cutout_checker.py IN OUT"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

src, out = sys.argv[1:3]
a = np.array(Image.open(src).convert('RGB')).astype(np.int16)
spread = a.max(axis=2) - a.min(axis=2)            # 0 = neutral grey/white
light = a.min(axis=2)
near = (spread < 14) & (light > 196)              # checker squares (white ~255, grey ~205-235)
near = ndimage.binary_opening(near, iterations=1)
lab, n = ndimage.label(near)
edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(edge))
bg = ndimage.binary_fill_holes(~bg) == 0 if False else bg
ring = ndimage.binary_dilation(bg, iterations=2) & ~bg
alpha = np.where(bg, 0, 255).astype(np.float32)
alpha[ring] = np.clip((196 - light[ring] + spread[ring] * 3) / 60.0, 0.35, 1) * 255
Image.fromarray(np.dstack([a.astype(np.uint8), alpha.astype(np.uint8)]), 'RGBA').save(out)
print(out, 'background removed: %.0f%%' % (bg.mean() * 100))
