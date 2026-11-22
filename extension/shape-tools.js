// Loaded after svg-editor.js — see manifest.json. Uses SB (slides-bridge.js),
// GEO (geo-ops.js), FONTKIT (fontkit.js), SVG2S_EDIT (svg-editor.js) and
// writeClipBundleLogged / isMac from content.js.
//
// Shape tools (1.3): one rail docked at the left edge of the slide canvas,
// in the same spot as the Edit Shape editor's rail, which takes its place
// while you edit points. It has
//   - Edit Shape             → opens the point editor (svg-editor.js)
//   - Group / Ungroup        → Slides' own ⌘⌥G / ⇧⌘⌥G (synthetic keys work,
//                              verified live Nov 19, 2026)
//   - Union, Subtract, Intersect, Exclude
//   - Outline stroke, Outline text
//   - Layers: the current slide's objects, top to bottom. Click to select,
//     drag to restack, double-click to rename, eye to hide while you work.
//
// Geometry comes from what Slides draws (every object is plain SVG under
// g#editor-<id>, in page units after the page CTM), so presets, lines,
// WordArt and our own shapes all work the same way. Results go back with
// the same delete + synthetic paste the editor uses on Done, into the
// stacking slot of the bottom-most original. Nothing here needs a Google
// API, a server or a new permission.
//
// Text outlines need the font's glyphs. Google Fonts families come from
// fonts.googleapis.com / fonts.gstatic.com (public, CORS-open). Fonts that
// aren't on Google Fonts (Arial, Verdana…) come from the computer itself
// through the Local Font Access API (Chrome asks once), with metric-matched
// stand-ins (Arimo, Tinos, Cousine, Carlito, Caladea) if that's declined.

console.log('[svg2slides] shape-tools.js loaded');

(() => {
  if (typeof SB === 'undefined' || typeof GEO === 'undefined') {
    console.warn('[svg2slides] shape tools: missing SB or GEO');
    return;
  }

  const ACCENT = '#0b57d0';
  const FONT = "'Google Sans', Roboto, Arial, sans-serif";
  const GM = {
    surface: '#f0f4f9', icon: '#444746', hover: 'rgba(68,71,70,.08)', selected: '#d3e3fd',
    tonal: '#c2e7ff', onTonal: '#004a77', tooltip: '#303030', onTooltip: '#f2f2f2', outline: '#c4c7c5',
    elev1: '0 1px 2px rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15)',
    elev2: '0 1px 2px rgba(60,64,67,.3), 0 2px 6px 2px rgba(60,64,67,.15)',
  };
  const SVGNS = 'http://www.w3.org/2000/svg';
  const IS_MAC = /Mac|iPhone|iPad/.test(navigator.platform || '');
  const MOD = IS_MAC ? '⌘' : 'Ctrl+';
  const ALT = IS_MAC ? '⌥' : 'Alt+';
  const SHIFT = IS_MAC ? '⇧' : 'Shift+';
  const sleep = SB.sleep;

  // Slides enforces Trusted Types: DOM calls only, never innerHTML.
  function el(tag, attrs = {}, ...kids) {
    const e = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => { if (v != null) e.setAttribute(k, v); });
    kids.forEach((c) => e.append(c));
    return e;
  }
  function sv(tag, attrs = {}) {
    const e = document.createElementNS(SVGNS, tag);
    Object.entries(attrs).forEach(([k, v]) => { if (v != null) e.setAttribute(k, v); });
    return e;
  }
  const clone = (o) => JSON.parse(JSON.stringify(o));

  // ── Selection ───────────────────────────────────────────────────────────
  function topIdsOf(resolved) {
    if (!resolved) return [];
    const kids = new Set();
    resolved.forEach((e) => { if (e[0] === 2) (e[2] || []).forEach((k) => kids.add(k)); });
    return resolved.filter((e) => (e[0] === 2 || e[0] === 3) && !kids.has(e[1])).map((e) => e[1]);
  }
  function entryById(resolved, id) {
    return resolved.find((e) => (e[0] === 2 || e[0] === 3) && e[1] === id) || null;
  }
  // Bottom → top, by Slides' paint order.
  function zSort(ids, order) {
    return ids.slice().sort((a, b) => order.indexOf(a) - order.indexOf(b));
  }
  function childOrder(groupId) {
    const g = SB.elementFor(groupId);
    if (!g) return [];
    return [...g.querySelectorAll('g[id^="editor-"]')]
      .filter((c) => c.parentNode.closest('g[id^="editor-"]') === g && !/-bg$|-paragraph/.test(c.id))
      .map((c) => c.id.slice('editor-'.length));
  }

  function keyCombo(key, code, keyCode, mods) {
    const tb = SB.textbox();
    if (!tb) return false;
    const o = Object.assign({ key, code, keyCode, which: keyCode, bubbles: true, cancelable: true }, mods);
    tb.dispatchEvent(new KeyboardEvent('keydown', o));
    tb.dispatchEvent(new KeyboardEvent('keyup', o));
    if (key !== 'Tab' && key !== 'Escape') SB.tick(); // Tab only moves the selection
    return true;
  }
  const PRIMARY = IS_MAC ? { metaKey: true } : { ctrlKey: true };

  // Selecting an object from script: a synthetic click on a visible part of
  // it is fastest (Slides hit-tests untrusted mouse events normally). If
  // nothing of it is visible, Tab steps through the slide's objects in
  // stacking order until it is the selection (verified live).
  function visiblePoint(id) {
    const g = SB.elementFor(id);
    if (!g) return null;
    const r = g.getBoundingClientRect();
    const vis = SB.visibleWorkspaceRect();
    const inside = (x, y) => x > vis.left + 2 && x < vis.right - 2 && y > vis.top + 2 && y < vis.bottom - 2;
    // Fast: the middle of each drawn part (a word of text, a path).
    for (const part of [...g.querySelectorAll('text, path, image')].slice(0, 24)) {
      const pr = part.getBoundingClientRect();
      if (pr.width < 1 && pr.height < 1) continue;
      const x = pr.left + pr.width / 2, y = pr.top + pr.height / 2;
      if (!inside(x, y)) continue;
      const t = document.elementFromPoint(x, y);
      if (t && g.contains(t)) return { x, y, t };
    }
    for (let n = 3; n <= 12; n += 3) {
      for (let gy = 1; gy < n; gy++) {
        for (let gx = 1; gx < n; gx++) {
          const x = r.left + (r.width * gx) / n, y = r.top + (r.height * gy) / n;
          if (x < vis.left + 2 || x > vis.right - 2 || y < vis.top + 2 || y > vis.bottom - 2) continue;
          const t = document.elementFromPoint(x, y);
          if (t && g.contains(t)) return { x, y, t };
        }
      }
    }
    return null;
  }
  function clickAt(p, shift) {
    const o = { bubbles: true, cancelable: true, composed: true, clientX: p.x, clientY: p.y, button: 0, buttons: 1, shiftKey: !!shift, view: window, detail: 1 };
    p.t.dispatchEvent(new PointerEvent('pointerdown', o));
    p.t.dispatchEvent(new MouseEvent('mousedown', o));
    o.buttons = 0;
    p.t.dispatchEvent(new PointerEvent('pointerup', o));
    p.t.dispatchEvent(new MouseEvent('mouseup', o));
    p.t.dispatchEvent(new MouseEvent('click', o));
  }
  const sameSet = (a, b) => a.length === b.length && a.every((x) => b.includes(x));
  // A click on a text box's text selects it and puts the cursor in it in
  // one go; a copy then carries no objects, so the selection reads as
  // empty and a shift-click row in Layers would start from nothing. One
  // Escape leaves the text and keeps the box selected (checked live).
  async function outOfText() {
    if (SB.readSelection()) return true;
    SB.pressKey('Escape');
    await sleep(70);
    return !!SB.readSelection();
  }

  // An object inside a group (or groups): Slides selects the outermost
  // group on the first click and one level further in on each click after,
  // so click where it shows until it alone is selected (checked live).
  async function deepSelect(id, add, at) {
    const now = () => topIdsOf(SB.readSelection());
    if (!add && sameSet(now(), [id])) return true;
    const p = at || visiblePoint(id);
    if (!p) return false;
    const depth = ancestorsOf(id).length;
    if (add) {
      clickAt(p, true);
      await sleep(60);
      await outOfText();
      return now().includes(id);
    }
    // Start from nothing selected, so the clicks count from the outside.
    SB.focusTextbox();
    SB.pressKey('Escape'); await sleep(30);
    SB.pressKey('Escape'); await sleep(30);
    for (let i = 0; i <= depth + 1; i++) {
      clickAt(p, false);
      await sleep(70);
      if (sameSet(now(), [id])) break;
    }
    if (!sameSet(now(), [id])) await outOfText();
    if (!renaming) SB.focusTextbox();
    return sameSet(now(), [id]);
  }
  async function selectIds(ids) {
    if (!ids.length) return false;
    const want = ids.slice();
    const now = () => topIdsOf(SB.readSelection());
    await outOfText();
    const cur = now();
    if (sameSet(cur, want)) return true;
    const inner = want.filter((id) => ancestorsOf(id).length);
    if (inner.length) {
      // Inside groups: the first one fresh, the rest added.
      const first = want.length === 1 || !cur.length ? want[0] : null;
      if (first && !(await deepSelect(first, false))) return false;
      for (const id of want) if (id !== first && !now().includes(id)) await deepSelect(id, true);
      return sameSet(now(), want);
    }
    // A click on an object that is already selected puts a text cursor in
    // it (every Slides shape takes text), so never click a selected one:
    // keep what's already right and shift-click only what's missing.
    const wantSet = new Set(want);
    const extra = cur.some((id) => !wantSet.has(id));
    let rest;
    if (!extra && cur.length) {
      rest = want.filter((id) => !cur.includes(id));
    } else {
      // Start fresh from an object that isn't selected yet; if every one
      // of them is, clear the selection first.
      let first = want.find((id) => !cur.includes(id));
      if (!first) {
        SB.focusTextbox();
        SB.pressKey('Escape'); await sleep(40); // out of text, if in it
        SB.pressKey('Escape'); await sleep(40); // nothing selected
        first = want[0];
      }
      const p = visiblePoint(first);
      if (p) { clickAt(p, false); await sleep(60); await outOfText(); }
      if (!sameSet(now(), [first])) {
        // Nothing of it to click: Tab through the slide's objects, out of
        // sight under the frozen copy.
        const found = await frozenWhile(null, async () => {
          SB.focusTextbox();
          const n = SB.topLevelOrder().length + 2;
          // Leave text editing / group drill-in first, or Tab would type a tab.
          SB.pressKey('Escape'); await sleep(40);
          SB.pressKey('Escape'); await sleep(40);
          for (let i = 0; i < n && !sameSet(now(), [first]); i++) {
            keyCombo('Tab', 'Tab', 9, {});
            await sleep(45);
          }
          return sameSet(now(), [first]);
        });
        if (!found) return false;
      }
      rest = want.filter((id) => id !== first);
    }
    // The rest: shift-click where they show.
    for (const id of rest) {
      const q = visiblePoint(id);
      if (!q) continue;
      clickAt(q, true);
      await sleep(60);
      await outOfText();
    }
    if (!renaming) SB.focusTextbox();
    return sameSet(now(), want);
  }

  // ── Geometry from the rendering ─────────────────────────────────────────
  function pageInv() {
    const c = SB.pageCTM();
    return c ? SB.matInv(c) : null;
  }
  function toPage(node, inv) {
    const c = node.getScreenCTM();
    return c ? SB.matMul(inv, [c.a, c.b, c.c, c.d, c.e, c.f]) : null;
  }
  // parseRenderedD segments → node model, mapped through M.
  function segsToSubs(segs, M) {
    const ap = (x, y) => SB.apply(M, x, y);
    return segs.map((sp) => {
      const s = { closed: false, nodes: [] };
      for (const seg of sp) {
        if (seg[0] === 'M') { const p = ap(seg[1], seg[2]); s.nodes.push({ x: p.x, y: p.y, in: null, out: null }); }
        else if (seg[0] === 'L') { const p = ap(seg[1], seg[2]); s.nodes.push({ x: p.x, y: p.y, in: null, out: null }); }
        else if (seg[0] === 'C') {
          const c1 = ap(seg[1], seg[2]), c2 = ap(seg[3], seg[4]), p = ap(seg[5], seg[6]);
          if (s.nodes.length) s.nodes[s.nodes.length - 1].out = c1;
          s.nodes.push({ x: p.x, y: p.y, in: c2, out: null });
        } else if (seg[0] === 'Z') {
          s.closed = true;
          const n = s.nodes;
          if (n.length > 1 && Math.abs(n[0].x - n[n.length - 1].x) < 0.5 && Math.abs(n[0].y - n[n.length - 1].y) < 0.5) {
            const last = n.pop();
            n[0].in = last.in;
          }
        }
      }
      return s;
    }).filter((s) => s.nodes.length > 1);
  }

  let _ctx = null;
  function hex(c) {
    if (!c || c === 'none' || /^url\(/.test(c)) return null;
    if (/^#[0-9a-f]{6}$/i.test(c)) return c.toLowerCase();
    if (!_ctx) _ctx = document.createElement('canvas').getContext('2d');
    _ctx.fillStyle = '#000';
    _ctx.fillStyle = c;
    const v = _ctx.fillStyle;
    return /^#[0-9a-f]{6}$/i.test(v) ? v.toLowerCase() : null;
  }

  const SELECTION_BLUE = /^#8ab4f8$/i;
  // Every drawable path of one object, in page units, with its paint.
  // Text glyphs and hit areas are left out.
  function objectPaths(id, inv) {
    const g = SB.elementFor(id);
    if (!g) return null;
    if (g.querySelector('image, foreignObject, video, canvas')) return null;
    const out = [];
    for (const p of g.querySelectorAll('path')) {
      if (p.closest('[class*="text"], g[id*="-paragraph"]')) continue;
      const cs = getComputedStyle(p);
      if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      const op = parseFloat(cs.opacity);
      const fill = hex(cs.fill), stroke = hex(cs.stroke);
      const sw = parseFloat(cs.strokeWidth) || 0;
      const hasFill = !!fill && parseFloat(cs.fillOpacity) !== 0 && op !== 0;
      const hasStroke = !!stroke && !SELECTION_BLUE.test(stroke) && parseFloat(cs.strokeOpacity) !== 0 && op !== 0 && sw > 0;
      if (!hasFill && !hasStroke) continue;
      const segs = SB.parseRenderedD(p.getAttribute('d'));
      const M = segs && toPage(p, inv);
      if (!M) return null;
      const scale = Math.sqrt(Math.abs(M[0] * M[3] - M[1] * M[2])) || 1;
      const dash = cs.strokeDasharray && cs.strokeDasharray !== 'none'
        ? cs.strokeDasharray.split(/[ ,]+/).map(parseFloat).filter((v) => v >= 0).map((v) => v * scale) : null;
      out.push({
        el: p, subs: segsToSubs(segs, M), fill, stroke, hasFill, hasStroke,
        sw: sw * scale, cap: cs.strokeLinecap || 'butt', join: cs.strokeLinejoin || 'miter',
        miter: parseFloat(cs.strokeMiterlimit) || 4, dash: dash && dash.some((v) => v > 0) ? dash : null,
        dashOffset: (parseFloat(cs.strokeDashoffset) || 0) * scale,
        fillRule: cs.fillRule === 'evenodd' ? 'evenodd' : 'nonzero',
      });
    }
    return out;
  }

  // includeHidden: the editor hides the objects it is editing, text and all.
  function textElements(id, includeHidden) {
    const g = SB.elementFor(id);
    if (!g) return [];
    return [...g.querySelectorAll('text')].filter((t) => (t.textContent || '').trim() && (includeHidden || getComputedStyle(t).visibility !== 'hidden'));
  }
  const hasRenderedText = (id, includeHidden) => textElements(id, includeHidden).length > 0;

  function strokeOf(p) {
    return GEO.outlineStroke(p.subs, p.sw, {
      cap: p.cap, join: p.join === 'arcs' || p.join === 'miter-clip' ? 'miter' : p.join,
      miterLimit: p.miter, dashes: p.dash, dashOffset: p.dashOffset,
    }).subs;
  }

  // ── Fonts → glyph outlines ──────────────────────────────────────────────
  // Families Google Fonts doesn't serve, and their metric-compatible
  // stand-ins (same widths, so line breaks and layout hold).
  const SYSTEM = {
    'arial': 'Arimo', 'helvetica': 'Arimo', 'helvetica neue': 'Arimo', 'arial black': null,
    'times new roman': 'Tinos', 'times': 'Tinos', 'courier new': 'Cousine', 'courier': 'Cousine',
    'calibri': 'Carlito', 'cambria': 'Caladea', 'georgia': 'Gelasio', 'verdana': null, 'tahoma': null,
    'trebuchet ms': null, 'comic sans ms': null, 'impact': null, 'garamond': 'EB Garamond',
    'palatino': null, 'palatino linotype': null, 'century gothic': null, 'segoe ui': null,
  };
  const fontCache = new Map();
  const notes = new Set();

  function parseFaces(css) {
    const faces = [];
    const re = /@font-face\s*{([^}]*)}/g;
    let m;
    while ((m = re.exec(css))) {
      const body = m[1];
      const url = (body.match(/url\((['"]?)(https:[^)'"]+)\1\)/) || [])[2];
      if (!url) continue;
      const ranges = [];
      const ur = (body.match(/unicode-range:\s*([^;]+)/) || [])[1];
      if (ur) {
        ur.split(',').forEach((part) => {
          const s = part.trim().replace(/^U\+/i, '');
          if (s.includes('-')) { const [a, b] = s.split('-'); ranges.push([parseInt(a, 16), parseInt(b, 16)]); }
          else if (s.includes('?')) ranges.push([parseInt(s.replace(/\?/g, '0'), 16), parseInt(s.replace(/\?/g, 'F'), 16)]);
          else { const v = parseInt(s, 16); ranges.push([v, v]); }
        });
      }
      // What the face really is, so a bold or italic the family lacks can be drawn the way Chrome draws it.
      const fw = (body.match(/font-weight:\s*([^;]+)/) || [])[1];
      const wts = fw ? fw.trim().split(/\s+/).map((v) => (v === 'bold' ? 700 : v === 'normal' ? 400 : parseInt(v, 10))).filter((v) => v > 0) : [400];
      const fs = ((body.match(/font-style:\s*([^;]+)/) || [])[1] || 'normal').trim();
      faces.push({ url, ranges: ranges.length ? ranges : [[0, 0x10ffff]], font: null,
        wMin: Math.min(...(wts.length ? wts : [400])), wMax: Math.max(...(wts.length ? wts : [400])), italic: /italic|oblique/.test(fs) });
    }
    return faces;
  }

  async function googleFaces(family, weight, italic) {
    const fam = family.trim().replace(/\s+/g, '+');
    const tries = [
      `https://fonts.googleapis.com/css2?family=${fam}:ital,wght@${italic ? 1 : 0},${weight}`,
      `https://fonts.googleapis.com/css2?family=${fam}:wght@${weight}`,
      `https://fonts.googleapis.com/css2?family=${fam}`,
    ];
    for (const url of tries) {
      try {
        const r = await fetch(url, { credentials: 'omit' });
        if (!r.ok) continue;
        const faces = parseFaces(await r.text());
        if (faces.length) return faces;
      } catch (err) {
        console.warn('[svg2slides] Google Fonts request failed', err);
        return null;
      }
    }
    return null;
  }

  const WEIGHT_WORDS = [[100, /thin|hairline/], [200, /extra ?light|ultra ?light/], [300, /light/], [500, /medium/],
    [600, /semi ?bold|demi ?bold/], [800, /extra ?bold|ultra ?bold/], [900, /black|heavy/], [700, /bold/]];
  function styleWeight(style) {
    const s = (style || '').toLowerCase();
    for (const [w, re] of WEIGHT_WORDS) if (re.test(s)) return w;
    return 400;
  }

  async function localFaces(family, weight, italic) {
    if (typeof window.queryLocalFonts !== 'function') return null;
    try {
      const all = await window.queryLocalFonts();
      const fam = family.toLowerCase();
      const cands = all.filter((f) => (f.family || '').toLowerCase() === fam);
      if (!cands.length) return null;
      const score = (f) => {
        const st = (f.style || '').toLowerCase();
        const it = /italic|oblique/.test(st);
        return Math.abs(styleWeight(st) - weight) + (it === italic ? 0 : 1000);
      };
      cands.sort((a, b) => score(a) - score(b));
      const pick = cands[0];
      const bytes = new Uint8Array(await (await pick.blob()).arrayBuffer());
      let font = FONTKIT.create(bytes);
      if (font && font.fonts) font = font.fonts.find((f) => f.postscriptName === pick.postscriptName) || font.fonts[0];
      const pw = styleWeight(pick.style);
      return [{ url: 'local:' + pick.postscriptName, ranges: [[0, 0x10ffff]], font, wMin: pw, wMax: pw, italic: /italic|oblique/i.test(pick.style || '') }];
    } catch (err) {
      console.warn('[svg2slides] local font access unavailable', err);
      return null;
    }
  }

  // Resolve family → list of faces (each with unicode ranges), cached.
  function facesFor(family, weight, italic) {
    const key = family.toLowerCase() + '|' + weight + '|' + (italic ? 'i' : 'n');
    if (!fontCache.has(key)) {
      fontCache.set(key, (async () => {
        const lc = family.toLowerCase();
        const isSystem = Object.prototype.hasOwnProperty.call(SYSTEM, lc);
        let faces = null;
        if (!isSystem) faces = await googleFaces(family, weight, italic);
        if (!faces) faces = await localFaces(family, weight, italic);
        if (!faces && isSystem && SYSTEM[lc]) {
          faces = await googleFaces(SYSTEM[lc], weight, italic);
          if (faces) notes.add(`${family} isn't downloadable, so its outlines use ${SYSTEM[lc]} (same letter widths)`);
        }
        if (!faces && !isSystem) faces = await localFaces(family, weight, italic);
        if (!faces) throw userError(`Couldn't get the ${family} font. Allow font access when Chrome asks, or use a Google font.`);
        return faces;
      })());
      fontCache.get(key).catch(() => fontCache.delete(key));
    }
    return fontCache.get(key);
  }

  // The B button asks for weight 700 whether or not the family has a bold.
  // When it hasn't, Chrome fattens the regular letters itself; the same for
  // italic, which it slants. Outlines have to match what is on the slide, so
  // do what Chrome does (Skia): bold grows the outline by 1/32 of the font
  // size at 36 px and up, 1/24 at 9 px and down, and in between by size;
  // italic leans the letters by a quarter.
  function synthFor(face, weight, italic) {
    const has = face.wMax === undefined ? weight : face.wMax;
    return { bold: weight >= 600 && has < 600, italic: !!italic && face.italic === false };
  }
  function fakeBoldEm(sizePx) {
    const k = sizePx <= 9 ? 1 / 24 : sizePx >= 36 ? 1 / 32 : 1 / 24 + (1 / 32 - 1 / 24) * (sizePx - 9) / 27;
    return k / 2;                       // outward growth, as a share of the em
  }
  const boldCache = new WeakMap();      // font → Map(glyph id | growth → subs in font units)
  function glyphSubs(font, glyph, growEm) {
    const base = () => GEO.glyphToSubs(glyph.path.commands, [1, 0, 0, 1, 0, 0]);
    if (!growEm) return base();
    let m = boldCache.get(font);
    if (!m) boldCache.set(font, (m = new Map()));
    const key = glyph.id + '|' + Math.round(growEm * 1e5);
    if (!m.has(key)) {
      let subs = base();
      try {
        const r = GEO.offsetSubs(GEO.unionAll(subs), growEm * font.unitsPerEm, { join: 'round' });
        if (r && !r.empty && r.subs.length) subs = r.subs;
      } catch (err) { /* keep the regular outline */ }
      m.set(key, subs);
    }
    return m.get(key);
  }
  const mapSubs = (subs, m) => subs.map((sp) => ({ closed: sp.closed, nodes: sp.nodes.map((n) => {
    const ap = (q) => (q ? { x: m[0] * q.x + m[2] * q.y + m[4], y: m[1] * q.x + m[3] * q.y + m[5] } : null);
    const p = ap(n);
    return { x: p.x, y: p.y, in: ap(n.in), out: ap(n.out) };
  }) }));

  async function glyphFor(faces, cp) {
    for (const f of faces) {
      if (!f.ranges.some(([a, b]) => cp >= a && cp <= b)) continue;
      if (!f.font) {
        const r = await fetch(f.url, { credentials: 'omit' });
        if (!r.ok) continue;
        f.font = FONTKIT.create(new Uint8Array(await r.arrayBuffer()));
      }
      if (f.font.hasGlyphForCodePoint && !f.font.hasGlyphForCodePoint(cp)) continue;
      return { font: f.font, glyph: f.font.glyphForCodePoint(cp), face: f };
    }
    return null;
  }

  function firstFamily(ff) {
    return (ff || '').split(',')[0].trim().replace(/^["']|["']$/g, '') || 'Arial';
  }
  // Slides loads its Google fonts under its own names: "docs-Nunito",
  // "docs-Amatic SC" (seen live, Nov 19 2026). Some menus also fold the
  // weight into the name ("Roboto Light"). Back to Google Fonts terms.
  const WEIGHT_SUFFIX = [[/\s+(Thin|Hairline)$/i, 100], [/\s+(ExtraLight|Extra Light|UltraLight)$/i, 200], [/\s+Light$/i, 300],
    [/\s+Medium$/i, 500], [/\s+(SemiBold|Semi Bold|DemiBold)$/i, 600], [/\s+(ExtraBold|Extra Bold|UltraBold)$/i, 800],
    [/\s+(Black|Heavy)$/i, 900], [/\s+Bold$/i, 700]];
  function fontRequest(familyCss, weight) {
    let family = firstFamily(familyCss).replace(/^docs-/i, '').trim();
    let w = weight;
    for (const [re, ww] of WEIGHT_SUFFIX) {
      if (re.test(family)) { family = family.replace(re, ''); if (w === 400) w = ww; break; }
    }
    return { family, weight: w };
  }

  // Outline every rendered text run of one object. Returns
  // [{ fill, subs }] grouped by colour, in page units.
  async function textOutlines(id, inv, includeHidden) {
    const byFill = new Map();
    for (const t of textElements(id, includeHidden)) {
      const cs = getComputedStyle(t);
      const { family, weight } = fontRequest(cs.fontFamily, parseInt(cs.fontWeight, 10) || 400);
      const italic = /italic|oblique/.test(cs.fontStyle);
      const size = parseFloat(cs.fontSize) || 16;
      const fill = hex(cs.fill) || '#000000';
      const Mt = toPage(t, inv);
      if (!Mt) continue;
      const faces = await facesFor(family, weight, italic);
      const str = t.textContent;
      const n = t.getNumberOfChars();
      for (let i = 0; i < n && i < str.length; i++) {
        const cp = str.codePointAt(i);
        if (cp > 0xffff) i++; // the low surrogate has no position of its own
        if (/\s/.test(String.fromCodePoint(cp))) continue;
        let pos;
        try { pos = t.getStartPositionOfChar(cp > 0xffff ? i - 1 : i); } catch { continue; }
        const g = await glyphFor(faces, cp);
        if (!g || !g.glyph || !g.glyph.path) continue;
        const s = size / g.font.unitsPerEm;
        const syn = synthFor(g.face, weight, italic);
        if (syn.bold) notes.add(`${family} has no bold of its own, so the bold is drawn the way Chrome draws it`);
        const m = SB.matMul(Mt, [s, 0, syn.italic ? 0.25 * s : 0, -s, pos.x, pos.y]);
        const subs = mapSubs(glyphSubs(g.font, g.glyph, syn.bold ? fakeBoldEm(size) : 0), m);
        if (!subs.length) continue;
        if (!byFill.has(fill)) byFill.set(fill, []);
        byFill.get(fill).push(...subs);
      }
    }
    return [...byFill].map(([fill, subs]) => ({ fill, subs: GEO.unionAll(subs) }));
  }

  // True when `id` sits in a group on the slide that the copied selection
  // doesn't include (the user drilled into a group and picked a child).
  function pickedFromGroup(resolved, id) {
    const g = SB.elementFor(id);
    const page = SB.currentPageGroup();
    const parent = g && g.parentNode && g.parentNode.closest ? g.parentNode.closest('g[id^="editor-"]') : null;
    if (!parent || parent === page) return false;
    return !entryById(resolved, parent.id.slice('editor-'.length));
  }

  // ── Payload building ────────────────────────────────────────────────────
  // subs in page units → type 1 custom shape at the top level (or under a
  // parent whose page transform inverse is `parentInv`).
  function shapeEntry(subs, paint, parentInv) {
    const s = clone(subs).filter((sp) => sp.nodes.length > 1);
    if (!s.length) return null;
    const norm = SB.normalizeSubs(s);
    const { meta, coords } = SB.encodePath(s);
    const props = [8, norm.w, 9, norm.h, 12, [[1, 1, meta, coords, [], 0]],
      14, paint.fill ? 1 : 0, 15, paint.fill || '#eeeeee'];
    if (paint.stroke && paint.sw > 0) props.push(18, 1, 19, paint.stroke, 22, Math.max(1, Math.round(paint.sw)));
    else props.push(18, 0, 23, 0);
    const T = SB.matMul(parentInv || [1, 0, 0, 1, 0, 0], [1, 0, 0, 1, Math.round(norm.dx), Math.round(norm.dy)]);
    return [3, SB.newId(), 1, T, props];
  }
  const areaOfEntry = (e) => (SB.getProp(e[4], 8) || 0) * (SB.getProp(e[4], 9) || 0);

  // Replace shape entries in a copied selection: fn(entry) → { shapes,
  // keepText } or null (leave as is). Several shapes become a group; groups
  // in the selection keep their place; text follows the largest new shape
  // unless dropped. Mirrors SB.convertSelection.
  async function rebuild(resolved, fn) {
    const replaced = new Map();
    const srcOf = {};
    for (const e of resolved) {
      if (e[0] !== 3) continue;
      const parentToPage = SB.matMul(SB.localToPage(resolved, e), SB.matInv(e[3]) || [1, 0, 0, 1, 0, 0]);
      const parentInv = SB.matInv(parentToPage) || [1, 0, 0, 1, 0, 0];
      const r = await fn(e, parentInv);
      if (!r || !r.shapes.length) continue;
      const shapes = r.shapes;
      const carrier = shapes.reduce((a, b) => (areaOfEntry(b) > areaOfEntry(a) ? b : a))[1];
      const group = shapes.length > 1 ? [2, SB.newId(), shapes.map((s) => s[1]), [1, 0, 0, 1, 0, 0]] : null;
      shapes.forEach((s) => { srcOf[s[1]] = e[1]; });
      if (group) srcOf[group[1]] = e[1];
      replaced.set(e[1], { id: group ? group[1] : shapes[0][1], carrier, shapes, group, keepText: !!r.keepText });
    }
    if (!replaced.size) return null;
    const out = [];
    for (const e of resolved) {
      const r = typeof e[1] === 'string' ? replaced.get(e[1]) : null;
      if (e[0] === 3 && r) {
        out.push(...r.shapes);
        if (r.group) out.push(r.group);
      } else if (e[0] === 2) {
        const c = clone(e);
        c[2] = (c[2] || []).map((id) => (replaced.has(id) ? replaced.get(id).id : id));
        out.push(c);
      } else if (r) {
        if (!r.keepText && (e[0] === 15 || e[0] === 17)) continue;
        const c = clone(e);
        c[1] = r.carrier;
        out.push(c);
      } else {
        out.push(e);
      }
    }
    return { resolved: out, srcOf };
  }

  // ── Replace on the slide ────────────────────────────────────────────────
  // Same mechanism as the editor's Done: copy the result to the OS clipboard
  // while still inside the click (fallback), delete the selection, paste the
  // result, then put each unit back in its original stacking slot.
  // ── Freeze the canvas while we work ────────────────────────────────────
  // A replace is delete, paste and Arrange presses, which Slides draws one
  // by one. A still copy of the slide sits over the canvas meanwhile (with
  // moved objects already in their new place), so the slide changes once.
  // Light DOM, ids stripped; below our toolbar.
  let frozen = null;
  // Pictures in the copy have to load before it can be shown; shown at once
  // they're blank for a frame or two, and the slide flickers (seen on
  // aligning photos). The copy goes in hidden, and shows when its pictures
  // have loaded (they're in the browser's cache: a few ms; at most 250).
  function freeze(moves) {
    if (frozen) { frozen.n++; return frozen.ready; }
    const page = SB.currentPageGroup();
    const svg = page && page.ownerSVGElement;
    if (!svg) return Promise.resolve();
    const moving = !!(moves && moves.size);
    // The slide, and Slides' selection layer over it (a sibling SVG in
    // #workspace) unless objects are about to move out from under it.
    const r0 = svg.getBoundingClientRect();
    const sources = [svg];
    if (!moving) {
      const ws = document.getElementById('workspace');
      (ws ? [...ws.querySelectorAll(':scope > svg')] : []).forEach((o) => {
        const ro = o.getBoundingClientRect();
        if (o !== svg && Math.abs(ro.width - r0.width) < 2 && Math.abs(ro.height - r0.height) < 2) sources.push(o);
      });
    }
    const clones = sources.map((src) => {
      const r = src.getBoundingClientRect();
      const clone = src.cloneNode(true);
      if (moving && src === svg) {
        clone.querySelectorAll('g[id^="editor-"]').forEach((g) => {
          const d = moves.get(g.id.slice('editor-'.length));
          if (d) g.setAttribute('transform', `translate(${d.x} ${d.y}) ` + (g.getAttribute('transform') || ''));
        });
      }
      clone.querySelectorAll('[id]').forEach((n) => {
        if (!n.id.startsWith('editor-')) return;
        const own = n.id.slice('editor-'.length);
        if ([...hidden.keys()].some((h) => own === h || own.startsWith(h + '-'))) n.style.setProperty('visibility', 'hidden', 'important');
        n.removeAttribute('id');
      });
      clone.removeAttribute('id');
      clone.style.cssText = `position:absolute;left:${r.left}px;top:${r.top}px;width:${r.width}px;height:${r.height}px;margin:0;`;
      return clone;
    });
    const v = SB.visibleWorkspaceRect();
    let bg = '#f9fbfd';
    for (let n = document.getElementById('workspace-container'); n && n.nodeType === 1; n = n.parentElement) {
      const c = getComputedStyle(n).backgroundColor;
      if (c && c !== 'transparent' && !/rgba\(.*,\s*0\)$/.test(c)) { bg = c; break; }
    }
    const layer = document.createElement('div');
    layer.id = 'svg2slides-freeze';
    layer.style.cssText = `position:fixed;inset:0;z-index:2;pointer-events:none;background:${bg};` +
      `clip-path:inset(${v.top}px ${Math.max(0, innerWidth - v.right)}px ${Math.max(0, innerHeight - v.bottom)}px ${v.left}px);`;
    layer.append(...clones);
    const pics = [...layer.querySelectorAll('image')];
    if (pics.length) layer.style.visibility = 'hidden';
    document.documentElement.insertBefore(layer, host || null);
    const f = { layer, bar: null, n: 1, ready: null };
    frozen = f;
    f.ready = (async () => {
      if (pics.length) {
        await Promise.race([
          Promise.all(pics.map((im) => new Promise((res) => {
            im.addEventListener('load', res, { once: true });
            im.addEventListener('error', res, { once: true });
          }))),
          sleep(250),
        ]);
        await new Promise((r) => requestAnimationFrame(r));
        layer.style.visibility = '';
      }
      if (frozen === f) f.bar = freezeToolbar();
    })();
    return f.ready;
  }
  async function thaw() {
    if (!frozen || --frozen.n > 0) return;
    const f = frozen;
    frozen = null;
    // Let Slides draw the final state first.
    await sleep(60);
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    // Pictures Slides has just redrawn: wait for them too, so the copy
    // doesn't come off over a blank one.
    const page = SB.currentPageGroup();
    const pics = page ? [...page.querySelectorAll('image')] : [];
    if (pics.length) {
      await Promise.race([Promise.all(pics.map((im) => {
        const url = im.getAttribute('href') || im.getAttribute('xlink:href');
        if (!url) return null;
        const pre = new Image();
        pre.src = url;
        return pre.decode().catch(() => null);
      })), sleep(250)]);
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    }
    f.layer.remove();
    if (f.bar) f.bar.remove();
  }
  // Slides' toolbar swaps its buttons with every selection change (shape,
  // nothing, shape again during a replace). A still copy of it sits on top
  // meanwhile. The copy goes inside #docs-toolbar-wrapper, after the real
  // buttons, so Slides' own CSS styles it and lookups by id still find the
  // real ones first.
  function freezeToolbar() {
    const wrap = document.getElementById('docs-toolbar-wrapper');
    if (!wrap || !wrap.offsetWidth) return null;
    let bg = '';
    for (let n = wrap; n && n.nodeType === 1; n = n.parentElement) {
      const c = getComputedStyle(n).backgroundColor;
      if (c && c !== 'transparent' && !/rgba\(.*,\s*0\)$/.test(c)) { bg = c; break; }
    }
    const cover = document.createElement('div');
    cover.className = 'svg2slides-bar-freeze';
    cover.setAttribute('aria-hidden', 'true');
    cover.style.cssText = `position:absolute;left:0;top:0;width:${wrap.offsetWidth}px;height:${wrap.offsetHeight}px;z-index:10;pointer-events:none;background:${bg || '#f9fbfd'};overflow:hidden;`;
    [...wrap.children].forEach((c) => {
      if (!c.offsetWidth || c.classList.contains('svg2slides-bar-freeze')) return;
      const k = c.cloneNode(true);
      k.style.position = 'absolute';
      k.style.left = c.offsetLeft + 'px';
      k.style.top = c.offsetTop + 'px';
      k.style.width = c.offsetWidth + 'px';
      k.style.height = c.offsetHeight + 'px';
      k.style.margin = '0';
      cover.append(k);
    });
    wrap.append(cover);
    return cover;
  }
  async function frozenWhile(moves, fn) {
    await freeze(moves);
    try { return await fn(); } finally { await thaw(); }
  }

  async function replaceSelection(original, resolved, opts = {}) {
    return frozenWhile(opts.moves, () => replaceSelectionNow(original, resolved, opts));
  }
  // gestureCopy: also put the result on the clipboard as a fallback. Off:
  // it replaces whatever the user had copied and moves focus around.
  async function replaceSelectionNow(original, resolved, { srcOf = {}, slotIndex = null, gestureCopy = false, reselect = true } = {}) {
    const E = self.SVG2S_EDIT;
    const oldTop = topIdsOf(original);
    const order0 = SB.topLevelOrder();
    let copied = false;
    if (gestureCopy && typeof writeClipBundleLogged === 'function') {
      try { copied = writeClipBundleLogged({ [SB.MIME]: SB.wrap(resolved) }); } catch { copied = false; }
    }
    const oldUnits = E.payloadUnits(original).map((u) => {
      const top = SB.topLevelIdOf(u.id) || u.id;
      return Object.assign(u, { slot: { top, exact: top === u.id, index: order0.indexOf(top) } });
    });
    const slotFor = (nu) => {
      if (slotIndex !== null) return { top: null, exact: true, index: slotIndex };
      for (const nid of nu.ids) {
        const oid = srcOf[nid] || nid;
        const u = oldUnits.find((x) => x.ids.has(oid));
        if (u) return u.slot;
      }
      return null;
    };
    touched = true;
    // Pictures (images, masked images) only come back if the paste looks
    // like a real copy of them: take one of the originals before they go.
    const named = (list) => list.some((e) => e[0] === 3 && typeof SB.getProp(e[4], 49) === 'string');
    const clip = !SB.hasClip() && named(resolved) ? SB.readClip() : null;
    if (!(await E.deleteSelected(oldTop))) {
      toast(copied ? `Couldn't replace the shapes. Delete them, then press ${MOD}V.` : "Couldn't replace the shapes.");
      return false;
    }
    const ok = clip ? await SB.withClip(clip, () => E.pasteInPlace(resolved, slotFor)) : await E.pasteInPlace(resolved, slotFor);
    SB.focusTextbox();
    // Each unit pastes on its own, so only the last stays selected. Select
    // them all again, as the selection was before.
    if (ok && reselect) {
      const before = new Set(order0);
      const made = SB.topLevelOrder().filter((id) => !before.has(id));
      if (made.length > 1) await selectIds(made);
    }
    if (!ok) {
      toast(copied ? `Press ${MOD}V to finish` : "Slides didn't accept the result. Press " + MOD + 'Z to undo.');
      return false;
    }
    return true;
  }

  // ── Operations ──────────────────────────────────────────────────────────
  let busy = false;
  let touched = false; // set once an operation starts changing the slide
  async function run(name, fn) {
    if (busy) return;
    if (self.SVG2S_EDIT && self.SVG2S_EDIT.isOpen()) return;
    busy = true;
    rail && rail.classList.add('busy');
    notes.clear();
    touched = false;
    SB.beginMacro(name);
    try {
      await fn();
    } catch (err) {
      console.error('[svg2slides] ' + name + ' failed', err);
      toast(err && err.userMessage ? err.userMessage
        : touched ? `Something went wrong. Press ${MOD}Z to put the slide back.` : 'Something went wrong. Nothing on the slide changed.');
    } finally {
      SB.endMacro();
      busy = false;
      rail && rail.classList.remove('busy');
      SB.focusTextbox();
      scheduleRefresh(150);
    }
  }
  const userError = (msg) => Object.assign(new Error(msg), { userMessage: msg });

  function requireSelection() {
    const sel = SB.readSelection();
    if (!sel || !topIdsOf(sel).length) throw userError('Select a shape first');
    return sel;
  }

  // The filled region an object covers, plus the paint to carry over.
  async function regionOf(id, inv) {
    const paths = objectPaths(id, inv);
    if (paths === null) throw userError("Images, video and charts can't be combined");
    const parts = [];
    let paint = null;
    for (const p of paths) {
      if (p.hasFill) parts.push({ subs: p.subs, fillRule: p.fillRule });
      else if (p.hasStroke) parts.push({ subs: strokeOf(p), fillRule: 'nonzero' });
      if (!paint) paint = p.hasFill ? { fill: p.fill, stroke: p.hasStroke ? p.stroke : null, sw: p.sw } : { fill: p.stroke, stroke: null, sw: 0 };
    }
    if (hasRenderedText(id)) {
      const runs = await textOutlines(id, inv);
      runs.forEach((r) => {
        parts.push({ subs: r.subs, fillRule: 'nonzero' });
        if (!paint) paint = { fill: r.fill, stroke: null, sw: 0 };
      });
    }
    const usable = parts.filter((p) => p.subs.length);
    if (!usable.length) return null;
    const subs = usable.length === 1 ? usable[0].subs : GEO.boolean('union', usable).subs;
    return { subs, fillRule: usable.length === 1 ? usable[0].fillRule : 'nonzero', paint };
  }

  const OP_LABEL = { union: 'Union', subtract: 'Subtract', intersect: 'Intersect', exclude: 'Exclude' };

  function booleanOp(op) {
    return run(op, async () => {
      const sel = requireSelection();
      const inv = pageInv();
      if (!inv) throw userError("Couldn't find the slide");
      let ids = topIdsOf(sel);
      const order = SB.topLevelOrder();
      let slotIndex;
      if (ids.length === 1 && entryById(sel, ids[0])[0] === 2) {
        // One group selected: combine its children, Figma-style.
        slotIndex = order.indexOf(ids[0]);
        ids = childOrder(ids[0]).filter((c) => entryById(sel, c));
      } else {
        ids = zSort(ids, order);
        slotIndex = Math.min(...ids.map((id) => order.indexOf(id)).filter((i) => i >= 0));
      }
      if (ids.length < 2) throw userError(`Select two or more shapes to ${OP_LABEL[op].toLowerCase()}`);
      const regions = [];
      for (const id of ids) {
        const r = await regionOf(id, inv);
        if (r) regions.push(r);
      }
      if (regions.length < 2) throw userError('Select two or more shapes with a fill or outline');
      const res = GEO.boolean(op, regions);
      if (res.empty) throw userError(op === 'intersect' ? "These shapes don't overlap" : 'Nothing would be left');
      const entry = shapeEntry(res.subs, regions[0].paint || { fill: '#9e9e9e' });
      if (!entry) throw userError('Nothing would be left');
      const ok = await replaceSelection(sel, [entry], { slotIndex: Number.isFinite(slotIndex) ? slotIndex : null });
      if (ok) toastNotes();
    });
  }

  function outlineStrokeOp() {
    return run('outline stroke', async () => {
      const sel = requireSelection();
      const inv = pageInv();
      if (!inv) throw userError("Couldn't find the slide");
      let any = false;
      const rebuilt = await rebuild(sel, async (e, parentInv) => {
        const paths = objectPaths(e[1], inv);
        if (!paths || !paths.some((p) => p.hasStroke)) return null;
        any = true;
        const shapes = [];
        for (const p of paths) {
          if (p.hasFill) {
            const s = shapeEntry(p.subs, { fill: p.fill }, parentInv);
            if (s) shapes.push(s);
          }
          if (p.hasStroke) {
            const s = shapeEntry(strokeOf(p), { fill: p.stroke }, parentInv);
            if (s) shapes.push(s);
          }
        }
        // A text-only frame keeps carrying its text; others keep it on the
        // largest new shape too.
        return { shapes, keepText: true };
      });
      if (!any || !rebuilt) throw userError('Nothing selected has an outline');
      await replaceSelection(sel, rebuilt.resolved, { srcOf: rebuilt.srcOf });
    });
  }

  function outlineTextOp() {
    return run('outline text', async () => {
      const sel = requireSelection();
      const inv = pageInv();
      if (!inv) throw userError("Couldn't find the slide");
      let any = false;
      const made = []; // { glyph entry, original object id }
      const rebuilt = await rebuild(sel, async (e, parentInv) => {
        if (!hasRenderedText(e[1])) return null;
        any = true;
        const runs = await textOutlines(e[1], inv);
        const glyphs = runs.map((r) => shapeEntry(r.subs, { fill: r.fill }, parentInv)).filter(Boolean);
        glyphs.forEach((g) => made.push({ g, from: e[1] }));
        const frame = (objectPaths(e[1], inv) || []).filter((p) => p.hasFill || p.hasStroke);
        const shapes = [];
        if (frame.length && !pickedFromGroup(sel, e[1])) {
          // Keep Slides' own shape (preset handles and all), minus its text.
          const keep = clone(e);
          keep[1] = SB.newId();
          shapes.push(keep);
        } else {
          // Picked from inside a group: its transform is relative to a group
          // that isn't in the copy, so rebuild the frame from the drawing.
          frame.forEach((p) => {
            const s = shapeEntry(p.subs, { fill: p.hasFill ? p.fill : null, stroke: p.hasStroke ? p.stroke : null, sw: p.sw }, parentInv);
            if (s) shapes.push(s);
          });
        }
        shapes.push(...glyphs);
        return { shapes, keepText: false };
      });
      if (!any || !rebuilt) throw userError('Nothing selected has text');
      // The kept frame's id changed, so its text entries (dropped above)
      // can't follow it back.
      const ok = await replaceSelection(sel, rebuilt.resolved, { srcOf: rebuilt.srcOf, gestureCopy: false });
      if (ok) {
        // So the text can come back later: the whole original object (font,
        // size, styles), and where the glyphs sat when it was outlined.
        const units = self.SVG2S_EDIT.payloadUnits(sel);
        made.forEach(({ g, from }) => {
          const unit = units.find((u) => u.ids.has(from));
          if (!unit) return;
          remember(SB.pathFingerprint(g), { kind: 'text', unit: unit.entries, box: entryBox(rebuilt.resolved, g), label: describeText(from) });
        });
        toastNotes();
      }
    });
  }
  function describeText(id) {
    return textElements(id, true).map((t) => t.textContent).join(' ').replace(/\s+/g, ' ').trim().slice(0, 60);
  }

  // Put outlined text back as live text, at the glyphs' current place and
  // size. Works as long as this computer did the outlining.
  function restoreTextOp() {
    return run('restore text', async () => {
      const sel = requireSelection();
      const hit = outlinedTextIn(sel);
      if (!hit) throw userError('This isn’t text outlined on this computer');
      const units = self.SVG2S_EDIT.payloadUnits(sel);
      const unit = units.find((u) => u.ids.has(hit.entry[1]));
      const b0 = hit.rec.box, b1 = entryBox(sel, hit.entry);
      const sx = (b1.maxX - b1.minX) / Math.max(1, b0.maxX - b0.minX), sy = (b1.maxY - b1.minY) / Math.max(1, b0.maxY - b0.minY);
      const D = SB.matMul([1, 0, 0, 1, b1.minX, b1.minY], SB.matMul([sx, 0, 0, sy, 0, 0], [1, 0, 0, 1, -b0.minX, -b0.minY]));
      const back = clone(hit.rec.unit);
      const kids = new Set();
      back.forEach((e) => { if (e[0] === 2) (e[2] || []).forEach((k) => kids.add(k)); });
      back.forEach((e) => { if ((e[0] === 2 || e[0] === 3) && !kids.has(e[1]) && Array.isArray(e[3])) e[3] = SB.matMul(D, e[3]); });
      const keep = sel.filter((e) => !(typeof e[1] === 'string' && unit && unit.ids.has(e[1])));
      const order = SB.topLevelOrder();
      const slot = unit ? order.indexOf(SB.topLevelIdOf(unit.id) || unit.id) : null;
      await replaceSelection(sel, keep.concat(back), { srcOf: {}, slotIndex: slot >= 0 ? slot : null, gestureCopy: false });
    });
  }

  // ── Stroke position (centre / inside / outside) ─────────────────────────
  // Slides only draws centred strokes, so inside and outside are drawn by
  // moving the outline: half the weight in for inside, out for outside. The
  // shape's own outline is remembered so the stroke can move back, change
  // weight, or open in Edit Shape as the original.
  function bakeAlign(e, resolved, align, weightPx) {
    const rec0 = recall(SB.pathFingerprint(e));
    const M = SB.localToPage(resolved, e);
    const Mi = SB.matInv(M);
    if (!Mi) return null;
    const recNow = SB.pathRecord(e);
    // Design outline in shape-local units (shifted so the current path's
    // box origin is where the remembered one was).
    let design = rec0 && rec0.kind === 'align' ? rec0.design : SB.decodePath(recNow[2], recNow[3]);
    if (!design) return null;
    const P = SB.paintFromProps(e[4]);
    const w = (weightPx !== undefined ? weightPx * 381 : P.weight);
    const toPg = (subs) => subs.map((sp) => ({ closed: sp.closed, nodes: sp.nodes.map((n) => ({ x: SB.apply(M, n.x, n.y).x, y: SB.apply(M, n.x, n.y).y, in: n.in ? SB.apply(M, n.in.x, n.in.y) : null, out: n.out ? SB.apply(M, n.out.x, n.out.y) : null })) }));
    const toLc = (subs) => subs.map((sp) => ({ closed: sp.closed, nodes: sp.nodes.map((n) => ({ x: SB.apply(Mi, n.x, n.y).x, y: SB.apply(Mi, n.x, n.y).y, in: n.in ? SB.apply(Mi, n.in.x, n.in.y) : null, out: n.out ? SB.apply(Mi, n.out.x, n.out.y) : null })) }));
    if (!design.every((sp) => sp.closed)) return null; // open lines have no inside
    let local = design;
    if (align !== 'center') {
      const res = GEO.offsetSubs(toPg(design), (align === 'inside' ? -1 : 1) * w / 2);
      if (res.empty) return null;
      local = toLc(res.subs);
    }
    const shifted = clone(local);
    const norm = SB.normalizeSubs(shifted);
    const designShifted = clone(design).map((sp) => ({ closed: sp.closed, nodes: sp.nodes.map((n) => ({ x: n.x - norm.dx, y: n.y - norm.dy, in: n.in ? { x: n.in.x - norm.dx, y: n.in.y - norm.dy } : null, out: n.out ? { x: n.out.x - norm.dx, y: n.out.y - norm.dy } : null })) }));
    const { meta, coords } = SB.encodePath(shifted);
    const m = e[3];
    const out = clone(e);
    out[3] = [m[0], m[1], m[2], m[3], m[4] + m[0] * norm.dx + m[2] * norm.dy, m[5] + m[1] * norm.dx + m[3] * norm.dy];
    const rec = clone(recNow);
    rec[2] = meta; rec[3] = coords;
    SB.setProp(out[4], 12, [rec]);
    SB.setProp(out[4], 8, norm.w);
    SB.setProp(out[4], 9, norm.h);
    if (weightPx !== undefined) SB.applyPaint(out[4], Object.assign({}, P, { strokeOn: weightPx > 0, weight: w }));
    out[2] = SB.typeFor(out[2], shifted);
    if (align !== 'center') remember(SB.pathFingerprint(out), { kind: 'align', align, design: designShifted });
    return out;
  }
  function strokeAlignOp(align) {
    return run('stroke position', async () => {
      const original = requireSelection();
      let sel = original, srcOf = {};
      // Slides' own shapes become custom shapes first (their outline is what moves).
      if (sel.some((e) => e[0] === 3 && !SB.isEditableShape(e) && SB.convertibleKind(sel, e))) {
        const conv = SB.convertSelection(sel);
        if (conv) { sel = conv.resolved; srcOf = conv.srcOf || {}; }
      }
      let n = 0;
      const out = sel.map((e) => {
        if (e[0] !== 3 || !SB.isEditableShape(e) || !SB.paintFromProps(e[4]).strokeOn) return e;
        const b = bakeAlign(e, sel, align);
        if (b) n++;
        return b || e;
      });
      if (!n) throw userError(align === 'center' ? 'Nothing selected has a moved stroke' : 'Select a closed shape with a stroke');
      await replaceSelection(original, out, { srcOf });
      rk.setIcon('strokeAlign', { center: 'strokeCenter', inside: 'strokeInside', outside: 'strokeOutside' }[align]);
    });
  }
  const alignOf = (e) => { const r = recall(SB.pathFingerprint(e)); return r && r.kind === 'align' ? r.align : 'center'; };

  // ── Align and distribute ────────────────────────────────────────────────
  // Ours, not Slides' Arrange › Align menu: two or more objects align to
  // their combined bounds, one object to the slide. The objects' own
  // transforms move and they go back in place.
  // Each selected object's frame, the way Slides aligns it: from the
  // copied data (size and transform), not the drawn pixels. A text box's
  // drawing is only its words, a callout's tail sticks out of its frame,
  // so pixel boxes put the preview off from where Slides then puts things
  // (seen live: 14 px on a callout).
  function unitBoxes(sel) {
    const inv = pageInv();
    let units = [];
    try { units = self.SVG2S_EDIT.payloadUnits(sel); } catch { units = []; }
    return topIdsOf(sel).map((id) => {
      const g = SB.elementFor(id);
      const r = g && g.getBoundingClientRect();
      const drawn = r && inv ? (() => { const p = SB.apply(inv, r.left, r.top), z = SB.apply(inv, r.right, r.bottom); return { minX: p.x, minY: p.y, maxX: z.x, maxY: z.y }; })() : null;
      const unit = units.find((u) => u.ids.has(id));
      const frames = unit ? unit.entries.filter((e) => e[0] === 3 && Array.isArray(e[3])) : [];
      if (frames.length) {
        const bs = frames.map((e) => frameBox(sel, e));
        const f = { minX: Math.min(...bs.map((b) => b.minX)), minY: Math.min(...bs.map((b) => b.minY)), maxX: Math.max(...bs.map((b) => b.maxX)), maxY: Math.max(...bs.map((b) => b.maxY)) };
        // Sanity check against the drawing: a stroke, a tail or a text box
        // wider than its words make them differ, but not by 4×.
        const near = (a, b) => { const m = 381 * 6; a = Math.max(a, m); b = Math.max(b, m); return a / b < 4 && b / a < 4; };
        const ok = !drawn || (near(f.maxX - f.minX, drawn.maxX - drawn.minX) && near(f.maxY - f.minY, drawn.maxY - drawn.minY));
        if (ok) return Object.assign({ id }, f);
      }
      return drawn ? Object.assign({ id }, drawn) : null;
    }).filter(Boolean);
  }
  // A shape's frame in page units: its own size (8/9) for our shapes; Slides'
  // own shapes and text boxes have none and scale a 120000-unit square
  // (measured live: a 94 × 125 px can is that square scaled 0.381 × 0.508).
  const NATIVE_FRAME = 120000;
  function frameBox(resolved, e) {
    const M = SB.localToPage(resolved, e);
    const w0 = SB.getProp(e[4], 8), h0 = SB.getProp(e[4], 9);
    const own = w0 != null || h0 != null; // a line can be 0 high
    const w = own ? (w0 || 0) : NATIVE_FRAME, h = own ? (h0 || 0) : NATIVE_FRAME;
    const pts = [[0, 0], [w, 0], [w, h], [0, h]].map(([x, y]) => SB.apply(M, x, y));
    const xs = pts.map((q) => q.x), ys = pts.map((q) => q.y);
    return { minX: Math.min(...xs), minY: Math.min(...ys), maxX: Math.max(...xs), maxY: Math.max(...ys) };
  }
  function pageBox() {
    const page = SB.currentPageGroup();
    const bg = page && [...page.querySelectorAll('g[id$="-bg"]')][0];
    const inv = pageInv();
    const r = bg && bg.getBoundingClientRect();
    if (!r || !inv) return null;
    const a = SB.apply(inv, r.left, r.top), z = SB.apply(inv, r.right, r.bottom);
    return { minX: a.x, minY: a.y, maxX: z.x, maxY: z.y };
  }
  function moveUnits(sel, deltas) {
    const out = clone(sel);
    const kids = new Set();
    out.forEach((e) => { if (e[0] === 2) (e[2] || []).forEach((k) => kids.add(k)); });
    out.forEach((e) => {
      const d = deltas.get(e[1]);
      if (!d || kids.has(e[1]) || !Array.isArray(e[3])) return;
      e[3][4] = Math.round(e[3][4] + d.x);
      e[3][5] = Math.round(e[3][5] + d.y);
    });
    return out;
  }
  function alignOp(act) {
    return run('align', async () => {
      const sel = requireSelection();
      const boxes = unitBoxes(sel);
      const ref = boxes.length >= 2
        ? { minX: Math.min(...boxes.map((b) => b.minX)), minY: Math.min(...boxes.map((b) => b.minY)), maxX: Math.max(...boxes.map((b) => b.maxX)), maxY: Math.max(...boxes.map((b) => b.maxY)) }
        : pageBox();
      if (!ref) throw userError("Couldn't find the slide");
      const deltas = new Map();
      boxes.forEach((b) => {
        let dx = 0, dy = 0;
        if (act === 'alignLeft') dx = ref.minX - b.minX;
        if (act === 'alignRight') dx = ref.maxX - b.maxX;
        if (act === 'alignHCenter') dx = (ref.minX + ref.maxX) / 2 - (b.minX + b.maxX) / 2;
        if (act === 'alignTop') dy = ref.minY - b.minY;
        if (act === 'alignBottom') dy = ref.maxY - b.maxY;
        if (act === 'alignVMiddle') dy = (ref.minY + ref.maxY) / 2 - (b.minY + b.maxY) / 2;
        if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) deltas.set(b.id, { x: dx, y: dy });
      });
      if (!deltas.size) return;
      // Slides' own Align (two or more) or Center on page (one, centre or
      // middle): one Slides step, nothing pasted, so images stay intact.
      // Its menus are made invisible while they're used.
      const native = boxes.length >= 2 ? ['Align', ALIGN_LABEL[act]]
        : act === 'alignHCenter' ? ['Center on page', 'Horizontally'] : act === 'alignVMiddle' ? ['Center on page', 'Vertically'] : null;
      if (native && await frozenWhile(deltas, () => slidesMenuPick(native[0], native[1], [...deltas.keys()]))) return;
      // One object to a slide edge: Slides has no command for that, so give
      // its Align something to align with for a moment (see alignToSlide).
      if (!native && boxes.length === 1 && await frozenWhile(deltas, () => alignToSlide(boxes[0].id, act))) return;
      if (hasImage(boxes.map((b) => b.id))) throw userError('Couldn’t align that image to the slide’s edge. Select something to align it with, or use centre or middle.');
      await replaceSelection(sel, moveUnits(sel, deltas), { srcOf: {}, moves: deltas });
    });
  }
  function distributeOp(axis) {
    return run('distribute', async () => {
      const sel = requireSelection();
      const boxes = unitBoxes(sel);
      if (boxes.length < 3) throw userError('Select three or more objects to distribute');
      const lo = axis === 'h' ? 'minX' : 'minY', hi = axis === 'h' ? 'maxX' : 'maxY';
      boxes.sort((a, b) => (a[lo] + a[hi]) - (b[lo] + b[hi]));
      const span = boxes[boxes.length - 1][hi] - boxes[0][lo];
      const total = boxes.reduce((t, b) => t + (b[hi] - b[lo]), 0);
      const gap = (span - total) / (boxes.length - 1);
      const deltas = new Map();
      let at = boxes[0][hi] + gap;
      boxes.slice(1, -1).forEach((b) => {
        const d = at - b[lo];
        if (Math.abs(d) > 0.5) deltas.set(b.id, axis === 'h' ? { x: d, y: 0 } : { x: 0, y: d });
        at += (b[hi] - b[lo]) + gap;
      });
      if (!deltas.size) return;
      if (await frozenWhile(deltas, () => slidesMenuPick('Distribute', axis === 'h' ? 'Horizontally' : 'Vertically', [...deltas.keys()]))) return;
      if (hasImage(boxes.map((b) => b.id))) throw userError('Couldn’t distribute these with Slides’ own Distribute, and images can’t be moved another way');
      await replaceSelection(sel, moveUnits(sel, deltas), { srcOf: {}, moves: deltas });
    });
  }
  // A single object to the slide's left, right, top or bottom edge. Slides'
  // Align needs two objects, and moving an image by pasting its data back
  // breaks the picture. So: paste a 1 px square with no fill and no line
  // at that corner of the slide, select it with the object, use Slides'
  // own Align, then delete the square. All under the frozen copy, as one
  // undo step; nothing extra stays on the slide.
  async function alignToSlide(id, act) {
    const pb = pageBox();
    if (!pb) return false;
    const U = 381; // 1 px
    const far = act === 'alignRight' || act === 'alignBottom';
    const x = Math.round(far ? pb.maxX - U : pb.minX), y = Math.round(far ? pb.maxY - U : pb.minY);
    const sq = [3, SB.newId(), 1, [1, 0, 0, 1, x, y], [8, U, 9, U, 12, [[1, 1, [0, 2, 1, 6, 5, 0], [0, 0, U, 0, U, U, 0, U], [], 0]], 14, 0, 15, '#FFFFFF', 18, 0, 23, 0]];
    const before = new Set(SB.topLevelOrder());
    SB.paste([sq]);
    const sel = await SB.waitForSelection((r) => { const t = topIdsOf(r); return t.length === 1 && !before.has(t[0]); });
    const anchor = sel && topIdsOf(sel)[0];
    if (!anchor) return false;
    let ok = false;
    try {
      if (!(await selectIds([anchor, id]))) return false;
      ok = await slidesMenuPick('Align', ALIGN_LABEL[act], [id]);
    } finally {
      // Take the square away again: the object off the selection, delete
      // what's left (only if it's just the square).
      const p = visiblePoint(id);
      if (p && topIdsOf(SB.readSelection()).includes(id)) { clickAt(p, true); await sleep(60); }
      if (!sameSet(topIdsOf(SB.readSelection()), [anchor])) await selectIds([anchor]);
      if (sameSet(topIdsOf(SB.readSelection()), [anchor])) { SB.pressKey('Delete'); await sleep(150); }
      if (SB.elementFor(anchor)) console.warn('[svg2slides] align helper square left on the slide:', anchor);
      await selectIds([id]);
    }
    return ok;
  }

  // ── Mask image with shape ───────────────────────────────────────────────
  // What Slides' own Mask image does, with any shape: a masked image is a
  // shape with the picture as its fill (checked live: masking an image as
  // an oval turned its entry into an oval, type 8, with the picture's blob
  // (49), an image-fill flag (86 = 1) and the picture's size in pixels (87
  // high, 88 wide)). A custom shape (type 1) with our own path and the same
  // props shows the picture inside the path, and it survives deleting the
  // original and reloading. Where the picture sits is 84/85 (offset) and
  // 79/80 (size) as fractions of the path's exact box, so the picture stays
  // exactly where it was, uncropped and unstretched.
  //
  // The picture of an object: its image fill props and where the whole
  // picture sits on the page (from the drawn <image>).
  function pictureOf(resolved, id) {
    const e = resolved && entryById(resolved, id);
    if (!e || e[0] !== 3) return null;
    const props = e[4];
    const blob = SB.getProp(props, 49);
    if (typeof blob !== 'string' || !blob) return null;
    const filled = SB.getProp(props, 86) === 1;
    const natW = filled ? SB.getProp(props, 88) : SB.getProp(props, 8);
    const natH = filled ? SB.getProp(props, 87) : SB.getProp(props, 9);
    return { entry: e, blob, natW, natH };
  }
  function pictureRectOnPage(id) {
    const g = SB.elementFor(id);
    const im = g && g.querySelector('image');
    const inv = pageInv();
    if (!im || !inv) return null;
    const M = toPage(im, inv);
    if (!M) return null;
    if (Math.abs(M[1]) > 1e-6 * Math.abs(M[0]) || Math.abs(M[2]) > 1e-6 * Math.abs(M[3])) return { rotated: true };
    const x = parseFloat(im.getAttribute('x')) || 0, y = parseFloat(im.getAttribute('y')) || 0;
    const w = parseFloat(im.getAttribute('width')) || 0, h = parseFloat(im.getAttribute('height')) || 0;
    const a = SB.apply(M, x, y), b = SB.apply(M, x + w, y + h);
    return { x: Math.min(a.x, b.x), y: Math.min(a.y, b.y), w: Math.abs(b.x - a.x), h: Math.abs(b.y - a.y) };
  }
  function maskOp() {
    return run('mask', async () => {
      const sel = requireSelection();
      const ids = topIdsOf(sel);
      if (ids.length !== 2) throw userError('Select an image and the shape to mask it with (two objects)');
      const order = SB.topLevelOrder();
      const [low, high] = zSort(ids, order);
      // The picture is the one with a picture; with two, the lower one
      // (the shape on top does the cutting, as in Illustrator and Figma).
      const picId = pictureOf(sel, low) ? low : pictureOf(sel, high) ? high : null;
      if (!picId) throw userError('Select an image and a shape to mask it with');
      const maskId = picId === low ? high : low;
      const pic = pictureOf(sel, picId);
      const rect = pictureRectOnPage(picId);
      if (!rect) throw userError('Couldn’t find where the picture is on the slide');
      if (rect.rotated) throw userError('Straighten the image first: masking a rotated image isn’t supported yet');
      const inv = pageInv();
      const paths = objectPaths(maskId, inv);
      if (!paths || !paths.length) {
        throw userError(hasRenderedText(maskId) ? 'Outline the text first (⌥⌘T), then mask with it' : 'The mask has to be a shape (the other object is an image too)');
      }
      const use = paths.some((p) => p.hasFill) ? paths.filter((p) => p.hasFill) : paths;
      const subs = use.flatMap((p) => p.subs).filter((sp) => sp.nodes.length >= 2);
      if (!subs.length) throw userError('That shape has nothing to mask with');
      // Page units, whole numbers, relative to the path's corner.
      const box0 = SB.subsBBox(subs);
      const ox = Math.round(box0.x), oy = Math.round(box0.y);
      const r = (v) => Math.round(v);
      const local = subs.map((sp) => ({ closed: true, nodes: sp.nodes.map((n) => ({
        x: r(n.x - ox), y: r(n.y - oy),
        in: n.in ? { x: r(n.in.x - ox), y: r(n.in.y - oy) } : null,
        out: n.out ? { x: r(n.out.x - ox), y: r(n.out.y - oy) } : null,
      })) }));
      const lb = SB.subsBBox(local);
      const box = { x: ox + lb.x, y: oy + lb.y, w: lb.w, h: lb.h };
      if (box.w < 1 || box.h < 1) throw userError('That shape is too thin to mask with');
      const { meta, coords } = SB.encodePath(local);
      const props = clone(pic.entry[4]);
      [8, 9, 12, 14, 79, 80, 84, 85, 86, 87, 88].forEach((k) => SB.removeProp(props, k));
      const fit = SB.imageFillProps(rect, box);
      SB.setProp(props, 8, Math.max(1, Math.round(lb.x + lb.w)));
      SB.setProp(props, 9, Math.max(1, Math.round(lb.y + lb.h)));
      SB.setProp(props, 12, [[1, 1, meta, coords, [], 0]]);
      SB.setProp(props, 86, 1);
      SB.setProp(props, 87, pic.natH);
      SB.setProp(props, 88, pic.natW);
      [84, 85, 79, 80].forEach((k) => SB.setProp(props, k, fit[k]));
      const id = SB.newId();
      const entry = [3, id, 1, [1, 0, 0, 1, ox, oy], props];
      // A copy of the picture alone: its wrapper and image clip let the
      // paste fetch the picture (see SB.withClip).
      let clip = null;
      if (await selectIds([picId])) clip = SB.readClip();
      if (!clip || !clip[Object.keys(clip).find((t) => /image-clip/.test(t))]) {
        await selectIds(ids);
        throw userError('Couldn’t get the picture from Slides to mask it. Try again, or copy and paste the image first.');
      }
      if (!(await selectIds(ids))) throw userError('Couldn’t select the image and the shape again');
      // In the image's place in the stack; both originals go.
      await SB.withClip(clip, () => replaceSelection(sel, [entry], { srcOf: { [id]: picId } }));
    });
  }

  // ── Adjust the picture under its mask ───────────────────────────────────
  // The same gesture as cropping an image in Slides: double-click (or the
  // Mask button) and the whole picture shows, faded where the mask hides
  // it. Drag the picture to slide it under the mask, drag a corner to
  // resize it (proportions kept), arrow keys nudge. ↵, ✓ or a click away
  // keeps the change; Esc or ✕ puts it back. The mask itself stays put.
  // A masked picture is a shape whose fill is the picture: 79/80 are the
  // picture's width and height and 84/85 its left and top, as fractions of
  // the path's own box, so only those four numbers change.
  let adjust = null;
  function maskedPicture(sel) {
    const ids = topIdsOf(sel);
    if (ids.length !== 1) return null;
    const e = entryById(sel, ids[0]);
    if (!e || e[0] !== 3) return null;
    const p = e[4];
    if (typeof SB.getProp(p, 49) !== 'string' || SB.getProp(p, 86) !== 1 || !SB.getProp(p, 12)) return null;
    return e;
  }
  const subsD = (subs) => subs.map((sp) => {
    let d = '';
    sp.nodes.forEach((n, i) => {
      if (!i) { d += `M${n.x} ${n.y}`; return; }
      const a = sp.nodes[i - 1];
      d += a.out || n.in ? `C${(a.out || a).x} ${(a.out || a).y} ${(n.in || n).x} ${(n.in || n).y} ${n.x} ${n.y}` : `L${n.x} ${n.y}`;
    });
    if (sp.closed && sp.nodes.length > 1) {
      const a = sp.nodes[sp.nodes.length - 1], n = sp.nodes[0];
      if (a.out || n.in) d += `C${(a.out || a).x} ${(a.out || a).y} ${(n.in || n).x} ${(n.in || n).y} ${n.x} ${n.y}`;
      d += 'Z';
    }
    return d;
  }).join('');
  async function adjustMask() {
    if (adjust || busy || (self.SVG2S_EDIT && self.SVG2S_EDIT.isOpen())) return;
    await outOfText();
    const sel = SB.readSelection();
    const e = maskedPicture(sel);
    if (!e) { toast('Select one masked image to adjust the picture under its mask'); return; }
    const id = e[1];
    if (ancestorsOf(id).length) { toast('Ungroup first: a masked image inside a group can’t be adjusted yet'); return; }
    const g = SB.elementFor(id);
    const im = g && g.querySelector('image');
    const href = im && (im.getAttribute('href') || im.getAttributeNS('http://www.w3.org/1999/xlink', 'href'));
    const path = SB.getProp(e[4], 12);
    let subs = null;
    try { subs = SB.decodePath(path[0][2], path[0][3]); } catch { subs = null; }
    if (!href || !subs || !subs.length || !SB.pageCTM()) { toast('Couldn’t read that picture to adjust it'); return; }
    const lb = SB.subsBBox(subs);
    const start = SB.pictureRect(e[4], lb);
    const rect = Object.assign({}, start);
    const NS = 'http://www.w3.org/2000/svg';
    const mk = (tag, attrs) => { const n = document.createElementNS(NS, tag); Object.entries(attrs || {}).forEach(([k, v]) => n.setAttribute(k, v)); return n; };
    const svg = mk('svg', { class: 'madj', tabindex: '-1' });
    const back = mk('rect', { x: 0, y: 0, width: '100%', height: '100%', fill: 'transparent' });
    const world = mk('g');
    const clipId = 'madj-clip-' + Date.now();
    const clip = mk('clipPath', { id: clipId });
    const d = subsD(subs);
    clip.append(mk('path', { d, 'clip-rule': 'evenodd' }));
    const ghost = mk('image', { href, preserveAspectRatio: 'none', opacity: '0.35', class: 'pic' });
    const inner = mk('g', { 'clip-path': `url(#${clipId})` });
    const full = mk('image', { href, preserveAspectRatio: 'none', class: 'pic' });
    inner.append(mk('path', { d, fill: '#fff', 'fill-rule': 'evenodd' }), full);
    const edge = mk('path', { d, class: 'edge' });
    const frame = mk('rect', { class: 'frame' });
    world.append(clip, ghost, inner, edge, frame);
    const handles = [0, 1, 2, 3].map((i) => mk('circle', { r: 5.5, class: 'h', 'data-h': i }));
    svg.append(back, world, ...handles);
    const pct = el('input', { type: 'number', min: '1', step: '1', 'aria-label': 'Picture size, percent of the size that just covers the mask' });
    const pbtn = (cls, tipText, key, dd) => {
      const b = el('button', { class: 'pb ' + cls, type: 'button', 'aria-label': tipText, 'data-tip': tipText, 'data-key': key });
      const ic = sv('svg', { viewBox: '0 0 20 20', 'aria-hidden': 'true' });
      ic.append(sv('path', { d: dd, fill: 'none', stroke: 'currentColor', 'stroke-width': '2.2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
      b.append(ic);
      return b;
    };
    const bFit = el('button', { class: 'tx', type: 'button', 'data-tip': 'Size the picture so it just covers the mask, centred' }, 'Fit');
    const bNo = pbtn('no', 'Cancel', 'Esc', 'M5.5 5.5l9 9M14.5 5.5l-9 9');
    const bOk = pbtn('ok', 'Keep', '↵', 'M4.5 10.5l3.6 3.6 7.4-8');
    const pill = el('div', { class: 'apill', role: 'group', 'aria-label': 'Picture under the mask' },
      el('span', { class: 'seg', 'data-tip': 'Picture size · 100% just covers the mask · ⌥-drag to scrub' }, el('span', { class: 'lb' }, 'Picture'), pct, el('span', { class: 'u' }, '%')),
      el('span', { class: 'seg' }, bFit), el('span', { class: 'seg' }, bNo, bOk));
    root.append(svg, pill);
    rk.attachTips(pill, 'above');
    const was = g.style.visibility;
    g.style.visibility = 'hidden';
    // The size at which the picture just covers the mask's box.
    const aspect = start.w / Math.max(start.h, 1e-9);
    const coverW = Math.max(lb.w, lb.h * aspect);
    const T = () => SB.matMul(SB.pageCTM(), e[3]);
    const paint = () => {
      const t = T();
      world.setAttribute('transform', `matrix(${t.join(' ')})`);
      [ghost, full].forEach((n) => { n.setAttribute('x', rect.x); n.setAttribute('y', rect.y); n.setAttribute('width', rect.w); n.setAttribute('height', rect.h); });
      frame.setAttribute('x', rect.x); frame.setAttribute('y', rect.y); frame.setAttribute('width', rect.w); frame.setAttribute('height', rect.h);
      const cs = [[rect.x, rect.y], [rect.x + rect.w, rect.y], [rect.x + rect.w, rect.y + rect.h], [rect.x, rect.y + rect.h]].map(([x, y]) => SB.apply(t, x, y));
      cs.forEach((c, i) => { handles[i].setAttribute('cx', c.x); handles[i].setAttribute('cy', c.y); });
      if (root.activeElement !== pct) pct.value = String(Math.round(rect.w / coverW * 100));
      const mb = [[lb.x, lb.y], [lb.x + lb.w, lb.y], [lb.x + lb.w, lb.y + lb.h], [lb.x, lb.y + lb.h]].map(([x, y]) => SB.apply(t, x, y));
      const all = cs.concat(mb), vis = SB.visibleWorkspaceRect();
      const midX = (Math.min(...mb.map((c) => c.x)) + Math.max(...mb.map((c) => c.x))) / 2;
      const half = (pill.offsetWidth || 240) / 2;
      pill.style.left = Math.max(vis.left + half + 8, Math.min(vis.right - half - 8, midX)) + 'px';
      pill.style.top = Math.min(vis.bottom - 44, Math.max(...all.map((c) => c.y)) + 18) + 'px';
    };
    const toLocal = (ev) => SB.apply(SB.matInv(T()), ev.clientX, ev.clientY);
    const scaleAbout = (w, cx, cy) => {
      const k = Math.max(w, 1) / rect.w;
      rect.x = cx - (cx - rect.x) * k; rect.y = cy - (cy - rect.y) * k; rect.w *= k; rect.h *= k;
    };
    let drag = null;
    const down = (ev) => {
      if (ev.button !== 0) return;
      ev.preventDefault(); ev.stopPropagation();
      svg.focus({ preventScroll: true });
      if (ev.target === back) { close(true); return; }
      const p = toLocal(ev);
      const h = ev.target.getAttribute && ev.target.getAttribute('data-h');
      drag = h !== null && h !== undefined && ev.target.classList.contains('h')
        ? { kind: 'size', i: +h, r0: Object.assign({}, rect) }
        : { kind: 'move', p, r0: Object.assign({}, rect) };
      svg.setPointerCapture(ev.pointerId);
    };
    const move = (ev) => {
      if (!drag) return;
      const p = toLocal(ev), r0 = drag.r0;
      if (drag.kind === 'move') {
        let dx = p.x - drag.p.x, dy = p.y - drag.p.y;
        if (ev.shiftKey) { if (Math.abs(dx) > Math.abs(dy)) dy = 0; else dx = 0; }
        rect.x = r0.x + dx; rect.y = r0.y + dy;
      } else {
        // The corner across from the one held stays where it is.
        const right = drag.i === 1 || drag.i === 2, bottom = drag.i >= 2;
        const ax = right ? r0.x : r0.x + r0.w, ay = bottom ? r0.y : r0.y + r0.h;
        const k = Math.max(Math.abs(p.x - ax) / r0.w, Math.abs(p.y - ay) / r0.h, 0.02);
        rect.w = r0.w * k; rect.h = r0.h * k;
        rect.x = right ? ax : ax - rect.w; rect.y = bottom ? ay : ay - rect.h;
      }
      paint();
    };
    const up = (ev) => { if (drag) { drag = null; try { svg.releasePointerCapture(ev.pointerId); } catch { /* not captured */ } } };
    const key = (ev) => {
      if (!adjust) return;
      const inPill = root.activeElement === pct;
      if (ev.key === 'Escape') { ev.preventDefault(); ev.stopPropagation(); close(false); return; }
      if (ev.key === 'Enter') { ev.preventDefault(); ev.stopPropagation(); if (inPill) pct.blur(); close(true); return; }
      if (inPill) { ev.stopPropagation(); return; }
      const step = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[ev.key];
      ev.preventDefault(); ev.stopPropagation();
      if (!step) return;
      const t = T(), px = Math.hypot(t[0], t[1]) || 1, n = (ev.shiftKey ? 10 : 1) / px;
      rect.x += step[0] * n; rect.y += step[1] * n;
      paint();
    };
    const swallow = (ev) => { if (adjust) ev.stopPropagation(); };
    const repaint = () => { if (adjust) paint(); };
    async function close(keep) {
      if (!adjust) return;
      adjust = null;
      window.removeEventListener('keydown', key, true);
      window.removeEventListener('keyup', swallow, true);
      window.removeEventListener('resize', repaint);
      window.removeEventListener('wheel', repaint, true);
      svg.remove(); pill.remove();
      const moved = ['x', 'y', 'w', 'h'].some((k) => Math.abs(rect[k] - start[k]) > 1e-6 * Math.max(1, Math.abs(start[k])) + 1e-9);
      if (!keep || !moved) { g.style.visibility = was; SB.focusTextbox(); return; }
      await run('maskAdjust', async () => {
        try {
          if (!sameSet(topIdsOf(SB.readSelection()), [id]) && !(await selectIds([id]))) throw userError('Couldn’t select the masked image again to save the change');
          const now = SB.readSelection();
          const cur = maskedPicture(now);
          if (!cur) throw userError('The masked image changed while it was being adjusted. Nothing was saved.');
          const props = clone(cur[4]);
          const fit = SB.imageFillProps(rect, lb);
          [84, 85, 79, 80].forEach((k) => SB.setProp(props, k, fit[k]));
          const nid = SB.newId();
          await replaceSelection(now, [[3, nid, cur[2], cur[3].slice(), props]], { srcOf: { [nid]: id } });
        } finally {
          const still = SB.elementFor(id);
          if (still) still.style.visibility = was;
        }
      });
    }
    svg.addEventListener('pointerdown', down);
    svg.addEventListener('pointermove', move);
    svg.addEventListener('pointerup', up);
    svg.addEventListener('pointercancel', up);
    ['mousedown', 'mouseup', 'click', 'dblclick', 'contextmenu'].forEach((t) => svg.addEventListener(t, (ev) => { ev.preventDefault(); ev.stopPropagation(); }));
    pill.addEventListener('pointerdown', (ev) => ev.stopPropagation());
    pill.addEventListener('mousedown', (ev) => { if (ev.target !== pct) ev.preventDefault(); ev.stopPropagation(); });
    pct.addEventListener('focus', () => setTimeout(() => pct.select(), 0));
    const setPct = () => {
      const v = parseFloat(pct.value);
      if (!Number.isFinite(v) || v <= 0) return;
      scaleAbout(coverW * v / 100, lb.x + lb.w / 2, lb.y + lb.h / 2);
      paint();
    };
    pct.addEventListener('input', setPct);
    RK.scrub(pill.querySelector('.seg'), pct, { step: 1, min: 1, onValue: () => setPct() });
    bFit.addEventListener('click', () => {
      rect.w = coverW; rect.h = coverW / aspect;
      rect.x = lb.x + (lb.w - rect.w) / 2; rect.y = lb.y + (lb.h - rect.h) / 2;
      paint();
    });
    bNo.addEventListener('click', () => close(false));
    bOk.addEventListener('click', () => close(true));
    window.addEventListener('keydown', key, true);
    window.addEventListener('keyup', swallow, true);
    window.addEventListener('resize', repaint);
    window.addEventListener('wheel', repaint, true);
    adjust = { id, close };
    paint();
    svg.focus({ preventScroll: true });
    toast('Drag the picture under its mask · corners resize · ↵ keeps, Esc cancels', 5000);
  }

  // Images can't go through a copy and paste of their data (Slides drops
  // the picture), so anything that moves them uses Slides' own commands.
  const hasImage = (ids) => ids.some((id) => { const g = SB.elementFor(id); return !!(g && g.querySelector('image')); });
  const ALIGN_LABEL = { alignLeft: 'Left', alignHCenter: 'Center', alignRight: 'Right', alignTop: 'Top', alignVMiddle: 'Middle', alignBottom: 'Bottom' };
  // Arrange › <group> › <item>, with Slides' menus invisible. Labels as seen
  // live: Align › Left, Center, Right, Top, Middle, Bottom (two or more
  // selected); Distribute (three or more); Center on page › Horizontally,
  // Vertically.
  // Picks Arrange › group › label from Slides' own menu, unseen. Waits on
  // what Slides does rather than fixed pauses: the menu showing, its
  // submenu showing, then (with ids to watch) those objects moving.
  async function slidesMenuPick(group, label, watch = []) {
    const mb = document.getElementById('sketchy-arrange-menu');
    if (!mb) return false;
    const hide = document.createElement('style');
    hide.textContent = '.goog-menu, .goog-menu * { opacity: 0 !important; }';
    document.documentElement.appendChild(hide);
    const vis = () => [...document.querySelectorAll('.goog-menu')].filter((m) => m.getBoundingClientRect().width > 0 && getComputedStyle(m).display !== 'none' && getComputedStyle(m).visibility !== 'hidden');
    const hoverEl = (n) => {
      const r = n.getBoundingClientRect();
      const o = { bubbles: true, cancelable: true, view: window, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2 };
      n.dispatchEvent(new MouseEvent('mouseover', o));
      n.dispatchEvent(new MouseEvent('mousemove', o));
    };
    const until = async (f, ms) => { const t = performance.now(); let v; while (!(v = f()) && performance.now() - t < ms) await sleep(16); return v; };
    const rectOf = (id) => { const g = SB.elementFor(id); const r = g && g.getBoundingClientRect(); return r ? r.left + ',' + r.top : ''; };
    const before = watch.map(rectOf);
    try {
      pressEl(mb);
      const top = await until(() => vis()[0], 600);
      const it = top && [...top.querySelectorAll('.goog-menuitem')].find((x) => x.textContent.trim().startsWith(group));
      if (!it || it.getAttribute('aria-disabled') === 'true') { if (top) pressEl(mb); return false; }
      hoverEl(it);
      const item = await until(() => {
        const sub = vis().find((m) => m !== top);
        return sub && [...sub.querySelectorAll('.goog-menuitem')].find((x) => x.textContent.trim().startsWith(label));
      }, 600);
      if (!item || item.getAttribute('aria-disabled') === 'true') { pressEl(mb); return false; }
      pressEl(item);
      SB.tick();
      if (watch.length) await until(() => watch.some((id, i) => rectOf(id) !== before[i]), 800);
      else await sleep(120);
      return true;
    } finally {
      setTimeout(() => hide.remove(), 250);
    }
  }

  // ── Command palette ─────────────────────────────────────────────────────
  let pal = null;
  function openPalette() {
    if (pal) { pal.close(); return; }
    const sel = SB.readSelection();
    const n = topIdsOf(sel).length;
    const cmds = RK.commandList([
      { act: 'edit', label: 'Edit Shape', group: 'Shape tools', key: 'Double-click', icon: 'edit' },
      { act: 'pen', label: 'Pen: draw new shapes (or edit the selected ones)', group: 'Shape tools', key: SB.SHORTCUT_LABEL.pen, icon: 'pen' },
      { act: 'layers', label: panel && panel.classList.contains('show') ? 'Hide layers' : 'Show layers', group: 'Shape tools', key: SB.SHORTCUT_LABEL.layers, icon: 'layers' },
      { act: 'toggleRail', label: rail && rail.classList.contains('min') ? 'Show the toolbar' : 'Hide the toolbar', group: 'Shape tools', key: SB.SHORTCUT_LABEL.toggleRail, icon: 'logo' },
      { act: 'themeBuilder', label: 'Theme builder (layouts and master)', group: 'Shape tools', key: SB.SHORTCUT_LABEL.themeBuilder, icon: 'logo' },
      { act: 'restoreText', label: 'Restore outlined text', group: 'Outline', key: SB.SHORTCUT_LABEL.outlineText, icon: 'restoreText' },
    ]).map((c) => Object.assign(c, { enabled: ['layers', 'toggleRail', 'themeBuilder', 'pen'].includes(c.act) || n > 0 }));
    pal = RK.palette(root, cmds, (act) => { SB.focusTextbox(); command(act); }, {
      rect: SB.visibleWorkspaceRect(),
      onClose: () => { pal = null; SB.focusTextbox(); },
    });
  }

  // Shortcuts that work with nothing selected.
  const ANYTIME = new Set(['palette', 'toggleRail', 'layers', 'themeBuilder', 'pen']);

  // ── ⌘Z / ⌘⇧Z over our multi-step changes ──────────────────────────────
  // See SB.beginMacro: right after one of ours, one press walks Slides'
  // own history back (or forward) over all of its steps.
  function undoKind(e) {
    const prim = SB.IS_MAC ? e.metaKey && !e.ctrlKey : e.ctrlKey && !e.metaKey;
    if (!prim || e.altKey) return null;
    if (e.code === 'KeyZ') return e.shiftKey ? 'redo' : 'undo';
    if (e.code === 'KeyY' && !e.shiftKey) return 'redo'; // Slides' own redo is ⌘Y on Mac too
    return null;
  }
  function undoRedoKey(e) {
    const k = undoKind(e);
    if (!k) return false;
    if (editingText()) return false;
    const stop = () => { e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation(); };
    // Still finishing one of ours: wait for it, then decide.
    if (SB.isReplaying() || busy || SB.isRecording()) {
      stop();
      (async () => {
        for (let i = 0; i < 100 && (SB.isReplaying() || busy || SB.isRecording()); i++) await sleep(30);
        if (k === 'undo' ? SB.canUndoMacro() : SB.canRedoMacro()) {
          busy = true;
          try { await frozenWhile(null, () => (k === 'undo' ? SB.undoMacro() : SB.redoMacro())); } finally { busy = false; scheduleRefresh(150); }
        } else {
          SB.nativeUndo(k === 'redo');
        }
      })();
      return true;
    }
    if (!(k === 'undo' ? SB.canUndoMacro() : SB.canRedoMacro())) return false;
    stop();
    busy = true;
    frozenWhile(null, () => (k === 'undo' ? SB.undoMacro() : SB.redoMacro())).finally(() => { busy = false; scheduleRefresh(150); });
    return true;
  }
  // Slides' toolbar Undo / Redo buttons get the same treatment.
  function onUndoButton(e) {
    if (!e.isTrusted || (self.SVG2S_EDIT && self.SVG2S_EDIT.isOpen())) return;
    const b = e.target.closest && e.target.closest('#undoButton, #redoButton, [aria-label^="Undo ("], [aria-label^="Redo ("]');
    if (!b || b.closest('#svg2slides-shape-tools')) return;
    const redo = /redo/i.test(b.id || b.getAttribute('aria-label') || '');
    if (e.type === 'click') { if (b._svgxTake) { b._svgxTake = false; e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation(); } return; }
    if (e.type === 'mousedown') b._svgxTake = !busy && !SB.isReplaying() && (redo ? SB.canRedoMacro() : SB.canUndoMacro());
    if (!b._svgxTake) return;
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    if (e.type === 'mouseup') {
      busy = true;
      frozenWhile(null, () => (redo ? SB.redoMacro() : SB.undoMacro())).finally(() => { busy = false; scheduleRefresh(150); });
    }
  }

  // ── Theme objects (from the slide's layout or master) ───────────────────
  // Slides draws them on the slide like its own objects, but edits made to
  // them there don't stick. Slides' Select all (⌘A) takes only the slide's
  // own objects (checked live: it left out the one master object), so one
  // quiet ⌘A per slide sorts them; anything that appears later is the
  // slide's own.
  const themeCache = new Map(); // page id → { own: Set, seen: Set }
  let probing = null;
  function isThemeObject(id) {
    const page = SB.currentPageGroup();
    const c = page && themeCache.get(page.id);
    if (!c) return false;
    let top = id;
    const anc = ancestorsOf(id);
    if (anc.length) top = anc[0];
    return c.seen.has(top) && !c.own.has(top);
  }
  // Known for this slide, and no objects have appeared since (a theme
  // edit can add theme objects too, so new ones are checked again).
  function themeKnown() {
    const page = SB.currentPageGroup();
    const c = page && themeCache.get(page.id);
    if (!c) return false;
    const order = SB.topLevelOrder();
    const fresh = order.filter((id) => !c.seen.has(id));
    if (!fresh.length) return true;
    // New objects above the slide's backmost own object are the slide's own
    // (theme objects are always drawn underneath); only a new one at the
    // very back needs another look.
    const firstOwn = order.findIndex((id) => c.own.has(id));
    if (firstOwn >= 0 && fresh.every((id) => order.indexOf(id) > firstOwn)) {
      fresh.forEach((id) => { c.seen.add(id); c.own.add(id); });
      return true;
    }
    themeCache.delete(page.id);
    return false;
  }
  function markTheme(id) {
    const page = SB.currentPageGroup();
    if (!page) return;
    const anc = ancestorsOf(id);
    const top = anc.length ? anc[0] : id;
    const c = themeCache.get(page.id) || { own: new Set(SB.topLevelOrder().filter((x) => x !== top)), seen: new Set(SB.topLevelOrder()) };
    c.own.delete(top);
    c.seen.add(top);
    themeCache.set(page.id, c);
  }
  function probeTheme() {
    if (probing) return probing;
    const page = SB.currentPageGroup();
    if (!page || themeCache.has(page.id) || editingText() || (self.SVG2S_EDIT && self.SVG2S_EDIT.isOpen())) return Promise.resolve();
    probing = (async () => {
      const wasBusy = busy;
      busy = true;
      try {
        const prior = topIdsOf(SB.readSelection());
        const seen = new Set(SB.topLevelOrder());
        let own = null;
        const hash0 = location.hash;
        // Wherever the keyboard was (the filmstrip, say), it goes back there.
        const focus0 = document.activeElement;
        await frozenWhile(null, async () => {
          const tb = SB.textbox();
          if (!tb) return;
          // ⌘A goes wherever Slides thinks the keyboard is: after a slide
          // change that's the filmstrip, where it selects every slide (and
          // jumps to the last one). A click on empty canvas first makes the
          // slide the place (and clears the selection).
          const spot = emptyCanvasPoint();
          if (!spot) return;
          clickAt(spot, false);
          await sleep(60);
          SB.focusTextbox();
          const o = Object.assign({ key: 'a', code: 'KeyA', keyCode: 65, which: 65, bubbles: true, cancelable: true }, SB.IS_MAC ? { metaKey: true } : { ctrlKey: true });
          tb.dispatchEvent(new KeyboardEvent('keydown', o));
          tb.dispatchEvent(new KeyboardEvent('keyup', o));
          // Read until two reads agree: on a busy slide Slides is still
          // selecting when the first read comes back, and a short read made
          // ordinary objects look like theme objects.
          let last = null;
          for (let i = 0; i < 12; i++) {
            await sleep(i ? 60 : 120);
            const ids = topIdsOf(SB.readSelection()).sort().join(' ');
            if (ids && ids === last) break;
            last = ids;
          }
          own = new Set(last ? last.split(' ') : []);
          // Put the selection back as it was.
          if (prior.length) await selectIds(prior);
          else { SB.pressKey('Escape'); await sleep(30); }
        });
        const ifr = SB.iframe();
        if (focus0 && focus0 !== ifr && focus0 !== document.body && focus0.isConnected && !(host && host.contains(focus0))) { try { focus0.focus(); } catch { /* gone */ } }
        // Only keep a clean answer: same slide, and only this slide's objects.
        if (own && own.size && SB.currentPageGroup() === page && location.hash === hash0 && [...own].every((id) => seen.has(id))) {
          // Theme objects are drawn under the slide's own, so they can only
          // be at the back of the stack: anything left out above the
          // slide's backmost own object was a misread, not the theme.
          const order = SB.topLevelOrder();
          const firstOwn = order.findIndex((id) => own.has(id));
          order.forEach((id, i) => { if (i > firstOwn) own.add(id); });
          themeCache.set(page.id, { own, seen });
        }
        else if (location.hash !== hash0) { location.hash = hash0; }
      } finally {
        busy = wasBusy;
        probing = null;
      }
      if (panel && panel.classList.contains('show')) renderList(true);
      updateHover();
    })();
    return probing;
  }

  // A point that clicks nothing: the grey margin around the slide, else a
  // bare part of the slide's background.
  function emptyCanvasPoint() {
    const page = SB.currentPageGroup();
    if (!page) return null;
    const pr = page.getBoundingClientRect();
    const vis = SB.visibleWorkspaceRect();
    const isEmpty = (x, y) => {
      if (x < vis.left + 2 || x > vis.right - 2 || y < vis.top + 2 || y > vis.bottom - 2) return null;
      const t = document.elementFromPoint(x, y);
      if (!t || (host && host.contains(t)) || t.closest('#svg2slides-freeze')) return null;
      const obj = t.closest && t.closest('g[id^="editor-"]');
      if (obj && obj !== page && !/-bg$/.test(obj.id)) return null; // an object
      if (!document.getElementById('workspace') || !document.getElementById('workspace').contains(t)) return null;
      return { x, y, t };
    };
    const tries = [[pr.left - 10, pr.top + pr.height / 2], [pr.right + 10, pr.top + pr.height / 2], [pr.left + pr.width / 2, pr.top - 10], [pr.left + pr.width / 2, pr.bottom + 10]];
    for (let gy = 1; gy < 8; gy++) for (let gx = 1; gx < 8; gx++) tries.push([pr.left + (pr.width * gx) / 8, pr.top + (pr.height * gy) / 8]);
    for (const [x, y] of tries) { const p = isEmpty(x, y); if (p) return p; }
    return null;
  }

  // Two-step answers: the first click says what's going on, a second click
  // on the same thing within a few seconds does it.
  // While armed, the row (and the outline on the slide, if showing) says
  // what the next click will do.
  let ask = null, askT = null;
  function askTwice(kind, id, msg) {
    const now = Date.now();
    clearTimeout(askT);
    if (ask && ask.kind === kind && ask.id === id && now < ask.until) { ask = null; showArmed(null); return true; }
    ask = { kind, id, until: now + 5000, msg };
    toast(msg, 5000);
    showArmed(ask);
    askT = setTimeout(() => { ask = null; showArmed(null); }, 5000);
    return false;
  }
  const ARMED_LABEL = { theme: 'Click again → theme builder', small: 'Click again → zoom in' };
  function showArmed(a) {
    if (!list) return;
    list.querySelectorAll('.row.armed').forEach((r) => { r.classList.remove('armed'); const nm = r.querySelector('.nm'); if (nm && nm._was !== undefined) { nm.textContent = nm._was; delete nm._was; } });
    if (a) {
      const r = list.querySelector(`.row[data-id="${a.id}"]`);
      const nm = r && r.querySelector('.nm');
      if (r && nm) { r.classList.add('armed'); nm._was = nm.textContent; nm.textContent = ARMED_LABEL[a.kind] || nm.textContent; }
    }
    if (hoverBox && hoverBox._id) paintHover(hoverBox._id);
  }

  // Theme builder (View › Theme builder), on the layout or master that
  // holds `objId`. Slides' theme filmstrip names its pages and their objects
  // filmstrip-master-<id> and filmstrip-layout-<n>-<id> (seen live), and
  // #slide=id.<page> opens any of them; a slide id goes back.
  let returnTo = null;
  const inThemeBuilder = () => !!document.querySelector('g[id^="filmstrip-layout-"], g[id^="filmstrip-master-"]') &&
    [...document.querySelectorAll('g[id^="filmstrip-layout-"], g[id^="filmstrip-master-"]')].some((g) => g.getBoundingClientRect().width > 0);
  async function openThemeBuilder(objId) {
    if (busy) return;
    busy = true;
    toast(objId ? 'Opening the theme builder on its layout…' : 'Opening the theme builder…', 6000);
    try {
      const page = SB.currentPageGroup();
      themeCache.clear(); // the theme may change; sort the slides again after
      if (!inThemeBuilder()) {
        returnTo = page ? page.id.slice('editor-'.length) : null;
        // Through Slides' View menu, kept out of sight.
        const hideMenus = document.createElement('style');
        hideMenus.textContent = '.goog-menu, .goog-menu * { opacity: 0 !important; }';
        document.documentElement.appendChild(hideMenus);
        try {
          const vm = document.getElementById('docs-view-menu');
          if (!vm) throw userError('Couldn’t find Slides’ View menu');
          // Slides opens its menus for the document it thinks is active:
          // start from the slide (a click in our panel leaves it elsewhere),
          // close any menu already open, and give the menu a few tries.
          const findItem = () => [...document.querySelectorAll('.goog-menuitem')].find((i) => i.getBoundingClientRect().width > 0 && /^Theme builder/.test(i.textContent.replace(/\s+/g, ' ').trim()));
          // Called from a Layers click, the rest of that click (mouseup,
          // click) would land after the menu opens and close it: let it pass.
          await sleep(150);
          let item = null;
          for (let attempt = 0; attempt < 3 && !item; attempt++) {
            SB.focusTextbox();
            SB.pressKey('Escape');
            await sleep(60);
            pressEl(vm);
            for (let i = 0; i < 12 && !item; i++) { await sleep(60); item = findItem(); }
            if (!item) { pressEl(vm); await sleep(120); }
          }
          if (!item) throw userError('Couldn’t open Theme builder from Slides’ View menu');
          pressEl(item);
        } finally {
          setTimeout(() => hideMenus.remove(), 300);
        }
        for (let i = 0; i < 60 && !inThemeBuilder(); i++) await sleep(80);
        if (!inThemeBuilder()) throw userError('The theme builder didn’t open');
      }
      if (!objId) return;
      // The layout or master that holds the object.
      const tag = [...document.querySelectorAll('g[id^="filmstrip-layout-"], g[id^="filmstrip-master-"]')].find((g) => g.id.endsWith('-' + objId));
      let root = tag;
      for (let p = tag && tag.parentNode && tag.parentNode.closest('g[id^="filmstrip-"]'); p; p = p.parentNode && p.parentNode.closest('g[id^="filmstrip-"]')) root = p;
      const pageId = root ? root.id.replace(/^filmstrip-(master|layout-\d+)-/, '') : null;
      if (pageId && (!SB.currentPageGroup() || SB.currentPageGroup().id !== 'editor-' + pageId)) {
        location.hash = '#slide=id.' + pageId;
        for (let i = 0; i < 40 && !(SB.currentPageGroup() && SB.currentPageGroup().id === 'editor-' + pageId); i++) await sleep(80);
      }
      // Let the page finish drawing, then select the object, checking it
      // took (Slides can still be settling the new page).
      let ok = false;
      for (let tries = 0; tries < 3 && !ok; tries++) {
        await sleep(tries ? 400 : 300);
        const g = SB.elementFor(objId);
        if (!g || !g.getBoundingClientRect().width) continue;
        busy = false;
        ok = await selectIds([objId]);
        busy = true;
      }
      if (!ok) toast('In the theme builder: couldn’t select it for you, but it’s on this page');
      else toast('Editing the theme. ' + SB.SHORTCUT_LABEL.themeBuilder + ' takes you back to the slide.', 4000);
    } catch (err) {
      toast(err && err.userMessage ? err.userMessage : 'Couldn’t open the theme builder');
    } finally {
      busy = false;
      refreshSelection();
    }
  }
  function toggleThemeBuilder() {
    if (inThemeBuilder()) {
      if (returnTo) location.hash = '#slide=id.' + returnTo;
      else toast('Close the theme builder with the × at its top right');
      return;
    }
    return openThemeBuilder(null);
  }

  // Objects too small to click at this zoom: zoom in on them.
  function screenSize(id) {
    const g = SB.elementFor(id);
    const r = g && g.getBoundingClientRect();
    return r ? Math.max(r.width, r.height) : 0;
  }
  // Its size on screen, or null if it can't be measured. Slides redraws
  // objects (text especially) by taking them out and putting them back, so
  // a single look can find nothing there and call it tiny.
  async function screenSizeSettled(id) {
    for (let i = 0; i < 4; i++) {
      const g = SB.elementFor(id);
      if (g && g.isConnected) {
        const r = g.getBoundingClientRect();
        const n = Math.max(r.width, r.height);
        if (n >= 6) return n;
        // Measure what's drawn too: a group's box can lag its contents.
        const kids = [...g.querySelectorAll('path, image, text, rect, ellipse, line, polyline, polygon')];
        const m = kids.reduce((a, k) => { const q = k.getBoundingClientRect(); return Math.max(a, q.width, q.height); }, n);
        if (m >= 6) return m;
        if (i === 3) return m;
      }
      await sleep(50);
    }
    return null;
  }
  async function zoomTo(id) {
    const g = SB.elementFor(id);
    const ctm = SB.pageCTM();
    const inv = ctm && SB.matInv(ctm);
    if (!g || !inv) return false;
    const r = g.getBoundingClientRect();
    const a = SB.apply(inv, r.left, r.top), z = SB.apply(inv, r.right, r.bottom);
    const vis = SB.visibleWorkspaceRect();
    const size = Math.max(1, Math.max(r.width, r.height));
    const pct0 = SB.zoomPctFromCTM(ctm);
    const want = Math.min(SB.ZOOM_MAX, Math.max(pct0, pct0 * (Math.min(vis.right - vis.left, vis.bottom - vis.top) * 0.25) / size));
    await SB.matchSlidesView(Math.round(want), { x: (a.x + z.x) / 2, y: (a.y + z.y) / 2 }, (vis.left + vis.right) / 2, (vis.top + vis.bottom) / 2);
    await sleep(250);
    return true;
  }

  // ── ⌘-click: pick the object itself, even deep inside groups ───────────
  // Figma's deep select. The innermost object under the pointer is selected
  // directly (⇧ too adds it). Slides never sees the ⌘-click.
  const primaryHeld = (e) => (SB.IS_MAC ? e.metaKey : e.ctrlKey);
  let deepGesture = false;
  function innermostAt(target) {
    const page = SB.currentPageGroup();
    if (!page || !target || !page.contains(target)) return null;
    let g = target.closest && target.closest('g[id^="editor-"]');
    while (g && g !== page && !/^editor-[^-]+$/.test(g.id)) g = g.parentNode && g.parentNode.closest('g[id^="editor-"]');
    return g && g !== page ? g.id.slice('editor-'.length) : null;
  }
  // ⌘-clicks are handled one after another, never dropped, so a second
  // click that lands while the first is still being worked out counts.
  let deepQueue = Promise.resolve();
  function onDeepClick(e) {
    if (!e.isTrusted || (self.SVG2S_EDIT && self.SVG2S_EDIT.isOpen())) return;
    if (e.type === 'pointerdown' || e.type === 'mousedown') {
      if (e.button !== 0 || !primaryHeld(e) || e.altKey) { if (e.type === 'pointerdown') deepGesture = false; return; }
      const id = innermostAt(e.target);
      if (!id) { if (e.type === 'pointerdown') deepGesture = false; return; }
      e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
      if (e.type === 'pointerdown') {
        deepGesture = true;
        const at = { x: e.clientX, y: e.clientY, t: e.target }, add = e.shiftKey;
        deepQueue = deepQueue.then(async () => {
          for (let i = 0; i < 100 && busy && !probing; i++) await sleep(30);
          if (!themeKnown()) await probeTheme();
          if (isThemeObject(id)) {
            if (askTwice('theme', id, 'Part of the theme, so changes here won’t stick. ⌘-click it again to edit it in the theme builder.')) await openThemeBuilder(id);
            return;
          }
          busy = true;
          try { await deepSelect(id, add, at); } finally { busy = false; refreshSelection(); }
        }).catch(() => {});
      }
      return;
    }
    if (!deepGesture) return;
    e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
    if (e.type === 'click') deepGesture = false;
  }

  // ── ⌘ held over the slide: outline what a ⌘-click would pick ───────────
  let hoverBox = null, hoverPt = null;
  function paintHover(id) {
    if (!hoverBox) return;
    const g = id && SB.elementFor(id);
    const r = g && g.getBoundingClientRect();
    if (!r || !r.width) { hoverBox.style.display = 'none'; hoverBox._id = null; return; }
    const theme = isThemeObject(id);
    const armed = !!(ask && ask.id === id && ask.kind === 'theme' && Date.now() < ask.until);
    hoverBox._id = id;
    hoverBox.className = 'hov' + (theme ? ' theme' : '') + (armed ? ' armed' : '');
    hoverBox.style.cssText = `display:block;left:${r.left - 2}px;top:${r.top - 2}px;width:${r.width + 4}px;height:${r.height + 4}px;`;
    hoverBox.firstChild.textContent = theme ? (armed ? '⌘-click again: edit in theme builder' : 'Theme object · ⌘-click twice to edit it') : (names[id] || describe(id).label);
  }
  function updateHover(e) {
    if (!hoverBox || (self.SVG2S_EDIT && self.SVG2S_EDIT.isOpen())) return;
    if (e && e.clientX !== undefined) hoverPt = { x: e.clientX, y: e.clientY, meta: primaryHeld(e) };
    if (!hoverPt || !hoverPt.meta) { hoverBox.style.display = 'none'; hoverBox._id = null; return; }
    const t = document.elementFromPoint(hoverPt.x, hoverPt.y);
    const id = innermostAt(t);
    if (id && !themeKnown() && !probing) probeTheme();
    paintHover(id);
  }

  // ── Paste SVG code ──────────────────────────────────────────────────────
  // Copied SVG markup pasted onto the slide goes through the same flow as a
  // dropped file: the ghost follows the pointer, click to place. Text boxes
  // being typed in still get the code as text.
  let lastPointer = null;
  document.addEventListener('pointermove', (e) => { lastPointer = { x: e.clientX, y: e.clientY }; }, true);
  function looksLikeSvg(t) {
    const s2 = (t || '').trim();
    return s2.length < 5e6 && /^(<\?xml[\s\S]*?\?>\s*)?(<!--[\s\S]*?-->\s*)*(<!DOCTYPE[^>]*>\s*)?<svg[\s>]/i.test(s2) && /<\/svg>\s*$/i.test(s2);
  }
  const editingText = () => !!document.querySelector('.docs-text-selectionhandle');
  function onPasteSvg(e) {
    if (!e.isTrusted || editingText() || (self.SVG2S_EDIT && self.SVG2S_EDIT.isOpen())) return;
    const cd = e.clipboardData;
    if (!cd || [...cd.types].includes(SB.MIME)) return;
    const txt = cd.getData('text/plain');
    if (!looksLikeSvg(txt) || typeof beginInsertFlow !== 'function') return;
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    const vis = SB.visibleWorkspaceRect();
    const inside = lastPointer && lastPointer.x > vis.left && lastPointer.x < vis.right && lastPointer.y > vis.top && lastPointer.y < vis.bottom;
    const p = inside ? lastPointer : { x: (vis.left + vis.right) / 2, y: (vis.top + vis.bottom) / 2 };
    const name = ((txt.match(/<title>([^<]{1,60})<\/title>/i) || [])[1] || 'pasted').replace(/[^\w -]+/g, '').trim() || 'pasted';
    beginInsertFlow([new File([txt], name + '.svg', { type: 'image/svg+xml' })], p.x, p.y);
  }

  // ── Slides' own commands ───────────────────────────────────────────────

  // Edit Shape from the rail: the same editor the double-click opens.
  // Slides' own shapes, lines and WordArt convert first (Cancel restores).
  function editShape(tool) {
    const E = self.SVG2S_EDIT;
    if (!E || busy || E.isOpen()) return;
    const sel = SB.readSelection();
    const shapes = (sel || []).filter((x) => x[0] === 3);
    // Nothing selected: draw new shapes with the pen.
    if (!shapes.length) { E.openEditor([], { blank: true, tool: 'pen' }); return; }
    if (shapes.every(SB.isEditableShape)) { E.openEditor(sel, { tool }); return; }
    if (shapes.every((x) => SB.isEditableShape(x) || SB.convertibleKind(sel, x))) { E.convertAndOpen(sel, { tool }); return; }
    toast("Images, video and charts can't be edited as shapes");
  }

  function groupOp(want) {
    return run('group', async () => {
      const sel = requireSelection();
      const ids = topIdsOf(sel);
      const single = ids.length === 1 ? entryById(sel, ids[0]) : null;
      if (want === 'ungroup' && !(single && single[0] === 2)) throw userError('Select a group to ungroup');
      if (want === 'group' && ids.length < 2) throw userError('Select two or more objects to group');
      if (want === 'group') {
        // Slides won't group a layout placeholder (title, subtitle, body):
        // Arrange › Group stays grey. A copy pasted from the resolved data
        // is the same box with the same text and no tie to the layout, so
        // swap each placeholder for that first (checked live).
        const ph = SB.placeholderIds(SB.readSelectionRaw()).filter((id) => ids.includes(id));
        if (ph.length) {
          const others = ids.filter((id) => !ph.includes(id));
          const before = new Set(SB.topLevelOrder());
          if (!(await selectIds(ph))) throw userError('Couldn’t select the placeholder text to group it');
          const phSel = SB.readSelection();
          if (!phSel || !(await replaceSelection(phSel, phSel))) throw userError('Couldn’t turn the placeholder into a text box to group it');
          const made = SB.topLevelOrder().filter((id) => !before.has(id));
          if (made.length !== ph.length || !(await selectIds([...others, ...made]))) throw userError(`Couldn’t select everything again. Select the objects and press Group once more.`);
          notes.add(ph.length === 1 ? 'The placeholder became a plain text box, since Slides can’t group placeholders' : 'The placeholders became plain text boxes, since Slides can’t group placeholders');
          keyCombo('g', 'KeyG', 71, Object.assign({ altKey: true }, PRIMARY));
          await sleep(250);
          if (topIdsOf(SB.readSelection()).length !== 1) throw userError('Slides wouldn’t group that selection');
          return;
        }
      }
      if (single && single[0] === 2) {
        keyCombo('G', 'KeyG', 71, Object.assign({ altKey: true, shiftKey: true }, PRIMARY));
      } else if (ids.length >= 2) {
        keyCombo('g', 'KeyG', 71, Object.assign({ altKey: true }, PRIMARY));
      } else {
        throw userError('Select two or more objects to group');
      }
      await sleep(250);
    });
  }

  // ── Memory: what our own results were made from ─────────────────────────
  // Keyed by path fingerprint (SB.pathFingerprint): ids change on paste,
  // geometry doesn't. Kept in chrome.storage on this computer.
  //   text:  outlined glyphs → the original text object (font, size, place)
  //   align: an inside/outside stroke → the shape's own outline + position
  const MEM_KEY = 'svgxMemory';
  let memory = {};
  try { chrome.storage.local.get(MEM_KEY, (v) => { memory = (v && v[MEM_KEY]) || {}; }); } catch { /* storage unavailable */ }
  let memT = null;
  function remember(fp, rec) {
    if (!fp) return;
    memory[fp] = Object.assign({ at: Date.now() }, rec);
    const keys = Object.keys(memory);
    if (keys.length > 400) keys.sort((a, b) => memory[a].at - memory[b].at).slice(0, keys.length - 400).forEach((k) => delete memory[k]);
    clearTimeout(memT);
    memT = setTimeout(() => { try { chrome.storage.local.set({ [MEM_KEY]: memory }); } catch { /* storage unavailable */ } }, 300);
  }
  const recall = (fp) => (fp && memory[fp]) || null;
  // Page-unit box of a shape entry, from its payload (w/h through its
  // page transform).
  function entryBox(resolved, e) {
    const M = SB.localToPage(resolved, e);
    const w = SB.getProp(e[4], 8) || 0, h = SB.getProp(e[4], 9) || 0;
    const pts = [[0, 0], [w, 0], [w, h], [0, h]].map(([x, y]) => SB.apply(M, x, y));
    const xs = pts.map((q) => q.x), ys = pts.map((q) => q.y);
    return { minX: Math.min(...xs), minY: Math.min(...ys), maxX: Math.max(...xs), maxY: Math.max(...ys) };
  }
  // The selected outlined text, if we made it: { rec, entry, unitTop }.
  function outlinedTextIn(sel) {
    for (const e of sel || []) {
      if (e[0] !== 3) continue;
      const rec = recall(SB.pathFingerprint(e));
      if (rec && rec.kind === 'text') return { rec, entry: e };
    }
    return null;
  }

  // ── Slides' own commands ───────────────────────────────────────────────
  // Rotate, resize, arrange: Slides' shortcuts, sent as synthetic keys
  // (verified live, Nov 19 2026). Fill, stroke colour and weight: Slides'
  // own toolbar menus, opened and picked from with synthetic clicks.
  const NATIVE = {
    rotL15: ['ArrowLeft', 'ArrowLeft', 37, { altKey: true }], rotR15: ['ArrowRight', 'ArrowRight', 39, { altKey: true }],
    rotL1: ['ArrowLeft', 'ArrowLeft', 37, { altKey: true, shiftKey: true }], rotR1: ['ArrowRight', 'ArrowRight', 39, { altKey: true, shiftKey: true }],
    scaleUp: ['k', 'KeyK', 75, SB.IS_MAC ? { metaKey: true, ctrlKey: true } : { ctrlKey: true, altKey: true }],
    scaleDown: ['j', 'KeyJ', 74, SB.IS_MAC ? { metaKey: true, ctrlKey: true } : { ctrlKey: true, altKey: true }],
  };
  function nativeCommand(act) {
    if (!topIdsOf(SB.readSelection()).length) { toast('Select something first'); return; }
    SB.focusTextbox();
    if (NATIVE[act]) keyCombo(...NATIVE[act]);
    else SB.pressArrange(act);
    scheduleRefresh(200);
  }
  function pressEl(n) {
    const r = n.getBoundingClientRect();
    const o = { bubbles: true, cancelable: true, view: window, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2, button: 0 };
    n.dispatchEvent(new MouseEvent('mouseover', o));
    n.dispatchEvent(new MouseEvent('mousedown', o));
    n.dispatchEvent(new MouseEvent('mouseup', o));
    n.dispatchEvent(new MouseEvent('click', o));
  }
  function openSlidesMenu() {
    return [...document.querySelectorAll('.goog-menu')].find((m) => m.getBoundingClientRect().width > 0 && getComputedStyle(m).display !== 'none' && getComputedStyle(m).visibility !== 'hidden');
  }
  function toolbarButton(id) {
    const b = document.getElementById(id);
    return b && b.getBoundingClientRect().width > 0 ? b : null;
  }
  const MENU_IDS = { fill: 'fillColorMenuButton', stroke: 'lineColorMenuButton', weight: 'lineWidthMenuButton' };
  function showSlidesMenu(which) {
    const b = toolbarButton(MENU_IDS[which]);
    if (!b) { toast(which === 'fill' ? 'Select a shape to change its fill' : 'Select a shape or line to change its stroke'); return; }
    pressEl(b);
  }
  async function pickFromMenu(which, test) {
    const b = toolbarButton(MENU_IDS[which]);
    if (!b) return false;
    pressEl(b);
    await sleep(220);
    const m = openSlidesMenu();
    const item = m && [...m.querySelectorAll('[aria-label], .goog-menuitem')].find(test);
    if (!item) { if (m) pressEl(b); return false; }
    pressEl(item.closest('.goog-menuitem') || item);
    SB.tick();
    await sleep(200);
    return true;
  }
  let lastStroke = null; // colour to bring back when stroke goes on again
  function selectionStroke() {
    const inv = pageInv() || [1, 0, 0, 1, 0, 0];
    let best = null;
    topIdsOf(SB.readSelection()).forEach((id) => (objectPaths(id, inv) || []).forEach((p) => { if (p.hasStroke && (!best || p.sw > best.sw)) best = p; }));
    return best;
  }
  // Several menu picks (stroke back on, then a weight) undo as one.
  async function asOne(name, fn) {
    SB.beginMacro(name);
    try { return await fn(); } finally { SB.endMacro(); }
  }
  async function strokeToggle() {
    const cur = selectionStroke();
    if (cur) {
      lastStroke = cur.stroke;
      if (!(await pickFromMenu('stroke', (n) => /^\s*Transparent\s*$/.test(n.textContent || '')))) toast('Couldn’t turn the stroke off here');
      return;
    }
    const want = (lastStroke || '').toLowerCase();
    const ok = (want && await pickFromMenu('stroke', (n) => (n.getAttribute('aria-label') || '').toLowerCase().includes(want)))
      || await pickFromMenu('stroke', (n) => (n.getAttribute('aria-label') || '') === 'black');
    if (!ok) toast('Select a shape or line to change its stroke');
  }
  async function strokeStep(dir) {
    const cur = selectionStroke();
    const px = cur ? cur.sw / 381 : 0;
    const W = SB.WEIGHTS;
    const w = dir > 0 ? (W.find((v) => v > px + 0.25) || W[W.length - 1]) : [...W].reverse().find((v) => v < px - 0.25);
    if (!w) { if (cur) await strokeToggle(); return; }
    if (!cur) await strokeToggle();
    if (!(await pickFromMenu('weight', (n) => (n.textContent || '').trim() === w + 'px'))) toast('Select a shape or line to change its stroke');
  }

  // Exact stroke weight. Slides' own weights go through its menu (one undo
  // step); anything else is written into the shapes' own data and pasted
  // back in place, which Slides renders exactly (3.5 px verified live on a
  // native preset, Nov 19 2026). 0 turns the stroke off.
  function setStrokeWeight(v) {
    const px = parseFloat(v);
    if (!Number.isFinite(px) || px < 0) return;
    if (px === 0) { if (selectionStroke()) strokeToggle(); return; }
    return run('stroke weight', async () => {
      const aligned = (SB.readSelection() || []).some((e) => e[0] === 3 && alignOf(e) !== 'center');
      if (aligned) {
        const sel0 = requireSelection();
        const out0 = sel0.map((e) => (e[0] === 3 && alignOf(e) !== 'center' ? bakeAlign(e, sel0, alignOf(e), px) || e : e));
        await replaceSelection(sel0, out0, { srcOf: {} });
        return;
      }
      if (SB.WEIGHTS.includes(px)) {
        if (!selectionStroke()) await strokeToggle();
        if (await pickFromMenu('weight', (n) => (n.textContent || '').trim() === px + 'px')) return;
      }
      const sel = requireSelection();
      const out = clone(sel);
      let n = 0;
      out.forEach((e) => {
        if (e[0] !== 3 || !Array.isArray(e[4])) return;
        const props = e[4];
        if (SB.getProp(props, 19) === undefined && SB.getProp(props, 18) !== 1) SB.setProp(props, 19, lastStroke || '#000000');
        if (SB.getProp(props, 18) !== undefined) { SB.setProp(props, 18, 1); SB.removeProp(props, 23); }
        SB.setProp(props, 22, Math.max(1, Math.round(px * 381)));
        n++;
      });
      if (!n) throw userError('Select a shape or line to change its stroke');
      await replaceSelection(sel, out, { srcOf: {} });
    });
  }

  // Every command, from the rail, a flyout or a shortcut.
  // Every command is noted as one change (see SB.beginMacro), so one-press
  // undo knows when a single-step Slides command (group, a menu pick) has
  // moved the slide on. Edit Shape and the palette note their own.
  const UNNOTED = new Set(['edit', 'pen', 'layers', 'palette', 'collapse', 'expand', 'toggleRail', 'themeBuilder']);
  function command(act) {
    if (busy && act !== 'layers') return;
    if (UNNOTED.has(act)) return commandNow(act);
    SB.beginMacro(act);
    let r;
    try { r = commandNow(act); } catch (err) { SB.endMacro(); throw err; }
    // Our own operations end when they finish; Slides' own keys land a
    // moment later, so give those time.
    if (r && typeof r.then === 'function') r.finally(() => SB.endMacro());
    else setTimeout(() => SB.endMacro(), 300);
    return r;
  }
  function commandNow(act) {
    switch (act) {
      case 'edit': return editShape('direct');
      case 'pen': return editShape('pen');
      case 'layers':
        // From the closed toolbar: open it, then the panel.
        if (collapsed) { setCollapsed(false); return togglePanel(true); }
        return togglePanel();
      case 'forward': case 'backward': case 'front': case 'back':
      case 'rotL15': case 'rotR15': case 'rotL1': case 'rotR1': case 'scaleUp': case 'scaleDown':
        return nativeCommand(act);
      case 'union': case 'subtract': case 'intersect': case 'exclude': return booleanOp(act);
      case 'group': case 'ungroup': return groupOp(act);
      case 'mask': return maskedPicture(SB.readSelection()) ? adjustMask() : maskOp();
      case 'outlineStroke': return outlineStrokeOp();
      case 'outlineText': return outlinedTextIn(SB.readSelection()) ? restoreTextOp() : outlineTextOp();
      case 'restoreText': return restoreTextOp();
      case 'alignLeft': case 'alignHCenter': case 'alignRight': case 'alignTop': case 'alignVMiddle': case 'alignBottom': return alignOp(act);
      case 'distH': return distributeOp('h');
      case 'distV': return distributeOp('v');
      case 'strokeCenter': return strokeAlignOp('center');
      case 'strokeInside': return strokeAlignOp('inside');
      case 'strokeOutside': return strokeAlignOp('outside');
      case 'palette': return openPalette();
      case 'fill': case 'fillColor': return showSlidesMenu('fill');
      case 'stroke': case 'strokeColor': return showSlidesMenu('stroke');
      case 'strokeToggle': return strokeToggle();
      case 'strokeThinner': return asOne('stroke', () => strokeStep(-1));
      case 'strokeThicker': return asOne('stroke', () => strokeStep(1));
      case 'collapse': return setCollapsed(true);
      case 'expand': return setCollapsed(false);
      case 'toggleRail': return setCollapsed(!collapsed);
      case 'themeBuilder': return toggleThemeBuilder();
      default: return undefined;
    }
  }
  // Slides already owns these keys; the rest are ours while shapes are selected.
  const SLIDES_KEYS = new Set(['rotL15', 'rotR15', 'rotL1', 'rotR1', 'scaleUp', 'scaleDown', 'forward', 'backward', 'front', 'back', 'group', 'ungroup']);

  // ── Toast (dark chip under the rail) ────────────────────────────────────
  let toastT = null;
  function toast(msg, ms = 4000) {
    if (!hint) return;
    hint.textContent = msg;
    const r = rail.getBoundingClientRect();
    hint.style.top = Math.min(innerHeight - 40, r.bottom + 8) + 'px';
    hint.style.left = r.left + 'px';
    hint.classList.add('show');
    clearTimeout(toastT);
    toastT = setTimeout(() => hint.classList.remove('show'), ms);
  }
  function toastNotes() {
    if (notes.size) toast([...notes].join(' · '), 6000);
  }

  // ── Icons for the Layers panel (the rail's come from rail-kit.js) ───────
  function icon(parts) {
    const s = sv('svg', { viewBox: '0 0 20 20', 'aria-hidden': 'true' });
    parts.forEach(([d, extra]) => s.append(sv('path', Object.assign({ d, fill: 'currentColor' }, extra || {}))));
    return s;
  }
  const I = {
    eye: icon([['M10 5c-3.6 0-6.4 2.3-7.5 5 1.1 2.7 3.9 5 7.5 5s6.4-2.3 7.5-5c-1.1-2.7-3.9-5-7.5-5Zm0 8.3A3.3 3.3 0 1 1 10 6.7a3.3 3.3 0 0 1 0 6.6Zm0-5a1.7 1.7 0 1 0 0 3.4 1.7 1.7 0 0 0 0-3.4Z']]),
    eyeOff: icon([['M3.3 2.2 2.2 3.3l2.4 2.4C3.7 6.6 3 7.7 2.5 9c1.1 2.7 3.9 5 7.5 5 1.2 0 2.3-.3 3.3-.7l2.4 2.4 1.1-1.1ZM10 12.3a3.3 3.3 0 0 1-3.3-3.3c0-.5.1-1 .3-1.4l4.4 4.4c-.4.2-.9.3-1.4.3Zm7.5-3.3c-1.1-2.7-3.9-5-7.5-5-1 0-1.9.2-2.8.5l1.4 1.4c.4-.1.9-.2 1.4-.2a3.3 3.3 0 0 1 3.3 3.3c0 .5-.1 1-.2 1.4l2.1 2.1c.9-.9 1.7-2 2.3-3.5Z']]),
    kShape: icon([['M4 4h12v12H4Z', { fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5' }]]),
    kText: icon([['M5 4h10v2.5h-1.5v-1h-2.75V15H12.5v1.5h-5V15h1.75V5.5H6.5v1H5Z']]),
    kTheme: icon([['M3 3h14v14H3Zm1.5 1.5v11h11v-11Z', { 'fill-rule': 'evenodd' }], ['M6 13V7h1.6l2.4 3 2.4-3H14v6h-1.5V9.3L10 12.3 7.5 9.3V13Z']]),
    kGroup: icon([['M3 3h8v8H3Zm1.5 1.5v5h5v-5ZM9 9h8v8H9Zm1.5 1.5v5h5v-5Z', { 'fill-rule': 'evenodd' }]]),
    kImage: icon([['M3 4h14v12H3Zm1.5 1.5v7.4l3-3 2.5 2.5 2-2 3.5 3.5V5.5ZM13 7a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3Z', { 'fill-rule': 'evenodd' }]]),
    kLine: icon([['M4.5 16.5 3.5 15.5 15.5 3.5l1 1Z']]),
  };
  const ic = (k) => I[k].cloneNode(true);

  // ── Rail ────────────────────────────────────────────────────────────────
  let host = null, root = null, rail = null, hint = null, tip = null, panel = null, list = null, rk = null;
  let collapsed = true; // closed until opened from the svgslid.es button
  const L_PAL = SB.SHORTCUT_LABEL.toggleRail + ' · ' + SB.SHORTCUT_LABEL.palette + ' for commands';
  function logoNode() {
    try {
      if (chrome.runtime && chrome.runtime.getURL) return el('img', { src: chrome.runtime.getURL('icons/icon48.png'), alt: '' });
    } catch { /* not in the extension */ }
    return RK.icon('logo');
  }
  const CSS = `
    :host { all: initial; }
    ${RK.CSS}
    .rail { z-index: 3; }
    .hint { position: fixed; z-index: 2147482999; pointer-events: none; background: ${GM.tooltip}; color: ${GM.onTooltip};
            font: 400 12px/16px ${FONT}; padding: 6px 10px; border-radius: 4px; max-width: 320px; opacity: 0; transition: opacity .2s; }
    .hint.show { opacity: .95; }
    .madj { position: fixed; inset: 0; width: 100vw; height: 100vh; z-index: 1; outline: none; cursor: default; }
    .madj .pic { cursor: move; }
    .madj .edge { fill: none; stroke: #1a73e8; stroke-width: 1.5; vector-effect: non-scaling-stroke; pointer-events: none; }
    .madj .frame { fill: none; stroke: #1a73e8; stroke-width: 1; stroke-dasharray: 4 3; vector-effect: non-scaling-stroke; pointer-events: none; }
    .madj .h { fill: #fff; stroke: #1a73e8; stroke-width: 1.5; cursor: nwse-resize; }
    .madj .h[data-h="1"], .madj .h[data-h="3"] { cursor: nesw-resize; }
    .apill { position: fixed; z-index: 2; display: flex; align-items: center; gap: 10px; height: 30px; padding: 0 8px 0 12px; transform: translateX(-50%);
             background: #303134; color: #f2f2f2; border-radius: 15px; font: 500 12px/16px ${FONT}; box-shadow: 0 1px 3px rgba(0,0,0,.3); white-space: nowrap; }
    .apill .seg { display: flex; align-items: center; gap: 6px; }
    .apill .seg + .seg { border-left: 1px solid rgba(255,255,255,.25); padding-left: 10px; }
    .apill .lb, .apill .u { opacity: .7; }
    .apill input { width: 44px; height: 20px; box-sizing: border-box; border: 0; border-radius: 4px; padding: 0 4px; background: rgba(255,255,255,.12); color: inherit; font: inherit; text-align: right; }
    .apill input::-webkit-inner-spin-button, .apill input::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
    .apill input:focus { outline: 1px solid #a8c7fa; background: rgba(255,255,255,.18); }
    .apill .tx { border: 0; background: rgba(255,255,255,.14); color: inherit; font: inherit; height: 22px; padding: 0 10px; border-radius: 11px; cursor: pointer; }
    .apill .tx:hover { background: rgba(255,255,255,.26); }
    .apill .pb { width: 22px; height: 22px; border-radius: 50%; border: 0; padding: 0; display: grid; place-items: center; cursor: pointer; background: rgba(255,255,255,.14); color: #f2f2f2; }
    .apill .pb svg { width: 14px; height: 14px; display: block; }
    .apill .pb:hover { background: rgba(255,255,255,.26); }
    .apill .pb.ok { background: #a8c7fa; color: #062e6f; }
    .panel { position: fixed; z-index: 2; display: none; flex-direction: column; width: 248px; box-sizing: border-box;
             background: #fff; border-radius: 12px; box-shadow: ${GM.elev2}; font: 400 13px/1 ${FONT}; color: #1f1f1f;
             user-select: none; overflow: hidden; }
    .panel.show { display: flex; }
    .panel.dock { border-radius: 0; box-shadow: 1px 0 0 #dadce0, 4px 0 8px rgba(60,64,67,.08); }
    .ph { display: flex; align-items: center; justify-content: space-between; height: 40px; padding: 0 8px 0 14px;
          font: 500 14px/1 ${FONT}; border-bottom: 1px solid #e3e3e3; flex: none; }
    .ph .count { font-weight: 400; color: #5e5e5e; font-size: 12px; margin-left: 6px; }
    .list { overflow-y: auto; padding: 4px 0; flex: 1; position: relative; }
    .row { display: flex; align-items: center; gap: 8px; height: 30px; padding: 0 6px 0 12px; cursor: default; position: relative; }
    .row:hover { background: #f1f3f4; }
    .row.sel { background: ${GM.selected}; }
    .row.hid .nm, .row.hid .kd { opacity: .45; }
    .row .kd { width: 16px; height: 16px; color: #5e5e5e; flex: none; }
    .row { gap: 6px; }
    .row .tw { width: 16px; height: 16px; flex: none; display: flex; align-items: center; justify-content: center; border-radius: 4px; color: #5e5e5e; transition: transform .12s; }
    .row .tw.open { transform: rotate(90deg); }
    .row .tw.none { visibility: hidden; }
    .row .tw:hover { background: ${GM.hover}; }
    .row .tw svg { width: 14px; height: 14px; display: block; }
    .row.child .nm { color: #1f1f1f; }
    .row.theme .kd, .row.theme .nm, .row.theme .tw { opacity: .45; }
    .row.armed { background: #fef7e0; box-shadow: inset 3px 0 0 #f9ab00; }
    .row.armed .nm { opacity: 1 !important; color: #7a4f01; font-weight: 500; }
    .row.armed .eye, .row.armed .th { display: none; }
    .row.theme { cursor: pointer; }
    .hov { position: fixed; z-index: 3; pointer-events: none; border: 1.5px solid ${ACCENT}; border-radius: 2px; display: none; box-sizing: border-box; }
    .hov.theme { border-color: #f9ab00; border-style: dashed; background: rgba(249,171,0,.06); }
    .hov.armed { border-style: solid; background: rgba(249,171,0,.14); }
    .hov .lb { position: absolute; left: -1.5px; top: -22px; white-space: nowrap; font: 500 11px/20px ${FONT}; padding: 0 6px; border-radius: 3px; color: #fff; background: ${ACCENT}; }
    .hov.theme .lb { background: #b06000; }
    .row .th { width: 16px; height: 16px; flex: none; color: #5e5e5e; opacity: .8; }
    .row .th svg { width: 16px; height: 16px; display: block; }
    .row .kd svg { width: 16px; height: 16px; display: block; }
    .row .nm { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .row .nm.auto { color: #444746; }
    .row .eye { width: 24px; height: 24px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
                color: #5e5e5e; visibility: hidden; flex: none; cursor: pointer; }
    .row .eye svg { width: 16px; height: 16px; }
    .row:hover .eye, .row.hid .eye { visibility: visible; }
    .row .eye:hover { background: ${GM.hover}; }
    .row input { flex: 1; min-width: 0; height: 22px; box-sizing: border-box; border: 1px solid ${ACCENT}; border-radius: 4px;
                 padding: 0 6px; font: 400 13px/1 ${FONT}; color: #1f1f1f; outline: none; }
    .row.drag { opacity: .5; }
    .drop { position: absolute; left: 8px; right: 8px; height: 2px; background: ${ACCENT}; border-radius: 1px; pointer-events: none; display: none; }
    .empty { padding: 16px 14px; color: #5e5e5e; line-height: 18px; }
    .foot { padding: 8px 14px 10px; color: #5e5e5e; font-size: 11px; line-height: 15px; border-top: 1px solid #e3e3e3; flex: none; }`;

  function build() {
    host = document.createElement('div');
    host.id = 'svg2slides-shape-tools';
    root = host.attachShadow({ mode: 'open' });
    const style = document.createElement('style');
    style.textContent = CSS;
    hint = el('div', { class: 'hint', role: 'status' });
    list = el('div', { class: 'list' });
    const count = el('span', { class: 'count' });
    panel = el('div', { class: 'panel', role: 'dialog', 'aria-label': 'Layers' },
      el('div', { class: 'ph' }, el('span', {}, 'Layers', count), el('div', { class: 'btn', role: 'button', 'data-act': 'closepanel', 'aria-label': 'Close layers', 'data-tip': 'Close layers (back to slides)' },
        icon([['M6.06 15 5 13.94 8.94 10 5 6.06 6.06 5 10 8.94 13.94 5 15 6.06 11.06 10 15 13.94 13.94 15 10 11.06Z']]))),
      list,
      el('div', { class: 'foot' }, 'Top of the list is the front. Drag to restack, double-click to rename. Names and hiding stay on this computer.'));
    panel._count = count;
    root.append(style);
    // The svgslid.es button opens and closes the toolbar from one spot: it
    // is the whole toolbar when closed and the first button when open.
    rk = RK.mountRail(root, [
      [{ act: 'toggleRail', tip: 'Hide the toolbar', key: SB.SHORTCUT_LABEL.toggleRail, cls: 'keep logo', node: logoNode() }, { act: 'layers', tip: 'Layers panel', key: SB.SHORTCUT_LABEL.layers },
        { act: 'edit', tip: 'Edit Shape (double-click a shape)' }, { act: 'pen', tip: 'Pen: draw a shape anywhere', key: SB.SHORTCUT_LABEL.pen }, { act: 'palette', tip: 'Commands', key: SB.SHORTCUT_LABEL.palette }],
    ], [], (act) => command(act), {
      label: 'Shape tools', onEnter: () => refreshSelection(),
      onField: (act, v, how) => { if (act === 'weight' && how.commit) setStrokeWeight(v); },
      onFieldBlur: () => SB.focusTextbox(),
    });
    rail = rk.rail;
    tip = rk.tip;
    root.append(panel, hint);
    rk.attachTips(panel, 'right');

    panel.addEventListener('mousedown', (e) => { if (e.target.tagName !== 'INPUT') e.preventDefault(); e.stopPropagation(); });
    panel.addEventListener('pointerdown', (e) => {
      e.stopPropagation();
      if (e.target.closest('[data-act="closepanel"]')) { e.preventDefault(); togglePanel(false); }
    });
    panel.addEventListener('keydown', (e) => e.stopPropagation());
    panel.addEventListener('keyup', (e) => e.stopPropagation());
    document.documentElement.appendChild(host);
    scheduleIdle(3000);
  }

  function scheduleIdle(ms) { if (rk) rk.scheduleIdle(ms); }

  function setCollapsed(v, persist = true) {
    collapsed = v;
    rail.classList.toggle('min', v);
    rk.setTip('toggleRail', v ? 'SVG to Slides tools' : 'Hide the toolbar', v ? L_PAL : SB.SHORTCUT_LABEL.toggleRail);
    if (v) { togglePanel(false); rk.closeFly(); }
    if (persist) { try { chrome.storage.local.set({ shapeToolsCollapsed: v }); } catch { /* storage unavailable */ } }
    place();
  }

  function place() {
    if (!rail) return;
    const r = SB.visibleWorkspaceRect();
    const editorOpen = (self.SVG2S_EDIT && self.SVG2S_EDIT.isOpen()) || document.getElementById('svg2slides-editor');
    const show = !editorOpen && !document.fullscreenElement && r.right - r.left > 240 && r.bottom - r.top > 200 && !!SB.currentPageGroup();
    host.style.display = show ? '' : 'none';
    if (!show) return;
    // The Layers panel docks where Figma keeps it: the left column, over
    // Slides' filmstrip (close it to get the slides back). With the
    // filmstrip hidden it docks at the canvas's left edge instead.
    let rr = r;
    if (panel.classList.contains('show')) {
      const fs = document.querySelector('.filmstrip') || document.getElementById('filmstrip');
      const fr = fs && fs.getBoundingClientRect();
      panel.classList.add('dock');
      if (fr && fr.width >= 150 && fr.height > 200) {
        Object.assign(panel.style, { left: fr.left + 'px', top: fr.top + 'px', width: fr.width + 'px', height: fr.height + 'px', maxHeight: '' });
      } else {
        Object.assign(panel.style, { left: r.left + 'px', top: r.top + 'px', width: '248px', height: (r.bottom - r.top) + 'px', maxHeight: '' });
        rr = Object.assign({}, r, { left: r.left + 248 });
      }
    }
    // Same left and top as the editor's rail, so opening Edit Shape swaps
    // tools in place instead of jumping.
    rk.place(rr);
  }

  // Dim tools that can't apply to the current selection. Read on demand
  // only (hovering the rail, a click or key in Slides while it's visible):
  // the synthetic copy never touches the OS clipboard (verified live).
  let lastSel = [];
  let refreshT = null;
  function scheduleRefresh(ms = 200) {
    clearTimeout(refreshT);
    refreshT = setTimeout(refreshSelection, ms);
  }
  function refreshSelection() {
    if (!rail || host.style.display === 'none' || busy) return;
    const sel = SB.readSelection();
    const ids = topIdsOf(sel);
    lastSel = ids;
    const single = ids.length === 1 && sel ? entryById(sel, ids[0]) : null;
    const isGroup = !!single && single[0] === 2;
    const multi = ids.length >= 2 || (isGroup && (single[2] || []).length >= 2);
    const set = (act, on) => rk.setDim(act, !on);
    const shp = (sel || []).filter((x) => x[0] === 3);
    const inv = pageInv() || [1, 0, 0, 1, 0, 0];
    const paths = ids.flatMap((id) => objectPaths(id, inv) || []);
    set('edit', shp.length > 0 && shp.every((x) => SB.isEditableShape(x) || SB.convertibleKind(sel, x)));
    set('group', ids.length >= 2);
    set('ungroup', isGroup);
    const masked = maskedPicture(sel);
    set('mask', !!masked || (ids.length === 2 && ids.some((id) => pictureOf(sel, id))));
    rk.setIcon('mask', masked ? 'maskAdjust' : 'mask');
    rk.setTip('mask', masked ? 'Adjust the picture under its mask (or double-click it)' : 'Mask image with shape (the shape on top cuts out the picture under it)', SB.SHORTCUT_LABEL.mask);
    Object.keys(OP_LABEL).forEach((op) => set(op, multi));
    set('combine', multi || ids.length >= 2 || isGroup);
    set('outlineStroke', paths.some((p) => p.hasStroke));
    const outlined = outlinedTextIn(sel);
    set('outlineText', !!outlined || ids.some((id) => hasRenderedText(id)));
    rk.setIcon('outlineText', outlined ? 'restoreText' : 'outlineText');
    rk.setTip('outlineText', outlined ? 'Restore text' + (outlined.rec.label ? ': “' + outlined.rec.label + '”' : '') : 'Outline text', SB.SHORTCUT_LABEL.outlineText);
    const firstShape = (sel || []).find((x) => x[0] === 3);
    rk.setIcon('strokeAlign', { center: 'strokeCenter', inside: 'strokeInside', outside: 'strokeOutside' }[firstShape ? alignOf(firstShape) : 'center']);
    set('outline', paths.some((p) => p.hasStroke) || ids.some((id) => hasRenderedText(id)));
    ['arrange', 'forward', 'backward', 'front', 'back'].forEach((a2) => set(a2, ids.length > 0));
    const fillBtn = !!toolbarButton(MENU_IDS.fill), strokeBtn = !!toolbarButton(MENU_IDS.stroke);
    set('fill', fillBtn);
    ['stroke', 'strokeColor', 'strokeToggle', 'strokeThinner', 'strokeThicker', 'strokeAlign'].forEach((a2) => set(a2, strokeBtn));
    set('align', ids.length > 0);
    ['distH', 'distV'].forEach((a2) => set(a2, ids.length >= 3));
    const fp = paths.find((p) => p.hasFill), sp = paths.find((p) => p.hasStroke);
    rk.setSwatch('fill', fp ? fp.fill : null);
    rk.setSwatch('stroke', sp ? sp.stroke : null);
    set('weight', ids.length > 0);
    const wts = [...new Set(paths.filter((q) => q.hasStroke).map((q) => Math.round(q.sw / 381 * 100) / 100))];
    rk.setField('weight', !ids.length ? '' : !wts.length ? 0 : wts.length === 1 ? wts[0] : null);
    if (panel.classList.contains('show')) markSelectedRows();
  }

  // ── Layers panel ────────────────────────────────────────────────────────
  const presId = (location.pathname.match(/\/presentation\/d\/([^/]+)/) || [])[1] || 'deck';
  let names = {};
  let layersAtStart = false;
  const hidden = new Map(); // id → previous visibility
  try {
    chrome.storage.local.get(['layerNames', 'shapeToolsCollapsed', 'layersOpen'], (v) => {
      names = (v && v.layerNames && v.layerNames[presId]) || {};
      if (v && v.layersOpen) { if (panel) togglePanel(true); else layersAtStart = true; }
      else if (v && v.shapeToolsCollapsed === false) { collapsed = false; if (rail) setCollapsed(false, false); }
      if (panel && panel.classList.contains('show')) renderList();
    });
  } catch { /* storage unavailable */ }
  function saveName(id, name) {
    if (name) names[id] = name; else delete names[id];
    try {
      chrome.storage.local.get('layerNames', (v) => {
        const all = (v && v.layerNames) || {};
        all[presId] = names;
        chrome.storage.local.set({ layerNames: all });
      });
    } catch { /* storage unavailable */ }
  }

  function describe(id) {
    const g = SB.elementFor(id);
    if (!g) return { kind: 'kShape', label: 'Shape' };
    const nested = [...g.querySelectorAll('g[id^="editor-"]')].filter((c) => !/-paragraph|-bg$/.test(c.id) && c.parentNode.closest('g[id^="editor-"]') === g);
    if (nested.length) return { kind: 'kGroup', label: `Group of ${nested.length}` };
    if (g.querySelector('image')) return { kind: 'kImage', label: 'Image' };
    const txt = textElements(id).map((t) => t.textContent).join(' ').replace(/\s+/g, ' ').trim();
    if (txt) return { kind: 'kText', label: txt.length > 40 ? txt.slice(0, 40) + '…' : txt };
    const paths = [...g.querySelectorAll('path')].filter((p) => {
      const cs = getComputedStyle(p);
      return hex(cs.fill) && parseFloat(cs.fillOpacity) !== 0;
    });
    if (!paths.length && g.querySelector('path')) return { kind: 'kLine', label: 'Line' };
    return { kind: 'kShape', label: 'Shape' };
  }

  function togglePanel(force) {
    const on = force === undefined ? !panel.classList.contains('show') : force;
    panel.classList.toggle('show', on);

    if (on) { renderList(); place(); observePage(); refreshSelection(); }
    else { unobservePage(); place(); }
    rk.setOn('layers', on);
    try { chrome.storage.local.set({ layersOpen: on }); } catch { /* storage unavailable */ }
  }

  let renderedFor = null;
  // Groups open and close like an accordion; open ones are remembered for
  // this page view. Children are listed front first, indented.
  const expanded = new Set();
  let lastModel = '';
  function ancestorsOf(id) {
    const out = [];
    let g = SB.elementFor(id);
    const page = SB.currentPageGroup();
    for (let p = g && g.parentNode && g.parentNode.closest('g[id^="editor-"]'); p && p !== page; p = p.parentNode && p.parentNode.closest('g[id^="editor-"]')) {
      if (!/-paragraph|-bg$/.test(p.id)) out.unshift(p.id.slice('editor-'.length));
    }
    return out;
  }
  function renderList(force) {
    if (renaming) return; // don't pull the name field out from under typing
    const page = SB.currentPageGroup();
    renderedFor = page;
    const order = SB.topLevelOrder().slice().reverse(); // front first
    const model = [];
    const walk = (id, depth) => {
      const d = describe(id);
      const kids = d.kind === 'kGroup' ? childOrder(id).slice().reverse() : [];
      const open = kids.length > 0 && expanded.has(id);
      model.push({ id, depth, kind: d.kind, label: names[id] || d.label, custom: !!names[id], hid: hidden.has(id), group: kids.length > 0, open });
      if (open) kids.forEach((k) => walk(k, depth + 1));
    };
    order.forEach((id) => walk(id, 0));
    model.forEach((r) => { r.theme = isThemeObject(r.id); });
    if (!themeKnown()) setTimeout(() => probeTheme(), 0);
    // Slides redraws text all the time; only rebuild when the list changes.
    const sig = JSON.stringify(model);
    if (!force && sig === lastModel && list.querySelector('.row, .empty')) { markSelectedRows(); return; }
    lastModel = sig;
    panel._count.textContent = order.length ? String(order.length) : '';
    const rows = model.map((r) => {
      const row = el('div', { class: 'row' + (r.depth ? ' child' : '') + (r.hid ? ' hid' : '') + (r.theme ? ' theme' : ''), 'data-id': r.id, 'data-depth': String(r.depth),
        'data-tip': r.theme ? 'Part of the theme (layout or master): changes here won’t stick. Click twice to edit it in the theme builder.' : undefined },
        el('span', { class: 'tw' + (r.group ? '' : ' none') + (r.open ? ' open' : ''), role: r.group ? 'button' : 'presentation',
          'aria-label': r.open ? 'Close group' : 'Open group', 'data-tip': r.group ? (r.open ? 'Close group' : 'Show what’s in the group') : undefined }, r.group ? RK.icon('caret') : ''),
        el('span', { class: 'kd' }, ic(r.kind)),
        el('span', { class: 'nm' + (r.custom ? '' : ' auto') }, r.label),
        ...(r.theme && !r.depth ? [el('span', { class: 'th' }, ic('kTheme'))] : []),
        el('span', { class: 'eye', role: 'button', 'aria-label': 'Hide while you work', 'data-tip': r.hid ? 'Show' : "Hide while you work (doesn't change the slide)" }, ic(r.hid ? 'eyeOff' : 'eye')));
      row.style.paddingLeft = (4 + r.depth * 16) + 'px';
      return row;
    });
    const drop = el('div', { class: 'drop' });
    list.replaceChildren(...(rows.length ? rows : [el('div', { class: 'empty' }, 'Nothing on this slide yet.')]), drop);
    list._drop = drop;
    markSelectedRows();
    if (ask && Date.now() < ask.until) showArmed(ask);
  }
  function markSelectedRows() {
    // Something picked inside a group: open the groups around it.
    let opened = false;
    lastSel.forEach((id) => {
      if (list.querySelector(`.row[data-id="${id}"]`)) return;
      ancestorsOf(id).forEach((a) => { if (!expanded.has(a)) { expanded.add(a); opened = true; } });
    });
    if (opened) { renderList(true); return; }
    list.querySelectorAll('.row').forEach((r) => r.classList.toggle('sel', lastSel.includes(r.dataset.id)));
  }

  // Hidden through a stylesheet, not the element's own style: Slides
  // redraws objects (text especially, on every selection change) and its
  // text sets its own visibility, which beat an inline style on the group.
  function setHidden(id, hide) {
    if (hide) hidden.set(id, true); else hidden.delete(id);
    let st = document.getElementById('svg2slides-hidden');
    if (!st) { st = document.createElement('style'); st.id = 'svg2slides-hidden'; document.documentElement.appendChild(st); }
    st.textContent = [...hidden.keys()].map((h) => {
      const a = `[id="editor-${h}"]`, b = `[id^="editor-${h}-"]`;
      return `${a}, ${a} *, ${b}, ${b} * { visibility: hidden !important; }`;
    }).join('\n');
  }
  function restoreAllHidden() {
    [...hidden.keys()].forEach((id) => setHidden(id, false));
  }

  let pageObs = null, pagePoll = null;
  function observePage() {
    unobservePage();
    const page = SB.currentPageGroup();
    let t = null;
    const later = () => { clearTimeout(t); t = setTimeout(() => { if (!dragging && !renaming) renderList(); }, 250); };
    if (page) {
      pageObs = new MutationObserver((muts) => {
        // Objects only: Slides redraws text paragraphs constantly.
        if (muts.some((m) => [...m.addedNodes, ...m.removedNodes].some((n) => n.nodeType === 1 && /^editor-[^-]+$/.test(n.id || '')))) later();
      });
      pageObs.observe(page, { childList: true, subtree: true });
    }
    // Slide changes swap the page group.
    pagePoll = setInterval(() => {
      if (SB.currentPageGroup() !== renderedFor) {
        restoreAllHidden();
        observePage();
        renderList();
      }
    }, 700);
  }
  function unobservePage() {
    if (pageObs) pageObs.disconnect();
    pageObs = null;
    clearInterval(pagePoll);
    pagePoll = null;
  }

  // Rows: click selects (⇧ adds), drag restacks, double-click renames.
  let dragging = null, renaming = false, clickT = null, lastUp = null;
  function rowsNow() { return [...list.querySelectorAll('.row[data-depth="0"]')]; }

  function onListDown(e) {
    const row = e.target.closest('.row');
    if (!row || renaming || busy) return;
    if (e.target.closest('.tw') && !e.target.closest('.tw.none')) {
      e.preventDefault();
      const id = row.dataset.id;
      if (expanded.has(id)) expanded.delete(id); else expanded.add(id);
      renderList(true);
      return;
    }
    if (e.target.closest('.eye')) {
      e.preventDefault();
      const id = row.dataset.id;
      setHidden(id, !hidden.has(id));
      renderList();
      return;
    }
    if (e.target.tagName === 'INPUT') return;
    e.preventDefault();
    const id = row.dataset.id;
    const start = { x: e.clientX, y: e.clientY };
    const shift = e.shiftKey;
    const move = (ev) => {
      if (!dragging && row.dataset.depth === '0' && Math.abs(ev.clientY - start.y) > 4) {
        dragging = { id, row };
        row.classList.add('drag');
      }
      if (dragging) dropAt(ev.clientY);
    };
    const up = async (ev) => {
      window.removeEventListener('pointermove', move, true);
      window.removeEventListener('pointerup', up, true);
      if (dragging) {
        const target = dropAt(ev.clientY);
        list._drop.style.display = 'none';
        row.classList.remove('drag');
        const d = dragging;
        dragging = null;
        if (target !== null) await restack(d.id, target);
        return;
      }
      // The second click of a double-click: the dblclick that follows
      // renames. (Pointer events carry no click count, so time it.)
      const now = Date.now();
      if (lastUp && lastUp.id === id && now - lastUp.t < 450) { lastUp = null; return; }
      lastUp = { id, t: now };
      // Select right away; the row shows it before Slides does.
      if (!row.classList.contains('theme')) {
        if (!shift) list.querySelectorAll('.row.sel').forEach((r) => r.classList.remove('sel'));
        row.classList.add('sel');
      }
      select(id, shift);
    };
    window.addEventListener('pointermove', move, true);
    window.addEventListener('pointerup', up, true);
  }

  // Where a dragged row would land; returns the target stacking index
  // (0 = back) or null.
  function dropAt(clientY) {
    const rows = rowsNow();
    if (!rows.length) return null;
    let slot = rows.length; // list position (0 = front)
    for (let i = 0; i < rows.length; i++) {
      const r = rows[i].getBoundingClientRect();
      if (clientY < r.top + r.height / 2) { slot = i; break; }
    }
    const lr = list.getBoundingClientRect();
    const ref = slot < rows.length ? rows[slot].getBoundingClientRect().top : rows[rows.length - 1].getBoundingClientRect().bottom;
    list._drop.style.top = (ref - lr.top + list.scrollTop - 1) + 'px';
    list._drop.style.display = 'block';
    const from = rows.findIndex((r) => r.dataset.id === (dragging && dragging.id));
    let listIdx = slot > from ? slot - 1 : slot; // position after removal
    const n = rows.length;
    return n - 1 - listIdx; // list is front-first; stacking index is back-first
  }

  async function select(id, add) {
    // Sort theme objects first if this slide hasn't been checked yet (or
    // has objects the last check didn't see).
    if (!themeKnown()) await probeTheme();
    const themeMsg = 'This is part of the theme, so changes made here won’t stick. Click again to edit it in the theme builder.';
    if (isThemeObject(id)) {
      if (askTwice('theme', id, themeMsg)) openThemeBuilder(id);
      return;
    }
    const size = await screenSizeSettled(id);
    if (size !== null && size < 6) {
      if (!askTwice('small', id, 'Too small to pick at this zoom. Click again to zoom in on it.')) return;
      busy = true;
      try { await zoomTo(id); } finally { busy = false; }
    }
    busy = true;
    let ok = false;
    try {
      let base = lastSel;
      if (add) { await outOfText(); const cur = topIdsOf(SB.readSelection()); if (cur.length) base = cur; }
      const ids = add ? [...new Set([...base, id])] : [id];
      ok = await selectIds(ids);
    } finally {
      busy = false;
      refreshSelection();
    }
    if (ok || add) return;
    // Slides wouldn't select it. That alone doesn't make it a theme object
    // (a select can fail for other reasons): check the slide again, and
    // only call it theme if Select all leaves it out.
    const page = SB.currentPageGroup();
    if (page) themeCache.delete(page.id);
    await probeTheme();
    renderList(true);
    if (isThemeObject(id)) { if (askTwice('theme', id, themeMsg)) openThemeBuilder(id); }
    else toast('Couldn’t select that one. Try clicking it on the slide.');
  }

  async function restack(id, target) {
    busy = true;
    SB.beginMacro('restack');
    try {
      if (!(await selectIds([id]))) { toast('Couldn’t select that object to move it.'); return; }
      if (!(await frozenWhile(null, () => SB.moveToIndex(id, target)))) toast('Couldn’t move it all the way. Try Arrange in the menu.');
    } finally {
      SB.endMacro();
      busy = false;
      SB.focusTextbox();
      renderList();
      refreshSelection();
    }
  }

  // Rename in place. Slides listens for keys on the whole page (and pulls
  // focus back to its own text frame), so while the name field is open the
  // keyboard is held for it at the window: typing goes into the field, ↵
  // keeps the name, Esc drops it, and a click anywhere else keeps it.
  function onListDbl(e) {
    const row = e.target.closest('.row');
    if (!row || e.target.closest('.eye') || e.target.closest('.tw') || renaming) return;
    clearTimeout(clickT);
    clickT = null;
    const id = row.dataset.id;
    const nm = row.querySelector('.nm');
    if (!nm) return;
    const input = el('input', { type: 'text', 'aria-label': 'Layer name', value: names[id] || '' });
    input.placeholder = describe(id).label;
    renaming = true;
    nm.replaceWith(input);
    const grab = () => { if (root.activeElement !== input) { input.focus({ preventScroll: true }); } };
    grab();
    input.select();
    const refocus = setInterval(() => { if (!done) grab(); }, 120);
    let done = false;
    // Never stuck: a minute without a key ends it, keeping what's typed.
    let idle = setTimeout(() => finish(true), 60000);
    const inField = (ev) => ev.composedPath().includes(input);
    const onKey = (ev) => {
      if (!ev.isTrusted) return; // our own key presses to Slides
      if (!inField(ev) && !(ev.type === 'keydown' && (ev.key === 'Enter' || ev.key === 'Escape'))) {
        // A key meant for the field that landed elsewhere (Slides took
        // focus): send focus back; this key is lost, the next one lands.
        if (ev.type === 'keydown' && !ev.metaKey && !ev.ctrlKey) { ev.preventDefault(); grab(); }
        ev.stopPropagation();
        return;
      }
      ev.stopPropagation(); // nothing of Slides' (or ours) sees it
      if (ev.type !== 'keydown') return;
      clearTimeout(idle); idle = setTimeout(() => finish(true), 60000);
      if (ev.key === 'Enter') { ev.preventDefault(); finish(true); }
      else if (ev.key === 'Escape') { ev.preventDefault(); finish(false); }
    };
    // Only a real click ends it (our own selecting clicks the slide too).
    const onDown = (ev) => { if (ev.isTrusted && !inField(ev)) finish(true); };
    const KEYS = ['keydown', 'keypress', 'keyup', 'beforeinput', 'input'];
    KEYS.forEach((t) => window.addEventListener(t, onKey, true));
    window.addEventListener('pointerdown', onDown, true);
    const ifr = SB.iframe();
    let idoc = null;
    try { idoc = ifr && ifr.contentDocument; } catch { idoc = null; }
    if (idoc) { KEYS.forEach((t) => idoc.addEventListener(t, onKey, true)); idoc.addEventListener('pointerdown', onDown, true); }
    const finish = (keep) => {
      if (done) return;
      done = true;
      clearInterval(refocus);
      clearTimeout(idle);
      KEYS.forEach((t) => window.removeEventListener(t, onKey, true));
      window.removeEventListener('pointerdown', onDown, true);
      if (idoc) { KEYS.forEach((t) => idoc.removeEventListener(t, onKey, true)); idoc.removeEventListener('pointerdown', onDown, true); }
      renaming = false;
      if (keep) saveName(id, input.value.trim());
      renderList(true);
      SB.focusTextbox();
    };
    input.addEventListener('blur', () => setTimeout(() => {
      // Focus went somewhere on purpose (a click elsewhere ends it through
      // pointerdown); a blur with no click is Slides taking focus.
      if (!done && root.activeElement !== input) grab();
    }, 0));
  }

  // ── Wiring ──────────────────────────────────────────────────────────────
  function init() {
    if (host) return;
    if (!SB.currentPageGroup()) return;
    build();
    setCollapsed(collapsed, false);
    if (layersAtStart && !collapsed) togglePanel(true);
    list.addEventListener('pointerdown', onListDown);
    list.addEventListener('dblclick', onListDbl);
    place();
    window.addEventListener('resize', place);
    setInterval(place, 1000);
    // Keep the dimmed states honest after the user changes the selection.
    document.addEventListener('mouseup', (e) => {
      if (!e.isTrusted || (host && host.contains(e.target))) return;
      if (rail.classList.contains('min') && !panel.classList.contains('show')) return;
      scheduleRefresh(180);
    }, true);
    const hookIframe = () => {
      const ifr = SB.iframe();
      let doc = null;
      try { doc = ifr && ifr.contentDocument; } catch { doc = null; }
      if (!doc || doc.__svg2slidesShapeTools) return;
      doc.__svg2slidesShapeTools = true;
      doc.addEventListener('keyup', (e) => {
        if (!e.isTrusted || !panel.classList.contains('show')) return;
        scheduleRefresh(250);
      }, true);
      doc.addEventListener('paste', onPasteSvg, true);
      // Shape tools shortcuts. Only while shapes (not text) are selected,
      // so typing ⌥⇧ characters in a text box still works.
      doc.addEventListener('keydown', (e) => {
        if (!e.isTrusted || (self.SVG2S_EDIT && self.SVG2S_EDIT.isOpen())) return;
        if (undoRedoKey(e)) return;
        const sc = SB.matchShortcut(e);
        if (!sc || SLIDES_KEYS.has(sc) || editingText()) return;
        if (!ANYTIME.has(sc) && !topIdsOf(SB.readSelection()).length) return;
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        command(sc);
      }, true);
    };
    hookIframe();
    setInterval(hookIframe, 1500);
    document.addEventListener('paste', onPasteSvg, true);
    ['mousedown', 'mouseup', 'click'].forEach((t) => document.addEventListener(t, onUndoButton, true));
    ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach((t) => document.addEventListener(t, onDeepClick, true));
    hoverBox = el('div', { class: 'hov' }, el('span', { class: 'lb' }));
    root.append(hoverBox);
    document.addEventListener('mousemove', updateHover, true);
    const metaKey = (e) => { if (e.key === 'Meta' || e.key === 'Control') { if (hoverPt) hoverPt.meta = e.type === 'keydown'; updateHover(); } };
    window.addEventListener('keydown', metaKey, true);
    window.addEventListener('keyup', metaKey, true);
    // Leaving the window lets go of ⌘; focus moving into Slides' own text
    // frame (which we do ourselves) doesn't.
    window.addEventListener('blur', () => setTimeout(() => {
      if (document.activeElement === SB.iframe() && document.hasFocus()) return;
      if (hoverPt) hoverPt.meta = false;
      updateHover();
    }, 0));
    const hookMeta = () => {
      const ifr = SB.iframe();
      let d = null;
      try { d = ifr && ifr.contentDocument; } catch { d = null; }
      if (!d || d.__svgxMeta) return;
      d.__svgxMeta = true;
      d.addEventListener('keydown', metaKey, true);
      d.addEventListener('keyup', metaKey, true);
    };
    hookMeta();
    setInterval(hookMeta, 1500);
    document.addEventListener('keydown', (e) => {
      if (!e.isTrusted || (self.SVG2S_EDIT && self.SVG2S_EDIT.isOpen()) || (host && e.composedPath().includes(host))) return;
      const t = e.target;
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
      if (undoRedoKey(e)) return;
      const sc = SB.matchShortcut(e);
      if (sc && ANYTIME.has(sc)) { e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation(); command(sc); }
    }, true);
  }
  const boot = setInterval(() => { if (SB.currentPageGroup()) { clearInterval(boot); init(); } }, 1000);

  // For the console and tests.
  // For Edit Shape: outlined text made there, and inside/outside strokes.
  function noteOutlinedText(resolved, glyph, unitEntries, label) {
    remember(SB.pathFingerprint(glyph), { kind: 'text', unit: clone(unitEntries), box: entryBox(resolved, glyph), label });
  }
  self.SVG2S_SHAPES = {
    remember, recall, noteOutlinedText, describeText,
    booleanOp, outlineStrokeOp, outlineTextOp, groupOp, adjustMask, maskedPicture, selectIds, regionOf, textOutlines, objectPaths, facesFor, command,
    hasText: (id, includeHidden) => hasRenderedText(id, includeHidden),
    takeNotes: () => { const t = [...notes].join(' · '); notes.clear(); return t; },
  };
})();
