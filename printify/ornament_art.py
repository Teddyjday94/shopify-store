"""Round-ornament art (2026-11-18): every design fits inside the circle (clear of the hanging hole) and the
background is a soft blurred glow of the design's own colours instead of flat black.
Graphic designs only; the full-bleed paintings already fill the ornament.
Usage: python3 printify/ornament_art.py SRC_DIR OUT_DIR   (SRC_DIR/<printify id>_src.png + info.json)"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(exist_ok=True)
N = 1908                      # print file size (Printify circle placeholder 954 px, printed at 2x)
SAFE = 0.85                   # every visible art pixel within 80% of the radius
CY = 0.53                     # nudge art below centre, away from the hanging hole


def glow_background(art):
    rgb = Image.new("RGB", art.size, (0, 0, 0)); rgb.paste(art, mask=art.split()[-1])
    a = np.asarray(art.split()[-1], dtype=np.float32) / 255
    # average colour of the art, used where the blurred art is thin
    px = np.asarray(art.convert("RGB"), dtype=np.float32)[a > 0.5]
    mean = tuple(int(v) for v in px.mean(0))
    big = rgb.resize((N, N), Image.LANCZOS) if rgb.width >= rgb.height else rgb.resize((N, N), Image.LANCZOS)
    bg = Image.new("RGB", (N, N), tuple(int(c * 0.55) for c in mean))
    blur = big.filter(ImageFilter.GaussianBlur(150)).filter(ImageFilter.GaussianBlur(60))
    bg = Image.blend(bg, blur, 0.8)
    bg = ImageEnhance.Color(bg).enhance(1.7)
    bg = ImageEnhance.Brightness(bg).enhance(0.85)
    # gentle radial lift in the middle so the art pops
    yy, xx = np.mgrid[0:N, 0:N]
    r = np.sqrt((xx - N / 2) ** 2 + (yy - N * CY) ** 2) / (N / 2)
    lift = (1.15 - 0.35 * np.clip(r, 0, 1))[..., None]
    out = np.clip(np.asarray(bg, dtype=np.float32) * lift, 0, 255).astype(np.uint8)
    return Image.fromarray(out)


def fit(art):
    art = art.crop(art.getbbox())
    a = np.asarray(art.split()[-1]) > 40
    ys, xs = np.nonzero(a)
    cx, cy = art.width / 2, art.height / 2
    reach = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2).max()     # farthest visible pixel from the art centre
    scale = (SAFE * N / 2) / reach
    return art.resize((int(art.width * scale), int(art.height * scale)), Image.LANCZOS)


def text_background():
    yy, xx = np.mgrid[0:N, 0:N]
    t = np.clip(np.sqrt((xx - N / 2) ** 2 + (yy - N * CY) ** 2) / (N * 0.6), 0, 1)[..., None]
    inner, outer = np.array([74, 52, 120]), np.array([28, 22, 58])     # dusk purple, not black
    return Image.fromarray((inner * (1 - t) + outer * t).astype(np.uint8))


info = json.load(open(SRC / "info.json"))
for title, v in info.items():
    f = SRC / f"{v['id']}_src.png"
    if not f.exists():
        continue
    art = Image.open(f).convert("RGBA")
    if title.startswith("Not AI"):            # the tee file is black ink; the ornament needs it light
        white = Image.new("RGBA", art.size, (245, 240, 232, 255)); white.putalpha(art.split()[-1]); art = white
    bg = text_background() if title.startswith("Not AI") else glow_background(art.crop(art.getbbox()))
    a = fit(art)
    canvas = bg.convert("RGBA")
    canvas.alpha_composite(a, (int(N / 2 - a.width / 2), int(N * CY - a.height / 2)))
    name = "ornament-" + v["art"].replace("ornament-", "").replace(".jpg", "") + "-v2.png"
    canvas.convert("RGB").save(OUT / name)
    v["new_art"] = name
    # preview: what shows on the round ornament
    pv = canvas.convert("RGB").resize((400, 400))
    m = Image.new("L", (400, 400), 0); ImageDraw.Draw(m).ellipse((0, 0, 399, 399), fill=255)
    ImageDraw.Draw(m).ellipse((190, 14, 210, 34), fill=0)                     # hanging hole
    prev = Image.new("RGB", (400, 400), "white"); prev.paste(pv, mask=m)
    prev.save(OUT / name.replace(".png", "-preview.jpg"))
    print(title, "->", name)
json.dump(info, open(SRC / "info.json", "w"), indent=1)
