"""Can cooler (Printify bp951, Pic The Gift) print sheets (2026-11-18). The sheet folds in half: top half = front
(upright, with the bottom tab at its foot), bottom half = back (upside down). Each design is centred on the body of
both sides, clear of the tab, on a solid background. Usage: python3 printify/koozie_art.py ART.png BG OUT_PREFIX
BG is a hex colour; writes OUT_PREFIX-regular.png (1425x3300) and OUT_PREFIX-slim.png (1382x4161)."""
import sys
from PIL import Image

SIZES = {"regular": (1425, 3300, 0.40, 0.60), "slim": (1382, 4161, 0.42, 0.64)}   # w, h, centre y, max art height (fractions of a half)


def sheet(art, bg, w, h, cy, maxh):
    half = h // 2
    art = art.crop(art.getbbox())
    s = min(0.84 * w / art.width, maxh * half / art.height)
    a = art.resize((int(art.width * s), int(art.height * s)), Image.LANCZOS)
    panel = Image.new("RGBA", (w, half), bg)
    panel.alpha_composite(a, ((w - a.width) // 2, int(cy * half - a.height / 2)))
    out = Image.new("RGBA", (w, h), bg)
    out.alpha_composite(panel, (0, 0))
    out.alpha_composite(panel.rotate(180), (0, h - half))
    return out.convert("RGB")


art = Image.open(sys.argv[1]).convert("RGBA")
bg = sys.argv[2]
for name, (w, h, cy, maxh) in SIZES.items():
    sheet(art, bg, w, h, cy, maxh).save(f"{sys.argv[3]}-{name}.png")
