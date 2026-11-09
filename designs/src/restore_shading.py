"""Put the dark shading back inside keyed-out art so it prints on colored fabric.

The Christmas back prints were made by turning every near-black pixel transparent, which also emptied the
shadows inside the art: fine on a black hoodie, but on maroon or green the fabric shows through. This keeps the
background outside the art transparent and fills everything inside the art's outline with black under the art,
fading over a few pixels at the outline so the edge stays soft.
usage: restore_shading.py IN OUT"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

src, out = sys.argv[1:3]
im = Image.open(src).convert("RGBA")
a = np.asarray(im).astype(np.float32) / 255
alpha = a[..., 3]
solid = alpha > 0.25
r = max(4, round(min(alpha.shape) / 250))                      # close gaps between bits of the art
inside = ndimage.binary_closing(solid, structure=np.ones((3, 3)), iterations=r)
inside = ndimage.binary_fill_holes(inside)
inside = ndimage.binary_erosion(inside, iterations=max(1, r // 3))
soft = ndimage.gaussian_filter(inside.astype(np.float32), sigma=r * 0.6)
new_alpha = np.maximum(alpha, np.clip(soft * 1.15, 0, 1))
rgb = a[..., :3] * alpha[..., None]                             # art over black
outa = np.dstack([rgb / np.maximum(new_alpha, 1e-6)[..., None], new_alpha])
Image.fromarray((np.clip(outa, 0, 1) * 255).round().astype(np.uint8), "RGBA").save(out, optimize=True)
print(out, im.size, "filled %.0f%% of the art area" % (100 * (inside & ~solid).sum() / max(inside.sum(), 1)))
