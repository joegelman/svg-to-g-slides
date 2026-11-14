"""SVG to Slides solution brief (Letter, 2 pages), built from the brand tokens in brands.SVGS.

Every text box carries alt-text title "slot:<key>" matching a row on the messaging sheet's
Messages tab, so Collateral > Sync all keeps it in step with the master. Icons carry
"icon:<key>" (Icons tab). Copy lives in BRIEF below; the same rows go to the sheet.
"""
import sys
from pathlib import Path
from pptx.util import Inches
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import make_templates as mt
from brands import SVGS
import vec

ROOT = HERE.parent.parent
ICON = "/home/claude/node_modules/@phosphor-icons/core/assets/fill/%s-fill.svg"
OUT = HERE / "out"
C = {r[0]: RGBColor.from_string(r[1].lstrip("#")) for r in SVGS["colors"]}
TYPE = {r[0]: r for r in SVGS["type"]}

# key: (role, text, budget, used in). Keys without "sb_" are shared with the other assets.
BRIEF = {
    "sb_eyebrow": ("eyebrow", "New in version 1.2", 28),
    "sb_headline": ("headline", "Reshape any shape in Google Slides", 40),
    "sb_subhead": ("subhead", "Bring SVGs in as native shapes, then edit points, curves and corners right on the slide. A free Chrome extension.", 190),
    "sb_hero_caption": ("label", "Three cards, twelve corners, one drag. Recorded in Google Slides.", 70),
    "sb_problem_title": ("title", "The problem", 24),
    "sb_problem_body": ("body", "Google Slides doesn't support SVG files, and it can recolour and resize a shape but not reshape it. Edit points works only on lines and polylines you draw.", 170),
    "sb_solution_title": ("title", "How SVG to Slides fixes it", 30),
    "sb_solution_body": ("body", "Drag an SVG onto the slide and it lands as native shapes. Double-click any shape and a vector editor opens in place, at the shape's exact size and position.", 170),
    "sb_caps_title": ("title", "What's new in 1.2", 30),
    "sb_cap_1_title": ("title", "Edit Shape", 18),
    "sb_cap_1_body": ("body", "Drag points and curve handles, add or remove points, and select several at once. Undo, redo and zoom work as in Figma.", 140),
    "sb_cap_2_title": ("title", "Round corners", 18),
    "sb_cap_2_body": ("body", "Drag a handle inside any corner, or type a pixel radius. Select several shapes and every corner rounds together.", 140),
    "sb_cap_3_title": ("title", "Any shape", 18),
    "sb_cap_3_body": ("body", "Works on Slides' own shapes, arrows, callouts, lines, text boxes and WordArt. Text inside a shape stays editable.", 140),
    "sb_cap_4_title": ("title", "Layers stay put", 18),
    "sb_cap_4_body": ("body", "Shapes above the one you're editing stay visible. Done puts each shape back in its place in the stack.", 140),
    "sb_how_title": ("title", "How it works", 30),
    "step_1_title": ("title", "Drag", 12),
    "step_1_body": ("body", "Drag an .svg file onto an open Google Slides tab.", 60),
    "step_2_title": ("title", "Place", 12),
    "step_2_body": ("body", "Click where it goes. It lands as native shapes.", 60),
    "step_3_title": ("title", "Reshape", 12),
    "step_3_body": ("body", "Double-click any shape and click Edit Shape to reshape it.", 60),
    "sb_changes_title": ("title", "What changes when a Slides shape converts", 44),
    "sb_changes_body": ("body", "Shapes lose their adjustment handles.\nLines lose connection points, and arrowheads become separate shapes.\n3D shapes keep their shading as flat colours.\nWordArt becomes outlined letters.\nCancel puts the original back.", 230),
    "stat_1_value": ("stat", "5.0", 6),
    "stat_1_label": ("label", "Chrome Web Store rating", 26),
    "stat_2_value": ("stat", "0", 6),
    "stat_2_label": ("label", "Google permissions needed", 26),
    "stat_3_value": ("stat", "25", 6),
    "stat_3_label": ("label", "files per drop", 26),
    "sb_boilerplate": ("body", "SVG to Slides is a free Chrome extension that turns SVG files into native, editable shapes in Google Slides. It converts in your browser and needs no access to your Google account.", 200),
    "cta": ("cta", "Add to Chrome", 18),
    "cta_url": ("label", "svgslid.es/chrome", 24),
    "free_line": ("label", "Free to use, forever. No sign-up.", 40),
    "legal": ("legal", "Google Slides, Google Docs and Google Drawings are trademarks of Google LLC.", 90),
}
ICONS = {"sb_cap_1": "bezier-curve", "sb_cap_2": "sliders", "sb_cap_3": "squares-four", "sb_cap_4": "stack",
         "step_1": "hand-grabbing", "step_2": "cursor-click", "step_3": "pen-nib"}
mt.LINE = {k: v[1] for k, v in BRIEF.items()}


def slot(p, key, x, y, w, h, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    r = TYPE[BRIEF[key][0]]
    return p.text(key, x, y, w, h, r[3], C[r[6]], r[1], r[2] != "Regular", align, anchor, spacing=r[5])


def icon(p, key, x, y, size, token):
    vec.place_svg(p.s, ICON % ICONS[key], x, y, size, fill=str(C[token]), tag=f"icon:{key}")


def header(p, label):
    vec.place_svg(p.s, ROOT / "cloud/static/mark.svg", 0.6, 0.5, 0.5, tag="mark")
    p.text("wordmark", 1.25, 0.5, 3, 0.5, 16, C["ink"], "Overpass", True, anchor=MSO_ANCHOR.MIDDLE, text="SVG to Slides", slot=False)
    p.text("doc_label", 4.9, 0.5, 3.0, 0.5, 9, C["grey"], "Verdana", False, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE, text=label, slot=False)


def picture(p, path, x, y, w, name):
    pic = p.s.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w))
    pic.name = name
    pic.line.color.rgb = C["rule"]
    return pic.height / 914400


def page1(prs):
    p = mt.Page(prs)
    header(p, "Solution brief")
    slot(p, "sb_eyebrow", 0.6, 1.45, 7.3, 0.28)
    slot(p, "sb_headline", 0.6, 1.75, 7.3, 1.05)
    slot(p, "sb_subhead", 0.6, 2.92, 6.8, 0.62)
    h = picture(p, HERE / "brief/round-corners.png", 0.6, 3.7, 7.3, "ui:brief-round-corners")
    slot(p, "sb_hero_caption", 0.6, 3.7 + h + 0.1, 7.3, 0.25)
    y = 3.7 + h + 0.55
    p.rect(0.6, y, 0.9, 0.06, C["amber"], "rule_accent")
    slot(p, "sb_problem_title", 0.6, y + 0.2, 3.4, 0.32)
    slot(p, "sb_problem_body", 0.6, y + 0.58, 3.4, 1.2)
    slot(p, "sb_solution_title", 4.5, y + 0.2, 3.4, 0.32)
    slot(p, "sb_solution_body", 4.5, y + 0.58, 3.4, 1.2)
    slot(p, "legal", 0.6, 10.48, 7.3, 0.25)


def page2(prs):
    p = mt.Page(prs)
    header(p, "Solution brief")
    slot(p, "sb_caps_title", 0.6, 1.3, 7.3, 0.32)
    for i in range(4):
        x, y = 0.6 + (i % 2) * 3.75, 1.75 + (i // 2) * 1.2
        icon(p, f"sb_cap_{i+1}", x, y, 0.3, "blue")
        slot(p, f"sb_cap_{i+1}_title", x + 0.45, y - 0.02, 3.0, 0.3)
        slot(p, f"sb_cap_{i+1}_body", x + 0.45, y + 0.32, 3.0, 0.8)
    p.rect(0.6, 4.15, 7.3, 0.01, C["rule"], "rule_mid")
    slot(p, "sb_how_title", 0.6, 4.3, 7.3, 0.32)
    for i in range(3):
        x = 0.6 + i * 2.5
        p.rect(x, 4.75, 0.42, 0.42, C["amber"], f"step_{i+1}_badge", MSO_SHAPE.OVAL)
        icon(p, f"step_{i+1}", x + 0.08, 4.83, 0.26, "ink")
        slot(p, f"step_{i+1}_title", x + 0.55, 4.79, 1.7, 0.32)
        slot(p, f"step_{i+1}_body", x, 5.27, 2.25, 0.6)
    p.rect(0.6, 6.0, 7.3, 0.01, C["rule"], "rule_mid2")
    picture(p, HERE / "brief/edit-points.png", 0.6, 6.2, 2.04, "ui:brief-edit-points")
    slot(p, "sb_changes_title", 3.0, 6.2, 4.9, 0.32)
    slot(p, "sb_changes_body", 3.0, 6.6, 4.9, 1.4)
    y = 8.25
    p.rect(0.6, y, 7.3, 0.9, C["tint"], "block_proof")
    for i in range(3):
        x = 0.9 + i * 2.4
        slot(p, f"stat_{i+1}_value", x, y + 0.08, 2.1, 0.45)
        slot(p, f"stat_{i+1}_label", x, y + 0.56, 2.1, 0.26)
    slot(p, "sb_boilerplate", 0.6, 9.3, 7.3, 0.42)
    p.rect(0.6, 9.9, 2.0, 0.42, C["blue"], "block_cta", MSO_SHAPE.ROUNDED_RECTANGLE).adjustments[0] = 0.5
    slot(p, "cta", 0.6, 9.9, 2.0, 0.42, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    slot(p, "cta_url", 2.8, 9.9, 1.9, 0.42, anchor=MSO_ANCHOR.MIDDLE)
    slot(p, "free_line", 4.7, 9.9, 3.2, 0.42, PP_ALIGN.RIGHT, MSO_ANCHOR.MIDDLE)
    slot(p, "legal", 0.6, 10.48, 7.3, 0.25)


if __name__ == "__main__":
    for k, (role, text, budget) in BRIEF.items():
        assert len(text) <= budget, (k, len(text), budget)
        assert "—" not in text, k
    OUT.mkdir(exist_ok=True)
    prs = mt.new(8.5, 11)
    page1(prs); page2(prs)
    prs.save(OUT / "svgs-solution-brief.pptx")
    print("ok", OUT / "svgs-solution-brief.pptx")
