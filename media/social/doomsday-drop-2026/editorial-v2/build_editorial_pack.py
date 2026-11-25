from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "media" / "doom-promo-photos"
OUT = Path(__file__).resolve().parent

W, H = 1080, 1350
SW, SH = 1080, 1920

PAPER = (242, 239, 229)
INK = (20, 22, 19)
WHITE = (248, 247, 241)
GREEN = (39, 76, 50)
SAGE = (177, 201, 146)
GRAY = (107, 111, 102)

SERIF = "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Regular.otf"
SERIF_ITALIC = "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Italic.otf"
SERIF_BOLD = "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Bold.otf"
SANS = "/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Regular.otf"
SANS_BOLD = "/usr/share/fonts/opentype/urw-base35/NimbusSansNarrow-Bold.otf"


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


def tracked(draw, xy, text, typeface, fill=INK, tracking=2, anchor="la"):
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


def folio(draw, number, dark=False):
    color = WHITE if dark else INK
    draw.line((54, 1287, 1026, 1287), fill=color, width=1)
    tracked(draw, (54, 1302), "ELSEWHERE APPAREL CO.", f(SANS_BOLD, 18), color, 2)
    tracked(draw, (1026, 1302), number, f(SANS, 18), color, 2, "ra")


def save(image, name):
    image.convert("RGB").save(OUT / name, "JPEG", quality=95, subsampling=0, optimize=True)


def slide_1():
    canvas = Image.new("RGB", (W, H), PAPER)
    hero = photo("17-d-crest-varsity-jacket-two-friends-lobby.png", (688, 990), 0.54, 0.42)
    canvas.paste(hero, (340, 130))
    draw = ImageDraw.Draw(canvas)
    tracked(draw, (54, 48), "ELSEWHERE / EDITORIAL 01", f(SANS_BOLD, 20), INK, 3)
    tracked(draw, (1026, 48), "NOV — DEC 2026", f(SANS, 19), INK, 2, "ra")
    draw.line((54, 90, 1026, 90), fill=INK, width=1)
    draw.text((49, 164), "The", font=f(SERIF_ITALIC, 72), fill=GREEN)
    draw.text((48, 238), "Doomsday", font=f(SERIF, 68), fill=INK)
    draw.text((52, 307), "Drop", font=f(SERIF_ITALIC, 98), fill=GREEN)
    draw.line((54, 436, 278, 436), fill=INK, width=2)
    draw.multiline_text((54, 468), "A limited-run study\nin graphic streetwear.", font=f(SANS, 25), fill=GRAY, spacing=9)
    draw.text((368, 1064), "Limited run", font=f(SERIF_ITALIC, 38), fill=PAPER)
    tracked(draw, (370, 1122), "NOV 25 — DEC 18", f(SANS_BOLD, 20), PAPER, 3)
    folio(draw, "01 / 05")
    save(canvas, "editorial-carousel-01-cover.jpg")


def slide_2():
    canvas = Image.new("RGB", (W, H), PAPER)
    main = photo("04-crest-tee-theater-hallway-group.png", (786, 1120), 0.50, 0.42)
    canvas.paste(main, (240, 78))
    draw = ImageDraw.Draw(canvas)
    tracked(draw, (54, 58), "LOOK 01", f(SANS_BOLD, 20), GREEN, 3)
    draw.text((52, 142), "D", font=f(SERIF_BOLD, 154), fill=INK)
    draw.text((56, 280), "Crest", font=f(SERIF_ITALIC, 57), fill=GREEN)
    draw.line((56, 366, 190, 366), fill=INK, width=1)
    tracked(draw, (57, 393), "THE TEE", f(SANS_BOLD, 20), INK, 3)
    draw.multiline_text((56, 440), "Washed black.\nStatement front.\nMade to move.", font=f(SANS, 23), fill=GRAY, spacing=10)
    tracked(draw, (260, 1216), "CINEMA LOBBY / AFTER DARK", f(SANS, 18), INK, 3)
    folio(draw, "02 / 05")
    save(canvas, "editorial-carousel-02-d-crest.jpg")


def slide_3():
    canvas = Image.new("RGB", (W, H), PAPER)
    top = photo("03-king-of-the-3-realms-hoodie-theater-aisle.png", (670, 560), 0.50, 0.45)
    bottom = photo("08-king-of-the-3-realms-hoodie-theater-seats.png", (670, 560), 0.50, 0.48)
    canvas.paste(top, (54, 78))
    canvas.paste(bottom, (356, 666))
    draw = ImageDraw.Draw(canvas)
    tracked(draw, (766, 87), "LOOK 02", f(SANS_BOLD, 20), GREEN, 3)
    draw.text((760, 145), "King", font=f(SERIF_ITALIC, 80), fill=INK)
    draw.text((760, 220), "of the", font=f(SERIF, 48), fill=GREEN)
    draw.text((760, 270), "3 Realms", font=f(SERIF_ITALIC, 65), fill=INK)
    draw.line((760, 360, 1026, 360), fill=INK, width=1)
    draw.multiline_text((760, 390), "The back graphic\nas the main event.", font=f(SANS, 23), fill=GRAY, spacing=9)
    tracked(draw, (54, 1164), "AISLE / SEAT / EXIT", f(SANS, 18), INK, 3)
    draw.text((56, 1202), "One hoodie. Two scenes.", font=f(SERIF_ITALIC, 34), fill=GREEN)
    folio(draw, "03 / 05")
    save(canvas, "editorial-carousel-03-king-hoodie.jpg")


def slide_4():
    canvas = Image.new("RGB", (W, H), PAPER)
    front = photo("14-crest-varsity-jacket-front.png", (452, 918), 0.50, 0.50)
    back = photo("15-crest-varsity-jacket-back.png", (452, 918), 0.50, 0.50)
    canvas.paste(front, (54, 178))
    canvas.paste(back, (574, 178))
    draw = ImageDraw.Draw(canvas)
    tracked(draw, (54, 48), "OBJECT STUDY / 04", f(SANS_BOLD, 20), GREEN, 3)
    draw.text((54, 82), "The D Crest Varsity", font=f(SERIF_ITALIC, 59), fill=INK)
    tracked(draw, (54, 1126), "FRONT", f(SANS_BOLD, 20), INK, 3)
    tracked(draw, (574, 1126), "BACK", f(SANS_BOLD, 20), INK, 3)
    draw.text((54, 1170), "Green / cream", font=f(SERIF_ITALIC, 32), fill=GREEN)
    draw.text((574, 1170), "Full-scale crest", font=f(SERIF_ITALIC, 32), fill=GREEN)
    folio(draw, "04 / 05")
    save(canvas, "editorial-carousel-04-varsity-study.jpg")


def slide_5():
    canvas = photo("12-rack-king-inevitable-stolen-life-crest-lobby.png", (W, H), 0.50, 0.46)
    veil = Image.new("RGBA", (W, H), (10, 13, 10, 88))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), veil)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((52, 52, 1028, 1298), outline=PAPER, width=1)
    tracked(draw, (540, 88), "ELSEWHERE APPAREL CO. / LIMITED EDITION", f(SANS, 18), PAPER, 3, "ma")
    draw.text((540, 500), "The Drop", font=f(SERIF_ITALIC, 120), fill=PAPER, anchor="ma")
    draw.text((540, 607), "is live.", font=f(SERIF, 90), fill=SAGE, anchor="ma")
    tracked(draw, (540, 728), "NOVEMBER 25 — DECEMBER 18", f(SANS_BOLD, 22), PAPER, 3, "ma")
    draw.line((322, 789, 758, 789), fill=PAPER, width=1)
    tracked(draw, (540, 835), "ELSEWHEREAPPARELCO.COM", f(SANS_BOLD, 23), PAPER, 3, "ma")
    tracked(draw, (540, 1244), "05 / 05", f(SANS, 18), PAPER, 3, "ma")
    save(canvas, "editorial-carousel-05-shop.jpg")


def story():
    canvas = Image.new("RGB", (SW, SH), PAPER)
    hero = photo("17-d-crest-varsity-jacket-two-friends-lobby.png", (850, 1180), 0.52, 0.43)
    detail = photo("12-rack-king-inevitable-stolen-life-crest-lobby.png", (610, 410), 0.50, 0.47)
    canvas.paste(hero, (176, 328))
    canvas.paste(detail, (54, 1450))
    draw = ImageDraw.Draw(canvas)
    tracked(draw, (54, 66), "ELSEWHERE / EDITORIAL 01", f(SANS_BOLD, 20), INK, 3)
    tracked(draw, (1026, 66), "2026", f(SANS, 20), INK, 3, "ra")
    draw.line((54, 110, 1026, 110), fill=INK, width=1)
    draw.text((48, 142), "The Doomsday", font=f(SERIF_ITALIC, 76), fill=INK)
    draw.text((50, 216), "Drop", font=f(SERIF, 88), fill=GREEN)
    draw.rectangle((52, 1266, 720, 1404), fill=PAPER)
    draw.text((72, 1281), "Limited run", font=f(SERIF_ITALIC, 45), fill=INK)
    tracked(draw, (75, 1344), "NOV 25 — DEC 18", f(SANS_BOLD, 20), GREEN, 3)
    tracked(draw, (695, 1790), "SHOP THE COLLECTION", f(SANS_BOLD, 20), PAPER, 3, "ma")
    tracked(draw, (695, 1830), "ELSEWHEREAPPARELCO.COM", f(SANS, 18), PAPER, 3, "ma")
    save(canvas, "editorial-story-1080x1920.jpg")


def reel_cover():
    canvas = Image.new("RGB", (SW, SH), PAPER)
    hero = photo("18-d-crest-varsity-jacket-back-theater-hallway.png", (930, 1480), 0.50, 0.42)
    canvas.paste(hero, (75, 218))
    draw = ImageDraw.Draw(canvas)
    tracked(draw, (54, 60), "ELSEWHERE APPAREL CO.", f(SANS_BOLD, 20), INK, 3)
    tracked(draw, (1026, 60), "ISSUE 01", f(SANS, 20), GREEN, 3, "ra")
    draw.line((54, 105, 1026, 105), fill=INK, width=1)
    draw.rectangle((54, 158, 762, 420), fill=PAPER)
    draw.text((60, 165), "Doomsday", font=f(SERIF_ITALIC, 94), fill=INK)
    draw.text((62, 260), "after dark", font=f(SERIF, 67), fill=GREEN)
    tracked(draw, (540, 1760), "LIMITED RUN / NOV 25 — DEC 18", f(SANS_BOLD, 22), INK, 3, "ma")
    tracked(draw, (540, 1812), "ELSEWHEREAPPARELCO.COM", f(SANS, 19), GREEN, 3, "ma")
    save(canvas, "editorial-reel-cover-1080x1920.jpg")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    slide_1()
    slide_2()
    slide_3()
    slide_4()
    slide_5()
    story()
    reel_cover()
