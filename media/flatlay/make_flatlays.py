"""Streetwear flat-lay photos (2026-11-17): our Printify flat tee mockups cut out from their white background and
laid on a generated cracked-concrete floor with soft shadows. Usage: python3 make_flatlays.py SRC_DIR OUT_DIR"""
import sys, math, random
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(7); random.seed(7)


def cutout(path):
    im = Image.open(path).convert("RGB"); a = np.asarray(im).astype(np.int16)
    whiteish = (a.min(2) > 244) & ((a.max(2) - a.min(2)) < 6)
    lab, _ = ndimage.label(whiteish)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    fg = ~bg
    fg = ndimage.binary_opening(fg, iterations=2)
    fg = ndimage.binary_fill_holes(fg)
    lab2, n2 = ndimage.label(fg)                      # keep the shirt only, not stray specks
    if n2 > 1:
        sizes = ndimage.sum(fg, lab2, range(1, n2 + 1)); fg = lab2 == (np.argmax(sizes) + 1)
    fg = ndimage.binary_erosion(fg, iterations=8)     # drop the pale anti-aliased fringe
    alpha = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))
    rgba = im.convert("RGBA"); rgba.putalpha(alpha)
    return rgba.crop(rgba.getbbox())


def concrete(w, h):
    def noise(scale):
        small = rng.normal(0, 1, (h // scale + 2, w // scale + 2))
        return np.asarray(Image.fromarray(small.astype(np.float32)).resize((w, h), Image.BICUBIC))
    n = 0.45 * noise(320) + 0.30 * noise(90) + 0.25 * noise(20) + 0.35 * noise(4) + 0.25 * noise(1)
    base = 146 + 9 * n
    spots = (noise(6) > 2.2) * -10.0                  # small pits like poured concrete
    base = base + spots
    yy, xx = np.mgrid[0:h, 0:w]
    vign = 1 - 0.08 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    g = np.clip(base * vign, 0, 255)
    img = np.stack([g * 0.99, g * 1.0, g * 1.02], 2).clip(0, 255).astype(np.uint8)
    out = Image.fromarray(img)
    d = ImageDraw.Draw(out)
    for _ in range(2):  # hairline cracks with a lighter lip
        x, y = random.uniform(0, w), random.uniform(0, h * 0.3); ang = random.uniform(1.1, 2.0)
        pts = [(x, y)]
        for _ in range(90):
            ang += random.uniform(-0.45, 0.45); x += 14 * math.cos(ang); y += 14 * math.sin(ang); pts.append((x, y))
        d.line([(px + 2, py + 2) for px, py in pts], fill=(165, 166, 168), width=2)
        d.line(pts, fill=(96, 97, 99), width=2)
    return out.filter(ImageFilter.GaussianBlur(0.7))


def place(canvas, tee, cx, cy, width, angle):
    t = tee.resize((int(width), int(tee.height * width / tee.width)), Image.LANCZOS).rotate(angle, Image.BICUBIC, expand=True)
    a = t.split()[-1]
    sh = Image.new("RGBA", t.size, (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: int(v * 0.55)))
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    x, y = int(cx - t.width / 2), int(cy - t.height / 2)
    canvas.alpha_composite(sh, (x + 14, y + 22))
    canvas.alpha_composite(t, (x, y))


tees = {k: cutout(SRC / f) for k, f in {
    "black": "elsewhere-ransom-note-tee-Black-102044.jpg",
    "natural": "elsewhere-chrome-globe-tee-Natural-102044.jpg",
    "forest": "elsewhere-chrome-script-tee-Forest-102044.jpg",
    "autumn": "elsewhere-groovy-retro-tee-Autumn-102044.jpg",
    "maroon": "elsewhere-psychedelic-drip-tee-Maroon-102044.jpg"}.items()}

# 1. 2x2 grid, slightly overhead, small tilts
W = H = 2048
c = concrete(W, H).convert("RGBA")
for (k, cx, cy, ang) in [("black", 545, 560, 1.5), ("natural", 1500, 545, -1), ("forest", 540, 1500, -1.5), ("autumn", 1505, 1490, 1)]:
    place(c, tees[k], cx, cy, 900, ang)
c.convert("RGB").save(OUT / "flatlay-grid.jpg", quality=90)

# 2. Fanned stack, cropped off the right edge
c = concrete(1700, 3000).convert("RGBA")
for i, k in enumerate(["natural", "autumn", "forest", "black"]):   # top first; each next shirt overlaps the one above
    place(c, tees[k], 820 + i * 35, 620 + i * 640, 1350, -4 + i * 1.2)
c = c.crop((50, 0, 1650, 2000))
c.convert("RGB").save(OUT / "flatlay-stack.jpg", quality=90)

# 3. Close-up: natural tee over the maroon tee, zoomed on the print
c = concrete(3000, 3600).convert("RGBA")
place(c, tees["maroon"], 1450, 3500, 4200, 5)
place(c, tees["natural"], 1520, 1150, 3500, -4)
c.crop((420, 300, 2660, 3100)).resize((1600, 2000), Image.LANCZOS).convert("RGB").save(OUT / "flatlay-closeup.jpg", quality=90)
print("done")
