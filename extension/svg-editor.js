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
  const SVGNS = 'http://www.w3.org/2000/svg';

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
    for (let attempt = 0; attempt < 2; attempt++) {
      SB.focusTextbox();
      await SB.sleep(attempt ? 120 : 30);
      SB.pressKey('Delete');
      await SB.sleep(150);
      if (!ids.some((id) => SB.elementFor(id))) return true;
    }
    return false;
  }

  // ── Convert a native object, then edit it ──────────────────────────────
  // Delete + paste the converted shapes in place (same mechanism as Done),
  // then open the editor on them. Cancel in the editor puts the original
  // back the same way.
  let converting = false;
  async function convertAndOpen(hint) {
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
      const shapesOf = (r) => r.filter((e) => e[0] === 3);
      const sigOf = (r) => shapesOf(r).map((e) => SB.getProp(e[4], 8) + 'x' + SB.getProp(e[4], 9)).sort().join(',');
      const want = sigOf(conv.resolved), n = shapesOf(conv.resolved).length;
      const oldIds = shapesOf(original).map((e) => e[1]);

      if (!(await deleteSelected(oldIds))) { console.warn('[svg2slides] delete did not remove the original'); return; }
      SB.paste(conv.resolved);
      const pasted = await SB.waitForSelection((s) => shapesOf(s).length === n && sigOf(s) === want);
      if (!pasted) {
        console.warn('[svg2slides] converted paste not confirmed — restoring original');
        SB.paste(original);
        return;
      }
      console.log('[svg2slides] converted', conv.converted);
      openEditor(pasted, original);
    } finally {
      converting = false;
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
  function openEditor(hint, restoreOnCancel = null) {
    if (editor) return;
    // Re-read the live selection: what we edit must be exactly what Done
    // deletes. If Slides went into text editing (or its own point editing)
    // on the double-click, Escape returns to plain shape selection.
    const wanted = new Set(hint.filter((x) => x[0] === 3).map((x) => x[1]));
    const matches = (s) => s && s.some((x) => x[0] === 3 && wanted.has(x[1])) && s.filter((x) => x[0] === 3).every(SB.isEditableShape);
    let resolved = SB.readSelection();
    if (!matches(resolved)) {
      SB.pressKey('Escape');
      resolved = SB.readSelection();
    }
    if (!matches(resolved)) { console.warn('[svg2slides] selection changed — not opening editor'); return; }
    const ctm = SB.pageCTM();
    if (!ctm) { console.warn('[svg2slides] no page CTM — cannot open editor'); return; }
    const shapes = [];
    for (const entry of resolved) {
      if (!SB.isEditableShape(entry)) continue;
      const rec = SB.pathRecord(entry);
      const subs = SB.decodePath(rec[2], rec[3]);
      if (!subs) { console.warn('[svg2slides] could not decode', entry[1]); return; }
      const fill = SB.getProp(entry[4], 15);
      shapes.push({
        entry,
        id: entry[1],
        subs,
        toPage: SB.localToPage(resolved, entry),
        fill: typeof fill === 'string' ? fill : '#9e9e9e',
        filled: SB.getProp(entry[4], 14) !== 0,
      });
    }
    if (!shapes.length) return;
    const vis = SB.visibleWorkspaceRect();
    if (vis.right - vis.left < 160 || vis.bottom - vis.top < 120) {
      console.warn('[svg2slides] canvas too small or off-screen — not opening editor', vis);
      return;
    }
    try {
      editor = new Editor(resolved, shapes, ctm);
      editor.restoreOnCancel = restoreOnCancel;
    } catch (err) {
      // Never leave a half-built overlay holding the page hostage.
      console.error('[svg2slides] editor failed to open', err);
      emergencyRestore();
      editor = null;
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

  class Editor {
    constructor(resolved, shapes, ctm) {
      this.resolved = resolved;
      this.shapes = shapes;
      this.tool = 'direct';
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
      shapes.forEach((s) => {
        const el = SB.elementFor(s.id);
        if (el) { this.hidden.push([el, el.style.visibility]); el.dataset.svg2slidesHidden = el.style.visibility || '-'; el.style.visibility = 'hidden'; }
      });

      this.hideSlidesChrome();
      this.buildDOM();
      this.render();
      this.onResize = () => {
        const c = SB.pageCTM();
        if (!c) return;
        this.dropZoomLayer();
        this.setCTM(c);
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
      if (this.zoomLabel) this.zoomLabel.textContent = Math.round(v.s * 100) + '%';
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
          .rail { position: fixed; z-index: 2; display: flex; flex-direction: column; align-items: center; gap: 2px;
                  width: 40px; padding: 6px 0; background: ${GM.surface}; border-radius: 20px; box-shadow: ${GM.elev2};
                  font: 500 11px/1 ${FONT}; color: ${GM.icon}; user-select: none;
                  transition: opacity .18s ease, transform .18s ease; transform-origin: left center; }
          .rail.idle { opacity: .45; transform: scale(.94); }
          .rail.busy { opacity: .6; pointer-events: none; }
          .btn { width: 32px; height: 32px; border-radius: 16px; display: flex; align-items: center; justify-content: center;
                 cursor: pointer; color: ${GM.icon}; }
          .btn:hover { background: ${GM.hover}; }
          .btn.on { background: ${GM.selected}; color: #1f1f1f; }
          .btn.dim { opacity: .38; pointer-events: none; }
          .btn svg { width: 20px; height: 20px; display: block; }
          .btn.done { background: ${GM.tonal}; color: ${GM.onTonal}; }
          .btn.done:hover { filter: brightness(.96); }
          .zoom { width: 36px; height: 22px; border-radius: 11px; font-size: 11px; font-variant-numeric: tabular-nums; }
          .sep { width: 20px; height: 1px; background: #c4c7c5; margin: 4px 0; }
          .tip { position: fixed; z-index: 3; pointer-events: none; background: ${GM.tooltip}; color: ${GM.onTooltip};
                 font: 500 12px/16px ${FONT}; padding: 4px 8px; border-radius: 4px; white-space: nowrap;
                 opacity: 0; transition: opacity .1s; }
          .tip.show { opacity: 1; }
          .tip .k { opacity: .7; margin-left: 6px; }
          .hint { position: fixed; z-index: 2; pointer-events: none; background: ${GM.tooltip}; color: ${GM.onTooltip};
                  font: 400 12px/16px ${FONT}; padding: 6px 10px; border-radius: 4px; white-space: nowrap;
                  opacity: 0; transition: opacity .25s; }
          .hint.show { opacity: .94; }
          .btn.hide { display: none; }
          .corners { position: fixed; z-index: 2; display: none; align-items: center; gap: 8px; height: 40px; padding: 0 12px 0 14px;
                     background: ${GM.surface}; border-radius: 20px; box-shadow: ${GM.elev2}; color: #1f1f1f;
                     font: 500 12px/1 ${FONT}; user-select: none; white-space: nowrap; }
          .corners.show { display: flex; }
          .corners .cl { color: ${GM.icon}; }
          .corners input[type=range] { width: 120px; accent-color: ${ACCENT}; margin: 0; cursor: pointer; }
          .corners input[type=number] { width: 52px; height: 26px; box-sizing: border-box; border: 1px solid #c4c7c5; border-radius: 6px;
                     background: #fff; font: 500 12px/1 ${FONT}; color: #1f1f1f; padding: 0 4px 0 8px; text-align: right; }
          .corners input[type=number]:focus { outline: 2px solid ${ACCENT}; outline-offset: -1px; border-color: transparent; }
          .corners .u { color: ${GM.icon}; margin-left: -4px; }
          .corners .sc { color: ${GM.icon}; font-weight: 400; padding-left: 8px; border-left: 1px solid #c4c7c5; }
          .anchors, .handles { filter: drop-shadow(0 0 1px rgba(0,0,0,.35)) drop-shadow(0 1px 2px rgba(0,0,0,.18)); }`));

      const svg = sv('svg', { class: 'stage' });
      ['fills', 'outlines', 'handles', 'anchors'].forEach((c) => svg.append(sv('g', { class: c })));
      svg.append(
        sv('rect', { class: 'marquee', fill: 'rgba(11,87,208,.08)', stroke: ACCENT, 'stroke-width': 1, visibility: 'hidden' }),
        sv('circle', { class: 'pen-ghost', r: 4, fill: ACCENT, visibility: 'hidden' })
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
      const b = (attrs, child) => el('div', Object.assign({ class: 'btn', role: 'button' }, attrs), child);
      const zoomLabel = el('div', { class: 'btn zoom', role: 'button', 'data-act': 'zoomreset', 'data-tip': 'Fit / reset zoom', 'data-key': '⇧1 · ⌘0' }, '100%');
      this.zoomLabel = zoomLabel;
      const rail = el('div', { class: 'rail' },
        b({ 'data-tool': 'direct', 'data-tip': 'Select points', 'data-key': 'A' }, I.select),
        b({ 'data-tool': 'pen', 'data-tip': 'Add / remove points', 'data-key': 'P' }, I.pen),
        b({ 'data-act': 'corners', class: 'btn hide', 'data-tip': 'Round corners' }, I.corners),
        el('div', { class: 'sep' }),
        b({ 'data-act': 'undo', 'data-tip': 'Undo', 'data-key': '⌘Z' }, I.undo),
        b({ 'data-act': 'redo', 'data-tip': 'Redo', 'data-key': '⇧⌘Z' }, I.redo),
        el('div', { class: 'sep' }),
        b({ 'data-act': 'zoomin', 'data-tip': 'Zoom in', 'data-key': '⌘+' }, I.plus),
        zoomLabel,
        b({ 'data-act': 'zoomout', 'data-tip': 'Zoom out', 'data-key': '⌘−' }, I.minus),
        el('div', { class: 'sep' }),
        b({ 'data-act': 'cancel', 'data-tip': 'Discard changes' }, I.close),
        b({ 'data-act': 'done', class: 'btn done', 'data-tip': 'Done', 'data-key': '↵' }, I.done)
      );
      const tip = el('div', { class: 'tip' });
      const hint = el('div', { class: 'hint' });
      // Corner radius: drag the slider or type a value. Rounds every corner,
      // or only the selected points when some are selected.
      const cRange = el('input', { type: 'range', min: '0', max: '100', step: '1', value: '0', 'aria-label': 'Corner radius' });
      const cNum = el('input', { type: 'number', min: '0', step: '1', value: '0', 'aria-label': 'Corner radius in px' });
      const cScope = el('span', { class: 'sc' }, 'All corners');
      const corners = el('div', { class: 'corners', role: 'group', 'aria-label': 'Round corners' },
        el('span', { class: 'cl' }, 'Corners'), cRange, cNum, el('span', { class: 'u' }, 'px'), cScope);
      root.append(svg, rail, corners, tip, hint);
      this.cornersPanel = corners;
      this.cornerRange = cRange;
      this.cornerNum = cNum;
      this.cornerScopeEl = cScope;
      this.cornerOpen = true;
      corners.addEventListener('pointerdown', (e) => { e.stopPropagation(); this.hideHint(); });
      cRange.addEventListener('input', () => this.setRound(Number(cRange.value), false));
      cNum.addEventListener('input', () => {
        const v = parseFloat(cNum.value);
        if (Number.isFinite(v) && v >= 0) this.setRound(v, true);
      });

      this.root = root;
      this.svg = svg;
      this.gFills = svg.querySelector('.fills');
      this.gOutlines = svg.querySelector('.outlines');
      this.gHandles = svg.querySelector('.handles');
      this.gAnchors = svg.querySelector('.anchors');
      this.marquee = svg.querySelector('.marquee');
      this.penGhost = svg.querySelector('.pen-ghost');
      this.rail = rail;
      this.tip = tip;
      this.hint = hint;

      rail.addEventListener('pointerdown', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.hideTip();
        const t = e.target.closest('.btn');
        if (!t) return;
        if (t.dataset.tool) this.setTool(t.dataset.tool);
        else if (t.dataset.act === 'undo') this.doUndo();
        else if (t.dataset.act === 'redo') this.doRedo();
        else if (t.dataset.act === 'zoomin') this.zoomStep(1.5);
        else if (t.dataset.act === 'zoomout') this.zoomStep(1 / 1.5);
        else if (t.dataset.act === 'zoomreset') { if (this.isIdentityView()) this.fitView(); else this.resetView(); }
        else if (t.dataset.act === 'corners') { this.cornerOpen = !this.cornerOpen; this.render(); }
        else if (t.dataset.act === 'cancel') this.close(true);
        else if (t.dataset.act === 'done') this.commit();
      });
      // Tooltips, Slides-style: dark chip to the right of the button.
      rail.addEventListener('pointerover', (e) => {
        const t = e.target.closest('[data-tip]');
        if (!t) return;
        clearTimeout(this._tipT);
        this._tipT = setTimeout(() => this.showTip(t), 350);
      });
      rail.addEventListener('pointerout', (e) => {
        // Leaving a button hides its tip unless the pointer went straight
        // onto another button (that one's tip takes over).
        const to = e.relatedTarget && e.relatedTarget.closest ? e.relatedTarget.closest('[data-tip]') : null;
        if (!to || !rail.contains(to)) this.hideTip();
      });
      rail.addEventListener('pointerdown', () => this.hideTip(), true);
      // Fade back when not in use.
      rail.addEventListener('pointerenter', () => { clearTimeout(this._idleT); rail.classList.remove('idle'); });
      rail.addEventListener('pointerleave', () => { this.scheduleIdle(600); });
      this.scheduleIdle(2500);

      svg.addEventListener('pointerdown', (e) => { this.hideHint(); this.endRound(); this.onDown(e); });
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
      const r = this.wsRect;
      const h = this.rail.offsetHeight || 380;
      this.rail.style.left = (r.left + 12) + 'px';
      this.rail.style.top = Math.max(r.top + 12, Math.min(r.top + 56, r.bottom - h - 12)) + 'px';
    }

    scheduleIdle(ms) {
      clearTimeout(this._idleT);
      this._idleT = setTimeout(() => { if (this.rail) this.rail.classList.add('idle'); }, ms);
    }

    showTip(t) {
      const rr = t.getBoundingClientRect();
      this.tip.replaceChildren(t.dataset.tip, ...(t.dataset.key ? [el('span', { class: 'k' }, t.dataset.key)] : []));
      this.tip.style.left = (this.rail.getBoundingClientRect().right + 8) + 'px';
      this.tip.style.top = (rr.top + rr.height / 2 - 12) + 'px';
      this.tip.classList.add('show');
    }
    hideTip() {
      clearTimeout(this._tipT);
      if (this.tip) this.tip.classList.remove('show');
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
      this.endRound();
      const changed = this.tool !== t;
      this.tool = t;
      this.root.querySelectorAll('[data-tool]').forEach((b) => b.classList.toggle('on', b.dataset.tool === t));
      this.svg.classList.toggle('pen', t === 'pen');
      this.penGhost.setAttribute('visibility', 'hidden');
      if (changed && t === 'pen') this.flashHint('Click a segment to add a point · click a point to remove it · ⌥-click to convert', 3000);
    }

    updateUndoButtons() {
      this.root.querySelector('[data-act="undo"]').classList.toggle('dim', !this.undo.length);
      this.root.querySelector('[data-act="redo"]').classList.toggle('dim', !this.redo.length);
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

    snapshot() { return JSON.stringify(this.shapes.map((s) => s.subs)); }
    pushUndo() {
      this.undo.push(this.snapshot());
      if (this.undo.length > 200) this.undo.shift();
      this.redo = [];
      this.dirty = true;
      this.updateUndoButtons();
    }
    restore(snap) {
      const all = JSON.parse(snap);
      this.shapes.forEach((s, i) => { s.subs = all[i]; });
      this.sel.clear();
      this.render();
    }
    doUndo() {
      this.endRound();
      if (!this.undo.length) return;
      this.redo.push(this.snapshot());
      this.restore(this.undo.pop());
      this.updateUndoButtons();
    }
    doRedo() {
      this.endRound();
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
      this.shapes.forEach((s, si) => {
        const d = SB.svgPathD(s.subs, s.M);
        const f = sv('path', { 'data-si': si, d, fill: s.filled ? s.fill : 'none', 'fill-rule': 'nonzero' });
        if (!s.filled) f.setAttribute('stroke', s.fill);
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

      this.gFills.replaceChildren(...fills);
      this.gOutlines.replaceChildren(...outlines);
      this.gHandles.replaceChildren(...handles);
      this.gAnchors.replaceChildren(...anchors);
      if (!this.drag) this.updateCornerUI();
    }

    // ── Corner rounding ──
    // Works in page units so the radius means the same thing at any zoom;
    // 381 page units = 1 px at Slides' 100%. A corner is a point with no
    // handles between two straight segments. Rounding replaces it with two
    // points joined by a cubic that approximates a circular arc: for a turn
    // of φ, the tangent points sit R·tan(φ/2) from the corner and each
    // handle is (4/3)·tan(φ/4)·R long. Each corner is capped at half its
    // shorter side. A session keeps the unrounded geometry, so dragging the
    // slider back to 0 restores it exactly.
    roundableCorners(subsList, keys) {
      const out = [];
      subsList.forEach((subs, si) => {
        const T = this.shapes[si].toPage;
        subs.forEach((sp, pi) => {
          const L = sp.nodes.length;
          if (L < 3) return;
          sp.nodes.forEach((n, ni) => {
            if (keys && !keys.has(this.key(si, pi, ni))) return;
            if (n.in || n.out) return;
            const pI = ni > 0 ? ni - 1 : (sp.closed ? L - 1 : -1);
            const nI = ni < L - 1 ? ni + 1 : (sp.closed ? 0 : -1);
            if (pI < 0 || nI < 0) return;
            const pp = sp.nodes[pI], nn = sp.nodes[nI];
            if (pp.out || nn.in) return;
            const P = SB.apply(T, n.x, n.y), A = SB.apply(T, pp.x, pp.y), B = SB.apply(T, nn.x, nn.y);
            const l1 = Math.hypot(P.x - A.x, P.y - A.y), l2 = Math.hypot(B.x - P.x, B.y - P.y);
            if (l1 < 1e-6 || l2 < 1e-6) return;
            const u1 = { x: (P.x - A.x) / l1, y: (P.y - A.y) / l1 };
            const u2 = { x: (B.x - P.x) / l2, y: (B.y - P.y) / l2 };
            const phi = Math.acos(Math.max(-1, Math.min(1, u1.x * u2.x + u1.y * u2.y)));
            if (phi < 0.05 || phi > Math.PI - 0.05) return;
            out.push({ si, pi, ni, P, u1, u2, phi, rmax: (Math.min(l1, l2) / 2) / Math.tan(phi / 2) });
          });
        });
      });
      return out;
    }

    // Which corners the control would act on right now.
    cornerScope() {
      if (this.round) return { corners: this.round.corners, scoped: this.round.scoped };
      let total = 0;
      this.eachNode(() => { total++; });
      if (total > 160) return null; // complex artwork: leave it alone
      const subsList = this.shapes.map((sh) => sh.subs);
      const all = this.roundableCorners(subsList, null);
      const sel = this.sel.size ? all.filter((c) => this.sel.has(this.key(c.si, c.pi, c.ni))) : [];
      if (sel.length) return { corners: sel, scoped: true };
      if (all.length >= 3) return { corners: all, scoped: false };
      return null;
    }

    beginRound() {
      const sc = this.cornerScope();
      if (!sc || !sc.corners.length) return false;
      this.pushUndo();
      this.round = { base: this.snapshot(), corners: sc.corners, scoped: sc.scoped, value: 0 };
      this.sel.clear(); // point indices shift as corners split in two
      return true;
    }

    endRound() {
      if (!this.round) return;
      this.round = null;
      if (this.cornerRange) { this.cornerRange.value = '0'; this.cornerNum.value = '0'; }
    }

    setRound(px, fromNumber) {
      if (!this.round && !this.beginRound()) return;
      const r = this.round;
      r.value = Math.max(0, px);
      const R = r.value * 381;
      const byKey = new Map(r.corners.map((c) => [this.key(c.si, c.pi, c.ni), c]));
      const subsList = JSON.parse(r.base);
      subsList.forEach((subs, si) => {
        const inv = SB.matInv(this.shapes[si].toPage);
        const loc = (p) => SB.apply(inv, p.x, p.y);
        subs.forEach((sp, pi) => {
          const nodes = [];
          sp.nodes.forEach((n, ni) => {
            const c = byKey.get(this.key(si, pi, ni));
            const Re = c ? Math.min(R, c.rmax) : 0;
            if (!c || Re <= 0) { nodes.push(n); return; }
            const d = Re * Math.tan(c.phi / 2);
            const h = (4 / 3) * Math.tan(c.phi / 4) * Re;
            const a = { x: c.P.x - c.u1.x * d, y: c.P.y - c.u1.y * d };
            const b = { x: c.P.x + c.u2.x * d, y: c.P.y + c.u2.y * d };
            nodes.push(
              Object.assign(loc(a), { in: null, out: loc({ x: a.x + c.u1.x * h, y: a.y + c.u1.y * h }), smooth: false }),
              Object.assign(loc(b), { in: loc({ x: b.x - c.u2.x * h, y: b.y - c.u2.y * h }), out: null, smooth: false })
            );
          });
          sp.nodes = nodes;
        });
      });
      subsList.forEach((subs, si) => { this.shapes[si].subs = subs; });
      this.dirty = true;
      if (fromNumber) this.cornerRange.value = String(Math.min(r.value, Number(this.cornerRange.max)));
      else this.cornerNum.value = String(Math.round(r.value));
      this.render();
    }

    updateCornerUI() {
      const btn = this.root.querySelector('[data-act="corners"]');
      const sc = this.cornerScope();
      btn.classList.toggle('hide', !sc);
      btn.classList.toggle('on', !!sc && this.cornerOpen);
      const show = !!sc && this.cornerOpen;
      this.cornersPanel.classList.toggle('show', show);
      if (!show) return;
      const maxPx = Math.max(1, Math.ceil(Math.max(...sc.corners.map((c) => c.rmax)) / 381));
      this.cornerRange.max = String(Math.min(maxPx, 999));
      this.cornerScopeEl.textContent = sc.scoped
        ? (sc.corners.length === 1 ? '1 corner' : sc.corners.length + ' corners')
        : 'All corners';
      const br = btn.getBoundingClientRect(), rr = this.rail.getBoundingClientRect();
      this.cornersPanel.style.left = (rr.right + 8) + 'px';
      this.cornersPanel.style.top = (br.top + br.height / 2 - 20) + 'px';
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
      const paths = this.gFills.querySelectorAll('path');
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

      if (this.tool === 'pen') {
        const nk = this.hitNode(x, y);
        if (nk) {
          this.pushUndo();
          if (e.altKey) this.toggleSmooth(nk);
          else this.deleteNodes(new Set([nk]));
          this.render();
          return;
        }
        const seg = this.hitSegment(x, y);
        if (seg) {
          this.pushUndo();
          const k = this.splitSegment(seg);
          this.sel = new Set([k]);
          this.render();
        }
        return;
      }

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
        this.startNodeDrag(x, y);
        this.render();
        return;
      }
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

    startNodeDrag(x, y) {
      const orig = new Map();
      this.sel.forEach((k) => { const h = this.nodeAt(k); if (h) orig.set(k, clone({ x: h.n.x, y: h.n.y, in: h.n.in, out: h.n.out })); });
      this.drag = { kind: 'nodes', start: { x, y }, orig, pushed: false };
    }

    onMove(e) {
      const x = e.clientX, y = e.clientY;
      if (!this.drag) {
        if (this.tool === 'pen') {
          const seg = !this.hitNode(x, y) && this.hitSegment(x, y);
          if (seg) { this.penGhost.setAttribute('cx', seg.x); this.penGhost.setAttribute('cy', seg.y); this.penGhost.setAttribute('visibility', 'visible'); }
          else this.penGhost.setAttribute('visibility', 'hidden');
        }
        return;
      }
      e.preventDefault();
      let dx = x - this.drag.start.x, dy = y - this.drag.start.y;
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
      if (e.shiftKey && this.drag.kind === 'nodes') { const s = snap45(dx, dy); dx = s.x; dy = s.y; }

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
      this.drag = null;
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

    // ── Commit / close ──
    buildResolved() {
      const idMap = new Map();
      this.resolved.forEach((e) => { if ((e[0] === 2 || e[0] === 3) && typeof e[1] === 'string') idMap.set(e[1], SB.newId()); });
      const byId = new Map(this.shapes.map((s) => [s.id, s]));
      const dropped = new Set();
      const out = [];

      for (const e of this.resolved) {
        if (e[0] === 3 && byId.has(e[1])) {
          const s = byId.get(e[1]);
          const subs = clone(s.subs);
          if (!subs.some((sp) => sp.nodes.length >= 2)) { dropped.add(e[1]); continue; }
          const norm = SB.normalizeSubs(subs);
          const { meta, coords } = SB.encodePath(subs);
          const m = e[3];
          const newM = [m[0], m[1], m[2], m[3], m[4] + m[0] * norm.dx + m[2] * norm.dy, m[5] + m[1] * norm.dx + m[3] * norm.dy];
          const props = clone(e[4]);
          const rec = clone(SB.pathRecord(e));
          rec[2] = meta;
          rec[3] = coords;
          SB.setProp(props, 12, [rec]);
          SB.setProp(props, 8, norm.w);
          SB.setProp(props, 9, norm.h);
          out.push([3, idMap.get(e[1]), SB.typeFor(e[2], subs), newM, props, ...clone(e.slice(5))]);
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
      // A group left with one child: ungroup it.
      return out.filter((e) => !(e[0] === 2 && e[2].length < 2));
    }

    onKeyUp(e) {
      if (e.key === ' ') {
        e.preventDefault();
        this.spaceDown = false;
        if (!this.drag) this.setPanCursor('');
      }
    }

    teardown(restoreOriginals = true) {
      cancelAnimationFrame(this._raf);
      if (this.zoomLayer) this.zoomLayer.remove();
      this.zoomLayer = null;
      window.removeEventListener('pointermove', this._mv, true);
      window.removeEventListener('pointerup', this._up, true);
      window.removeEventListener('resize', this.onResize);
      if (restoreOriginals) this.restoreOriginals();
      this.restoreSlidesChrome();
      this.host.remove();
      editor = null;
    }

    restoreOriginals() {
      this.hidden.forEach(([el, v]) => { el.style.visibility = v || ''; delete el.dataset.svg2slidesHidden; });
    }

    close(cancel = false) {
      const original = cancel ? this.restoreOnCancel : null;
      this.teardown();
      SB.focusTextbox();
      // Cancel after a conversion: swap the original object back in.
      if (original) {
        const ids = this.shapes.map((sh) => sh.id);
        deleteSelected(ids).then((ok) => { if (ok) SB.paste(original); });
      }
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
      const promptAt = this.rail.getBoundingClientRect();
      const nShapes = resolved.filter((e) => e[0] === 3).length;
      const sig = resolved.filter((e) => e[0] === 3).map((e) => SB.getProp(e[4], 8) + 'x' + SB.getProp(e[4], 9)).sort().join(',');
      const oldIds = this.shapes.map((s) => s.id);

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
      if (!(await deleteSelected(oldIds))) {
        console.warn('[svg2slides] scripted delete did not remove the original');
        this.teardown(true);
        showCommitPrompt(promptAt, copied ? 'Delete the original, then ' + pasteLabel() + ' to commit changes' : 'Could not apply changes');
        return;
      }
      let ok = true;
      if (nShapes) {
        SB.paste(resolved);
        ok = !!(await SB.waitForSelection((sel) => {
          const shapes = sel.filter((e) => e[0] === 3);
          if (shapes.length !== nShapes) return false;
          return shapes.map((e) => SB.getProp(e[4], 8) + 'x' + SB.getProp(e[4], 9)).sort().join(',') === sig;
        }));
      }
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
