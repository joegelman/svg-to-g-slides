"""Build the master library decks: one item per slide, native shapes titled lib:<name>,
plus a tiny white text label (title lib-label) so Ctrl+F finds an item by name or keyword."""
import re, sys, json
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import vec

ICON_DIR = Path("/home/claude/work/icons/node_modules/@phosphor-icons/core/assets/fill")
UMD = Path("/home/claude/work/icons/node_modules/@phosphor-icons/core/dist/index.umd.js").read_text()
INK = "1C1E22"

IN_USE = ["hand-grabbing", "cursor-click", "clipboard-text", "bezier-curve", "stack", "magic-wand", "seal-check"]
STARTER = """arrow-right arrow-up-right arrows-clockwise check check-circle x-circle warning info question
lightning rocket target flag star heart shield-check lock key eye gear sliders wrench plug puzzle-piece
cube stack-simple squares-four layout table chart-bar chart-line-up chart-pie-slice trend-up gauge timer clock calendar
users user-circle handshake chat-circle envelope megaphone bell globe link cloud database code terminal-window
file-text files folder image palette pen-nib pencil-simple text-t presentation-chart download-simple upload-simple
share-network copy export magnifying-glass funnel currency-dollar credit-card shopping-cart tag
device-mobile desktop browser cursor robot sparkle lightbulb brain""".split()

def tags(name):
    m = re.search(r'"%s",pascal_name:"[^"]*",.*?tags:\[([^\]]*)\]' % re.escape(name), UMD)
    if not m: return []
    return [t for t in re.findall(r'"([^"]*)"', m.group(1)) if not t.startswith("*")]

def new():
    p = Presentation(); p.slide_width = Inches(13.333); p.slide_height = Inches(7.5); return p

def label(slide, text, x, y, w=6.0):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(0.3))
    tb.name = "lib-label"
    tb._element.nvSpPr.cNvPr.set("title", "lib-label")
    tf = tb.text_frame; tf.word_wrap = True
    r = tf.paragraphs[0].add_run(); r.text = text
    r.font.size = Pt(6); r.font.name = "Verdana"; r.font.color.rgb = RGBColor(255, 255, 255)

def icons():
    p = new(); names, missing = [], []
    for n in IN_USE + [s for s in STARTER if s not in IN_USE]:
        f = ICON_DIR / f"{n}-fill.svg"
        if not f.exists(): missing.append(n); continue
        s = p.slides.add_slide(p.slide_layouts[6])
        h, k, _ = vec.place_svg(s, f, 1.0, 1.0, 3.0, fill=INK, tag=f"lib:{n}")
        label(s, " ".join([f"icon:{n}", n.replace("-", " "), "phosphor fill"] + tags(n)), 4.3, 1.0)
        names.append((n, k))
    p.save("lib/icon-library.pptx"); return names, missing

def uis():
    p = new()
    s = p.slides.add_slide(p.slide_layouts[6])
    h, k, t = vec.place_svg(s, "out2/gemini-ui.svg", 1.0, 0.8, 8.0, tag="lib:ui-editor-mock", text_tag="lib:ui-editor-mock")
    for sh in s.shapes:
        if sh.name.startswith("lib:ui-editor-mock") and sh.has_text_frame and sh.text_frame.text:
            sh._element.nvSpPr.cNvPr.set("title", "lib:ui-editor-mock")
    label(s, "ui:editor-mock ui-editor-mock editor mockup app window toolbar canvas sidebar gemini svg", 9.3, 0.8, 3.6)
    p.save("lib/ui-library.pptx"); return k, t

if __name__ == "__main__":
    n, m = icons(); print(len(n), "icons; missing:", m); print("multi-shape:", [x for x in n if x[1] != 1])
    print("ui shapes/text:", uis())
    json.dump([x[0] for x in n], open("lib/icon-names.json", "w"))
