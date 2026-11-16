"""Cut a logo out of its flat paper/black background and write a 300 DPI print PNG.

usage: logo_cutout.py IN OUT [--max 4500]

The background colour is read from the image border. Only background-coloured pixels
connected to the border are removed (flood fill), so enclosed areas of the same colour
inside the art (cream clouds, petals, lettering inside outlines) stay. A thin band around
the cut gets a soft alpha ramp and the background colour is un-blended from those pixels,
so edges stay crisp with no paper/black halo.
"""
import argparse
import numpy as np
from PIL import Image
from scipy import ndimage

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--max", type=int, default=4500, help="longest side of the print file")
ap.add_argument("--tol", type=float, default=0, help="background match distance (0 = auto)")
ap.add_argument("--soft", type=float, default=0, help="alpha ramp width (0 = auto)")
ap.add_argument("--pockets", action="store_true", help="also remove enclosed pockets of paper colour")
ap.add_argument("--min-blob", type=int, default=0, help="drop opaque specks smaller than this (px, at output size)")
a = ap.parse_args()

im = Image.open(a.src).convert("RGB")
s = a.max / max(im.size)
if s < 1:
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
px = np.asarray(im).astype(np.float32)
H, W, _ = px.shape

edge = np.concatenate([px[:8].reshape(-1, 3), px[-8:].reshape(-1, 3), px[:, :8].reshape(-1, 3), px[:, -8:].reshape(-1, 3)])
bg = np.median(edge, 0)
dark = bg.mean() < 128
dist = np.sqrt(((px - bg) ** 2).sum(2))
spread = np.percentile(np.sqrt(((edge - bg) ** 2).sum(1)), 97)
tol = a.tol or max(18.0, spread * 1.6)
soft = a.soft or (70.0 if dark else 55.0)

# Background = pixels close to the paper colour that touch the image border.
near = dist < tol
lab, _ = ndimage.label(near)
border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
border = border[border > 0]
bgmask = np.isin(lab, border)
# Small enclosed holes of paper colour fully surrounded by background (e.g. gaps in
# the paper texture) are background too; real enclosed art areas are far bigger.
holes = ndimage.binary_fill_holes(bgmask) & ~bgmask
hl, hn = ndimage.label(holes)
if hn:
    sizes = ndimage.sum(holes, hl, range(1, hn + 1))
    tiny = np.isin(hl, np.where(sizes < (H * W) * 2e-6)[0] + 1)
    bgmask |= tiny

# Enclosed pockets of paper (gaps between drips, inside a wireframe): flat regions whose
# average colour is the paper colour itself. White highlights in chrome or cream art are a
# different tint, so their average sits further from the paper colour and they stay.
if a.pockets:
    tight = dist < 12
    pl, pn = ndimage.label(tight)
    if pn:
        idx = np.arange(1, pn + 1)
        sizes = ndimage.sum(tight, pl, idx)
        means = np.stack([ndimage.mean(px[..., c], pl, idx) for c in range(3)], 1)
        mdist = np.sqrt(((means - bg) ** 2).sum(1))
        # Paper is warm (red above blue); chrome highlights are neutral white. Match on the tint.
        warm = means[:, 0] - means[:, 2]
        keep = idx[(sizes > H * W * 1.8e-4) & (mdist < 6) & (np.abs(warm - (bg[0] - bg[2])) < 2.5)]
        pocket = np.isin(pl, keep) & ~bgmask
        bgmask |= ndimage.binary_dilation(pocket, iterations=1) & near

alpha = np.ones((H, W), np.float32)
alpha[bgmask] = 0
band = ndimage.binary_dilation(bgmask, iterations=3) & ~bgmask
ramp = np.clip((dist - tol) / soft, 0, 1)
alpha[band] = np.minimum(alpha[band], ramp[band])

# Un-blend the background colour from partially transparent pixels.
part = (alpha > 0) & (alpha < 1)
ap_ = alpha[part][:, None]
px[part] = np.clip((px[part] - (1 - ap_) * bg) / np.maximum(ap_, 1e-3), 0, 255)

if a.min_blob:
    solid = alpha > 0.5
    bl, bn = ndimage.label(solid)
    if bn:
        sizes = ndimage.sum(solid, bl, range(1, bn + 1))
        drop = np.isin(bl, np.where(sizes < a.min_blob)[0] + 1)
        alpha[drop] = 0

rgba = np.dstack([px, alpha * 255]).round().clip(0, 255).astype(np.uint8)
out = Image.fromarray(rgba, "RGBA")
out = out.crop(out.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
out.save(a.out, dpi=(300, 300), optimize=True)
print(f"{a.out}: {out.size[0]}x{out.size[1]} bg={bg.round()} tol={tol:.0f} "
      f"{out.size[0] / 300:.1f}x{out.size[1] / 300:.1f} in at 300 DPI")
