#!/usr/bin/env python3
"""Figures for /blog/letter-spacing-google-slides-pdf-export.

Usage: python3 tools/blog_pdf_images.py <export.pdf> <editor_roboto_pos.jpg>
  export.pdf  Drive PDF export of the 30-slide test deck (10 fonts x 0/+3/-1.5).
  editor jpg  Chrome screenshot of the Roboto +3 slide in the Slides editor
              (1470x802 viewport; slide canvas at x 343..1263, y 132..649).
Crops come straight from a 300 dpi render of the PDF, located with pdfplumber.
Needs pdftoppm, pdfplumber, Pillow, and Overpass at /tmp/fonts/Overpass.ttf.
"""
import statistics as st
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import pdfplumber
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cloud" / "static" / "blog" / "img"
FONT = Path("/tmp/fonts/Overpass.ttf")
DPI = 300
K = DPI / 72

SLIDES = (244, 180, 0)
INK = (28, 30, 34)
MUTE = (107, 111, 118)
RULE = (226, 228, 232)
BG = (246, 247, 249)
WHITE = (255, 255, 255)
BLUE = (0, 102, 255)
RED = (226, 64, 52)
CYAN = (0, 170, 200)

SANS = ["Roboto", "Inter", "Open Sans", "Montserrat", "Lato"]
SERIF = ["Playfair Display", "Merriweather", "Lora", "EB Garamond", "Libre Baskerville"]


def font(size, weight="Bold"):
    f = ImageFont.truetype(str(FONT), size)
    f.set_variation_by_name(weight)
    return f


def card(img, pad=48, radius=22, bg=WHITE, canvas=BG):
    w, h = img.size
    W, H = w + pad * 2, h + pad * 2
    out = Image.new("RGB", (W, H), canvas)
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 10, pad + w, pad + h + 10], radius, fill=60)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    out.paste(Image.new("RGB", (W, H), (205, 208, 214)), (0, 0), sh)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
    tile = Image.new("RGB", (w, h), bg)
    tile.paste(img, (0, 0))
    out.paste(tile, (pad, pad), mask)
    ImageDraw.Draw(out).rounded_rectangle([pad, pad, pad + w - 1, pad + h - 1], radius, outline=RULE, width=2)
    return out


def pill(d, x, y, text, bg=SLIDES, fg=INK, size=30):
    f = font(size, "ExtraBold")
    w = d.textlength(text, font=f)
    h = size + 18
    d.rounded_rectangle([x, y, x + w + 32, y + h], h // 2, fill=bg)
    d.text((x + 16, y + h / 2 + 1), text, font=f, fill=fg, anchor="lm")
    return x + w + 32


class Deck:
    def __init__(self, pdf_path, tmp):
        subprocess.run(["pdftoppm", "-r", str(DPI), "-png", str(pdf_path), str(Path(tmp) / "p")], check=True)
        self.pages = {}
        self.chars = {}
        with pdfplumber.open(pdf_path) as pdf:
            for i, p in enumerate(pdf.pages):
                label = "".join(c["text"] for c in p.chars if "Mono" in c["fontname"])
                fam, var = [s.strip() for s in label.split("|")]
                key = (fam, var.split()[1])
                img = sorted(Path(tmp).glob(f"p-{i + 1:02d}.png"))[0]
                self.pages[key] = Image.open(img).convert("RGB")
                lines = defaultdict(list)
                for c in p.chars:
                    if "Mono" not in c["fontname"]:
                        lines[round(c["size"])].append(c)
                self.chars[key] = {s: sorted(cs, key=lambda c: (round(c["top"]), c["x0"])) for s, cs in lines.items()}

    def line(self, fam, var, size, start=0, end=None, pad=0.18, first_row=True):
        cs = self.chars[(fam, var)][size]
        if first_row:
            top = min(c["top"] for c in cs)
            cs = [c for c in cs if c["top"] < top + 1]
        cs = cs[start:end]
        x0 = min(c["x0"] for c in cs); x1 = max(c["x1"] for c in cs)
        t = min(c["top"] for c in cs); b = max(c["bottom"] for c in cs)
        p = size * pad
        box = tuple(int(v * K) for v in (x0 - p, t - p * 0.4, x1 + p, b + p * 0.2))
        return self.pages[(fam, var)].crop(box), cs

    def adv(self, fam, var, size):
        return self.chars[(fam, var)][size]


def ink_only(img, color=INK):
    """Recolour the grey slide text to a solid ink on white."""
    g = img.convert("L")
    a = g.point(lambda v: max(0, min(255, int((255 - v) * 255 / (255 - 89)))))
    out = Image.new("RGB", img.size, WHITE)
    out.paste(Image.new("RGB", img.size, color), (0, 0), a)
    return out


def fit_w(img, w):
    return img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)


# ------------------------------------------------------------------ figures

def side_by_side(deck, editor):
    ed = Image.open(editor).convert("RGB").crop((343, 132, 1263, 649))
    pdf = deck.pages[("Roboto", "+")]
    W = 1100
    a = fit_w(ed, W); b = fit_w(pdf, W)
    a = a.crop((0, 0, W, int(a.height * 0.74))); b = b.crop((0, 0, W, int(b.height * 0.74)))
    gap, top = 70, 80
    img = Image.new("RGB", (W * 2 + gap, a.height + top), WHITE)
    img.paste(a, (0, top)); img.paste(b, (W + gap, top))
    d = ImageDraw.Draw(img)
    pill(d, 0, 6, "SLIDES EDITOR", bg=(232, 234, 238))
    pill(d, W + gap, 6, "PDF EXPORT", bg=SLIDES)
    d.rectangle([0, top, W - 1, img.height - 1], outline=RULE, width=2)
    d.rectangle([W + gap, top, 2 * W + gap - 1, img.height - 1], outline=RULE, width=2)
    card(img).save(OUT / "pdf-editor-side-by-side.png")


def overlay(deck, editor):
    src = Image.open(editor).convert("L")
    ed = src.crop((343, 132, 1263, 649))
    pdf = deck.pages[("Roboto", "+")].convert("L").resize(ed.size, Image.LANCZOS)
    W = 2000
    ed = fit_w(ed, W); pdf = fit_w(pdf, W)
    h = int(ed.height * 0.74)
    W = W - 10
    ed = ed.crop((0, 0, W, h)); pdf = pdf.crop((0, 0, W, h))
    # editor in red, PDF in cyan; where both have ink the result is dark grey
    r = pdf; g = ed; b = ed
    img = Image.merge("RGB", (r, g, b))
    img = ImageChops.multiply(img, Image.new("RGB", img.size, WHITE))
    top = 90
    canvas = Image.new("RGB", (W, h + top), WHITE)
    canvas.paste(img, (0, top))
    d = ImageDraw.Draw(canvas)
    x = pill(d, 0, 10, "EDITOR", bg=(255, 214, 210), fg=(170, 30, 20))
    x = pill(d, x + 14, 10, "PDF", bg=(200, 240, 248), fg=(0, 110, 130))
    d.text((x + 24, 34), "Grey where they agree. The thin colour fringes are screenshot alignment, under 1 px.", font=font(30, "SemiBold"), fill=MUTE, anchor="lm")
    card(canvas).save(OUT / "pdf-editor-overlay.png")


def measured(deck):
    rows = []
    for fam in SANS + SERIF:
        for size in (64, 36, 24, 14, 11, 8):
            c0 = deck.adv(fam, "0", size)
            for var in ("+", "-"):
                cs = deck.adv(fam, var, size)
                top0 = min(c["top"] for c in c0); top1 = min(c["top"] for c in cs)
                a = [c for c in c0 if c["top"] < top0 + 1]
                b = [c for c in cs if c["top"] < top1 + 1]
                n = min(len(a), len(b)) - 4
                d = [(b[i + 1]["x0"] - b[i]["x0"]) - (a[i + 1]["x0"] - a[i]["x0"]) for i in range(n)
                     if a[i]["text"] == b[i]["text"] and a[i + 1]["text"] == b[i + 1]["text"]]
                rows.append((fam, size, var, st.median(d), len(d)))
    W, H = 2000, 1000
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    L, R, T, B = 330, 1930, 150, 870
    ymin, ymax = -3, 4.5
    Y = lambda v: B - (v - ymin) / (ymax - ymin) * (B - T)
    d.text((0, 30), "Measured extra space per letter in the PDF", font=font(44, "ExtraBold"), fill=INK)
    d.text((0, 90), "Median shift vs. the 0 slide, every letter step, 10 fonts × 6 sizes", font=font(30, "SemiBold"), fill=MUTE)
    for v in (-3, -1.5, 0, 1.5, 3, 4.5):
        y = Y(v)
        d.line([L, y, R, y], fill=RULE if v not in (0,) else (190, 194, 200), width=2)
        d.text((L - 20, y), f"{v:+g} pt" if v else "0", font=font(28, "SemiBold"), fill=MUTE, anchor="rm")
    fams = SANS + SERIF
    step = (R - L) / len(fams)
    for i, fam in enumerate(fams):
        cx = L + step * (i + 0.5)
        name = fam.replace(" Display", "").replace("Libre ", "")
        d.text((cx, B + 30), name, font=font(25, "SemiBold"), fill=INK, anchor="mt")
        for (f, size, var, med, n) in rows:
            if f != fam:
                continue
            j = (64, 36, 24, 14, 11, 8).index(size)
            x = cx + (j - 2.5) * 16
            col = SLIDES if var == "+" else BLUE
            d.ellipse([x - 9, Y(med) - 9, x + 9, Y(med) + 9], fill=col, outline=WHITE, width=2)
    d.text((R, Y(3) - 34), "set to +3", font=font(28, "ExtraBold"), fill=(138, 90, 0), anchor="rb")
    d.text((R, Y(-1.5) + 30), "set to −1.5", font=font(28, "ExtraBold"), fill=BLUE, anchor="rt")
    d.text((0, H - 40), "Dots per font, left to right: 64, 36, 24, 14, 11, 8 pt.", font=font(26, "SemiBold"), fill=MUTE)
    card(img).save(OUT / "pdf-tracking-measured.png")
    return rows


def kerning(deck):
    """AV in Roboto 64 pt: the kern stays, tracking is added on top."""
    c0 = deck.adv("Roboto", "0", 64)
    vw = c0[6]["width"]                          # V's own width at 0 (x1 includes tracking when spaced)
    out = []
    for var, lab in (("0", "0"), ("+", "+3")):
        cs = deck.adv("Roboto", var, 64)
        a, v = cs[5], cs[6]                      # "AVATAR": A, V
        assert a["text"] == "A" and v["text"] == "V", (a["text"], v["text"])
        x0, x1 = a["x0"] - 4, v["x0"] + vw - 5
        t, bt = a["top"] + 4, a["bottom"] - 2
        crop = deck.pages[("Roboto", var)].crop(tuple(int(z * K) for z in (x0, t, x1, bt)))
        out.append((lab, ink_only(crop), v["x0"] - a["x0"], a, v, x0))
    gap = 200
    W = max(1450, sum(o[1].width for o in out) + gap)
    H = max(o[1].height for o in out)
    img = Image.new("RGB", (W, H + 360), WHITE)
    d = ImageDraw.Draw(img)
    x = 0
    base = out[0][2]
    for lab, crop, adv, a, v, x0 in out:
        img.paste(crop, (x, 110))
        pill(d, x, 10, f"LETTER SPACING {lab}", bg=SLIDES if lab != "0" else (232, 234, 238))
        vx = x + int((v["x0"] - x0) * K)
        d.line([vx, 100, vx, 120 + crop.height], fill=BLUE, width=4)
        d.text((x, 150 + crop.height), f"A to V: {adv:.2f} pt", font=font(36, "ExtraBold"), fill=INK)
        if lab != "0":
            d.text((x, 200 + crop.height), f"+{adv - base:.2f} pt vs. 0 (3 pt on a 1/1000 em grid)", font=font(30, "Bold"), fill=(138, 90, 0))
        x += crop.width + gap
    d.text((0, H + 340), "Roboto\u2019s AV kern (\u22122.69 pt at 64 pt) is still applied. Tracking sits on top of it.",
           font=font(30, "SemiBold"), fill=MUTE, anchor="lb")
    card(img).save(OUT / "pdf-kerning-kept.png")


def points_not_em(deck):
    big, _ = deck.line("Roboto", "+", 64, 0, 4)       # "WAVY"
    small, _ = deck.line("Roboto", "+", 8, 0, 4)      # "Trac"
    b = ink_only(big); s_ = ink_only(small)
    h = 220
    b = b.resize((int(b.width * h / b.height), h), Image.LANCZOS)
    s_ = s_.resize((int(s_.width * h / s_.height), h), Image.LANCZOS)
    W = max(1700, 120 + b.width + s_.width)
    img = Image.new("RGB", (W, 1000), WHITE)
    d = ImageDraw.Draw(img)
    pill(d, 0, 10, "+3 AT 64 PT", bg=SLIDES)
    img.paste(b, (0, 90))
    d.text((0, 90 + h + 20), "0.047 em: barely there", font=font(34, "Bold"), fill=INK)
    x2 = b.width + 120
    pill(d, x2, 10, "+3 AT 8 PT, SCALED UP TO MATCH", bg=SLIDES)
    img.paste(s_, (x2, 90))
    d.text((x2, 90 + h + 20), "0.375 em: very loose", font=font(34, "Bold"), fill=INK)
    y0 = 90 + h + 120
    d.text((0, y0), "+3 pt as a share of the font size", font=font(32, "ExtraBold"), fill=INK)
    sizes = (64, 36, 24, 14, 11, 8)
    bw = (W - 320) / 0.40
    for i, sz in enumerate(sizes):
        y = y0 + 60 + i * 52
        frac = 3 / sz
        d.text((0, y + 18), f"{sz} pt", font=font(28, "SemiBold"), fill=MUTE, anchor="lm")
        d.rounded_rectangle([110, y + 4, 110 + frac * bw, y + 32], 8, fill=SLIDES)
        d.text((124 + frac * bw, y + 18), f"{frac:.3f} em", font=font(26, "Bold"), fill=INK, anchor="lm")
    img = img.crop((0, 0, W, y0 + 60 + len(sizes) * 52 + 10))
    card(img).save(OUT / "pdf-points-not-em.png")


def ligatures(deck):
    fam = "Libre Baskerville"
    crops = []
    for var, lab in (("0", "0"), ("+", "+3"), ("-", "\u22121.5")):
        cs = deck.adv(fam, var, 11)
        last = max(round(c["top"]) for c in cs)
        row = [c for c in cs if round(c["top"]) == last]
        i = max(j for j, c in enumerate(row) if c["text"] == "o")
        tail = [c for c in row[i + 1:] if c["text"].strip()]
        x0 = min(c["x0"] for c in tail) - 0.6; x1 = max(c["x0"] + 3.5 for c in tail)
        t = min(c["top"] for c in tail) - 1; b = max(c["bottom"] for c in tail) + 1
        crop = deck.pages[(fam, var)].crop(tuple(int(z * K) for z in (x0, t, x1, b)))
        crops.append((lab, ink_only(crop), "".join(c["text"] for c in tail)))
    S = 3.6
    H = int(max(c[1].height for c in crops) * S)
    W = 1700
    img = Image.new("RGB", (W, 100 + 3 * (H + 60)), WHITE)
    d = ImageDraw.Draw(img)
    d.text((0, 20), "\u201cff fi.\u201d in Libre Baskerville, 11 pt, enlarged from the PDF", font=font(34, "ExtraBold"), fill=INK)
    for i, (lab, crop, glyphs) in enumerate(crops):
        y = 100 + i * (H + 60)
        pill(d, 0, y + H // 2 - 24, lab, bg=SLIDES if lab != "0" else (232, 234, 238))
        big = crop.resize((int(crop.width * S), int(crop.height * S)), Image.LANCZOS)
        img.paste(big, (200, y))
        lig = any(g in glyphs for g in ("\ufb00", "\ufb01"))
        note = ("ligatures on: ff and fi each drawn as one glyph" if lig else
                "ligatures off: the f\u2019s crowd each other" if lab.startswith("\u2212") else
                "ligatures off: every letter separate")
        d.text((260 + big.width, y + H // 2), note, font=font(30, "SemiBold"), fill=MUTE, anchor="lm")
        print("lig", lab, repr(glyphs))
    card(img).save(OUT / "pdf-ligatures.png")


def open_sans(deck):
    items = []
    for fam in ("Roboto", "Open Sans"):
        cs = deck.adv(fam, "0", 64)
        a, v = cs[5], cs[6]
        kern = (v["x0"] - a["x0"]) - a["width"]
        crop, _ = deck.line(fam, "0", 64, 5, 11)  # AVATAR
        items.append((fam, ink_only(crop), kern))
    W = 1700
    img = Image.new("RGB", (W, 520), WHITE)
    d = ImageDraw.Draw(img)
    for i, (fam, crop, kern) in enumerate(items):
        x = i * (W // 2)
        c = fit_w(crop, W // 2 - 80)
        pill(d, x, 10, fam.upper(), bg=SLIDES if fam == "Roboto" else (232, 234, 238))
        img.paste(c, (x, 100))
        d.text((x, 100 + c.height + 30), f"AV kern: {kern:+.2f} pt".replace("-", "\u2212") if abs(kern) > 0.01 else "AV kern: none",
               font=font(36, "ExtraBold"), fill=INK)
    d.text((0, 470), "Both at letter spacing 0, 64 pt. Open Sans on Google Fonts ships without kerning data.",
           font=font(28, "SemiBold"), fill=MUTE)
    card(img).save(OUT / "pdf-open-sans-kerning.png")


def ten_fonts(deck):
    rows = []
    for fam in SANS + SERIF:
        crop, _ = deck.line(fam, "+", 64)
        rows.append((fam, fit_w(ink_only(crop), 820)))
    colw, rowh = 900, 200
    W = colw * 2
    H = 90 + 5 * rowh
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    pill(d, 0, 6, "SANS", bg=(232, 234, 238)); pill(d, colw, 6, "SERIF", bg=(232, 234, 238))
    for i, (fam, crop) in enumerate(rows):
        col, r = divmod(i, 5)
        x, y = col * colw, 90 + r * rowh
        d.text((x, y), fam, font=font(26, "Bold"), fill=MUTE)
        c = crop if crop.height <= rowh - 60 else crop.resize((int(crop.width * (rowh - 60) / crop.height), rowh - 60), Image.LANCZOS)
        img.paste(c, (x, y + 40))
    card(img).save(OUT / "pdf-ten-fonts.png")


def hero(editor):
    W, H = 2400, 1260
    img = Image.new("RGB", (W, H), SLIDES)
    d = ImageDraw.Draw(img)
    pill(d, 88, 68, "GOOGLE SLIDES", bg=WHITE, size=34)
    f = font(104, "ExtraBold")
    d.text((88, 180), "Letter spacing", font=f, fill=INK)
    d.text((88, 300), "in a PDF export", font=f, fill=INK)
    d.text((88, H - 110), "Tested: 10 fonts, 6 sizes, the hard kerning pairs", font=font(44, "Bold"), fill=INK)
    ed = Image.open(editor).convert("RGB").crop((343, 175, 1263, 400))
    ed = fit_w(ed, 1220)
    src = OVERLAY_SRC
    pdf = src.crop((0, int(src.height * 43 / 517), src.width, int(src.height * 268 / 517)))
    pdf = fit_w(pdf, 1220)
    for (im, x, y, lab, bg, fg) in ((ed, 1090, 200, "SLIDES EDITOR", WHITE, INK), (pdf, 1090, 680, "PDF EXPORT", INK, WHITE)):
        sh = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sh).rounded_rectangle([x, y + 16, x + im.width, y + im.height + 16], 20, fill=90)
        img.paste(Image.new("RGB", (W, H), (150, 110, 0)), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)))
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], 20, fill=255)
        img.paste(im, (x, y), m)
        pill(d, x, y - 70, lab, bg=bg, fg=fg, size=28)
    img.save(OUT / "hero-pdf-spacing.png")
    img.resize((1200, 630), Image.LANCZOS).save(OUT / "og-pdf-spacing.png")


def main(pdf_path, editor):
    global OVERLAY_SRC
    with tempfile.TemporaryDirectory() as tmp:
        deck = Deck(pdf_path, tmp)
        OVERLAY_SRC = deck.pages[("Roboto", "+")]
        side_by_side(deck, editor)
        overlay(deck, editor)
        rows = measured(deck)
        kerning(deck)
        points_not_em(deck)
        ligatures(deck)
        open_sans(deck)
        ten_fonts(deck)
        hero(editor)
    meds = [r[3] for r in rows]
    print("plus range", min(r[3] for r in rows if r[2] == "+"), max(r[3] for r in rows if r[2] == "+"))
    print("minus range", min(r[3] for r in rows if r[2] == "-"), max(r[3] for r in rows if r[2] == "-"))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
