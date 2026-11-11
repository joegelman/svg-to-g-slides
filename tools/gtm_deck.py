#!/usr/bin/env python3
"""Build the Apps Script for GTM part 1 deck as a .pptx, for upload to Drive as Google Slides.

Usage: python3 tools/gtm_deck.py OUT.pptx
"""
import sys
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import gtm_appscript as G  # noqa: E402

W, H = 720, 405  # points, Google Slides 16:9 default
INK, GREY, RULE, TINT = "1C1E22", "6B6F76", "DADCE0", "F4F5F7"
ACCENT, AMBER = "1A73E8", "F9C80E"
HEAD, BODY, MONO = "Overpass", "Verdana", "Roboto Mono"


def rgb(h):
    return RGBColor.from_string(h.lstrip("#").upper())


def box(slide, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE, radius=None):
    s = slide.shapes.add_shape(shape, Pt(x), Pt(y), Pt(w), Pt(h))
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line); s.line.width = Pt(1)
    else:
        s.line.fill.background()
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    return s


def text(slide, x, y, w, h, runs, size=14, font=BODY, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         spacing=1.15, inset=0):
    """runs: str, or list of paragraphs; a paragraph is str or list of (text, dict) runs."""
    tb = slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Pt(inset)
    tf.vertical_anchor = anchor
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        parts = para if isinstance(para, list) else [(para, {})]
        for t, st in parts:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = st.get("font", font)
            f.size = Pt(st.get("size", size))
            f.bold = st.get("bold", bold)
            f.italic = st.get("italic", False)
            f.color.rgb = rgb(st.get("color", color))
    return tb


def chrome(slide, n, eyebrow, title):
    box(slide, 36, 30, 28, 4, fill=ACCENT)
    text(slide, 36, 40, 600, 16, eyebrow.upper(), size=9, font=HEAD, color=ACCENT, bold=True)
    text(slide, 36, 56, 648, 44, title, size=24, font=HEAD, bold=True, spacing=1.0)
    text(slide, 36, 378, 400, 14, "Apps Script for GTM  ·  Part 1  ·  svgslid.es", size=7.5, color=GREY)
    text(slide, 600, 378, 84, 14, str(n), size=7.5, color=GREY, align=PP_ALIGN.RIGHT)


def code_panel(slide, x, y, w, h, key, max_size=12):
    src = G.CODE[key]
    lines = src.split("\n")
    longest = max(len(l) for l in lines)
    size = min(max_size, (w - 30) / (longest * 0.62), (h - 40) / (len(lines) * 1.3))
    h = min(h, len(lines) * size * 1.3 + 46)
    box(slide, x, y, w, h, fill=G.DARK["bg"][1:], shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.04)
    # dots
    for i, c in enumerate(("FF5F57", "FEBC2E", "28C840")):
        box(slide, x + 12 + i * 11, y + 10, 6, 6, fill=c, shape=MSO_SHAPE.OVAL)
    paras, cur = [], []
    for k, t in G.tokens(src):
        pieces = t.split("\n")
        for j, piece in enumerate(pieces):
            if j:
                paras.append(cur); cur = []
            if piece:
                st = {"color": G.DARK.get(k, G.DARK["tx"])[1:]}
                if k == "cm":
                    st["italic"] = True
                cur.append((piece, st))
    paras.append(cur)
    paras = [p if p else [(" ", {"color": G.DARK["tx"][1:]})] for p in paras]
    text(slide, x + 14, y + 24, w - 28, h - 34, paras, size=round(size, 1), font=MONO, color=G.DARK["tx"][1:], spacing=1.2)


def bullets(slide, x, y, w, items, size=12, gap=10):
    paras = []
    for i, b in enumerate(items):
        paras.append([("■  ", {"color": ACCENT, "size": size * 0.6}), (b, {})])
    tb = text(slide, x, y, w, 260, paras, size=size, spacing=1.25)
    for p in tb.text_frame.paragraphs:
        p.space_after = Pt(gap)
    return tb


def build(out):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Pt(W), Pt(H)
    blank = prs.slide_layouts[6]
    for n, s in enumerate(G.SLIDES, start=1):
        sl = prs.slides.add_slide(blank)
        k = s["kind"]
        if k == "title":
            box(sl, 0, 0, W, H, fill="FFFFFF")
            box(sl, 36, 64, 40, 6, fill=ACCENT)
            text(sl, 36, 84, 360, 120, s["title"], size=44, font=HEAD, bold=True, spacing=0.95)
            text(sl, 36, 200, 330, 70, s["sub"], size=15, color=GREY, spacing=1.25)
            text(sl, 36, 360, 300, 16, s["foot"], size=9, color=GREY)
            box(sl, 400, 70, 284, 230, fill=G.DARK["bg"][1:], shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
            for i, c in enumerate(("FF5F57", "FEBC2E", "28C840")):
                box(sl, 414 + i * 11, 82, 6, 6, fill=c, shape=MSO_SHAPE.OVAL)
            demo = [[("=", {"color": "E6E6E6"}), ("FITS", {"color": "82AAFF"}), ("(D2, E2)", {"color": "E6E6E6"})],
                    [("// OK", {"color": "7F848E", "italic": True})], [(" ", {})],
                    [("buildDecks", {"color": "82AAFF"}), ("()", {"color": "E6E6E6"})],
                    [("// 24 account decks, filled", {"color": "7F848E", "italic": True})], [(" ", {})],
                    [("draftFollowUps", {"color": "82AAFF"}), ("()", {"color": "E6E6E6"})],
                    [("// 9 drafts, 0 sent", {"color": "7F848E", "italic": True})]]
            text(sl, 418, 102, 250, 190, demo, size=13, font=MONO, spacing=1.2)
        elif k == "text":
            chrome(sl, n, s["eyebrow"], s["title"])
            bullets(sl, 36, 124, 620, s["bullets"], size=17, gap=16)
        elif k == "split":
            chrome(sl, n, s["eyebrow"], s["title"])
            for i, (h, items) in enumerate((s["left"], s["right"])):
                x = 36 + i * 330
                box(sl, x, 116, 312, 236, fill=TINT if i else "FFFFFF", line=RULE, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
                if i == 0:
                    box(sl, x, 116, 6, 236, fill=ACCENT)
                text(sl, x + 22, 134, 270, 26, h, size=17, font=HEAD, bold=True)
                bullets(sl, x + 22, 170, 272, items, size=12, gap=9)
        elif k == "code":
            chrome(sl, n, s["eyebrow"], s["title"])
            bullets(sl, 36, 124, 216, s["bullets"], size=12.5, gap=12)
            code_panel(sl, 266, 112, 418, 254, s["code"])
        elif k == "steps":
            chrome(sl, n, s["eyebrow"], s["title"])
            for i, st in enumerate(s["steps"]):
                y = 118 + i * 50
                c = box(sl, 36, y, 28, 28, fill=ACCENT, shape=MSO_SHAPE.OVAL)
                text(sl, 36, y + 5, 28, 20, str(i + 1), size=12, font=HEAD, bold=True, color="FFFFFF", align=PP_ALIGN.CENTER)
                text(sl, 78, y + 4, 600, 30, st, size=13.5)
        elif k == "recap":
            chrome(sl, n, s["eyebrow"], s["title"])
            for i, (fn, d) in enumerate(s["items"]):
                y = 116 + i * 50
                box(sl, 36, y, 648, 42, fill=TINT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.15)
                text(sl, 50, y + 11, 190, 22, fn, size=13, font=MONO, color=ACCENT, bold=True)
                text(sl, 250, y + 12, 420, 22, d, size=12.5)
        elif k == "next":
            box(sl, 0, 0, W, H, fill=INK)
            box(sl, 36, 30, 28, 4, fill=AMBER)
            text(sl, 36, 40, 600, 16, s["eyebrow"].upper(), size=9, font=HEAD, color=AMBER, bold=True)
            text(sl, 36, 56, 648, 50, s["title"], size=32, font=HEAD, bold=True, color="FFFFFF")
            paras = [[("→  ", {"color": AMBER}), (b, {"color": "FFFFFF"})] for b in s["bullets"]]
            tb = text(sl, 36, 130, 620, 200, paras, size=16, spacing=1.25)
            for p in tb.text_frame.paragraphs:
                p.space_after = Pt(12)
            text(sl, 36, 360, 500, 16, s["foot"], size=9, color="9AA0A6")
            text(sl, 600, 378, 84, 14, str(n), size=7.5, color="9AA0A6", align=PP_ALIGN.RIGHT)
    prs.save(out)


if __name__ == "__main__":
    build(sys.argv[1])
    print("ok", sys.argv[1])
