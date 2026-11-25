from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "media" / "doom-promo-photos"
OUT = Path(__file__).resolve().parent

W, H = 1080, 1350
SW, SH = 1080, 1920

BLACK = (7, 10, 8)
CHARCOAL = (14, 18, 15)
PANEL = (20, 25, 21)
WHITE = (244, 244, 236)
MUTED = (157, 165, 153)
GREEN = (177, 255, 82)
DEEP_GREEN = (37, 78, 48)

SERIF = "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Regular.otf"
SERIF_ITALIC = "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Italic.otf"
SERIF_BOLD = "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Bold.otf"
SANS = "/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Regular.otf"
SANS_BOLD = "/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Bold.otf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def f(path, size):
    return ImageFont.truetype(path, size=size)


def cover(image, size, focal_x=0.5, focal_y=0.5):
    tw, th = size
    scale = max(tw / image.width, th / image.height)
    nw, nh = round(image.width * scale), round(image.height * scale)
    image = image.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, min(round((nw - tw) * focal_x), nw - tw))
    top = max(0, min(round((nh - th) * focal_y), nh - th))
    return image.crop((left, top, left + tw, top + th))


def photo(name, size, focal_x=0.5, focal_y=0.5):
    return cover(Image.open(SOURCE / name).convert("RGB"), size, focal_x, focal_y)


def darken(image, alpha=65):
    veil = Image.new("RGBA", image.size, (2, 7, 3, alpha))
    return Image.alpha_composite(image.convert("RGBA"), veil)


def tracked(draw, xy, text, typeface, fill=WHITE, tracking=2, anchor="la"):
    x, y = xy
    widths = [draw.textlength(char, font=typeface) for char in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    if anchor.startswith("m"):
        x -= total / 2
    elif anchor.startswith("r"):
        x -= total
    for char, width in zip(text, widths):
        draw.text((x, y), char, font=typeface, fill=fill, anchor="la")
        x += width + tracking


def glow_text(image, xy, text, typeface, fill=GREEN, anchor="la", blur=16, glow_alpha=210):
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text(xy, text, font=typeface, fill=(*fill, glow_alpha), anchor=anchor)
    soft = glow.filter(ImageFilter.GaussianBlur(blur))
    image.alpha_composite(soft)
    draw = ImageDraw.Draw(image)
    draw.text(xy, text, font=typeface, fill=fill, anchor=anchor)


def glow_tracked(image, xy, text, typeface, fill=GREEN, tracking=3, anchor="la", blur=12):
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    tracked(gd, xy, text, typeface, (*fill, 210), tracking, anchor)
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(blur)))
    tracked(ImageDraw.Draw(image), xy, text, typeface, fill, tracking, anchor)


def framed_paste(canvas, image, xy, border=1, color=(70, 86, 72)):
    x, y = xy
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((x - border, y - border, x + image.width + border, y + image.height + border), fill=color)
    canvas.paste(image, (x, y))


def header(draw, section, number, width=W):
    tracked(draw, (44, 36), "ELSEWHERE / DOOMSDAY EDITORIAL", f(SANS_BOLD, 18), WHITE, 3)
    tracked(draw, (width - 44, 36), number, f(MONO, 16), GREEN, 2, "ra")
    draw.line((44, 72, width - 44, 72), fill=(85, 96, 86), width=1)
    tracked(draw, (44, 91), section, f(SANS, 17), MUTED, 3)


def footer(draw, number):
    draw.line((44, 1288, 1036, 1288), fill=(75, 86, 76), width=1)
    tracked(draw, (44, 1302), "ELSEWHEREAPPARELCO.COM", f(SANS_BOLD, 17), WHITE, 3)
    tracked(draw, (1036, 1302), number, f(MONO, 15), GREEN, 2, "ra")


def save(image, name):
    image.convert("RGB").save(OUT / name, "JPEG", quality=95, subsampling=0, optimize=True)


def slide_1():
    canvas = Image.new("RGBA", (W, H), BLACK + (255,))
    hero = darken(photo("17-d-crest-varsity-jacket-two-friends-lobby.png", (720, 1080), 0.55, 0.43), 42)
    framed_paste(canvas, hero, (316, 124), 1)
    draw = ImageDraw.Draw(canvas)
    header(draw, "ISSUE 01 / AFTER DARK", "01 / 07")
    draw.text((42, 175), "The", font=f(SERIF_ITALIC, 70), fill=WHITE)
    draw.text((40, 246), "Doomsday", font=f(SERIF, 74), fill=WHITE)
    draw.text((42, 323), "Drop", font=f(SERIF_ITALIC, 101), fill=WHITE)
    glow_tracked(canvas, (45, 450), "AFTER DARK", f(SANS_BOLD, 25), GREEN, 5)
    draw.line((45, 504, 260, 504), fill=GREEN, width=2)
    draw.multiline_text((44, 533), "A cinematic study\nin original artwork,\nwashed black fabric\nand emerald light.", font=f(SANS, 23), fill=MUTED, spacing=10)
    glow_tracked(canvas, (344, 1138), "NOV 25 — DEC 18", f(MONO, 18), GREEN, 3)
    footer(draw, "01 / 07")
    save(canvas, "dark-carousel-01-cover.jpg")


def slide_2():
    canvas = Image.new("RGBA", (W, H), BLACK + (255,))
    main = photo("04-crest-tee-theater-hallway-group.png", (624, 1020), 0.5, 0.43)
    inset = photo("07-no-gods-only-doom-tee-concession-stand.png", (350, 586), 0.52, 0.43)
    framed_paste(canvas, main, (44, 150), 1)
    framed_paste(canvas, inset, (686, 472), 2, GREEN)
    draw = ImageDraw.Draw(canvas)
    header(draw, "THE NIGHT SHIFT / TEES", "02 / 07")
    draw.text((690, 148), "Two", font=f(SERIF_ITALIC, 60), fill=WHITE)
    draw.text((688, 210), "statements.", font=f(SERIF, 50), fill=WHITE)
    glow_text(canvas, (690, 292), "One night.", f(SERIF_ITALIC, 54), GREEN, blur=13)
    tracked(draw, (691, 374), "D CREST TEE", f(SANS_BOLD, 18), WHITE, 3)
    tracked(draw, (691, 406), "NO GODS, ONLY DOOM", f(SANS, 17), MUTED, 2)
    glow_tracked(canvas, (688, 1097), "ORIGINAL ARTWORK", f(MONO, 16), GREEN, 3)
    footer(draw, "02 / 07")
    save(canvas, "dark-carousel-02-night-shift.jpg")


def slide_3():
    canvas = Image.new("RGBA", (W, H), CHARCOAL + (255,))
    aisle = photo("03-king-of-the-3-realms-hoodie-theater-aisle.png", (480, 830), 0.5, 0.44)
    seats = photo("08-king-of-the-3-realms-hoodie-theater-seats.png", (480, 830), 0.5, 0.48)
    framed_paste(canvas, aisle, (44, 198), 1)
    framed_paste(canvas, seats, (556, 198), 1)
    draw = ImageDraw.Draw(canvas)
    header(draw, "BACK GRAPHICS / IN MOTION", "03 / 07")
    draw.text((44, 114), "King of the 3 Realms", font=f(SERIF_ITALIC, 52), fill=WHITE)
    glow_tracked(canvas, (44, 1068), "AISLE / SEAT / EXIT", f(SANS_BOLD, 21), GREEN, 4)
    draw.text((44, 1124), "The back graphic becomes the main event.", font=f(SERIF, 31), fill=WHITE)
    tracked(draw, (44, 1180), "WASHED BLACK HOODIE / FULL BACK PRINT", f(SANS, 18), MUTED, 3)
    footer(draw, "03 / 07")
    save(canvas, "dark-carousel-03-king-hoodie.jpg")


def slide_4():
    canvas = Image.new("RGBA", (W, H), BLACK + (255,))
    p1 = photo("09-flatlay-crest-no-gods-doom-in-our-time-recliners.png", (474, 448), 0.5, 0.5)
    p2 = photo("11-group-king-inevitable-stolen-life-crest-lounge-sofa.png", (474, 448), 0.5, 0.5)
    p3 = photo("12-rack-king-inevitable-stolen-life-crest-lobby.png", (474, 448), 0.5, 0.5)
    p4 = photo("13-flatlay-king-inevitable-stolen-life-crest.png", (474, 448), 0.5, 0.5)
    framed_paste(canvas, p1, (44, 164), 1)
    framed_paste(canvas, p2, (562, 164), 1)
    framed_paste(canvas, p3, (44, 642), 1)
    framed_paste(canvas, p4, (562, 642), 1)
    draw = ImageDraw.Draw(canvas)
    header(draw, "THE LINEUP / FOUR STUDIES", "04 / 07")
    draw.rectangle((250, 552, 830, 702), fill=(7, 10, 8, 235))
    draw.text((540, 570), "The full collection", font=f(SERIF_ITALIC, 55), fill=WHITE, anchor="ma")
    glow_tracked(canvas, (540, 650), "TOGETHER", f(SANS_BOLD, 23), GREEN, 5, "ma")
    tracked(draw, (44, 1128), "RECLINERS / LOUNGE / RACK / FLAT LAY", f(MONO, 16), MUTED, 3)
    footer(draw, "04 / 07")
    save(canvas, "dark-carousel-04-lineup.jpg")


def slide_5():
    canvas = Image.new("RGBA", (W, H), CHARCOAL + (255,))
    worn = photo("01-a-stolen-life-hoodie-sidewalk.png", (540, 980), 0.5, 0.45)
    bench = photo("02-a-stolen-life-tee-porch-bench.png", (410, 455), 0.5, 0.5)
    recliner = photo("10-a-stolen-life-tee-recliner.png", (410, 455), 0.5, 0.5)
    framed_paste(canvas, worn, (44, 166), 1)
    framed_paste(canvas, bench, (626, 166), 1)
    framed_paste(canvas, recliner, (626, 690), 1)
    draw = ImageDraw.Draw(canvas)
    header(draw, "A STOLEN LIFE / THREE VIEWS", "05 / 07")
    glow_text(canvas, (622, 635), "A Stolen Life", f(SERIF_ITALIC, 50), GREEN, blur=12)
    tracked(draw, (626, 1183), "HOODIE / TEE / DETAIL", f(SANS_BOLD, 18), WHITE, 3)
    footer(draw, "05 / 07")
    save(canvas, "dark-carousel-05-stolen-life.jpg")


def slide_6():
    canvas = Image.new("RGBA", (W, H), BLACK + (255,))
    names = [
        "14-crest-varsity-jacket-front.png",
        "15-crest-varsity-jacket-back.png",
        "16-crest-varsity-jacket-worn-concession.png",
        "18-d-crest-varsity-jacket-back-theater-hallway.png",
    ]
    coords = [(44, 186), (552, 186), (44, 688), (552, 688)]
    for name, xy in zip(names, coords):
        framed_paste(canvas, photo(name, (484, 466), 0.5, 0.47), xy, 1)
    draw = ImageDraw.Draw(canvas)
    header(draw, "D CREST VARSITY / OBJECT + MOTION", "06 / 07")
    draw.text((44, 112), "Front. Back. After dark.", font=f(SERIF_ITALIC, 48), fill=WHITE)
    glow_tracked(canvas, (540, 631), "D CREST VARSITY", f(SANS_BOLD, 22), GREEN, 5, "ma")
    tracked(draw, (44, 1194), "GREEN / CREAM / FULL-SCALE BACK CREST", f(MONO, 16), MUTED, 3)
    footer(draw, "06 / 07")
    save(canvas, "dark-carousel-06-varsity.jpg")


def slide_7():
    canvas = darken(photo("12-rack-king-inevitable-stolen-life-crest-lobby.png", (W, H), 0.5, 0.46), 120)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((44, 44, 1036, 1306), outline=(119, 141, 119), width=1)
    tracked(draw, (540, 88), "ELSEWHERE APPAREL CO. / LIMITED RUN", f(SANS_BOLD, 18), WHITE, 3, "ma")
    draw.text((540, 470), "The Drop", font=f(SERIF_ITALIC, 118), fill=WHITE, anchor="ma")
    glow_text(canvas, (540, 594), "is live.", f(SERIF, 99), GREEN, "ma", 22, 235)
    glow_tracked(canvas, (540, 734), "NOV 25 — DEC 18", f(MONO, 20), GREEN, 4, "ma", 14)
    draw.line((310, 798, 770, 798), fill=WHITE, width=1)
    tracked(draw, (540, 848), "ELSEWHEREAPPARELCO.COM", f(SANS_BOLD, 23), WHITE, 4, "ma")
    tracked(draw, (540, 1250), "07 / 07", f(MONO, 15), GREEN, 3, "ma")
    save(canvas, "dark-carousel-07-shop.jpg")


def story():
    canvas = Image.new("RGBA", (SW, SH), BLACK + (255,))
    hero = photo("17-d-crest-varsity-jacket-two-friends-lobby.png", (790, 1180), 0.53, 0.42)
    tee = photo("04-crest-tee-theater-hallway-group.png", (430, 500), 0.5, 0.45)
    rack = photo("12-rack-king-inevitable-stolen-life-crest-lobby.png", (540, 500), 0.5, 0.48)
    framed_paste(canvas, hero, (246, 206), 1)
    framed_paste(canvas, tee, (44, 1348), 1)
    framed_paste(canvas, rack, (496, 1348), 1)
    draw = ImageDraw.Draw(canvas)
    tracked(draw, (44, 50), "ELSEWHERE / EDITORIAL 01", f(SANS_BOLD, 18), WHITE, 3)
    draw.line((44, 88, 1036, 88), fill=(90, 103, 92), width=1)
    draw.text((42, 146), "The", font=f(SERIF_ITALIC, 65), fill=WHITE)
    draw.text((40, 211), "Doomsday", font=f(SERIF, 63), fill=WHITE)
    draw.text((42, 276), "Drop", font=f(SERIF_ITALIC, 86), fill=WHITE)
    glow_tracked(canvas, (45, 388), "AFTER DARK", f(SANS_BOLD, 22), GREEN, 5)
    draw.rectangle((44, 1118, 680, 1290), fill=(7, 10, 8, 230))
    draw.text((70, 1142), "Limited run", font=f(SERIF_ITALIC, 45), fill=WHITE)
    glow_tracked(canvas, (72, 1212), "NOV 25 — DEC 18", f(MONO, 18), GREEN, 3)
    tracked(draw, (540, 1875), "SHOP ELSEWHEREAPPARELCO.COM", f(SANS_BOLD, 19), WHITE, 3, "ma")
    save(canvas, "dark-story-1080x1920.jpg")


def reel_cover():
    canvas = darken(photo("18-d-crest-varsity-jacket-back-theater-hallway.png", (SW, SH), 0.5, 0.41), 52)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((42, 42, 1038, 1878), outline=(111, 132, 112), width=1)
    tracked(draw, (540, 80), "ELSEWHERE APPAREL CO.", f(SANS_BOLD, 18), WHITE, 4, "ma")
    draw.text((540, 242), "Doomsday", font=f(SERIF_ITALIC, 94), fill=WHITE, anchor="ma")
    glow_text(canvas, (540, 352), "after dark", f(SERIF, 82), GREEN, "ma", 19, 230)
    tracked(draw, (540, 464), "THE D CREST VARSITY", f(SANS_BOLD, 20), WHITE, 4, "ma")
    glow_tracked(canvas, (540, 1742), "LIMITED RUN / NOV 25 — DEC 18", f(MONO, 18), GREEN, 3, "ma")
    tracked(draw, (540, 1802), "ELSEWHEREAPPARELCO.COM", f(SANS_BOLD, 18), WHITE, 3, "ma")
    save(canvas, "dark-reel-cover-1080x1920.jpg")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    slide_1()
    slide_2()
    slide_3()
    slide_4()
    slide_5()
    slide_6()
    slide_7()
    story()
    reel_cover()
