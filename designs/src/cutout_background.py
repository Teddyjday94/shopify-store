"""Remove a solid background that touches the image edges (white or black), keeping the art inside.
usage: cutout.py IN OUT white|black"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

src, out, kind = sys.argv[1:4]
a = np.array(Image.open(src).convert('RGB')).astype(np.int16)
ref = np.array([255, 255, 255] if kind == 'white' else [0, 0, 0])
dist = np.abs(a - ref).max(axis=2)              # 0 = exactly background colour
near = dist < 28                                 # background-like pixels
lab, n = ndimage.label(near)
edge_labels = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(edge_labels))
# soft edge: pixels just outside the background fade in over a short colour ramp
ring = ndimage.binary_dilation(bg, iterations=2) & ~bg
alpha = np.where(bg, 0, 255).astype(np.float32)
alpha[ring] = np.clip((dist[ring] - 10) / 60.0, 0, 1) * 255
rgba = np.dstack([a.astype(np.uint8), alpha.astype(np.uint8)])
Image.fromarray(rgba, 'RGBA').save(out)
print(out, 'background removed: %.0f%%' % (bg.mean() * 100))
