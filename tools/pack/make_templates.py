"""Build the starter-pack Slides templates as .pptx (converted to Google Slides on upload).

Every text box that takes copy is named for its row in the messaging sheet and carries
alt-text title "slot:<key>", so a script or an agent can address it by name.
"""
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn

sys.path.insert(0, str(Path(__file__).parent))
from messages import LINE

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

INK = RGBColor(0x1C, 0x1E, 0x22)
GREY = RGBColor(0x6B, 0x6F, 0x76)
RULE = RGBColor(0xE3, 0xE5, 0xE8)
TINT = RGBColor(0xF4, 0xF5, 0xF7)
BLUE = RGBColor(0x00, 0x66, 0xFF)
AMBER = RGBColor(0xF9, 0xC8, 0x0E)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RED = RGBColor(0xE2, 0x40, 0x34)
HEAD, BODY = "Overpass", "Verdana"


class Page:
    def __init__(self, prs, ox=0.0, oy=0.0):
        self.s = prs.slides.add_slide(prs.slide_layouts[6])
        self.ox, self.oy = ox, oy

    def rect(self, x, y, w, h, fill, name="block", shape=MSO_SHAPE.RECTANGLE, line=None, dash=False):
        sh = self.s.shapes.add_shape(shape, Inches(x + self.ox), Inches(y + self.oy), Inches(w), Inches(h))
        sh.name = name
        sh.shadow.inherit = False
        st = sh._element.find(qn('p:style'))
        if st is not None:
            sh._element.remove(st)
        if fill is None:
            sh.fill.background()
        else:
            sh.fill.solid()
            sh.fill.fore_color.rgb = fill
        if line is None:
            sh.line.fill.background()
        else:
            sh.line.color.rgb = line
            sh.line.width = Pt(0.75)
            if dash:
                sh.line.dash_style = 4  # dash
        return sh

    def text(self, key, x, y, w, h, size, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, text=None, slot=True, spacing=1.15):
        tb = self.s.shapes.add_textbox(Inches(x + self.ox), Inches(y + self.oy), Inches(w), Inches(h))
        tb.name = key
        if slot:
            tb._element.nvSpPr.cNvPr.set("title", f"slot:{key}")
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.auto_size = MSO_AUTO_SIZE.NONE  # fixed box: no shrink or grow on import
        for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
            setattr(tf, m, 0)
        p = tf.paragraphs[0]
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = text if text is not None else LINE[key]
        f = r.font
        f.name, f.size, f.bold = font, Pt(size), bold
        f.color.rgb = color
        return tb

    def note(self, label, x, y, w, h):
        """Dashed placeholder a person replaces (logo, image, linked table)."""
        sh = self.rect(x, y, w, h, TINT, name=label, line=GREY, dash=True)
        tf = sh.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = label
        r.font.name, r.font.size, r.font.color.rgb = BODY, Pt(9), GREY
        return sh


def new(w, h):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(w), Inches(h)
    return prs


def one_pager_page(prs, ox=0.0, oy=0.0, bleed=0.0):
    p = Page(prs, ox, oy)
    W, H = 8.5, 11.0
    b = bleed
    p.rect(-b, -b, W + 2 * b, 3.55 + b, INK, "block_hero")
    p.note("Logo: drop an SVG here", 0.6, 0.55, 1.5, 0.45)
    p.text("eyebrow", 0.6, 1.3, 7.3, 0.3, 11, AMBER, HEAD, True)
    p.text("headline", 0.6, 1.62, 7.3, 1.05, 30, WHITE, HEAD, True, spacing=1.0)
    p.text("subhead", 0.6, 2.72, 6.6, 0.62, 11.5, WHITE, spacing=1.3)
    for i in range(3):
        x = 0.6 + i * 2.5
        p.rect(x, 4.05, 0.42, 0.42, AMBER, f"icon_{i+1}", MSO_SHAPE.OVAL)
        p.text(f"benefit_{i+1}_title", x, 4.62, 2.2, 0.32, 14, INK, HEAD, True)
        p.text(f"benefit_{i+1}_body", x, 4.98, 2.2, 0.95, 10, GREY, spacing=1.35)
    p.rect(0.6, 6.3, 7.3, 1.45, TINT, "block_proof")
    for i in range(3):
        x = 0.9 + i * 2.4
        p.text(f"stat_{i+1}_value", x, 6.52, 2.1, 0.6, 30, BLUE, HEAD, True)
        p.text(f"stat_{i+1}_label", x, 7.2, 2.1, 0.3, 10, GREY)
    p.note("Linked table or chart from the messaging sheet goes here", 0.6, 8.05, 7.3, 1.45)
    p.rect(0.6, 9.85, 2.3, 0.5, BLUE, "block_cta", MSO_SHAPE.ROUNDED_RECTANGLE)
    p.text("cta", 0.6, 9.85, 2.3, 0.5, 12, WHITE, HEAD, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    p.text("cta_url", 3.1, 9.85, 3.0, 0.5, 11, INK, BODY, False, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    p.text("legal", 0.6, 10.48, 7.3, 0.25, 7.5, GREY)
    return p


def one_pager():
    prs = new(8.5, 11)
    one_pager_page(prs)
    prs.save(OUT / "One-pager (Letter).pptx")


def one_pager_bleed():
    b = 0.125
    prs = new(8.5 + 2 * b, 11 + 2 * b)
    p = one_pager_page(prs, b, b, b)
    # guides: delete before export
    trim = p.rect(0, 0, 8.5, 11, None, "GUIDE trim line (delete before export)", line=RED, dash=True)
    safe = p.rect(0.25, 0.25, 8.0, 10.5, None, "GUIDE safe margin (delete before export)", line=BLUE, dash=True)
    p.text("guide_label", 0.3, 0.06, 6, 0.18, 6.5, RED, BODY, text="Red: trim (8.5 x 11 in). Blue: safe margin (0.25 in). Canvas adds 0.125 in bleed per side. Delete guides before export.", slot=False)
    prs.save(OUT / "One-pager, print with bleed (8.75 x 11.25 in).pptx")


def solution_brief():
    prs = new(8.5, 11)
    p = Page(prs)
    p.rect(0, 0, 8.5, 0.9, INK, "block_header")
    p.note("Logo: drop an SVG here", 0.6, 0.24, 1.4, 0.42)
    p.text("doc_type", 5.4, 0.3, 2.5, 0.3, 10, WHITE, HEAD, True, PP_ALIGN.RIGHT, text="SOLUTION BRIEF", slot=False)
    p.text("eyebrow", 0.6, 1.35, 7.3, 0.3, 11, BLUE, HEAD, True)
    p.text("headline", 0.6, 1.68, 7.3, 1.05, 30, INK, HEAD, True, spacing=1.0)
    p.text("subhead", 0.6, 2.8, 7.0, 0.62, 11.5, GREY, spacing=1.3)
    p.rect(0.6, 3.75, 3.5, 2.6, TINT, "block_challenge")
    p.text("challenge_title", 0.85, 3.98, 3.0, 0.32, 14, INK, HEAD, True)
    p.text("challenge_body", 0.85, 4.4, 3.0, 1.75, 10, INK, spacing=1.4)
    p.rect(4.4, 3.75, 3.5, 2.6, INK, "block_solution")
    p.text("solution_title", 4.65, 3.98, 3.0, 0.32, 14, AMBER, HEAD, True)
    p.text("solution_body", 4.65, 4.4, 3.0, 1.75, 10, WHITE, spacing=1.4)
    p.note("Product image or diagram", 0.6, 6.7, 7.3, 3.2)
    p.text("legal", 0.6, 10.48, 7.3, 0.25, 7.5, GREY)

    p = Page(prs)
    p.rect(0, 0, 8.5, 0.9, INK, "block_header")
    p.text("doc_type", 0.6, 0.3, 4, 0.3, 10, WHITE, HEAD, True, text="HOW IT WORKS", slot=False)
    for i in range(3):
        x = 0.6 + i * 2.5
        p.rect(x, 1.4, 0.5, 0.5, AMBER, f"step_{i+1}_badge", MSO_SHAPE.OVAL)
        p.text(f"step_{i+1}_num", x, 1.4, 0.5, 0.5, 14, INK, HEAD, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, text=str(i + 1), slot=False)
        p.text(f"step_{i+1}", x, 2.05, 2.2, 0.7, 12, INK, HEAD, True, spacing=1.2)
    p.note("Linked table from the messaging sheet (Data tab): capabilities by plan", 0.6, 3.2, 7.3, 2.5)
    p.rect(0.6, 6.05, 7.3, 1.75, TINT, "block_quote")
    p.text("quote", 0.9, 6.3, 6.7, 0.9, 14, INK, HEAD, True, spacing=1.25)
    p.text("quote_source", 0.9, 7.3, 6.7, 0.3, 10, GREY)
    p.text("boilerplate", 0.6, 8.2, 7.3, 0.75, 10, GREY, spacing=1.4)
    p.rect(0.6, 9.4, 2.3, 0.5, BLUE, "block_cta", MSO_SHAPE.ROUNDED_RECTANGLE)
    p.text("cta", 0.6, 9.4, 2.3, 0.5, 12, WHITE, HEAD, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    p.text("cta_url", 3.1, 9.4, 3.0, 0.5, 11, INK, BODY, False, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    p.text("legal", 0.6, 10.48, 7.3, 0.25, 7.5, GREY)
    prs.save(OUT / "Solution brief (Letter, 2 pages).pptx")


def whitepaper():
    prs = new(8.5, 11)
    p = Page(prs)
    p.rect(0, 0, 8.5, 11, INK, "block_cover")
    p.rect(0.6, 0.6, 0.9, 0.12, AMBER, "block_accent")
    p.note("Logo: drop an SVG here", 0.6, 9.75, 1.5, 0.45)
    p.text("doc_type", 0.6, 3.3, 7, 0.3, 11, AMBER, HEAD, True, text="WHITEPAPER", slot=False)
    p.text("wp_title", 0.6, 3.7, 7.0, 1.7, 38, WHITE, HEAD, True, spacing=1.0)
    p.text("wp_subtitle", 0.6, 5.5, 6.4, 0.75, 14, WHITE, spacing=1.3)
    p.text("wp_date", 5.4, 9.85, 2.5, 0.3, 10, WHITE, BODY, False, PP_ALIGN.RIGHT)

    p = Page(prs)
    p.text("running_head", 0.6, 0.5, 5, 0.25, 8, GREY, HEAD, True, text="A PRACTICAL GUIDE TO SECURE FILE TRANSFER", slot=False)
    p.rect(0.6, 0.82, 7.3, 0.01, RULE, "rule_top")
    p.text("wp_h2", 0.6, 1.2, 7.3, 0.6, 24, INK, HEAD, True)
    p.text("wp_body_1", 0.6, 2.05, 3.5, 3.3, 10.5, INK, spacing=1.5)
    p.text("wp_body_2", 4.4, 2.05, 3.5, 3.3, 10.5, INK, spacing=1.5)
    p.rect(0.6, 5.7, 7.3, 1.5, TINT, "block_pull")
    p.text("wp_pull", 0.9, 5.95, 6.7, 1.0, 20, BLUE, HEAD, True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.15)
    p.note("Linked chart from the messaging sheet (Data tab)", 0.6, 7.55, 7.3, 2.5)
    p.text("page_num", 7.4, 10.48, 0.5, 0.25, 8, GREY, BODY, False, PP_ALIGN.RIGHT, text="2", slot=False)
    p.text("legal", 0.6, 10.48, 6.5, 0.25, 7.5, GREY)

    p = Page(prs)
    p.rect(0, 6.2, 8.5, 4.8, TINT, "block_back")
    p.text("about_title", 0.6, 6.7, 7.3, 0.35, 14, INK, HEAD, True, text="About Example Co.", slot=False)
    p.text("boilerplate", 0.6, 7.15, 6.4, 0.9, 10.5, GREY, spacing=1.45)
    p.rect(0.6, 8.5, 2.3, 0.5, BLUE, "block_cta", MSO_SHAPE.ROUNDED_RECTANGLE)
    p.text("cta", 0.6, 8.5, 2.3, 0.5, 12, WHITE, HEAD, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    p.text("cta_url", 3.1, 8.5, 3.0, 0.5, 11, INK, BODY, False, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)
    p.text("legal", 0.6, 10.48, 7.3, 0.25, 7.5, GREY)
    prs.save(OUT / "Whitepaper (Letter, cover + inside + back).pptx")


def battlecard():
    prs = new(11, 8.5)
    p = Page(prs)
    p.rect(0, 0, 11, 1.0, INK, "block_header")
    p.text("doc_type", 0.5, 0.2, 6, 0.25, 9, AMBER, HEAD, True, text="BATTLECARD  ·  INTERNAL ONLY", slot=False)
    p.text("card_title", 0.5, 0.45, 7, 0.4, 18, WHITE, HEAD, True, text="Relay vs. Competitor", slot=False)
    p.note("Logo", 9.2, 0.28, 1.3, 0.44)
    # why we win
    p.text("col_1", 0.5, 1.35, 3.1, 0.3, 12, BLUE, HEAD, True, text="WHY WE WIN", slot=False)
    for i in range(3):
        y = 1.8 + i * 1.05
        p.rect(0.5, y, 3.1, 0.9, TINT, f"block_win_{i+1}")
        p.text(f"win_{i+1}", 0.68, y, 2.75, 0.9, 10.5, INK, HEAD, True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)
    # claims
    p.text("col_2", 3.95, 1.35, 3.1, 0.3, 12, BLUE, HEAD, True, text="THEY SAY / WE ASK", slot=False)
    for i in range(2):
        y = 1.8 + i * 1.6
        p.rect(3.95, y, 3.1, 1.45, None, f"block_claim_{i+1}", line=RULE)
        p.text(f"claim_{i+1}", 4.13, y + 0.14, 2.75, 0.55, 10.5, GREY, spacing=1.25)
        p.text(f"answer_{i+1}", 4.13, y + 0.75, 2.75, 0.6, 10.5, INK, HEAD, True, spacing=1.2)
    # landmines
    p.text("col_3", 7.4, 1.35, 3.1, 0.3, 12, BLUE, HEAD, True, text="QUESTIONS TO PLANT", slot=False)
    for i in range(2):
        y = 1.8 + i * 1.05
        p.rect(7.4, y, 3.1, 0.9, INK, f"block_landmine_{i+1}")
        p.text(f"landmine_{i+1}", 7.58, y, 2.75, 0.9, 10.5, WHITE, HEAD, True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)
    p.rect(0.5, 5.25, 10, 1.9, TINT, "block_features")
    for i in range(3):
        x = 0.8 + i * 3.3
        p.text(f"benefit_{i+1}_title", x, 5.5, 3.0, 0.32, 13, INK, HEAD, True)
    p.note("Linked comparison table from the messaging sheet (Data tab)", 0.8, 5.95, 9.4, 1.0)
    p.text("cta_url", 0.5, 7.6, 5, 0.3, 10, INK)
    p.text("legal", 5.5, 7.62, 5, 0.25, 7.5, GREY, BODY, False, PP_ALIGN.RIGHT)
    prs.save(OUT / "Battlecard (Letter landscape).pptx")


if __name__ == "__main__":
    one_pager(); one_pager_bleed(); solution_brief(); whitepaper(); battlecard()
    for f in sorted(OUT.glob("*.pptx")):
        print(f.name, f.stat().st_size)
