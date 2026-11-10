"""UI mockups as plain SVG (rects, circles, paths, text) in the SVG to Slides palette.
Each function returns SVG text. vec.place_svg turns them into native shapes and text boxes."""
import re
from pathlib import Path
ICONS = Path("/home/claude/work/icons/node_modules/@phosphor-icons/core/assets/fill")
INK, GREY, WHITE, AMBER, BLUE, TINT, RULE, GREEN = "#1C1E22", "#6B6F76", "#FFFFFF", "#F9C80E", "#0066FF", "#F4F5F7", "#E3E5E8", "#1E8E3E"

def R(x, y, w, h, fill, rx=0): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"/>'
def O(x, y, w, h, color, sw=2, rx=0): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" stroke="{color}" stroke-width="{sw}"/>'
def C(cx, cy, r, fill): return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'
def T(x, y, s, size=13, fill=INK, anchor="start", bold=False):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{" font-weight=\"700\"" if bold else ""}>{s}</text>'
def I(name, x, y, size, fill=INK):
    d = " ".join(re.findall(r'<path d="([^"]+)"', (ICONS / f"{name}-fill.svg").read_text()))
    return f'<g transform="translate({x},{y}) scale({size/256})"><path d="{d}" fill="{fill}"/></g>'
def svg(w, h, *parts): return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">' + "".join(parts) + "</svg>"
def card(w, h): return R(6, 6, w - 12, h - 12, RULE, 14) + R(8, 8, w - 16, h - 16, WHITE, 12)
def handles(x, y, w, h):
    out = O(x, y, w, h, BLUE, 2)
    for hx, hy in [(x, y), (x + w, y), (x, y + h), (x + w, y + h), (x + w / 2, y), (x + w / 2, y + h), (x, y + h / 2), (x + w, y + h / 2)]:
        out += R(hx - 5, hy - 5, 10, 10, BLUE) + R(hx - 3, hy - 3, 6, 6, WHITE)
    return out
def pill(cx, y, text, w=None, fill=INK, color=WHITE, size=13):
    w = w or len(text) * size * 0.62 + 36
    return R(cx - w / 2, y, w, 30, fill, 15) + T(cx, y + 20, text, size, color, "middle", True)
def mark(x, y, s):  # stand-in logo: amber disc with ink bar, three separate shapes
    return C(x + s / 2, y + s / 2, s / 2, AMBER) + R(x + s * .28, y + s * .28, s * .44, s * .16, INK) + R(x + s * .28, y + s * .56, s * .44, s * .16, INK)

def slides_frame(title="Untitled presentation", thumbs=3):
    p = card(960, 540) + R(3, 3, 954, 44, WHITE, 12) + R(3, 46, 954, 2, RULE)
    p += R(20, 16, 20, 20, AMBER, 4) + T(52, 31, title, 14, INK, bold=True)
    p += R(820, 13, 120, 26, BLUE, 13) + T(880, 31, "Share", 12, WHITE, "middle", True)
    p += R(3, 48, 954, 34, TINT) + "".join(R(22 + i * 34, 57, 18, 16, RULE, 3) for i in range(9))
    p += R(3, 82, 150, 455, WHITE) + R(152, 82, 2, 455, RULE)
    for i in range(thumbs):
        p += R(22, 98 + i * 86, 112, 64, RULE, 4) + R(24, 100 + i * 86, 108, 60, WHITE, 3)
    p += O(20, 96, 116, 68, BLUE, 2, 5)
    p += R(154, 82, 803, 455, TINT) + R(196, 110, 720, 400, WHITE)
    return p

def ui_slides_editor():
    p = slides_frame("Q4 launch deck") + T(240, 170, "Product launch", 30, INK, bold=True) + R(240, 190, 220, 10, RULE, 5) + R(240, 210, 160, 10, RULE, 5)
    p += I("rocket", 610, 200, 190, BLUE) + handles(600, 190, 210, 210)
    return svg(960, 540, p)
def ui_drag_ghost():
    p = slides_frame("Q4 launch deck") + T(240, 170, "Product launch", 30, INK, bold=True) + R(240, 190, 220, 10, RULE, 5)
    p += I("rocket", 560, 250, 96, "#9DBEF5") + C(662, 252, 14, GREEN) + R(655, 250, 14, 4, WHITE) + R(660, 245, 4, 14, WHITE)
    p += I("cursor", 640, 330, 34, INK) + pill(556, 452, "Double Click to Place")
    return svg(960, 540, p)
def ui_paste_pill():
    p = slides_frame("Q4 launch deck") + T(240, 170, "Product launch", 30, INK, bold=True) + R(240, 190, 220, 10, RULE, 5)
    p += I("rocket", 560, 220, 150, BLUE) + handles(552, 212, 166, 166) + pill(556, 452, "Cmd + V to Confirm")
    return svg(960, 540, p)
def ui_fill_picker():
    p = slides_frame("Brand icons") + I("seal-check", 250, 180, 220, AMBER) + handles(242, 172, 236, 236)
    p += R(560, 130, 300, 330, RULE, 12) + R(562, 132, 296, 326, WHITE, 10) + T(582, 166, "Fill colour", 15, INK, bold=True)
    cols = [INK, GREY, BLUE, "#0A57D0", AMBER, "#FDB707", GREEN, "#D93025", "#8E24AA", "#00897B", RULE, TINT]
    for i, c in enumerate(cols):
        p += C(600 + (i % 4) * 66, 215 + (i // 4) * 62, 20, c)
    p += O(644, 255, 44, 44, BLUE, 3, 22) + R(582, 400, 256, 36, TINT, 8) + T(596, 423, "#F9C80E", 13, INK) + T(824, 423, "Custom", 12, BLUE, "end", True)
    return svg(960, 540, p)
def ui_png_vs_shapes():
    p = card(960, 420) + R(480, 30, 2, 360, RULE)
    p += T(60, 70, "Pasted SVG", 18, INK, bold=True) + T(60, 96, "One flat picture", 13, GREY)
    px = [(0,1),(1,0),(2,0),(3,1),(4,2),(3,3),(2,4),(1,3),(0,2),(2,2),(1,1),(3,2),(2,1),(1,2),(2,3)]
    p += "".join(R(160 + x * 34, 150 + y * 34, 34, 34, GREY if (x + y) % 2 else "#8D9198") for x, y in px) + O(150, 140, 190, 190, RULE, 2)
    p += T(540, 70, "With SVG to Slides", 18, INK, bold=True) + T(540, 96, "Separate shapes you can select", 13, GREY)
    p += C(700, 245, 86, AMBER) + R(655, 205, 90, 30, INK, 6) + R(655, 255, 90, 30, BLUE, 6) + handles(645, 245, 110, 50)
    return svg(960, 420, p)
def ui_reuse():
    p = card(960, 420)
    for i, (name, col) in enumerate([("Slides theme", AMBER), ("Docs", BLUE), ("Drawings", "#D93025")]):
        x = 50 + i * 300
        p += R(x, 50, 260, 320, RULE, 10) + R(x + 2, 52, 256, 316, WHITE, 8) + R(x + 2, 52, 256, 40, TINT, 8) + R(x + 16, 64, 16, 16, col, 3) + T(x + 42, 78, name, 13, INK, bold=True)
        p += mark(x + 24, 116, 56) + R(x + 24, 196, 200, 10, RULE, 5) + R(x + 24, 218, 170, 10, RULE, 5) + R(x + 24, 240, 190, 10, RULE, 5) + R(x + 24, 262, 120, 10, RULE, 5)
    return svg(960, 420, p)
def ui_letterhead():
    p = card(960, 420) + R(90, 30, 300, 380, RULE, 4) + R(92, 32, 296, 376, WHITE, 3) + mark(116, 56, 40) + T(166, 83, "Company name", 14, INK, bold=True) + R(116, 116, 248, 2, AMBER)
    p += "".join(R(116, 140 + i * 22, 248 - (i % 3) * 40, 8, RULE, 4) for i in range(9))
    p += R(450, 30, 440, 250, RULE, 4) + R(452, 32, 436, 246, WHITE, 3) + mark(476, 56, 40) + T(476, 150, "Slide template", 26, INK, bold=True) + R(476, 172, 240, 10, RULE, 5) + R(476, 194, 180, 10, RULE, 5) + R(452, 262, 436, 16, AMBER)
    p += R(450, 300, 440, 110, TINT, 8) + T(474, 334, "Motion", 14, INK, bold=True) + R(474, 350, 180, 40, WHITE, 6) + T(488, 375, "Fade in", 12, INK) + R(670, 350, 196, 40, WHITE, 6) + T(684, 375, "On click", 12, INK)
    return svg(960, 420, p)
def ui_addon_dialog():
    p = card(760, 480) + T(36, 54, "Insert SVGs", 20, INK, bold=True) + R(3, 76, 754, 2, RULE)
    names = ["rocket", "seal-check", "lightning", "palette", "chart-bar", "globe", "shield-check", "sparkle"]
    for i, n in enumerate(names):
        x, y = 36 + (i % 4) * 176, 100 + (i // 4) * 130
        p += R(x, y, 160, 112, TINT, 8) + I(n, x + 52, y + 26, 56, INK)
    p += T(380, 392, "Ready, click below or press Enter to copy", 15, INK, "middle", True) + R(280, 412, 200, 40, BLUE, 20) + T(380, 438, "Copy", 15, WHITE, "middle", True)
    return svg(760, 480, p)
def ui_web_converter():
    p = card(760, 480) + T(36, 54, "svgslid.es/convert", 16, INK, bold=True) + R(3, 76, 754, 2, RULE)
    p += R(36, 100, 688, 150, TINT, 12) + I("upload-simple", 356, 122, 48, GREY) + T(380, 200, "Drop SVG files here", 16, INK, "middle", True) + T(380, 224, "One slide per file", 12, GREY, "middle")
    for i, n in enumerate(["logo.svg", "icon-rocket.svg", "icon-shield.svg"]):
        y = 270 + i * 44
        p += R(36, y, 688, 36, WHITE) + R(36, y + 36, 688, 2, RULE) + I("file-text", 44, y + 6, 24, GREY) + T(80, y + 24, n, 13, INK) + I("check-circle", 690, y + 6, 24, GREEN)
    p += R(36, 414, 688, 40, TINT, 8) + I("link", 48, 422, 24, BLUE) + T(84, 440, "Drive link to your PPTX", 13, BLUE, bold=True)
    return svg(760, 480, p)
def ui_permissions():
    p = card(640, 400) + R(36, 36, 48, 48, AMBER, 10) + I("puzzle-piece", 46, 46, 28, INK) + T(100, 58, "SVG to Slides", 18, INK, bold=True) + T(100, 80, "Chrome extension", 12, GREY)
    rows = [("Google permissions", "None"), ("Conversion", "In your browser"), ("Sign-up", "None"), ("Price", "Free")]
    for i, (k, v) in enumerate(rows):
        y = 120 + i * 62
        p += R(36, y, 568, 2, RULE) + T(36, y + 38, k, 14, GREY) + T(604, y + 38, v, 14, INK, "end", True)
    return svg(640, 400, p)
def ui_batch_grid():
    names = "rocket seal-check lightning palette chart-bar globe shield-check sparkle star heart lock key eye gear cube cloud database code folder image bell flag tag link users".split()
    p = slides_frame("Icon set")
    for i, n in enumerate(names):
        p += I(n, 250 + (i % 5) * 124, 124 + (i // 5) * 76, 52, [INK, BLUE, AMBER][i % 3])
    return svg(960, 540, p)
def ui_shape_list():
    p = slides_frame("Logo")
    p += C(430, 300, 120, AMBER) + R(370, 250, 120, 40, INK, 8) + R(370, 310, 120, 40, BLUE, 8) + handles(362, 302, 136, 56)
    p += R(650, 130, 230, 250, RULE, 12) + R(652, 132, 226, 246, WHITE, 10) + T(672, 164, "3 shapes", 14, INK, bold=True)
    for i, (n, c) in enumerate([("Disc", AMBER), ("Bar, top", INK), ("Bar, bottom", BLUE)]):
        y = 184 + i * 60
        p += R(664, y, 202, 48, TINT if i == 2 else WHITE, 8) + R(678, y + 14, 20, 20, c, 4) + T(710, y + 30, n, 13, INK)
    return svg(960, 540, p)

UIS = {
    "slides-editor": (ui_slides_editor, "Slides editor with one converted icon selected", "slides editor canvas filmstrip selected icon handles"),
    "drag-ghost": (ui_drag_ghost, "Step 1 and 2: ghost preview, green plus badge, Double Click to Place pill", "drag drop ghost place pill step"),
    "paste-pill": (ui_paste_pill, "Step 3: placed outline and the Cmd + V to Confirm pill", "paste confirm pill step"),
    "fill-picker": (ui_fill_picker, "A converted shape recoloured with the fill picker", "fill colour color picker recolour swatches"),
    "png-vs-shapes": (ui_png_vs_shapes, "Flat pasted picture next to separate native shapes", "before after png raster comparison shapes"),
    "reuse": (ui_reuse, "The same mark in a Slides theme, Docs and Drawings", "reuse theme docs drawings everywhere"),
    "letterhead": (ui_letterhead, "Letterhead, slide template and a motion panel built on vector shapes", "letterhead template motion animate"),
    "addon-dialog": (ui_addon_dialog, "Add-on dialog: thumbnail grid and Copy button", "add-on dialog thumbnails copy"),
    "web-converter": (ui_web_converter, "Web converter: drop zone, file list, Drive link", "web converter upload drop drive link pptx"),
    "permissions": (ui_permissions, "Extension card: no Google permissions, converts in the browser", "permissions privacy browser free"),
    "batch-grid": (ui_batch_grid, "25 icons dropped onto one slide", "batch 25 files grid icons"),
    "shape-list": (ui_shape_list, "A logo as three separate shapes, one selected", "shapes separate paths list select"),
}
if __name__ == "__main__":
    import sys; sys.path.insert(0, ".")
    from pptx import Presentation; from pptx.util import Inches
    import vec
    Path("ui").mkdir(exist_ok=True)
    for n, (f, _, _) in UIS.items():
        Path(f"ui/{n}.svg").write_text(f())
    p = Presentation(); p.slide_width = Inches(13.333); p.slide_height = Inches(7.5)
    for n in UIS:
        s = p.slides.add_slide(p.slide_layouts[6]); print(n, vec.place_svg(s, f"ui/{n}.svg", 1.5, 0.6, 10)[1:])
    p.save("ui/test.pptx")
