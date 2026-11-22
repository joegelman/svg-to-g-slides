// Loaded last — see manifest.json. Uses SB (slides-bridge.js) plus a few
// helpers from content.js (writeClipBundleLogged, showInsertTooltip,
// removeInsertTooltip, armPasteDetection, isMac).
//
// "Edit Shape" (was "Edit as SVG"): double-click a shape that came from a path (ours, or any
// custom/polyline shape) and an "Edit Shape" button appears. The editor
// lays the shape's true vector form over the Slides shape at the exact same
// size and position, hides the Slides version, and lets you edit anchors and
// Bézier handles. Done replaces the shape: delete the original, paste the
// edited version at the same transform. If Slides ever rejects the scripted
// paste, the edited shape is already on the OS clipboard (copied inside the
// Done click) and a "⌘V to commit changes" prompt appears instead.
//
// Slides' own "Edit points" can't do this: its point editor has no Bézier
// model (it flattens curves into their control polygons on the first drag)
// and merges multi-outline shapes. See editable-points-findings.md.

console.log('[svg2slides] svg-editor.js loaded');

(() => {
  const ACCENT = '#0b57d0'; // GM3 primary, as Slides uses for selection
  const FONT = "'Google Sans', Roboto, Arial, sans-serif";
  // Colours and elevation read off the live Slides UI (Nov 2026).
  const GM = {
    surface: '#f0f4f9',      // toolbar pill
    icon: '#444746',         // toolbar icon grey
    hover: 'rgba(68,71,70,.08)',
    selected: '#d3e3fd',     // pressed tool (e.g. Select)
    tonal: '#c2e7ff',        // Share button
    onTonal: '#004a77',
    tooltip: '#303030',
    onTooltip: '#f2f2f2',
    elev1: '0 1px 2px rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15)',
    elev2: '0 1px 2px rgba(60,64,67,.3), 0 2px 6px 2px rgba(60,64,67,.15)',
  };
  const HIT = 9; // px: matches the larger point markers
  const CORNER_INSET = 14; // px from a corner to its radius handle at radius 0
  const SVGNS = 'http://www.w3.org/2000/svg';
  // A curved double arrow, for the rotate zone outside the transform box.
  const cur = (svg, hot = '12 12', fb = 'default') => 'url("data:image/svg+xml;utf8,' + encodeURIComponent(svg) + '") ' + hot + ', ' + fb;
  const SKEW_H_CURSOR = cur("<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'><path d='M3 9h14l-3-3M21 15H7l3 3' fill='none' stroke='#fff' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/><path d='M3 9h14l-3-3M21 15H7l3 3' fill='none' stroke='#000' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/></svg>", '12 12', 'ew-resize');
  const SKEW_V_CURSOR = cur("<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'><path d='M9 21V7l-3 3M15 3v14l3-3' fill='none' stroke='#fff' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/><path d='M9 21V7l-3 3M15 3v14l3-3' fill='none' stroke='#000' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/></svg>", '12 12', 'ns-resize');
  const ROTATE_CURSOR = 'url("data:image/svg+xml;utf8,' + encodeURIComponent('<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'24\' height=\'24\' viewBox=\'0 0 24 24\'><path d=\'M6 15a7 7 0 0 1 9-9\' fill=\'none\' stroke=\'#fff\' stroke-width=\'4\'/><path d=\'M6 15a7 7 0 0 1 9-9\' fill=\'none\' stroke=\'#000\' stroke-width=\'1.6\'/><path d=\'M13 3l4 3-4 3Z M3 13l3 4 3-4Z\' fill=\'#000\' stroke=\'#fff\' stroke-width=\'.8\'/></svg>') + '") 12 12, crosshair';

  // Slides enforces Trusted Types, so build every element with DOM calls —
  // never innerHTML.
  function el(tag, attrs = {}, ...kids) {
    const e = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
    kids.forEach((c) => e.append(c));
    return e;
  }
  function sv(tag, attrs = {}) {
    const e = document.createElementNS(SVGNS, tag);
    Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
    return e;
  }
  function styleEl(css) {
    const s = document.createElement('style');
    s.textContent = css;
    return s;
  }

  // ── Trigger: double-click an editable shape ─────────────────────────────
  // Slides counts clicks on mousedown, so the second mousedown (detail === 2)
  // is where it would enter text editing or drill into a group. At that
  // moment the first click has already selected the shape (or its group),
  // so read the selection synchronously; if everything selected is an
  // editable path and the click is on it, swallow the double-click and show
  // the button. Anything else is left entirely to Slides.

  let editBtn = null;
  let editBtnTimer = null;
  let swallowUntil = 0;
  let editor = null;

  function shapeIdFromTarget(t) {
    let g = t && t.closest ? t.closest('g[id^="editor-"]') : null;
    while (g) {
      const id = g.id.slice('editor-'.length);
      if (id && !id.endsWith('-bg') && !/_\d+_\d+-paragraph/.test(id)) return id;
      g = g.parentNode && g.parentNode.closest ? g.parentNode.closest('g[id^="editor-"]') : null;
    }
    return null;
  }

  document.addEventListener('mousedown', (e) => {
    if (editor) return;
    if (editBtn && !editBtn.contains(e.target) && e.target !== editHost) hideEditButton();
    if (e.detail !== 2 || e.button !== 0) return;
    const targetId = shapeIdFromTarget(e.target);
    if (!targetId) return;
    const sel = SB.readSelection();
    if (!sel) return;
    const shapes = sel.filter((x) => x[0] === 3);
    if (!shapes.length || !sel.some((x) => x[1] === targetId)) return;
    // A masked image: double-click adjusts the picture under the mask, the
    // way a double-click crops an image in Slides.
    const ST = self.SVG2S_SHAPES;
    if (ST && ST.maskedPicture && ST.maskedPicture(sel)) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      swallowUntil = Date.now() + 400;
      setTimeout(() => ST.adjustMask(), 0);
      return;
    }
    if (!shapes.every(SB.isEditableShape)) {
      // Presets, lines, WordArt, text boxes: offer to convert, but let
      // Slides have its double-click (text editing, group drill-in).
      const kinds = shapes.map((x) => (SB.isEditableShape(x) ? 'editable' : SB.convertibleKind(sel, x)));
      if (kinds.some((k) => !k)) return;
      const kind = kinds.find((k) => k !== 'editable');
      setTimeout(() => { if (!editor) showEditButton(sel, kind); }, 0);
      return;
    }
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    swallowUntil = Date.now() + 400;
    showEditButton(sel);
  }, true);

  // Swallow the rest of the swallowed double-click so Slides never sees it.
  ['mouseup', 'click', 'dblclick'].forEach((type) => {
    document.addEventListener(type, (e) => {
      if (Date.now() < swallowUntil && !(editHost && editHost.contains(e.target))) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
      }
    }, true);
  });

  function unionRect(ids) {
    let r = null;
    ids.forEach((id) => {
      const el = SB.elementFor(id);
      if (!el) return;
      const b = el.getBoundingClientRect();
      if (!b.width && !b.height) return;
      r = r
        ? { left: Math.min(r.left, b.left), top: Math.min(r.top, b.top), right: Math.max(r.right, b.right), bottom: Math.max(r.bottom, b.bottom) }
        : { left: b.left, top: b.top, right: b.right, bottom: b.bottom };
    });
    return r;
  }

  let editHost = null;
  function showEditButton(sel, convertKind = null) {
    hideEditButton();
    const ids = sel.filter((x) => x[0] === 3).map((x) => x[1]);
    const r = unionRect(ids);
    if (!r) return;
    editHost = document.createElement('div');
    editHost.id = 'svg2slides-edit-btn';
    const root = editHost.attachShadow({ mode: 'open' });
    // Slides' own tonal button (the Share button's colours), small.
    root.append(
      styleEl(`
        .b { position: fixed; z-index: 2147483000; display: flex; align-items: center; gap: 6px;
             background: ${GM.tonal}; color: ${GM.onTonal}; padding: 0 12px; height: 28px; border-radius: 14px;
             cursor: pointer; font: 500 13px/1 ${FONT}; box-shadow: ${GM.elev1};
             user-select: none; white-space: nowrap; animation: in .12s ease-out; }
        .b:hover { box-shadow: ${GM.elev2}; filter: brightness(.97); }
        .k { opacity: .6; font-size: 12px; }
        .n { opacity: .7; font-weight: 400; font-size: 12px; }
        @keyframes in { from { opacity: 0; transform: translateY(4px); } }`),
      convertKind
        ? el('div', { class: 'b', role: 'button', title: 'Converts to a custom shape. ' + SB.KIND_NOTE[convertKind] + '. Cancel in the editor restores the original.' },
          'Edit Shape', el('span', { class: 'n' }, '· ' + SB.KIND_NOTE[convertKind].toLowerCase()))
        : el('div', { class: 'b', role: 'button', title: 'Edit the points and curves (Enter)' }, 'Edit Shape', el('span', { class: 'k' }, '↵'))
    );
    editBtn = root.querySelector('.b');
    const top = Math.max(8, r.top - 36);
    const left = Math.min(window.innerWidth - (convertKind ? 330 : 130), Math.max(8, r.right - (convertKind ? 300 : 110)));
    editBtn.style.top = top + 'px';
    editBtn.style.left = left + 'px';
    editBtn.addEventListener('pointerdown', (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      hideEditButton();
      if (convertKind) convertAndOpen(sel);
      else openEditor(sel);
    });
    editBtn.addEventListener('mousedown', (ev) => { ev.preventDefault(); ev.stopPropagation(); });
    document.documentElement.appendChild(editHost);
    pendingSel = convertKind ? null : sel; // Enter stays Slides' while it may be editing text
    editBtnTimer = setTimeout(hideEditButton, 8000);
  }

  let pendingSel = null;
  function hideEditButton() {
    clearTimeout(editBtnTimer);
    if (editHost) editHost.remove();
    editHost = null;
    editBtn = null;
    pendingSel = null;
  }

  // Enter while the button is showing opens the editor (keyboard lands in
  // Slides' iframe textbox, so listen there).
  function attachIframeKeys() {
    const ifr = SB.iframe();
    let doc = null;
    try { doc = ifr && ifr.contentDocument; } catch { doc = null; }
    if (!doc || doc.__svg2slidesKeys) return;
    doc.__svg2slidesKeys = true;
    doc.addEventListener('keydown', (e) => {
      // Our own scripted keys (Delete on Done, Escape) must reach Slides.
      if (!e.isTrusted) return;
      if (editor) { editor.onKey(e); e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation(); return; }
      if (editHost && pendingSel) {
        if (e.key === 'Enter') {
          e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation();
          const sel = pendingSel;
          hideEditButton();
          openEditor(sel);
        } else {
          hideEditButton();
        }
      }
    }, true);
    doc.addEventListener('keyup', (e) => {
      if (!e.isTrusted) return;
      if (editor) { editor.onKeyUp(e); e.preventDefault(); e.stopPropagation(); e.stopImmediatePropagation(); }
    }, true);
  }
  setInterval(attachIframeKeys, 1500);
  attachIframeKeys();

  // Delete the current Slides selection and confirm the given ids are gone.
  // Focus has to be inside Slides' text iframe first, and the overlay may
  // still hold it, so focus, wait a frame, and retry once.
  async function deleteSelected(ids) {
    if (!ids.length) return true; // nothing to take away (only new shapes)
    for (let attempt = 0; attempt < 2; attempt++) {
      SB.focusTextbox();
      await SB.sleep(attempt ? 120 : 30);
      SB.pressKey('Delete');
      await SB.sleep(150);
      if (!ids.some((id) => SB.elementFor(id))) return true;
    }
    return false;
  }

  // A shape picked from inside a group arrives in the copy data with its
  // transform relative to that group, and the group itself isn't in the
  // data, so the payload alone puts it in the wrong place. Slides draws
  // every path in absolute page units, so fit the decoded points to the
  // drawn ones and use that as the true local → page mapping; `fix` is the
  // correction to bake into the pasted transform on Done.
  function placeFromRendering(sh) {
    if (sh.src !== sh.id) return; // converted in memory: already absolute
    try {
      const el = SB.elementFor(sh.id);
      if (!el) return;
      let sp0 = null, rendered = null;
      for (const p of el.querySelectorAll('path')) {
        const subs = SB.parseRenderedD(p.getAttribute('d'));
        if (!subs) continue;
        // Same subpath on both sides, the first with enough points.
        const own = sh.drawn || sh.subs; // what the slide shows (a moved outline for inside/outside strokes)
        for (let i = 0; i < Math.min(subs.length, own.length); i++) {
          const pts = subs[i].filter((seg) => seg[0] !== 'Z').map((seg) => ({ x: seg[seg.length - 2], y: seg[seg.length - 1] }));
          if (pts.length >= 3 && own[i].nodes.length >= 3) { sp0 = own[i]; rendered = pts; break; }
        }
        if (rendered) break;
      }
      if (!rendered) return;
      const k = Math.min(sp0.nodes.length, rendered.length, 16);
      const fit = SB.solveAffine(sp0.nodes.slice(0, k), rendered.slice(0, k));
      if (!fit) return;
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      rendered.forEach((q) => { minX = Math.min(minX, q.x); maxX = Math.max(maxX, q.x); minY = Math.min(minY, q.y); maxY = Math.max(maxY, q.y); });
      const size = Math.hypot(maxX - minX, maxY - minY) || 1;
      if (fit.err > Math.max(2, size * 0.004)) return; // points don't correspond: trust the payload
      const M0 = sh.toPage;
      const same = M0.every((v, i) => Math.abs(v - fit.m[i]) <= (i < 4 ? 1e-3 * Math.max(1, Math.abs(v)) : Math.max(2, size * 0.002)));
      if (same) return;
      sh.fix = SB.matMul(fit.m, SB.matInv(M0));
      sh.toPage = fit.m;
    } catch (err) {
      console.warn('[svg2slides] could not check placement against the slide', err);
    }
  }

  // ── Replace in place ──────────────────────────────────────────────────
  // A payload's top-level units: each top-level shape, or a group together
  // with everything inside it (and the text entries that belong to them).
  function sizeSig(entries) {
    return entries.filter((e) => e[0] === 3).map((e) => SB.getProp(e[4], 8) + 'x' + SB.getProp(e[4], 9)).sort().join(',');
  }
  function payloadUnits(resolved) {
    const childIds = new Set();
    const byId = new Map();
    resolved.forEach((e) => {
      if (e[0] === 2 || e[0] === 3) byId.set(e[1], e);
      if (e[0] === 2) (e[2] || []).forEach((id) => childIds.add(id));
    });
    const collect = (id, acc) => {
      acc.add(id);
      const e = byId.get(id);
      if (e && e[0] === 2) (e[2] || []).forEach((c) => collect(c, acc));
      return acc;
    };
    return resolved.filter((e) => (e[0] === 2 || e[0] === 3) && !childIds.has(e[1])).map((top) => {
      const ids = collect(top[1], new Set());
      const entries = resolved.filter((e) => typeof e[1] === 'string' && ids.has(e[1]));
      return { id: top[1], ids, entries, nShapes: entries.filter((e) => e[0] === 3).length, sig: sizeSig(entries) };
    });
  }
  // Paste each unit separately, lowest original slot first, and walk it
  // back down to that slot (a paste always lands on top). Everything below
  // a slot is either untouched or already re-placed, so the recorded index
  // is exactly where it belongs. Objects edited from inside a group come
  // back just above that group.
  async function pasteInPlace(resolved, slotFor) {
    const items = payloadUnits(resolved).map((u) => ({ u, slot: slotFor(u) }));
    items.sort((a, b) => (a.slot && a.slot.index >= 0 ? a.slot.index : 1e9) - (b.slot && b.slot.index >= 0 ? b.slot.index : 1e9));
    for (const { u, slot } of items) {
      SB.paste(u.entries);
      const sel = await SB.waitForSelection((x) => x.filter((e) => e[0] === 3).length === u.nShapes && sizeSig(x) === u.sig);
      if (!sel) return false;
      if (!slot || slot.index < 0) continue;
      const pasted = payloadUnits(sel)[0];
      if (!pasted) continue;
      let target = slot.index;
      if (!slot.exact) {
        const ai = SB.topLevelOrder().indexOf(slot.top);
        if (ai >= 0) target = ai + 1;
      }
      if (!(await SB.moveToIndex(pasted.id, target))) console.warn('[svg2slides] could not restore stacking order for', pasted.id);
    }
    return true;
  }

  // ── Convert a native object, then edit it ──────────────────────────────
  // Delete + paste the converted shapes in place (same mechanism as Done),
  // then open the editor on them. Cancel in the editor puts the original
  // back the same way.
  let converting = false;
  async function convertAndOpen(hint, opts = {}) {
    if (editor || converting) return;
    converting = true;
    try {
      const wanted = new Set(hint.filter((x) => x[0] === 3).map((x) => x[1]));
      const usable = (s) => s && s.some((x) => x[0] === 3 && wanted.has(x[1]))
        && s.filter((x) => x[0] === 3).every((x) => SB.isEditableShape(x) || SB.convertibleKind(s, x));
      let original = SB.readSelection();
      for (let i = 0; i < 2 && !usable(original); i++) {
        SB.pressKey('Escape'); // out of text editing / group drill-in
        await SB.sleep(80);
        original = SB.readSelection();
      }
      if (!usable(original)) { console.warn('[svg2slides] selection changed — not converting'); return; }
      const conv = SB.convertSelection(original);
      if (!conv) { console.warn('[svg2slides] nothing convertible in selection'); return; }
      // Nothing on the slide changes yet: the editor opens on the converted
      // geometry while the originals stay put (hidden). Done swaps them in
      // place; Cancel just closes.
      console.log('[svg2slides] converted', conv.converted);
      openEditor(original, { preset: conv.resolved, srcOf: conv.srcOf, original, tool: opts.tool });
    } finally {
      converting = false;
    }
  }

  // Slides styles parts of its SVG with page CSS (e.g. invisible text-box
  // backings), which doesn't reach into our shadow root. Copy the computed
  // paint and text styles onto a clone so it renders the same.
  const COVER_STYLE_PROPS = ['fill', 'fill-opacity', 'fill-rule', 'stroke', 'stroke-opacity', 'stroke-width', 'stroke-linecap',
    'stroke-linejoin', 'stroke-dasharray', 'opacity', 'visibility', 'display', 'font-family', 'font-size', 'font-weight',
    'font-style', 'letter-spacing', 'word-spacing', 'text-decoration', 'white-space', 'dominant-baseline', 'text-anchor'];
  function inlineComputedStyles(orig, copy) {
    const a = [orig, ...orig.querySelectorAll('*')];
    const b = [copy, ...copy.querySelectorAll('*')];
    for (let i = 0; i < a.length && i < b.length; i++) {
      const cs = getComputedStyle(a[i]);
      const st = b[i].style;
      COVER_STYLE_PROPS.forEach((p) => { const v = cs.getPropertyValue(p); if (v) st.setProperty(p, v); });
    }
  }

  // ── Geometry helpers ───────────────────────────────────────────────────
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const lerp = (a, b, t) => ({ x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t });
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

  function cubicAt(p0, c1, c2, p1, t) {
    const mt = 1 - t;
    return {
      x: mt * mt * mt * p0.x + 3 * mt * mt * t * c1.x + 3 * mt * t * t * c2.x + t * t * t * p1.x,
      y: mt * mt * mt * p0.y + 3 * mt * mt * t * c1.y + 3 * mt * t * t * c2.y + t * t * t * p1.y,
    };
  }

  function snap45(dx, dy) {
    const len = Math.hypot(dx, dy);
    if (!len) return { x: 0, y: 0 };
    const ang = Math.round(Math.atan2(dy, dx) / (Math.PI / 4)) * (Math.PI / 4);
    return { x: Math.cos(ang) * len, y: Math.sin(ang) * len };
  }

  // ── Editor ─────────────────────────────────────────────────────────────
  function openEditor(hint, opts = {}) {
    if (editor) return;
    if (opts.blank) return openBlank(opts);
    // Re-read the live selection: what we edit must be exactly what Done
    // deletes. If Slides went into text editing (or its own point editing)
    // on the double-click, Escape returns to plain shape selection.
    const wanted = new Set(hint.filter((x) => x[0] === 3).map((x) => x[1]));
    const matches = (s) => s && s.some((x) => x[0] === 3 && wanted.has(x[1])) && s.filter((x) => x[0] === 3).every(SB.isEditableShape);
    let resolved = opts.preset || SB.readSelection();
    if (!opts.preset && !matches(resolved)) {
      SB.pressKey('Escape');
      resolved = SB.readSelection();
    }
    if (!opts.preset && !matches(resolved)) { console.warn('[svg2slides] selection changed — not opening editor'); return; }
    const srcOf = opts.srcOf || {};
    const ctm = SB.pageCTM();
    if (!ctm) { console.warn('[svg2slides] no page CTM — cannot open editor'); return; }
    const shapes = [];
    for (const entry of resolved) {
      if (!SB.isEditableShape(entry)) continue;
      const rec = SB.pathRecord(entry);
      let subs = SB.decodePath(rec[2], rec[3]);
      if (!subs) { console.warn('[svg2slides] could not decode', entry[1]); return; }
      const paint = SB.paintFromProps(entry[4]);
      // An inside or outside stroke made earlier: edit the shape's own
      // outline, not the moved one.
      const mem = self.SVG2S_SHAPES && self.SVG2S_SHAPES.recall && self.SVG2S_SHAPES.recall(SB.pathFingerprint(entry));
      let drawn;
      if (mem && mem.kind === 'align' && paint.strokeOn) { drawn = subs; subs = JSON.parse(JSON.stringify(mem.design)); paint.align = mem.align; }
      shapes.push({
        drawn,
        entry,
        id: entry[1],
        src: srcOf[entry[1]] || entry[1], // the slide object this shape stands for
        subs,
        toPage: SB.localToPage(resolved, entry),
        paint,
      });
    }
    if (!shapes.length) return;
    shapes.forEach(placeFromRendering);
    const vis = SB.visibleWorkspaceRect();
    if (vis.right - vis.left < 160 || vis.bottom - vis.top < 120) {
      console.warn('[svg2slides] canvas too small or off-screen — not opening editor', vis);
      return;
    }
    try {
      // Everything from here to close (Arrange on the originals, Done's
      // delete and paste) undoes as one step.
      SB.beginMacro('edit shape');
      editor = new Editor(resolved, shapes, ctm, { original: opts.original || resolved, srcOf, tool: opts.tool });
    } catch (err) {
      // Never leave a half-built overlay holding the page hostage.
      console.error('[svg2slides] editor failed to open', err);
      emergencyRestore();
      editor = null;
      SB.endMacro();
    }
  }

  // The pen with nothing selected: an editor with no shapes in it, to draw
  // new ones anywhere on the slide.
  function openBlank(opts) {
    const ctm = SB.pageCTM();
    if (!ctm) { console.warn('[svg2slides] no page CTM — cannot open editor'); return; }
    const vis = SB.visibleWorkspaceRect();
    if (vis.right - vis.left < 160 || vis.bottom - vis.top < 120) return;
    try {
      SB.beginMacro('draw');
      editor = new Editor([], [], ctm, { original: [], srcOf: {}, tool: opts.tool || 'pen' });
    } catch (err) {
      console.error('[svg2slides] editor failed to open', err);
      emergencyRestore();
      editor = null;
      SB.endMacro();
    }
  }

  // Undo everything the editor may have done to the page: our overlays go,
  // anything we hid comes back.
  function emergencyRestore() {
    ['svg2slides-editor', 'svg2slides-zoom-layer'].forEach((id) => { const n = document.getElementById(id); if (n) n.remove(); });
    document.querySelectorAll('[data-svg2slides-hidden]').forEach((n) => {
      n.style.visibility = n.dataset.svg2slidesHidden === '-' ? '' : n.dataset.svg2slidesHidden;
      delete n.dataset.svg2slidesHidden;
    });
    SB.focusTextbox();
  }

  // Snapping (pen and point editing): to other points and the lines
  // through them (and the slide's edges and centre), to whole pixels, and
  // to a grid of a chosen size. Kept on this computer.
  const SNAP_KEY = 'svgxSnap';
  const snapPrefs = { points: true, px: true, grid: false, size: 10 };
  try { chrome.storage.local.get(SNAP_KEY, (v) => { Object.assign(snapPrefs, (v && v[SNAP_KEY]) || {}); }); } catch { /* storage unavailable */ }
  const saveSnap = () => { try { chrome.storage.local.set({ [SNAP_KEY]: Object.assign({}, snapPrefs) }); } catch { /* storage unavailable */ } };
  const SNAP_PX = 6; // how close, on screen, counts as on a point or line

  class Editor {
    constructor(resolved, shapes, ctm, ctx = {}) {
      // Commands below restructure the payload (groups, new shapes), so work
      // on a copy and keep the original for stacking slots on Done.
      this.original = clone(ctx.original || resolved); // what is on the slide now
      this.resolved = clone(resolved);
      this.srcOf = Object.assign({}, ctx.srcOf || {});
      this.shapes = shapes;
      this.srcIds = [...new Set(shapes.map((s) => s.src))]; // deleted on Done
      this.textSrcs = new Set(this.srcIds.filter((id) => self.SVG2S_SHAPES && self.SVG2S_SHAPES.hasText(id, true)));
      this.tool = 'direct';
      this.drawing = null; // the path the pen is drawing: { si, pi }
      this.sel = new Set(); // "si:pi:ni"
      this.undo = [];
      this.redo = [];
      this.drag = null;
      this.hover = null;
      this.dirty = false;
      this.spaceDown = false;
      // Editor-local view (zoom/pan) on top of Slides' own screen mapping.
      // Identity = exactly where Slides draws the shape.
      this.view = { s: 1, tx: 0, ty: 0 };
      this.findPageSvg();
      this.setCTM(ctm);

      // Hide the Slides originals while editing.
      this.hidden = [];
      [...new Set(shapes.map((s) => s.src))].forEach((src) => {
        const el = SB.elementFor(src);
        if (el) { this.hidden.push([el, el.style.visibility]); el.dataset.svg2slidesHidden = el.style.visibility || '-'; el.style.visibility = 'hidden'; }
      });

      this.hideSlidesChrome();
      this.buildDOM();
      this.updateSnapUI();
      this.buildCover();
      if (ctx.tool) this.setTool(ctx.tool);
      this.render();
      this.onResize = () => {
        const c = SB.pageCTM();
        if (!c) return;
        this.dropZoomLayer();
        this.setCTM(c);
        if (this.rk) this.placeRail();
        this.render();
      };
      window.addEventListener('resize', this.onResize);
    }

    setCTM(base) {
      this.baseCTM = base;
      this.applyView();
    }

    applyView() {
      const v = this.view;
      this.ctm = SB.matMul([v.s, 0, 0, v.s, v.tx, v.ty], this.baseCTM);
      this.shapes.forEach((s) => {
        s.M = SB.matMul(this.ctm, s.toPage);
        s.Minv = SB.matInv(s.M);
      });
      this.updateZoomLayer();
      if (this.coverGaps) this.updateCoverTransforms();
      if (this.zoomLabel && this.rk) this.rk.setText('zoomreset', Math.round(v.s * 100) + '%');
    }

    // ── Shapes above the one being edited ──
    // Anything Slides draws on top of the edited shape stays on top while
    // editing: a static copy of those objects sits over our fills but under
    // the outline, points and handles, and ignores the pointer. Copies keep
    // their ids (they live in our shadow root, so document lookups never
    // see them) so internal clip paths and gradients still resolve; defs
    // they borrow from elsewhere on the page are copied alongside.
    buildCover() {
      this.coverGaps = [];
      this.zRank = this.shapes.map((_, i) => i);
      try {
        const page = SB.currentPageGroup();
        const pageCTM = SB.pageCTM();
        if (!page || !pageCTM) return;
        const pageInv = SB.matInv(pageCTM);
        // The slide objects being edited (several converted pieces can
        // share one), in paint order (document order = z-order).
        const srcs = [...new Set(this.shapes.map((sh) => sh.src))];
        const els = srcs.map((id) => SB.elementFor(id));
        if (els.some((e) => !e)) return;
        const sorted = els.slice().sort((a, b) => (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1));
        this.shapes.forEach((sh, si) => { this.zRank[si] = sorted.indexOf(els[srcs.indexOf(sh.src)]); });
        // gap k holds the objects painted after edited shape k and before
        // edited shape k + 1 (the last gap: everything above the topmost).
        const gaps = sorted.map(() => []);
        const taken = [];
        for (const g of page.querySelectorAll('g[id^="editor-"]')) {
          if (/-bg$|-paragraph$/.test(g.id)) continue;
          if (els.some((e) => e.contains(g) || g.contains(e))) continue;
          if (taken.some((t) => t.contains(g))) continue;
          let k = -1;
          sorted.forEach((e, r) => { if (e.compareDocumentPosition(g) & Node.DOCUMENT_POSITION_FOLLOWING) k = r; });
          if (k < 0) continue; // below every edited shape: the real slide shows it
          const cs = getComputedStyle(g);
          if (cs.visibility === 'hidden' || cs.display === 'none') continue;
          taken.push(g);
          gaps[k].push(g);
        }
        const refs = new Set();
        const gapEls = gaps.map((list) => {
          const gap = sv('g', { class: 'cover', 'pointer-events': 'none' });
          list.forEach((g) => {
            const parent = g.parentNode && g.parentNode.getScreenCTM ? g.parentNode.getScreenCTM() : null;
            const rel = parent ? SB.matMul(pageInv, [parent.a, parent.b, parent.c, parent.d, parent.e, parent.f]) : [1, 0, 0, 1, 0, 0];
            const wrap = sv('g', { transform: 'matrix(' + rel.join(' ') + ')' });
            const copy = g.cloneNode(true);
            inlineComputedStyles(g, copy);
            copy.style.visibility = 'visible';
            wrap.append(copy);
            gap.append(wrap);
            [copy, ...copy.querySelectorAll('*')].forEach((n) => {
              for (const a of ['clip-path', 'mask', 'fill', 'stroke', 'filter', 'href', 'xlink:href']) {
                const v = n.getAttribute(a);
                const m = v && /^url\(["']?#([^"')]+)["']?\)$/.exec(v);
                if (m) refs.add(m[1]);
                else if (v && (a === 'href' || a === 'xlink:href') && v[0] === '#') refs.add(v.slice(1));
              }
            });
          });
          return gap;
        });
        refs.forEach((id) => {
          if (gapEls.some((gp) => gp.querySelector('#' + CSS.escape(id)))) return;
          const src = document.getElementById(id);
          if (src) this.gDefs.append(src.cloneNode(true));
        });
        this.coverGaps = gapEls;
        this.updateCoverTransforms();
      } catch (err) {
        console.warn('[svg2slides] could not copy shapes stacked with the edited ones', err);
        this.coverGaps = [];
      }
    }

    updateCoverTransforms() {
      (this.coverGaps || []).forEach((gp) => gp.setAttribute('transform', 'matrix(' + this.ctm.join(' ') + ')'));
    }

    // ── Zoom / pan ──
    // Zooming happens inside the editor, not in Slides. While the view is
    // not identity, a static clone of the slide is shown behind the editing
    // layer with the same transform, so the rest of the slide zooms too.
    findPageSvg() {
      const page = SB.currentPageGroup();
      this.pageSvg = page ? page.ownerSVGElement : null;
      // The visible canvas, not #workspace: at high Slides zoom #workspace
      // is the whole page and starts far off-screen, which once clipped the
      // editor to a sliver and hid it.
      const ws = document.getElementById('workspace-container') || document.getElementById('workspace') || (this.pageSvg && this.pageSvg.parentElement);
      this.wsRect = SB.visibleWorkspaceRect();
      let bgc = '';
      for (let n = ws; n && n.nodeType === 1; n = n.parentElement) {
        const c = getComputedStyle(n).backgroundColor;
        if (c && c !== 'transparent' && !/rgba\(.*,\s*0\)$/.test(c)) { bgc = c; break; }
      }
      this.wsBg = bgc || '#f9fbfd';
    }

    clipInset() {
      const r = this.wsRect;
      return `inset(${r.top}px ${Math.max(0, innerWidth - r.right)}px ${Math.max(0, innerHeight - r.bottom)}px ${r.left}px)`;
    }

    isIdentityView() {
      const v = this.view;
      return Math.abs(v.s - 1) < 1e-6 && Math.abs(v.tx) < 0.5 && Math.abs(v.ty) < 0.5;
    }

    updateZoomLayer() {
      if (this.isIdentityView()) {
        if (this.zoomLayer) this.zoomLayer.style.display = 'none';
        return;
      }
      if (!this.zoomLayer) this.buildZoomLayer();
      if (!this.zoomLayer) return;
      const v = this.view;
      this.zoomLayer.style.display = '';
      this.zoomInner.style.transform = `matrix(${v.s},0,0,${v.s},${v.tx},${v.ty})`;
    }

    // Light DOM (not the shadow root) so Slides' own CSS still styles the
    // clone. Editor ids are stripped so nothing resolves to the copy.
    buildZoomLayer() {
      if (!this.pageSvg) return;
      const r = this.pageSvg.getBoundingClientRect();
      const clone = this.pageSvg.cloneNode(true);
      clone.querySelectorAll('[id^="editor-"]').forEach((n) => n.removeAttribute('id'));
      clone.style.cssText = `position:absolute;left:${r.left}px;top:${r.top}px;width:${r.width}px;height:${r.height}px;`;
      const inner = el('div');
      inner.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0;transform-origin:0 0;';
      inner.append(clone);
      const layer = el('div', { id: 'svg2slides-zoom-layer' });
      layer.style.cssText = `position:fixed;inset:0;z-index:2147482999;pointer-events:none;background:${this.wsBg};clip-path:${this.clipInset()};`;
      layer.append(inner);
      document.documentElement.appendChild(layer);
      this.zoomLayer = layer;
      this.zoomInner = inner;
    }

    dropZoomLayer() {
      if (this.zoomLayer) this.zoomLayer.remove();
      this.zoomLayer = null;
      this.zoomInner = null;
      this.findPageSvg();
      if (this.svg) this.svg.style.clipPath = this.clipInset();
    }

    // Slides' own zoom range (25–1000%), so Done can hand the exact view
    // back to Slides. view.s is relative to the zoom the editor opened at.
    basePct() { return SB.zoomPctFromCTM(this.baseCTM); }
    clampScale(s) {
      const b = this.basePct();
      return Math.min(SB.ZOOM_MAX / b, Math.max(SB.ZOOM_MIN / b, s));
    }

    zoomAt(cx, cy, factor) {
      const v = this.view;
      const s = this.clampScale(v.s * factor);
      const f = s / v.s;
      v.tx = cx - f * (cx - v.tx);
      v.ty = cy - f * (cy - v.ty);
      v.s = s;
      this.applyView();
      this.render();
    }

    zoomStep(factor) {
      const r = this.wsRect;
      this.zoomAt((r.left + r.right) / 2, (r.top + r.bottom) / 2, factor);
    }

    resetView() {
      this.view = { s: 1, tx: 0, ty: 0 };
      this.applyView();
      this.render();
    }

    // Fit the shapes being edited into ~70% of the workspace.
    fitView() {
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      this.shapes.forEach((s) => {
        const M = SB.matMul(this.baseCTM, s.toPage);
        s.subs.forEach((sp) => sp.nodes.forEach((n) => [n, n.in, n.out].forEach((p) => {
          if (!p) return;
          const q = SB.apply(M, p.x, p.y);
          minX = Math.min(minX, q.x); maxX = Math.max(maxX, q.x);
          minY = Math.min(minY, q.y); maxY = Math.max(maxY, q.y);
        })));
      });
      if (!isFinite(minX)) return;
      const r = this.wsRect;
      const bw = Math.max(1, maxX - minX), bh = Math.max(1, maxY - minY);
      const s = this.clampScale(Math.min((r.right - r.left) * 0.7 / bw, (r.bottom - r.top) * 0.7 / bh));
      this.view = {
        s,
        tx: (r.left + r.right) / 2 - s * (minX + maxX) / 2,
        ty: (r.top + r.bottom) / 2 - s * (minY + maxY) / 2,
      };
      this.applyView();
      this.render();
    }

    onWheel(e) {
      e.preventDefault();
      if (this.committing) return;
      if (e.ctrlKey || e.metaKey) {
        // Trackpad pinch arrives as ctrl+wheel with small deltas; ⌘/ctrl
        // + mouse wheel has large ones.
        const k = (e.ctrlKey && !e.metaKey && Math.abs(e.deltaY) < 50) ? 0.01 : 0.002;
        this.zoomAt(e.clientX, e.clientY, Math.exp(-e.deltaY * k));
        return;
      }
      let dx = e.deltaX, dy = e.deltaY;
      if (e.shiftKey && !dx) { dx = dy; dy = 0; }
      this.view.tx -= dx;
      this.view.ty -= dy;
      this.applyView();
      this.render();
    }

    setPanCursor(state) {
      this.svg.style.cursor = state || '';
    }

    // ── DOM ──
    // A compact vertical rail docked at the workspace's left edge, styled
    // like Slides' own toolbar (surface pill, 32px icon buttons, GM3
    // colours). It fades back when the pointer isn't on it. Shortcuts live
    // in tooltips; a single hint shows briefly on open and on tool change.
    buildDOM() {
      this.host = document.createElement('div');
      this.host.id = 'svg2slides-editor';
      this.host.tabIndex = -1;
      this.host.style.cssText = 'position:fixed;inset:0;z-index:2147483000;outline:none;';
      const root = this.host.attachShadow({ mode: 'open' });
      root.append(styleEl(`
          :host { all: initial; }
          svg.stage { position: fixed; inset: 0; width: 100vw; height: 100vh; cursor: default; }
          svg.stage.pen { cursor: crosshair; }
          ${RK.CSS}
          .btn.dim[data-act="undo"], .btn.dim[data-act="redo"] { pointer-events: none; }
          .hint { position: fixed; z-index: 2; pointer-events: none; background: ${GM.tooltip}; color: ${GM.onTooltip};
                  font: 400 12px/16px ${FONT}; padding: 6px 10px; border-radius: 4px; white-space: nowrap;
                  opacity: 0; transition: opacity .25s; }
          .hint.show { opacity: .94; }
          .rpill { position: fixed; z-index: 2; display: none; align-items: center; gap: 6px; height: 30px; padding: 0 10px 0 12px;
                   background: ${GM.tooltip}; color: ${GM.onTooltip}; border-radius: 15px; box-shadow: ${GM.elev2};
                   font: 500 12px/1 ${FONT}; user-select: none; white-space: nowrap; transform: translateX(-50%); }
          .rpill.show { display: flex; }
          .rpill .ic { width: 14px; height: 14px; display: block; opacity: .8; }
          .rpill input { width: 40px; height: 20px; box-sizing: border-box; border: 0; border-radius: 4px; padding: 0 4px;
                   background: rgba(255,255,255,.12); color: inherit; font: 500 12px/1 ${FONT}; text-align: right;
                   -moz-appearance: textfield; }
          .rpill input::-webkit-inner-spin-button, .rpill input::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
          .rpill input::placeholder { color: rgba(242,242,242,.6); }
          .rpill input:focus { outline: 1px solid #a8c7fa; background: rgba(255,255,255,.18); }
          .rpill .u { opacity: .7; margin-left: -2px; }
          .rpill .sc { opacity: .7; padding-left: 8px; border-left: 1px solid rgba(255,255,255,.25); }
          .rpill.live input { background: transparent; }
          .rpill .seg { display: flex; align-items: center; gap: 6px; }
          .rpill .seg + .seg { border-left: 1px solid rgba(255,255,255,.25); padding-left: 10px; }
          .rpill .lb { opacity: .7; }
          .rpill .pb { width: 22px; height: 22px; border-radius: 50%; border: 0; padding: 0; display: grid; place-items: center; cursor: pointer;
            background: rgba(255,255,255,.14); color: #f2f2f2; }
          .rpill .pb svg { width: 14px; height: 14px; display: block; }
          .rpill .pb:hover { background: rgba(255,255,255,.26); }
          .rpill .pb.ok { background: #a8c7fa; color: #062e6f; }
          .rpill .pb.ok:hover { background: #c2d9fc; }
          .rpill .pb[disabled] { opacity: .35; cursor: default; pointer-events: none; }
          .rpill .seg.act { gap: 6px; }
          .anchors, .handles, .cornerh { filter: drop-shadow(0 0 1px rgba(0,0,0,.35)) drop-shadow(0 1px 2px rgba(0,0,0,.18)); }`));

      const svg = sv('svg', { class: 'stage' });
      ['defs', 'grid', 'fills', 'outlines', 'xform', 'handles', 'anchors', 'cornerh', 'guides'].forEach((c) => svg.append(sv(c === 'defs' ? 'defs' : 'g', { class: c, 'pointer-events': c === 'grid' || c === 'guides' ? 'none' : null })));
      svg.append(
        sv('rect', { class: 'marquee', fill: 'rgba(11,87,208,.08)', stroke: ACCENT, 'stroke-width': 1, visibility: 'hidden' }),
        sv('circle', { class: 'pen-ghost', r: 4, fill: ACCENT, visibility: 'hidden' }),
        sv('path', { class: 'pen-rubber', fill: 'none', stroke: ACCENT, 'stroke-width': 1.5, 'stroke-dasharray': '4 3', visibility: 'hidden', 'pointer-events': 'none' }),
        sv('circle', { class: 'pen-close', r: 9, fill: 'none', stroke: ACCENT, 'stroke-width': 2, visibility: 'hidden', 'pointer-events': 'none' })
      );

      const icon = (viewBox, d, rule) => {
        const s = sv('svg', { viewBox, 'aria-hidden': 'true' });
        s.append(sv('path', Object.assign({ d, fill: 'currentColor' }, rule ? { 'fill-rule': rule } : {})));
        return s;
      };
      // Undo/redo/minus are Slides' own GM3 glyphs, lifted from its sprite
      // sheet (viewBox = the glyph's cell in that sheet). The others are
      // drawn to the same 20px grid and weight.
      const I = {
        select: icon('0 0 20 20', 'M5.5 2.5v13.3l3.4-3.2 2.3 5 1.9-.9-2.3-4.9h4.6Z'),
        pen: icon('0 0 20 20', 'M10 2l5.5 7.5-3 6h-5l-3-6Zm0 6.2a1.6 1.6 0 1 0 0 3.2 1.6 1.6 0 0 0 0-3.2ZM7.5 16.75h5V18.25h-5Z', 'evenodd'),
        undo: icon('7028 94 20 20', 'M7034 110v-1.5h6q1.042 0 1.771-.729t.729-1.771-.729-1.771-1.771-.729h-5.125l1.937 1.938-1.062 1.062-3.75-3.75 3.75-3.75 1.062 1.062-1.937 1.938H7040q1.667 0 2.833 1.167Q7044 104.333 7044 106t-1.167 2.833Q7041.667 110 7040 110Z'),
        redo: icon('1064 94 20 20', 'M1072 110q-1.667 0-2.833-1.167Q1068 107.667 1068 106t1.167-2.833Q1070.333 102 1072 102h5.125l-1.937-1.938L1076.25 99l3.75 3.75-3.75 3.75-1.062-1.062 1.937-1.938H1072q-1.042 0-1.771.729T1069.5 106t.729 1.771 1.771.729h6v1.5Z'),
        minus: icon('1154 94 20 20', 'M1159 104.75v-1.5h10v1.5Z'),
        plus: icon('1154 94 20 20', 'M1163.25 109v-4.25H1159v-1.5h4.25V99h1.5v4.25H1169v1.5h-4.25V109Z'),
        done: icon('0 0 20 20', 'M8 13.6 4.4 10l-1.05 1.05L8 15.7l9-9-1.05-1.05Z'),
        corners: icon('0 0 20 20', 'M4.25 17V9.5A5.25 5.25 0 0 1 9.5 4.25H17v1.5H9.5A3.75 3.75 0 0 0 5.75 9.5V17Z'),
        close: icon('0 0 20 20', 'M6.06 15 5 13.94 8.94 10 5 6.06 6.06 5 10 8.94 13.94 5 15 6.06 11.06 10 15 13.94 13.94 15 10 11.06Z'),
      };
      const MODK = SB.IS_MAC ? '⌘' : 'Ctrl+';
      this.rk = RK.mountRail(root, [
        [{ act: 'select', tip: 'Select points', key: 'V', node: I.select }, { act: 'pen', tip: 'Pen: draw shapes, add / remove points', key: 'P', node: I.pen },
          { act: 'snap', tip: 'Snapping (hold ' + (SB.IS_MAC ? '⌘' : 'Ctrl') + ' while dragging to ignore it)', key: '', fly: [
            { act: 'snapPoints', tip: 'Snap to points, their lines and the slide’s edges and centre' },
            { act: 'snapPx', tip: 'Snap to whole pixels' },
            { act: 'snapGrid', tip: 'Snap to the grid (shows it)', key: (SB.IS_MAC ? '⌘' : 'Ctrl+') + "'" },
            { act: 'snapSize', field: true, icon: 'snapGrid', unit: 'px', step: 1, tip: 'Grid size' },
          ] }],
      ], [
        [{ act: 'undo', tip: 'Undo', key: MODK + 'Z', node: I.undo }, { act: 'redo', tip: 'Redo', key: (SB.IS_MAC ? '⇧⌘' : 'Ctrl+Shift+') + 'Z', node: I.redo }],
        [{ act: 'zoomreset', tip: 'Fit / reset zoom (pinch or ' + MODK + '+ / ' + MODK + '− to zoom)', key: '⇧1 · ' + MODK + '0', text: '100%', span: true }],
        [{ act: 'cancel', tip: 'Discard changes', key: 'Esc', node: I.close }, { act: 'done', tip: 'Done', key: '↵', node: I.done, cls: 'done' }],
      ], (act, info) => this.onRailAct(act, info), {
        label: 'Edit Shape', onEnter: () => this.updateRailState(),
        onField: (act, v, how) => this.onField(act, v, how),
        onFieldBlur: () => { this._fieldTyping = false; this.host.focus(); },
      });
      const rail = this.rk.rail;
      this.zoomLabel = true;
      const hint = el('div', { class: 'hint' });
      // Corner radius pill: shows under the shape while corner handles are
      // visible. Live value while dragging a handle; type a px value too.
      const rIcon = sv('svg', { class: 'ic', viewBox: '0 0 20 20', 'aria-hidden': 'true' });
      rIcon.append(sv('path', { d: 'M4.25 17V9.5A5.25 5.25 0 0 1 9.5 4.25H17v1.5H9.5A3.75 3.75 0 0 0 5.75 9.5V17Z', fill: 'currentColor' }));
      const rNum = el('input', { type: 'number', min: '0', step: '1', 'aria-label': 'Corner radius in px' });
      const rScope = el('span', { class: 'sc' }, 'All corners');
      // Precise values for what's in scope: corner radius (when there are
      // corners), width and height in px, and rotate by degrees.
      const num = (label) => el('input', { type: 'number', step: 'any', 'aria-label': label });
      const wNum = num('Width in px'), hNum = num('Height in px'), aNum = num('Rotate by degrees');
      aNum.placeholder = '0';
      const segR = el('span', { class: 'seg', 'data-tip': 'Corner radius · ⌥-drag to scrub' }, rIcon, rNum, el('span', { class: 'u' }, 'px'), rScope);
      const wLb = el('span', { class: 'lb', 'data-tip': 'Width · ⌥-drag to scrub' }, 'W'), hLb = el('span', { class: 'lb', 'data-tip': 'Height · ⌥-drag to scrub' }, 'H');
      wNum.dataset.tip = 'Width · ⌥-drag to scrub'; hNum.dataset.tip = 'Height · ⌥-drag to scrub';
      const segS = el('span', { class: 'seg' }, wLb, wNum, hLb, hNum, el('span', { class: 'u' }, 'px'));
      const aIcon = sv('svg', { class: 'ic', viewBox: '0 0 20 20', 'aria-hidden': 'true' });
      aIcon.append(sv('path', { d: 'M10 3.5a6.5 6.5 0 1 0 6.5 6.5H15a5 5 0 1 1-5-5v2.3l3.2-3-3.2-3Z', fill: 'currentColor' }));
      const segA = el('span', { class: 'seg', 'data-tip': 'Rotate by (type and press ↵) · ⌥-drag to scrub', 'data-key': SB.SHORTCUT_LABEL.rotL15 + ' ' + SB.SHORTCUT_LABEL.rotR15 }, aIcon, aNum, el('span', { class: 'u' }, '°'));
      // Keep or drop what the pill changed. Everything typed or scrubbed in
      // the pill applies live; ✓ (or ↵) keeps it, ✕ (or Esc) puts the shape
      // back as it was when the pill was first touched.
      const pillBtn = (cls, tip, key, d) => {
        const b = el('button', { class: 'pb ' + cls, type: 'button', 'aria-label': tip, 'data-tip': tip, 'data-key': key });
        const g = sv('svg', { viewBox: '0 0 20 20', 'aria-hidden': 'true' });
        g.append(sv('path', { d, fill: 'none', stroke: 'currentColor', 'stroke-width': '2.2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
        b.append(g);
        return b;
      };
      const pNo = pillBtn('no', 'Cancel these changes', 'Esc', 'M5.5 5.5l9 9M14.5 5.5l-9 9');
      const pOk = pillBtn('ok', 'Keep these changes', '↵', 'M4.5 10.5l3.6 3.6 7.4-8');
      const segOk = el('span', { class: 'seg act' }, pNo, pOk);
      const rpill = el('div', { class: 'rpill', role: 'group', 'aria-label': 'Size, rotation and corner radius' }, segR, segS, segA, segOk);
      this.pNo = pNo; this.pOk = pOk;
      pNo.addEventListener('click', (e) => { e.stopPropagation(); this.cancelPill(); });
      pOk.addEventListener('click', (e) => { e.stopPropagation(); this.commitPill(); });
      this.segR = segR; this.wNum = wNum; this.hNum = hNum; this.aNum = aNum;
      const sizeInput = (inp, axis) => {
        inp.addEventListener('focus', () => { this._sizeBase = null; });
        inp.addEventListener('input', () => {
          const v = parseFloat(inp.value);
          if (!Number.isFinite(v) || v <= 0) return;
          if (!this._sizeBase) { this.pushUndo(); this._sizeBase = { box: this.scopeBBox(), subs: clone(this.shapes.map((s) => s.subs)) }; }
          const b = this._sizeBase.box;
          if (!b) return;
          const cur = axis === 'x' ? b.maxX - b.minX : b.maxY - b.minY;
          if (cur < 1e-6) return;
          const f = (v * 381) / cur;
          const S = axis === 'x' ? [f, 0, 0, 1, 0, 0] : [1, 0, 0, f, 0, 0];
          this.transformScope(SB.matMul([1, 0, 0, 1, b.minX, b.minY], SB.matMul(S, [1, 0, 0, 1, -b.minX, -b.minY])), this._sizeBase.subs);
          this.render();
        });
        inp.addEventListener('blur', () => { this._sizeBase = null; });
      };
      sizeInput(wNum, 'x');
      sizeInput(hNum, 'y');
      [rNum, wNum, hNum, aNum].forEach((inp) => inp.addEventListener('focus', () => setTimeout(() => inp.select(), 0)));
      aNum.addEventListener('keydown', (e) => {
        if (e.key !== 'Enter') return;
        const v = parseFloat(aNum.value);
        if (Number.isFinite(v) && v) this.rotateBy(v);
        aNum.value = '';
      });
      // ⌥-drag scrubbing. Width and height go through their input handlers
      // (one undo step per drag); rotation turns live from where it started.
      RK.scrub(wLb, wNum, { step: 1, min: 1, onStart: () => { this._sizeBase = null; }, onEnd: () => { this._sizeBase = null; this.updatePill(); } });
      RK.scrub(hLb, hNum, { step: 1, min: 1, onStart: () => { this._sizeBase = null; }, onEnd: () => { this._sizeBase = null; this.updatePill(); } });
      RK.scrub(wNum, wNum, { step: 1, min: 1, onStart: () => { this._sizeBase = null; }, onEnd: () => { this._sizeBase = null; this.updatePill(); } });
      RK.scrub(hNum, hNum, { step: 1, min: 1, onStart: () => { this._sizeBase = null; }, onEnd: () => { this._sizeBase = null; this.updatePill(); } });
      RK.scrub(segR, rNum, { step: 0.5, min: 0, onStart: () => { this._rTyping = false; }, onEnd: () => { this._rTyping = false; } });
      let rot0 = null;
      RK.scrub(segA, aNum, {
        step: 0.5,
        onStart: () => { const b = this.scopeBBox(); if (!b) return; this.pushUndo(); rot0 = { b, base: clone(this.shapes.map((x) => x.subs)) }; },
        onValue: (v) => {
          if (!rot0) return;
          const r = v * Math.PI / 180, c = Math.cos(r), sn = Math.sin(r);
          this.transformScope(this.about(rot0.b.cx, rot0.b.cy, [c, sn, -sn, c, 0, 0]), rot0.base);
          this.render();
        },
        onEnd: () => { rot0 = null; aNum.value = ''; },
      });
      root.prepend(svg);
      root.append(rpill, hint);
      this.rk.attachTips(rpill, 'above');
      this.rpill = rpill;
      this.rNum = rNum;
      this.rScope = rScope;
      rpill.addEventListener('pointerdown', (e) => { e.stopPropagation(); this.hideHint(); if (!e.target.closest('.pb')) this.markPill(); }, true);
      rpill.addEventListener('focusin', () => this.markPill());
      rpill.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); this.cancelPill(); }
        else if (e.key === 'Enter' && e.target !== aNum) { e.preventDefault(); e.stopPropagation(); this.commitPill(); }
      });
      rNum.addEventListener('focus', () => { this._rTyping = false; });
      rNum.addEventListener('input', () => {
        const v = parseFloat(rNum.value);
        if (!Number.isFinite(v) || v < 0) return;
        if (!this._rTyping) { this.pushUndo(); this._rTyping = true; }
        this.setRadius(this.cornerScope(), v * 381);
      });
      rNum.addEventListener('blur', () => { this._rTyping = false; });

      this.root = root;
      this.svg = svg;
      this.gFills = svg.querySelector('.fills');
      this.gOutlines = svg.querySelector('.outlines');
      this.gHandles = svg.querySelector('.handles');
      this.gAnchors = svg.querySelector('.anchors');
      this.gDefs = svg.querySelector('defs');
      this.gCorners = svg.querySelector('.cornerh');
      this.gGrid = svg.querySelector('.grid');
      this.gGuides = svg.querySelector('.guides');
      this.marquee = svg.querySelector('.marquee');
      this.penGhost = svg.querySelector('.pen-ghost');
      this.penRubber = svg.querySelector('.pen-rubber');
      this.penClose = svg.querySelector('.pen-close');
      this.rail = rail;
      this.hint = hint;
      this.gXform = svg.querySelector('.xform');

      this.scheduleIdle(2500);

      svg.addEventListener('pointerdown', (e) => { this.hideHint(); this.commitPill(true); this.onDown(e); });
      svg.addEventListener('dblclick', (e) => this.onDbl(e));
      window.addEventListener('pointermove', this._mv = (e) => this.onMove(e), true);
      window.addEventListener('pointerup', this._up = (e) => this.onUp(e), true);
      this.host.addEventListener('keydown', (e) => { this.onKey(e); e.stopPropagation(); });
      this.host.addEventListener('keyup', (e) => { this.onKeyUp(e); e.stopPropagation(); });
      this.host.addEventListener('wheel', (e) => this.onWheel(e), { passive: false });
      this.host.addEventListener('contextmenu', (e) => e.preventDefault());
      svg.style.clipPath = this.clipInset();

      document.documentElement.appendChild(this.host);
      this.host.focus();
      this.placeRail();
      this.setTool('direct');
      this.applyView(); // fills in the zoom label
      this.flashHint('Drag points or handles · ⇧ constrain · ⌥ break handle · double-click point: smooth/corner · pinch to zoom, Space-drag to pan', 5000);
    }

    placeRail() {
      this.rk.place(this.wsRect);
    }

    scheduleIdle(ms) {
      if (this.rk) this.rk.scheduleIdle(ms);
    }
    hideTip() {
      if (this.rk) this.rk.hideTip();
    }

    hideHint() {
      clearTimeout(this._hintT);
      if (this.hint) this.hint.classList.remove('show');
    }

    flashHint(text, ms) {
      const r = this.wsRect;
      this.hint.textContent = text;
      this.hint.style.left = (r.left + 64) + 'px';
      this.hint.style.top = (r.bottom - 44) + 'px';
      this.hint.classList.add('show');
      clearTimeout(this._hintT);
      this._hintT = setTimeout(() => this.hint.classList.remove('show'), ms);
    }

    // Slides draws its selection box/handles in a layer that is a sibling
    // of the page group. Hide it while editing so only our handles show.
    hideSlidesChrome() {
      this.chrome = [];
      const hide = (c) => { this.chrome.push([c, c.style.visibility]); c.dataset.svg2slidesHidden = c.style.visibility || '-'; c.style.visibility = 'hidden'; };
      const page = SB.currentPageGroup();
      if (!page) return;
      // Selection box + handles live in a separate <svg> layer that is a
      // direct child of #workspace (seen live, Nov 2026). Hide every such
      // layer that doesn't hold the slide itself.
      const ws = document.getElementById('workspace');
      if (ws) {
        Array.from(ws.children).forEach((c) => {
          if (c.tagName.toLowerCase() === 'svg' && !c.contains(page)) hide(c);
        });
      }
      // Older render path: chrome as a sibling of the page group.
      const wrap = page.parentNode;
      Array.from(wrap.children).forEach((c) => {
        if (c !== page && c.tagName.toLowerCase() === 'g') hide(c);
      });
    }
    restoreSlidesChrome() {
      (this.chrome || []).forEach(([c, v]) => { c.style.visibility = v || ''; delete c.dataset.svg2slidesHidden; });
      this.chrome = [];
    }

    setTool(t) {
      const changed = this.tool !== t;
      this.tool = t;
      this.rk.setOn('select', t === 'direct');
      this.rk.setOn('pen', t === 'pen');
      this.svg.classList.toggle('pen', t === 'pen');
      this.penGhost.setAttribute('visibility', 'hidden');
      if (t !== 'pen') this.finishDrawing();
      if (changed && t === 'pen') this.flashHint(this.shapes.some((sh) => !sh.added)
        ? 'Click anywhere to draw · drag for curves · click the first point to close · on a shape: click a segment to add a point, a point to remove it'
        : 'Click anywhere to draw · drag for curves · click the first point to close · ↵ to finish', 4500);
    }

    // ── Pen: draw new shapes ──
    // Click places a corner, click-drag pulls out a smooth curve (⌥ while
    // dragging breaks the handles), a click on the path's first point
    // closes it, and ↵ or Esc leaves it open. Each path is a new shape,
    // stroked like the last one drawn; clicking the end of an open path
    // (new or old) carries on drawing it.
    addNewShape() {
      const id = SB.newId();
      const paint = Object.assign({ fill: '#FFFFFF', filled: false, stroke: '#1F1F1F', weight: 2 * 381, strokeOn: true }, this.penPaint || {});
      const entry = [3, id, 1, [1, 0, 0, 1, 0, 0], [8, 1, 9, 1, 12, [[1, 1, [], [], [], 0]], 14, 0, 15, paint.fill, 18, 1, 19, paint.stroke, 22, paint.weight]];
      this.resolved.push(entry);
      const shape = { entry, id, src: id, subs: [], toPage: [1, 0, 0, 1, 0, 0], paint, added: true, drawnHere: true };
      this.shapes.push(shape);
      this.zRank = this.zRank || [];
      this.zRank.push((this.coverGaps || []).length + this.shapes.length); // above everything
      this.applyView();
      return this.shapes.length - 1;
    }
    finishDrawing() {
      const d = this.drawing;
      this.drawing = null;
      if (this.penRubber) { this.penRubber.setAttribute('visibility', 'hidden'); this.penClose.setAttribute('visibility', 'hidden'); }
      this.showGuides(null);
      if (!d) return;
      const s = this.shapes[d.si];
      const sp = s && s.subs[d.pi];
      if (sp && sp.nodes.length < 2) {
        // A lone point isn't a path: take it away again.
        s.subs.splice(d.pi, 1);
        if (!s.subs.length && s.drawnHere) {
          this.resolved = this.resolved.filter((e) => e !== s.entry && !(e[0] === 3 && e[1] === s.id));
          this.shapes.splice(d.si, 1);
          if (this.zRank) this.zRank.splice(d.si, 1);
          this.applyView();
        }
      }
      if (s && s.drawnHere) this.penPaint = Object.assign({}, s.paint);
      this.sel.clear();
      this.render();
    }
    penPoint(s, x, y) { return this.local(s, { x, y }); }
    penDown(x0, y0, e) {
      // Points snap where they land (the path's own first point included,
      // so a snapped close is exact); a click on the first point closes.
      const tg = this.snapTargets(null);
      const q = this.snapScreen(x0, y0, tg, e);
      this.showGuides(null);
      const x = q.x, y = q.y;
      const d = this.drawing;
      if (d) {
        const s = this.shapes[d.si], sp = s.subs[d.pi];
        const first = this.screen(s, sp.nodes[0]);
        this.pushUndo();
        if (sp.nodes.length >= 2 && Math.hypot(first.x - x0, first.y - y0) <= 9) {
          sp.closed = true;
          this.drag = { kind: 'pen', si: d.si, pi: d.pi, ni: 0, start: { x, y }, pushed: true, closing: true };
          this.drawing = null;
          this.penRubber.setAttribute('visibility', 'hidden');
          this.penClose.setAttribute('visibility', 'hidden');
          if (s.drawnHere) this.penPaint = Object.assign({}, s.paint);
        } else {
          sp.nodes.push(Object.assign(this.penPoint(s, x, y), { in: null, out: null }));
          this.drag = { kind: 'pen', si: d.si, pi: d.pi, ni: sp.nodes.length - 1, start: { x, y }, pushed: true };
        }
        this.sel = new Set([this.key(this.drag.si, this.drag.pi, this.drag.ni)]);
        this.render();
        return;
      }
      const nk = this.hitNode(x0, y0);
      if (nk) {
        const h = this.nodeAt(nk);
        const L = h.sp.nodes.length;
        if (!h.sp.closed && !e.altKey && (h.ni === 0 || h.ni === L - 1)) {
          // The end of an open path: carry on from there.
          this.pushUndo();
          if (h.ni === 0 && L > 1) h.sp.nodes = h.sp.nodes.reverse().map((n) => Object.assign({}, n, { in: n.out, out: n.in }));
          this.drawing = { si: h.si, pi: h.pi };
          this.sel = new Set([this.key(h.si, h.pi, h.sp.nodes.length - 1)]);
          this.render();
          return;
        }
        this.pushUndo();
        if (e.altKey) this.toggleSmooth(nk);
        else this.deleteNodes(new Set([nk]));
        this.render();
        return;
      }
      const seg = this.hitSegment(x0, y0);
      if (seg) {
        this.pushUndo();
        const k = this.splitSegment(seg);
        this.sel = new Set([k]);
        this.render();
        return;
      }
      // Empty space: a new path.
      this.pushUndo();
      const si = this.addNewShape();
      const s = this.shapes[si];
      s.subs.push({ closed: false, nodes: [Object.assign(this.penPoint(s, x, y), { in: null, out: null })] });
      this.drawing = { si, pi: s.subs.length - 1 };
      this.drag = { kind: 'pen', si, pi: s.subs.length - 1, ni: 0, start: { x, y }, pushed: true };
      this.sel = new Set([this.key(si, s.subs.length - 1, 0)]);
      this.render();
    }
    // Dragging out of a pen click pulls the point's handles: the out handle
    // follows the pointer, the in handle mirrors it (⌥: only the out one).
    penDrag(x, y, e) {
      const dr = this.drag;
      const s = this.shapes[dr.si];
      const n = s && s.subs[dr.pi] && s.subs[dr.pi].nodes[dr.ni];
      if (!n) return;
      if (!dr.moved && Math.hypot(x - dr.start.x, y - dr.start.y) < 3) return;
      dr.moved = true;
      let tx = x, ty = y;
      if (e.shiftKey) { const a = this.screen(s, n); const q = snap45(x - a.x, y - a.y); tx = a.x + q.x; ty = a.y + q.y; }
      else {
        if (!dr.targets) dr.targets = this.snapTargets(new Set([this.key(dr.si, dr.pi, dr.ni)]));
        const q = this.snapScreen(x, y, dr.targets, e); tx = q.x; ty = q.y;
      }
      const p = this.penPoint(s, tx, ty);
      if (dr.closing) {
        // Closing on the first point: the pointer sets the curve coming in.
        n.in = { x: 2 * n.x - p.x, y: 2 * n.y - p.y };
        if (!e.altKey) n.out = { x: p.x, y: p.y };
      } else {
        n.out = p;
        n.in = e.altKey ? n.in : { x: 2 * n.x - p.x, y: 2 * n.y - p.y };
      }
      n.smooth = !e.altKey;
    }
    // The dashed segment from the last point to the pointer, and a ring on
    // the first point when a click there would close the path.
    drawRubber(x, y) {
      const d = this.drawing;
      if (!d || this.tool !== 'pen') { this.penRubber.setAttribute('visibility', 'hidden'); this.penClose.setAttribute('visibility', 'hidden'); return; }
      const s = this.shapes[d.si], sp = s && s.subs[d.pi];
      if (!sp || !sp.nodes.length) return;
      const last = sp.nodes[sp.nodes.length - 1];
      const a = this.screen(s, last), c = last.out ? this.screen(s, last.out) : null;
      const first = this.screen(s, sp.nodes[0]);
      const closing = sp.nodes.length >= 2 && Math.hypot(first.x - x, first.y - y) <= 9;
      let tx = x, ty = y;
      if (closing) { tx = first.x; ty = first.y; this.showGuides(null); }
      else {
        if (!this._rubberT || this._rubberT.n !== sp.nodes.length) this._rubberT = { n: sp.nodes.length, t: this.snapTargets(null) };
        const q = this.snapScreen(x, y, this._rubberT.t, this._lastMoveEvt); tx = q.x; ty = q.y;
      }
      this.penRubber.setAttribute('d', c ? `M${a.x} ${a.y}C${c.x} ${c.y} ${tx} ${ty} ${tx} ${ty}` : `M${a.x} ${a.y}L${tx} ${ty}`);
      this.penRubber.setAttribute('visibility', 'visible');
      this.penClose.setAttribute('cx', first.x); this.penClose.setAttribute('cy', first.y);
      this.penClose.setAttribute('visibility', closing ? 'visible' : 'hidden');
    }

    updateUndoButtons() {
      this.root.querySelector('[data-act="undo"]').classList.toggle('dim', !this.undo.length);
      this.root.querySelector('[data-act="redo"]').classList.toggle('dim', !this.redo.length);
      this.syncPillButtons();
    }

    // ── Model iteration ──
    eachNode(fn) {
      this.shapes.forEach((s, si) => s.subs.forEach((sp, pi) => sp.nodes.forEach((n, ni) => fn(n, s, si, pi, ni, sp))));
    }
    key(si, pi, ni) { return si + ':' + pi + ':' + ni; }
    nodeAt(k) {
      const [si, pi, ni] = k.split(':').map(Number);
      const s = this.shapes[si];
      const sp = s && s.subs[pi];
      const n = sp && sp.nodes[ni];
      return n ? { s, sp, n, si, pi, ni } : null;
    }
    screen(s, p) { return SB.apply(s.M, p.x, p.y); }
    local(s, p) { return SB.apply(s.Minv, p.x, p.y); }
    localVec(s, dx, dy) { const m = s.Minv; return { x: m[0] * dx + m[2] * dy, y: m[1] * dx + m[3] * dy }; }

    // The whole model, not just points: commands add, drop, regroup and
    // repaint shapes, and native Arrange moves the originals on the slide.
    snapshot() {
      return JSON.stringify({
        resolved: this.resolved, zRank: this.zRank, srcOf: this.srcOf,
        shapes: this.shapes.map((s) => ({ entry: s.entry, id: s.id, src: s.src, subs: s.subs, toPage: s.toPage, paint: s.paint, fix: s.fix || null, added: !!s.added, fromText: s.fromText || null })),
        slot: this.nativeArranged ? SB.topLevelOrder().indexOf(this.srcTop()) : null,
      });
    }
    pushUndo() {
      this.undo.push(this.snapshot());
      if (this.undo.length > 200) this.undo.shift();
      this.redo = [];
      this.dirty = true;
      this.updateUndoButtons();
    }
    restore(snap) {
      const o = JSON.parse(snap);
      this.resolved = o.resolved;
      this.zRank = o.zRank;
      this.srcOf = o.srcOf;
      this.shapes = o.shapes.map((s) => Object.assign({}, s, { fix: s.fix || undefined }));
      // Each shape's entry is the one in the restored payload.
      this.shapes.forEach((sh) => { const e = this.resolved.find((x) => x[0] === 3 && x[1] === sh.id); if (e) sh.entry = e; });
      this.sel.clear();
      if (this.drawing) {
        const sh = this.shapes[this.drawing.si], sp = sh && sh.subs[this.drawing.pi];
        if (!sp || sp.closed || !sp.nodes.length) this.drawing = null;
        if (this.penRubber) { this.penRubber.setAttribute('visibility', 'hidden'); this.penClose.setAttribute('visibility', 'hidden'); }
      }
      this.applyView();
      this.render();
      if (o.slot !== null && o.slot !== undefined && this.nativeArranged) {
        const top = this.srcTop();
        if (SB.topLevelOrder().indexOf(top) !== o.slot) this.nativeMoveTo(o.slot);
      }
    }
    doUndo() {
      if (!this.undo.length) return;
      this.redo.push(this.snapshot());
      this.restore(this.undo.pop());
      this.updateUndoButtons();
    }
    doRedo() {
      if (!this.redo.length) return;
      this.undo.push(this.snapshot());
      this.restore(this.redo.pop());
      this.updateUndoButtons();
    }

    // ── Rendering ──
    render() {
      if (this._raf) return;
      this._raf = requestAnimationFrame(() => { this._raf = null; this.draw(); });
    }

    draw() {
      const fills = [], outlines = [], handles = [], anchors = [];
      const k = this.pageScale();
      this.shapes.forEach((s, si) => {
        const d = SB.svgPathD(s.subs, s.M);
        const p = s.paint;
        // Slides fills every path even-odd. Inside/outside strokes draw the
        // moved outline (what Done will put on the slide).
        const al = this.alignedSubs(s);
        const f = sv('path', { 'data-si': si, d: al ? SB.svgPathD(al, s.M) : d, fill: p.filled ? p.fill : 'none', 'fill-rule': 'evenodd' });
        if (p.strokeOn) {
          f.setAttribute('stroke', p.stroke);
          f.setAttribute('stroke-width', Math.max(0.5, p.weight * k));
          f.setAttribute('stroke-linejoin', 'miter');
        } else if (!p.filled) f.setAttribute('stroke', p.fill);
        fills.push(f);
        outlines.push(sv('path', { d, fill: 'none', stroke: ACCENT, 'stroke-width': 1.5 }));
      });

      // Handles: selected nodes, plus the inner handles of their neighbours.
      const shown = new Set();
      this.sel.forEach((k) => {
        const h = this.nodeAt(k);
        if (!h) return;
        const { sp, ni, si, pi } = h;
        shown.add(this.key(si, pi, ni) + ':in');
        shown.add(this.key(si, pi, ni) + ':out');
        const L = sp.nodes.length;
        const prev = ni > 0 ? ni - 1 : (sp.closed ? L - 1 : -1);
        const next = ni < L - 1 ? ni + 1 : (sp.closed ? 0 : -1);
        if (prev >= 0) shown.add(this.key(si, pi, prev) + ':out');
        if (next >= 0) shown.add(this.key(si, pi, next) + ':in');
      });
      this.visibleHandles = [];
      shown.forEach((hk) => {
        const parts = hk.split(':');
        const which = parts[3];
        const h = this.nodeAt(parts.slice(0, 3).join(':'));
        if (!h || !h.n[which]) return;
        const a = this.screen(h.s, h.n);
        const c = this.screen(h.s, h.n[which]);
        this.visibleHandles.push({ k: parts.slice(0, 3).join(':'), which, x: c.x, y: c.y });
        // Curve handles read as a different kind of thing from points:
        // a thin arm ending in a small solid blue dot.
        handles.push(
          sv('line', { x1: a.x, y1: a.y, x2: c.x, y2: c.y, stroke: ACCENT, 'stroke-width': 1.25, 'stroke-opacity': 0.85 }),
          sv('circle', { cx: c.x, cy: c.y, r: 4, fill: ACCENT, stroke: '#fff', 'stroke-width': 1.5 })
        );
      });

      // Points: white with a strong blue edge, squares for corners and
      // circles for curve points. Selected points fill solid blue and get
      // a halo, so the selection reads at a glance on any fill colour.
      this.eachNode((n, s, si, pi, ni) => {
        const p = this.screen(s, n);
        const on = this.sel.has(this.key(si, pi, ni));
        const curve = !!(n.in || n.out);
        const r = on ? 6 : 5;
        if (on) anchors.push(curve
          ? sv('circle', { cx: p.x, cy: p.y, r: r + 3, fill: 'rgba(11,87,208,.18)' })
          : sv('rect', { x: p.x - r - 3, y: p.y - r - 3, width: 2 * r + 6, height: 2 * r + 6, rx: 3, fill: 'rgba(11,87,208,.18)' }));
        const attrs = { fill: on ? ACCENT : '#fff', stroke: on ? '#fff' : ACCENT, 'stroke-width': on ? 1.5 : 2 };
        anchors.push(curve
          ? sv('circle', Object.assign({ cx: p.x, cy: p.y, r }, attrs))
          : sv('rect', Object.assign({ x: p.x - r, y: p.y - r, width: 2 * r, height: 2 * r, rx: 1.5 }, attrs)));
      });

      // Interleave in Slides' stacking order: each edited shape, then the
      // static copies of whatever sits between it and the next one.
      const rank = this.zRank || this.shapes.map((_, i) => i);
      const painted = [];
      const ord = this.dfsOrder();
      const byRank = this.shapes.map((_, si) => si).sort((a, b) => rank[a] - rank[b] || ord[a] - ord[b] || a - b);
      byRank.forEach((si, i) => {
        painted.push(fills[si]);
        const last = i === byRank.length - 1 || rank[byRank[i + 1]] !== rank[si];
        const gap = last && this.coverGaps && this.coverGaps[rank[si]];
        if (gap) painted.push(gap);
      });
      this.gFills.replaceChildren(...painted);
      this.gOutlines.replaceChildren(...outlines);
      this.gHandles.replaceChildren(...handles);
      this.gAnchors.replaceChildren(...anchors);
      if (!this.drag || this.drag.kind === 'radius') this.updateCornerUI();
      else { this.gCorners.replaceChildren(); }
      this.drawXform();
      this.drawGrid();
      this.updateRailState();
    }

    // ── Corner rounding (Figma-style) ──
    // A corner is a vertex between two straight segments: either a sharp
    // point with no handles, or a pair of points joined by an arc-shaped
    // cubic (what rounding leaves behind). Both are recognised, so a corner
    // can be re-rounded any time without hidden state. Geometry is in page
    // units (381 = 1 px at Slides' 100%). For a turn of φ and radius R the
    // tangent points sit R·tan(φ/2) from the corner and each handle is
    // (4/3)·tan(φ/4)·R long; a corner is capped at half its side when the
    // neighbouring vertex is also a corner, at the full side otherwise.
    subVertices(si, pi) {
      const s = this.shapes[si], sp = s.subs[pi], T = s.toPage, nodes = sp.nodes, L = nodes.length;
      const pg = (n) => SB.apply(T, n.x, n.y);
      const unit = (a, b) => { const l = Math.hypot(b.x - a.x, b.y - a.y); return l < 1e-9 ? null : { x: (b.x - a.x) / l, y: (b.y - a.y) / l, l }; };
      const at = (i) => (sp.closed ? nodes[(i + L) % L] : nodes[i]);
      const pairAt = (i) => {
        const A = at(i), B = at(i + 1), prev = at(i - 1), next = at(i + 2);
        if (!A || !B || !prev || !next || A.in || !A.out || !B.in || B.out || prev.out || next.in) return null;
        const pA = pg(A), pB = pg(B);
        // Directions come from the arc's own handles; the outer segments
        // only have to line up with them (they may be zero-length when a
        // corner is rounded all the way to its neighbour).
        const u1 = unit(pA, pg(A.out)), u2 = unit(pg(B.in), pB);
        if (!u1 || !u2) return null;
        const s1 = unit(pg(prev), pA), s2 = unit(pB, pg(next));
        if ((s1 && s1.l > 1 && s1.x * u1.x + s1.y * u1.y < 0.999) || (s2 && s2.l > 1 && s2.x * u2.x + s2.y * u2.y < 0.999)) return null;
        const cr = u1.x * u2.y - u1.y * u2.x;
        if (Math.abs(cr) < 1e-6) return null;
        const t = ((pB.x - pA.x) * u2.y - (pB.y - pA.y) * u2.x) / cr; // P = pA + u1·t
        const P = { x: pA.x + u1.x * t, y: pA.y + u1.y * t };
        const d1 = Math.hypot(P.x - pA.x, P.y - pA.y), d2 = Math.hypot(P.x - pB.x, P.y - pB.y);
        if (t <= 0 || Math.abs(d1 - d2) > 0.03 * Math.max(d1, d2) + 2) return null;
        const phi = Math.acos(Math.max(-1, Math.min(1, u1.x * u2.x + u1.y * u2.y)));
        if (phi < 0.05 || phi > Math.PI - 0.05) return null;
        return { P, u1, u2, phi, R: ((d1 + d2) / 2) / Math.tan(phi / 2) };
      };
      const sharpAt = (i) => {
        const n = at(i), prev = at(i - 1), next = at(i + 1);
        if (!n || !prev || !next || n.in || n.out || prev.out || next.in) return null;
        const P = pg(n), u1 = unit(pg(prev), P), u2 = unit(P, pg(next));
        if (!u1 || !u2) return null;
        const phi = Math.acos(Math.max(-1, Math.min(1, u1.x * u2.x + u1.y * u2.y)));
        if (phi < 0.05 || phi > Math.PI - 0.05) return null;
        return { P, u1, u2, phi, R: 0 };
      };
      if (L < 3) return null;
      const verts = [];
      let start = 0, end = L;
      if (sp.closed && pairAt(L - 1)) { start = 1; } // a pair that wraps round the start
      for (let i = start; i < end;) {
        const pr = (sp.closed || i + 1 < L) ? pairAt(i) : null;
        if (pr && (i + 1 < L || sp.closed)) { verts.push(Object.assign({ nodes: [i, (i + 1) % L] }, pr)); i += 2; continue; }
        const sh = sharpAt(i);
        verts.push(sh ? Object.assign({ nodes: [i] }, sh) : { nodes: [i], P: pg(nodes[i]), plain: true });
        i++;
      }
      // Caps: how far each corner's tangent points may travel.
      const V = verts.length;
      verts.forEach((v, k) => {
        if (v.plain) return;
        const pv = sp.closed ? verts[(k - 1 + V) % V] : verts[k - 1];
        const nv = sp.closed ? verts[(k + 1) % V] : verts[k + 1];
        const side = (o) => (o ? Math.hypot(o.P.x - v.P.x, o.P.y - v.P.y) * (o.plain ? 1 : 0.5) : 0);
        v.rmax = Math.max(0, Math.min(side(pv), side(nv))) / Math.tan(v.phi / 2);
      });
      return verts;
    }

    // Corners the handles act on: every corner when nothing (or the whole
    // shape) is selected, otherwise just the corners whose points are selected.
    cornerScope() {
      if (this.tool !== 'direct') return null;
      let total = 0;
      this.eachNode(() => { total++; });
      if (total > 160) return null; // detailed artwork: leave it alone
      const all = [];
      this.shapes.forEach((s, si) => s.subs.forEach((sp, pi) => {
        const verts = this.subVertices(si, pi);
        if (verts) verts.forEach((v, k) => { if (!v.plain) all.push({ si, pi, k, v }); });
      }));
      const whole = this.sel.size === 0 || this.sel.size === total;
      if (whole) return all.length >= 2 ? { corners: all, scoped: false } : null;
      const picked = all.filter((c) => c.v.nodes.some((ni) => this.sel.has(this.key(c.si, c.pi, ni))));
      return picked.length ? { corners: picked, scoped: true } : null;
    }

    // Rebuild the affected subpaths with radius R (page units) on the given
    // corners, keeping the selection on the same corners.
    setRadius(scope, R) {
      if (!scope) return;
      const want = new Set(scope.corners.map((c) => c.si + ':' + c.pi + ':' + c.k));
      const subsTouched = new Set(scope.corners.map((c) => c.si + ':' + c.pi));
      const newSel = new Set([...this.sel].filter((k) => !subsTouched.has(k.split(':').slice(0, 2).join(':'))));
      subsTouched.forEach((sk) => {
        const [si, pi] = sk.split(':').map(Number);
        const s = this.shapes[si], sp = s.subs[pi];
        const verts = this.subVertices(si, pi);
        if (!verts) return;
        const inv = SB.matInv(s.toPage);
        const loc = (p) => SB.apply(inv, p.x, p.y);
        const out = [];
        verts.forEach((v, k) => {
          const wasSel = v.nodes.some((ni) => this.sel.has(this.key(si, pi, ni)));
          const first = out.length;
          const target = want.has(si + ':' + pi + ':' + k);
          if (v.plain || !target) {
            v.nodes.forEach((ni) => out.push(sp.nodes[ni]));
          } else {
            const Re = Math.max(0, Math.min(R, v.rmax));
            if (Re <= 1e-6) {
              out.push(Object.assign(loc(v.P), { in: null, out: null, smooth: false }));
            } else {
              const d = Re * Math.tan(v.phi / 2), h = (4 / 3) * Math.tan(v.phi / 4) * Re;
              const a = { x: v.P.x - v.u1.x * d, y: v.P.y - v.u1.y * d };
              const b = { x: v.P.x + v.u2.x * d, y: v.P.y + v.u2.y * d };
              out.push(
                Object.assign(loc(a), { in: null, out: loc({ x: a.x + v.u1.x * h, y: a.y + v.u1.y * h }), smooth: false }),
                Object.assign(loc(b), { in: loc({ x: b.x - v.u2.x * h, y: b.y - v.u2.y * h }), out: null, smooth: false }));
            }
          }
          if (wasSel) for (let n = first; n < out.length; n++) newSel.add(this.key(si, pi, n));
        });
        sp.nodes = out;
      });
      this.sel = newSel;
      this.dirty = true;
      this.render();
    }

    // Small circles just inside each corner in scope, plus the radius pill.
    updateCornerUI() {
      const g = this.gCorners;
      const sc = this.drag && this.drag.kind === 'radius' ? this.drag.liveScope() : this.cornerScope();
      this.cornerHandles = [];
      if (!sc) { g.replaceChildren(); this.segR.style.display = 'none'; this.updatePill(); return; }
      const k = Math.sqrt(Math.abs(this.ctm[0] * this.ctm[3] - this.ctm[1] * this.ctm[2])); // page → screen
      const els = [];
      let minX = Infinity, maxX = -Infinity, maxY = -Infinity;
      sc.corners.forEach((c) => {
        const v = c.v;
        const P = SB.apply(this.ctm, v.P.x, v.P.y);
        let bx = v.u2.x - v.u1.x, by = v.u2.y - v.u1.y;
        const bl = Math.hypot(bx, by) || 1; bx /= bl; by /= bl;
        const dist = CORNER_INSET + (v.R * k) / Math.cos(v.phi / 2);
        const H = { x: P.x + bx * dist, y: P.y + by * dist };
        this.cornerHandles.push({ c, x: H.x, y: H.y, P, bx, by });
        const active = this.drag && this.drag.kind === 'radius';
        els.push(sv('circle', { cx: H.x, cy: H.y, r: 4.5, fill: active ? ACCENT : '#fff', stroke: ACCENT, 'stroke-width': 1.5 }));
        minX = Math.min(minX, P.x); maxX = Math.max(maxX, P.x); maxY = Math.max(maxY, P.y);
      });
      g.replaceChildren(...els);
      // Pill: under the corners in scope.
      this.shapes.forEach((s) => s.subs.forEach((sp) => sp.nodes.forEach((n) => {
        const q = this.screen(s, n); maxY = Math.max(maxY, q.y);
      })));
      const Rs = sc.corners.map((c) => c.v.R / 381);
      const same = Rs.every((r) => Math.abs(r - Rs[0]) < 0.5);
      if (document.activeElement !== this.host || this.root.activeElement !== this.rNum) {
        this.rNum.value = same ? String(Math.round(Rs[0])) : '';
        this.rNum.placeholder = same ? '' : 'Mixed';
      }
      this.rScope.textContent = sc.scoped ? (sc.corners.length === 1 ? '1 corner' : sc.corners.length + ' corners') : 'All corners';
      this.segR.style.display = '';
      this.updatePill();
    }

    // Pill session: where the undo stack stood when the pill was first
    // touched. ✕ walks back to it; ✓, or doing anything on the canvas, ends it.
    markPill() {
      if (this._pillBase === null || this._pillBase === undefined) this._pillBase = this.undo.length;
      this.syncPillButtons();
    }
    pillChanged() {
      return this._pillBase !== null && this._pillBase !== undefined && this.undo.length > this._pillBase;
    }
    syncPillButtons() {
      if (!this.pNo) return;
      const on = this.pillChanged();
      this.pNo.disabled = !on; this.pOk.disabled = !on;
    }
    commitPill(quiet) {
      const had = this.pillChanged();
      this._pillBase = null;
      this._rTyping = false; this._sizeBase = null;
      if (!quiet) { const a = this.root && this.root.activeElement; if (a && a.blur && this.rpill.contains(a)) a.blur(); this.host.focus(); }
      if (had || !quiet) this.updatePill();
      this.syncPillButtons();
    }
    cancelPill() {
      const base = this._pillBase;
      this._pillBase = null;
      this._rTyping = false; this._sizeBase = null;
      const a = this.root && this.root.activeElement;
      if (a && a.blur && this.rpill.contains(a)) a.blur();
      if (base !== null && base !== undefined) {
        let moved = false;
        while (this.undo.length > base) { this.restore(this.undo.pop()); moved = true; }
        if (moved) { this.redo = []; this.updateUndoButtons(); }
      }
      this.aNum.value = '';
      this.host.focus();
      this.updatePill();
      this.syncPillButtons();
    }

    // The value pill under what's in scope.
    updatePill() {
      const pill = this.rpill;
      this.syncPillButtons();
      const ok = this.tool === 'direct' && this.targets().length && (!this.drag || this.drag.kind === 'radius' || this.drag.kind === 'xform');
      const b = ok ? (this.drag && this.drag.kind === 'xform' ? null : this.scopeBBox()) : null;
      if (!b) { if (!(this.drag && this.drag.kind === 'xform')) pill.classList.remove('show'); return; }
      const fmt = (v) => String(Math.round(v * 10) / 10);
      const focused = this.root.activeElement;
      if (focused !== this.wNum) this.wNum.value = fmt((b.maxX - b.minX) / 381);
      if (focused !== this.hNum) this.hNum.value = fmt((b.maxY - b.minY) / 381);
      pill.classList.add('show');
      pill.classList.toggle('live', !!(this.drag && this.drag.kind === 'radius'));
      const a = SB.apply(this.ctm, b.minX, b.minY), z = SB.apply(this.ctm, b.maxX, b.maxY);
      const r = this.wsRect;
      const half = (pill.offsetWidth || 300) / 2;
      const railR = this.rail ? this.rail.getBoundingClientRect().right : r.left;
      pill.style.left = Math.max(railR + half + 10, Math.min(r.right - half - 8, (a.x + z.x) / 2)) + 'px';
      pill.style.top = Math.min(r.bottom - 42, Math.max(a.y, z.y) + 22) + 'px';
    }

    hitCornerHandle(x, y) {
      let best = null, bd = 8;
      (this.cornerHandles || []).forEach((h) => { const d = Math.hypot(h.x - x, h.y - y); if (d <= bd) { bd = d; best = h; } });
      return best;
    }

    // ── Hit testing ──
    hitHandle(x, y) {
      let best = null, bd = HIT;
      (this.visibleHandles || []).forEach((h) => {
        const d = Math.hypot(h.x - x, h.y - y);
        if (d <= bd) { bd = d; best = h; }
      });
      return best;
    }
    hitNode(x, y) {
      let best = null, bd = HIT;
      this.eachNode((n, s, si, pi, ni) => {
        const p = this.screen(s, n);
        const d = Math.hypot(p.x - x, p.y - y);
        if (d <= bd) { bd = d; best = this.key(si, pi, ni); }
      });
      return best;
    }
    hitShape(x, y) {
      const paths = this.gFills.querySelectorAll(':scope > path[data-si]');
      for (let i = paths.length - 1; i >= 0; i--) {
        const p = paths[i];
        try {
          const pt = new DOMPoint(x, y);
          if (p.isPointInFill(pt) || p.isPointInStroke(pt)) return Number(p.dataset.si);
        } catch { /* ignore */ }
      }
      return null;
    }
    // Nearest point on any segment, in screen space.
    hitSegment(x, y) {
      let best = null, bd = HIT;
      this.shapes.forEach((s, si) => s.subs.forEach((sp, pi) => {
        const L = sp.nodes.length;
        const segs = sp.closed ? L : L - 1;
        for (let j = 0; j < segs; j++) {
          const a = sp.nodes[j], b = sp.nodes[(j + 1) % L];
          const p0 = this.screen(s, a), p1 = this.screen(s, b);
          const c1 = this.screen(s, a.out || a), c2 = this.screen(s, b.in || b);
          const curve = a.out || b.in;
          const N = curve ? 48 : 1;
          let tBest = 0, dBest = Infinity;
          if (!curve) {
            const vx = p1.x - p0.x, vy = p1.y - p0.y;
            const len2 = vx * vx + vy * vy || 1;
            const t = Math.max(0, Math.min(1, ((x - p0.x) * vx + (y - p0.y) * vy) / len2));
            dBest = Math.hypot(p0.x + vx * t - x, p0.y + vy * t - y);
            tBest = t;
          } else {
            for (let i = 0; i <= N; i++) {
              const t = i / N;
              const q = cubicAt(p0, c1, c2, p1, t);
              const d = Math.hypot(q.x - x, q.y - y);
              if (d < dBest) { dBest = d; tBest = t; }
            }
          }
          if (dBest <= bd && tBest > 0.02 && tBest < 0.98) {
            bd = dBest;
            const q = curve ? cubicAt(p0, c1, c2, p1, tBest) : lerp(p0, p1, tBest);
            best = { si, pi, j, t: tBest, x: q.x, y: q.y };
          }
        }
      }));
      return best;
    }

    // ── Pointer ──
    onDown(e) {
      e.preventDefault();
      if (this.committing) return;
      this.host.focus();
      this.hideTip();
      this.rail.classList.add('idle');
      const x = e.clientX, y = e.clientY;

      // Space-drag or middle-button drag pans the view (Figma/Illustrator).
      if (this.spaceDown || e.button === 1) {
        this.drag = { kind: 'pan', start: { x, y }, tx0: this.view.tx, ty0: this.view.ty };
        this.setPanCursor('grabbing');
        return;
      }

      if (this.tool === 'pen') { this.penDown(x, y, e); return; }

      const ch = this.hitCornerHandle(x, y);
      if (ch) {
        // Drag a corner handle along the corner's bisector to scrub the
        // radius of every corner in scope.
        const scope = this.cornerScope();
        if (scope) {
          const ids = scope.corners.map((c) => [c.si, c.pi, c.k]);
          this.drag = { kind: 'radius', start: { x, y }, pushed: false, h: ch, scope,
            liveScope: () => {
              const corners = [];
              ids.forEach(([si, pi, k]) => { const vs = this.subVertices(si, pi); const v = vs && vs[k]; if (v && !v.plain) corners.push({ si, pi, k, v }); });
              return { corners, scoped: scope.scoped };
            } };
          this.render();
          return;
        }
      }
      const xs = this.hitXform(x, y, 'box', e);
      if (xs) { this.startXform(xs, x, y); return; }
      const h = this.hitHandle(x, y);
      if (h) {
        const hn = this.nodeAt(h.k);
        this.drag = { kind: 'handle', h, start: { x, y }, pushed: false, alt: e.altKey,
          orig: { anchor: clone({ x: hn.n.x, y: hn.n.y }), self: clone(hn.n[h.which]) } };
        return;
      }
      const nk = this.hitNode(x, y);
      if (nk) {
        if (e.shiftKey) {
          if (this.sel.has(nk)) this.sel.delete(nk); else this.sel.add(nk);
        } else if (!this.sel.has(nk)) {
          this.sel = new Set([nk]);
        }
        this.startNodeDrag(x, y, nk);
        this.render();
        return;
      }
      const xr = this.hitXform(x, y, 'outside', e);
      if (xr) { this.startXform(xr, x, y); return; }
      const si = this.hitShape(x, y);
      if (si != null) {
        const keys = [];
        this.shapes[si].subs.forEach((sp, pi) => sp.nodes.forEach((n, ni) => keys.push(this.key(si, pi, ni))));
        if (e.shiftKey) keys.forEach((k) => this.sel.add(k));
        else if (!keys.every((k) => this.sel.has(k))) this.sel = new Set(keys);
        this.startNodeDrag(x, y);
        this.render();
        return;
      }
      // Empty space: marquee.
      if (!e.shiftKey) this.sel.clear();
      this.drag = { kind: 'marquee', start: { x, y }, base: new Set(this.sel) };
      this.render();
    }

    // ── Snapping ──
    snapOn() { return snapPrefs.points || snapPrefs.px || snapPrefs.grid; }
    updateSnapUI() {
      this.rk.setOn('snapPoints', snapPrefs.points);
      this.rk.setOn('snapPx', snapPrefs.px);
      this.rk.setOn('snapGrid', snapPrefs.grid);
      this.rk.setOn('snap', this.snapOn());
      this.rk.setField('snapSize', snapPrefs.size);
    }
    toggleSnap(which) {
      snapPrefs[which] = !snapPrefs[which];
      saveSnap();
      this.updateSnapUI();
      const names = { points: 'points', px: 'whole pixels', grid: 'grid (' + snapPrefs.size + ' px)' };
      this.flashHint('Snap to ' + names[which] + ': ' + (snapPrefs[which] ? 'on' : 'off'), 1600);
      this.render();
    }
    // The slide's own box in page units (edges and centre snap too).
    pageBox() {
      if (this._pageBox !== undefined) return this._pageBox;
      let b = null;
      try {
        const page = SB.currentPageGroup();
        const bg = page && document.getElementById(page.id + '-bg');
        const r = bg && bg.getBBox();
        if (r && r.width) b = { x: r.x, y: r.y, w: r.width, h: r.height };
      } catch { b = null; }
      this._pageBox = b;
      return b;
    }
    // What can be snapped to during one drag, in page units: every point
    // except the ones moving, plus the slide's edges and centre.
    snapTargets(skip) {
      const pts = [];
      this.eachNode((n, s, si, pi, ni) => {
        if (skip && skip.has(this.key(si, pi, ni))) return;
        pts.push(SB.apply(s.toPage, n.x, n.y));
      });
      const b = this.pageBox();
      const xs = b ? [b.x, b.x + b.w / 2, b.x + b.w] : [];
      const ys = b ? [b.y, b.y + b.h / 2, b.y + b.h] : [];
      return { pts, xs, ys };
    }
    // Snap a page point. Points (and lines through them) win when close;
    // otherwise the grid, or whole pixels, round it. Returns the point and
    // the guides to show.
    snapPage(P, targets, e) {
      const out = { x: P.x, y: P.y, guides: [] };
      if (!this.snapOn() || (e && (SB.IS_MAC ? e.metaKey : e.ctrlKey))) return out;
      const tol = SNAP_PX / (this.pageScale() || 1);
      let gx = false, gy = false;
      if (snapPrefs.points && targets) {
        let best = null, bd = tol;
        targets.pts.forEach((q) => { const d = Math.hypot(q.x - P.x, q.y - P.y); if (d <= bd) { bd = d; best = q; } });
        if (best) { out.x = best.x; out.y = best.y; out.guides.push({ kind: 'point', x: best.x, y: best.y }); return out; }
        let bx = null, dx = tol, by = null, dy = tol;
        targets.pts.forEach((q) => {
          const ddx = Math.abs(q.x - P.x), ddy = Math.abs(q.y - P.y);
          if (ddx <= dx) { dx = ddx; bx = q; }
          if (ddy <= dy) { dy = ddy; by = q; }
        });
        targets.xs.forEach((x) => { const d = Math.abs(x - P.x); if (d <= dx) { dx = d; bx = { x, y: null }; } });
        targets.ys.forEach((y) => { const d = Math.abs(y - P.y); if (d <= dy) { dy = d; by = { x: null, y }; } });
        if (bx) { out.x = bx.x; gx = true; out.guides.push({ kind: 'v', x: bx.x, from: bx.y }); }
        if (by) { out.y = by.y; gy = true; out.guides.push({ kind: 'h', y: by.y, from: by.x }); }
      }
      const step = snapPrefs.grid ? Math.max(0.01, snapPrefs.size) * 381 : snapPrefs.px ? 381 : 0;
      if (step) {
        const b = this.pageBox();
        const ox = b ? b.x : 0, oy = b ? b.y : 0;
        if (!gx) out.x = ox + Math.round((out.x - ox) / step) * step;
        if (!gy) out.y = oy + Math.round((out.y - oy) / step) * step;
      }
      return out;
    }
    // Screen point → snapped screen point (and its guides shown).
    snapScreen(x, y, targets, e) {
      const inv = SB.matInv(this.ctm);
      if (!inv) return { x, y };
      const P = SB.apply(inv, x, y);
      const r = this.snapPage(P, targets, e);
      this.showGuides(r.guides, P);
      const q = SB.apply(this.ctm, r.x, r.y);
      return { x: q.x, y: q.y };
    }
    showGuides(guides, P) {
      if (!this.gGuides) return;
      if (!guides || !guides.length) { this.gGuides.replaceChildren(); return; }
      const C = (x, y) => SB.apply(this.ctm, x, y);
      const kids = [];
      const line = (a, b) => kids.push(sv('line', { x1: a.x, y1: a.y, x2: b.x, y2: b.y, stroke: '#e8458b', 'stroke-width': 1 }));
      const mark = (p) => kids.push(sv('path', { d: `M${p.x - 4} ${p.y - 4}l8 8m0 -8l-8 8`, stroke: '#e8458b', 'stroke-width': 1.5 }));
      const box = this.pageBox();
      guides.forEach((g) => {
        if (g.kind === 'point') { mark(C(g.x, g.y)); return; }
        if (g.kind === 'v') {
          const y0 = g.from !== null && g.from !== undefined ? g.from : (box ? box.y : P.y), y1 = g.from !== null && g.from !== undefined ? P.y : (box ? box.y + box.h : P.y);
          line(C(g.x, y0), C(g.x, y1)); mark(C(g.x, P.y));
        } else {
          const x0 = g.from !== null && g.from !== undefined ? g.from : (box ? box.x : P.x), x1 = g.from !== null && g.from !== undefined ? P.x : (box ? box.x + box.w : P.x);
          line(C(x0, g.y), C(x1, g.y)); mark(C(P.x, g.y));
        }
      });
      this.gGuides.replaceChildren(...kids);
    }
    // The grid, while grid snapping is on and its lines are far enough apart
    // on screen to read.
    drawGrid() {
      if (!this.gGrid) return;
      const b = this.pageBox();
      const step = snapPrefs.grid ? Math.max(0.01, snapPrefs.size) * 381 : 0;
      const k = this.pageScale();
      if (!b || !step || step * k < 6) { this.gGrid.replaceChildren(); this._gridSig = null; return; }
      const sig = this.ctm.join(',') + '|' + step;
      if (sig === this._gridSig) return;
      this._gridSig = sig;
      const C = (x, y) => SB.apply(this.ctm, x, y);
      let d = '';
      for (let x = b.x; x <= b.x + b.w + 0.5; x += step) { const a = C(x, b.y), z = C(x, b.y + b.h); d += `M${a.x} ${a.y}L${z.x} ${z.y}`; }
      for (let y = b.y; y <= b.y + b.h + 0.5; y += step) { const a = C(b.x, y), z = C(b.x + b.w, y); d += `M${a.x} ${a.y}L${z.x} ${z.y}`; }
      this.gGrid.replaceChildren(sv('path', { d, stroke: 'rgba(11,87,208,.16)', 'stroke-width': 1, fill: 'none', 'shape-rendering': 'crispEdges' }));
    }

    startNodeDrag(x, y, leadKey) {
      const orig = new Map();
      this.sel.forEach((k) => { const h = this.nodeAt(k); if (h) orig.set(k, clone({ x: h.n.x, y: h.n.y, in: h.n.in, out: h.n.out })); });
      // The point that snaps: the one grabbed, else the selected point
      // nearest the pointer; the others move with it.
      let lead = leadKey && orig.has(leadKey) ? leadKey : null;
      if (!lead) {
        let bd = Infinity;
        orig.forEach((o, k) => { const h = this.nodeAt(k); const p = this.screen(h.s, o); const d = Math.hypot(p.x - x, p.y - y); if (d < bd) { bd = d; lead = k; } });
      }
      const lh = lead && this.nodeAt(lead);
      const leadScreen = lh ? this.screen(lh.s, orig.get(lead)) : null;
      this.drag = { kind: 'nodes', start: { x, y }, orig, pushed: false, leadScreen, targets: this.snapTargets(new Set(orig.keys())) };
    }

    onMove(e) {
      const x = e.clientX, y = e.clientY;
      if (!this.drag) {
        this._hoverPt = { x, y };
        this.hoverCursor(e);
        this._lastMoveEvt = e;
        if (this.tool === 'pen' && this.drawing) { this.penGhost.setAttribute('visibility', 'hidden'); this.drawRubber(x, y); return; }
        if (this.tool === 'pen') {
          const seg = !this.hitNode(x, y) && this.hitSegment(x, y);
          if (seg) { this.penGhost.setAttribute('cx', seg.x); this.penGhost.setAttribute('cy', seg.y); this.penGhost.setAttribute('visibility', 'visible'); }
          else this.penGhost.setAttribute('visibility', 'hidden');
        }
        return;
      }
      e.preventDefault();
      let dx = x - this.drag.start.x, dy = y - this.drag.start.y;
      if (this.drag.kind === 'xform') {
        if (!this.drag.pushed) {
          if (Math.hypot(dx, dy) < 2) return;
          this.pushUndo();
          this.drag.pushed = true;
        }
        this.moveXform(x, y, e);
        return;
      }
      if (this.drag.kind === 'pen') { this.penDrag(x, y, e); this.render(); return; }
      if (this.drag.kind === 'pan') {
        this.view.tx = this.drag.tx0 + dx;
        this.view.ty = this.drag.ty0 + dy;
        this.applyView();
        this.render();
        return;
      }
      if (this.drag.kind !== 'marquee' && !this.drag.pushed) {
        if (Math.hypot(dx, dy) < 2) return;
        this.pushUndo();
        this.drag.pushed = true;
      }
      if (this.drag.kind === 'radius') {
        const h = this.drag.h;
        const k = Math.sqrt(Math.abs(this.ctm[0] * this.ctm[3] - this.ctm[1] * this.ctm[2]));
        const proj = (x - h.P.x) * h.bx + (y - h.P.y) * h.by;
        let R = Math.max(0, proj - CORNER_INSET) * Math.cos(h.c.v.phi / 2) / k;
        if (e.shiftKey) R = Math.round(R / 381 / 10) * 10 * 381; // Shift: steps of 10 px
        else R = Math.round(R / 381) * 381;                      // whole px
        this.setRadius(this.drag.liveScope(), R);
        return;
      }
      if (e.shiftKey && this.drag.kind === 'nodes') { const s = snap45(dx, dy); dx = s.x; dy = s.y; }
      else if (this.drag.kind === 'nodes' && this.drag.leadScreen) {
        const L = this.drag.leadScreen;
        const q = this.snapScreen(L.x + dx, L.y + dy, this.drag.targets, e);
        dx = q.x - L.x; dy = q.y - L.y;
      }

      if (this.drag.kind === 'nodes') {
        this.drag.orig.forEach((o, k) => {
          const h = this.nodeAt(k);
          if (!h) return;
          const v = this.localVec(h.s, dx, dy);
          h.n.x = o.x + v.x; h.n.y = o.y + v.y;
          h.n.in = o.in ? { x: o.in.x + v.x, y: o.in.y + v.y } : null;
          h.n.out = o.out ? { x: o.out.x + v.x, y: o.out.y + v.y } : null;
        });
      } else if (this.drag.kind === 'handle') {
        const { h, orig } = this.drag;
        const hn = this.nodeAt(h.k);
        if (!hn) return;
        const anchorS = this.screen(hn.s, orig.anchor);
        const selfS = this.screen(hn.s, orig.self);
        let tx = selfS.x + dx, ty = selfS.y + dy;
        if (e.shiftKey) { const s = snap45(tx - anchorS.x, ty - anchorS.y); tx = anchorS.x + s.x; ty = anchorS.y + s.y; }
        else {
          if (!this.drag.targets) this.drag.targets = this.snapTargets(null);
          const q = this.snapScreen(tx, ty, this.drag.targets, e); tx = q.x; ty = q.y;
        }
        const p = this.local(hn.s, { x: tx, y: ty });
        hn.n[h.which] = p;
        const other = h.which === 'in' ? 'out' : 'in';
        if (e.altKey || this.drag.alt) hn.n.smooth = false;
        if (hn.n.smooth && hn.n[other]) {
          const len = dist(hn.n, hn.n[other]);
          const vx = hn.n.x - p.x, vy = hn.n.y - p.y;
          const l = Math.hypot(vx, vy) || 1;
          hn.n[other] = { x: hn.n.x + (vx / l) * len, y: hn.n.y + (vy / l) * len };
        }
      } else if (this.drag.kind === 'marquee') {
        const x0 = Math.min(this.drag.start.x, x), y0 = Math.min(this.drag.start.y, y);
        const w = Math.abs(x - this.drag.start.x), hgt = Math.abs(y - this.drag.start.y);
        this.marquee.setAttribute('x', x0); this.marquee.setAttribute('y', y0);
        this.marquee.setAttribute('width', w); this.marquee.setAttribute('height', hgt);
        this.marquee.setAttribute('visibility', 'visible');
        const next = new Set(this.drag.base);
        this.eachNode((n, s, si, pi, ni) => {
          const p = this.screen(s, n);
          if (p.x >= x0 && p.x <= x0 + w && p.y >= y0 && p.y <= y0 + hgt) next.add(this.key(si, pi, ni));
        });
        this.sel = next;
      }
      this.render();
    }

    onUp() {
      if (this.drag && this.drag.kind === 'marquee') this.marquee.setAttribute('visibility', 'hidden');
      if (this.drag && this.drag.kind === 'pan') this.setPanCursor(this.spaceDown ? 'grab' : '');
      this.showGuides(null);
      const redraw = this.drag && (this.drag.kind === 'radius' || this.drag.kind === 'xform' || this.drag.kind === 'pen');
      if (this.drag && this.drag.kind === 'pen' && this.drag.closing) this.sel.clear();
      this.drag = null;
      if (redraw) this.render();
    }

    onDbl(e) {
      if (this.tool !== 'direct') return;
      const nk = this.hitNode(e.clientX, e.clientY);
      if (!nk) return;
      this.pushUndo();
      this.toggleSmooth(nk);
      this.render();
    }

    // ── Edits ──
    toggleSmooth(k) {
      const h = this.nodeAt(k);
      if (!h) return;
      const { n, sp, ni } = h;
      if (n.in || n.out) {
        n.in = null; n.out = null; n.smooth = false;
        return;
      }
      const L = sp.nodes.length;
      const prev = ni > 0 ? sp.nodes[ni - 1] : (sp.closed ? sp.nodes[L - 1] : null);
      const next = ni < L - 1 ? sp.nodes[ni + 1] : (sp.closed ? sp.nodes[0] : null);
      const a = prev || n, b = next || n;
      let tx = b.x - a.x, ty = b.y - a.y;
      const tl = Math.hypot(tx, ty) || 1;
      tx /= tl; ty /= tl;
      const lp = prev ? dist(prev, n) / 3 : 0;
      const ln = next ? dist(n, next) / 3 : 0;
      n.in = prev ? { x: n.x - tx * lp, y: n.y - ty * lp } : null;
      n.out = next ? { x: n.x + tx * ln, y: n.y + ty * ln } : null;
      n.smooth = !!(n.in && n.out);
    }

    splitSegment(seg) {
      const s = this.shapes[seg.si];
      const sp = s.subs[seg.pi];
      const L = sp.nodes.length;
      const a = sp.nodes[seg.j], b = sp.nodes[(seg.j + 1) % L];
      const t = seg.t;
      let node;
      if (a.out || b.in) {
        const p0 = a, c1 = a.out || a, c2 = b.in || b, p1 = b;
        const q1 = lerp(p0, c1, t), q2 = lerp(c1, c2, t), q3 = lerp(c2, p1, t);
        const r1 = lerp(q1, q2, t), r2 = lerp(q2, q3, t);
        const m = lerp(r1, r2, t);
        a.out = a.out ? q1 : null;
        b.in = b.in ? q3 : null;
        node = { x: m.x, y: m.y, in: r1, out: r2, smooth: true };
      } else {
        const m = lerp(a, b, t);
        node = { x: m.x, y: m.y, in: null, out: null, smooth: false };
      }
      sp.nodes.splice(seg.j + 1, 0, node);
      return this.key(seg.si, seg.pi, seg.j + 1);
    }

    deleteNodes(keys) {
      this.shapes.forEach((s, si) => {
        s.subs.forEach((sp, pi) => {
          sp.nodes = sp.nodes.filter((n, ni) => !keys.has(this.key(si, pi, ni)));
        });
        s.subs = s.subs.filter((sp) => sp.nodes.length >= 2);
      });
      this.sel.clear();
    }

    nudge(dx, dy) {
      if (!this.sel.size) return;
      this.pushUndo();
      this.sel.forEach((k) => {
        const h = this.nodeAt(k);
        if (!h) return;
        const v = this.localVec(h.s, dx, dy);
        h.n.x += v.x; h.n.y += v.y;
        if (h.n.in) { h.n.in.x += v.x; h.n.in.y += v.y; }
        if (h.n.out) { h.n.out.x += v.x; h.n.out.y += v.y; }
      });
      this.render();
    }

    // ── Keyboard (Figma / Illustrator conventions) ──
    onKey(e) {
      if (this.committing) { e.preventDefault(); return; }
      const t0 = e.composedPath ? e.composedPath()[0] : e.target;
      if (t0 && t0.tagName === 'INPUT') {
        // Typing a radius: let the field have its keys. Enter/Escape leave it.
        if (e.key === 'Enter' || e.key === 'Escape') { e.preventDefault(); t0.blur(); this.host.focus(); }
        return;
      }
      const mod = e.metaKey || e.ctrlKey;
      const k = e.key;
      const handled = () => { e.preventDefault(); };
      if (k === 'Meta' || k === 'Control' || k === 'Alt' || k === 'Shift') { this.hoverCursor(e); return; }
      if (this.pal && k === 'Escape') { handled(); this.pal.close(); return; }
      if (this.pop && k === 'Escape') { handled(); this.pop.close(); return; }
      if (mod && (k === "'" || e.code === 'Quote')) { handled(); this.toggleSnap('grid'); return; }
      const sc = SB.matchShortcut(e);
      if (sc) { handled(); this.command(sc); return; }
      // View: Space pans; ⌘+/⌘− zoom; ⌘0 or ⇧0 resets; ⇧1 / ⇧2 fit.
      if (k === ' ') {
        handled();
        if (!this.spaceDown) { this.spaceDown = true; if (!this.drag) this.setPanCursor('grab'); }
        return;
      }
      if (mod && (k === '=' || k === '+')) { handled(); this.zoomStep(1.5); return; }
      if (mod && (k === '-' || k === '_')) { handled(); this.zoomStep(1 / 1.5); return; }
      if ((mod && k === '0') || (e.shiftKey && e.code === 'Digit0')) { handled(); this.resetView(); return; }
      if (e.shiftKey && (e.code === 'Digit1' || e.code === 'Digit2')) { handled(); this.fitView(); return; }
      if (mod && (k === 'z' || k === 'Z')) { handled(); if (e.shiftKey) this.doRedo(); else this.doUndo(); return; }
      if (mod && (k === 'y' || k === 'Y')) { handled(); this.doRedo(); return; }
      if (mod && (k === 'a' || k === 'A')) {
        handled();
        this.sel = new Set();
        this.eachNode((n, s, si, pi, ni) => this.sel.add(this.key(si, pi, ni)));
        this.render();
        return;
      }
      if (this.drawing && (k === 'Enter' || k === 'Escape')) { handled(); this.finishDrawing(); return; }
      if (this.drawing && (k === 'Backspace' || k === 'Delete')) {
        handled();
        const sp = this.shapes[this.drawing.si].subs[this.drawing.pi];
        this.pushUndo();
        sp.nodes.pop();
        if (!sp.nodes.length) { sp.nodes.push({ x: 0, y: 0, in: null, out: null }); this.finishDrawing(); return; }
        this.sel = new Set([this.key(this.drawing.si, this.drawing.pi, sp.nodes.length - 1)]);
        if (this._hoverPt) this.drawRubber(this._hoverPt.x, this._hoverPt.y);
        this.render();
        return;
      }
      if (k === 'Enter') { handled(); this.commit(); return; }
      if (k === 'Escape') {
        handled();
        if (this.sel.size) { this.sel.clear(); this.render(); } else this.commit();
        return;
      }
      if (k === 'Backspace' || k === 'Delete') {
        handled();
        if (this.sel.size) { this.pushUndo(); this.deleteNodes(new Set(this.sel)); this.render(); }
        return;
      }
      const step = e.shiftKey ? 10 : 1;
      if (k === 'ArrowLeft') { handled(); this.nudge(-step, 0); return; }
      if (k === 'ArrowRight') { handled(); this.nudge(step, 0); return; }
      if (k === 'ArrowUp') { handled(); this.nudge(0, -step); return; }
      if (k === 'ArrowDown') { handled(); this.nudge(0, step); return; }
      if (!mod && (k === 'a' || k === 'A' || k === 'v' || k === 'V')) { handled(); this.setTool('direct'); return; }
      if (!mod && (k === 'p' || k === 'P')) { handled(); this.setTool('pen'); return; }
      handled();
    }

    // ── One toolbar: commands (rail, flyouts and shortcuts) ──
    // Everything acts on the shapes being edited, in memory, with the
    // editor's own undo; Done puts the result on the slide. The scope is the
    // shapes with selected points, or every shape when nothing is selected.
    onRailAct(act, info) {
      if (act === 'undo') this.doUndo();
      else if (act === 'redo') this.doRedo();
      else if (act === 'zoomreset') { if (this.isIdentityView()) this.fitView(); else this.resetView(); }
      else if (act === 'cancel') this.close(true);
      else if (act === 'done') this.commit();
      else this.command(act, info);
    }

    command(act, info = {}) {
      if (this.committing) return;
      const btn = (a) => { const r = this.rk.items.get(a); return r ? r.b.getBoundingClientRect() : null; };
      switch (act) {
        case 'select': return this.setTool('direct');
        case 'pen': return this.setTool('pen');
        case 'snapPoints': return this.toggleSnap('points');
        case 'snapPx': return this.toggleSnap('px');
        case 'snapGrid': return this.toggleSnap('grid');
        case 'rotL15': return this.rotateBy(-15);
        case 'rotR15': return this.rotateBy(15);
        case 'rotL1': return this.rotateBy(-1);
        case 'rotR1': return this.rotateBy(1);
        case 'scaleUp': return this.scaleBy(1.1);
        case 'scaleDown': return this.scaleBy(1 / 1.1);
        case 'forward': case 'backward': case 'front': case 'back': return this.arrange(act);
        case 'union': case 'subtract': case 'intersect': case 'exclude': return this.booleanOp(act);
        case 'group': return this.groupOp();
        case 'ungroup': return this.ungroupOp();
        case 'outlineStroke': return this.outlineStrokeOp();
        case 'outlineText': return this.outlineTextOp();
        case 'restoreText': return this.flashHint('Restore text from the toolbar, after Done', 2500);
        case 'mask': return this.flashHint('Mask from the toolbar, after Done', 2500);
        case 'alignLeft': case 'alignHCenter': case 'alignRight': case 'alignTop': case 'alignVMiddle': case 'alignBottom': return this.alignOp(act);
        case 'distH': return this.distributeOp('h');
        case 'distV': return this.distributeOp('v');
        case 'strokeCenter': return this.setStrokeAlign('center');
        case 'strokeInside': return this.setStrokeAlign('inside');
        case 'strokeOutside': return this.setStrokeAlign('outside');
        case 'palette': return this.openPalette();
        case 'undo': return this.doUndo();
        case 'redo': return this.doRedo();
        case 'done': return this.commit();
        case 'cancel': return this.close(true);
        case 'fit': return this.fitView();
        case 'fill': case 'fillColor': return this.openColor('fill', info.anchor || btn('fill'));
        case 'stroke': case 'strokeColor': return this.openColor('stroke', info.anchor || btn('stroke'));
        case 'strokeToggle': return this.strokeToggle();
        case 'strokeThinner': return this.strokeStep(-1);
        case 'strokeThicker': return this.strokeStep(1);
        default: return undefined;
      }
    }

    onField(act, v, how) {
      if (act === 'snapSize') {
        const n = parseFloat(v);
        if (!Number.isFinite(n) || n <= 0) return;
        snapPrefs.size = n;
        if (how && (how.commit || how.cancel)) { if (!snapPrefs.grid && how.commit) snapPrefs.grid = true; saveSnap(); this.updateSnapUI(); }
        this._gridSig = null;
        this.render();
        return;
      }
      if (act !== 'weight') return;
      const px = parseFloat(v);
      if (!Number.isFinite(px) || px < 0) return;
      const ts = this.targets();
      if (!ts.length) return;
      if (!this._fieldTyping) { this.pushUndo(); this._fieldTyping = true; }
      ts.forEach((si) => { const s = this.shapes[si]; s.paint = Object.assign({}, s.paint, px > 0 ? { strokeOn: true, weight: px * 381 } : { strokeOn: false }); });
      this.render();
      if (how && (how.commit || how.cancel)) this._fieldTyping = false;
    }

    // ── Command palette ──
    openPalette() {
      if (this.pal) { this.pal.close(); return; }
      const n = this.targets().length;
      const cmds = RK.commandList([
        { act: 'select', label: 'Select points', group: 'Edit Shape', key: 'V' },
        { act: 'pen', label: 'Pen: draw shapes, add / remove points', group: 'Edit Shape', key: 'P' },
        { act: 'snapPoints', label: (snapPrefs.points ? 'Stop snapping' : 'Snap') + ' to points and lines', group: 'Snapping' },
        { act: 'snapPx', label: (snapPrefs.px ? 'Stop snapping' : 'Snap') + ' to whole pixels', group: 'Snapping' },
        { act: 'snapGrid', label: (snapPrefs.grid ? 'Hide the grid and stop snapping to it' : 'Show the grid and snap to it') + ' (' + snapPrefs.size + ' px)', group: 'Snapping', key: (SB.IS_MAC ? '⌘' : 'Ctrl+') + "'" },
        { act: 'undo', label: 'Undo', group: 'Edit Shape', key: (SB.IS_MAC ? '⌘' : 'Ctrl+') + 'Z' },
        { act: 'redo', label: 'Redo', group: 'Edit Shape', key: (SB.IS_MAC ? '⇧⌘' : 'Ctrl+Shift+') + 'Z' },
        { act: 'fit', label: 'Fit to window', group: 'Edit Shape', key: '⇧1', icon: 'expand' },
        { act: 'done', label: 'Done', group: 'Edit Shape', key: '↵' },
        { act: 'cancel', label: 'Discard changes', group: 'Edit Shape', key: 'Esc', icon: 'close' },
      ]).map((c) => Object.assign(c, { enabled: ['select', 'pen', 'undo', 'redo', 'fit', 'done', 'cancel', 'snapPoints', 'snapPx', 'snapGrid'].includes(c.act) || n > 0 }));
      this.pal = RK.palette(this.root, cmds, (act) => { this.host.focus(); this.command(act); }, {
        rect: this.wsRect,
        onClose: () => { this.pal = null; this.host.focus(); },
      });
    }

    // ── Align and distribute ──
    // Several shapes: each shape moves as a whole. Points selected in one
    // shape: the points move. Nothing selected: every shape.
    alignUnits() {
      const bySi = new Map();
      if (this.sel.size) this.sel.forEach((k) => { const si = Number(k.split(':')[0]); if (!bySi.has(si)) bySi.set(si, []); bySi.get(si).push(k); });
      else this.shapes.forEach((sh, si) => { if (!this.live(si)) return; const ks = []; sh.subs.forEach((sp, pi) => sp.nodes.forEach((n, ni) => ks.push(this.key(si, pi, ni)))); bySi.set(si, ks); });
      let units = [...bySi.values()].map((keys) => ({ keys }));
      if (units.length === 1 && this.sel.size) units = units[0].keys.map((k) => ({ keys: [k] }));
      units.forEach((u) => {
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        u.keys.forEach((k) => { const h = this.nodeAt(k); if (!h) return; const q = SB.apply(h.s.toPage, h.n.x, h.n.y); minX = Math.min(minX, q.x); maxX = Math.max(maxX, q.x); minY = Math.min(minY, q.y); maxY = Math.max(maxY, q.y); });
        u.box = { minX, minY, maxX, maxY };
      });
      return units.filter((u) => isFinite(u.box.minX));
    }
    moveKeys(keys, dx, dy) {
      keys.forEach((k) => {
        const h = this.nodeAt(k);
        if (!h) return;
        const Ti = SB.matInv(h.s.toPage);
        if (!Ti) return;
        const lx = Ti[0] * dx + Ti[2] * dy, ly = Ti[1] * dx + Ti[3] * dy;
        const n = h.n;
        n.x += lx; n.y += ly;
        if (n.in) n.in = { x: n.in.x + lx, y: n.in.y + ly };
        if (n.out) n.out = { x: n.out.x + lx, y: n.out.y + ly };
      });
    }
    alignOp(act) {
      const units = this.alignUnits();
      if (units.length < 2) { this.flashHint('Select two or more shapes or points to align', 2200); return; }
      const ref = { minX: Math.min(...units.map((u) => u.box.minX)), minY: Math.min(...units.map((u) => u.box.minY)), maxX: Math.max(...units.map((u) => u.box.maxX)), maxY: Math.max(...units.map((u) => u.box.maxY)) };
      const moves = units.map((u) => {
        const b = u.box;
        let dx = 0, dy = 0;
        if (act === 'alignLeft') dx = ref.minX - b.minX;
        if (act === 'alignRight') dx = ref.maxX - b.maxX;
        if (act === 'alignHCenter') dx = (ref.minX + ref.maxX) / 2 - (b.minX + b.maxX) / 2;
        if (act === 'alignTop') dy = ref.minY - b.minY;
        if (act === 'alignBottom') dy = ref.maxY - b.maxY;
        if (act === 'alignVMiddle') dy = (ref.minY + ref.maxY) / 2 - (b.minY + b.maxY) / 2;
        return { u, dx, dy };
      }).filter((m) => Math.abs(m.dx) > 1e-3 || Math.abs(m.dy) > 1e-3);
      if (!moves.length) return;
      this.pushUndo();
      moves.forEach((m) => this.moveKeys(m.u.keys, m.dx, m.dy));
      this.render();
    }
    distributeOp(axis) {
      const units = this.alignUnits();
      if (units.length < 3) { this.flashHint('Select three or more shapes or points to distribute', 2200); return; }
      const lo = axis === 'h' ? 'minX' : 'minY', hi = axis === 'h' ? 'maxX' : 'maxY';
      units.sort((a, b) => (a.box[lo] + a.box[hi]) - (b.box[lo] + b.box[hi]));
      const span = units[units.length - 1].box[hi] - units[0].box[lo];
      const total = units.reduce((t, u) => t + (u.box[hi] - u.box[lo]), 0);
      const gap = (span - total) / (units.length - 1);
      this.pushUndo();
      let at = units[0].box[hi] + gap;
      units.slice(1, -1).forEach((u) => {
        const d = at - u.box[lo];
        this.moveKeys(u.keys, axis === 'h' ? d : 0, axis === 'h' ? 0 : d);
        at += (u.box[hi] - u.box[lo]) + gap;
      });
      this.render();
    }

    // ── Stroke position ──
    // Slides draws strokes centred on the outline. Inside and outside move
    // the outline by half the weight; the shape keeps its own outline here,
    // so the weight and position stay editable.
    setStrokeAlign(align) {
      const ts = this.targets().filter((si) => this.shapes[si].paint.strokeOn);
      if (!ts.length) { this.flashHint('Turn the stroke on first', 2000); return; }
      const ok = ts.filter((si) => this.shapes[si].subs.every((sp) => sp.closed || sp.nodes.length < 2));
      if (!ok.length) { this.flashHint('Inside and outside need a closed shape', 2200); return; }
      this.pushUndo();
      ok.forEach((si) => { const sh = this.shapes[si]; sh.paint = Object.assign({}, sh.paint, { align }); });
      if (ok.length < ts.length) this.flashHint('Open lines keep a centred stroke', 2200);
      this.render();
    }
    alignedSubs(s) {
      const p = s.paint;
      if (!p.strokeOn || !p.align || p.align === 'center' || typeof GEO === 'undefined') return null;
      const live = s.subs.filter((sp) => sp.nodes.length >= 2);
      if (!live.length || !live.every((sp) => sp.closed)) return null;
      const sig = JSON.stringify(live) + p.align + p.weight + s.toPage.join();
      if (s._al && s._al.sig === sig) return s._al.subs;
      let out = null;
      try {
        const res = GEO.offsetSubs(this.mapSubs(live, s.toPage), (p.align === 'inside' ? -1 : 1) * p.weight / 2);
        out = res.empty ? null : this.toLocal(s, res.subs);
      } catch (err) { console.warn('[svg2slides] stroke offset failed', err); }
      Object.defineProperty(s, '_al', { value: { sig, subs: out }, writable: true, configurable: true, enumerable: false });
      return out;
    }

    // ── Model helpers ──
    pageScale() { return Math.sqrt(Math.abs(this.ctm[0] * this.ctm[3] - this.ctm[1] * this.ctm[2])); }
    live(si) { const s = this.shapes[si]; return !!s && s.subs.some((sp) => sp.nodes.length >= 2); }
    targets() {
      const set = new Set();
      this.sel.forEach((k) => set.add(Number(k.split(':')[0])));
      return (set.size ? [...set] : this.shapes.map((_, i) => i)).filter((si) => this.live(si));
    }
    entryOf(id) { return this.resolved.find((e) => (e[0] === 2 || e[0] === 3) && e[1] === id) || null; }
    parentOf(id) { return this.resolved.find((e) => e[0] === 2 && Array.isArray(e[2]) && e[2].includes(id)) || null; }
    srcTop() { return SB.topLevelIdOf(this.srcIds[0]) || this.srcIds[0]; }
    // Paint order inside each slide object: the payload's group tree, depth
    // first (children are listed bottom to top).
    dfsOrder() {
      const byId = new Map(this.resolved.filter((e) => e[0] === 2 || e[0] === 3).map((e) => [e[1], e]));
      const kids = new Set();
      this.resolved.forEach((e) => { if (e[0] === 2) (e[2] || []).forEach((k) => kids.add(k)); });
      const order = new Map();
      let n = 0;
      const walk = (id, seen) => {
        const e = byId.get(id);
        if (!e || seen.has(id)) return;
        seen.add(id);
        if (e[0] === 3) order.set(id, n++);
        else (e[2] || []).forEach((c) => walk(c, seen));
      };
      this.resolved.forEach((e) => { if ((e[0] === 2 || e[0] === 3) && !kids.has(e[1])) walk(e[1], new Set()); });
      return this.shapes.map((s, i) => (order.has(s.id) ? order.get(s.id) : 1e6 + i));
    }
    paintSorted(list) {
      const rank = this.zRank || [], ord = this.dfsOrder();
      return list.slice().sort((a, b) => (rank[a] || 0) - (rank[b] || 0) || ord[a] - ord[b] || a - b);
    }
    mapSubs(subs, M) {
      const ap = (p) => (p ? SB.apply(M, p.x, p.y) : null);
      return subs.map((sp) => ({ closed: sp.closed, nodes: sp.nodes.map((n) => { const q = ap(n); return { x: q.x, y: q.y, in: ap(n.in), out: ap(n.out), smooth: n.smooth }; }) }));
    }
    pageSubs(s) { return this.mapSubs(s.subs, s.toPage); }
    toLocal(s, pageSubs) { return this.mapSubs(pageSubs, SB.matInv(s.toPage) || [1, 0, 0, 1, 0, 0]); }
    docColors() {
      const out = [];
      this.shapes.forEach((s) => { if (this.live(this.shapes.indexOf(s))) { if (s.paint.filled) out.push(s.paint.fill); if (s.paint.strokeOn) out.push(s.paint.stroke); } });
      return out;
    }

    // A new shape drawn in page units, stacked just above `ref` and kept in
    // the same slide object: inside ref's group when it has one, otherwise
    // ref and the new shapes become a group.
    addShapeAfter(ref, pageSubs, paint) {
      const re = this.entryOf(ref.id);
      if (!re) return null;
      const id = SB.newId();
      let parent = this.parentOf(ref.id);
      let F;
      if (parent) {
        F = SB.localToPage(this.resolved, parent);
      } else {
        F = ref.fix ? ref.fix.slice() : [1, 0, 0, 1, 0, 0];
        parent = [2, SB.newId(), [ref.id], [1, 0, 0, 1, 0, 0]];
        this.resolved.push(parent);
        this.srcOf[parent[1]] = ref.src;
      }
      const props = clone(re[4]);
      const entry = [3, id, 1, [1, 0, 0, 1, 0, 0], props];
      this.resolved.splice(this.resolved.indexOf(re) + 1, 0, entry);
      // After ref and anything already added for it.
      const kids = parent[2];
      let at = kids.indexOf(ref.id);
      while (at + 1 < kids.length && (this.shapes.find((x) => x.id === kids[at + 1]) || {}).addedFor === ref.id) at++;
      kids.splice(at + 1, 0, id);
      const shape = { entry, id, src: ref.src, subs: [], toPage: F, paint: Object.assign({}, paint), added: true, addedFor: ref.id };
      shape.subs = this.toLocal(shape, pageSubs);
      this.shapes.push(shape);
      const ri = this.shapes.indexOf(ref);
      this.zRank.push(this.zRank[ri] !== undefined ? this.zRank[ri] : 0);
      this.srcOf[id] = ref.src;
      this.applyView();
      return shape;
    }

    // ── Rotate / scale ──
    // About the centre of what's in scope: selected points (with their
    // handles), or whole shapes when nothing is selected.
    scopeBBox() {
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      const all = !this.sel.size;
      this.eachNode((n, s, si, pi, ni) => {
        if (!all && !this.sel.has(this.key(si, pi, ni))) return;
        const q = SB.apply(s.toPage, n.x, n.y);
        minX = Math.min(minX, q.x); maxX = Math.max(maxX, q.x);
        minY = Math.min(minY, q.y); maxY = Math.max(maxY, q.y);
      });
      return isFinite(minX) ? { minX, minY, maxX, maxY, cx: (minX + maxX) / 2, cy: (minY + maxY) / 2 } : null;
    }
    transformScope(M, base) {
      const keys = this.sel.size ? this.sel : null;
      this.shapes.forEach((s, si) => {
        const Ti = SB.matInv(s.toPage);
        if (!Ti) return;
        const Lm = SB.matMul(Ti, SB.matMul(M, s.toPage));
        const src = base ? base[si] : s.subs;
        s.subs.forEach((sp, pi) => sp.nodes.forEach((n, ni) => {
          if (keys && !keys.has(this.key(si, pi, ni))) return;
          const o = src[pi].nodes[ni];
          const q = SB.apply(Lm, o.x, o.y);
          const qi = o.in ? SB.apply(Lm, o.in.x, o.in.y) : null;
          const qo = o.out ? SB.apply(Lm, o.out.x, o.out.y) : null;
          n.x = q.x; n.y = q.y; n.in = qi; n.out = qo;
        }));
      });
    }
    about(cx, cy, M) { return SB.matMul([1, 0, 0, 1, cx, cy], SB.matMul(M, [1, 0, 0, 1, -cx, -cy])); }
    rotateBy(deg) {
      const b = this.scopeBBox();
      if (!b) return;
      this.pushUndo();
      const r = deg * Math.PI / 180, c = Math.cos(r), sn = Math.sin(r);
      this.transformScope(this.about(b.cx, b.cy, [c, sn, -sn, c, 0, 0]));
      this.render();
    }
    scaleBy(f) {
      const b = this.scopeBBox();
      if (!b) return;
      this.pushUndo();
      this.transformScope(this.about(b.cx, b.cy, [f, 0, 0, f, 0, 0]));
      this.render();
    }

    // Smart box: shown round two or more selected points.
    //   corner drag        scale (⇧ keeps proportions, ⌥ from the centre)
    //   edge drag          stretch one way (⌥ from the centre)
    //   ⌘ + edge drag      skew (⇧ snaps to 15°)
    //   ⌘ + corner drag,
    //   or just outside    rotate (⇧ snaps to 15°)
    xformBox() {
      if (this.tool !== 'direct' || this.sel.size < 2) return null;
      if (this.drag && this.drag.kind !== 'xform') return null;
      const b = this.drag && this.drag.kind === 'xform' ? this.drag.box0 : this.scopeBBox();
      if (!b) return null;
      const a = SB.apply(this.ctm, b.minX, b.minY), z = SB.apply(this.ctm, b.maxX, b.maxY);
      if (Math.abs(z.x - a.x) < 4 && Math.abs(z.y - a.y) < 4) return null;
      const pad = 8;
      const box = { l: Math.min(a.x, z.x) - pad, t: Math.min(a.y, z.y) - pad, r: Math.max(a.x, z.x) + pad, b: Math.max(a.y, z.y) + pad };
      box.corners = [{ x: box.l, y: box.t }, { x: box.r, y: box.t }, { x: box.r, y: box.b }, { x: box.l, y: box.b }];
      const mx = (box.l + box.r) / 2, my = (box.t + box.b) / 2;
      // Edges: 0 top, 1 right, 2 bottom, 3 left. A flat box (a straight run
      // of points) keeps only the edges that can move something.
      box.edges = [{ x: mx, y: box.t }, { x: box.r, y: my }, { x: mx, y: box.b }, { x: box.l, y: my }];
      box.flatX = Math.abs(z.x - a.x) < 4;
      box.flatY = Math.abs(z.y - a.y) < 4;
      return box;
    }
    drawXform() {
      const g = this.gXform;
      if (!g) return;
      const box = this.drag && this.drag.kind === 'xform' ? null : this.xformBox();
      if (!box) { g.replaceChildren(); return; }
      const els = [sv('rect', { x: box.l, y: box.t, width: box.r - box.l, height: box.b - box.t, fill: 'none', stroke: ACCENT, 'stroke-width': 1, 'stroke-dasharray': '4 3', 'stroke-opacity': 0.8 })];
      const long = (i) => (i % 2 ? box.b - box.t : box.r - box.l) > 40;
      box.edges.forEach((c, i) => { if (long(i)) els.push(sv('rect', { x: c.x - 3, y: c.y - 3, width: 6, height: 6, fill: '#fff', stroke: ACCENT, 'stroke-width': 1.25 })); });
      box.corners.forEach((c) => els.push(sv('rect', { x: c.x - 4, y: c.y - 4, width: 8, height: 8, fill: '#fff', stroke: ACCENT, 'stroke-width': 1.5 })));
      g.replaceChildren(...els);
    }
    // where: 'box' (corners and edges) or 'outside' (the rotate zone).
    hitXform(x, y, where, mods = {}) {
      const box = this.xformBox();
      if (!box) return null;
      const cmd = !!(mods.metaKey || mods.ctrlKey);
      const outside = x < box.l || x > box.r || y < box.t || y > box.b;
      for (let i = 0; i < 4; i++) {
        const c = box.corners[i];
        const d = Math.hypot(c.x - x, c.y - y);
        if (where === 'box' && d <= 6) return { kind: cmd ? 'rotate' : 'scale', corner: i, box };
        if (where === 'outside' && d > 6 && d <= 24 && outside) return { kind: 'rotate', corner: i, box };
      }
      if (where !== 'box') return null;
      // Edges: the whole side, away from the corners.
      const near = 4;
      const sides = [
        { i: 0, on: Math.abs(y - box.t) <= near && x > box.l + 8 && x < box.r - 8 },
        { i: 2, on: Math.abs(y - box.b) <= near && x > box.l + 8 && x < box.r - 8 },
        { i: 1, on: Math.abs(x - box.r) <= near && y > box.t + 8 && y < box.b - 8 },
        { i: 3, on: Math.abs(x - box.l) <= near && y > box.t + 8 && y < box.b - 8 },
      ];
      for (const sd of sides) {
        if (!sd.on) continue;
        const horiz = sd.i % 2 === 0; // top/bottom
        if (!cmd && (horiz ? box.flatY : box.flatX)) continue; // nothing to stretch
        return { kind: cmd ? 'skew' : 'edge', edge: sd.i, box };
      }
      return null;
    }
    xformCursor(hx) {
      if (!hx) return '';
      if (hx.kind === 'rotate') return ROTATE_CURSOR;
      if (hx.kind === 'scale') return hx.corner % 2 ? 'nesw-resize' : 'nwse-resize';
      if (hx.kind === 'edge') return hx.edge % 2 ? 'ew-resize' : 'ns-resize';
      if (hx.kind === 'skew') return hx.edge % 2 ? SKEW_V_CURSOR : SKEW_H_CURSOR;
      return '';
    }
    hoverCursor(e) {
      const pt = this._hoverPt;
      if (!pt || this.drag || this.tool !== 'direct' || !this.svg || this.spaceDown) return;
      const hx = this.hitXform(pt.x, pt.y, 'box', e) || (!this.hitNode(pt.x, pt.y) && this.hitXform(pt.x, pt.y, 'outside', e));
      const c = this.xformCursor(hx);
      if (this.svg.style.cursor !== c && !(this.svg.style.cursor === 'grab' && !c)) this.svg.style.cursor = c;
    }
    startXform(hit, x, y) {
      const b = this.scopeBBox();
      if (!b) return;
      const inv = SB.matInv(this.ctm);
      this.drag = {
        kind: 'xform', mode: hit.kind, corner: hit.corner, edge: hit.edge, start: { x, y }, pushed: false, box0: b,
        base: clone(this.shapes.map((sh) => sh.subs)), inv,
        startPage: SB.apply(inv, x, y),
      };
      this.render();
    }
    moveXform(x, y, e) {
      const d = this.drag, b = d.box0;
      const P = SB.apply(d.inv, x, y);
      const at = (F, M0) => SB.matMul([1, 0, 0, 1, F[0], F[1]], SB.matMul(M0, [1, 0, 0, 1, -F[0], -F[1]]));
      const snap = (ang) => Math.round(ang / (Math.PI / 12)) * (Math.PI / 12);
      const safe = (v) => (!Number.isFinite(v) ? 1 : Math.abs(v) < 1e-3 ? (v < 0 ? -1e-3 : 1e-3) : v);
      let M;
      if (d.mode === 'rotate') {
        let ang = Math.atan2(P.y - b.cy, P.x - b.cx) - Math.atan2(d.startPage.y - b.cy, d.startPage.x - b.cx);
        if (e.shiftKey) ang = snap(ang);
        const c = Math.cos(ang), sn = Math.sin(ang);
        M = this.about(b.cx, b.cy, [c, sn, -sn, c, 0, 0]);
      } else if (d.mode === 'scale') {
        const cs = [[b.minX, b.minY], [b.maxX, b.minY], [b.maxX, b.maxY], [b.minX, b.maxY]];
        const C = cs[d.corner];
        const F = e.altKey ? [b.cx, b.cy] : cs[(d.corner + 2) % 4];
        let sx = (C[0] - F[0]) ? (P.x - F[0]) / (C[0] - F[0]) : 1;
        let sy = (C[1] - F[1]) ? (P.y - F[1]) / (C[1] - F[1]) : 1;
        if (e.shiftKey) { const m = Math.max(Math.abs(sx), Math.abs(sy)); sx = Math.sign(sx || 1) * m; sy = Math.sign(sy || 1) * m; }
        M = at(F, [safe(sx), 0, 0, safe(sy), 0, 0]);
      } else {
        // Edges. E: the dragged side's coordinate; F: the fixed one.
        const horiz = d.edge % 2 === 0; // top/bottom
        const E = horiz ? (d.edge === 0 ? b.minY : b.maxY) : (d.edge === 3 ? b.minX : b.maxX);
        const F = horiz ? (e.altKey ? b.cy : (d.edge === 0 ? b.maxY : b.minY)) : (e.altKey ? b.cx : (d.edge === 3 ? b.maxX : b.minX));
        const span = E - F;
        if (d.mode === 'edge') {
          const f = span ? (horiz ? (P.y - F) / span : (P.x - F) / span) : 1;
          M = horiz ? at([0, F], [1, 0, 0, safe(f), 0, 0]) : at([F, 0], [safe(f), 0, 0, 1, 0, 0]);
        } else {
          // Skew: slide the dragged side along itself; the fixed side stays.
          let k = span ? (horiz ? (P.x - d.startPage.x) / span : (P.y - d.startPage.y) / span) : 0;
          if (e.shiftKey) k = Math.tan(Math.max(-Math.PI / 2.4, Math.min(Math.PI / 2.4, snap(Math.atan(k)))));
          M = horiz ? [1, 0, k, 1, -k * F, 0] : [1, k, 0, 1, 0, -k * F];
        }
      }
      this.transformScope(M, d.base);
      this.render();
    }

    // ── Arrange ──
    // Shapes inside one group of the object: restack within the group here.
    // Whole objects (or everything being edited): Slides' own Arrange moves
    // the originals, which stay selected under the editor, and the shapes
    // stacked above are re-read so the view stays true.
    arrange(dir) {
      const ts = this.targets();
      if (!ts.length) return;
      const ids = ts.map((si) => this.shapes[si].id);
      const parents = [...new Set(ids.map((id) => { const p = this.parentOf(id); return p ? p[1] : null; }))];
      const everything = ts.length === this.shapes.filter((_, i) => this.live(i)).length;
      if (!everything && parents.length === 1 && parents[0]) {
        const P = this.entryOf(parents[0]);
        const list = P[2].slice();
        const mv = new Set(ids);
        let next = list;
        if (dir === 'front') next = [...list.filter((x) => !mv.has(x)), ...list.filter((x) => mv.has(x))];
        else if (dir === 'back') next = [...list.filter((x) => mv.has(x)), ...list.filter((x) => !mv.has(x))];
        else if (dir === 'forward') { next = list.slice(); for (let i = next.length - 2; i >= 0; i--) if (mv.has(next[i]) && !mv.has(next[i + 1])) [next[i], next[i + 1]] = [next[i + 1], next[i]]; }
        else { next = list.slice(); for (let i = 1; i < next.length; i++) if (mv.has(next[i]) && !mv.has(next[i - 1])) [next[i], next[i - 1]] = [next[i - 1], next[i]]; }
        if (next.join() === list.join()) return;
        this.pushUndo();
        P[2] = next;
        this.render();
        return;
      }
      if (!everything && this.srcIds.length > 1) this.flashHint('Arrange moves everything being edited together. Edit one object to move it alone.', 3500);
      this.nativeArrange(dir);
    }
    async nativeArrange(dir) {
      if (this._arranging) return;
      this._arranging = true;
      try {
        if (!this.nativeArranged) { this.nativeStart = SB.topLevelOrder().indexOf(this.srcTop()); }
        this.pushUndo();
        this.nativeArranged = true;
        SB.focusTextbox();
        SB.pressArrange(dir);
        await SB.sleep(140);
        this.rebuildCover();
      } finally {
        this._arranging = false;
        this.host.focus();
      }
    }
    async nativeMoveTo(index) {
      SB.focusTextbox();
      await SB.moveToIndex(this.srcTop(), index);
      this.rebuildCover();
      this.host.focus();
    }
    rebuildCover() {
      this.gDefs.replaceChildren();
      this.buildCover();
      this.render();
    }

    // ── Combine ──
    booleanOp(op) {
      const ts = this.paintSorted(this.targets());
      if (ts.length < 2) { this.flashHint('Select points on two or more shapes, or select none to combine them all', 3000); return; }
      const input = ts.map((si) => ({ subs: this.pageSubs(this.shapes[si]).map((sp) => Object.assign(sp, { closed: true })), fillRule: 'evenodd' }));
      let res;
      try { res = GEO.boolean(op, input); } catch (err) { console.warn('[svg2slides] boolean failed', err); this.flashHint('Couldn’t combine these shapes', 2500); return; }
      if (res.empty) { this.flashHint(op === 'intersect' ? 'These shapes don’t overlap' : 'Nothing would be left', 2500); return; }
      this.pushUndo();
      const bottom = this.shapes[ts[0]];
      bottom.subs = this.toLocal(bottom, res.subs);
      ts.slice(1).forEach((si) => { this.shapes[si].subs = []; });
      this.sel.clear();
      this.render();
    }

    groupOp() {
      const ts = this.paintSorted(this.targets());
      if (ts.length < 2) { this.flashHint('Select points on two or more shapes to group them', 2500); return; }
      const ids = ts.map((si) => this.shapes[si].id);
      const parents = ids.map((id) => this.parentOf(id));
      const pid = parents[0] ? parents[0][1] : null;
      if (!parents.every((p) => (p ? p[1] : null) === pid)) { this.flashHint('Pick shapes at the same level to group them', 2500); return; }
      if (pid && parents[0][2].length === ids.length) { this.flashHint('Already a group', 2000); return; }
      this.pushUndo();
      const gid = SB.newId();
      if (pid) {
        const P = parents[0];
        const first = P[2].findIndex((k) => ids.includes(k));
        const inOrder = P[2].filter((k) => ids.includes(k));
        P[2] = P[2].filter((k) => !ids.includes(k));
        P[2].splice(first, 0, gid);
        this.resolved.push([2, gid, inOrder, [1, 0, 0, 1, 0, 0]]);
      } else {
        this.resolved.push([2, gid, ids, [1, 0, 0, 1, 0, 0]]);
      }
      this.srcOf[gid] = this.shapes[ts[0]].src;
      this.render();
    }

    ungroupOp() {
      const ts = this.targets();
      const P = ts.length ? this.parentOf(this.shapes[ts[0]].id) : null;
      if (!P) { this.flashHint('Nothing here is grouped', 2000); return; }
      this.pushUndo();
      const M = Array.isArray(P[3]) ? P[3] : [1, 0, 0, 1, 0, 0];
      P[2].forEach((k) => { const e = this.entryOf(k); if (e && Array.isArray(e[3])) e[3] = SB.matMul(M, e[3]); });
      const GP = this.parentOf(P[1]);
      if (GP) GP[2].splice(GP[2].indexOf(P[1]), 1, ...P[2]);
      this.resolved = this.resolved.filter((e) => e !== P);
      this.render();
    }

    // ── Outline ──
    strokeStyleOf(src) {
      const g = SB.elementFor(src);
      const p = g && [...g.querySelectorAll('path')].find((q) => { const cs = getComputedStyle(q); return cs.stroke && cs.stroke !== 'none' && parseFloat(cs.strokeWidth) > 0; });
      const cs = p ? getComputedStyle(p) : null;
      const join = cs ? cs.strokeLinejoin : 'miter';
      return { cap: cs ? cs.strokeLinecap : 'butt', join: join === 'arcs' || join === 'miter-clip' ? 'miter' : join, miterLimit: cs ? parseFloat(cs.strokeMiterlimit) || 4 : 4 };
    }
    outlineStrokeOp() {
      const ts = this.targets().filter((si) => this.shapes[si].paint.strokeOn);
      if (!ts.length) { this.flashHint('Nothing here has a stroke', 2000); return; }
      const made = [];
      for (const si of ts) {
        const s = this.shapes[si];
        let out;
        try { out = GEO.outlineStroke(this.pageSubs(s), s.paint.weight, this.strokeStyleOf(s.src)).subs; } catch (err) { console.warn('[svg2slides] outline stroke failed', err); continue; }
        if (out.length) made.push({ s, out });
      }
      if (!made.length) { this.flashHint('Couldn’t outline that stroke', 2000); return; }
      this.pushUndo();
      made.forEach(({ s, out }) => {
        if (s.paint.filled) {
          this.addShapeAfter(s, out, Object.assign({}, s.paint, { fill: s.paint.stroke, filled: true, strokeOn: false }));
          s.paint = Object.assign({}, s.paint, { strokeOn: false });
        } else {
          s.subs = this.toLocal(s, out);
          s.paint = Object.assign({}, s.paint, { fill: s.paint.stroke, filled: true, strokeOn: false });
        }
      });
      this.sel.clear();
      this.render();
    }

    async outlineTextOp() {
      const ST = self.SVG2S_SHAPES;
      const srcs = [...new Set(this.targets().map((si) => this.shapes[si].src))].filter((src) => this.textSrcs.has(src));
      if (!ST || !srcs.length) { this.flashHint('Nothing here has text', 2000); return; }
      if (this._outlining) return;
      this._outlining = true;
      this.rail.classList.add('busy');
      try {
        const inv = SB.matInv(SB.pageCTM());
        const plans = [];
        for (const src of srcs) plans.push({ src, runs: await ST.textOutlines(src, inv, true) });
        this.pushUndo();
        for (const { src, runs } of plans) {
          const mine = this.shapes.filter((s) => s.src === src && this.live(this.shapes.indexOf(s)));
          const ids = new Set([src, ...this.shapes.filter((s) => s.src === src).map((s) => s.id)]);
          const ref = mine.find((s) => this.resolved.some((e) => e[0] === 15 && e[1] === s.id)) || mine[0];
          if (!ref) continue;
          const unit = payloadUnits(this.original).find((u) => u.ids.has(src));
          this.textMemo = this.textMemo || {};
          if (unit) this.textMemo[src] = { entries: clone(unit.entries), label: ST.describeText ? ST.describeText(src) : '' };
          runs.forEach((r) => { const g = this.addShapeAfter(ref, r.subs, { fill: r.fill, filled: true, stroke: '#000000', weight: 381, strokeOn: false }); if (g) g.fromText = src; });
          this.resolved = this.resolved.filter((e) => !((e[0] === 15 || e[0] === 17) && ids.has(e[1])));
          this.textSrcs.delete(src);
        }
        const note = ST.takeNotes && ST.takeNotes();
        if (note) this.flashHint(note, 5000);
        this.render();
      } catch (err) {
        console.warn('[svg2slides] outline text failed', err);
        this.flashHint((err && err.userMessage) || 'Couldn’t outline the text', 3500);
      } finally {
        this._outlining = false;
        this.rail.classList.remove('busy');
        this.host.focus();
      }
    }

    // ── Fill and stroke ──
    repaint(fn) {
      const ts = this.targets();
      if (!ts.length) return;
      this.pushUndo();
      ts.forEach((si) => { const s = this.shapes[si]; s.paint = Object.assign({}, s.paint, fn(s.paint)); });
      this.render();
    }
    openColor(which, anchor) {
      if (this.pop) { const was = this.pop.which; this.pop.close(); if (was === which) return; }
      const ts = this.targets();
      if (!ts.length) return;
      const p = this.shapes[ts[0]].paint;
      const stroke = which === 'stroke';
      const r = anchor || this.rail.getBoundingClientRect();
      const pop = RK.colorPopover(this.root, { right: this.rail.getBoundingClientRect().right, top: r.top }, {
        title: stroke ? 'Stroke' : 'Fill', key: SB.SHORTCUT_LABEL[stroke ? 'strokeColor' : 'fillColor'],
        value: stroke ? (p.strokeOn ? p.stroke : null) : (p.filled ? p.fill : null),
        noneLabel: stroke ? 'No stroke' : 'No fill', doc: this.docColors(),
        weights: stroke ? SB.WEIGHTS : null, weight: p.weight / 381, strokeOn: p.strokeOn,
        onClose: () => { if (this.pop === pop) this.pop = null; this.host.focus(); },
      }, (pick) => {
        if (stroke) {
          if (pick.none) this.repaint(() => ({ strokeOn: false }));
          else if (pick.weight) this.repaint(() => ({ strokeOn: true, weight: pick.weight * 381 }));
          else this.repaint(() => ({ strokeOn: true, stroke: pick.color }));
        } else if (pick.none) this.repaint(() => ({ filled: false }));
        else this.repaint(() => ({ filled: true, fill: pick.color }));
      });
      pop.which = which;
      this.pop = pop;
    }
    strokeToggle() {
      const ts = this.targets();
      if (!ts.length) return;
      const allOn = ts.every((si) => this.shapes[si].paint.strokeOn);
      this.repaint(() => ({ strokeOn: !allOn }));
    }
    strokeStep(dir) {
      const ts = this.targets();
      if (!ts.length) return;
      const W = SB.WEIGHTS;
      this.repaint((p) => {
        const px = p.strokeOn ? p.weight / 381 : 0;
        let w;
        if (dir > 0) w = W.find((v) => v > px + 0.25) || W[W.length - 1];
        else w = [...W].reverse().find((v) => v < px - 0.25);
        return w ? { strokeOn: true, weight: w * 381 } : { strokeOn: false };
      });
    }

    // Dim what can't apply; show the current fill and stroke in the rail.
    alignUnitsCount() {
      const si = new Set([...this.sel].map((k) => k.split(':')[0]));
      if (!this.sel.size) return this.shapes.filter((_, i) => this.live(i)).length;
      return si.size === 1 ? this.sel.size : si.size;
    }
    updateRailState() {
      if (!this.rk) return;
      const ts = this.targets();
      const n = ts.length;
      const parents = new Set(ts.map((si) => { const p = this.parentOf(this.shapes[si].id); return p ? p[1] : null; }));
      const rk = this.rk;
      ['union', 'subtract', 'intersect', 'exclude'].forEach((a) => rk.setDim(a, n < 2));
      rk.setDim('group', n < 2 || parents.size > 1);
      rk.setDim('ungroup', !(n && this.parentOf(this.shapes[ts[0]].id)));
      rk.setDim('outlineStroke', !ts.some((si) => this.shapes[si].paint.strokeOn));
      rk.setDim('outlineText', !ts.some((si) => this.textSrcs.has(this.shapes[si].src)));
      ['arrange', 'fill', 'stroke', 'forward', 'backward', 'front', 'back', 'rotL15', 'rotR15', 'scaleUp', 'scaleDown'].forEach((a) => rk.setDim(a, !n));
      rk.setDim('combine', n < 2);
      rk.setDim('outline', !ts.some((si) => this.shapes[si].paint.strokeOn || this.textSrcs.has(this.shapes[si].src)));
      const p = n ? this.shapes[ts[0]].paint : null;
      rk.setSwatch('fill', p && p.filled ? p.fill : null);
      rk.setSwatch('stroke', p && p.strokeOn ? p.stroke : null);
      rk.setDim('weight', !n);
      rk.setDim('align', n < 1);
      ['alignLeft', 'alignHCenter', 'alignRight', 'alignTop', 'alignVMiddle', 'alignBottom'].forEach((a) => rk.setDim(a, this.alignUnitsCount() < 2));
      ['distH', 'distV'].forEach((a) => rk.setDim(a, this.alignUnitsCount() < 3));
      rk.setDim('strokeAlign', !ts.some((si) => this.shapes[si].paint.strokeOn));
      rk.setDim('strokeToggle', !n);
      rk.setIcon('strokeAlign', { center: 'strokeCenter', inside: 'strokeInside', outside: 'strokeOutside' }[(p && p.align) || 'center']);
      const ws = ts.map((si) => { const q = this.shapes[si].paint; return q.strokeOn ? Math.round(q.weight / 381 * 100) / 100 : 0; });
      rk.setField('weight', !n ? '' : ws.every((w) => w === ws[0]) ? ws[0] : null);
    }

    // ── Commit / close ──
    buildResolved() {
      const idMap = new Map();
      this.resolved.forEach((e) => { if ((e[0] === 2 || e[0] === 3) && typeof e[1] === 'string') idMap.set(e[1], SB.newId()); });
      this.idBack = new Map([...idMap].map(([o, n]) => [n, o]));
      const byId = new Map(this.shapes.map((s) => [s.id, s]));
      const dropped = new Set();
      const out = [];

      for (const e of this.resolved) {
        if (e[0] === 3 && byId.has(e[1])) {
          const s = byId.get(e[1]);
          const al = this.alignedSubs(s);
          const subs = clone(al || s.subs);
          if (!subs.some((sp) => sp.nodes.length >= 2)) { dropped.add(e[1]); continue; }
          // A masked picture (image fill): its place is set relative to the
          // path's exact box, so keep the picture where it was as the path
          // changes (box before and after, in the shape's own units).
          let picFit = null;
          if (SB.getProp(e[4], 86) === 1) {
            const rec0 = SB.pathRecord(e);
            const old = rec0 && SB.decodePath(rec0[2], rec0[3]);
            const b0 = old && SB.subsBBox(old), b1 = SB.subsBBox(subs);
            if (b0 && b1) picFit = SB.imageFillProps(SB.pictureRect(e[4], b0), b1);
          }
          const norm = SB.normalizeSubs(subs);
          const design = al ? clone(s.subs).map((sp) => ({ closed: sp.closed, nodes: sp.nodes.map((n) => ({ x: n.x - norm.dx, y: n.y - norm.dy, in: n.in ? { x: n.in.x - norm.dx, y: n.in.y - norm.dy } : null, out: n.out ? { x: n.out.x - norm.dx, y: n.out.y - norm.dy } : null, smooth: n.smooth })) })) : null;
          const { meta, coords } = SB.encodePath(subs);
          const m = e[3];
          const newM = [m[0], m[1], m[2], m[3], m[4] + m[0] * norm.dx + m[2] * norm.dy, m[5] + m[1] * norm.dx + m[3] * norm.dy];
          let props = SB.applyPaint(clone(e[4]), s.paint);
          if (picFit) {
            // Keep the picture as the fill unless a colour was chosen here.
            const p0 = SB.paintFromProps(e[4]);
            if (s.paint.fill === p0.fill && s.paint.filled === p0.filled) {
              [14, 15].forEach((k) => { SB.removeProp(props, k); const v = SB.getProp(e[4], k); if (v !== undefined) SB.setProp(props, k, v); });
            }
            if (SB.getProp(props, 86) === 1) [84, 85, 79, 80].forEach((k) => SB.setProp(props, k, picFit[k]));
          }
          const rec = clone(SB.pathRecord(e));
          rec[2] = meta;
          rec[3] = coords;
          SB.setProp(props, 12, [rec]);
          SB.setProp(props, 8, norm.w);
          SB.setProp(props, 9, norm.h);
          const made = [3, idMap.get(e[1]), SB.typeFor(e[2], subs), newM, props, ...clone(e.slice(5))];
          out.push(made);
          if (design && self.SVG2S_SHAPES && self.SVG2S_SHAPES.remember) self.SVG2S_SHAPES.remember(SB.pathFingerprint(made), { kind: 'align', align: s.paint.align, design });
        } else if (e[0] === 2) {
          const kids = (e[2] || []).filter((id) => !dropped.has(id)).map((id) => idMap.get(id) || id);
          if (!kids.length) continue;
          out.push([2, idMap.get(e[1]), kids, ...clone(e.slice(3))]);
        } else {
          const c = clone(e);
          if (typeof c[1] === 'string' && idMap.has(c[1])) {
            if (dropped.has(c[1])) continue;
            c[1] = idMap.get(c[1]);
          }
          out.push(c);
        }
      }
      // A group left with one child: ungroup it, folding the group's
      // transform into the child so it stays put.
      let final = out;
      for (let guard = 0; guard < 50; guard++) {
        const g = final.find((e) => e[0] === 2 && e[2].length < 2);
        if (!g) break;
        const child = g[2][0];
        final = final.filter((e) => e !== g);
        if (child) {
          const ce = final.find((e) => (e[0] === 2 || e[0] === 3) && e[1] === child);
          if (ce && Array.isArray(g[3]) && Array.isArray(ce[3])) ce[3] = SB.matMul(g[3], ce[3]);
          final.forEach((e) => { if (e[0] === 2) e[2] = e[2].map((id) => (id === g[1] ? child : id)); });
        }
      }
      // Shapes edited from inside a group paste at the top level, so give
      // their units absolute transforms (see placeFromRendering).
      const fixOf = new Map();
      this.shapes.forEach((sh) => { if (sh.fix) fixOf.set(idMap.get(sh.id), sh.fix); });
      if (fixOf.size) {
        const childIds = new Set();
        final.forEach((e) => { if (e[0] === 2) e[2].forEach((c) => childIds.add(c)); });
        const byId = new Map(final.filter((e) => e[0] === 2 || e[0] === 3).map((e) => [e[1], e]));
        const firstFix = (id) => {
          if (fixOf.has(id)) return fixOf.get(id);
          const e = byId.get(id);
          if (e && e[0] === 2) for (const c of e[2]) { const f = firstFix(c); if (f) return f; }
          return null;
        };
        final.forEach((e) => {
          if ((e[0] !== 2 && e[0] !== 3) || childIds.has(e[1])) return;
          const f = firstFix(e[1]);
          if (f && Array.isArray(e[3])) e[3] = SB.matMul(f, e[3]);
        });
      }
      return final;
    }

    onKeyUp(e) {
      if (['Meta', 'Control', 'Alt', 'Shift'].includes(e.key)) this.hoverCursor(e);
      if (e.key === ' ') {
        e.preventDefault();
        this.spaceDown = false;
        if (!this.drag) this.setPanCursor('');
      }
    }

    teardown(restoreOriginals = true) {
      if (!this._endLater) setTimeout(() => SB.endMacro(), 0);
      cancelAnimationFrame(this._raf);
      if (this.zoomLayer) this.zoomLayer.remove();
      this.zoomLayer = null;
      window.removeEventListener('pointermove', this._mv, true);
      window.removeEventListener('pointerup', this._up, true);
      window.removeEventListener('resize', this.onResize);
      if (this.pop) this.pop.close();
      if (this.rk) this.rk.destroy();
      if (restoreOriginals) this.restoreOriginals();
      this.restoreSlidesChrome();
      this.host.remove();
      editor = null;
    }

    restoreOriginals() {
      this.hidden.forEach(([el, v]) => { el.style.visibility = v || ''; delete el.dataset.svg2slidesHidden; });
    }

    close() {
      // Nothing on the slide has changed before Done (conversions happen in
      // memory), so closing just restores what we hid. The one exception is
      // Arrange on whole objects, which moves the originals: put them back.
      const back = this.nativeArranged && this.nativeStart >= 0 ? { top: this.srcTop(), at: this.nativeStart } : null;
      this._endLater = true;
      this.teardown();
      SB.focusTextbox();
      const moved = back && SB.topLevelOrder().indexOf(back.top) !== back.at ? SB.moveToIndex(back.top, back.at) : null;
      Promise.resolve(moved).finally(() => SB.endMacro());
    }

    async commit() {
      if (this.committing) return;
      // Where Slides should end up looking: the editor's current zoom, with
      // the workspace centre showing the same page point.
      const handoff = this.isIdentityView() ? null : (() => {
        const r = this.wsRect;
        const cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2;
        const P = SB.apply(SB.matInv(this.ctm), cx, cy);
        return { pct: SB.zoomPctFromCTM(this.ctm), P, cx, cy };
      })();

      if (!this.dirty) {
        if (handoff) { this.committing = true; this.rail.classList.add('busy'); await SB.matchSlidesView(handoff.pct, handoff.P, handoff.cx, handoff.cy); }
        this.close();
        return;
      }
      this.committing = true;
      this.rail.classList.add('busy');
      this.hideTip();
      const resolved = this.buildResolved();
      // Outlined text made here can be restored later from the toolbar.
      if (this.textMemo && self.SVG2S_SHAPES && self.SVG2S_SHAPES.noteOutlinedText) {
        resolved.forEach((e) => {
          if (e[0] !== 3) return;
          const old = this.idBack && this.idBack.get(e[1]);
          const sh = old && this.shapes.find((x) => x.id === old);
          const memo = sh && sh.fromText && this.textMemo[sh.fromText];
          if (memo) { try { self.SVG2S_SHAPES.noteOutlinedText(resolved, e, memo.entries, memo.label); } catch (err) { console.warn('[svg2slides] text memory', err); } }
        });
      }
      const promptAt = this.rail.getBoundingClientRect();
      const nShapes = resolved.filter((e) => e[0] === 3).length;
      const sig = resolved.filter((e) => e[0] === 3).map((e) => SB.getProp(e[4], 8) + 'x' + SB.getProp(e[4], 9)).sort().join(',');
      const oldIds = this.srcIds;
      // Where each slide object sits in the stacking order, before we touch
      // anything: the replacements go back into the same slots.
      const order0 = SB.topLevelOrder();
      const oldUnits = payloadUnits(this.original).map((u) => {
        const top = SB.topLevelIdOf(u.id);
        return Object.assign(u, { slot: { top, exact: top === u.id, index: order0.indexOf(top) } });
      });
      const slotFor = (newUnit) => {
        for (const nid of newUnit.ids) {
          const rid = (this.idBack && this.idBack.get(nid)) || nid;
          const oid = this.srcOf[rid] || rid;
          const u = oldUnits.find((x) => x.ids.has(oid));
          if (u) return u.slot;
        }
        return null;
      };

      // Fallback first, while we're still inside the Done click/keypress:
      // put the edited shape on the OS clipboard so ⌘V works if the direct
      // replace is rejected.
      let copied = false;
      if (nShapes) {
        try { copied = writeClipBundleLogged({ [SB.MIME]: SB.wrap(resolved) }); } catch (err) { console.warn('[svg2slides] fallback copy failed', err); }
      }

      // The overlay stays up (frozen) through the swap and the view
      // handoff, so the user never sees Slides jump: delete the original
      // (still selected, since the overlay blocked all input), paste the
      // edit at the same transform, match Slides' zoom/scroll to the
      // editor's view, then remove the overlay.
      // Masked pictures only come back if the paste looks like a real copy
      // of them (see SB.withClip): take one before the originals go.
      const clip = resolved.some((e) => e[0] === 3 && typeof SB.getProp(e[4], 49) === 'string') ? SB.readClip() : null;
      if (!(await deleteSelected(oldIds))) {
        console.warn('[svg2slides] scripted delete did not remove the original');
        this.teardown(true);
        showCommitPrompt(promptAt, copied ? 'Delete the original, then ' + pasteLabel() + ' to commit changes' : 'Could not apply changes');
        return;
      }
      let ok = true;
      if (nShapes) ok = clip ? await SB.withClip(clip, () => pasteInPlace(resolved, slotFor)) : await pasteInPlace(resolved, slotFor);
      if (handoff) await SB.matchSlidesView(handoff.pct, handoff.P, handoff.cx, handoff.cy);
      this.teardown(false);
      SB.focusTextbox();
      if (ok) { console.log('[svg2slides] edit committed'); return; }
      console.warn('[svg2slides] scripted paste not confirmed — falling back to ⌘V');
      if (copied) {
        showCommitPrompt(promptAt, pasteLabel() + ' to commit changes');
        armPasteDetection(SB.iframe());
      }
    }
  }

  // Shared with shape-tools.js: the same delete + paste-in-place that Done
  // uses, so Shape tools results land in the same stacking slots, and the
  // rail's Edit Shape button opens this editor in the rail's own spot.
  self.SVG2S_EDIT = { payloadUnits, pasteInPlace, deleteSelected, openEditor, convertAndOpen, isOpen: () => !!editor };

  function pasteLabel() {
    return (typeof isMac === 'function' && isMac()) ? '⌘ + V' : 'Ctrl + V';
  }

  function showCommitPrompt(rect, text) {
    if (typeof showInsertTooltip === 'function') {
      showInsertTooltip(rect.left + rect.width / 2, rect.top + 30);
      const el = document.getElementById('svg2slides-insert-tooltip');
      if (el) {
        const style = el.querySelector('style');
        el.textContent = '';
        if (style) el.appendChild(style);
        el.append(text);
      }
      dismissPromptLater();
    }
  }

  // The prompt goes on the next paste, Escape, click, or after 8 s.
  function dismissPromptLater() {
    const done = () => {
      clearTimeout(timer);
      document.removeEventListener('mousedown', done, true);
      if (doc) doc.removeEventListener('keydown', onKey, true);
      document.removeEventListener('keydown', onKey, true);
      if (typeof removeInsertTooltip === 'function') removeInsertTooltip();
    };
    const onKey = (e) => {
      if (!e.isTrusted) return;
      if (e.key === 'Escape' || ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'v')) setTimeout(done, 300);
    };
    let doc = null;
    try { doc = SB.iframe() && SB.iframe().contentDocument; } catch { doc = null; }
    const timer = setTimeout(done, 8000);
    setTimeout(() => {
      document.addEventListener('mousedown', done, true);
      if (doc) doc.addEventListener('keydown', onKey, true);
      document.addEventListener('keydown', onKey, true);
    }, 0);
  }
})();
