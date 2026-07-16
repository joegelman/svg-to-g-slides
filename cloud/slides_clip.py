"""
Build Google Slides' internal clipboard payload directly from SVG paths,
bypassing the Slides API entirely (no OAuth scope required for the insert
step — the add-on writes this to the OS clipboard client-side and the user
pastes with Cmd/Ctrl+V).

Reuses svg_to_slides.py's SVG parsing (collect/extract_gradients) and path
walking (expand_path) unchanged; the only new logic here is emitting Slides'
run-length-encoded path arrays instead of DrawingML XML, and the final
placement math.

── Calibration facts (2026-07) ──
- Path opcodes: Move=0, Line=1, Quad=2, Cubic=3, Arc=4, Close=5. We only ever
  emit Move/Line/Cubic/Close — arcs are pre-normalized to cubics upstream by
  svg_to_slides.normalize_arcs(), and no shape needs Quad.
- pathMetadata is (opcode, coordCount) pairs with coordCount = raw numeric
  count (2 per Move/Line point, 6 per Cubic command, 0 for Close) — NOT a
  point count. Confirmed against a real captured payload for a 3-line/2-cubic
  path: [0,2, 1,6, 3,12, 5,0].
- EMU_PER_UNIT=30: the Slides-internal position unit, confirmed via a
  controlled experiment — a native 75x75px rectangle placed at the slide's
  true top-left produced widthScale=0.2381 (=23812.5/100000) and x=y=0;
  75px * 9525 EMU/px = 714375 EMU; 714375 / 23812.5 = exactly 30.
- Object IDs are arbitrary, client-generated, and not validated against any
  server-side state.
- IMPORTANT (superseded an earlier wrong approach): same-session Slides-to-
  Slides copy captures include a much richer structure — dih, edi/edrk
  (opaque signed-looking tokens we cannot produce), unresolved, autotext_
  content, per-shape trailing "p" tag, widthScale/heightScale != 1 with a
  separate local-coordinate-space split, opaque property keys 32/40/44/53/60.
  Matching that structure exactly did NOT work — paste silently no-opped.
  What actually works (confirmed by direct paste test) is a much more
  minimal structure: bare {"data": "{\"resolved\": [...]}"}, no trailing
  type tag on the shape entry, widthScale/heightScale always 1 with path
  coordinates and width/height baked to final absolute units directly. This
  matches what a reference converter (github.com/Tikolu/SketchyShapes)
  produces, confirmed working by direct test — the richer same-session
  structure is apparently NOT what external-paste validation requires, and
  chasing it was a dead end.
"""
import json
import secrets
from xml.etree import ElementTree as ET

from svg_to_slides import COORD, collect, expand_path, extract_gradients

EMU_PER_UNIT = 30
_PT_TO_EMU = 12700
_FIT_FRACTION = 0.85

_OP_MOVE, _OP_LINE, _OP_CUBIC, _OP_CLOSE = 0, 1, 3, 5


def path_to_clip_geometry(d, xfm, vb_x, vb_y, vb_w, vb_h):
    """Mirror of svg_to_slides.make_a_path(): same local-COORD-space walk of
    expand_path(d), but run-length-encodes into (path_metadata, flat_coords)
    instead of building DrawingML <a:pt> XML elements.
    """
    cw = COORD
    ch = round(COORD * vb_h / vb_w) if vb_w else COORD

    def sc(x, y):
        tx, ty = xfm(x, y)
        return round((tx - vb_x) / vb_w * cw), round((ty - vb_y) / vb_h * ch)

    path_metadata = []
    flat_coords = []

    def emit(opcode, pts):
        # path_metadata is a FLAT array of alternating (opcode, coordCount)
        # numbers — NOT nested [opcode,count] pairs. Confirmed against a
        # real working payload: [0,2,1,6,3,12,5,0], not [[0,2],[1,6],...].
        n = 2 * len(pts)
        if path_metadata and path_metadata[-2] == opcode:
            path_metadata[-1] += n
        else:
            path_metadata.append(opcode)
            path_metadata.append(n)
        for x, y in pts:
            flat_coords.extend((x, y))

    cx = cy = mx = my = 0.0
    last_ctrl = None

    for cmd, args in expand_path(d):
        if cmd not in ('C', 'c', 'S', 's', 'Q', 'q', 'T', 't'):
            last_ctrl = None

        if cmd == 'M':
            cx, cy = mx, my = args
            emit(_OP_MOVE, [sc(cx, cy)])
        elif cmd == 'm':
            cx, cy = mx, my = cx + args[0], cy + args[1]
            emit(_OP_MOVE, [sc(cx, cy)])
        elif cmd == 'L':
            cx, cy = args
            emit(_OP_LINE, [sc(cx, cy)])
        elif cmd == 'l':
            cx += args[0]; cy += args[1]
            emit(_OP_LINE, [sc(cx, cy)])
        elif cmd == 'H':
            cx = args[0]
            emit(_OP_LINE, [sc(cx, cy)])
        elif cmd == 'h':
            cx += args[0]
            emit(_OP_LINE, [sc(cx, cy)])
        elif cmd == 'V':
            cy = args[0]
            emit(_OP_LINE, [sc(cx, cy)])
        elif cmd == 'v':
            cy += args[0]
            emit(_OP_LINE, [sc(cx, cy)])
        elif cmd == 'C':
            x1, y1, x2, y2, x, y = args
            emit(_OP_CUBIC, [sc(x1, y1), sc(x2, y2), sc(x, y)])
            last_ctrl = (x2, y2); cx, cy = x, y
        elif cmd == 'c':
            x1, y1, x2, y2, dx, dy = args
            ax1, ay1 = cx + x1, cy + y1
            ax2, ay2 = cx + x2, cy + y2
            ax, ay = cx + dx, cy + dy
            emit(_OP_CUBIC, [sc(ax1, ay1), sc(ax2, ay2), sc(ax, ay)])
            last_ctrl = (ax2, ay2); cx, cy = ax, ay
        elif cmd == 'S':
            x2, y2, x, y = args
            lx, ly = last_ctrl if last_ctrl else (cx, cy)
            x1, y1 = 2 * cx - lx, 2 * cy - ly
            emit(_OP_CUBIC, [sc(x1, y1), sc(x2, y2), sc(x, y)])
            last_ctrl = (x2, y2); cx, cy = x, y
        elif cmd == 's':
            dx2, dy2, dx, dy = args
            x2, y2 = cx + dx2, cy + dy2
            x, y = cx + dx, cy + dy
            lx, ly = last_ctrl if last_ctrl else (cx, cy)
            x1, y1 = 2 * cx - lx, 2 * cy - ly
            emit(_OP_CUBIC, [sc(x1, y1), sc(x2, y2), sc(x, y)])
            last_ctrl = (x2, y2); cx, cy = x, y
        elif cmd == 'Q':
            qx, qy, x, y = args
            x1, y1 = cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)
            x2, y2 = x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)
            emit(_OP_CUBIC, [sc(x1, y1), sc(x2, y2), sc(x, y)])
            last_ctrl = (qx, qy); cx, cy = x, y
        elif cmd == 'q':
            dqx, dqy, dx, dy = args
            qx, qy = cx + dqx, cy + dqy
            x, y = cx + dx, cy + dy
            x1, y1 = cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)
            x2, y2 = x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)
            emit(_OP_CUBIC, [sc(x1, y1), sc(x2, y2), sc(x, y)])
            last_ctrl = (qx, qy); cx, cy = x, y
        elif cmd == 'T':
            x, y = args
            lx, ly = last_ctrl if last_ctrl else (cx, cy)
            qx, qy = 2 * cx - lx, 2 * cy - ly
            x1, y1 = cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)
            x2, y2 = x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)
            emit(_OP_CUBIC, [sc(x1, y1), sc(x2, y2), sc(x, y)])
            last_ctrl = (qx, qy); cx, cy = x, y
        elif cmd == 't':
            dx, dy = args
            x, y = cx + dx, cy + dy
            lx, ly = last_ctrl if last_ctrl else (cx, cy)
            qx, qy = 2 * cx - lx, 2 * cy - ly
            x1, y1 = cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)
            x2, y2 = x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)
            emit(_OP_CUBIC, [sc(x1, y1), sc(x2, y2), sc(x, y)])
            last_ctrl = (qx, qy); cx, cy = x, y
        elif cmd in ('Z', 'z'):
            path_metadata.append(_OP_CLOSE)
            path_metadata.append(0)
            cx, cy = mx, my
        # 'A'/'a' deliberately unhandled: normalize_arcs() removes them
        # upstream before collect() ever yields a path to us.

    return path_metadata, flat_coords


def _endpoint_bbox(path_metadata, flat_coords):
    """Endpoint-only bbox (excludes cubic control points), mirroring
    add_shapes()'s ep_xs/ep_ys logic — bezier control points can lie far
    outside the visual curve, so including them would produce a wrong bbox.
    """
    xs, ys = [], []
    idx = 0
    for m in range(0, len(path_metadata), 2):
        opcode, count = path_metadata[m], path_metadata[m + 1]
        n = count // 2
        if opcode == _OP_CLOSE:
            continue
        if opcode in (_OP_MOVE, _OP_LINE):
            for i in range(n):
                xs.append(flat_coords[idx + 2 * i])
                ys.append(flat_coords[idx + 2 * i + 1])
        elif opcode == _OP_CUBIC:
            for i in range(0, n, 3):
                xs.append(flat_coords[idx + 2 * (i + 2)])
                ys.append(flat_coords[idx + 2 * (i + 2) + 1])
        idx += count
    return xs, ys


def _trim_to_origin(flat_coords, px_min, py_min):
    out = list(flat_coords)
    for i in range(0, len(out), 2):
        out[i] -= px_min
        out[i + 1] -= py_min
    return out


def layout_slots(n, slide_w_emu, slide_h_emu):
    """n==1: single centered slot at 85% of both dimensions — matches the
    existing PPTX pipeline's sizing exactly. n>1: equal-width horizontal row,
    vertically centered, small gutter — new layout, no existing analog (the
    old pipeline appended separate slides per file instead)."""
    if n == 1:
        w = round(slide_w_emu * _FIT_FRACTION)
        h = round(slide_h_emu * _FIT_FRACTION)
        return [((slide_w_emu - w) // 2, (slide_h_emu - h) // 2, w, h)]

    gutter = round(slide_w_emu * 0.02)
    total_w = round(slide_w_emu * _FIT_FRACTION)
    slot_w = (total_w - gutter * (n - 1)) // n
    slot_h = round(slide_h_emu * _FIT_FRACTION)
    start_x = (slide_w_emu - total_w) // 2
    y = (slide_h_emu - slot_h) // 2
    return [(start_x + i * (slot_w + gutter), y, slot_w, slot_h) for i in range(n)]


def _build_shape_entry(path_metadata, flat_coords, w, h, x, y, fill_hex):
    """Mirrors the proven-working structure produced by a reference SVG-to-
    Slides-clipboard converter (github.com/Tikolu/SketchyShapes), confirmed
    by direct paste test to work — as opposed to the richer structure
    (dih/edi/edrk/opaque tail keys/trailing type tag) seen in same-session
    Slides-to-Slides copies, which apparently isn't what external-paste
    validation actually requires. widthScale/heightScale are always 1 —
    path coordinates and width/height are baked to final absolute units
    directly rather than a local-shape + scale-factor split.
    """
    obj_id = 'ga' + secrets.token_hex(5)
    # The [1, 1, ...] prefix on the path record is required — present in
    # every real capture (including the proven-working reference) and
    # missing from earlier versions of this encoder.
    props = [
        8, w, 9, h,
        12, [[1, 1, path_metadata, flat_coords, [], 0]],
        14, 1, 15, f'#{fill_hex}',
        18, 0, 23, 0,
    ]
    return [3, obj_id, 1, [1, 0, 0, 1, x, y], props]


def add_shapes_to_clip(svg_shape_groups, slide_w_pt, slide_h_pt):
    """svg_shape_groups: list of ((vb_x,vb_y,vb_w,vb_h), shapes) where shapes
    is collect()'s (d, xfm, fill_hex) output for one SVG file. Mirrors
    add_shapes()'s per-shape endpoint-bbox fit, retargeted from DrawingML
    XML/EMU to the clip array structure/EMU_PER_UNIT-converted units.
    """
    slide_w_emu = round(slide_w_pt * _PT_TO_EMU)
    slide_h_emu = round(slide_h_pt * _PT_TO_EMU)
    slots = layout_slots(len(svg_shape_groups), slide_w_emu, slide_h_emu)

    resolved = []
    for (vb, shapes), (slot_x, slot_y, slot_w, slot_h) in zip(svg_shape_groups, slots):
        vb_x, vb_y, vb_w, vb_h = vb
        aspect = vb_w / vb_h if vb_h else 1
        if aspect >= slot_w / slot_h:
            sw = slot_w; sh = round(sw / aspect)
        else:
            sh = slot_h; sw = round(sh * aspect)
        ox = slot_x + (slot_w - sw) // 2
        oy = slot_y + (slot_h - sh) // 2

        cw = COORD
        ch = round(COORD * vb_h / vb_w) if vb_w else COORD

        for d, xfm, fill_hex in shapes:
            path_metadata, flat_coords = path_to_clip_geometry(d, xfm, vb_x, vb_y, vb_w, vb_h)
            xs, ys = _endpoint_bbox(path_metadata, flat_coords)
            if not xs:
                continue
            px_min, py_min = min(xs), min(ys)
            px_max, py_max = max(xs), max(ys)
            pw, ph = max(px_max - px_min, 1), max(py_max - py_min, 1)
            flat_coords = _trim_to_origin(flat_coords, px_min, py_min)

            shape_ox = ox + round(px_min / cw * sw)
            shape_oy = oy + round(py_min / ch * sh)
            shape_sw = max(round(pw / cw * sw), 1)
            shape_sh = max(round(ph / ch * sh), 1)

            # v1: gradient fills collapse to their first stop's solid color —
            # full fillGradientType/Colors/Angle (keys 60/61/62) encoding is
            # a fast-follow once those keys are decoded from a captured
            # gradient-shape payload.
            fill = fill_hex['stops'][0][1] if isinstance(fill_hex, dict) else fill_hex

            # Bake local->final scaling directly into the coordinates
            # (widthScale/heightScale left at 1) rather than emitting a
            # local-normalized shape + separate scale factor — matches the
            # proven-working reference structure, not the DrawingML-style
            # split we originally mirrored.
            scale_x = (shape_sw / EMU_PER_UNIT) / pw
            scale_y = (shape_sh / EMU_PER_UNIT) / ph
            final_coords = [
                round(v * (scale_x if i % 2 == 0 else scale_y))
                for i, v in enumerate(flat_coords)
            ]
            final_w = max(round(shape_sw / EMU_PER_UNIT), 1)
            final_h = max(round(shape_sh / EMU_PER_UNIT), 1)
            x_unit = round(shape_ox / EMU_PER_UNIT)
            y_unit = round(shape_oy / EMU_PER_UNIT)

            resolved.append(_build_shape_entry(
                path_metadata, final_coords, final_w, final_h,
                x_unit, y_unit, fill))

    return resolved


def build_clip_bundle(svg_sources, slide_w_pt, slide_h_pt):
    """svg_sources: list of (filename, svg_bytes). Returns a dict of the 4
    clipboard MIME types -> string payloads, ready to be written via the
    add-on's client-side `copy`-event clipboardData.setData() handler.
    """
    groups = []
    for _name, svg_bytes in svg_sources:
        root = ET.fromstring(svg_bytes)
        vb = root.get('viewBox', '0 0 100 100')
        vb_x, vb_y, vb_w, vb_h = (float(v) for v in vb.strip().split())
        gradients = extract_gradients(root)
        shapes = list(collect(root, gradients=gradients, vb=(vb_x, vb_y, vb_w, vb_h)))
        groups.append(((vb_x, vb_y, vb_w, vb_h), shapes))

    resolved = add_shapes_to_clip(groups, slide_w_pt, slide_h_pt)

    # Minimal structure, confirmed by direct paste test to work: just
    # {"data": "{\"resolved\": [...]}"}. Earlier attempts added dih/edi/edrk/
    # unresolved/autotext_content/etc. by matching same-session Slides-to-
    # Slides copy captures — that richer structure turned out to be a red
    # herring for external paste, which this minimal shape satisfies fine.
    data = {'resolved': resolved}
    wrapper = {'data': json.dumps(data, separators=(',', ':'))}

    # Only this one MIME type — no text/plain, text/html, or clip-id.
    # SketchyShapes' demo (confirmed working by direct test) sets only this
    # single type. Real native-Slides captures always carry the other three
    # alongside it, which is what we matched originally — but offering
    # text/html at the same time may cause Slides to prioritize it (as a
    # more "standard" type) over the custom drawings-object type and paste
    # that instead, silently. Dropping them is the last structural gap
    # versus the proven-working reference.
    return {
        'application/x-vnd.google-docs-drawings-object+wrapped': json.dumps(wrapper, separators=(',', ':')),
    }
