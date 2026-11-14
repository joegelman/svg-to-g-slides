// Loaded before content.js and svg-editor.js — see manifest.json.
//
// Everything that talks to the Slides editor directly, without the OS
// clipboard and without any Google API. All of it was verified live in a
// scratch deck (Nov 2026, see the project's edit-as-svg.md):
//
// - Reading the current selection: dispatch a synthetic `copy`
//   ClipboardEvent carrying a fresh DataTransfer at the contenteditable
//   inside .docs-texteventtarget-iframe. Slides' own copy handler fills our
//   DataTransfer with the same payload a real ⌘C would produce. The OS
//   clipboard is never touched.
// - Inserting: dispatch a synthetic `paste` ClipboardEvent whose
//   DataTransfer carries our drawings payload. Slides inserts it exactly as
//   if the user had pressed ⌘V. No user gesture needed.
// - Deleting the selection: synthetic Delete keydown/keyup at the same
//   textbox.
// - Geometry: shapes render inside <g id="editor-<objectId>"> using the same
//   internal units as the payload, and the slide's page group
//   (the parent of <g id="editor-<pageId>-bg">) has a screen CTM that maps
//   those units to client pixels at the current zoom and scroll.
//
// If Google ever starts ignoring untrusted events, every caller here falls
// back to the original copy + "⌘V" flow, so nothing hard-breaks.

console.log('[svg2slides] slides-bridge.js loaded');

const SB = (() => {
  const MIME = 'application/x-vnd.google-docs-drawings-object+wrapped';

  function iframe() {
    return document.querySelector('.docs-texteventtarget-iframe');
  }

  function textbox() {
    const ifr = iframe();
    try {
      return ifr && ifr.contentDocument
        ? ifr.contentDocument.querySelector('[contenteditable="true"][role="textbox"]') ||
          ifr.contentDocument.querySelector('[contenteditable="true"]')
        : null;
    } catch {
      return null;
    }
  }

  // Focus must move to the iframe element in the top document as well as
  // the textbox inside it, or Slides' key handling doesn't see our keys.
  function focusTextbox() {
    const tb = textbox();
    if (!tb) return false;
    const ifr = iframe();
    const ae = document.activeElement;
    if (ae && ae !== ifr && typeof ae.blur === 'function') ae.blur();
    if (ifr) ifr.focus();
    tb.focus();
    return true;
  }

  // ── Payload wrap/unwrap ────────────────────────────────────────────────
  function wrap(resolved) {
    return JSON.stringify({ data: JSON.stringify({ resolved }) });
  }
  function unwrap(str) {
    if (!str) return null;
    try {
      const data = JSON.parse(JSON.parse(str).data);
      return data.resolved || null;
    } catch {
      return null;
    }
  }

  // ── Synthetic clipboard / keyboard ────────────────────────────────────
  function readSelection() {
    const tb = textbox();
    if (!tb) return null;
    const dt = new DataTransfer();
    tb.dispatchEvent(new ClipboardEvent('copy', { clipboardData: dt, bubbles: true, cancelable: true }));
    return unwrap(dt.getData(MIME));
  }

  function paste(resolved) {
    const tb = textbox();
    if (!tb) return false;
    tb.focus();
    const dt = new DataTransfer();
    dt.setData(MIME, wrap(resolved));
    tb.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }));
    return true;
  }

  const KEYCODES = { Delete: 46, Escape: 27, Backspace: 8 };
  function pressKey(key) {
    const tb = textbox();
    if (!tb) return false;
    const opts = { key, code: key, keyCode: KEYCODES[key] || 0, which: KEYCODES[key] || 0, bubbles: true, cancelable: true };
    tb.dispatchEvent(new KeyboardEvent('keydown', opts));
    tb.dispatchEvent(new KeyboardEvent('keyup', opts));
    return true;
  }

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // Poll the selection until `test(resolved)` passes. Slides' paste handler
  // may finish asynchronously, so a single immediate read isn't enough.
  async function waitForSelection(test, timeouts = [40, 120, 250, 500, 900]) {
    for (const t of timeouts) {
      await sleep(t);
      const sel = readSelection();
      if (sel && test(sel)) return sel;
    }
    return null;
  }

  // ── Entry / props helpers ──────────────────────────────────────────────
  // Shape entry: [3, id, type, [a,b,c,d,e,f], props, ...]. props is a flat
  // [key, value, key, value, ...] list, so look keys up pairwise — never by
  // indexOf, since a value can equal a key number.
  function getProp(props, key) {
    for (let i = 0; i + 1 < props.length; i += 2) if (props[i] === key) return props[i + 1];
    return undefined;
  }
  function setProp(props, key, value) {
    for (let i = 0; i + 1 < props.length; i += 2) {
      if (props[i] === key) { props[i + 1] = value; return props; }
    }
    props.push(key, value);
    return props;
  }

  function newId() {
    const a = new Uint8Array(5);
    crypto.getRandomValues(a);
    return 'ga' + Array.from(a, (b) => b.toString(16).padStart(2, '0')).join('');
  }

  // Shape types whose stored path is real geometry we can round-trip.
  // 1 = custom shape (ours, PPTX imports); 138 = polyline tool.
  // Deliberately NOT 154 (curve tool): it stores through-points that Slides
  // splines itself, so treating them as Bézier data would misrepresent it.
  const EDITABLE_TYPES = new Set([1, 138]);

  function pathRecord(entry) {
    if (!entry || entry[0] !== 3 || !Array.isArray(entry[4])) return null;
    const p = getProp(entry[4], 12);
    if (!Array.isArray(p) || !Array.isArray(p[0])) return null;
    const rec = p[0];
    if (!Array.isArray(rec[2]) || !Array.isArray(rec[3])) return null;
    return rec;
  }

  function isEditableShape(entry) {
    if (!entry || entry[0] !== 3 || !EDITABLE_TYPES.has(entry[2])) return false;
    const rec = pathRecord(entry);
    if (!rec) return false;
    const ops = rec[2].filter((_, i) => i % 2 === 0);
    return ops.every((op) => op === 0 || op === 1 || op === 2 || op === 3 || op === 5);
  }

  // Composite matrix from shape-local coords to page units, walking up any
  // group entries in the same payload (groups may carry their own
  // transform once the user has moved them).
  function matMul(m, n) {
    return [
      m[0] * n[0] + m[2] * n[1],
      m[1] * n[0] + m[3] * n[1],
      m[0] * n[2] + m[2] * n[3],
      m[1] * n[2] + m[3] * n[3],
      m[0] * n[4] + m[2] * n[5] + m[4],
      m[1] * n[4] + m[3] * n[5] + m[5],
    ];
  }
  function matInv(m) {
    const det = m[0] * m[3] - m[1] * m[2];
    if (!det) return null;
    return [
      m[3] / det, -m[1] / det, -m[2] / det, m[0] / det,
      (m[2] * m[5] - m[3] * m[4]) / det,
      (m[1] * m[4] - m[0] * m[5]) / det,
    ];
  }
  function apply(m, x, y) {
    return { x: m[0] * x + m[2] * y + m[4], y: m[1] * x + m[3] * y + m[5] };
  }

  function parentGroupOf(resolved, id) {
    return resolved.find((e) => e[0] === 2 && Array.isArray(e[2]) && e[2].includes(id)) || null;
  }

  function localToPage(resolved, entry) {
    let m = entry[3].slice();
    let g = parentGroupOf(resolved, entry[1]);
    const seen = new Set();
    while (g && !seen.has(g[1])) {
      seen.add(g[1]);
      if (Array.isArray(g[3])) m = matMul(g[3], m);
      g = parentGroupOf(resolved, g[1]);
    }
    return m;
  }

  // Page units → client px for the slide currently shown in the editor.
  // Slides keeps the SVG of every slide visited this session in the DOM,
  // laid out at 0×0 when not shown, so the first "-bg" in document order is
  // often the wrong slide. The current slide is the one with real size.
  function currentPageBg() {
    let best = null, bestArea = 0;
    document.querySelectorAll('g[id^="editor-"][id$="-bg"]').forEach((bg) => {
      const r = bg.getBoundingClientRect();
      const a = r.width * r.height;
      if (a > bestArea) { best = bg; bestArea = a; }
    });
    return best;
  }
  function currentPageGroup() {
    const bg = currentPageBg();
    return bg && bg.parentNode && bg.parentNode.closest ? bg.parentNode.closest('g[id^="editor-"]') : null;
  }

  function pageCTM() {
    const bg = currentPageBg();
    const page = currentPageGroup();
    const el = page || bg;
    if (!el || typeof el.getScreenCTM !== 'function') return null;
    const c = el.getScreenCTM();
    return c ? [c.a, c.b, c.c, c.d, c.e, c.f] : null;
  }

  function elementFor(id) {
    return document.getElementById('editor-' + id);
  }

  // ── Slides zoom + scroll (for handing the editor's view back) ──────────
  // Verified live (Nov 2026): page units are 25 EMU, so Slides' "100%"
  // is 1/381 px per unit (96 dpi). Typing a percentage into the toolbar's
  // Zoom box and pressing Enter works from script; the accepted range is
  // 25–1000%, and an out-of-range value jams the box, so always clamp.
  const PX_PER_UNIT_AT_100 = 1 / 381;
  const ZOOM_MIN = 25;
  const ZOOM_MAX = 1000;

  function zoomPctFromCTM(c) {
    return (c[0] / PX_PER_UNIT_AT_100) * 100;
  }

  async function setSlidesZoom(pct) {
    const z = Array.from(document.querySelectorAll('input')).find((i) => i.getAttribute('aria-label') === 'Zoom');
    if (!z) return false;
    const v = Math.round(Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, pct))) + '%';
    z.blur();
    await sleep(50);
    z.focus();
    z.select();
    z.value = v;
    z.dispatchEvent(new Event('input', { bubbles: true }));
    z.dispatchEvent(new Event('change', { bubbles: true }));
    const o = { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true };
    z.dispatchEvent(new KeyboardEvent('keydown', o));
    z.dispatchEvent(new KeyboardEvent('keypress', o));
    z.dispatchEvent(new KeyboardEvent('keyup', o));
    await sleep(450);
    // Focusing the box opens Slides' zoom menu; Escape closes it and keeps
    // the value just applied (verified live).
    z.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true, cancelable: true }));
    await sleep(50);
    z.blur();
    return true;
  }

  // Least-squares affine map taking points `src` to `dst` (≥ 3 pairs, not
  // all collinear). Returns { m: [a,b,c,d,e,f], err } (max residual) or null.
  function solveAffine(src, dst) {
    const n = Math.min(src.length, dst.length);
    if (n < 3) return null;
    let sxx = 0, sxy = 0, sx = 0, syy = 0, sy = 0;
    let bx = [0, 0, 0], by = [0, 0, 0];
    for (let i = 0; i < n; i++) {
      const { x, y } = src[i], X = dst[i].x, Y = dst[i].y;
      sxx += x * x; sxy += x * y; sx += x; syy += y * y; sy += y;
      bx[0] += x * X; bx[1] += y * X; bx[2] += X;
      by[0] += x * Y; by[1] += y * Y; by[2] += Y;
    }
    const A = [[sxx, sxy, sx], [sxy, syy, sy], [sx, sy, n]];
    const solve3 = (M, b) => {
      const det = (m) => m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
      const D = det(M);
      if (Math.abs(D) < 1e-12) return null;
      return [0, 1, 2].map((k) => det(M.map((row, r) => row.map((v, c) => (c === k ? b[r] : v)))) / D);
    };
    const px = solve3(A, bx), py = solve3(A, by);
    if (!px || !py) return null;
    const m = [px[0], py[0], px[1], py[1], px[2], py[2]];
    let err = 0;
    for (let i = 0; i < n; i++) {
      const q = apply(m, src[i].x, src[i].y);
      err = Math.max(err, Math.hypot(q.x - dst[i].x, q.y - dst[i].y));
    }
    return { m, err };
  }

  // ── Stacking order ────────────────────────────────────────────────────
  // Top-level objects on the current slide, bottom to top (document order
  // is paint order). A paste always lands on top, so after replacing a
  // shape we walk it back down with Slides' own Arrange shortcuts, which
  // accept synthetic keys (verified live, Nov 2026): Cmd/Ctrl+Up/Down one
  // step, with Shift to front/back. They act on the current selection.
  function topLevelOrder() {
    const page = currentPageGroup();
    if (!page) return [];
    return [...page.querySelectorAll('g[id^="editor-"]')]
      .filter((g) => !/-bg$|-paragraph$/.test(g.id) && g.parentNode.closest('g[id^="editor-"]') === page)
      .map((g) => g.id.slice('editor-'.length));
  }
  function topLevelIdOf(id) {
    const page = currentPageGroup();
    let el = elementFor(id);
    if (!page || !el) return null;
    for (let p = el.parentNode && el.parentNode.closest('g[id^="editor-"]'); p && p !== page; p = p.parentNode && p.parentNode.closest('g[id^="editor-"]')) el = p;
    return el.id.slice('editor-'.length);
  }
  const IS_MAC = /Mac|iPhone|iPad/.test(navigator.platform || '');
  function pressArrange(dir) {
    const tb = textbox();
    if (!tb) return false;
    const up = dir === 'forward' || dir === 'front';
    const o = { key: up ? 'ArrowUp' : 'ArrowDown', code: up ? 'ArrowUp' : 'ArrowDown', keyCode: up ? 38 : 40, which: up ? 38 : 40,
      metaKey: IS_MAC, ctrlKey: !IS_MAC, shiftKey: dir === 'front' || dir === 'back', bubbles: true, cancelable: true };
    tb.dispatchEvent(new KeyboardEvent('keydown', o));
    tb.dispatchEvent(new KeyboardEvent('keyup', o));
    return true;
  }
  // Move the selected top-level object `id` to stacking index `target`
  // (0 = bottom), taking the fewest key presses.
  async function moveToIndex(id, target) {
    focusTextbox();
    let stuck = 0;
    for (let guard = 0; guard < 300; guard++) {
      const order = topLevelOrder();
      const cur = order.indexOf(id), n = order.length;
      if (cur < 0) return false;
      const t = Math.max(0, Math.min(n - 1, target));
      if (cur === t) return true;
      if (t === 0) pressArrange('back');
      else if (t === n - 1) pressArrange('front');
      else if (guard === 0 && cur > t && t + 1 < cur - t) pressArrange('back'); // back, then step up t times
      else if (guard === 0 && cur < t && (n - 1 - t) + 1 < t - cur) pressArrange('front');
      else pressArrange(cur > t ? 'backward' : 'forward');
      await sleep(30);
      const after = topLevelOrder().indexOf(id);
      if (after === cur) { if (++stuck > 3) return false; await sleep(80); } else stuck = 0;
    }
    return false;
  }

  // The part of the slide canvas you can actually see, in client px.
  // #workspace is the whole zoomed page and at high Slides zoom runs far
  // off-screen; #workspace-container is the scrolling viewport around it.
  // Clamp to the window and leave out scrollbars.
  function visibleWorkspaceRect() {
    const c = document.getElementById('workspace-container');
    let r;
    if (c) {
      const b = c.getBoundingClientRect();
      const left = b.left + c.clientLeft, top = b.top + c.clientTop;
      r = { left, top, right: left + c.clientWidth, bottom: top + c.clientHeight };
    } else {
      const w = document.getElementById('workspace');
      const b = w ? w.getBoundingClientRect() : { left: 0, top: 0, right: innerWidth, bottom: innerHeight };
      r = { left: b.left, top: b.top, right: b.right, bottom: b.bottom };
    }
    r.left = Math.max(0, r.left); r.top = Math.max(0, r.top);
    r.right = Math.min(innerWidth, r.right); r.bottom = Math.min(innerHeight, r.bottom);
    return r;
  }

  // Scroll the workspace so page point P lands on client point (cx, cy).
  // Converges in one or two steps; clamps silently at the scroll limits.
  async function scrollPagePointTo(P, cx, cy) {
    const ws = document.getElementById('workspace-container');
    if (!ws) return;
    for (let i = 0; i < 3; i++) {
      const c = pageCTM();
      if (!c) return;
      const q = apply(c, P.x, P.y);
      const dx = q.x - cx, dy = q.y - cy;
      if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;
      ws.scrollLeft += dx;
      ws.scrollTop += dy;
      await sleep(120);
    }
  }

  // Make Slides show page point P at (cx, cy) at `pct` zoom. Re-checks the
  // resulting scale once and corrects if this deck's units differ.
  async function matchSlidesView(pct, P, cx, cy) {
    const target = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, pct));
    if (!(await setSlidesZoom(target))) return false;
    const c = pageCTM();
    if (c) {
      const got = zoomPctFromCTM(c);
      if (Math.abs(got / target - 1) > 0.02) {
        await setSlidesZoom(target * (target / got));
      }
    }
    await scrollPagePointTo(P, cx, cy);
    return true;
  }

  // ── Path codec: Slides path record <-> editable node model ───────────
  // Opcodes: Move=0, Line=1, Quad=2, Cubic=3, Arc=4, Close=5.
  // pathMetadata is (op, rawCoordCount) pairs; consecutive Lines/Cubics
  // may be merged into one run.
  //
  // Node model: subpath = { closed, nodes: [{ x, y, in, out, smooth }] }
  // where in/out are control points {x, y} or null.
  function decodePath(meta, coords) {
    const subs = [];
    let cur = null;
    let i = 0;
    const take = () => coords[i++];
    const near = (a, b) => Math.abs(a.x - b.x) < 0.5 && Math.abs(a.y - b.y) < 0.5;

    for (let k = 0; k + 1 < meta.length; k += 2) {
      const op = meta[k];
      const cnt = meta[k + 1];
      if (cur && cur._implicit && op !== 0 && op !== 5) {
        delete cur._implicit;
        subs.push(cur);
      }
      if (op === 0) {
        for (let n = 0; n < cnt; n += 2) {
          cur = { closed: false, nodes: [{ x: take(), y: take(), in: null, out: null }] };
          subs.push(cur);
        }
      } else if (op === 1) {
        for (let n = 0; n < cnt; n += 2) {
          if (!cur) { cur = { closed: false, nodes: [] }; subs.push(cur); }
          cur.nodes.push({ x: take(), y: take(), in: null, out: null });
        }
      } else if (op === 3) {
        for (let n = 0; n < cnt; n += 6) {
          const c1 = { x: take(), y: take() };
          const c2 = { x: take(), y: take() };
          const p = { x: take(), y: take() };
          if (!cur || !cur.nodes.length) return null;
          cur.nodes[cur.nodes.length - 1].out = c1;
          cur.nodes.push({ x: p.x, y: p.y, in: c2, out: null });
        }
      } else if (op === 2) {
        for (let n = 0; n < cnt; n += 4) {
          const q = { x: take(), y: take() };
          const p = { x: take(), y: take() };
          if (!cur || !cur.nodes.length) return null;
          const p0 = cur.nodes[cur.nodes.length - 1];
          p0.out = { x: p0.x + (2 / 3) * (q.x - p0.x), y: p0.y + (2 / 3) * (q.y - p0.y) };
          cur.nodes.push({ x: p.x, y: p.y, in: { x: p.x + (2 / 3) * (q.x - p.x), y: p.y + (2 / 3) * (q.y - p.y) }, out: null });
        }
      } else if (op === 5) {
        if (cur) {
          cur.closed = true;
          const nodes = cur.nodes;
          if (nodes.length > 1 && near(nodes[0], nodes[nodes.length - 1])) {
            const last = nodes.pop();
            nodes[0].in = last.in;
          }
          // A later op without a Move continues from the start point.
          const start = nodes[0];
          cur = { closed: false, nodes: [{ x: start.x, y: start.y, in: null, out: null }] };
          cur._implicit = true;
        }
      } else {
        return null; // Arc (4) or unknown: not editable
      }
    }
    const out = subs.filter((s) => s.nodes.length > 0);
    out.forEach((s) => s.nodes.forEach((n) => { n.smooth = isSmooth(n); }));
    return out;
  }

  function isSmooth(n) {
    if (!n.in || !n.out) return false;
    const ax = n.x - n.in.x, ay = n.y - n.in.y;
    const bx = n.out.x - n.x, by = n.out.y - n.y;
    const la = Math.hypot(ax, ay), lb = Math.hypot(bx, by);
    if (la < 1e-6 || lb < 1e-6) return false;
    return (ax * bx + ay * by) / (la * lb) > 0.995;
  }

  function encodePath(subs) {
    const meta = [];
    const coords = [];
    const r = (v) => Math.round(v);
    let lastOp = null;
    const emit = (op, nums) => {
      if (op === lastOp && (op === 1 || op === 3)) {
        meta[meta.length - 1] += nums.length;
      } else {
        meta.push(op, nums.length);
      }
      nums.forEach((v) => coords.push(r(v)));
      lastOp = op;
    };
    const seg = (a, b) => {
      if (a.out || b.in) {
        const c1 = a.out || a;
        const c2 = b.in || b;
        emit(3, [c1.x, c1.y, c2.x, c2.y, b.x, b.y]);
      } else {
        emit(1, [b.x, b.y]);
      }
    };
    for (const s of subs) {
      const minNodes = s.closed ? 2 : 2;
      if (s.nodes.length < minNodes) continue;
      emit(0, [s.nodes[0].x, s.nodes[0].y]);
      for (let j = 1; j < s.nodes.length; j++) seg(s.nodes[j - 1], s.nodes[j]);
      if (s.closed) {
        const last = s.nodes[s.nodes.length - 1];
        const first = s.nodes[0];
        if (last.out || first.in) seg(last, first);
        emit(5, []);
      }
    }
    return { meta, coords };
  }

  // Shift local coords so their bbox starts at 0,0; returns the shift and
  // the new width/height (props 8/9).
  function normalizeSubs(subs) {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    const visit = (p) => {
      if (!p) return;
      minX = Math.min(minX, p.x); minY = Math.min(minY, p.y);
      maxX = Math.max(maxX, p.x); maxY = Math.max(maxY, p.y);
    };
    subs.forEach((s) => s.nodes.forEach((n) => { visit(n); visit(n.in); visit(n.out); }));
    if (!isFinite(minX)) return { dx: 0, dy: 0, w: 1, h: 1 };
    const shift = (p) => { if (p) { p.x -= minX; p.y -= minY; } };
    subs.forEach((s) => s.nodes.forEach((n) => { shift(n); shift(n.in); shift(n.out); }));
    return { dx: minX, dy: minY, w: Math.max(1, Math.round(maxX - minX)), h: Math.max(1, Math.round(maxY - minY)) };
  }

  // Type rule mirrors slides_clip._shape_type: polylines (138) can only be
  // point-edited safely when they are one subpath of straight lines.
  function typeFor(originalType, subs) {
    if (originalType !== 138) return originalType;
    const lineOnly = subs.length === 1 && subs[0].nodes.every((n, i, arr) => {
      const next = arr[(i + 1) % arr.length];
      return !n.out && !(next && next.in);
    });
    return lineOnly ? 138 : 1;
  }

  // SVG path string for a node model, mapped through matrix m.
  function svgPathD(subs, m) {
    const P = (p) => { const q = apply(m, p.x, p.y); return q.x.toFixed(2) + ' ' + q.y.toFixed(2); };
    let d = '';
    for (const s of subs) {
      if (!s.nodes.length) continue;
      d += 'M' + P(s.nodes[0]);
      const seg = (a, b) => {
        if (a.out || b.in) d += 'C' + P(a.out || a) + ' ' + P(b.in || b) + ' ' + P(b);
        else d += 'L' + P(b);
      };
      for (let j = 1; j < s.nodes.length; j++) seg(s.nodes[j - 1], s.nodes[j]);
      if (s.closed && s.nodes.length > 1) {
        seg(s.nodes[s.nodes.length - 1], s.nodes[0]);
        d += 'Z';
      }
    }
    return d;
  }


  // ── Rendered geometry → custom shapes ("Edit any shape as SVG") ───────
  // Slides draws every object as plain SVG under g#editor-<id>: presets,
  // lines, WordArt, text-box frames. Those paths use only M/L/C/Z, so
  // reading them back gives exact geometry. Each visible path becomes a
  // type 1 custom shape (which the editor can open); several paths become
  // a group. One-way: preset handles, connector glue, automatic shading
  // and live WordArt text don't survive. Verified Nov 2026.
  const SELECTION_BLUE = /^#8ab4f8$/i;

  function parseRenderedD(d) {
    const toks = (d || '').match(/[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?/g);
    if (!toks) return null;
    const subs = [];
    let i = 0, cmd = null, cx = 0, cy = 0, sx = 0, sy = 0, cur = null;
    const num = () => parseFloat(toks[i++]);
    while (i < toks.length) {
      if (/[A-Za-z]/.test(toks[i])) cmd = toks[i++];
      if (!cmd) return null;
      const rel = cmd === cmd.toLowerCase() && cmd !== 'z';
      const C = cmd.toUpperCase();
      const ox = rel ? cx : 0, oy = rel ? cy : 0;
      if (C === 'M') {
        const x = num() + ox, y = num() + oy;
        cx = sx = x; cy = sy = y;
        cur = [['M', x, y]]; subs.push(cur);
        cmd = rel ? 'l' : 'L';
      } else if (!cur) {
        return null;
      } else if (C === 'L') {
        const x = num() + ox, y = num() + oy; cur.push(['L', x, y]); cx = x; cy = y;
      } else if (C === 'H') {
        const x = num() + ox; cur.push(['L', x, cy]); cx = x;
      } else if (C === 'V') {
        const y = num() + oy; cur.push(['L', cx, y]); cy = y;
      } else if (C === 'C') {
        const a = [num() + ox, num() + oy, num() + ox, num() + oy, num() + ox, num() + oy];
        cur.push(['C', ...a]); cx = a[4]; cy = a[5];
      } else if (C === 'Q') {
        const qx = num() + ox, qy = num() + oy, x = num() + ox, y = num() + oy;
        cur.push(['C', cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy), x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y), x, y]);
        cx = x; cy = y;
      } else if (C === 'Z') {
        cur.push(['Z']); cx = sx; cy = sy;
      } else {
        return null; // arcs etc.: not seen in Slides output; refuse rather than guess
      }
    }
    if (!subs.length || subs.some((sp) => sp.some((seg) => seg.slice(1).some((v) => !Number.isFinite(v))))) return null;
    return subs;
  }

  function paintOf(p) {
    const a = (n) => p.getAttribute(n);
    const zero = (n) => a(n) !== null && parseFloat(a(n)) === 0;
    const fill = a('fill'), stroke = a('stroke');
    const hasFill = !!fill && fill !== 'none' && !/^url\(/.test(fill) && !zero('fill-opacity') && !zero('opacity');
    const hasStroke = !!stroke && stroke !== 'none' && !/^url\(/.test(stroke) && !SELECTION_BLUE.test(stroke) && !zero('stroke-opacity') && !zero('opacity') && !zero('stroke-width');
    return { fill, stroke, hasFill, hasStroke, sw: parseFloat(a('stroke-width')) || 0 };
  }

  // The drawable paths Slides renders for one object, in paint order.
  // Text (glyphs, paragraph groups) and hit areas are left out.
  function renderedPaths(id) {
    const g = elementFor(id);
    if (!g) return null;
    if (g.querySelector('image, foreignObject, video, canvas')) return null;
    const out = [];
    for (const p of g.querySelectorAll('path')) {
      if (p.closest('[class*="text"], g[id$="-paragraph"]')) continue;
      const own = p.closest('g[id^="editor-"]');
      if (own && own !== g && own.id.endsWith('-paragraph')) continue;
      const paint = paintOf(p);
      out.push({ el: p, ...paint });
    }
    return out;
  }

  function hasText(resolved, id) {
    return resolved.some((e) => e[0] === 15 && e[1] === id && typeof e[4] === 'string' && e[4].trim());
  }

  // What converting this object costs, in a few words (null = can't convert).
  function convertibleKind(resolved, entry) {
    if (!entry || entry[0] !== 3 || isEditableShape(entry)) return null;
    const paths = renderedPaths(entry[1]);
    if (!paths) return null;
    const visible = paths.filter((p) => p.hasFill || p.hasStroke);
    if (!visible.length && !hasText(resolved, entry[1])) return null;
    if (visible.some((p) => !parseRenderedD(p.el.getAttribute('d')))) return null;
    if (getProp(entry[4], 33) !== undefined) return 'wordart';
    // Lines and connectors carry no fill of their own (14 = 0); their heads
    // may be filled paths. A cube's outline is also an open stroke, so the
    // fill flag is what tells them apart.
    const strokeOnlyOpen = visible.some((p) => p.hasStroke && !p.hasFill && !/z\s*$/i.test(p.el.getAttribute('d') || ''));
    if (strokeOnlyOpen && getProp(entry[4], 14) === 0) return 'line';
    if (visible.filter((p) => p.hasFill).length > 1) return 'shaded';
    return 'preset';
  }

  const KIND_NOTE = {
    wordart: 'Text becomes outlines',
    line: 'Arrowheads become separate shapes',
    shaded: 'Shading becomes flat colours',
    preset: 'Shape handles go away',
  };

  function toPageMatrix(el, pageInv) {
    const c = el.getScreenCTM();
    return c ? matMul(pageInv, [c.a, c.b, c.c, c.d, c.e, c.f]) : null;
  }

  // Path in page units → type 1 shape entry with a translate-only transform
  // (pre-multiplied by `parentInv` when the object sits inside a group).
  function shapeFromPath(subs, M, paint, parentInv) {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    const pts = subs.map((sp) => sp.map((seg) => {
      if (seg[0] === 'Z') return seg;
      const o = [seg[0]];
      for (let k = 1; k < seg.length; k += 2) {
        const q = apply(M, seg[k], seg[k + 1]);
        o.push(q.x, q.y);
        minX = Math.min(minX, q.x); maxX = Math.max(maxX, q.x);
        minY = Math.min(minY, q.y); maxY = Math.max(maxY, q.y);
      }
      return o;
    }));
    const meta = [], coords = [];
    let last = null;
    const emit = (op, nums) => {
      if (op === last && (op === 1 || op === 3)) meta[meta.length - 1] += nums.length;
      else meta.push(op, nums.length);
      nums.forEach((v, k) => coords.push(Math.round(v - (k % 2 ? minY : minX))));
      last = op;
    };
    pts.forEach((sp) => sp.forEach((seg) => {
      if (seg[0] === 'M') emit(0, seg.slice(1));
      else if (seg[0] === 'L') emit(1, seg.slice(1));
      else if (seg[0] === 'C') emit(3, seg.slice(1));
      else emit(5, []);
    }));
    const w = Math.max(1, Math.round(maxX - minX)), h = Math.max(1, Math.round(maxY - minY));
    const scale = Math.sqrt(Math.abs(M[0] * M[3] - M[1] * M[2])) || 1;
    const props = [8, w, 9, h, 12, [[1, 1, meta, coords, [], 0]],
      14, paint.hasFill ? 1 : 0, 15, paint.hasFill ? paint.fill : '#EEEEEE'];
    if (paint.hasStroke) props.push(18, 1, 19, paint.stroke, 22, Math.max(1, Math.round(paint.sw * scale)));
    else props.push(18, 0, 23, 0);
    const T = matMul(parentInv, [1, 0, 0, 1, Math.round(minX), Math.round(minY)]);
    return { entry: [3, newId(), 1, T, props], area: w * h };
  }

  // Replace every convertible object in `resolved` with custom shapes.
  // Returns { resolved, converted: [{ from, to, kind }] } or null.
  function convertSelection(resolved) {
    const page = pageCTM();
    const pageInv = page && matInv(page);
    if (!pageInv) return null;
    const replaced = new Map(); // old id → { id: new top id, carrier, shapes, group }
    const converted = [];
    const srcOf = {}; // new shape/group id → id of the slide object it replaces
    for (const e of resolved) {
      const kind = convertibleKind(resolved, e);
      if (!kind) continue;
      const parentToPage = matMul(localToPage(resolved, e), matInv(e[3]) || [1, 0, 0, 1, 0, 0]);
      const parentInv = matInv(parentToPage) || [1, 0, 0, 1, 0, 0];
      const paths = renderedPaths(e[1]);
      let made = [];
      for (const p of paths) {
        if (!p.hasFill && !p.hasStroke) continue;
        const subs = parseRenderedD(p.el.getAttribute('d'));
        const M = toPageMatrix(p.el, pageInv);
        if (!subs || !M) { made = null; break; }
        made.push(shapeFromPath(subs, M, p, parentInv));
      }
      if (!made) continue;
      if (!made.length) {
        // Text-only object (text box): keep its frame as an invisible carrier.
        const frame = paths.find((p) => parseRenderedD(p.el.getAttribute('d')));
        const M = frame && toPageMatrix(frame.el, pageInv);
        if (!M) continue;
        made.push(shapeFromPath(parseRenderedD(frame.el.getAttribute('d')), M, { hasFill: false, hasStroke: false }, parentInv));
      }
      const carrier = made.reduce((a, b) => (b.area > a.area ? b : a)).entry[1];
      const group = made.length > 1 ? [2, newId(), made.map((m) => m.entry[1]), [1, 0, 0, 1, 0, 0]] : null;
      made.forEach((m) => { srcOf[m.entry[1]] = e[1]; });
      if (group) srcOf[group[1]] = e[1];
      replaced.set(e[1], { id: group ? group[1] : made[0].entry[1], carrier, shapes: made.map((m) => m.entry), group });
      converted.push({ from: e[1], to: group ? group[1] : made[0].entry[1], kind });
    }
    if (!converted.length) return null;
    const out = [];
    for (const e of resolved) {
      const r = typeof e[1] === 'string' ? replaced.get(e[1]) : null;
      if (e[0] === 3 && r) {
        out.push(...r.shapes);
        if (r.group) out.push(r.group);
      } else if (e[0] === 2) {
        const c = JSON.parse(JSON.stringify(e));
        c[2] = (c[2] || []).map((id) => (replaced.has(id) ? replaced.get(id).id : id));
        out.push(c);
      } else if (r) {
        // Text, text style, alt text: follow the shape that now carries them.
        const c = JSON.parse(JSON.stringify(e));
        c[1] = r.carrier;
        out.push(c);
      } else {
        out.push(e);
      }
    }
    return { resolved: out, converted, srcOf };
  }

  return {
    MIME, iframe, textbox, focusTextbox, wrap, unwrap,
    readSelection, paste, pressKey, sleep, waitForSelection,
    getProp, setProp, newId, pathRecord, isEditableShape,
    matMul, matInv, apply, localToPage, pageCTM, elementFor, currentPageGroup, visibleWorkspaceRect,
    topLevelOrder, topLevelIdOf, pressArrange, moveToIndex,
    ZOOM_MIN, ZOOM_MAX, zoomPctFromCTM, setSlidesZoom, scrollPagePointTo, matchSlidesView,
    decodePath, encodePath, normalizeSubs, typeFor, svgPathD,
    convertibleKind, convertSelection, KIND_NOTE, parseRenderedD, solveAffine,
  };
})();
