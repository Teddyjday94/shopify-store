from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "media" / "doom-promo-photos"
OUT = Path(__file__).resolve().parent

W, H = 1080, 1350
SW, SH = 1080, 1920

WHITE = (247, 247, 242)
GREEN = (160, 226, 84)
BLACK = (8, 10, 8)
MUTED = (200, 204, 195)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(path, size):
    return ImageFont.truetype(path, size=size)


def cover(img, size, focal_x=0.5, focal_y=0.5):
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = int((nw - tw) * focal_x)
    top = int((nh - th) * focal_y)
    left = max(0, min(left, nw - tw))
    top = max(0, min(top, nh - th))
    return img.crop((left, top, left + tw, top + th))


def load(name, size=(W, H), focal_x=0.5, focal_y=0.5):
    img = Image.open(SOURCE / name).convert("RGB")
    img = cover(img, size, focal_x, focal_y)
    img = ImageEnhance.Contrast(img).enhance(1.025)
    img = ImageEnhance.Color(img).enhance(0.96)
    return img


def gradient_overlay(img, top_alpha=0, bottom_alpha=210, top_stop=0.30):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    px = overlay.load()
    for y in range(img.height):
        t = y / max(1, img.height - 1)
        if t < top_stop:
            a = top_alpha
        else:
            u = (t - top_stop) / (1 - top_stop)
            a = round(top_alpha + (bottom_alpha - top_alpha) * (u ** 1.65))
        for x in range(img.width):
            px[x, y] = (0, 0, 0, a)
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def top_gradient(img, strength=210, reach=0.46):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    steps = int(img.height * reach)
    for y in range(steps):
        u = y / max(1, steps - 1)
        a = round(strength * ((1 - u) ** 1.8))
        draw.line((0, y, img.width, y), fill=(0, 0, 0, a))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def add_grain(img, amount=8, opacity=0.10, seed=94):
    random.seed(seed)
    noise = Image.new("L", img.size)
    data = [max(0, min(255, 128 + random.randint(-amount, amount))) for _ in range(img.width * img.height)]
    noise.putdata(data)
    noise = noise.filter(ImageFilter.GaussianBlur(0.25))
    grain = Image.merge("RGBA", (noise, noise, noise, Image.new("L", img.size, int(255 * opacity))))
    return Image.blend(img.convert("RGBA"), grain, opacity)


def tracking_text(draw, xy, text, typeface, fill, tracking=3, anchor="la"):
    x, y = xy
    widths = [draw.textlength(c, font=typeface) for c in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    if anchor.startswith("m"):
        x -= total / 2
    elif anchor.startswith("r"):
        x -= total
    for c, width in zip(text, widths):
        draw.text((x, y), c, font=typeface, fill=fill, anchor="la")
        x += width + tracking


def label(draw, x, y, text, width=None):
    f = font(FONT_MONO, 24)
    pad_x, pad_y = 14, 9
    tw = draw.textlength(text, font=f)
    box_w = width or int(tw + pad_x * 2)
    draw.rounded_rectangle((x, y, x + box_w, y + 47), radius=3, fill=GREEN)
    draw.text((x + pad_x, y + 9), text, font=f, fill=BLACK)


def brand_footer(draw, height, number=None):
    y = height - 58
    tracking_text(draw, (52, y), "ELSEWHERE APPAREL CO.", font(FONT_BOLD, 21), WHITE, tracking=2)
    if number:
        tracking_text(draw, (1028, y), number, font(FONT_MONO, 20), WHITE, tracking=1, anchor="ra")


def save(img, name):
    img = img.convert("RGB")
    img.save(OUT / name, "JPEG", quality=94, subsampling=0, optimize=True)


def slide_1():
    img = load("17-d-crest-varsity-jacket-two-friends-lobby.png", focal_y=0.42)
    img = top_gradient(img, 225, 0.48)
    img = gradient_overlay(img, 0, 140, 0.62)
    draw = ImageDraw.Draw(img)
    label(draw, 52, 52, "LIMITED RUN")
    draw.text((50, 132), "THE", font=font(FONT_BOLD, 67), fill=WHITE)
    draw.text((45, 188), "DOOMSDAY", font=font(FONT_BOLD, 126), fill=WHITE, stroke_width=1, stroke_fill=WHITE)
    draw.text((48, 300), "DROP", font=font(FONT_BOLD, 126), fill=GREEN, stroke_width=1, stroke_fill=GREEN)
    tracking_text(draw, (54, 423), "NOV 25 — DEC 18, 2026", font(FONT_MONO, 25), WHITE, tracking=2)
    brand_footer(draw, H, "01 / 05")
    save(add_grain(img), "carousel-01-launch.jpg")


def slide_2():
    img = load("04-crest-tee-theater-hallway-group.png", focal_y=0.42)
    img = gradient_overlay(img, 0, 215, 0.44)
    draw = ImageDraw.Draw(img)
    label(draw, 52, 52, "D CREST TEE")
    draw.text((48, 1010), "MADE FOR", font=font(FONT_BOLD, 63), fill=WHITE)
    draw.text((45, 1060), "THE NIGHT OUT.", font=font(FONT_BOLD, 91), fill=GREEN)
    tracking_text(draw, (54, 1165), "ORIGINAL ELSEWHERE ARTWORK", font(FONT_MONO, 22), MUTED, tracking=2)
    brand_footer(draw, H, "02 / 05")
    save(add_grain(img, seed=95), "carousel-02-d-crest-tee.jpg")


def slide_3():
    img = load("08-king-of-the-3-realms-hoodie-theater-seats.png", focal_y=0.44)
    img = gradient_overlay(img, 0, 220, 0.40)
    draw = ImageDraw.Draw(img)
    label(draw, 52, 52, "KING OF THE 3 REALMS")
    draw.text((49, 1010), "THE HOODIE", font=font(FONT_BOLD, 67), fill=WHITE)
    draw.text((45, 1067), "GETS THE LAST WORD.", font=font(FONT_BOLD, 78), fill=GREEN)
    tracking_text(draw, (54, 1170), "BACK GRAPHIC • WASHED BLACK", font(FONT_MONO, 22), MUTED, tracking=2)
    brand_footer(draw, H, "03 / 05")
    save(add_grain(img, seed=96), "carousel-03-king-hoodie.jpg")


def slide_4():
    img = load("17-d-crest-varsity-jacket-two-friends-lobby.png", focal_x=0.52, focal_y=0.43)
    img = gradient_overlay(img, 0, 210, 0.51)
    draw = ImageDraw.Draw(img)
    label(draw, 52, 52, "D CREST VARSITY")
    draw.text((48, 1020), "FRONT.", font=font(FONT_BOLD, 82), fill=WHITE)
    draw.text((45, 1094), "BACK. FULL EFFECT.", font=font(FONT_BOLD, 82), fill=GREEN)
    tracking_text(draw, (54, 1194), "GREEN / CREAM • STATEMENT CREST", font(FONT_MONO, 21), MUTED, tracking=2)
    brand_footer(draw, H, "04 / 05")
    save(add_grain(img, seed=97), "carousel-04-varsity.jpg")


def slide_5():
    img = load("12-rack-king-inevitable-stolen-life-crest-lobby.png", focal_y=0.47)
    veil = Image.new("RGBA", img.size, (5, 8, 5, 116))
    img = Image.alpha_composite(img.convert("RGBA"), veil)
    img = top_gradient(img, 190, 0.35)
    img = gradient_overlay(img, 30, 220, 0.34)
    draw = ImageDraw.Draw(img)
    tracking_text(draw, (540, 70), "THE DOOMSDAY DROP", font(FONT_MONO, 23), GREEN, tracking=3, anchor="ma")
    draw.text((540, 760), "THE DROP", font=font(FONT_BOLD, 112), fill=WHITE, anchor="ma")
    draw.text((540, 862), "IS LIVE.", font=font(FONT_BOLD, 112), fill=GREEN, anchor="ma")
    tracking_text(draw, (540, 980), "LIMITED RUN • NOV 25 — DEC 18", font(FONT_MONO, 23), WHITE, tracking=2, anchor="ma")
    draw.rounded_rectangle((224, 1044, 856, 1129), radius=5, fill=WHITE)
    tracking_text(draw, (540, 1068), "ELSEWHEREAPPARELCO.COM", font(FONT_BOLD, 28), BLACK, tracking=2, anchor="ma")
    brand_footer(draw, H, "05 / 05")
    save(add_grain(img, seed=98), "carousel-05-shop-now.jpg")


def story():
    top = load("17-d-crest-varsity-jacket-two-friends-lobby.png", (SW, 1240), focal_y=0.42)
    bottom = load("12-rack-king-inevitable-stolen-life-crest-lobby.png", (SW, 680), focal_y=0.48)
    canvas = Image.new("RGB", (SW, SH), BLACK)
    canvas.paste(top, (0, 0))
    canvas.paste(bottom, (0, 1240))
    img = top_gradient(canvas, 225, 0.28)
    overlay = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 1112, SW, 1360), fill=(7, 9, 7, 235))
    od.rectangle((0, 1358, SW, 1364), fill=GREEN)
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    label(draw, 54, 72, "LIMITED RUN")
    draw.text((52, 150), "DOOMSDAY", font=font(FONT_BOLD, 112), fill=WHITE)
    draw.text((49, 250), "DROP", font=font(FONT_BOLD, 132), fill=GREEN)
    tracking_text(draw, (55, 382), "NOV 25 — DEC 18, 2026", font(FONT_MONO, 25), WHITE, tracking=2)
    tracking_text(draw, (540, 1160), "THE COLLECTION IS LIVE", font(FONT_BOLD, 35), WHITE, tracking=2, anchor="ma")
    tracking_text(draw, (540, 1221), "SHOP ELSEWHEREAPPARELCO.COM", font(FONT_MONO, 24), GREEN, tracking=2, anchor="ma")
    tracking_text(draw, (54, 1846), "ELSEWHERE APPAREL CO.", font(FONT_BOLD, 22), WHITE, tracking=2)
    save(add_grain(img, seed=99), "story-launch-1080x1920.jpg")


def reel_cover():
    img = load("18-d-crest-varsity-jacket-back-theater-hallway.png", (SW, SH), focal_y=0.40)
    img = top_gradient(img, 222, 0.34)
    img = gradient_overlay(img, 0, 155, 0.66)
    draw = ImageDraw.Draw(img)
    tracking_text(draw, (540, 110), "ELSEWHERE APPAREL CO.", font(FONT_BOLD, 22), WHITE, tracking=3, anchor="ma")
    draw.text((540, 260), "DOOMSDAY", font=font(FONT_BOLD, 106), fill=WHITE, anchor="ma")
    draw.text((540, 365), "DROP", font=font(FONT_BOLD, 138), fill=GREEN, anchor="ma")
    tracking_text(draw, (540, 500), "LIMITED RUN", font(FONT_MONO, 27), WHITE, tracking=4, anchor="ma")
    tracking_text(draw, (540, 1732), "NOV 25 — DEC 18", font(FONT_MONO, 25), WHITE, tracking=3, anchor="ma")
    save(add_grain(img, seed=100), "reel-cover-varsity-1080x1920.jpg")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    slide_1()
    slide_2()
    slide_3()
    slide_4()
    slide_5()
    story()
    reel_cover()
