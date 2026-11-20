// Geometry for Shape tools (bundled into extension/geo-ops.js by build.js).
//
// Works on the editor's node model, in Slides page units:
//   subpath = { closed, nodes: [{ x, y, in, out }] }, in/out absolute or null.
// Booleans and stroke outlines run through Paper.js, which keeps curves as
// curves (a circle stays four Béziers after a union), so the results open
// cleanly in Edit Shape.

import paper from 'paper';
import { PaperOffset } from 'paperjs-offset';

let ready = false;
function setup() {
  if (ready) return;
  paper.setup(new paper.Size(1, 1));
  ready = true;
}

// ── node model <-> Paper ─────────────────────────────────────────────────
function toPaper(subs, fillRule = 'nonzero') {
  setup();
  const children = [];
  for (const s of subs) {
    if (!s.nodes || s.nodes.length < 2) continue;
    const segs = s.nodes.map((n) => new paper.Segment(
      new paper.Point(n.x, n.y),
      n.in ? new paper.Point(n.in.x - n.x, n.in.y - n.y) : null,
      n.out ? new paper.Point(n.out.x - n.x, n.out.y - n.y) : null,
    ));
    children.push(new paper.Path({ segments: segs, closed: !!s.closed, insert: false }));
  }
  const cp = new paper.CompoundPath({ children, insert: false });
  cp.fillRule = fillRule;
  return cp;
}

function pathsOf(item) {
  if (!item) return [];
  if (item instanceof paper.CompoundPath) return item.children.slice();
  if (item instanceof paper.Path) return [item];
  if (item.children) return item.children.flatMap(pathsOf);
  return [];
}

const EPS = 1e-6;
function fromPaper(item) {
  // Outer contours clockwise, holes counter-clockwise, nothing overlapping:
  // renders the same under nonzero and evenodd, whichever Slides applies.
  try { if (item && item.reorient) item.reorient(true, true); } catch { /* keep as is */ }
  const out = [];
  for (const p of pathsOf(item)) {
    if (!p.segments || p.segments.length < 2) continue;
    const nodes = p.segments.map((sg) => {
      const x = sg.point.x, y = sg.point.y;
      const hi = sg.handleIn, ho = sg.handleOut;
      return {
        x, y,
        in: hi && (Math.abs(hi.x) > EPS || Math.abs(hi.y) > EPS) ? { x: x + hi.x, y: y + hi.y } : null,
        out: ho && (Math.abs(ho.x) > EPS || Math.abs(ho.y) > EPS) ? { x: x + ho.x, y: y + ho.y } : null,
      };
    });
    out.push({ closed: !!p.closed, nodes });
  }
  return out;
}

function areaOf(item) {
  try { return Math.abs(item.area || 0); } catch { return 0; }
}

// Drop slivers and zero-area leftovers that booleans sometimes leave.
function clean(item, minArea) {
  for (const p of pathsOf(item)) {
    if (p.closed && Math.abs(p.area) < minArea) p.remove();
  }
  return item;
}

// ── Booleans ────────────────────────────────────────────────────────────
// `shapes` bottom → top, each { subs, fillRule }. Figma semantics:
// union/intersect/exclude fold across all; subtract removes everything above
// the bottom shape from it.
const OPS = { union: 'unite', subtract: 'subtract', intersect: 'intersect', exclude: 'exclude' };

// Paper's booleans can misfire on exact tangencies (a circle's extreme
// point lying exactly on a square's edge, which aligned slide shapes do all
// the time). So every result is checked against its inputs at sample points
// and, if it disagrees, recomputed with the inputs turned by a hair and the
// result turned back. The best of a few tries wins.
function insideFn(op, items) {
  return (pt) => {
    const hits = items.map((it) => it.contains(pt));
    if (op === 'union') return hits.some(Boolean);
    if (op === 'intersect') return hits.every(Boolean);
    if (op === 'subtract') return hits[0] && !hits.slice(1).some(Boolean);
    return hits.filter(Boolean).length % 2 === 1; // exclude
  };
}
function mismatch(op, items, result, bounds) {
  const want = insideFn(op, items);
  const res = result.clone({ insert: false });
  res.fillRule = 'evenodd';
  let bad = 0, n = 0;
  const N = 24;
  for (let i = 0; i < N; i++) {
    for (let j = 0; j < N; j++) {
      // Jittered grid, kept off exact edges.
      const x = bounds.x + bounds.width * (i + 0.37 + 0.26 * ((i * 7 + j * 3) % 5) / 5) / N;
      const y = bounds.y + bounds.height * (j + 0.41 + 0.22 * ((i * 3 + j * 5) % 7) / 7) / N;
      const pt = new paper.Point(x, y);
      if (want(pt) !== res.contains(pt)) bad++;
      n++;
    }
  }
  return bad / n;
}
function combine(op, items) {
  const fn = OPS[op];
  if (op === 'subtract') {
    const rest = items.slice(1).reduce((a, b) => a.unite(b, { insert: false }));
    return items[0].subtract(rest, { insert: false });
  }
  return items.reduce((a, b) => a[fn](b, { insert: false }));
}

function boolean(op, shapes) {
  setup();
  const fn = OPS[op];
  if (!fn) throw new Error('unknown op ' + op);
  if (!shapes || shapes.length < 2) throw new Error('need two or more shapes');
  const items = shapes.map((s) => {
    // Open subpaths have no area: close them so they still take part.
    const subs = s.subs.map((sp) => Object.assign({}, sp, { closed: true }));
    // Resolve each input's own overlaps first so its fill rule is honoured.
    const raw = toPaper(subs, s.fillRule || 'nonzero');
    const u = raw.unite(raw, { insert: false }) || raw;
    u.fillRule = 'nonzero';
    return u;
  });
  let size = 0;
  let bounds = null;
  items.forEach((it) => {
    const b = it.bounds;
    size = Math.max(size, b.width, b.height);
    bounds = bounds ? bounds.unite(b) : b.clone();
  });
  const centre = bounds.center;
  let best = null;
  for (let attempt = 0; attempt < 4; attempt++) {
    let acc;
    try {
      if (!attempt) acc = combine(op, items);
      else {
        const ang = 0.013 * attempt; // degrees
        const turned = items.map((it) => { const c = it.clone({ insert: false }); c.rotate(ang, centre); return c; });
        acc = combine(op, turned);
        acc.rotate(-ang, centre);
      }
    } catch (err) {
      continue;
    }
    clean(acc, Math.max(1, size * size * 1e-7));
    const err = mismatch(op, items, acc, bounds);
    if (!best || err < best.err) best = { acc, err };
    if (err < 0.004) break;
  }
  if (!best) throw new Error('boolean failed');
  const subs = fromPaper(best.acc);
  return { subs, empty: !subs.length || areaOf(best.acc) < 1, error: best.err };
}

// ── Stroke outlines ─────────────────────────────────────────────────────
// width in page units; cap 'butt' | 'round' | 'square'; join 'miter' |
// 'round' | 'bevel'; dashes = [on, off, ...] in page units or null.
function dashSplit(path, dashes, dashOffset = 0) {
  const total = dashes.reduce((a, b) => a + b, 0);
  if (!(total > 0)) return [path];
  const len = path.length;
  const pieces = [];
  let pos = -((dashOffset % total) + total) % total;
  let i = 0;
  while (pos < len && pieces.length < 4000) {
    const on = dashes[i % dashes.length];
    const off = dashes[(i + 1) % dashes.length];
    const a = Math.max(0, pos), b = Math.min(len, pos + on);
    if (b - a > 1e-3) {
      const c = path.clone({ insert: false });
      if (c.closed) c.splitAt(0); // open it at the start point
      let piece = c;
      if (b < len - 1e-3) { piece.splitAt(b); }
      // splitAt keeps the first part in `piece`; now cut the head.
      if (a > 1e-3) {
        const tail = piece.splitAt(a);
        piece = tail || piece;
      }
      pieces.push(piece);
    }
    pos += on + off;
    i += 2;
  }
  return pieces;
}

function outlineStroke(subs, width, opts = {}) {
  setup();
  const cap = opts.cap || 'butt';
  const join = opts.join || 'miter';
  const limit = opts.miterLimit || 4;
  const half = width / 2;
  let parts = [];
  for (const s of subs) {
    if (!s.nodes || s.nodes.length < 2) continue;
    let p = toPaper([s]).children[0];
    if (!p) continue;
    const pieces = opts.dashes && opts.dashes.length ? dashSplit(p, opts.dashes, opts.dashOffset || 0) : [p];
    for (const piece of pieces) {
      let o;
      try {
        o = PaperOffset.offsetStroke(piece, half, { cap, join, limit, insert: false });
      } catch (err) {
        o = null;
      }
      if (o) parts.push(o);
    }
  }
  if (!parts.length) return { subs: [], empty: true };
  let acc = parts.reduce((a, b) => a.unite(b, { insert: false }));
  clean(acc, Math.max(0.5, width * width * 1e-4));
  const out = fromPaper(acc);
  return { subs: out, empty: !out.length };
}

// ── Offset (inside / outside strokes) ─────────────────────────────────
// Grow (d > 0) or shrink (d < 0) a filled shape by |d|. paperjs-offset
// drops holes when given a compound path, so each outline is offset on its
// own: outer contours by d, holes by -d (a hole shrinks when the shape
// grows), then holes are cut back out.
function offsetSubs(subs, d, opts = {}) {
  setup();
  const join = opts.join || 'miter';
  const closed = subs.filter((sp) => sp.closed && sp.nodes.length > 2);
  if (!closed.length || !d) return { subs: closed.length ? subs : [], empty: !closed.length };
  const cp = toPaper(closed, 'evenodd');
  const u = cp.unite(cp, { insert: false }) || cp;
  try { u.reorient(true, true); } catch { /* keep */ }
  const paths = pathsOf(u);
  const off = (p, dd) => {
    try { return PaperOffset.offset(p, dd, { join, limit: opts.miterLimit || 10, insert: false }); } catch { return null; }
  };
  let acc = null;
  paths.filter((p) => p.clockwise).forEach((p) => {
    const o = off(p, d);
    if (o) acc = acc ? acc.unite(o, { insert: false }) : o;
  });
  if (!acc) return { subs: [], empty: true };
  paths.filter((p) => !p.clockwise).forEach((h) => {
    const o = off(h, -d);
    if (o && Math.abs(o.area) > 1) acc = acc.subtract(o, { insert: false });
  });
  const out = fromPaper(acc);
  return { subs: out, empty: !out.length };
}

// ── Glyphs → node model ─────────────────────────────────────────────────
// commands: fontkit path commands ({ command, args }) in font units, y up.
// m maps font units to page units (includes the y flip).
function glyphToSubs(commands, m) {
  const ap = (x, y) => ({ x: m[0] * x + m[2] * y + m[4], y: m[1] * x + m[3] * y + m[5] });
  const subs = [];
  let cur = null, last = null, start = null;
  for (const c of commands) {
    const a = c.args;
    if (c.command === 'moveTo') {
      start = ap(a[0], a[1]);
      cur = { closed: false, nodes: [{ x: start.x, y: start.y, in: null, out: null }] };
      subs.push(cur);
      last = { x: a[0], y: a[1] };
    } else if (c.command === 'lineTo') {
      const p = ap(a[0], a[1]);
      cur.nodes.push({ x: p.x, y: p.y, in: null, out: null });
      last = { x: a[0], y: a[1] };
    } else if (c.command === 'quadraticCurveTo') {
      const q = { x: a[0], y: a[1] }, e = { x: a[2], y: a[3] };
      const c1 = ap(last.x + 2 / 3 * (q.x - last.x), last.y + 2 / 3 * (q.y - last.y));
      const c2 = ap(e.x + 2 / 3 * (q.x - e.x), e.y + 2 / 3 * (q.y - e.y));
      const p = ap(e.x, e.y);
      cur.nodes[cur.nodes.length - 1].out = c1;
      cur.nodes.push({ x: p.x, y: p.y, in: c2, out: null });
      last = e;
    } else if (c.command === 'bezierCurveTo') {
      const c1 = ap(a[0], a[1]), c2 = ap(a[2], a[3]), p = ap(a[4], a[5]);
      cur.nodes[cur.nodes.length - 1].out = c1;
      cur.nodes.push({ x: p.x, y: p.y, in: c2, out: null });
      last = { x: a[4], y: a[5] };
    } else if (c.command === 'closePath') {
      if (cur) {
        cur.closed = true;
        const n = cur.nodes;
        if (n.length > 1) {
          const f = n[0], l = n[n.length - 1];
          if (Math.abs(f.x - l.x) < 1e-3 && Math.abs(f.y - l.y) < 1e-3) { n.pop(); f.in = l.in; }
        }
      }
      cur = null;
    }
  }
  return subs.filter((s) => s.nodes.length > 1);
}

// Merge glyph outlines into one clean shape (overlapping contours in script
// fonts and variable-font instances otherwise show seams).
function unionAll(subs) {
  setup();
  if (!subs.length) return [];
  const cp = toPaper(subs, 'nonzero');
  const u = cp.unite(cp, { insert: false }) || cp;
  return fromPaper(u);
}

export { boolean, outlineStroke, offsetSubs, glyphToSubs, unionAll, toPaper, fromPaper };
