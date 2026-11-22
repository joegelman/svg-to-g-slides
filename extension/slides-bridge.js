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

  // Both lists of a copy. Slides keeps what an object inherits from its
  // layout out of `unresolved`, and that is the only place a placeholder
  // says it is one (props 54/55: placeholder kind and index).
  function readSelectionRaw() {
    const tb = textbox();
    if (!tb) return null;
    const dt = new DataTransfer();
    tb.dispatchEvent(new ClipboardEvent('copy', { clipboardData: dt, bubbles: true, cancelable: true }));
    try {
      const data = JSON.parse(JSON.parse(dt.getData(MIME)).data);
      return data && data.resolved ? { resolved: data.resolved, unresolved: data.unresolved || [] } : null;
    } catch { return null; }
  }
  function placeholderIds(raw) {
    if (!raw) return [];
    return raw.unresolved.filter((e) => e[0] === 3 && Array.isArray(e[4]) && getProp(e[4], 54) !== undefined).map((e) => e[1]);
  }

  // Every format a copy of the selection carries (an image brings an
  // image clip with it: what lets a paste fetch the picture).
  const IMAGE_CLIP = 'application/x-vnd.google-docs-image-clip+wrapped';
  function readClip() {
    const tb = textbox();
    if (!tb) return null;
    const dt = new DataTransfer();
    tb.dispatchEvent(new ClipboardEvent('copy', { clipboardData: dt, bubbles: true, cancelable: true }));
    const out = {};
    [...dt.types].forEach((t) => { out[t] = dt.getData(t); });
    return out[MIME] ? out : null;
  }
  // Pastes made inside fn go out the way a real copy of `clip` would: the
  // copy's own wrapper (document id, tokens) with our objects as both its
  // resolved and unresolved lists, plus its image clip. A bare payload
  // that names a stored picture shows Slides' broken-image sign ("There
  // was a problem retrieving the specified image"); with the wrapper and
  // image clip of a copy of that picture, Slides fetches it (checked live
  // on a copy of the Vacay deck, also after deleting the original and
  // reloading).
  let pasteClip = null;
  async function withClip(clip, fn) {
    const prev = pasteClip;
    pasteClip = clip;
    try { return await fn(); } finally { pasteClip = prev; }
  }
  function clipWrap(resolved) {
    try {
      const w = JSON.parse(pasteClip[MIME]);
      const data = JSON.parse(w.data);
      const page = currentPageGroup();
      const pid = page ? page.id.replace(/^editor-/, '') : null;
      data.resolved = resolved;
      data.unresolved = resolved.map((e) => (pid ? JSON.parse(JSON.stringify(e)).concat([pid]) : e));
      w.data = JSON.stringify(data);
      return JSON.stringify(w);
    } catch {
      return wrap(resolved);
    }
  }

  function paste(resolved) {
    const tb = textbox();
    if (!tb) return false;
    tb.focus();
    const dt = new DataTransfer();
    dt.setData(MIME, pasteClip ? clipWrap(resolved) : wrap(resolved));
    if (pasteClip && pasteClip[IMAGE_CLIP]) dt.setData(IMAGE_CLIP, pasteClip[IMAGE_CLIP]);
    tb.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }));
    tick();
    return true;
  }

  const KEYCODES = { Delete: 46, Escape: 27, Backspace: 8 };
  function pressKey(key) {
    const tb = textbox();
    if (!tb) return false;
    const opts = { key, code: key, keyCode: KEYCODES[key] || 0, which: KEYCODES[key] || 0, bubbles: true, cancelable: true };
    tb.dispatchEvent(new KeyboardEvent('keydown', opts));
    tb.dispatchEvent(new KeyboardEvent('keyup', opts));
    if (key === 'Delete' || key === 'Backspace') tick();
    return true;
  }

  // ── One undo step for our multi-step changes ───────────────────────────
  // A combine, align, Done in Edit Shape and the like reach Slides as
  // several steps (delete, paste, Arrange presses, menu picks). We note the
  // slide as it was before and after; ⌘Z right after one of ours walks
  // Slides' own undo back to the "before" state in one go, and ⌘⇧Z walks it
  // forward again. Slides' history stays its own, so everything past ours
  // undoes as normal.
  let macro = null;
  const undoStack = [], redoStack = [];
  let replaying = false;
  function hashStr(str) {
    let h1 = 2166136261 >>> 0, h2 = 5381;
    for (let i = 0; i < str.length; i++) { const c = str.charCodeAt(i); h1 = Math.imul(h1 ^ c, 16777619) >>> 0; h2 = (Math.imul(h2, 33) + c) >>> 0; }
    return h1.toString(16) + h2.toString(16);
  }
  // What the current slide shows: each object in stacking order, with its
  // drawn outlines, paint and text.
  function slideSig() {
    const page = currentPageGroup();
    if (!page) return null;
    const parts = [page.id];
    topLevelOrder().forEach((id) => {
      const g = elementFor(id);
      if (!g) return;
      let t = id;
      // A gradient fill is url(#gradient-N), and N changes whenever Slides
      // redraws: read the gradient itself. Opacity, a text run's style
      // (its colour lives there) and where a picture sits under its mask
      // count too, or a change to only those looks like no change.
      const paintOf = (v) => {
        const m = /^url\(["']?#([^"')]+)/.exec(v || '');
        const gr = m && document.getElementById(m[1]);
        if (!gr) return v || '';
        const r3 = (a) => { const x = parseFloat(gr.getAttribute(a)); return Number.isFinite(x) ? x.toPrecision(3) : ''; };
        return gr.tagName + ['x1', 'y1', 'x2', 'y2', 'cx', 'cy', 'r'].map(r3).join(',') + [...gr.querySelectorAll('stop')].map((st) => (st.getAttribute('offset') || '') + (st.getAttribute('stop-color') || '') + (st.getAttribute('stop-opacity') || '')).join(';');
      };
      g.querySelectorAll('path, text, image').forEach((n) => {
        t += '|' + n.tagName + (n.getAttribute('d') || '').replace(/(\d+\.\d)\d+/g, '$1') + paintOf(n.getAttribute('fill')) + paintOf(n.getAttribute('stroke')) +
          (n.getAttribute('stroke-width') || '') + (n.getAttribute('fill-opacity') || '') + (n.getAttribute('stroke-opacity') || '') + (n.getAttribute('opacity') || '') +
          (n.getAttribute('transform') || '').replace(/(\d+\.\d)\d+/g, '$1') +
          (n.tagName === 'text' ? n.textContent + (n.getAttribute('style') || '') : '') +
          (n.tagName === 'image' ? ['x', 'y', 'width', 'height'].map((a) => (n.getAttribute(a) || '').replace(/(\d+\.\d)\d+/g, '$1')).join(',') : '');
      });
      parts.push(hashStr(t));
    });
    return parts.join(',');
  }
  function tick() { if (macro && !replaying) macro.steps++; }
  function untick() { if (macro && !replaying && macro.steps > 0) macro.steps--; }
  function forceMacro() { if (macro) macro.force = true; }
  // exact: undo presses every one of our steps instead of stopping when the
  // slide first looks right. Needed when steps cancel out on the way (a
  // copy pasted and later removed): stopping early would leave them in
  // Slides' history, and the next ⌘Z would bring the copy back.
  function exactMacro() { if (macro) macro.exact = true; }
  // Where our last action left the slide: after a macro (s1) or before it
  // (s0). With no input of the person's own since, that is where the slide
  // still is, even if Slides redrew it slightly differently.
  let here = null;
  let lastOursAt = 0;
  let lastUserInput = 0;
  const quiet = () => !(lastUserInput > lastOursAt);
  // Two places in the stack are the same slide state when one macro started
  // right where the one before it ended.
  function same(a, b) {
    if (!a || !b) return false;
    if (a.m === b.m) return a.side === b.side;
    const [x, y] = a.side === 's0' ? [a, b] : [b, a];
    return x.side === 's0' && y.side === 's1' && x.m.prev === y.m && x.m.prevContig;
  }
  function at(m, side) {
    if (!m) return false;
    if (slideSig() === m[side]) return true;
    return quiet() && same(here, { m, side });
  }
  function beginMacro(label) {
    if (replaying) return;
    if (macro) { macro.depth++; return; }
    const prev = undoStack[undoStack.length - 1] || null;
    macro = { label, s0: slideSig(), steps: 0, depth: 1, prev, prevContig: !!prev && at(prev, 's1') };
  }
  function endMacro() {
    if (!macro || replaying) return;
    if (--macro.depth > 0) return;
    const m = macro;
    macro = null;
    m.s1 = slideSig();
    // m.force: the change is on other slides (a colour replaced through the
    // deck), so this slide can look the same before and after.
    if (!m.s0 || !m.s1 || (m.s0 === m.s1 && !m.force)) return; // nothing changed
    lastOursAt = Date.now();
    // One Slides step needs no help, but the slide is somewhere new now.
    if (m.steps < 2) { here = null; return; }
    undoStack.push(m);
    if (undoStack.length > 30) undoStack.shift();
    redoStack.length = 0;
    here = { m, side: 's1' };
    settle(m, 's1');
  }
  // Slides keeps drawing for a moment after the last paste (text, fonts,
  // the kept frame of outlined text), so the picture is retaken until it
  // stops changing.
  async function settle(m, side) {
    let last = m[side];
    for (let i = 0; i < 20; i++) {
      await sleep(100);
      if (replaying || macro || !quiet() || !here || here.m !== m || here.side !== side) return;
      const now = slideSig();
      if (now === last) break;
      last = now;
    }
    if (here && here.m === m && here.side === side && quiet()) share(m, side, last);
  }
  // Record a picture for a place in the stack, and for its twin (the end of
  // the macro before, or the start of the one after).
  function share(m, side, sig) {
    m[side] = sig;
    if (side === 's0' && m.prevContig && m.prev) m.prev.s1 = sig;
    if (side === 's1') {
      const next = redoStack.find((r) => r.prev === m && r.prevContig) || undoStack.find((u) => u.prev === m && u.prevContig);
      if (next) next.s0 = sig;
    }
  }
  // The person's own input. Our own shortcuts, our toolbar and the undo
  // keys and buttons don't count.
  function noteInput(e) {
    if (!e.isTrusted || replaying) return;
    if (e.type === 'keydown') {
      if (['Meta', 'Control', 'Alt', 'Shift', 'CapsLock'].includes(e.key)) return;
      if ((e.metaKey || e.ctrlKey) && (e.code === 'KeyZ' || e.code === 'KeyY')) return;
      if (matchShortcut(e)) return;
    }
    const path = e.composedPath ? e.composedPath() : [];
    if (path.some((n) => n && (n.id === 'svg2slides-shape-tools' || n.id === 'undoButton' || n.id === 'redoButton'))) return;
    lastUserInput = Date.now();
  }
  document.addEventListener('pointerdown', noteInput, true);
  document.addEventListener('keydown', noteInput, true);
  setInterval(() => {
    const ifr = iframe();
    let doc = null;
    try { doc = ifr && ifr.contentDocument; } catch { doc = null; }
    if (!doc || doc.__svgxInput) return;
    doc.__svgxInput = true;
    doc.addEventListener('keydown', noteInput, true);
    doc.addEventListener('pointerdown', noteInput, true);
  }, 1500);
  function undoKey(redo) {
    const tb = textbox();
    if (!tb) return;
    const o = redo
      ? (MAC ? { key: 'z', code: 'KeyZ', keyCode: 90, metaKey: true, shiftKey: true } : { key: 'y', code: 'KeyY', keyCode: 89, ctrlKey: true })
      : Object.assign({ key: 'z', code: 'KeyZ', keyCode: 90 }, MAC ? { metaKey: true } : { ctrlKey: true });
    o.which = o.keyCode; o.bubbles = true; o.cancelable = true;
    tb.dispatchEvent(new KeyboardEvent('keydown', o));
    tb.dispatchEvent(new KeyboardEvent('keyup', o));
  }
  async function walk(m, redo) {
    const from = redo ? 's0' : 's1', side = redo ? 's1' : 's0';
    if (!at(m, from)) return false;
    const to = m[side];
    replaying = true;
    let ok = false;
    try {
      focusTextbox();
      // Never more presses than our steps: if the slide never matches, stop
      // there rather than undo something that wasn't ours.
      let done = 0;
      for (let i = 0; i < m.steps; i++) {
        const before = slideSig();
        undoKey(redo);
        for (let w = 0; w < 25 && slideSig() === before; w++) await sleep(40);
        if (m.exact) { done++; continue; }
        if (slideSig() === to) { ok = true; break; }
        if (slideSig() === before) break; // history ran out
        done++;
      }
      // Every one of our steps went through: that is the other state, even
      // if Slides draws it a little differently now.
      if (!ok && done === m.steps) ok = true;
    } finally {
      replaying = false;
    }
    lastOursAt = Date.now();
    if (!ok) { here = null; return false; }
    here = { m, side };
    share(m, side, slideSig());
    settle(m, side);
    return true;
  }
  // Called on ⌘Z / ⌘⇧Z.
  function canUndoMacro() { const m = undoStack[undoStack.length - 1]; return !!(m && !replaying && !macro && at(m, 's1')); }
  function canRedoMacro() { const m = redoStack[redoStack.length - 1]; return !!(m && !replaying && !macro && at(m, 's0')); }
  async function undoMacro() {
    if (!canUndoMacro()) return false;
    const m = undoStack.pop();
    if (await walk(m, false)) redoStack.push(m);
    return true;
  }
  async function redoMacro() {
    if (!canRedoMacro()) return false;
    const m = redoStack.pop();
    if (await walk(m, true)) undoStack.push(m);
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
  // Looked up often (once per object in a slide signature), so kept for a
  // moment.
  let pageMemo = null, pageMemoAt = 0;
  function currentPageGroup() {
    const now = performance.now();
    if (pageMemo && now - pageMemoAt < 40 && pageMemo.isConnected) return pageMemo;
    const bg = currentPageBg();
    pageMemo = bg && bg.parentNode && bg.parentNode.closest ? bg.parentNode.closest('g[id^="editor-"]') : null;
    pageMemoAt = now;
    return pageMemo;
  }

  function pageCTM() {
    const bg = currentPageBg();
    const page = currentPageGroup();
    const el = page || bg;
    if (!el || typeof el.getScreenCTM !== 'function') return null;
    const c = el.getScreenCTM();
    return c ? [c.a, c.b, c.c, c.d, c.e, c.f] : null;
  }

  // Theme objects are drawn on every page that uses them with the same id
  // (a slide, its layout in the theme builder), and pages seen earlier stay
  // in the DOM. Prefer the one on the page in view.
  function elementFor(id) {
    const page = currentPageGroup();
    if (page) {
      if (page.id === 'editor-' + id) return page;
      const g = page.querySelector('[id="editor-' + String(id).replace(/["\\]/g, '') + '"]');
      if (g) return g;
    }
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
      if (after === cur) { if (++stuck > 3) return false; await sleep(80); } else { stuck = 0; tick(); }
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
  // The exact box around a path (curves at their extremes, not their
  // control points): what Slides fits an image fill to (checked live: an
  // arch whose handles reach y=0 got its picture from y=12500, the curve's
  // real top).
  function subsBBox(subs) {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    const add = (x, y) => { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; };
    const ext = (a, b, c, d) => { // roots of the cubic's derivative in (0, 1)
      const A = -a + 3 * b - 3 * c + d, B = 2 * (a - 2 * b + c), C = b - a;
      const ts = [];
      if (Math.abs(A) < 1e-12) { if (Math.abs(B) > 1e-12) ts.push(-C / B); }
      else { const D = B * B - 4 * A * C; if (D >= 0) { const q = Math.sqrt(D); ts.push((-B + q) / (2 * A), (-B - q) / (2 * A)); } }
      return ts.filter((t) => t > 0 && t < 1);
    };
    const at = (a, b, c, d, t) => { const u = 1 - t; return u * u * u * a + 3 * u * u * t * b + 3 * u * t * t * c + t * t * t * d; };
    subs.forEach((sp) => {
      const n = sp.nodes, L = n.length;
      n.forEach((p) => add(p.x, p.y));
      const segs = sp.closed ? L : L - 1;
      for (let i = 0; i < segs; i++) {
        const a = n[i], d = n[(i + 1) % L];
        if (!a.out && !d.in) continue;
        const b = a.out || a, c = d.in || d;
        [...ext(a.x, b.x, c.x, d.x), ...ext(a.y, b.y, c.y, d.y)].forEach((t) => add(at(a.x, b.x, c.x, d.x, t), at(a.y, b.y, c.y, d.y, t)));
      }
    });
    return isFinite(x0) ? { x: x0, y: y0, w: x1 - x0, h: y1 - y0 } : null;
  }
  // An image-filled shape's picture is placed by props 84/85 (offset) and
  // 79/80 (size), as fractions of the path's exact box. Given the picture's
  // rect and the box (same units), the four values; Slides keeps 4
  // decimals.
  function imageFillProps(pic, box) {
    const r4 = (v) => Math.round(v * 1e4) / 1e4;
    const w = Math.max(box.w, 1e-9), h = Math.max(box.h, 1e-9);
    return { 84: r4((pic.x - box.x) / w), 85: r4((pic.y - box.y) / h), 79: r4(pic.w / w), 80: r4(pic.h / h) };
  }
  function pictureRect(props, box) {
    const g = (k, d) => { const v = getProp(props, k); return typeof v === 'number' ? v : d; };
    return { x: box.x + g(84, 0) * box.w, y: box.y + g(85, 0) * box.h, w: g(79, 1) * box.w, h: g(80, 1) * box.h };
  }

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

  // ── Paint props (fill / stroke) ───────────────────────────────────────
  // 14 = filled (1/0), 15 = fill hex. Stroke: our shapes and converted
  // ones use 18 = 1 with 19 = colour and 22 = weight (page units, 381 =
  // 1 px), and 18 = 0 + 23 = 0 for none (verified live, Nov 2026). Slides'
  // own polylines carry 19/22 with no 18 at all.
  function removeProp(props, key) {
    for (let i = 0; i + 1 < props.length; i += 2) if (props[i] === key) { props.splice(i, 2); i -= 2; }
    return props;
  }
  function paintFromProps(props) {
    const fill = getProp(props, 15), stroke = getProp(props, 19), w = getProp(props, 22), on = getProp(props, 18);
    return {
      fill: typeof fill === 'string' ? fill : '#9e9e9e',
      filled: getProp(props, 14) !== 0,
      stroke: typeof stroke === 'string' ? stroke : '#000000',
      weight: typeof w === 'number' && w > 0 ? w : 381,
      strokeOn: on === 1 || (on === undefined && typeof stroke === 'string'),
      // Opacity (16 fill, 20 stroke) and a gradient fill (60 kind, 61 stops,
      // 62 angle in radians, 73 radial start), so Edit Shape shows and keeps them.
      fillAlpha: typeof getProp(props, 16) === 'number' ? getProp(props, 16) : 1,
      strokeAlpha: typeof getProp(props, 20) === 'number' ? getProp(props, 20) : 1,
      grad: (getProp(props, 60) === 1 || getProp(props, 60) === 2) && Array.isArray(getProp(props, 61)) && getProp(props, 61).length >= 2
        ? { kind: getProp(props, 60), stops: getProp(props, 61).map((x) => [String(x[0]), +x[1] || 0]), angle: +getProp(props, 62) || 0, centre: getProp(props, 73) || 0 } : null,
    };
  }
  // The SVG gradient that draws the way Slides draws `grad` in a w × h frame
  // at (x, y): a line through the middle, w·|cos| + h·|sin| long; a radial
  // from the middle (radius: half the diagonal) or a corner (the diagonal).
  function gradientGeometry(grad, x, y, w, h) {
    if (grad.kind === 1) {
      const c = Math.cos(grad.angle), sn = Math.sin(grad.angle), L = w * Math.abs(c) + h * Math.abs(sn), cx = x + w / 2, cy = y + h / 2;
      return { tag: 'linearGradient', attrs: { x1: cx - L / 2 * c, y1: cy - L / 2 * sn, x2: cx + L / 2 * c, y2: cy + L / 2 * sn } };
    }
    const D = Math.hypot(w, h);
    const [cx, cy, r] = [[x + w / 2, y + h / 2, D / 2], [x, y, D], [x + w, y, D], [x, y + h, D], [x + w, y + h, D]][grad.centre || 0];
    return { tag: 'radialGradient', attrs: { cx, cy, r } };
  }
  function applyPaint(props, p) {
    setProp(props, 14, p.filled ? 1 : 0);
    setProp(props, 15, p.fill);
    if (p.fillAlpha !== undefined) { removeProp(props, 16); if (p.fillAlpha < 0.995) setProp(props, 16, Math.round(p.fillAlpha * 100) / 100); }
    if (p.strokeAlpha !== undefined) { removeProp(props, 20); if (p.strokeAlpha < 0.995) setProp(props, 20, Math.round(p.strokeAlpha * 100) / 100); }
    if (p.grad !== undefined) {
      [60, 61, 62, 73, 145].forEach((k) => removeProp(props, k));
      if (p.grad && p.filled) {
        setProp(props, 145, 1); setProp(props, 15, p.grad.stops[0][0]);
        setProp(props, 60, p.grad.kind); setProp(props, 61, p.grad.stops); setProp(props, 62, p.grad.kind === 1 ? Math.round(p.grad.angle * 1e4) / 1e4 : 1.5708);
        if (p.grad.kind === 2) setProp(props, 73, p.grad.centre || 0);
      }
    }
    if (p.strokeOn) {
      removeProp(props, 23);
      setProp(props, 18, 1);
      setProp(props, 19, p.stroke);
      setProp(props, 22, Math.max(1, Math.round(p.weight)));
    } else {
      setProp(props, 18, 0);
      setProp(props, 23, 0);
    }
    return props;
  }

  // ── Shortcuts (shared by the editor and the Shape tools rail) ─────────
  // Rotate, resize, arrange and group reuse Slides' own keys, so they mean
  // the same thing inside and outside Edit Shape. The rest follow Figma
  // where Slides leaves the key free.
  const MAC = /Mac|iPhone|iPad/.test(navigator.platform || '');
  function matchShortcut(e) {
    const prim = MAC ? e.metaKey : e.ctrlKey;
    const c = e.code, k = e.key;
    const altOnly = e.altKey && !e.metaKey && !e.ctrlKey;
    if (altOnly && (k === 'ArrowLeft' || k === 'ArrowRight')) {
      return (k === 'ArrowLeft' ? 'rotL' : 'rotR') + (e.shiftKey ? '1' : '15');
    }
    const scaleMods = MAC ? (e.metaKey && e.ctrlKey && !e.altKey) : (e.ctrlKey && e.altKey && !e.metaKey);
    if (scaleMods && !e.shiftKey && c === 'KeyK') return 'scaleUp';
    if (scaleMods && !e.shiftKey && c === 'KeyJ') return 'scaleDown';
    if (prim && !e.altKey && (k === 'ArrowUp' || k === 'ArrowDown')) {
      return k === 'ArrowUp' ? (e.shiftKey ? 'front' : 'forward') : (e.shiftKey ? 'back' : 'backward');
    }
    if (prim && e.altKey && c === 'KeyG') return e.shiftKey ? 'ungroup' : 'group';
    if (prim && e.altKey && !e.shiftKey && c === 'KeyO') return 'outlineStroke';
    if (prim && e.altKey && !e.shiftKey && c === 'KeyT') return 'outlineText';
    if (prim && !e.altKey && !e.shiftKey && c === 'Backslash') return 'palette';
    // Show / hide our toolbar (next to ⌘\, Figma hides its UI on backslash)
    // and the Layers panel (Figma's ⌥1).
    if (altOnly && !e.shiftKey && c === 'Backslash') return 'toggleRail';
    if (altOnly && !e.shiftKey && c === 'Digit1') return 'layers';
    if (altOnly && e.shiftKey && c === 'KeyM') return 'themeBuilder'; // M for master
    // Align and distribute: Figma's keys.
    if (altOnly && !e.shiftKey) {
      const al = ({ KeyA: 'alignLeft', KeyD: 'alignRight', KeyW: 'alignTop', KeyS: 'alignBottom', KeyH: 'alignHCenter', KeyV: 'alignVMiddle' })[c];
      if (al) return al;
    }
    if (altOnly && e.shiftKey) {
      return ({ KeyU: 'union', KeyS: 'subtract', KeyI: 'intersect', KeyE: 'exclude', Slash: 'strokeToggle',
        BracketLeft: 'strokeThinner', BracketRight: 'strokeThicker', KeyF: 'fillColor', KeyL: 'strokeColor',
        KeyP: 'pen', KeyH: 'distH', KeyV: 'distV', KeyK: 'mask' })[c] || null;
    }
    return null;
  }
  const K = MAC
    ? { alt: '⌥', shift: '⇧', cmd: '⌘', ctrl: '⌃', join: '' }
    : { alt: 'Alt+', shift: 'Shift+', cmd: 'Ctrl+', ctrl: 'Ctrl+', join: '' };
  const SHORTCUT_LABEL = {
    rotL15: K.alt + '←', rotR15: K.alt + '→', rotL1: K.alt + K.shift + '←', rotR1: K.alt + K.shift + '→',
    scaleUp: MAC ? '⌘⌃K' : 'Ctrl+Alt+K', scaleDown: MAC ? '⌘⌃J' : 'Ctrl+Alt+J',
    forward: K.cmd + '↑', backward: K.cmd + '↓', front: K.shift + K.cmd + '↑', back: K.shift + K.cmd + '↓',
    group: MAC ? '⌘⌥G' : 'Ctrl+Alt+G', ungroup: MAC ? '⇧⌘⌥G' : 'Ctrl+Alt+Shift+G',
    outlineStroke: MAC ? '⌥⌘O' : 'Ctrl+Alt+O', outlineText: MAC ? '⌥⌘T' : 'Ctrl+Alt+T',
    union: K.alt + K.shift + 'U', subtract: K.alt + K.shift + 'S', intersect: K.alt + K.shift + 'I', exclude: K.alt + K.shift + 'E',
    strokeToggle: K.alt + K.shift + '/', strokeThinner: K.alt + K.shift + '[', strokeThicker: K.alt + K.shift + ']',
    fillColor: K.alt + K.shift + 'F', strokeColor: K.alt + K.shift + 'L', pen: K.alt + K.shift + 'P',
    alignLeft: K.alt + 'A', alignHCenter: K.alt + 'H', alignRight: K.alt + 'D',
    alignTop: K.alt + 'W', alignVMiddle: K.alt + 'V', alignBottom: K.alt + 'S',
    distH: K.alt + K.shift + 'H', distV: K.alt + K.shift + 'V',
    palette: K.cmd + '\\',
    toggleRail: K.alt + '\\',
    layers: K.alt + '1',
    themeBuilder: K.alt + K.shift + 'M',
    mask: K.alt + K.shift + 'K',
  };

  // A stable id for a path's geometry, independent of object ids (Slides
  // reassigns those on paste) and position (the transform isn't included).
  // Used to recognise our own results later: outlined text, offset strokes.
  function pathFingerprint(entry) {
    const rec = pathRecord(entry);
    if (!rec) return null;
    const str = rec[2].join(',') + '|' + rec[3].map((v) => Math.round(v)).join(',');
    let h1 = 0x811c9dc5, h2 = 0x01000193;
    for (let i = 0; i < str.length; i++) {
      const c = str.charCodeAt(i);
      h1 = Math.imul(h1 ^ c, 16777619) >>> 0;
      h2 = Math.imul(h2 + c, 2246822519) >>> 0;
    }
    return h1.toString(16).padStart(8, '0') + h2.toString(16).padStart(8, '0') + ':' + rec[3].length;
  }
  // Slides' own border weights, in px.
  const WEIGHTS = [1, 2, 3, 4, 8, 12, 16, 24];

  return {
    MIME, iframe, textbox, focusTextbox, wrap, unwrap,
    forceMacro, exactMacro, untick, readSelection, readSelectionRaw, placeholderIds, readClip, withClip, hasClip: () => !!pasteClip, paste, pressKey, sleep, waitForSelection,
    getProp, setProp, newId, pathRecord, isEditableShape,
    matMul, matInv, apply, localToPage, pageCTM, elementFor, currentPageGroup, visibleWorkspaceRect,
    topLevelOrder, topLevelIdOf, pressArrange, moveToIndex,
    ZOOM_MIN, ZOOM_MAX, zoomPctFromCTM, setSlidesZoom, scrollPagePointTo, matchSlidesView,
    decodePath, encodePath, normalizeSubs, typeFor, svgPathD, subsBBox, imageFillProps, pictureRect,
    convertibleKind, convertSelection, KIND_NOTE, parseRenderedD, solveAffine,
    removeProp, paintFromProps, applyPaint, gradientGeometry, matchShortcut, SHORTCUT_LABEL, WEIGHTS, IS_MAC: MAC, pathFingerprint,
    beginMacro, endMacro, tick, slideSig, undoMacro, redoMacro, canUndoMacro, canRedoMacro, isReplaying: () => replaying,
    isRecording: () => !!macro, nativeUndo: (redo) => { focusTextbox(); undoKey(!!redo); },
  };
})();
