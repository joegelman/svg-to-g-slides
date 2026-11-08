#!/usr/bin/env python3
"""Render annotated blog graphics for /blog/letter-spacing-google-slides.

Usage: python3 tools/blog_images.py <dir-with-raw-captures>
Raw captures are browser screenshots named by key in RAW below.
Outputs PNGs into cloud/static/blog/img/.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cloud" / "static" / "blog" / "img"
FONT = Path("/tmp/fonts/Overpass.ttf")

YELLOW = (255, 199, 0)
BLUE = (0, 102, 255)
INK = (28, 30, 34)
MUTE = (107, 111, 118)
BG = (246, 247, 249)
WHITE = (255, 255, 255)
RED = (226, 64, 52)


def font(size, weight="Bold"):
    f = ImageFont.truetype(str(FONT), size)
    f.set_variation_by_name(weight)
    return f


def cursor(d, x, y, s=1.0):
    """Classic arrow pointer, tip at (x, y)."""
    pts = [(0, 0), (0, 34), (8, 26), (14, 40), (20, 37), (14, 24), (25, 24)]
    P = [(x + px * s, y + py * s) for px, py in pts]
    d.polygon(P, fill=(0, 0, 0), outline=WHITE)
    d.line(P + [P[0]], fill=WHITE, width=max(2, int(2.5 * s)), joint="curve")
    d.polygon(P, fill=(0, 0, 0))


def shadow_card(img, pad=48, radius=22, bg=BG):
    """Place img on a soft-shadow rounded card over a light canvas."""
    w, h = img.size
    W, H = w + pad * 2, h + pad * 2
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + w, pad + h + 10], radius, fill=70)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    canvas = Image.new("RGBA", (W, H), (20, 24, 40, 0))
    canvas.putalpha(sh)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
    canvas.paste(img, (pad, pad), mask)
    ImageDraw.Draw(canvas).rounded_rectangle([pad, pad, pad + w - 1, pad + h - 1], radius, outline=(222, 225, 230), width=2)
    return canvas


def ring(d, box, color=YELLOW, width=7, r=14, dashed=False):
    x0, y0, x1, y1 = box
    if not dashed:
        d.rounded_rectangle(box, r, outline=color, width=width)
        return
    seg, gap = 18, 12
    for x in range(int(x0), int(x1), seg + gap):
        d.line([(x, y0), (min(x + seg, x1), y0)], fill=color, width=width)
        d.line([(x, y1), (min(x + seg, x1), y1)], fill=color, width=width)
    for y in range(int(y0), int(y1), seg + gap):
        d.line([(x0, y), (x0, min(y + seg, y1))], fill=color, width=width)
        d.line([(x1, y), (x1, min(y + seg, y1))], fill=color, width=width)


def pill(d, xy, text, size=26, fg=WHITE, bg=BLUE, anchor="la"):
    f = font(size, "Bold")
    x, y = xy
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    w, h = r - l + size, int(size * 1.6)
    if anchor == "ra":
        x -= w
    if anchor == "ma":
        x -= w // 2
    d.rounded_rectangle([x, y, x + w, y + h], h // 2, fill=bg)
    d.text((x + w / 2, y + h / 2 + 2), text, font=f, fill=fg, anchor="mm")
    return (x, y, x + w, y + h)


def scale(img, k):
    return img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS)


# ------------------------------------------------------------------ graphics
def hero(dark=False):
    """Crisp vector close-up of the new toolbar button + cursor + tooltip."""
    W, H = 2400, 1260
    S = 2
    BGC = (20, 21, 24) if dark else (250, 250, 247)
    im = Image.new("RGB", (W, H), BGC)
    d = ImageDraw.Draw(im)
    # faint giant tracked word
    big = font(300, "Black")
    word, x = "TRACKING", 0
    widths = [d.textlength(c, font=big) for c in word]
    track = 70
    total = sum(widths) + track * (len(word) - 1)
    x = (W - total) / 2
    for c, cw in zip(word, widths):
        d.text((x, H - 140), c, font=big, fill=(36, 38, 43) if dark else (238, 238, 232), anchor="ls")
        x += cw + track
    # toolbar strip
    tb = [260, 300, 2140, 560]
    d.rounded_rectangle(tb, 60, fill=(40, 43, 50) if dark else (237, 242, 250))
    ic = (220, 222, 226) if dark else (68, 71, 70)
    cy = 430
    # line-spacing icon (left neighbor)
    lx = 760
    d.line([(lx, cy - 52), (lx, cy + 52)], fill=ic, width=12)
    d.polygon([(lx - 24, cy - 34), (lx + 24, cy - 34), (lx, cy - 62)], fill=ic)
    d.polygon([(lx - 24, cy + 34), (lx + 24, cy + 34), (lx, cy + 62)], fill=ic)
    for i, yy in enumerate([-40, 0, 40]):
        d.line([(lx + 50, cy + yy), (lx + 150, cy + yy)], fill=ic, width=12)
    # bullets icon (right neighbor)
    rx = 1560
    for yy in (-40, 0, 40):
        d.ellipse([rx - 11, cy + yy - 11, rx + 11, cy + yy + 11], fill=ic)
        d.line([(rx + 36, cy + yy), (rx + 140, cy + yy)], fill=ic, width=12)
    # the button (hover state)
    bx0, by0, bx1, by1 = 1060, 330, 1340, 530
    d.rounded_rectangle([bx0, by0, bx1, by1], 40, fill=(66, 71, 82) if dark else (218, 224, 233))
    bcx = (bx0 + bx1) // 2
    d.line([(bcx - 78, cy - 62), (bcx - 78, cy + 62)], fill=ic, width=13)
    d.line([(bcx + 78, cy - 62), (bcx + 78, cy + 62)], fill=ic, width=13)
    d.text((bcx, cy + 6), "A", font=font(150, "Bold"), fill=ic, anchor="mm")
    # highlight ring
    d.rounded_rectangle([bx0 - 26, by0 - 26, bx1 + 26, by1 + 26], 60, outline=YELLOW, width=16)
    # tooltip
    tf = font(64, "SemiBold")
    tw = d.textlength("Letter spacing", font=tf)
    tx0 = bcx - tw / 2 - 52
    TT = (232, 234, 237) if dark else (32, 33, 36)
    d.rounded_rectangle([tx0, 640, tx0 + tw + 104, 780], 28, fill=TT)
    d.polygon([(bcx - 26, 642), (bcx + 26, 642), (bcx, 614)], fill=TT)
    d.text((bcx, 712), "Letter spacing", font=tf, fill=(32, 33, 36) if dark else WHITE, anchor="mm")
    cursor(d, bx1 - 70, by1 - 46, 4.2)
    # kicker
    d.text((260, 150), "NEW IN GOOGLE SLIDES", font=font(54, "ExtraBold"), fill=(77, 141, 255) if dark else BLUE)
    if dark:
        im.save(OUT / "hero-letter-spacing-dark.png", optimize=True)
        im.resize((1200, 630), Image.LANCZOS).save(OUT / "og-letter-spacing-dark.png", optimize=True)
        return
    im.save(OUT / "hero-letter-spacing.png", optimize=True)
    og = im.resize((1200, 630), Image.LANCZOS)
    og.save(OUT / "og-letter-spacing.png", optimize=True)


def anatomy():
    """Tracking vs kerning vs leading, one panel each."""
    W, H = 2400, 900
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    col = W // 3
    lab = font(46, "ExtraBold")
    sub = font(34, "Regular")
    word = font(130, "Bold")
    for i, (t, s) in enumerate([("Tracking", "even space across a run"),
                                ("Kerning", "space between one pair"),
                                ("Leading", "space between lines")]):
        x0 = i * col
        if i:
            d.line([(x0, 90), (x0, H - 90)], fill=(230, 232, 236), width=3)
        d.text((x0 + col / 2, 120), t.upper(), font=lab, fill=INK, anchor="mm")
        d.text((x0 + col / 2, 178), s, font=sub, fill=MUTE, anchor="mm")
    # tracking: letters with equal yellow gaps
    cx = col / 2
    letters = "SLIDE"
    ws = [d.textlength(c, font=word) for c in letters]
    tr = 34
    x = cx - (sum(ws) + tr * 4) / 2
    base = 560
    for j, (c, w) in enumerate(zip(letters, ws)):
        d.text((x, base), c, font=word, fill=INK, anchor="ls")
        if j < 4:
            d.rectangle([x + w + 2, base - 110, x + w + tr - 2, base + 10], fill=YELLOW)
        x += w + tr
    d.text((cx, 700), "+3  →  same gap after every letter", font=font(32, "SemiBold"), fill=BLUE, anchor="mm")
    # kerning: AV pair pulled together
    cx = col * 1.5
    a = d.textlength("A", font=word)
    v = d.textlength("V", font=word)
    k = -22
    x = cx - (a + v + k) / 2
    d.text((x, base), "A", font=word, fill=INK, anchor="ls")
    d.text((x + a + k, base), "V", font=word, fill=INK, anchor="ls")
    mid = x + a + k / 2
    yb = base + 60
    d.line([(mid - 90, yb), (mid - 22, yb)], fill=BLUE, width=8)
    d.line([(mid + 22, yb), (mid + 90, yb)], fill=BLUE, width=8)
    d.polygon([(mid - 26, yb - 18), (mid - 26, yb + 18), (mid - 4, yb)], fill=BLUE)
    d.polygon([(mid + 26, yb - 18), (mid + 26, yb + 18), (mid + 4, yb)], fill=BLUE)
    d.text((cx, 700), "set by the font, not by Slides", font=font(32, "SemiBold"), fill=MUTE, anchor="mm")
    # leading: two lines with measured gap
    cx = col * 2.5
    lf = font(92, "Bold")
    d.text((cx, 400), "Line one", font=lf, fill=INK, anchor="ms")
    d.text((cx, 560), "Line two", font=lf, fill=INK, anchor="ms")
    lx = cx + 230
    d.line([(lx, 400), (lx, 560)], fill=BLUE, width=6)
    d.line([(lx - 18, 400), (lx + 18, 400)], fill=BLUE, width=6)
    d.line([(lx - 18, 560), (lx + 18, 560)], fill=BLUE, width=6)
    d.text((cx, 700), "the line spacing button, next door", font=font(32, "SemiBold"), fill=MUTE, anchor="mm")
    im.save(OUT / "tracking-kerning-leading.png", optimize=True)


def foreground_mask(orig, keep=()):
    """Pixels that should stay ON TOP of annotation rings: the cursor (dark pixels,
    dilated to include its white outline) and any ink inside `keep` boxes (scaled coords)."""
    from PIL import ImageChops
    lum = orig.convert("L")
    dark = lum.point(lambda v: 255 if v < 60 else 0).filter(ImageFilter.MaxFilter(9))
    mask = dark
    if keep:
        diff = ImageChops.difference(orig, Image.new("RGB", orig.size, WHITE)).convert("L")
        ink = diff.point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(3))
        box_m = Image.new("L", orig.size, 0)
        bd = ImageDraw.Draw(box_m)
        for b in keep:
            bd.rectangle(b, fill=255)
        mask = ImageChops.lighter(mask, ImageChops.multiply(ink, box_m))
    return mask


def annotated(raw, name, k=1.0, rings=(), pills=(), dashed=(), keep=()):
    img = scale(Image.open(raw).convert("RGB"), k)
    orig = img.copy()
    d = ImageDraw.Draw(img)
    for b in rings:
        ring(d, [v * k for v in b])
    if rings:
        img.paste(orig, (0, 0), foreground_mask(orig, [[v * k for v in b] for b in keep]))
        d = ImageDraw.Draw(img)
    for b in dashed:
        ring(d, [v * k for v in b], color=RED, width=6, dashed=True)
    for xy, text, *rest in pills:
        opts = rest[0] if rest else {}
        pill(d, (xy[0] * k, xy[1] * k), text, **opts)
    shadow_card(img).save(OUT / name, optimize=True)


def pair(raw_a, raw_b, la, lb, name, k=1.0):
    from PIL import ImageChops, ImageOps
    a0, b0 = Image.open(raw_a).convert("RGB"), Image.open(raw_b).convert("RGB")
    bb = [ImageOps.invert(x).getbbox() for x in (a0, b0)]
    x0 = max(0, min(bb[0][0], bb[1][0]) - 60)
    x1 = min(a0.width, max(bb[0][2], bb[1][2]) + 60)
    a = scale(a0.crop((x0, 0, x1, a0.height)), k)
    b = scale(b0.crop((x0, 0, x1, b0.height)), k)
    gap, lw = 18, 200
    W = a.width + lw
    im = Image.new("RGB", (W, a.height + b.height + gap), WHITE)
    im.paste(a, (lw, 0))
    im.paste(b, (lw, a.height + gap))
    d = ImageDraw.Draw(im)
    d.line([(0, a.height + gap // 2), (W, a.height + gap // 2)], fill=(230, 232, 236), width=2)
    pill(d, (36, a.height // 2 - 22), la, size=34, bg=(232, 234, 238), fg=INK)
    pill(d, (36, a.height + gap + b.height // 2 - 22), lb, size=34, bg=YELLOW, fg=INK)
    shadow_card(im).save(OUT / name, optimize=True)


def wayback(raw_a, raw_b, name):
    a = Image.open(raw_a).convert("RGB")
    b = Image.open(raw_b).convert("RGB")
    da, db = ImageDraw.Draw(a), ImageDraw.Draw(b)
    ring(da, [140, 196, 712, 318], color=RED, width=6, dashed=True)
    pill(da, (760, 230), "Oct 5, 2026: no letter spacing", size=26, bg=RED)
    ring(db, [140, 334, 712, 506])
    pill(db, (760, 380), "Oct 12, 2026: “Adjust letter spacing”", size=26, bg=BLUE)
    gap = 28
    im = Image.new("RGB", (a.width, a.height + b.height + gap), BG)
    im.paste(a, (0, 0))
    im.paste(b, (0, a.height + gap))
    shadow_card(im).save(OUT / name, optimize=True)


def main(src):
    src = Path(src)
    R = lambda key: next(src.glob(f"*{key}*.png"))
    OUT.mkdir(parents=True, exist_ok=True)
    hero()
    anatomy()
    annotated(R("1794061548627"), "toolbar-letter-spacing.png", k=2,
              rings=[(337, 10, 415, 86)])
    annotated(R("1794061557335"), "letter-spacing-presets.png", k=1.4,
              pills=[((470, 109), "open caps, tiny labels", {"size": 24}),
                     ((470, 173), "small caps, eyebrows", {"size": 24}),
                     ((470, 237), "default — body text", {"size": 24, "bg": (232, 234, 238), "fg": INK}),
                     ((470, 302), "big display headlines", {"size": 24, "bg": YELLOW, "fg": INK})])
    annotated(R("1794061567949"), "custom-letter-spacing.png", k=1.4,
              rings=[(58, 162, 610, 282)], keep=[(90, 152, 258, 190)])
    pair(R("1794061595890"), R("1794061608038"), "0", "+3", "caps-0-vs-3.png")
    pair(R("1794061623125"), R("1794061633883"), "0", "−1.5", "headline-0-vs-neg.png")
    annotated(R("1794061662318"), "format-text-letter-spacing.png",
              rings=[(578, 444, 1036, 500), (1040, 456, 1500, 780)])
    annotated(R("1794061702869"), "docs-format-text-today.png",
              dashed=[(652, 494, 1166, 640)],
              pills=[((700, 455), "Docs editor today: no Letter spacing", {"size": 24, "bg": RED})])
    annotated(R("1794061719689"), "docs-help-letter-spacing.png",
              rings=[(26, 322, 1452, 744)])
    wayback(R("1794061871130"), R("1794061980535"), "wayback-oct5-vs-oct12.png")
    for p in sorted(OUT.glob("*.png")):
        print(p.name, Image.open(p).size, p.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])
