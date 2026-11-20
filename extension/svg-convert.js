// SVG → Google Slides clipboard payload, in plain JavaScript.
//
// A line-for-line port of the parts of svg_to_slides.py (collect,
// extract_gradients, expand_path, normalize_arcs, stroke_to_outline and
// their helpers) and slides_clip.py (build_clip_bundle_at) that the
// extension used to run in Pyodide. Same arithmetic in the same order, and
// Python's rounding (ties to even) and its errors (bad numbers, a zero-size
// viewBox) are kept, so a file converts the same as before or fails the
// same way. Checked against the Python on every SVG in the repo.
//
// The Python (svg_to_slides.py, cloud/slides_clip.py) stays the source for
// the server and the command-line tool; a change there needs the same change
// here. tools/convert-parity/ checks the two still agree.
(() => {
  'use strict';

  const COORD = 100000;
  const KAPPA = 0.5522847498;
  const EMU_PER_UNIT = 30;
  const PT_TO_EMU = 12700;
  const GRID_SCALE = 1.5;
  const GRID_GUTTER = 0.08;
  const OP_MOVE = 0, OP_LINE = 1, OP_CUBIC = 3, OP_CLOSE = 5;
  const TYPE_CUSTOM = 1, TYPE_POLYLINE = 138;
  const EDITABLE_POINTS = true;
  const EDITABLE_MAX_ANCHORS = 150;
  const MIME = 'application/x-vnd.google-docs-drawings-object+wrapped';

  // ── Python semantics ──────────────────────────────────────────────────

  class ConvertError extends Error {}
  const fail = (msg) => { throw new ConvertError(msg); };

  // float(s): Python's grammar, not parseFloat's ("10px" is an error).
  const FLOAT_RE = /^[ \t\n\r\f\v]*[+-]?(?:(?:\d(?:_?\d)*(?:\.(?:\d(?:_?\d)*)?)?|\.\d(?:_?\d)*)(?:[eE][+-]?\d(?:_?\d)*)?|inf(?:inity)?|nan)[ \t\n\r\f\v]*$/i;
  function pyFloat(v) {
    if (typeof v === 'number') return v;
    if (v == null || !FLOAT_RE.test(v)) fail(`could not convert string to float: '${v}'`);
    const s = v.trim().replace(/_/g, '').toLowerCase();
    if (/^[+-]?inf/.test(s)) return s[0] === '-' ? -Infinity : Infinity;
    if (/^[+-]?nan$/.test(s)) return NaN;
    return Number(s);
  }

  // round(x): nearest integer, ties to even. Errors on inf/nan like Python.
  function pyRound(x) {
    if (!Number.isFinite(x)) fail('cannot convert float to integer');
    const f = Math.floor(x), d = x - f;
    if (d < 0.5) return f + 0;
    if (d > 0.5) return f + 1;
    return f % 2 === 0 ? f + 0 : f + 1;
  }

  // round(x, n) for n > 0: correctly rounded to n decimals, ties to even,
  // on the double's exact value (what CPython does).
  function pyRoundN(x, n) {
    if (!Number.isFinite(x) || x === 0) return x;
    const p = 10 ** n;
    const y = x * p;
    const fr = Math.abs(y - Math.trunc(y));
    if (Math.abs(fr - 0.5) > 1e-6) {
      const r = Math.round(Math.abs(y)) / p;
      return x < 0 ? -r : r;
    }
    // Near a tie: decide on the exact decimal expansion.
    const s = Math.abs(x).toFixed(100);
    const dot = s.indexOf('.');
    const keep = s.slice(0, dot) + s.slice(dot + 1, dot + 1 + n);
    const rest = s.slice(dot + 1 + n);
    let up;
    if (rest[0] > '5') up = true;
    else if (rest[0] < '5') up = false;
    else if (/[1-9]/.test(rest.slice(1))) up = true;
    else up = Number(keep[keep.length - 1]) % 2 === 1;
    const digits = (BigInt(keep) + (up ? 1n : 0n)).toString().padStart(n + 1, '0');
    const r = Number(digits.slice(0, digits.length - n) + '.' + digits.slice(digits.length - n));
    return x < 0 ? -r : r;
  }

  // str(round(v, 4)); only ever parsed back, so any exact spelling works.
  const fmt = (v) => { const r = pyRoundN(v, 4); return Object.is(r, -0) ? '-0.0' : String(r); };
  const F = (...vals) => vals.map(fmt).join(' ');
  const mod = (a, m) => ((a % m) + m) % m;
  const hex2 = (n) => n.toString(16).toUpperCase().padStart(2, '0');
  // math.hypot as CPython 3.12 computes it (vector_norm): exact squares and
  // sums, then one correction step. Math.hypot rounds differently, which
  // changes how many pieces some arcs are cut into.
  const SPLIT = 134217729; // 2^27 + 1
  function twoProd(a, b) {
    const p = a * b;
    let t = SPLIT * a; const ah = t - (t - a), al = a - ah;
    t = SPLIT * b; const bh = t - (t - b), bl = b - bh;
    return [p, ((ah * bh - p) + ah * bl + al * bh) + al * bl];
  }
  const fastSum = (a, b) => { const hi = a + b; return [hi, (a - hi) + b]; };
  function pyHypot(x, y) {
    x = Math.abs(x); y = Math.abs(y);
    const max = Math.max(x, y);
    if (max === Infinity) return Infinity;
    if (Number.isNaN(x) || Number.isNaN(y)) return NaN;
    if (max === 0) return max;
    // frexp: max = m * 2^e with 0.5 <= m < 1
    let e = Math.floor(Math.log2(max)) + 1;
    let scale = 2 ** -e;
    if (max * scale >= 1) { e += 1; scale = 2 ** -e; } else if (max * scale < 0.5) { e -= 1; scale = 2 ** -e; }
    if (e < -1021 || !Number.isFinite(scale)) return Math.hypot(x, y); // subnormal range: never reached here
    let csum = 1, frac1 = 0, frac2 = 0;
    for (let v of [x, y]) {
      v *= scale;
      const [phi, plo] = twoProd(v, v);
      const [shi, slo] = fastSum(csum, phi);
      csum = shi; frac1 += plo; frac2 += slo;
    }
    let h = Math.sqrt(csum - 1 + (frac1 + frac2));
    const [phi, plo] = twoProd(-h, h);
    const [shi, slo] = fastSum(csum, phi);
    csum = shi; frac1 += plo; frac2 += slo;
    const r = csum - 1 + (frac1 + frac2);
    h += r / (2 * h);
    return h / scale;
  }
  const radians = (d) => d * (Math.PI / 180);
  const degrees = (r) => r * (180 / Math.PI);

  // ElementTree access: tag without namespace, un-namespaced attributes,
  // element children only.
  const tagOf = (el) => el.localName;
  const attr = (el, k, dflt = null) => (el.hasAttributeNS(null, k) ? el.getAttributeNS(null, k) : dflt);
  const kids = (el) => [...el.children];
  function* iter(el) { yield el; for (const c of el.children) yield* iter(c); }

  // ── Colors ────────────────────────────────────────────────────────────

  const CSS_COLORS = {
    black: '#000000', white: '#ffffff', red: '#ff0000', green: '#008000',
    blue: '#0000ff', yellow: '#ffff00', orange: '#ffa500', purple: '#800080',
    pink: '#ffc0cb', gray: '#808080', grey: '#808080', brown: '#a52a2a',
    cyan: '#00ffff', magenta: '#ff00ff', lime: '#00ff00', navy: '#000080',
    teal: '#008080', silver: '#c0c0c0', maroon: '#800000', olive: '#808000',
    aqua: '#00ffff', fuchsia: '#ff00ff', coral: '#ff7f50', gold: '#ffd700',
    indigo: '#4b0082', violet: '#ee82ee', turquoise: '#40e0d0',
    darkblue: '#00008b', darkgreen: '#006400', darkred: '#8b0000',
    darkgray: '#a9a9a9', darkgrey: '#a9a9a9', lightgray: '#d3d3d3',
    lightgrey: '#d3d3d3', lightblue: '#add8e6', beige: '#f5f5dc',
    ivory: '#fffff0', khaki: '#f0e68c', lavender: '#e6e6fa',
    lightgreen: '#90ee90', lightyellow: '#ffffe0', limegreen: '#32cd32',
    orangered: '#ff4500', royalblue: '#4169e1', sienna: '#a0522d',
    skyblue: '#87ceeb', slategray: '#708090', steelblue: '#4682b4',
    tan: '#d2b48c', tomato: '#ff6347', wheat: '#f5deb3',
    whitesmoke: '#f5f5f5', yellowgreen: '#9acd32', crimson: '#dc143c',
    darkorange: '#ff8c00', deeppink: '#ff1493', dodgerblue: '#1e90ff',
    firebrick: '#b22222', forestgreen: '#228b22', goldenrod: '#daa520',
    hotpink: '#ff69b4', mediumblue: '#0000cd', mediumpurple: '#9370db',
    midnightblue: '#191970', peru: '#cd853f', plum: '#dda0dd',
    rosybrown: '#bc8f8f', saddlebrown: '#8b4513', salmon: '#fa8072',
    seagreen: '#2e8b57', snow: '#fffafa', slateblue: '#6a5acd',
    springgreen: '#00ff7f', darkviolet: '#9400d3', deepskyblue: '#00bfff',
  };
  const hasOwn = (o, k) => Object.prototype.hasOwnProperty.call(o, k);

  function parseColor(s) {
    if (!s) return null;
    s = s.trim();
    const sl = s.toLowerCase();
    if (sl === 'none' || sl === 'transparent' || sl === '') return null;
    if (sl === 'currentcolor') return null;
    if (hasOwn(CSS_COLORS, sl)) return CSS_COLORS[sl].replace(/^#+/, '').toUpperCase();
    if (s.startsWith('#')) {
      let h = s.slice(1);
      if ([...h].length === 3) { const c = [...h]; h = c[0] + c[0] + c[1] + c[1] + c[2] + c[2]; }
      return [...h].length === 6 ? h.toUpperCase() : null;
    }
    let m = /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/.exec(sl);
    if (m) return hex2(parseInt(m[1], 10)) + hex2(parseInt(m[2], 10)) + hex2(parseInt(m[3], 10));
    m = /^rgba?\(\s*(\d+(?:\.\d+)?)%\s*,\s*(\d+(?:\.\d+)?)%\s*,\s*(\d+(?:\.\d+)?)%/.exec(sl);
    if (m) {
      const p = (v) => pyRound(pyFloat(v) / 100 * 255);
      return hex2(p(m[1])) + hex2(p(m[2])) + hex2(p(m[3]));
    }
    return '000000';
  }

  // ── Gradients (only the first stop's colour reaches the payload) ──────

  function pct(raw, dflt = '0') {
    const s = raw ? raw.trim() : dflt;
    if (s.endsWith('%')) return pyFloat(s.slice(0, -1)) / 100;
    return pyFloat(s);
  }

  function extractGradients(root) {
    const grads = new Map();
    for (const el of iter(root)) {
      const tag = tagOf(el);
      if (tag !== 'linearGradient' && tag !== 'radialGradient') continue;
      const gid = attr(el, 'id');
      if (!gid) continue;
      const stops = [];
      for (const child of iter(el)) {
        if (tagOf(child) !== 'stop') continue;
        const style = attr(child, 'style', '');
        const offRaw = attr(child, 'offset', '0');
        const pos = pyRound(pct(offRaw) * 100000);
        const cm = /stop-color\s*:\s*([^;]+)/.exec(style);
        const colorRaw = cm ? cm[1].trim() : attr(child, 'stop-color', '#000000');
        const hex = parseColor(colorRaw) || '000000';
        const om = /stop-opacity\s*:\s*([^;]+)/.exec(style);
        const opacityRaw = om ? om[1].trim() : attr(child, 'stop-opacity', '1');
        const alpha = pyRound(pyFloat(opacityRaw) * 100000);
        stops.push([pos, hex, alpha]);
      }
      if (!stops.length) continue;
      stops.sort((a, b) => a[0] - b[0]);
      const usos = attr(el, 'gradientUnits', 'objectBoundingBox') === 'userSpaceOnUse';
      // Parsed for the same errors as the Python; the values aren't used.
      if (tag === 'linearGradient') {
        let x1, y1, x2, y2;
        if (usos) { x1 = pyFloat(attr(el, 'x1', 0)); y1 = pyFloat(attr(el, 'y1', 0)); x2 = pyFloat(attr(el, 'x2', 1)); y2 = pyFloat(attr(el, 'y2', 0)); }
        else { x1 = pct(attr(el, 'x1', '0')); y1 = pct(attr(el, 'y1', '0')); x2 = pct(attr(el, 'x2', '1')); y2 = pct(attr(el, 'y2', '0')); }
        mod(pyRound(degrees(Math.atan2(y2 - y1, x2 - x1)) * 60000), 21600000);
      } else if (usos) { pyFloat(attr(el, 'cx', 50)); pyFloat(attr(el, 'cy', 50)); }
      else { pyRound(pct(attr(el, 'cx', '0.5')) * 100000); pyRound(pct(attr(el, 'cy', '0.5')) * 100000); }
      grads.set(gid, { stops });
    }
    return grads;
  }

  // ── Style ─────────────────────────────────────────────────────────────

  function parseStyle(el) {
    const props = new Map();
    for (const part of attr(el, 'style', '').split(';')) {
      const i = part.indexOf(':');
      if (i < 0) continue;
      props.set(part.slice(0, i).trim().toLowerCase(), part.slice(i + 1).trim());
    }
    return props;
  }
  function getProp(style, el, ...keys) {
    for (const k of keys) {
      if (style.has(k)) return style.get(k);
      const v = attr(el, k);
      if (v !== null) return v;
    }
    return null;
  }

  function resolveFillStroke(el, gradients, inhFill) {
    const style = parseStyle(el);
    const fillRaw = getProp(style, el, 'fill');
    const strokeRaw = getProp(style, el, 'stroke');
    const swRaw = getProp(style, el, 'stroke-width');
    let fill;
    if (fillRaw && fillRaw.toLowerCase().startsWith('url(#')) {
      const m = /^url\(#([^)]+)\)/.exec(fillRaw);
      fill = m && gradients.has(m[1]) ? gradients.get(m[1]) : null;
      if (fill === null) fill = inhFill;
    } else if (fillRaw && fillRaw.toLowerCase().trim() === 'currentcolor') {
      fill = inhFill;
    } else if (fillRaw) {
      fill = parseColor(fillRaw);
    } else {
      fill = inhFill;
    }
    let stroke;
    if (strokeRaw && strokeRaw.toLowerCase().startsWith('url(#')) {
      const m = /^url\(#([^)]+)\)/.exec(strokeRaw);
      stroke = m && gradients.has(m[1]) ? gradients.get(m[1]) : null;
    } else {
      stroke = strokeRaw ? parseColor(strokeRaw) : null;
    }
    let sw;
    try { sw = swRaw ? pyFloat(swRaw.replace(/[^\d.]/g, '')) : 0; } catch { sw = 0; }
    if (stroke && swRaw === null) sw = 1;
    return [fill, stroke, sw];
  }

  // ── Basic shapes → path data ──────────────────────────────────────────

  function rectToD(el) {
    const x = pyFloat(attr(el, 'x', 0)), y = pyFloat(attr(el, 'y', 0));
    const w = pyFloat(attr(el, 'width', 0)), h = pyFloat(attr(el, 'height', 0));
    let rx = pyFloat(attr(el, 'rx') || attr(el, 'ry') || 0);
    let ry = pyFloat(attr(el, 'ry') || attr(el, 'rx') || 0);
    if (w <= 0 || h <= 0) return null;
    rx = Math.min(rx, w / 2); ry = Math.min(ry, h / 2);
    if (rx === 0 && ry === 0) {
      return `M ${F(x)},${F(y)} L ${F(x + w)},${F(y)} L ${F(x + w)},${F(y + h)} L ${F(x)},${F(y + h)} Z`;
    }
    const kx = KAPPA * rx, ky = KAPPA * ry;
    return `M ${F(x + rx)},${F(y)} L ${F(x + w - rx)},${F(y)} ` +
      `C ${F(x + w - rx + kx)},${F(y)} ${F(x + w)},${F(y + ry - ky)} ${F(x + w)},${F(y + ry)} ` +
      `L ${F(x + w)},${F(y + h - ry)} ` +
      `C ${F(x + w)},${F(y + h - ry + ky)} ${F(x + w - rx + kx)},${F(y + h)} ${F(x + w - rx)},${F(y + h)} ` +
      `L ${F(x + rx)},${F(y + h)} ` +
      `C ${F(x + rx - kx)},${F(y + h)} ${F(x)},${F(y + h - ry + ky)} ${F(x)},${F(y + h - ry)} ` +
      `L ${F(x)},${F(y + ry)} ` +
      `C ${F(x)},${F(y + ry - ky)} ${F(x + rx - kx)},${F(y)} ${F(x + rx)},${F(y)} Z`;
  }
  function ellipseD(cx, cy, rx, ry) {
    const kx = KAPPA * rx, ky = KAPPA * ry;
    return `M ${F(cx)},${F(cy - ry)} ` +
      `C ${F(cx + kx)},${F(cy - ry)} ${F(cx + rx)},${F(cy - ky)} ${F(cx + rx)},${F(cy)} ` +
      `C ${F(cx + rx)},${F(cy + ky)} ${F(cx + kx)},${F(cy + ry)} ${F(cx)},${F(cy + ry)} ` +
      `C ${F(cx - kx)},${F(cy + ry)} ${F(cx - rx)},${F(cy + ky)} ${F(cx - rx)},${F(cy)} ` +
      `C ${F(cx - rx)},${F(cy - ky)} ${F(cx - kx)},${F(cy - ry)} ${F(cx)},${F(cy - ry)} Z`;
  }
  function circleToD(el) {
    const cx = pyFloat(attr(el, 'cx', 0)), cy = pyFloat(attr(el, 'cy', 0)), r = pyFloat(attr(el, 'r', 0));
    return r > 0 ? ellipseD(cx, cy, r, r) : null;
  }
  function ellipseElToD(el) {
    const cx = pyFloat(attr(el, 'cx', 0)), cy = pyFloat(attr(el, 'cy', 0));
    const rx = pyFloat(attr(el, 'rx', 0)), ry = pyFloat(attr(el, 'ry', 0));
    return rx > 0 && ry > 0 ? ellipseD(cx, cy, rx, ry) : null;
  }
  const NUM_RE = /[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?/g;
  function pointsToD(el, close) {
    const pts = attr(el, 'points', '').match(NUM_RE) || [];
    if (pts.length < 4) return null;
    const c = pts.map(Number);
    const pairs = [];
    for (let i = 0; i < c.length - 1; i += 2) pairs.push([c[i], c[i + 1]]);
    let d = `M ${F(pairs[0][0])},${F(pairs[0][1])}`;
    for (const [x, y] of pairs.slice(1)) d += ` L ${F(x)},${F(y)}`;
    return close ? d + ' Z' : d;
  }
  const lineToD = (el) => `M ${F(pyFloat(attr(el, 'x1', 0)))},${F(pyFloat(attr(el, 'y1', 0)))} ` +
    `L ${F(pyFloat(attr(el, 'x2', 0)))},${F(pyFloat(attr(el, 'y2', 0)))}`;

  function elementToD(el) {
    switch (tagOf(el)) {
      case 'rect': return rectToD(el);
      case 'circle': return circleToD(el);
      case 'ellipse': return ellipseElToD(el);
      case 'polygon': return pointsToD(el, true);
      case 'polyline': return pointsToD(el, false);
      case 'line': return lineToD(el);
      case 'path': return attr(el, 'd', '') || null;
      default: return null;
    }
  }

  // ── Arcs → cubics ─────────────────────────────────────────────────────

  function arcToCubics(x1, y1, rx, ry, phiDeg, fa, fs, x2, y2) {
    if (rx === 0 || ry === 0) return [[x2, y2, x2, y2, x2, y2]];
    const phi = radians(phiDeg);
    const cp = Math.cos(phi), sp = Math.sin(phi);
    const dx = (x1 - x2) / 2, dy = (y1 - y2) / 2;
    const x1p = cp * dx + sp * dy;
    const y1p = -sp * dx + cp * dy;
    rx = Math.abs(rx); ry = Math.abs(ry);
    const qx = x1p / rx, qy = y1p / ry;
    const lam = qx * qx + qy * qy;
    if (lam > 1) { const s = Math.sqrt(lam); rx *= s; ry *= s; }
    const rx2 = rx * rx, ry2 = ry * ry;
    const x1p2 = x1p * x1p, y1p2 = y1p * y1p;
    const num = Math.max(0, rx2 * ry2 - rx2 * y1p2 - ry2 * x1p2);
    const den = rx2 * y1p2 + ry2 * x1p2;
    let sq = den ? Math.sqrt(num / den) : 0;
    if (fa === fs) sq = -sq;
    const cxp = sq * rx * y1p / ry;
    const cyp = -sq * ry * x1p / rx;
    const cx = cp * cxp - sp * cyp + (x1 + x2) / 2;
    const cy = sp * cxp + cp * cyp + (y1 + y2) / 2;
    const angle = (ux, uy, vx, vy) => {
      const n = pyHypot(ux, uy) * pyHypot(vx, vy);
      if (n === 0) return 0;
      const a = Math.acos(Math.max(-1, Math.min(1, (ux * vx + uy * vy) / n)));
      return ux * vy - uy * vx < 0 ? -a : a;
    };
    const theta1 = angle(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry);
    let dtheta = angle((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry);
    if (!fs && dtheta > 0) dtheta -= 2 * Math.PI;
    else if (fs && dtheta < 0) dtheta += 2 * Math.PI;
    const nSegs = Math.max(1, Math.ceil(Math.abs(dtheta) / (Math.PI / 2)));
    const dSeg = dtheta / nSegs;
    const out = [];
    let t = theta1;
    const deriv = (ct, st) => { const ddx = -rx * st, ddy = ry * ct; return [cp * ddx - sp * ddy, sp * ddx + cp * ddy]; };
    const ptOn = (ct, st) => [cx + cp * rx * ct - sp * ry * st, cy + sp * rx * ct + cp * ry * st];
    for (let i = 0; i < nSegs; i++) {
      const tanHalf = Math.tan(dSeg / 2);
      const alpha = Math.sin(dSeg) * (Math.sqrt(4 + 3 * tanHalf * tanHalf) - 1) / 3;
      const cosT = Math.cos(t), sinT = Math.sin(t);
      const cosT2 = Math.cos(t + dSeg), sinT2 = Math.sin(t + dSeg);
      const [px1, py1] = ptOn(cosT, sinT);
      const [px2, py2] = ptOn(cosT2, sinT2);
      const [d1x, d1y] = deriv(cosT, sinT);
      const [d2x, d2y] = deriv(cosT2, sinT2);
      out.push([px1 + alpha * d1x, py1 + alpha * d1y, px2 - alpha * d2x, py2 - alpha * d2y, px2, py2]);
      t += dSeg;
    }
    return out;
  }

  function normalizeArcs(d) {
    if (!d.includes('A') && !d.includes('a')) return d;
    const parts = [];
    let cx = 0, cy = 0, mx = 0, my = 0;
    const cubic = (c) => parts.push(`C ${F(c[0])},${F(c[1])} ${F(c[2])},${F(c[3])} ${F(c[4])},${F(c[5])}`);
    for (const [cmd, a] of expandPath(d)) {
      switch (cmd) {
        case 'M': cx = mx = a[0]; cy = my = a[1]; parts.push(`M ${F(cx)},${F(cy)}`); break;
        case 'm': cx = cx + a[0]; cy = cy + a[1]; mx = cx; my = cy; parts.push(`M ${F(cx)},${F(cy)}`); break;
        case 'L': cx = a[0]; cy = a[1]; parts.push(`L ${F(cx)},${F(cy)}`); break;
        case 'l': cx += a[0]; cy += a[1]; parts.push(`L ${F(cx)},${F(cy)}`); break;
        case 'H': cx = a[0]; parts.push(`L ${F(cx)},${F(cy)}`); break;
        case 'h': cx += a[0]; parts.push(`L ${F(cx)},${F(cy)}`); break;
        case 'V': cy = a[0]; parts.push(`L ${F(cx)},${F(cy)}`); break;
        case 'v': cy += a[0]; parts.push(`L ${F(cx)},${F(cy)}`); break;
        case 'C': parts.push(`C ${F(a[0])},${F(a[1])} ${F(a[2])},${F(a[3])} ${F(a[4])},${F(a[5])}`); cx = a[4]; cy = a[5]; break;
        case 'c': {
          const ax1 = cx + a[0], ay1 = cy + a[1], ax2 = cx + a[2], ay2 = cy + a[3], ax = cx + a[4], ay = cy + a[5];
          parts.push(`C ${F(ax1)},${F(ay1)} ${F(ax2)},${F(ay2)} ${F(ax)},${F(ay)}`);
          cx = ax; cy = ay; break;
        }
        case 'S': parts.push(`S ${F(a[0])},${F(a[1])} ${F(a[2])},${F(a[3])}`); cx = a[2]; cy = a[3]; break;
        case 's': parts.push(`s ${F(a[0])},${F(a[1])} ${F(a[2])},${F(a[3])}`); cx += a[2]; cy += a[3]; break;
        case 'Q': parts.push(`Q ${F(a[0])},${F(a[1])} ${F(a[2])},${F(a[3])}`); cx = a[2]; cy = a[3]; break;
        case 'q': parts.push(`q ${F(a[0])},${F(a[1])} ${F(a[2])},${F(a[3])}`); cx += a[2]; cy += a[3]; break;
        case 'T': parts.push(`T ${F(a[0])},${F(a[1])}`); cx = a[0]; cy = a[1]; break;
        case 't': parts.push(`t ${F(a[0])},${F(a[1])}`); cx += a[0]; cy += a[1]; break;
        case 'A': {
          const [rx, ry, phi, fa, fs, x, y] = a;
          for (const c of arcToCubics(cx, cy, rx, ry, phi, pyInt(fa), pyInt(fs), x, y)) cubic(c);
          cx = x; cy = y; break;
        }
        case 'a': {
          const [rx, ry, phi, fa, fs, dx, dy] = a;
          const x = cx + dx, y = cy + dy;
          for (const c of arcToCubics(cx, cy, rx, ry, phi, pyInt(fa), pyInt(fs), x, y)) cubic(c);
          cx = x; cy = y; break;
        }
        case 'Z': case 'z': parts.push('Z'); cx = mx; cy = my; break;
      }
    }
    return parts.join(' ');
  }
  const pyInt = (v) => { if (!Number.isFinite(v)) fail('cannot convert float to integer'); return Math.trunc(v) + 0; };

  // ── Transforms ────────────────────────────────────────────────────────

  function parseTransform(s) {
    const fns = [];
    for (const m of (s || '').matchAll(/(\w+)\(([^)]*)\)/g)) {
      const name = m[1];
      const vals = m[2].trim().split(/[\s,]+/).filter((v) => v).map(pyFloat);
      const need = (n) => { if (vals.length < n) fail(`bad ${name}() in transform`); };
      if (name === 'translate') {
        need(1);
        const tx = vals[0], ty = vals.length > 1 ? vals[1] : 0;
        fns.push((x, y) => [x + tx, y + ty]);
      } else if (name === 'scale') {
        need(1);
        const sx = vals[0], sy = vals.length > 1 ? vals[1] : sx;
        fns.push((x, y) => [x * sx, y * sy]);
      } else if (name === 'rotate') {
        need(1);
        const a = radians(vals[0]);
        const cx = vals.length > 1 ? vals[1] : 0, cy = vals.length > 2 ? vals[2] : 0;
        const ca = Math.cos(a), sa = Math.sin(a);
        fns.push((x, y) => [(x - cx) * ca - (y - cy) * sa + cx, (x - cx) * sa + (y - cy) * ca + cy]);
      } else if (name === 'matrix') {
        need(6);
        const [a, b, c, d, e, f] = vals;
        fns.push((x, y) => [a * x + c * y + e, b * x + d * y + f]);
      }
    }
    if (!fns.length) return null;
    return (x, y) => { for (let i = fns.length - 1; i >= 0; i--) [x, y] = fns[i](x, y); return [x, y]; };
  }
  function chain(outer, inner) {
    if (outer === null) return inner;
    if (inner === null) return outer;
    return (x, y) => outer(...inner(x, y));
  }

  // ── Path tokenizer ────────────────────────────────────────────────────

  const ARGC = { M: 2, L: 2, H: 1, V: 1, C: 6, S: 4, Q: 4, T: 2, A: 7, Z: 0 };
  const TOKEN_RE = /[MLHVCSQTAZmlhvcsqtaz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?/g;
  function expandPath(d) {
    const segs = [];
    let cmd = null, buf = [];
    for (const [t] of d.matchAll(TOKEN_RE)) {
      if (/^[A-Za-z]$/.test(t)) {
        if (cmd !== null) segs.push([cmd, buf]);
        cmd = t; buf = [];
      } else buf.push(Number(t));
    }
    if (cmd !== null) segs.push([cmd, buf]);
    const out = [];
    for (const [c, args] of segs) {
      const n = ARGC[c.toUpperCase()] || 0;
      if (n === 0) { out.push([c, []]); continue; }
      for (let i = 0; i < Math.max(args.length, n); i += n) {
        const chunk = args.slice(i, i + n);
        if (chunk.length < n) break;
        out.push([i > 0 ? (c === 'M' ? 'L' : c === 'm' ? 'l' : c) : c, chunk]);
      }
    }
    return out;
  }

  // ── Stroke → outline ──────────────────────────────────────────────────

  function norm(dx, dy) { const L = pyHypot(dx, dy); return L > 1e-10 ? [dx / L, dy / L] : [0, 0]; }
  function leftNormal(dx, dy) { const [nx, ny] = norm(dx, dy); return [-ny, nx]; }
  function miterOffset(n1, n2, hw, limit = 4) {
    const sx = n1[0] + n2[0], sy = n1[1] + n2[1];
    const denom = n1[0] * sx + n1[1] * sy;
    if (Math.abs(denom) < 1e-8) return [n1[0] * hw, n1[1] * hw];
    const scale = hw / denom;
    if (Math.abs(scale) > limit) return [n1[0] * hw, n1[1] * hw];
    return [sx * scale, sy * scale];
  }
  function bezier3(p0, p1, p2, p3, t) {
    const mt = 1 - t;
    return [mt ** 3 * p0[0] + 3 * mt ** 2 * t * p1[0] + 3 * mt * t ** 2 * p2[0] + t ** 3 * p3[0],
      mt ** 3 * p0[1] + 3 * mt ** 2 * t * p1[1] + 3 * mt * t ** 2 * p2[1] + t ** 3 * p3[1]];
  }

  function sampleSegments(d, n = 20) {
    let current = [];
    let mx = 0, my = 0, cx = 0, cy = 0;
    let last = null;
    const polylines = [];
    const ap = (x, y) => { const l = current[current.length - 1]; if (!current.length || l[0] !== x || l[1] !== y) current.push([x, y]); };
    const bez = (p0, p1, p2, p3) => { for (let i = 1; i <= n; i++) ap(...bezier3(p0, p1, p2, p3, i / n)); };
    const flush = (closed) => { if (current.length >= 2) polylines.push([current.slice(), closed]); };
    const CURVES = 'CcSsQqTt';
    for (const [cmd, a] of expandPath(d)) {
      if (!CURVES.includes(cmd)) last = null;
      switch (cmd) {
        case 'M': flush(false); current = []; cx = mx = a[0]; cy = my = a[1]; ap(cx, cy); break;
        case 'm': flush(false); current = []; cx = cx + a[0]; cy = cy + a[1]; mx = cx; my = cy; ap(cx, cy); break;
        case 'L': cx = a[0]; cy = a[1]; ap(cx, cy); break;
        case 'l': cx += a[0]; cy += a[1]; ap(cx, cy); break;
        case 'H': cx = a[0]; ap(cx, cy); break;
        case 'h': cx += a[0]; ap(cx, cy); break;
        case 'V': cy = a[0]; ap(cx, cy); break;
        case 'v': cy += a[0]; ap(cx, cy); break;
        case 'C': bez([cx, cy], [a[0], a[1]], [a[2], a[3]], [a[4], a[5]]); last = [a[2], a[3]]; cx = a[4]; cy = a[5]; break;
        case 'c': {
          const p1 = [cx + a[0], cy + a[1]], p2 = [cx + a[2], cy + a[3]], p3 = [cx + a[4], cy + a[5]];
          bez([cx, cy], p1, p2, p3); last = p2; [cx, cy] = p3; break;
        }
        case 'S': {
          const [lx, ly] = last || [cx, cy];
          bez([cx, cy], [2 * cx - lx, 2 * cy - ly], [a[0], a[1]], [a[2], a[3]]); last = [a[0], a[1]]; cx = a[2]; cy = a[3]; break;
        }
        case 's': {
          const [lx, ly] = last || [cx, cy];
          const p2 = [cx + a[0], cy + a[1]], p3 = [cx + a[2], cy + a[3]];
          bez([cx, cy], [2 * cx - lx, 2 * cy - ly], p2, p3); last = p2; [cx, cy] = p3; break;
        }
        case 'Q': {
          const [qx, qy, x, y] = a;
          const p1 = [cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)], p2 = [x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)];
          bez([cx, cy], p1, p2, [x, y]); last = [qx, qy]; cx = x; cy = y; break;
        }
        case 'q': {
          const qx = cx + a[0], qy = cy + a[1], x = cx + a[2], y = cy + a[3];
          const p1 = [cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)], p2 = [x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)];
          bez([cx, cy], p1, p2, [x, y]); last = [qx, qy]; cx = x; cy = y; break;
        }
        case 'T': {
          const [x, y] = a; const [lx, ly] = last || [cx, cy];
          const qx = 2 * cx - lx, qy = 2 * cy - ly;
          const p1 = [cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)], p2 = [x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)];
          bez([cx, cy], p1, p2, [x, y]); last = [qx, qy]; cx = x; cy = y; break;
        }
        case 't': {
          const x = cx + a[0], y = cy + a[1]; const [lx, ly] = last || [cx, cy];
          const qx = 2 * cx - lx, qy = 2 * cy - ly;
          const p1 = [cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)], p2 = [x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)];
          bez([cx, cy], p1, p2, [x, y]); last = [qx, qy]; cx = x; cy = y; break;
        }
        case 'Z': case 'z': flush(true); current = [[mx, my]]; cx = mx; cy = my; break;
        case 'A': cx = a[5]; cy = a[6]; ap(cx, cy); break;
        case 'a': cx += a[5]; cy += a[6]; ap(cx, cy); break;
      }
    }
    flush(false);
    return polylines;
  }

  function offsetPoints(points, hw, closed) {
    const n = points.length;
    if (n < 2) return [[], []];
    const seg = [];
    for (let i = 0; i < n - 1; i++) seg.push(leftNormal(points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1]));
    if (closed) seg.push(leftNormal(points[0][0] - points[n - 1][0], points[0][1] - points[n - 1][1]));
    const left = [], right = [];
    for (let i = 0; i < n; i++) {
      let n1, n2;
      if (closed) { n1 = seg[mod(i - 1, n)]; n2 = seg[i % n]; }
      else if (i === 0) { n1 = n2 = seg[0]; }
      else if (i === n - 1) { n1 = n2 = seg[seg.length - 1]; }
      else { n1 = seg[i - 1]; n2 = seg[i]; }
      const [ox, oy] = miterOffset(n1, n2, hw);
      left.push([points[i][0] + ox, points[i][1] + oy]);
      right.push([points[i][0] - ox, points[i][1] - oy]);
    }
    return [left, right];
  }

  function strokeToOutline(d, width) {
    const hw = width / 2;
    const parts = [];
    for (const [points, closed] of sampleSegments(d)) {
      if (points.length < 2) continue;
      const [lp, rp] = offsetPoints(points, hw, closed);
      if (!lp.length) continue;
      let out = `M ${F(...lp[0])}`;
      for (const p of lp.slice(1)) out += ` L ${F(...p)}`;
      if (closed) {
        out += ' Z';
        out += ` M ${F(...rp[rp.length - 1])}`;
        for (const p of rp.slice(0, -1).reverse()) out += ` L ${F(...p)}`;
        out += ' Z';
      } else {
        out += ` L ${F(...rp[rp.length - 1])}`;
        for (const p of rp.slice(0, -1).reverse()) out += ` L ${F(...p)}`;
        out += ' Z';
      }
      parts.push(out);
    }
    return parts.length ? parts.join(' ') : d;
  }

  // ── Tree walk ─────────────────────────────────────────────────────────

  const SHAPE_TAGS = new Set(['path', 'rect', 'circle', 'ellipse', 'polygon', 'polyline', 'line']);
  const SKIP_TAGS = new Set(['defs', 'clipPath', 'mask', 'symbol', 'pattern', 'linearGradient', 'radialGradient', 'filter', 'style', 'script']);

  function isBackgroundRect(el, vx, vy, vw, vh) {
    if (tagOf(el) !== 'rect') return false;
    let x, y, w, h;
    try { x = pyFloat(attr(el, 'x', 0)); y = pyFloat(attr(el, 'y', 0)); w = pyFloat(attr(el, 'width', 0)); h = pyFloat(attr(el, 'height', 0)); }
    catch (e) { if (e instanceof ConvertError) return false; throw e; }
    const tol = 0.02;
    return Math.abs(x - vx) <= vw * tol && Math.abs(y - vy) <= vh * tol && Math.abs(w - vw) <= vw * tol && Math.abs(h - vh) <= vh * tol;
  }

  const ident = (x, y) => [x, y];
  function collect(el, accXfm, inhFill, gradients, vb, out) {
    if (SKIP_TAGS.has(tagOf(el))) return out;
    const xfm = chain(accXfm, parseTransform(attr(el, 'transform', '')));
    const [fill, stroke, sw] = resolveFillStroke(el, gradients, inhFill);
    if (SHAPE_TAGS.has(tagOf(el)) && !(vb && isBackgroundRect(el, ...vb))) {
      let d = elementToD(el);
      if (d) d = normalizeArcs(d);
      if (d) {
        if (fill !== null) out.push([d, xfm || ident, fill]);
        if (stroke && sw > 0) out.push([strokeToOutline(d, sw), xfm || ident, stroke]);
        else if (stroke && fill === null) out.push([d, xfm || ident, stroke]);
      }
    }
    for (const c of kids(el)) collect(c, xfm, fill, gradients, vb, out);
    return out;
  }

  // ── Clipboard geometry (slides_clip.py) ───────────────────────────────

  function pathToClipGeometry(d, xfm, vx, vy, vw, vh) {
    const cw = COORD;
    const ch = vw ? pyRound(COORD * vh / vw) : COORD;
    const sc = precise
      ? (x, y) => {
        const [tx, ty] = xfm(x, y);
        const a = (tx - vx) / vw * cw, b = (ty - vy) / vh * ch;
        if (!Number.isFinite(a) || !Number.isFinite(b)) fail('cannot convert float to integer');
        return [a, b];
      }
      : (x, y) => { const [tx, ty] = xfm(x, y); return [pyRound((tx - vx) / vw * cw), pyRound((ty - vy) / vh * ch)]; };
    const meta = [], coords = [];
    const emit = (op, pts) => {
      const n = 2 * pts.length;
      if (meta.length && meta[meta.length - 2] === op) meta[meta.length - 1] += n;
      else meta.push(op, n);
      for (const [x, y] of pts) coords.push(x, y);
    };
    let cx = 0, cy = 0, mx = 0, my = 0, last = null;
    const CURVES = 'CcSsQqTt';
    for (const [cmd, a] of expandPath(d)) {
      if (!CURVES.includes(cmd)) last = null;
      switch (cmd) {
        case 'M': cx = mx = a[0]; cy = my = a[1]; emit(OP_MOVE, [sc(cx, cy)]); break;
        case 'm': cx = mx = cx + a[0]; cy = my = cy + a[1]; emit(OP_MOVE, [sc(cx, cy)]); break;
        case 'L': cx = a[0]; cy = a[1]; emit(OP_LINE, [sc(cx, cy)]); break;
        case 'l': cx += a[0]; cy += a[1]; emit(OP_LINE, [sc(cx, cy)]); break;
        case 'H': cx = a[0]; emit(OP_LINE, [sc(cx, cy)]); break;
        case 'h': cx += a[0]; emit(OP_LINE, [sc(cx, cy)]); break;
        case 'V': cy = a[0]; emit(OP_LINE, [sc(cx, cy)]); break;
        case 'v': cy += a[0]; emit(OP_LINE, [sc(cx, cy)]); break;
        case 'C': { const [x1, y1, x2, y2, x, y] = a; emit(OP_CUBIC, [sc(x1, y1), sc(x2, y2), sc(x, y)]); last = [x2, y2]; cx = x; cy = y; break; }
        case 'c': {
          const ax1 = cx + a[0], ay1 = cy + a[1], ax2 = cx + a[2], ay2 = cy + a[3], ax = cx + a[4], ay = cy + a[5];
          emit(OP_CUBIC, [sc(ax1, ay1), sc(ax2, ay2), sc(ax, ay)]); last = [ax2, ay2]; cx = ax; cy = ay; break;
        }
        case 'S': {
          const [x2, y2, x, y] = a; const [lx, ly] = last || [cx, cy];
          const x1 = 2 * cx - lx, y1 = 2 * cy - ly;
          emit(OP_CUBIC, [sc(x1, y1), sc(x2, y2), sc(x, y)]); last = [x2, y2]; cx = x; cy = y; break;
        }
        case 's': {
          const x2 = cx + a[0], y2 = cy + a[1], x = cx + a[2], y = cy + a[3]; const [lx, ly] = last || [cx, cy];
          const x1 = 2 * cx - lx, y1 = 2 * cy - ly;
          emit(OP_CUBIC, [sc(x1, y1), sc(x2, y2), sc(x, y)]); last = [x2, y2]; cx = x; cy = y; break;
        }
        case 'Q': {
          const [qx, qy, x, y] = a;
          emit(OP_CUBIC, [sc(cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)), sc(x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)), sc(x, y)]);
          last = [qx, qy]; cx = x; cy = y; break;
        }
        case 'q': {
          const qx = cx + a[0], qy = cy + a[1], x = cx + a[2], y = cy + a[3];
          emit(OP_CUBIC, [sc(cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)), sc(x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)), sc(x, y)]);
          last = [qx, qy]; cx = x; cy = y; break;
        }
        case 'T': {
          const [x, y] = a; const [lx, ly] = last || [cx, cy];
          const qx = 2 * cx - lx, qy = 2 * cy - ly;
          emit(OP_CUBIC, [sc(cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)), sc(x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)), sc(x, y)]);
          last = [qx, qy]; cx = x; cy = y; break;
        }
        case 't': {
          const x = cx + a[0], y = cy + a[1]; const [lx, ly] = last || [cx, cy];
          const qx = 2 * cx - lx, qy = 2 * cy - ly;
          emit(OP_CUBIC, [sc(cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy)), sc(x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y)), sc(x, y)]);
          last = [qx, qy]; cx = x; cy = y; break;
        }
        case 'Z': case 'z': meta.push(OP_CLOSE, 0); cx = mx; cy = my; break;
      }
    }
    return [meta, coords];
  }

  function endpointBbox(meta, coords) {
    const xs = [], ys = [];
    let idx = 0;
    for (let m = 0; m < meta.length; m += 2) {
      const op = meta[m], count = meta[m + 1], n = Math.floor(count / 2);
      if (op === OP_CLOSE) continue;
      if (op === OP_MOVE || op === OP_LINE) {
        for (let i = 0; i < n; i++) { xs.push(coords[idx + 2 * i]); ys.push(coords[idx + 2 * i + 1]); }
      } else if (op === OP_CUBIC) {
        for (let i = 0; i < n; i += 3) { xs.push(coords[idx + 2 * (i + 2)]); ys.push(coords[idx + 2 * (i + 2) + 1]); }
      }
      idx += count;
    }
    return [xs, ys];
  }

  function dropClosingDuplicates(meta, coords) {
    const runs = [];
    for (let i = 0; i < meta.length; i += 2) runs.push([meta[i], meta[i + 1]]);
    const starts = [];
    let at = 0;
    for (const [, cnt] of runs) { starts.push(at); at += cnt; }
    const drop = new Set();
    let subStart = null;
    runs.forEach(([op], k) => {
      if (op === OP_MOVE) subStart = [coords[starts[k]], coords[starts[k] + 1]];
      else if (op === OP_CLOSE && k > 0 && subStart !== null) {
        const [pop, pcnt] = runs[k - 1];
        if (pop === OP_LINE && pcnt >= 2) {
          const j = starts[k - 1] + pcnt - 2;
          if (coords[j] === subStart[0] && coords[j + 1] === subStart[1]) { drop.add(j); drop.add(j + 1); runs[k - 1][1] -= 2; }
        }
      }
    });
    if (!drop.size) return [meta, coords];
    const outC = coords.filter((_, i) => !drop.has(i));
    const outM = [];
    for (const [op, cnt] of runs) { if (op === OP_LINE && cnt === 0) continue; outM.push(op, cnt); }
    return [outM, outC];
  }

  function anchorCount(meta) {
    let n = 0;
    for (let i = 0; i < meta.length; i += 2) {
      const op = meta[i], count = meta[i + 1];
      if (op === OP_MOVE || op === OP_LINE) n += Math.floor(count / 2);
      else if (op === OP_CUBIC) n += Math.floor(count / 6);
    }
    return n;
  }
  function shapeType(meta) {
    if (!EDITABLE_POINTS) return TYPE_CUSTOM;
    const ops = meta.filter((_, i) => i % 2 === 0);
    if (ops.filter((o) => o === OP_MOVE).length > 1) return TYPE_CUSTOM;
    if (ops.some((o) => o !== OP_MOVE && o !== OP_LINE && o !== OP_CLOSE)) return TYPE_CUSTOM;
    if (EDITABLE_MAX_ANCHORS !== null && anchorCount(meta) > EDITABLE_MAX_ANCHORS) return TYPE_CUSTOM;
    return TYPE_POLYLINE;
  }

  let newId = () => {
    const b = crypto.getRandomValues(new Uint8Array(5));
    return 'ga' + [...b].map((x) => x.toString(16).padStart(2, '0')).join('');
  };

  function shapeEntry(id, meta, coords, w, h, x, y, fill) {
    const type = shapeType(meta);
    if (type === TYPE_POLYLINE) [meta, coords] = dropClosingDuplicates(meta, coords);
    return [3, id, type, [1, 0, 0, 1, x, y], [8, w, 9, h, 12, [[1, 1, meta, coords, [], 0]], 14, 1, 15, '#' + fill, 18, 0, 23, 0]];
  }

  // Precise (the default): each shape's points are kept at full resolution
  // in a frame of its own (LOCAL units across its larger side) and the
  // shape's transform scales that frame down to its size on the slide.
  // Slides keeps a pasted shape's points as given and resizes through the
  // transform (checked live: a 40-unit circle came back as 40-unit integer
  // points; the same circle sent as a 100000-unit frame scaled 0.0004 came
  // back at 100000 units), so points baked at the dropped size were all
  // the detail a shape ever had, and a small drop scaled up showed lumps
  // and corners. The legacy layout (points baked at the dropped size, as
  // slides_clip.py does) stays for the parity check.
  const LOCAL = 100000;
  let precise = true;
  function placeSvgGroupPrecise(shapes, vb, ox, oy, sw, sh) {
    const [vx, vy, vw, vh] = vb;
    const cw = COORD;
    const ch = vw ? pyRound(COORD * vh / vw) : COORD;
    if (ch === 0) fail('division by zero');
    const resolved = [], childIds = [];
    for (const [d, xfm, fillHex] of shapes) {
      const [meta, coords] = pathToClipGeometry(d, xfm, vx, vy, vw, vh);
      const [xs, ys] = endpointBbox(meta, coords);
      if (!xs.length) continue;
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      for (const v of xs) { if (v < x0) x0 = v; if (v > x1) x1 = v; }
      for (const v of ys) { if (v < y0) y0 = v; if (v > y1) y1 = v; }
      const pw = x1 - x0, ph = y1 - y0;
      // Size on the slide in units (never under one unit, like the legacy
      // layout) and where it sits.
      const ux = sw / cw / EMU_PER_UNIT, uy = sh / ch / EMU_PER_UNIT; // units per COORD
      const wU = Math.max(pw * ux, 1), hU = Math.max(ph * uy, 1);
      const xU = Math.round((ox + (x0 / cw) * sw) / EMU_PER_UNIT);
      const yU = Math.round((oy + (y0 / ch) * sh) / EMU_PER_UNIT);
      // One scale for both axes, rounded to 4 decimals because Slides keeps
      // only 4 (a 0.047625 came back 0.0476): the frame is then sized to
      // fit that scale exactly, so nothing drifts.
      const scale = Math.max(1e-4, Math.round(Math.max(wU, hU) / LOCAL * 1e4) / 1e4);
      const kx = (wU / Math.max(pw, 1e-12)) / scale, ky = (hU / Math.max(ph, 1e-12)) / scale;
      const local = coords.map((v, i) => Math.round(i % 2 === 0 ? (v - x0) * kx : (v - y0) * ky));
      const lw = Math.max(Math.round(wU / scale), 1), lh = Math.max(Math.round(hU / scale), 1);
      const fill = typeof fillHex === 'object' ? fillHex.stops[0][1] : fillHex;
      const id = newId();
      childIds.push(id);
      const entry = shapeEntry(id, meta, local, lw, lh, xU, yU, fill);
      entry[3][0] = scale;
      entry[3][3] = scale;
      resolved.push(entry);
    }
    if (childIds.length > 1) resolved.push([2, newId(), childIds, [1, 0, 0, 1, 0, 0]]);
    return resolved;
  }

  function placeSvgGroup(shapes, vb, ox, oy, sw, sh) {
    if (precise) return placeSvgGroupPrecise(shapes, vb, ox, oy, sw, sh);
    const [vx, vy, vw, vh] = vb;
    const cw = COORD;
    const ch = vw ? pyRound(COORD * vh / vw) : COORD;
    const resolved = [], childIds = [];
    for (const [d, xfm, fillHex] of shapes) {
      let [meta, coords] = pathToClipGeometry(d, xfm, vx, vy, vw, vh);
      const [xs, ys] = endpointBbox(meta, coords);
      if (!xs.length) continue;
      let pxMin = Infinity, pyMin = Infinity, pxMax = -Infinity, pyMax = -Infinity;
      for (const v of xs) { if (v < pxMin) pxMin = v; if (v > pxMax) pxMax = v; }
      for (const v of ys) { if (v < pyMin) pyMin = v; if (v > pyMax) pyMax = v; }
      const pw = Math.max(pxMax - pxMin, 1), ph = Math.max(pyMax - pyMin, 1);
      coords = coords.map((v, i) => v - (i % 2 === 0 ? pxMin : pyMin));
      if (ch === 0) fail('division by zero');
      const shapeOx = ox + pyRound(pxMin / cw * sw);
      const shapeOy = oy + pyRound(pyMin / ch * sh);
      const shapeSw = Math.max(pyRound(pw / cw * sw), 1);
      const shapeSh = Math.max(pyRound(ph / ch * sh), 1);
      const fill = typeof fillHex === 'object' ? fillHex.stops[0][1] : fillHex;
      const scaleX = (shapeSw / EMU_PER_UNIT) / pw;
      const scaleY = (shapeSh / EMU_PER_UNIT) / ph;
      const finalCoords = coords.map((v, i) => pyRound(v * (i % 2 === 0 ? scaleX : scaleY)));
      const finalW = Math.max(pyRound(shapeSw / EMU_PER_UNIT), 1);
      const finalH = Math.max(pyRound(shapeSh / EMU_PER_UNIT), 1);
      const id = newId();
      childIds.push(id);
      resolved.push(shapeEntry(id, meta, finalCoords, finalW, finalH, pyRound(shapeOx / EMU_PER_UNIT), pyRound(shapeOy / EMU_PER_UNIT), fill));
    }
    if (childIds.length > 1) resolved.push([2, newId(), childIds, [1, 0, 0, 1, 0, 0]]);
    return resolved;
  }

  function addShapesToClipAt(groups, xEmu, yEmu, boxW, boxH) {
    const n = groups.length;
    const resolved = [];
    if (n === 1) {
      const [vb, shapes] = groups[0];
      const aspect = vb[3] ? vb[2] / vb[3] : 1;
      let sw, sh;
      if (aspect >= boxW / boxH) { sw = boxW; sh = pyRound(sw / aspect); }
      else { sh = boxH; sw = pyRound(sh * aspect); }
      resolved.push(...placeSvgGroup(shapes, vb, xEmu - Math.floor(sw / 2), yEmu - Math.floor(sh / 2), sw, sh));
      return resolved;
    }
    const overallW = boxW * GRID_SCALE, overallH = boxH * GRID_SCALE;
    const cols = Math.ceil(Math.sqrt(n));
    const rows = Math.ceil(n / cols);
    const cellW = overallW / cols, cellH = overallH / rows;
    const left = xEmu - overallW / 2, top = yEmu - overallH / 2;
    groups.forEach(([vb, shapes], i) => {
      const row = Math.floor(i / cols), col = i % cols;
      const ccx = left + col * cellW + cellW / 2, ccy = top + row * cellH + cellH / 2;
      const slotW = cellW * (1 - GRID_GUTTER), slotH = cellH * (1 - GRID_GUTTER);
      const aspect = vb[3] ? vb[2] / vb[3] : 1;
      let sw, sh;
      if (aspect >= slotW / slotH) { sw = slotW; sh = sw / aspect; }
      else { sh = slotH; sw = sh * aspect; }
      sw = pyRound(sw); sh = pyRound(sh);
      resolved.push(...placeSvgGroup(shapes, vb, pyRound(ccx - sw / 2), pyRound(ccy - sh / 2), sw, sh));
    });
    return resolved;
  }

  // ── Parsing ───────────────────────────────────────────────────────────

  function decode(bytes) {
    const head = new TextDecoder('latin1').decode(bytes.slice(0, 200));
    const m = /^\s*<\?xml[^>]*encoding\s*=\s*["']([^"']+)["']/.exec(head);
    try { return new TextDecoder(m ? m[1] : 'utf-8').decode(bytes); } catch { return new TextDecoder('utf-8').decode(bytes); }
  }

  function parseSvg(source) {
    const text = typeof source === 'string' ? source : decode(source);
    const doc = new DOMParser().parseFromString(text, 'image/svg+xml');
    const err = doc.getElementsByTagName('parsererror')[0];
    if (err) {
      const why = ((err.querySelector('div') || err).textContent || '').trim().split('\n')[0];
      fail("This SVG isn't valid XML" + (why ? ': ' + why : ''));
    }
    const root = doc.documentElement;
    const parts = attr(root, 'viewBox', '0 0 100 100').trim().split(/\s+/);
    if (parts.length !== 4) fail('viewBox needs four numbers');
    const vb = parts.map(pyFloat);
    const gradients = extractGradients(root);
    return [vb, collect(root, null, '000000', gradients, vb, [])];
  }

  // JSON the way Python's json.dumps(..., separators=(',', ':')) writes it
  // (non-ASCII escaped).
  const pyJson = (v) => JSON.stringify(v).replace(/[\u007f-\uffff]/g, (c) => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0'));

  function wrap(resolved) {
    return { [MIME]: pyJson({ data: pyJson({ resolved }) }) };
  }

  // sources: [svg text or bytes, ...]. Same as slides_clip.build_clip_bundle_at.
  // opts.legacy: points baked at the dropped size, exactly as
  // slides_clip.py (for tools/convert-parity).
  function buildClipBundleAt(sources, xPt, yPt, boxWPt, boxHPt, opts = {}) {
    precise = !opts.legacy;
    const xEmu = pyRound(xPt * PT_TO_EMU), yEmu = pyRound(yPt * PT_TO_EMU);
    const boxW = Math.max(pyRound(boxWPt * PT_TO_EMU), 1), boxH = Math.max(pyRound(boxHPt * PT_TO_EMU), 1);
    return wrap(addShapesToClipAt(sources.map(parseSvg), xEmu, yEmu, boxW, boxH));
  }

  // files: File objects; placement: { x_pt, y_pt, box_w_pt, box_h_pt }.
  async function convertFiles(files, placement) {
    const sources = await Promise.all(files.map(async (f) => new Uint8Array(await f.arrayBuffer())));
    return buildClipBundleAt(sources, placement.x_pt, placement.y_pt, placement.box_w_pt, placement.box_h_pt);
  }

  self.SVG2S_CONVERT = {
    buildClipBundleAt, convertFiles, ConvertError,
    // For tests.
    _setIdSource: (fn) => { newId = fn; },
    _internals: { arcToCubics, pyRound, pyRoundN, pyFloat, expandPath, normalizeArcs, strokeToOutline, parseColor },
  };
})();
