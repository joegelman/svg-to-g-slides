"""Place an SVG on a python-pptx slide as native custom-geometry shapes, using the
SVG to Slides converter core (svg_to_slides.py). <text> elements become real text boxes."""
import sys, re
from pathlib import Path
from lxml import etree
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
sys.path.insert(0, "/home/claude/svg-to-g-slides")
import svg_to_slides as s2s

EMU = 914400
_A, _P = s2s._A, s2s._P


def _vb(root):
    vb = root.get("viewBox")
    if vb:
        return [float(v) for v in re.split(r"[ ,]+", vb.strip())]
    return [0, 0, float(re.sub(r"[a-z]+", "", root.get("width", "100"))), float(re.sub(r"[a-z]+", "", root.get("height", "100")))]


def place_svg(slide, svg, x, y, w, fill=None, tag=None, text_font="Verdana", text_tag=None):
    """svg: path or SVG text. x, y, w in inches (height follows the viewBox). Returns height in inches."""
    data = Path(svg).read_bytes() if not str(svg).lstrip().startswith("<") else str(svg).encode()
    root = etree.fromstring(data)
    vx, vy, vw, vh = _vb(root)
    sw, sh = round(w * EMU), round(w * EMU * vh / vw)
    ox, oy = round(x * EMU), round(y * EMU)
    cw, ch = s2s.COORD, round(s2s.COORD * vh / vw)
    grads = s2s.extract_gradients(root)
    paths = list(s2s.collect(root, gradients=grads, vb=(vx, vy, vw, vh)))
    ep = {f"{{{_A}}}cubicBezTo", f"{{{_A}}}lnTo", f"{{{_A}}}moveTo"}
    n = 0
    for d, xfm, fill_hex in paths:
        a_path = s2s.make_a_path(d, xfm, vx, vy, vw, vh)
        xs, ys = [], []
        for seg in a_path:
            if seg.tag in ep and len(seg):
                xs.append(int(seg[-1].get("x"))); ys.append(int(seg[-1].get("y")))
        if not xs:
            continue
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        pw, ph = max(x1 - x0, 1), max(y1 - y0, 1)
        for pt in a_path.iter(f"{{{_A}}}pt"):
            pt.set("x", str(int(pt.get("x")) - x0)); pt.set("y", str(int(pt.get("y")) - y0))
        a_path.set("w", str(pw)); a_path.set("h", str(ph))
        hx = (fill or (fill_hex if isinstance(fill_hex, str) else None) or "000000").upper().lstrip("#")
        n += 1
        sid = len(slide.shapes._spTree) + 10
        title = f' title="{tag}"' if tag else ""
        sp = etree.fromstring(
            f'<p:sp xmlns:p="{_P}" xmlns:a="{_A}"><p:nvSpPr><p:cNvPr id="{sid}" name="{tag or "vector"} {n}"{title}/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{ox + round(x0 / cw * sw)}" y="{oy + round(y0 / ch * sh)}"/>'
            f'<a:ext cx="{max(round(pw / cw * sw), 1)}" cy="{max(round(ph / ch * sh), 1)}"/></a:xfrm>'
            f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/><a:pathLst/></a:custGeom>'
            f'<a:solidFill><a:srgbClr val="{hx}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')
        sp.find(f".//{{{_A}}}pathLst").append(a_path)
        slide.shapes._spTree.append(sp)
    # text -> real text boxes
    k = w / vw  # inches per SVG unit
    t = 0
    for el in root.iter("{http://www.w3.org/2000/svg}text"):
        txt = "".join(el.itertext()).strip()
        if not txt:
            continue
        fs = float(re.sub(r"[a-z]+", "", el.get("font-size", "12")))
        tx, ty = float(el.get("x", "0")), float(el.get("y", "0"))
        anchor = el.get("text-anchor", "start")
        bw = max(len(txt) * fs * 0.95, fs * 3) * k  # Slides wraps at the box edge and renders Verdana wide; leave slack
        bx = x + (tx - vx) * k - (bw / 2 if anchor == "middle" else bw if anchor == "end" else 0)
        tb = slide.shapes.add_textbox(Inches(bx), Inches(y + (ty - vy - fs * 0.95) * k), Inches(bw), Inches(fs * 1.3 * k))
        t += 1
        tb.name = f"{text_tag or 'ui_text'} {t}"
        tf = tb.text_frame; tf.word_wrap = False
        tf.auto_size = MSO_AUTO_SIZE.NONE  # fixed box: no shrink or grow on import
        for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
            setattr(tf, m, 0)
        p = tf.paragraphs[0]
        p.alignment = {"middle": PP_ALIGN.CENTER, "end": PP_ALIGN.RIGHT}.get(anchor, PP_ALIGN.LEFT)
        r = p.add_run(); r.text = txt
        r.font.name = text_font; r.font.size = Pt(max(fs * k * 72, 4)); r.font.bold = el.get("font-weight") in ("bold", "600", "700", "800")
        col = s2s.parse_color(el.get("fill", "#1C1E22")) or "1C1E22"
        r.font.color.rgb = RGBColor.from_string(col.upper().lstrip("#"))
    return w * vh / vw, n, t
