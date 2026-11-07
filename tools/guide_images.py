#!/usr/bin/env python3
"""Card / OG illustrations for each guide (1200x630, PNG + WebP).

Drawn at 3x and downsampled for clean edges. Output: cloud/static/guides/img/<slug>.png|webp
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cloud" / "static" / "guides" / "img"
FONT = Path("/tmp/fonts/Overpass.ttf")
S = 3
W, H = 1200 * S, 630 * S

CREAM = (255, 251, 234)
YELLOW = (255, 199, 0)
BLUE = (0, 102, 255)
INK = (28, 30, 34)
MUTE = (107, 111, 118)
RULE = (226, 228, 232)
WHITE = (255, 255, 255)
GREEN = (76, 203, 62)
RED = (226, 64, 52)
TEAL = (38, 166, 154)
PALETTE = [(28, 30, 34), (0, 102, 255), (255, 199, 0), (76, 203, 62), (226, 64, 52), (38, 166, 154), (156, 39, 176)]


def f(size, weight="Bold"):
    ft = ImageFont.truetype(str(FONT), size * S)
    ft.set_variation_by_name(weight)
    return ft


def sc(*v):
    return [x * S for x in v]


def canvas(bg=CREAM):
    return Image.new("RGB", (W, H), bg)


def shadow(im, box, r=18, blur=22, off=10, alpha=60):
    x0, y0, x1, y1 = sc(*box)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle([x0, y0 + off * S, x1, y1 + off * S], r * S, fill=alpha)
    m = m.filter(ImageFilter.GaussianBlur(blur * S))
    im.paste(Image.new("RGB", (W, H), (30, 30, 40)), (0, 0), m)


def card(im, box, r=18, fill=WHITE, outline=RULE, sh=True):
    if sh:
        shadow(im, box, r)
    ImageDraw.Draw(im).rounded_rectangle(sc(*box), r * S, fill=fill, outline=outline, width=2 * S)


def svg_file(im, x, y, w=150, label="SVG", color=YELLOW):
    h = w * 1.28
    fold = w * 0.28
    shadow(im, (x, y, x + w, y + h), 10)
    d = ImageDraw.Draw(im)
    pts = [(x, y), (x + w - fold, y), (x + w, y + fold), (x + w, y + h), (x, y + h)]
    d.polygon([(px * S, py * S) for px, py in pts], fill=WHITE, outline=RULE)
    d.line([(px * S, py * S) for px, py in pts + [pts[0]]], fill=(210, 213, 218), width=2 * S, joint="curve")
    d.polygon([((x + w - fold) * S, y * S), ((x + w - fold) * S, (y + fold) * S), ((x + w) * S, (y + fold) * S)], fill=(236, 238, 241))
    bx = x + w * 0.12
    d.rounded_rectangle(sc(bx, y + h * 0.62, x + w * 0.88, y + h * 0.86), 8 * S, fill=color)
    d.text(((x + w / 2) * S, (y + h * 0.74) * S), label, font=f(int(w * 0.2), "ExtraBold"), fill=INK, anchor="mm")
    return h


def cursor(im, x, y, s=1.0):
    pts = [(0, 0), (0, 34), (8, 26), (14, 40), (20, 37), (14, 24), (25, 24)]
    P = [((x + px * s) * S, (y + py * s) * S) for px, py in pts]
    d = ImageDraw.Draw(im)
    d.polygon(P, fill=INK)
    d.line(P + [P[0]], fill=WHITE, width=int(2.5 * s * S), joint="curve")
    d.polygon(P, fill=INK)


def handles(im, box, color=BLUE):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    d.rectangle(sc(x0, y0, x1, y1), outline=color, width=2 * S)
    for hx in (x0, (x0 + x1) / 2, x1):
        for hy in (y0, (y0 + y1) / 2, y1):
            if hx == (x0 + x1) / 2 and hy == (y0 + y1) / 2:
                continue
            d.ellipse(sc(hx - 6, hy - 6, hx + 6, hy + 6), fill=WHITE, outline=color, width=2 * S)
    cx = (x0 + x1) / 2
    d.line(sc(cx, y0, cx, y0 - 28), fill=color, width=2 * S)
    d.ellipse(sc(cx - 8, y0 - 36, cx + 8, y0 - 20), fill=color)


def star_pts(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def mark(im, cx, cy, size, color=YELLOW):
    """Generic logo mark: rounded square + inner circle + diagonal leaf."""
    d = ImageDraw.Draw(im)
    s = size / 2
    d.rounded_rectangle(sc(cx - s, cy - s, cx + s, cy + s), size * 0.24 * S, fill=color)
    d.polygon(sc(*[c for p in star_pts(cx, cy + s * 0.06, s * 0.62, s * 0.26) for c in p]), fill=INK)


def slide(im, box, sh=True):
    card(im, box, 10, sh=sh)


def save(im, slug):
    out = im.resize((1200, 630), Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    out.save(OUT / f"{slug}.png", optimize=True)
    out.save(OUT / f"{slug}.webp", "WEBP", quality=88, method=6)


# --------------------------------------------------------------- guides
def does_support():
    """An SVG file at a slide's door: Slides shows a question mark."""
    im = canvas()
    slide(im, (400, 90, 1080, 470))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(sc(400, 90, 1080, 136), 10 * S, fill=(245, 246, 248))
    d.rectangle(sc(400, 124, 1080, 136), fill=(245, 246, 248))
    for i, c in enumerate([(255, 95, 87), (255, 189, 46), (40, 200, 64)]):
        d.ellipse(sc(422 + i * 26, 106, 436 + i * 26, 120), fill=c)
    d.ellipse(sc(645, 200, 835, 390), fill=(255, 244, 204))
    d.text((740 * S, 298 * S), "?", font=f(140, "Black"), fill=YELLOW, anchor="mm")
    svg_file(im, 120, 175, 200)
    d = ImageDraw.Draw(im)
    for i in range(6):
        x = 338 + i * 11
        d.ellipse(sc(x - 3, 303, x + 3, 309), fill=MUTE)
    chip(im, 400, 510, "Not natively", RED)
    chip(im, 625, 510, "Yes, with SVG to Slides", GREEN)
    save(im, "does-google-slides-support-svg")


def chip(im, x, y, text, color):
    d = ImageDraw.Draw(im)
    ft = f(26, "ExtraBold")
    tw = d.textlength(text, font=ft) / S
    d.rounded_rectangle(sc(x, y, x + tw + 64, y + 54), 27 * S, fill=WHITE, outline=RULE, width=2 * S)
    d.ellipse(sc(x + 16, y + 17, x + 36, y + 37), fill=color)
    d.text(((x + 46) * S, (y + 28) * S), text, font=ft, fill=INK, anchor="lm")


def insert():
    """SVG dragged onto a slide: ghost preview, cursor, + badge, paste pill."""
    im = canvas()
    slide(im, (250, 110, 950, 504))
    d = ImageDraw.Draw(im)
    # filmstrip hint
    for i in range(3):
        d.rounded_rectangle(sc(150, 130 + i * 110, 220, 170 + i * 110 + 20), 6 * S, fill=WHITE, outline=RULE, width=2 * S)
    # placed ghost: logo mark at 50% + dashed box
    gh = Image.new("RGB", (W, H), WHITE)
    mark(gh, 600, 300, 150)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle(sc(520, 220, 680, 380), 20 * S, fill=130)
    im.paste(gh, (0, 0), m)
    d = ImageDraw.Draw(im)
    for x in range(510, 690, 18):
        d.line(sc(x, 210, x + 9, 210), fill=BLUE, width=3 * S)
        d.line(sc(x, 390, x + 9, 390), fill=BLUE, width=3 * S)
    for y in range(210, 390, 18):
        d.line(sc(510, y, 510, y + 9), fill=BLUE, width=3 * S)
        d.line(sc(690, y, 690, y + 9), fill=BLUE, width=3 * S)
    # + badge
    d.ellipse(sc(668, 368, 712, 412), fill=GREEN, outline=WHITE, width=4 * S)
    d.text((690 * S, 389 * S), "+", font=f(36, "Black"), fill=WHITE, anchor="mm")
    cursor(im, 694, 394, 2.0)
    # paste pill
    d = ImageDraw.Draw(im)
    txt = "⌘ + V to confirm"
    ft = f(26, "ExtraBold")
    tw = d.textlength(txt, font=ft) / S
    d.rounded_rectangle(sc(600 - tw / 2 - 26, 438, 600 + tw / 2 + 26, 486), 24 * S, fill=INK)
    d.text((600 * S, 463 * S), txt, font=ft, fill=WHITE, anchor="mm")
    # source file
    svg_file(im, 990, 160, 130)
    save(im, "insert-svg-into-google-slides")


def svg_vs_png():
    """Same star: pixelated PNG left, crisp vector with bezier handles right."""
    im = canvas()
    for i, (x0, label, good) in enumerate([(110, "PNG", False), (630, "SVG", True)]):
        card(im, (x0, 90, x0 + 460, 470), 22)
        d = ImageDraw.Draw(im)
        cx, cy = x0 + 230, 270
        if not good:
            # pixelated star: sample star mask on coarse grid
            mask = Image.new("L", (40, 40), 0)
            ImageDraw.Draw(mask).polygon(star_pts(20, 21, 19, 8), fill=255)
            px = 8
            for gy in range(40):
                for gx in range(40):
                    v = mask.getpixel((gx, gy))
                    if v:
                        x, y = cx - 160 + gx * px, cy - 160 + gy * px
                        d.rectangle(sc(x, y, x + px, y + px), fill=YELLOW)
            # jaggy zoom inset
            d.rounded_rectangle(sc(x0 + 300, 330, x0 + 430, 450), 12 * S, fill=WHITE, outline=RULE, width=2 * S)
            for gy in range(4):
                for gx in range(4):
                    if (gx + gy) % 3 != 0:
                        d.rectangle(sc(x0 + 318 + gx * 24, 348 + gy * 22, x0 + 340 + gx * 24, 368 + gy * 22), fill=YELLOW if gx > gy - 1 else (255, 226, 140))
        else:
            pts = star_pts(cx, cy + 6, 150, 62)
            d.polygon(sc(*[c for p in pts for c in p]), fill=YELLOW)
            # bezier-ish handles on two points
            for (hx, hy) in (pts[0], pts[4]):
                d.line(sc(hx - 46, hy + 10, hx + 46, hy - 10), fill=BLUE, width=3 * S)
                for ex, ey in ((hx - 46, hy + 10), (hx + 46, hy - 10)):
                    d.ellipse(sc(ex - 7, ey - 7, ex + 7, ey + 7), fill=WHITE, outline=BLUE, width=3 * S)
                d.rectangle(sc(hx - 8, hy - 8, hx + 8, hy + 8), fill=BLUE)
        d.text(((x0 + 230) * S, 530 * S), label, font=f(46, "Black"), fill=RED if not good else BLUE, anchor="mm")
        d.text(((x0 + 230) * S, 574 * S), "flattened, blurs when resized" if not good else "native shape, sharp at any size",
               font=f(24, "SemiBold"), fill=MUTE, anchor="mm")
    d = ImageDraw.Draw(im)
    d.text((600 * S, 280 * S), "vs", font=f(40, "Black"), fill=MUTE, anchor="mm")
    save(im, "svg-vs-png-google-slides")


def converter():
    """A stack of SVG files -> arrow -> a deck of slides, one per file."""
    im = canvas()
    for i in range(3):
        svg_file(im, 120 + i * 46, 110 + i * 30, 160)
    d = ImageDraw.Draw(im)
    # arrow
    d.rounded_rectangle(sc(470, 300, 640, 330), 15 * S, fill=INK)
    d.polygon(sc(630, 270, 690, 315, 630, 360), fill=INK)
    # deck: one slide per file, no overlap
    shapes = [(BLUE, "c"), (YELLOW, "s"), (GREEN, "t")]
    for i in range(3):
        x0, y0 = 760, 70 + i * 170
        slide(im, (x0, y0, x0 + 300, y0 + 150))
        d = ImageDraw.Draw(im)
        col, kind = shapes[i]
        cx, cy = x0 + 150, y0 + 75
        if kind == "c":
            d.ellipse(sc(cx - 46, cy - 46, cx + 46, cy + 46), fill=col)
        elif kind == "s":
            d.polygon(sc(*[c for p in star_pts(cx, cy + 4, 54, 22) for c in p]), fill=col)
        else:
            d.polygon(sc(cx, cy - 48, cx + 54, cy + 42, cx - 54, cy + 42), fill=col)
        d.text(((x0 - 26) * S, cy * S), str(i + 1), font=f(26, "ExtraBold"), fill=MUTE, anchor="mm")
    chip(im, 150, 520, "One slide per SVG", BLUE)
    save(im, "svg-to-google-slides-converter")


def recolor():
    """One path selected inside a logo, fill picker open, swatches."""
    im = canvas()
    slide(im, (110, 100, 700, 520))
    d = ImageDraw.Draw(im)
    # logo: three overlapping shapes, middle one recoloured + selected
    d.ellipse(sc(200, 210, 380, 390), fill=(210, 214, 220))
    d.polygon(sc(*[c for p in star_pts(410, 300, 110, 46) for c in p]), fill=BLUE)
    d.rounded_rectangle(sc(470, 230, 620, 380), 30 * S, fill=(210, 214, 220))
    handles(im, (300, 190, 520, 410))
    cursor(im, 470, 360, 1.9)
    # fill picker panel
    card(im, (760, 120, 1100, 470), 18)
    d = ImageDraw.Draw(im)
    d.text((790 * S, 168 * S), "Fill colour", font=f(26, "ExtraBold"), fill=INK, anchor="lm")
    for i, c in enumerate(PALETTE):
        x = 795 + (i % 4) * 74
        y = 220 + (i // 4) * 74
        d.ellipse(sc(x, y, x + 54, y + 54), fill=c)
        if c == BLUE:
            d.ellipse(sc(x - 7, y - 7, x + 61, y + 61), outline=INK, width=4 * S)
    d.rounded_rectangle(sc(790, 390, 1070, 440), 25 * S, fill=(245, 246, 248))
    d.text((812 * S, 415 * S), "#0066FF", font=f(24, "Bold"), fill=MUTE, anchor="lm")
    d.rounded_rectangle(sc(1012, 400, 1052, 430), 8 * S, fill=BLUE)
    save(im, "recolor-svg-in-google-slides")


def logos_themes():
    """Theme layout with the logo; the same crisp mark repeats on every slide."""
    im = canvas()
    # master/theme panel
    card(im, (80, 90, 480, 520), 18, fill=(40, 43, 50), outline=(40, 43, 50))
    d = ImageDraw.Draw(im)
    d.text((110 * S, 130 * S), "THEME", font=f(22, "ExtraBold"), fill=(170, 175, 185), anchor="lm")
    slide(im, (110, 160, 450, 350), sh=False)
    mark(im, 410, 315, 46)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(sc(135, 190, 330, 210), 6 * S, fill=(210, 214, 220))
    d.rounded_rectangle(sc(135, 222, 280, 236), 6 * S, fill=(232, 234, 238))
    d.text((110 * S, 385 * S), "LAYOUTS", font=f(22, "ExtraBold"), fill=(170, 175, 185), anchor="lm")
    for i in range(3):
        x = 110 + i * 116
        d.rounded_rectangle(sc(x, 410, x + 104, 470), 6 * S, fill=WHITE, outline=YELLOW, width=3 * S)
        mark(im, x + 88, 456, 16)
        d = ImageDraw.Draw(im)
    # arrow
    d.polygon(sc(510, 280, 560, 305, 510, 330), fill=INK)
    # deck grid
    for i in range(6):
        r, c = divmod(i, 3)
        x0, y0 = 590 + c * 190, 120 + r * 200
        slide(im, (x0, y0, x0 + 170, y0 + 100 + 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle(sc(x0 + 14, y0 + 16, x0 + 110, y0 + 28), 5 * S, fill=(214, 218, 224))
        d.rounded_rectangle(sc(x0 + 14, y0 + 38, x0 + 80, y0 + 46), 4 * S, fill=(232, 234, 238))
        mark(im, x0 + 150, y0 + 82, 24)
    d = ImageDraw.Draw(im)
    d.text((875 * S, 470 * S), "Same logo, every slide, always sharp", font=f(26, "Bold"), fill=MUTE, anchor="mm")
    save(im, "svg-logos-icons-google-slides")


if __name__ == "__main__":
    for fn in (does_support, insert, svg_vs_png, converter, recolor, logos_themes):
        fn()
    for p in sorted(OUT.glob("*.png")):
        print(p.name, p.stat().st_size // 1024, "KB")
