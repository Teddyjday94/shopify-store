"""Fix misspelled / garbled text in the drop-2 print files.

Edits are made on the 4x print files in designs/print-drop2, which are upscaled from the
1000x1333 originals; coordinates below are measured on those originals and scaled by S.
Each fix erases only the old text pixels (so the ink texture and glitch streaks behind them
survive), then redraws the text in a matching font.

Usage: python3 designs/src/fix_drop2_text.py <path-to-Noto-Serif-JP-800.ttf> [fix ...]
(fixes: systems, error, skull, calmer, same-mind; default all, starting from fresh 4x files)
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PRINT = ROOT / "designs" / "print-drop2"
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"
S = 4  # print files are 4x the measured originals

OFF_WHITE = (232, 228, 220, 255)
CREAM = (236, 222, 196, 255)
INK = (14, 13, 12, 255)
SEAL_RED = (226, 52, 40, 255)


def erase(im, x0, y0, x1, y1, kind, grow=9):
    """Paint INK over light ('light') or red ('red') pixels inside a box, slightly grown."""
    region = (x0 * S, y0 * S, x1 * S, y1 * S)
    a = np.asarray(im.crop(region)).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    if kind == "light":
        hit = (r > 120) & (g > 120) & (b > 110) & (al > 60)
    elif kind == "not-black":
        hit = ((r + g + b) > 3 * 22) & (al > 60)
    else:
        hit = (r > 150) & (g < 110) & (b < 110) & (al > 60)
    mask = np.asarray(Image.fromarray((hit * 255).astype("uint8")).filter(ImageFilter.MaxFilter(grow))) > 0
    # Darken the color only; keep each pixel's alpha so feathered ink edges stay soft.
    a[mask, :3] = INK[:3]
    im.paste(Image.fromarray(a.astype("uint8"), "RGBA"), region[:2])


def mono_lines(draw, x, y_centers, lines, advance, fill):
    """Draw monospace lines whose character advance matches the original (in original px)."""
    font = ImageFont.truetype(MONO, round(advance * S / 0.6))
    for y, text in zip(y_centers, lines):
        draw.text((x * S, y * S), text, font=font, fill=fill, anchor="lm")


def vertical(draw, font_path, cx, y0, y1, chars, size, fill):
    font = ImageFont.truetype(font_path, round(size * S))
    step = (y1 - y0) / len(chars)
    for i, ch in enumerate(chars):
        draw.text((cx * S, (y0 + step * (i + 0.5)) * S), ch, font=font, fill=fill, anchor="mm")


def fix_systems():
    path = PRINT / "06-back-systems-still-functional.png"
    im = Image.open(path).convert("RGBA")
    # Top-right terminal block, redrawn whole.
    erase(im, 806, 213, 950, 281, "light")
    d = ImageDraw.Draw(im)
    mono_lines(d, 809, [222, 239, 256, 272],
               ["> BOOT SEQUENCE...OK", "> MEMORY CHECK...OK", "> ANOMALIES DETECTED", "> CONTINUE? [Y/N]"],
               advance=6.9, fill=OFF_WHITE)
    # "MORAL: LOW" -> "MORALE: LOW".
    erase(im, 722, 427, 834, 449, "light")
    mono_lines(d, 725, [437.5], ["MORALE: LOW"], advance=9.6, fill=OFF_WHITE)
    im.save(path, optimize=True)


def fix_error():
    path = PRINT / "06-front-error-skull.png"
    im = Image.open(path).convert("RGBA")
    erase(im, 327, 922, 404, 1018, "light")
    d = ImageDraw.Draw(im)
    mono_lines(d, 330, [934, 958, 982, 1006], ["504", "OFFLINE", "RETRY", "TIMEOUT"],
               advance=10.2, fill=OFF_WHITE)
    im.save(path, optimize=True)


def reseal(im, font_path, x0, y0, x1, y1, border, chars, size):
    """Redraw a two-character vertical seal, keeping its red frame."""
    erase(im, x0 + border, y0 + border, x1 - border, y1 - border, "red", grow=7)
    vertical(ImageDraw.Draw(im), font_path, (x0 + x1) / 2, y0 + border, y1 - border, chars, size, SEAL_RED)


def fix_skull(font_path):
    path = PRINT / "04-front-sumi-ink-skull-mountain-landscape.png"
    im = Image.open(path).convert("RGBA")
    # Two boxes: the top one stays clear of the skull's crack lines on the left.
    erase(im, 764, 893, 838, 990, "not-black", grow=13)
    erase(im, 750, 990, 842, 1124, "not-black", grow=13)
    vertical(ImageDraw.Draw(im), font_path, 793, 900, 1112, "無常", 62, CREAM)
    reseal(im, font_path, 762, 1130, 822, 1219, 6, "静心", 30)
    im.save(path, optimize=True)


def fix_calmer(font_path):
    path = PRINT / "04-back-calmer-place-mountain-landscape.png"
    im = Image.open(path).convert("RGBA")
    reseal(im, font_path, 772, 585, 808, 644, 4, "静心", 21)
    im.save(path, optimize=True)


def fix_same_mind(font_path):
    """Replace the illegible 2x2 seal under 平常心 with 明鏡止水 ("clear mirror, still water")."""
    path = PRINT / "02-back-sakura-moon-same-mind-brighter-days.png"
    im = Image.open(path).convert("RGBA")
    # The seal is red ink on a transparent background: clear the old characters inside the frame.
    x0, y0, x1, y1 = 164, 804, 247, 919
    region = (x0 * S, y0 * S, x1 * S, y1 * S)
    a = np.asarray(im.crop(region)).copy()
    old = (a[..., 0] > 120) & (a[..., 1] < 120) & (a[..., 3] > 30)
    grown = np.asarray(Image.fromarray((old * 255).astype("uint8")).filter(ImageFilter.MaxFilter(9))) > 0
    a[grown, 3] = 0
    im.paste(Image.fromarray(a, "RGBA"), region[:2])

    # Draw the new characters on their own layer, read right column first (top to bottom).
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    font = ImageFont.truetype(font_path, 37 * S)
    d = ImageDraw.Draw(layer)
    cols = {x1 - (x1 - x0) / 4: "明鏡", x0 + (x1 - x0) / 4: "止水"}
    for cx, chars in cols.items():
        for i, ch in enumerate(chars):
            cy = y0 + (y1 - y0) * (0.27 + 0.48 * i)
            d.text((cx * S, cy * S), ch, font=font, fill=SEAL_RED, anchor="mm")
    # Rough up the edges like a rubber stamp so it matches the frame around it.
    rng = np.random.default_rng(67)
    la = np.asarray(layer).copy()
    speckle = rng.random(la.shape[:2]) < 0.12
    la[speckle, 3] = (la[speckle, 3] * 0.35).astype("uint8")
    im.alpha_composite(Image.fromarray(la, "RGBA"))
    im.save(path, optimize=True)


FIXES = {"systems": fix_systems, "error": fix_error, "skull": fix_skull,
         "calmer": fix_calmer, "same-mind": fix_same_mind}

if __name__ == "__main__":
    jp_font, *names = sys.argv[1:]
    for name in names or FIXES:
        fn = FIXES[name]
        fn(jp_font) if fn.__code__.co_argcount else fn()
        print("fixed", name)
