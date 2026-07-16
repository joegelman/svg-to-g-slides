"""
Build Google Slides' internal clipboard payload directly from SVG paths,
bypassing the Slides API entirely (no OAuth scope required for the insert
step — the add-on writes this to the OS clipboard client-side and the user
pastes with Cmd/Ctrl+V).

Reuses svg_to_slides.py's SVG parsing (collect/extract_gradients) and path
walking (expand_path) unchanged; the only new logic here is emitting Slides'
run-length-encoded path arrays instead of DrawingML XML, and the final
placement math.

── Calibration facts (2026-07, see clipboard-inspector.html capture) ──
- Path opcodes: Move=0, Line=1, Quad=2, Cubic=3, Arc=4, Close=5. We only ever
  emit Move/Line/Cubic/Close — arcs are pre-normalized to cubics upstream by
  svg_to_slides.normalize_arcs(), and no shape needs Quad.
- pathMetadata is (opcode, coordCount) pairs with coordCount = raw numeric
  count (2 per Move/Line point, 6 per Cubic command, 0 for Close) — NOT a
  point count. Confirmed against a real captured payload for a 3-line/2-cubic
  path: [0,2, 1,6, 3,12, 5,0].
- Local path/shape width & height (keys 8/9) and path point coordinates use
  the SAME arbitrary local coordinate system we already use for DrawingML
  (COORD = 100000-normalized to the SVG viewBox) — confirmed byte-for-byte
  identical between our own make_a_path() output and a real captured payload.
- Final on-slide placement (transform's x, y, widthScale, heightScale) is in
  a distinct "Slides internal unit" where 1 unit = 30 EMU. Confirmed via a
  controlled experiment: a native 75x75px rectangle placed at the slide's
  true top-left produced widthScale=0.2381 (=23812.5/100000) and x=y=0;
  75px * 9525 EMU/px = 714375 EMU; 714375 / 23812.5 = exactly 30.
- Object IDs are arbitrary, client-generated, and not validated against any
  server-side state.
- The "dih" field looks like an integrity hash but isn't strictly validated
  on paste (SketchyShapes' demo, github.com/Tikolu/SketchyShapes, omits it
  entirely and works) — we still populate it with a fixed real-captured value
  as a defensive no-op.
- Opaque property keys (32, 40, 44, 53, 60) are copied verbatim from a real
  captured fill-only/no-stroke/no-text shape — semantics undocumented; only
  the keys we understand (12, 14, 15, 16, 18, 8, 9, and the transform) are
  computed.
"""
import json
import secrets
import uuid
from xml.etree import ElementTree as ET

from svg_to_slides import COORD, collect, expand_path, extract_gradients

EMU_PER_UNIT = 30
_PT_TO_EMU = 12700
_FIT_FRACTION = 0.85

_OP_MOVE, _OP_LINE, _OP_CUBIC, _OP_CLOSE = 0, 1, 3, 5

# Fixed template values captured from a real Slides copy of a fill-only shape.
_DIH_TEMPLATE = 2732344119
_OPAQUE_PROP_TAIL = [32, 1, 40, [0, 0, 0, 0, 3, 0, 4, 0], 44, 0, 53, [1828, 3657, 1828, 3657], 60, 0]


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
        n = 2 * len(pts)
        if path_metadata and path_metadata[-1][0] == opcode:
            path_metadata[-1][1] += n
        else:
            path_metadata.append([opcode, n])
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
            path_metadata.append([_OP_CLOSE, 0])
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
    for opcode, count in path_metadata:
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


def _build_shape_entry(path_metadata, flat_coords, pw, ph, width_scale, height_scale, x, y, fill_hex):
    obj_id = 'ga' + secrets.token_hex(5)
    props = [
        12, [[path_metadata, flat_coords, [], 0]],
        14, 1, 15, f'#{fill_hex}', 16, 1,
        18, 0,
        *_OPAQUE_PROP_TAIL,
        8, pw, 9, ph,
    ]
    return [3, obj_id, 1, [width_scale, 0, 0, height_scale, x, y], props, 'p']


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

            # Precision matters here — real Slides clipboard data (and
            # SketchyShapes' "Fix compatibility with Google Slides" commit)
            # rounds scale factors to exactly 4 decimals and position to
            # whole integers. Excess precision may be why earlier attempts
            # pasted nothing: Slides' deserializer likely drops the object
            # silently on an unexpected number format rather than erroring.
            width_scale = round((shape_sw / EMU_PER_UNIT) / pw, 4)
            height_scale = round((shape_sh / EMU_PER_UNIT) / ph, 4)
            x_unit = round(shape_ox / EMU_PER_UNIT)
            y_unit = round(shape_oy / EMU_PER_UNIT)

            resolved.append(_build_shape_entry(
                path_metadata, flat_coords, pw, ph,
                width_scale, height_scale, x_unit, y_unit, fill))

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

    # Every real capture we've taken includes these fields alongside
    # resolved/unresolved — absent from earlier attempts, added here as a
    # test of whether they (rather than the edi/edrk signed tokens, which we
    # cannot produce) are why Slides was silently ignoring the paste.
    autotext_content = {
        json.dumps({'shapeId': shape[1]}, separators=(',', ':')): {} for shape in resolved
    }
    data = {
        'resolved': resolved,
        'unresolved': [],
        'autotext_content': autotext_content,
        'did_remove_empty_picture_placeholders': False,
        'copy_source_supports_inheritance_via_master': True,
    }
    # dct/ds/cses/sm are present, with these exact values, in every real
    # capture we've taken — included here as part of the same test as
    # autotext_content above. edi/edrk (opaque signed-looking tokens) are
    # deliberately NOT included: we have no legitimate way to produce them,
    # and their presence in every real capture is the leading hypothesis for
    # why a from-scratch payload gets silently ignored on paste.
    wrapper = {
        'dih': _DIH_TEMPLATE,
        'data': json.dumps(data, separators=(',', ':')),
        'dct': 'punch',
        'ds': False,
        'cses': False,
        'sm': 'other',
    }

    return {
        'text/plain': ' ',
        'text/html': (
            "<meta charset='utf-8'><meta charset=\"utf-8\">"
            '<b style="font-weight:normal;" '
            f'id="docs-internal-guid-{uuid.uuid4()}">'
            '<span>&nbsp;</span></b>'
        ),
        'application/x-vnd.google-docs-drawings-object+wrapped': json.dumps(wrapper, separators=(',', ':')),
        'application/x-vnd.google-docs-internal-clip-id': str(uuid.uuid4()),
    }
