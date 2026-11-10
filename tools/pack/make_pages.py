"""Page-recipe decks for SVG to Slides: a solution page and a product page, one block per slide,
plus the expanded UI library and the recipes workbook."""
from pathlib import Path
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import make_templates as mt, make_brand as mb, make_library as ml, vec, ui_kit
from make_brand import C, slot, mark, icon

OUT = Path("pages"); OUT.mkdir(exist_ok=True); Path("ui").mkdir(exist_ok=True)
for n, (f, _, _) in ui_kit.UIS.items(): Path(f"ui/{n}.svg").write_text(f())
POS = "Drag an SVG into your deck. SVG to Slides converts it into native Google Slides shapes, so you can edit individual elements, change colours, and resize without losing quality."
# key, role, recipe, source (Architecture key or project context), line, budget, used in
M = [
 ("sol_hero_eyebrow", "eyebrow", "R1 Hero", "champion", "For product marketing teams", 32, "Solution"),
 ("sol_hero_headline", "headline", "R1 Hero", "context", "Crisp icons and logos in Google Slides", 40, "Solution"),
 ("sol_hero_subhead", "subhead", "R1 Hero", "positioning", POS, 190, "Solution"),
 ("proof_title", "title", "R2 Proof bar", "proof", "Live on the Chrome Web Store", 40, "Solution, Product"),
 ("sol_problem_title", "title", "R3 Problem", "problem", "Google Slides doesn't support SVG files", 44, "Solution"),
 ("sol_problem_body", "body", "R3 Problem", "problem", "Your options are to flatten them into PNGs or take the long way through EMF conversion, Google Drawings, and copy-paste.", 130, "Solution"),
 ("sol_pillars_title", "title", "R4 Pillar trio", "", "What your team gets", 30, "Solution"),
 ("sol_pillar_1_title", "title", "R4 Pillar trio", "benefit_1", "True vectors", 18, "Solution"),
 ("sol_pillar_1_body", "body", "R4 Pillar trio", "benefit_1", "True vectors, native to Google Workspace.", 70, "Solution"),
 ("sol_pillar_2_title", "title", "R4 Pillar trio", "benefit_2", "Import once", 18, "Solution"),
 ("sol_pillar_2_body", "body", "R4 Pillar trio", "benefit_2", "Import once, then reuse the shape in themes, Docs and Drawings.", 70, "Solution"),
 ("sol_pillar_3_title", "title", "R4 Pillar trio", "benefit_4", "On-brand", 18, "Solution"),
 ("sol_pillar_3_body", "body", "R4 Pillar trio", "benefit_4", "Keep every team on-brand with the real logo.", 70, "Solution"),
 ("row_edit_eyebrow", "eyebrow", "R5 Feature row", "", "Edit", 14, "Solution, Product"),
 ("row_edit_title", "title", "R5 Feature row (capability-led)", "need_important", "Recolour with the fill picker", 34, "Solution, Product"),
 ("row_edit_body", "body", "R5 Feature row", "promise", "Every SVG path becomes a shape that behaves like one drawn in Slides: selectable, recolourable and sharp at any size.", 130, "Solution, Product"),
 ("row_reuse_eyebrow", "eyebrow", "R5 Feature row", "", "Reuse", 14, "Solution"),
 ("row_reuse_title", "title", "R5 Feature row (benefit-led)", "benefit_2", "Import once, use everywhere", 34, "Solution"),
 ("row_reuse_body", "body", "R5 Feature row", "benefit_2", "Import once, then reuse the shape in themes, Docs and Drawings.", 130, "Solution"),
 ("row_build_eyebrow", "eyebrow", "R5 Feature row", "", "Build", 14, "Solution"),
 ("row_build_title", "title", "R5 Feature row (benefit-led)", "benefit_3", "Build beyond basic Slides", 34, "Solution"),
 ("row_build_body", "body", "R5 Feature row", "benefit_3", "Animate elements, make templates and letterheads.", 130, "Solution"),
 ("grid_title", "title", "R7 Feature grid", "", "Ways to convert", 30, "Solution"),
 ("grid_1_title", "title", "R7 Feature grid (feature name)", "what it is", "Chrome extension", 22, "Solution, Product"),
 ("grid_1_body", "body", "R7 Feature grid", "how", "Drag an .svg onto an open Slides tab, click to place, press Cmd/Ctrl+V.", 90, "Solution"),
 ("grid_2_title", "title", "R7 Feature grid (feature name)", "secondary_1", "Slides add-on", 22, "Solution, Product"),
 ("grid_2_body", "body", "R7 Feature grid", "project context", "Pick files in a dialog, click Copy, paste into the slide.", 90, "Solution"),
 ("grid_3_title", "title", "R7 Feature grid (feature name)", "secondary_2", "Web converter", 22, "Solution, Product"),
 ("grid_3_body", "body", "R7 Feature grid", "project context", "Drop SVGs in a browser, get a Drive link to a PPTX with one slide per file.", 90, "Solution"),
 ("grid_4_title", "title", "R7 Feature grid (feature name)", "secondary_3", "Batch drop", 22, "Solution"),
 ("grid_4_body", "body", "R7 Feature grid", "secondary_3", "Drop up to 25 files at once.", 90, "Solution"),
 ("faq_title", "title", "R9 FAQ", "", "Questions", 20, "Solution, Product"),
 ("faq_1_q", "title", "R9 FAQ", "", "Is it free?", 40, "Solution, Product"),
 ("faq_1_a", "body", "R9 FAQ", "secondary_4", "Free to use, forever. No sign-up.", 110, "Solution, Product"),
 ("faq_2_q", "title", "R9 FAQ", "", "What permissions does it need?", 40, "Solution, Product"),
 ("faq_2_a", "body", "R9 FAQ", "unique", "The extension converts locally in the browser and asks for no Google permissions.", 110, "Solution, Product"),
 ("faq_3_q", "title", "R9 FAQ", "", "How many files at once?", 40, "Solution, Product"),
 ("faq_3_a", "body", "R9 FAQ", "proof log", "Up to 25 per drop in the extension. Larger batches go to the web converter.", 110, "Solution, Product"),
 ("faq_4_q", "title", "R9 FAQ", "", "Do gradients convert?", 40, "Solution, Product"),
 ("faq_4_a", "body", "R9 FAQ", "known limitations", "The web converter keeps gradients. The extension and add-on use the gradient's first colour.", 110, "Solution, Product"),
 ("sol_close_headline", "headline", "R10 Closing CTA", "how_1", "Drag in your first SVG", 40, "Solution"),
 ("prod_hero_eyebrow", "eyebrow", "R1 Hero", "category", "Chrome extension", 32, "Product"),
 ("prod_hero_headline", "headline", "R1 Hero (feature-led)", "category", "SVG import for Google Slides", 40, "Product"),
 ("prod_hero_subhead", "subhead", "R1 Hero", "how", "Drag an .svg onto an open Slides tab, click to place, press Cmd/Ctrl+V. Every path lands as a native shape.", 190, "Product"),
 ("prod_benefits_title", "title", "R6 Benefit list", "", "What you get", 30, "Product"),
 ("prod_how_title", "title", "R8 How it works", "", "How it works", 30, "Product"),
 ("row_private_eyebrow", "eyebrow", "R5 Feature row", "", "Permissions", 14, "Product"),
 ("row_private_title", "title", "R5 Feature row (feature-led)", "unique", "No Google permissions", 34, "Product"),
 ("row_private_body", "body", "R5 Feature row", "unique", "The extension converts locally in the browser and asks for no Google permissions.", 130, "Product"),
 ("row_shapes_eyebrow", "eyebrow", "R5 Feature row", "", "Shapes", 14, "Product"),
 ("row_shapes_title", "title", "R5 Feature row (feature-led)", "unique", "Every path is its own shape", 34, "Product"),
 ("row_shapes_body", "body", "R5 Feature row", "positioning", "Edit individual elements, change colours, and resize without losing quality.", 130, "Product"),
 ("facts_title", "title", "R11 Fact columns", "", "Three ways in", 30, "Product"),
 ("facts_1_body", "body", "R11 Fact columns", "project context", "Drag and drop onto the slide\nConverts in your browser\nUp to 25 files per drop", 110, "Product"),
 ("facts_2_body", "body", "R11 Fact columns", "project context", "Opens from the Extensions menu\nPick files in a dialog\nCopy, then paste into the slide", 110, "Product"),
 ("facts_3_body", "body", "R11 Fact columns", "project context", "Drop SVGs in a browser\nOne slide per file in a PPTX\nDrive link, kept for 7 days", 110, "Product"),
 ("prod_close_headline", "headline", "R10 Closing CTA", "cta", "Add it to Chrome", 40, "Product"),
]
for m in M: mb.LINE[m[0]] = m[4]
GREY = C["grey"]

def ui(p, name, x, y, w):
    h, n, t = vec.place_svg(p.s, f"ui/{name}.svg", x, y, w, tag=f"ui:{name}", text_tag=f"uitext:{name}")
    for sh in p.s.shapes:
        if sh.name.startswith(f"uitext:{name}"): sh._element.nvSpPr.cNvPr.set("title", f"ui:{name}")
    return h
def base(prs, recipe):
    p = mt.Page(prs); mark(p, 0.8, 0.5, 0.45)
    p.text("recipe_tag", 9.3, 0.58, 3.2, 0.3, 9, GREY, "Verdana", align=PP_ALIGN.RIGHT, text=recipe, slot=False)
    slot(p, "legal", "legal", 0.8, 7.0, 11.7, 0.3, "deck"); return p
def cta(p, x, y, center=False):
    p.rect(x, y, 2.6, 0.62, C["blue"], "block_cta", MSO_SHAPE.ROUNDED_RECTANGLE).adjustments[0] = 0.5
    slot(p, "cta", "cta", x, y, 2.6, 0.62, "deck", PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    slot(p, "cta_url", "label", x + 2.85, y, 3, 0.62, "deck", anchor=MSO_ANCHOR.MIDDLE)
def hero(prs, pre, uiname):
    p = base(prs, "R1 Hero")
    slot(p, f"{pre}_hero_eyebrow", "eyebrow", 0.8, 1.6, 6, 0.35, "deck")
    slot(p, f"{pre}_hero_headline", "headline", 0.8, 2.0, 6.1, 1.5, "deck")
    slot(p, f"{pre}_hero_subhead", "subhead", 0.8, 3.65, 5.9, 1.45, "deck")
    cta(p, 0.8, 5.3); slot(p, "free_line", "label", 0.8, 6.1, 6, 0.35, "deck")
    ui(p, uiname, 7.2, 1.85, 5.5)
def proof(prs):
    p = base(prs, "R2 Proof bar")
    slot(p, "proof_title", "title", 0.8, 1.6, 11, 0.5, "deck")
    p.rect(0.8, 2.5, 11.7, 2.6, C["tint"], "block_proof")
    for i in range(3):
        x = 1.3 + i * 3.9
        slot(p, f"stat_{i+1}_value", "stat", x, 3.0, 3.4, 0.9, "deck"); slot(p, f"stat_{i+1}_label", "label", x, 4.05, 3.4, 0.4, "deck")
    slot(p, "free_line", "label", 0.8, 5.5, 8, 0.4, "deck")
def row(prs, key, uiname, flip=False, uw=6.2):
    p = base(prs, "R5 Feature row")
    tx, ux = (7.3, 0.8) if flip else (0.8, 13.333 - 0.8 - uw)
    slot(p, f"row_{key}_eyebrow", "eyebrow", tx, 2.4, 5.2, 0.35, "deck")
    slot(p, f"row_{key}_title", "title", tx, 2.8, 5.2, 0.9, "deck")
    slot(p, f"row_{key}_body", "body", tx, 3.75, 5.0, 1.8, "deck")
    ui(p, uiname, ux, 1.8, uw)
def faq(prs):
    p = base(prs, "R9 FAQ"); slot(p, "faq_title", "title", 0.8, 1.5, 11, 0.5, "deck")
    for i in range(4):
        x, y = 0.8 + (i % 2) * 6.0, 2.4 + (i // 2) * 2.1
        p.rect(x, y, 5.6, 0.02, C["rule"], f"faq_rule_{i+1}")
        slot(p, f"faq_{i+1}_q", "title", x, y + 0.2, 5.5, 0.5, "deck"); slot(p, f"faq_{i+1}_a", "body", x, y + 0.75, 5.4, 1.1, "deck")
def close(prs, pre):
    p = base(prs, "R10 Closing CTA")
    slot(p, f"{pre}_close_headline", "headline", 0.8, 2.6, 11.7, 0.9, "deck", PP_ALIGN.CENTER)
    p.rect(5.37, 4.0, 2.6, 0.62, C["blue"], "block_cta", MSO_SHAPE.ROUNDED_RECTANGLE).adjustments[0] = 0.5
    slot(p, "cta", "cta", 5.37, 4.0, 2.6, 0.62, "deck", PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    slot(p, "cta_url", "label", 0.8, 4.8, 11.7, 0.4, "deck", PP_ALIGN.CENTER); slot(p, "free_line", "label", 0.8, 5.25, 11.7, 0.4, "deck", PP_ALIGN.CENTER)

def solution():
    prs = mt.new(13.333, 7.5)
    hero(prs, "sol", "slides-editor"); proof(prs)
    p = base(prs, "R3 Problem")
    slot(p, "sol_problem_title", "title", 0.8, 2.5, 5.2, 1.0, "deck"); slot(p, "sol_problem_body", "body", 0.8, 3.55, 5.0, 1.8, "deck")
    ui(p, "png-vs-shapes", 6.4, 2.0, 6.1)
    p = base(prs, "R4 Pillar trio"); slot(p, "sol_pillars_title", "title", 0.8, 1.5, 11, 0.5, "deck")
    for i, ic in enumerate(["bezier-curve", "stack", "seal-check"]):
        x = 0.8 + i * 4.0
        p.rect(x, 2.7, 0.8, 0.8, C["amber"], f"pillar_{i+1}_badge", MSO_SHAPE.OVAL); icon(p, f"pillar_{i+1}", ic, x + 0.17, 2.87, 0.46, "ink")
        slot(p, f"sol_pillar_{i+1}_title", "title", x, 3.8, 3.5, 0.5, "deck"); slot(p, f"sol_pillar_{i+1}_body", "body", x, 4.35, 3.4, 1.4, "deck")
    row(prs, "edit", "fill-picker"); row(prs, "reuse", "reuse", True); row(prs, "build", "letterhead")
    p = base(prs, "R7 Feature grid"); slot(p, "grid_title", "title", 0.8, 1.3, 11, 0.5, "deck")
    for i, u in enumerate(["drag-ghost", "addon-dialog", "web-converter", "batch-grid"]):
        x = 0.8 + i * 2.98
        p.rect(x, 2.05, 2.75, 1.9, C["tint"], f"grid_{i+1}_block")
        uw = 2.45 if u in ("drag-ghost", "batch-grid") else 2.3
        ui(p, u, x + (2.75 - uw) / 2, 2.25 if uw == 2.45 else 2.27, uw)
        slot(p, f"grid_{i+1}_title", "title", x, 4.15, 2.75, 0.45, "deck"); slot(p, f"grid_{i+1}_body", "body", x, 4.65, 2.7, 1.9, "deck")
    faq(prs); close(prs, "sol")
    prs.save(OUT / "svgs-solution-page.pptx"); return len(prs.slides)

def product():
    prs = mt.new(13.333, 7.5)
    hero(prs, "prod", "drag-ghost")
    p = base(prs, "R6 Benefit list"); slot(p, "prod_benefits_title", "title", 0.8, 1.5, 11, 0.5, "deck")
    for i, ic in enumerate(mb.BEN_ICONS):
        x, y = 0.8 + (i % 2) * 6.0, 2.6 + (i // 2) * 1.7
        icon(p, f"benefit_{i+1}", ic, x, y, 0.5, "blue"); slot(p, f"benefit_{i+1}", "body", x + 0.8, y + 0.02, 4.7, 1.2, "deck")
    p = base(prs, "R8 How it works"); slot(p, "prod_how_title", "title", 0.8, 1.3, 11, 0.5, "deck")
    for i, u in enumerate(["drag-ghost", "drag-ghost", "paste-pill"]):
        x = 0.8 + i * 4.0
        ui(p, ["drag-ghost", "slides-editor", "paste-pill"][i], x, 2.05, 3.7)
        p.rect(x, 4.4, 0.5, 0.5, C["amber"], f"step_{i+1}_badge", MSO_SHAPE.OVAL); icon(p, f"step_{i+1}", mb.STEP_ICONS[i], x + 0.1, 4.5, 0.3, "ink")
        slot(p, f"step_{i+1}_title", "title", x + 0.65, 4.42, 3, 0.45, "deck"); slot(p, f"step_{i+1}_body", "body", x, 5.05, 3.6, 1.2, "deck")
    row(prs, "private", "permissions", uw=5.2); row(prs, "shapes", "shape-list", True); row(prs, "edit", "fill-picker")
    p = base(prs, "R11 Fact columns"); slot(p, "facts_title", "title", 0.8, 1.5, 11, 0.5, "deck")
    for i in range(3):
        x = 0.8 + i * 4.0
        p.rect(x, 2.5, 3.6, 0.05, C["amber"], f"facts_{i+1}_rule")
        slot(p, f"grid_{i+1}_title", "title", x, 2.75, 3.6, 0.5, "deck"); slot(p, f"facts_{i+1}_body", "body", x, 3.35, 3.6, 2.2, "deck")
    faq(prs); close(prs, "prod")
    prs.save(OUT / "svgs-product-page.pptx"); return len(prs.slides)

def ui_library():
    p = ml.new()
    s = p.slides.add_slide(p.slide_layouts[6])
    vec.place_svg(s, "out2/gemini-ui.svg", 1.0, 0.8, 8.0, tag="lib:ui-editor-mock", text_tag="libtext")
    for sh in s.shapes:
        if sh.name.startswith("libtext"): sh._element.nvSpPr.cNvPr.set("title", "lib:ui-editor-mock")
    ml.label(s, "ui:editor-mock ui-editor-mock editor mockup app window toolbar canvas gemini svg", 9.3, 0.8, 3.6)
    for n, (_, what, words) in ui_kit.UIS.items():
        s = p.slides.add_slide(p.slide_layouts[6])
        vec.place_svg(s, f"ui/{n}.svg", 1.0, 0.8, 8.0, tag=f"lib:ui-{n}", text_tag="libtext")
        for sh in s.shapes:
            if sh.name.startswith("libtext"): sh._element.nvSpPr.cNvPr.set("title", f"lib:ui-{n}")
        ml.label(s, f"ui:{n} ui-{n} {n.replace('-', ' ')} {words}", 9.3, 0.8, 3.6)
    p.save(OUT / "ui-library-v2.pptx"); return len(p.slides)

if __name__ == "__main__":
    print("solution", solution(), "product", product(), "ui lib", ui_library())
    over = [(m[0], len(m[4]), m[5]) for m in M if len(m[4]) > m[5]]; print("over budget:", over)
