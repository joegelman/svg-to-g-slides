"""SVG to Slides brand templates, built from the same tokens as the style sheet (brands.SVGS)."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import make_templates as mt
from brands import SVGS
import vec

ICON = '/home/claude/work/icons/node_modules/@phosphor-icons/core/assets/fill/%s-fill.svg'
STEP_ICONS = ['hand-grabbing', 'cursor-click', 'clipboard-text']
BEN_ICONS = ['bezier-curve', 'stack', 'magic-wand', 'seal-check']


def icon(p, key, name, x, y, size, token):
    vec.place_svg(p.s, ICON % name, x, y, size, fill=str(C[token]), tag=f'icon:{key}')

OUT = Path(__file__).parent / "out2"
C = {r[0]: RGBColor.from_string(r[1].lstrip("#")) for r in SVGS["colors"]}
TYPE = {r[0]: r for r in SVGS["type"]}
LINE = {m[0]: m[3] for m in SVGS["messages"]}
mt.LINE = LINE


def slot(p, key, role, x, y, w, h, kind="print", align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    r = TYPE[role]
    size = r[3] if kind == "print" else r[4]
    return p.text(key, x, y, w, h, size, C[r[6]], r[1], r[2] != "Regular", align, anchor, spacing=r[5])


def mark(p, x, y, h):
    pic = p.s.shapes.add_picture(str(OUT / "mark.png"), Inches(x), Inches(y), height=Inches(h))
    pic.name = "mark"
    p.text("wordmark", x + h + 0.15, y, 3, h, 16 if h < 0.7 else 22, C["ink"], "Overpass", True, anchor=MSO_ANCHOR.MIDDLE, text="SVG to Slides", slot=False)


def one_pager():
    prs = mt.new(8.5, 11); p = mt.Page(prs)
    mark(p, 0.6, 0.55, 0.55)
    slot(p, "eyebrow", "eyebrow", 0.6, 1.55, 7.3, 0.3)
    slot(p, "headline", "headline", 0.6, 1.88, 7.3, 0.7)
    slot(p, "subhead", "subhead", 0.6, 2.68, 7.0, 0.95)
    p.rect(0.6, 3.85, 0.9, 0.06, C["amber"], "rule_accent")
    slot(p, "problem_title", "title", 0.6, 4.1, 3.2, 0.32)
    slot(p, "problem_body", "body", 0.6, 4.48, 3.3, 1.3)
    for i in range(3):
        y = 4.1 + i * 0.62
        p.rect(4.4, y, 0.42, 0.42, C["amber"], f"step_{i+1}_badge", MSO_SHAPE.OVAL)
        icon(p, f"step_{i+1}", STEP_ICONS[i], 4.4 + 0.08, y + 0.08, 0.26, "ink")
        slot(p, f"step_{i+1}_title", "title", 4.98, y - 0.02, 0.9, 0.3)
        slot(p, f"step_{i+1}_body", "body", 5.9, y + 0.04, 2.0, 0.45)
    p.rect(0.6, 6.15, 7.3, 0.01, C["rule"], "rule_mid")
    for i in range(4):
        x, y = 0.6 + (i % 2) * 3.75, 6.45 + (i // 2) * 0.62
        icon(p, f"benefit_{i+1}", BEN_ICONS[i], x, y - 0.03, 0.26, "blue")
        slot(p, f"benefit_{i+1}", "body", x + 0.4, y, 3.1, 0.5)
    p.rect(0.6, 7.95, 7.3, 1.45, C["tint"], "block_proof")
    for i in range(3):
        x = 0.9 + i * 2.4
        slot(p, f"stat_{i+1}_value", "stat", x, 8.17, 2.1, 0.6)
        slot(p, f"stat_{i+1}_label", "label", x, 8.85, 2.1, 0.3)
    p.rect(0.6, 9.75, 2.0, 0.5, C["blue"], "block_cta", MSO_SHAPE.ROUNDED_RECTANGLE).adjustments[0] = 0.5
    slot(p, "cta", "cta", 0.6, 9.75, 2.0, 0.5, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    slot(p, "cta_url", "label", 2.8, 9.75, 1.9, 0.5, anchor=MSO_ANCHOR.MIDDLE)
    slot(p, "free_line", "label", 4.7, 9.75, 3.2, 0.5, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    slot(p, "legal", "legal", 0.6, 10.48, 7.3, 0.25)
    prs.save(OUT / "svgs-one-pager-v2.pptx")


def deck():
    prs = mt.new(13.333, 7.5); p = mt.Page(prs)
    mark(p, 0.8, 0.7, 0.7)
    slot(p, "eyebrow", "eyebrow", 0.8, 2.3, 10, 0.4, "deck")
    slot(p, "headline", "headline", 0.8, 2.75, 11.5, 0.9, "deck")
    slot(p, "subhead", "subhead", 0.8, 3.8, 9.5, 1.3, "deck")
    p.rect(0.8, 5.6, 2.6, 0.62, C["blue"], "block_cta", MSO_SHAPE.ROUNDED_RECTANGLE).adjustments[0] = 0.5
    slot(p, "cta", "cta", 0.8, 5.6, 2.6, 0.62, "deck", PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    slot(p, "cta_url", "label", 3.65, 5.6, 3, 0.62, "deck", anchor=MSO_ANCHOR.MIDDLE)
    slot(p, "legal", "legal", 0.8, 6.85, 11.5, 0.3, "deck")
    p = mt.Page(prs)
    mark(p, 0.8, 0.55, 0.5)
    p.text("slide_title", 0.8, 1.5, 11, 0.7, 32, C["ink"], "Overpass", True, text="How it works", slot=False)
    for i in range(3):
        x = 0.8 + i * 4.0
        p.rect(x, 2.8, 0.7, 0.7, C["amber"], f"step_{i+1}_badge", MSO_SHAPE.OVAL)
        icon(p, f"step_{i+1}", STEP_ICONS[i], x + 0.14, 2.8 + 0.14, 0.42, "ink")
        slot(p, f"step_{i+1}_title", "title", x, 3.75, 3.4, 0.5, "deck")
        slot(p, f"step_{i+1}_body", "body", x, 4.3, 3.4, 1.0, "deck")
    slot(p, "free_line", "label", 0.8, 6.3, 6, 0.4, "deck")
    slot(p, "legal", "legal", 0.8, 6.85, 11.5, 0.3, "deck")
    p = mt.Page(prs)
    mark(p, 0.8, 0.55, 0.5)
    p.text("slide_title", 0.8, 1.35, 11, 0.7, 32, C["ink"], "Overpass", True, text="In your deck", slot=False)
    p.rect(2.75, 2.25, 7.84, 4.41, C["tint"], "ui_background", line=C["rule"])
    h, n, t = vec.place_svg(p.s, OUT / "gemini-ui.svg", 2.75, 2.25, 7.84, tag="ui:editor_mock", text_tag="ui_text")
    print("ui mock:", round(h, 2), "in tall,", n, "shapes,", t, "text boxes")
    slot(p, "legal", "legal", 0.8, 6.95, 11.5, 0.3, "deck")
    prs.save(OUT / "svgs-deck-v2.pptx")


if __name__ == "__main__":
    one_pager(); deck()
