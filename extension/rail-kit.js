// Loaded after slides-bridge.js, before svg-editor.js and shape-tools.js.
//
// One toolbar, two modes. The Shape tools rail (shape-tools.js) and the
// Edit Shape rail (svg-editor.js) are built from these parts so they share
// a spot, a size, a grid and the same buttons in the same places: a two-
// column rail (like Illustrator's tool panel) in Slides' own GM3 colours,
// with flyouts for the groups of commands and a colour popover.
//
// Everything is built with DOM calls (Slides enforces Trusted Types).

console.log('[svg2slides] rail-kit.js loaded');

const RK = (() => {
  const ACCENT = '#0b57d0';
  const FONT = "'Google Sans', Roboto, Arial, sans-serif";
  const GM = {
    surface: '#f0f4f9', icon: '#444746', hover: 'rgba(68,71,70,.08)', selected: '#d3e3fd',
    tonal: '#c2e7ff', onTonal: '#004a77', tooltip: '#303030', onTooltip: '#f2f2f2', outline: '#c4c7c5',
    elev1: '0 1px 2px rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15)',
    elev2: '0 1px 2px rgba(60,64,67,.3), 0 2px 6px 2px rgba(60,64,67,.15)',
  };
  const SVGNS = 'http://www.w3.org/2000/svg';
  const L = (a) => (SB.SHORTCUT_LABEL && SB.SHORTCUT_LABEL[a]) || '';

  function el(tag, attrs = {}, ...kids) {
    const e = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => { if (v !== undefined && v !== null) e.setAttribute(k, v); });
    kids.forEach((c) => e.append(c));
    return e;
  }
  function sv(tag, attrs = {}) {
    const e = document.createElementNS(SVGNS, tag);
    Object.entries(attrs).forEach(([k, v]) => { if (v != null) e.setAttribute(k, v); });
    return e;
  }

  // ── Icons: 20px grid. Undo/redo/plus/minus are Slides' own glyphs. ──────
  const RING = (d, w = '1.5') => [d, { fill: 'none', stroke: 'currentColor', 'stroke-width': w }];
  const BAR = '__bar__'; // a colour bar under the glyph (fill / stroke buttons)
  const P = {
    select: [['M5.5 2.5v13.3l3.4-3.2 2.3 5 1.9-.9-2.3-4.9h4.6Z']],
    maskAdjust: [RING('M10 3.25a6.75 6.75 0 1 1 0 13.5 6.75 6.75 0 0 1 0-13.5Z'), ['M10 5.2 12.1 7.6H10.75V9.25H12.4V7.9L14.8 10 12.4 12.1V10.75H10.75V12.4H12.1L10 14.8 7.9 12.4H9.25V10.75H7.6V12.1L5.2 10 7.6 7.9V9.25H9.25V7.6H7.9Z']],
    mask: [RING('M10 3.25a6.75 6.75 0 1 1 0 13.5 6.75 6.75 0 0 1 0-13.5Z'), ['M4.6 13.6 8 9.4l2.4 2.9 1.9-1.9 3.1 3.2a6 6 0 0 1-10.8 0Z'], ['M12.6 6a1.3 1.3 0 1 1 0 2.6 1.3 1.3 0 0 1 0-2.6Z']],
    snap: [['M4 3h4.5v7a1.5 1.5 0 0 0 3 0V3H16v7a6 6 0 0 1-12 0Zm1.5 1.5V6h1.5V4.5Zm7.5 0V6h1.5V4.5Z', { 'fill-rule': 'evenodd' }]],
    snapPoints: [RING('M10 6.25a3.75 3.75 0 1 1 0 7.5 3.75 3.75 0 0 1 0-7.5Z'), ['M9.25 1.5h1.5v4h-1.5Zm0 13h1.5v4h-1.5ZM1.5 9.25h4v1.5h-4Zm13 0h4v1.5h-4Z']],
    snapPx: [['M3 3h6v6H3Zm8 8h6v6h-6Z'], RING('M11.75 3.75h4.5v4.5h-4.5Zm-8 8h4.5v4.5h-4.5Z', '1.2')],
    snapGrid: [RING('M3.75 3.75h12.5v12.5H3.75Z'), ['M7.4 3h1.2v14H7.4Zm4 0h1.2v14h-1.2ZM3 7.4h14v1.2H3Zm0 4h14v1.2H3Z']],
    pen: [['M10 2l5.5 7.5-3 6h-5l-3-6Zm0 6.2a1.6 1.6 0 1 0 0 3.2 1.6 1.6 0 0 0 0-3.2ZM7.5 16.75h5V18.25h-5Z', { 'fill-rule': 'evenodd' }]],
    edit: [RING('M4.6 15.4C6 10 9.5 6.6 15.4 4.6'), ['M2.5 13.5h4v4h-4Zm11-11h4v4h-4Z']],
    dropper: [['M14.9 3.3a2 2 0 0 1 1.8 3.2l-2 2 .7.7-1.1 1.1-.7-.7-5.2 5.2-2.9.7-.9.9-1-1 .9-.9.7-2.9 5.2-5.2-.7-.7 1.1-1.1.7.7 2-2a2 2 0 0 1 1.4-.6ZM11.5 8.9 6.6 13.8l-.4 1.4 1.4-.4 4.9-4.9Z']],
    layers: [['M10 16.3 3.9 11.5 2.6 12.5 10 18.3l7.4-5.8-1.3-1ZM10 14l7.4-5.8L10 2.4 2.6 8.2Z']],
    arrange: [['M3 3h9v4H7v5H3Z'], RING('M7.75 7.75h8.5v8.5h-8.5Z')],
    forward: [['M10 3.5 5.5 8h3v5h3V8h3Z'], ['M4 15h12v1.5H4Z']],
    backward: [['M10 16.5 14.5 12h-3V7h-3v5h-3Z'], ['M4 3.5h12V5H4Z']],
    front: [['M10 2 5.5 6.5h3v4h3v-4h3Z'], ['M4 12.5h12V14H4Zm0 3h12V17H4Z']],
    back: [['M10 18l4.5-4.5h-3v-4h-3v4h-3Z'], ['M4 3h12v1.5H4Zm0 3h12v1.5H4Z']],
    transform: [['M10 3.5a6.5 6.5 0 1 0 6.5 6.5H15a5 5 0 1 1-5-5v2.3l3.2-3-3.2-3Z']],
    rotL: [['M10 3.5a6.5 6.5 0 1 1-6.5 6.5H5a5 5 0 1 0 5-5v2.3l-3.2-3 3.2-3Z']],
    rotR: [['M10 3.5a6.5 6.5 0 1 0 6.5 6.5H15a5 5 0 1 1-5-5v2.3l3.2-3-3.2-3Z']],
    scaleUp: [['M3 3h5.5v1.5H5.6l3.6 3.6-1.1 1.1-3.6-3.6v2.9H3Zm14 14h-5.5v-1.5h2.9l-3.6-3.6 1.1-1.1 3.6 3.6v-2.9H17Z']],
    scaleDown: [['M9 9H3.5V7.5h2.9L2.8 3.9l1.1-1.1 3.6 3.6V3.5H9Zm2 2h5.5v1.5h-2.9l3.6 3.6-1.1 1.1-3.6-3.6v2.9H11Z']],
    combine: [['M3 3h9v5h5v9H8v-5H3Z']],
    union: [['M3 3h9v5h5v9H8v-5H3Z']],
    subtract: [['M3 3h9v5H8v4H3Z'], RING('M8.75 8.75h7.5v7.5h-7.5Z')],
    intersect: [RING('M3.75 3.75h7.5v7.5h-7.5Z'), RING('M8.75 8.75h7.5v7.5h-7.5Z'), ['M8 8h4v4H8Z']],
    exclude: [['M3 3h9v5H8v4H3Zm9 5h5v9H8v-5h4Z']],
    group: [['M2 2h3v1.5H3.5V5H2Zm13 0h3v3h-1.5V3.5H15ZM2 15h1.5v1.5H5V18H2Zm14.5 0H18v3h-3v-1.5h1.5ZM6 6h5v5H6Zm3 3h5v5H9Z', { 'fill-rule': 'evenodd' }]],
    ungroup: [['M3 3h6v6H3Zm8 8h6v6h-6Z']],
    outline: [['M3 3h14v14H3Zm1.5 1.5v11h11v-11Zm2 2h7v7h-7Zm1.5 1.5v4h4V8Z', { 'fill-rule': 'evenodd' }]],
    outlineStroke: [['M3 3h14v14H3Zm1.5 1.5v11h11v-11Zm2 2h7v7h-7Zm1.5 1.5v4h4V8Z', { 'fill-rule': 'evenodd' }]],
    outlineText: [['M4 3h12v4h-1.5V4.5h-3.75v11H13V17H7v-1.5h2.25v-11H5.5V7H4Z', { fill: 'none', stroke: 'currentColor', 'stroke-width': '1.2', 'stroke-linejoin': 'round' }]],
    fill: [['M7.2 1.6 6.1 2.7l1.8 1.8L3.2 9.2a1 1 0 0 0 0 1.4l3.3 3.3a1 1 0 0 0 1.4 0l4.7-4.7Zm.7 4.4 3 3H4.9Zm7.3 3.6s-1.5 1.7-1.5 2.7a1.5 1.5 0 0 0 3 0c0-1-1.5-2.7-1.5-2.7Z'], BAR],
    stroke: [['M3 11.6V14h2.4l7-7-2.4-2.4Zm11.2-6.4a.65.65 0 0 0 0-.9l-1.5-1.5a.65.65 0 0 0-.9 0l-1.1 1.1 2.4 2.4Z'], BAR],
    strokeColor: [['M3 11.6V14h2.4l7-7-2.4-2.4Zm11.2-6.4a.65.65 0 0 0 0-.9l-1.5-1.5a.65.65 0 0 0-.9 0l-1.1 1.1 2.4 2.4Z'], BAR],
    strokeToggle: [['M3 3h14v14H3Zm1.5 1.5v11h11v-11Z', { 'fill-rule': 'evenodd' }], ['M4.5 16.6 3.4 15.5 15.5 3.4l1.1 1.1Z']],
    strokeThinner: [['M3 5h10v3H3Zm0 5h10v1.5H3Zm11 3h4v1.5h-4Z']],
    strokeThicker: [['M3 5h10v3H3Zm0 5h10v1.5H3Zm12.25 1.5h1.5v1.75h1.75v1.5h-1.75v1.75h-1.5v-1.75H13.5v-1.5h1.75Z']],
    undo: [['M6 16v-1.5h6q1.042 0 1.771-.729t.729-1.771-.729-1.771-1.771-.729H6.875l1.937 1.938-1.062 1.062L4 9.75 7.75 6l1.062 1.062L6.875 9H12q1.667 0 2.833 1.167Q16 11.333 16 13t-1.167 2.833Q13.667 17 12 17Z', { transform: 'translate(0 -1)' }]],
    redo: [['M8 16q-1.667 0-2.833-1.167Q4 13.667 4 12t1.167-2.833Q6.333 8 8 8h5.125l-1.937-1.938L12.25 5 16 8.75l-3.75 3.75-1.062-1.062L13.125 9.5H8q-1.042 0-1.771.729T5.5 12t.729 1.771T8 14.5h6V16Z']],
    done: [['M8 13.6 4.4 10l-1.05 1.05L8 15.7l9-9-1.05-1.05Z']],
    close: [['M6.06 15 5 13.94 8.94 10 5 6.06 6.06 5 10 8.94 13.94 5 15 6.06 11.06 10 15 13.94 13.94 15 10 11.06Z']],
    collapse: [['M12.5 5.5 8 10l4.5 4.5 1.1-1.1L10.2 10l3.4-3.4Z']],
    expand: [['M7.5 5.5 12 10l-4.5 4.5L6.4 13.4 9.8 10 6.4 6.6Z']],
    caret: [['M7 4l6 6-6 6Z']],
    weight: [['M3 4h14v1.25H3Zm0 4h14v2.5H3Zm0 5h14V17H3Z']],
    align: [['M3 2.5h1.5v15H3Z'], ['M6 5h9v3.5H6Zm0 6.5h6V15H6Z']],
    alignLeft: [['M3 2.5h1.5v15H3Z'], ['M6 5h9v3.5H6Zm0 6.5h6V15H6Z']],
    alignHCenter: [['M9.25 2.5h1.5v15h-1.5Z'], ['M4.5 5h11v3.5h-11Zm2 6.5h7V15h-7Z']],
    alignRight: [['M15.5 2.5H17v15h-1.5Z'], ['M5 5h9v3.5H5Zm3 6.5h6V15H8Z']],
    alignTop: [['M2.5 3h15v1.5h-15Z'], ['M5 6h3.5v9H5Zm6.5 0H15v6h-3.5Z']],
    alignVMiddle: [['M2.5 9.25h15v1.5h-15Z'], ['M5 4.5h3.5v11H5Zm6.5 2H15v7h-3.5Z']],
    alignBottom: [['M2.5 15.5h15V17h-15Z'], ['M5 5h3.5v9H5Zm6.5 3H15v6h-3.5Z']],
    distH: [['M2.5 3H4v14H2.5Zm13.5 0h1.5v14H16Z'], ['M8 6h4v8H8Z']],
    distV: [['M3 2.5h14V4H3Zm0 13.5h14v1.5H3Z'], ['M6 8h8v4H6Z']],
    strokeAlign: [RING('M5.5 5.5h9v9h-9Z', '3')],
    strokeCenter: [['M4 4h12v12H4Z', { fill: 'none', stroke: 'currentColor', 'stroke-width': '1', 'stroke-dasharray': '1.5 1.5', opacity: '.6' }], RING('M4 4h12v12H4Z', '3')],
    strokeInside: [['M4 4h12v12H4Z', { fill: 'none', stroke: 'currentColor', 'stroke-width': '1', 'stroke-dasharray': '1.5 1.5', opacity: '.6' }], RING('M5.5 5.5h9v9h-9Z', '3')],
    strokeOutside: [['M5 5h10v10H5Z', { fill: 'none', stroke: 'currentColor', 'stroke-width': '1', 'stroke-dasharray': '1.5 1.5', opacity: '.6' }], RING('M3.5 3.5h13v13h-13Z', '3')],
    restoreText: [['M4 3h12v4h-1.5V4.5h-3.75v11H13V17H7v-1.5h2.25v-11H5.5V7H4Z']],
    palette: [['M3 4h14v12H3Zm1.5 1.5v9h11v-9ZM6 7.5h3v1.5H6Zm0 3h8V12H6Z', { 'fill-rule': 'evenodd' }]],
    logo: [['M2 2h16v16H2Z', { fill: '#f9ab00' }], ['M5 7.5h5.5V9H5Zm0 3.5h3.5v1.5H5Z', { fill: '#fff' }], ['M13 9h1.5v2.25h2.25v1.5H14.5V15H13v-2.25h-2.25v-1.5H13Z', { fill: '#fff' }]],
  };
  function icon(name) {
    const s = sv('svg', { viewBox: '0 0 20 20', 'aria-hidden': 'true' });
    (P[name] || []).forEach((part) => {
      if (part === BAR) { s.append(sv('rect', { class: 'bar', x: 2.5, y: 16.25, width: 15, height: 3, rx: 1, fill: 'currentColor' })); return; }
      const [d, extra] = part;
      s.append(sv('path', Object.assign({ d, fill: 'currentColor' }, extra || {})));
    });
    return s;
  }

  // ── Groups of commands shared by both rails ─────────────────────────────
  // Grouped the way Illustrator's tool panel and Figma's properties are:
  // transform, arrange, pathfinder (combine), group, outline, then paint.
  // Every command is a button of its own; on a short screen whole groups
  // fold into one flyout button each (transform first), see layout().
  const SECTIONS = [
    // Arrange and Align are pop-out menus (Illustrator's Object menu and
    // Figma's align bar), side by side.
    { id: 'place', items: [
      { act: 'arrange', tip: 'Arrange', fly: [
        { act: 'front', tip: 'Bring to front' }, { act: 'forward', tip: 'Bring forward' },
        { act: 'backward', tip: 'Send backward' }, { act: 'back', tip: 'Send to back' }] },
      { act: 'align', tip: 'Align and distribute', fly: [
        { act: 'alignLeft', tip: 'Align left' }, { act: 'alignHCenter', tip: 'Align centres horizontally' }, { act: 'alignRight', tip: 'Align right' },
        { sep: true },
        { act: 'alignTop', tip: 'Align top' }, { act: 'alignVMiddle', tip: 'Align middles vertically' }, { act: 'alignBottom', tip: 'Align bottom' },
        { sep: true },
        { act: 'distH', tip: 'Distribute horizontal spacing' }, { act: 'distV', tip: 'Distribute vertical spacing' }] }] },
    { id: 'combine', fold: { act: 'combine', tip: 'Combine' }, items: [
      { act: 'union', tip: 'Union' }, { act: 'subtract', tip: 'Subtract (top shapes cut the bottom one)' },
      { act: 'intersect', tip: 'Intersect' }, { act: 'exclude', tip: 'Exclude' }] },
    { id: 'group', items: [{ act: 'group', tip: 'Group' }, { act: 'ungroup', tip: 'Ungroup' },
      { act: 'mask', tip: 'Mask image with shape (the shape on top cuts out the picture under it)' }] },
    { id: 'outline', fold: { act: 'outline', tip: 'Outline' }, items: [{ act: 'outlineStroke', tip: 'Outline stroke' }, { act: 'outlineText', tip: 'Outline text' }] },
    { id: 'paint', items: [
      { act: 'fill', tip: 'Fill colour', key: L('fillColor') }, { act: 'stroke', icon: 'strokeColor', tip: 'Stroke colour', key: L('strokeColor') },
      { act: 'weight', field: true, icon: 'weight', unit: 'px', tip: 'Stroke weight (0 = none) · ⌥-drag to scrub', key: L('strokeThinner') + ' ' + L('strokeThicker') },
      { act: 'strokeAlign', icon: 'strokeCenter', tip: 'Stroke position', key: '', fly: [
        { act: 'strokeCenter', tip: 'Centre stroke' }, { act: 'strokeInside', tip: 'Inside stroke' }, { act: 'strokeOutside', tip: 'Outside stroke' }] },
      { act: 'strokeToggle', tip: 'Stroke on / off' }] },
  ];
  const FOLD_ORDER = ['combine', 'outline'];

  // ── CSS ─────────────────────────────────────────────────────────────────
  const CSS = `
    .rail { position: fixed; z-index: 3; display: grid; grid-template-columns: 32px 32px; gap: 2px; justify-content: center;
            width: 74px; padding: 4px 0 6px; background: ${GM.surface}; border-radius: 20px; box-shadow: ${GM.elev2};
            font: 500 11px/1 ${FONT}; color: ${GM.icon}; user-select: none; box-sizing: border-box;
            transition: opacity .15s ease; }
    .rail.busy { pointer-events: none; cursor: progress; }
    .rail.min { grid-template-columns: 32px; grid-template-rows: 32px; width: 40px; height: 40px; padding: 4px; border-radius: 50%; align-content: center; }
    .rail.min > :not(.mini):not(.keep) { display: none; }
    .rail:not(.min) > .mini { display: none; }
    .btn { width: 32px; height: 32px; border-radius: 16px; display: flex; align-items: center; justify-content: center;
           cursor: pointer; color: ${GM.icon}; position: relative; box-sizing: border-box; }
    .btn:hover { background: ${GM.hover}; }
    .btn.on { background: ${GM.selected}; color: #1f1f1f; }
    .btn.dim { opacity: .38; }
    .btn svg { width: 20px; height: 20px; display: block; }
    .btn .bar { fill: var(--sw, currentColor); stroke: rgba(0,0,0,.18); stroke-width: .5; }
    .btn.none .bar { fill: #fff; }
    .btn.hasfly::after { content: ''; position: absolute; right: 3px; bottom: 3px; border: 3px solid transparent;
           border-right-color: currentColor; border-bottom-color: currentColor; opacity: .55; }
    .btn.span { grid-column: 1 / -1; width: auto; margin: 0 4px; border-radius: 11px; height: 22px; font-size: 11px;
           font-variant-numeric: tabular-nums; }
    .btn.done { background: ${GM.tonal}; color: ${GM.onTonal}; }
    .btn.done:hover { filter: brightness(.96); }
    .sep { grid-column: 1 / -1; height: 1px; background: ${GM.outline}; margin: 3px 10px; }
    .field { grid-column: 1 / -1; display: flex; align-items: center; gap: 3px; height: 28px; margin: 0 3px; padding: 0 4px 0 5px;
             border-radius: 14px; color: ${GM.icon}; box-sizing: border-box; }
    .field:hover { background: ${GM.hover}; }
    .field svg { width: 14px; height: 14px; flex: none; }
    .field input { width: 27px; height: 22px; box-sizing: border-box; border: 0; border-radius: 4px; padding: 0 3px; margin: 0;
             background: transparent; color: #1f1f1f; font: 500 12px/1 ${FONT}; text-align: right; -moz-appearance: textfield; }
    .field input::-webkit-inner-spin-button, .field input::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
    .field input:focus { outline: 1.5px solid ${ACCENT}; background: #fff; }
    .field input::placeholder { color: #8a8d8c; }
    .field .u { font: 400 11px/1 ${FONT}; opacity: .75; }
    .field.dim { opacity: .38; }
    .btn.logo svg, .btn.logo img { width: 22px; height: 22px; border-radius: 5px; }
    .veil { position: fixed; inset: 0; z-index: 2147483600; background: rgba(32,33,36,.12); }
    .pal { position: fixed; z-index: 2147483601; width: 440px; display: flex; flex-direction: column; background: #fff; border-radius: 12px;
           box-shadow: 0 4px 8px 3px rgba(60,64,67,.15), 0 1px 3px rgba(60,64,67,.3); font: 400 13px/1 ${FONT}; color: #1f1f1f; overflow: hidden; }
    .pal .ph { display: flex; align-items: center; gap: 10px; height: 48px; padding: 0 14px; border-bottom: 1px solid #e3e3e3; color: ${GM.icon}; flex: none; }
    .pal .ph svg { width: 20px; height: 20px; flex: none; }
    .pal .ph input { flex: 1; min-width: 0; border: 0; outline: none; font: 400 15px/1 ${FONT}; color: #1f1f1f; background: transparent; }
    .pal .k { color: #5e5e5e; font: 500 12px/1 ${FONT}; white-space: nowrap; }
    .pal .pl { overflow-y: auto; padding: 6px 0; flex: 1; }
    .pal .pg { padding: 10px 16px 4px; color: #5e5e5e; font: 500 11px/1 ${FONT}; text-transform: uppercase; letter-spacing: .04em; }
    .pal .pi { display: flex; align-items: center; gap: 10px; height: 32px; padding: 0 16px; cursor: default; }
    .pal .pi.cur { background: ${GM.selected}; }
    .pal .pi.off { opacity: .45; }
    .pal .pic { width: 18px; height: 18px; color: ${GM.icon}; flex: none; }
    .pal .pic svg { width: 18px; height: 18px; display: block; }
    .pal .pt { flex: 1; }
    .pal .pe { padding: 16px; color: #5e5e5e; }
    .pal .pf { padding: 8px 16px; border-top: 1px solid #e3e3e3; color: #5e5e5e; font: 400 11px/1 ${FONT}; flex: none; }
    .fly { position: fixed; z-index: 4; display: none; align-items: center; gap: 2px; height: 40px; padding: 0 4px;
           background: ${GM.surface}; border-radius: 20px; box-shadow: ${GM.elev2}; user-select: none; }
    .fly.show { display: flex; }
    .fly .fsep { width: 1px; height: 20px; background: ${GM.outline}; margin: 0 3px; }
    .tip { position: fixed; z-index: 6; pointer-events: none; background: ${GM.tooltip}; color: ${GM.onTooltip};
           font: 500 12px/16px ${FONT}; padding: 4px 8px; border-radius: 4px; white-space: nowrap; opacity: 0; transition: opacity .1s; }
    .tip.show { opacity: 1; }
    .tip .k { opacity: .7; margin-left: 6px; }
    .pop { position: fixed; z-index: 5; display: none; width: 236px; box-sizing: border-box; padding: 10px 10px 8px;
           background: #fff; border-radius: 12px; box-shadow: ${GM.elev2}; font: 400 12px/1 ${FONT}; color: #1f1f1f; user-select: none; }
    .pop.show { display: block; }
    .pop .ttl { font: 500 12px/16px ${FONT}; color: #444746; margin: 0 2px 8px; display: flex; justify-content: space-between; }
    .pop .ttl .k { font-weight: 400; opacity: .7; }
    .pop .grid { display: grid; grid-template-columns: repeat(10, 18px); gap: 4px; margin-bottom: 8px; }
    .pop .sw { width: 18px; height: 18px; border-radius: 9px; box-sizing: border-box; border: 1px solid rgba(0,0,0,.12); cursor: pointer; }
    .pop .sw:hover { transform: scale(1.12); }
    .pop .sw.cur { outline: 2px solid ${ACCENT}; outline-offset: 1px; }
    .pop .sw.no { background: #fff; position: relative; overflow: hidden; }
    .pop .sw.no::after { content: ''; position: absolute; left: 50%; top: -3px; bottom: -3px; width: 1.5px; background: #d93025; transform: rotate(45deg); }
    .pop .lab { color: #5e5e5e; margin: 2px 2px 6px; }
    .pop .row { display: flex; align-items: center; gap: 6px; margin-top: 2px; }
    .pop input { flex: 1; min-width: 0; height: 26px; box-sizing: border-box; border: 1px solid #c4c7c5; border-radius: 6px;
           padding: 0 8px; font: 400 12px/1 ${FONT}; color: #1f1f1f; outline: none; text-transform: uppercase; }
    .pop input:focus { border-color: ${ACCENT}; }
    .pop .chip { height: 24px; padding: 0 8px; border-radius: 12px; display: inline-flex; align-items: center; cursor: pointer;
           border: 1px solid #c4c7c5; color: #444746; font: 500 11px/1 ${FONT}; }
    .pop .chip:hover { background: ${GM.hover}; }
    .pop .chip.cur { background: ${GM.selected}; border-color: ${GM.selected}; color: #1f1f1f; }
    .pop .wts { display: flex; flex-wrap: wrap; gap: 4px; margin: 2px 0 8px; }`;

  // Slides' standard palette (same order as its colour menus).
  const PALETTE = [
    '#000000', '#434343', '#666666', '#999999', '#b7b7b7', '#cccccc', '#d9d9d9', '#efefef', '#f3f3f3', '#ffffff',
    '#980000', '#ff0000', '#ff9900', '#ffff00', '#00ff00', '#00ffff', '#4a86e8', '#0000ff', '#9900ff', '#ff00ff',
    '#e6b8af', '#f4cccc', '#fce5cd', '#fff2cc', '#d9ead3', '#d0e0e3', '#c9daf8', '#cfe2f3', '#d9d2e9', '#ead1dc',
    '#cc4125', '#e06666', '#f6b26b', '#ffd966', '#93c47d', '#76a5af', '#6d9eeb', '#6fa8dc', '#8e7cc3', '#c27ba0',
    '#85200c', '#990000', '#b45f06', '#bf9000', '#38761d', '#134f5c', '#1155cc', '#0b5394', '#351c75', '#741b47',
  ];

  // ── Rail ────────────────────────────────────────────────────────────────
  // top: items above the shared groups; bottom: items below. Items are
  // { act, tip, key, icon, node, text, span, cls, field, unit }. A field is a
  // small number box (precise values, like the corner radius pill).
  // onAct(act, info) runs commands; opts.onField(act, value, how) gets
  // field edits (how.live while typing, how.commit on Enter or leaving).
  function mountRail(root, top, bottom, onAct, opts = {}) {
    const state = { dims: new Set(), on: new Set(), swatch: new Map(), tips: new Map(), text: new Map(), icon: new Map(), field: new Map() };
    let items = new Map();
    let folded = new Set();
    let lastAvail = null;
    const rail = el('div', { class: 'rail', role: 'toolbar', 'aria-label': opts.label || 'Shape tools' });
    const fly = el('div', { class: 'fly', role: 'toolbar' });
    const tip = el('div', { class: 'tip' });
    let flyFor = null;
    const sections = [...(top || []).map((t, i) => ({ id: 'top' + i, items: t, mini: t.mini })), ...SECTIONS, ...(bottom || []).map((t, i) => ({ id: 'bottom' + i, items: t, mini: t.mini }))];

    const makeBtn = (it, inFly) => {
      if (it.field) {
        const inp = el('input', { type: 'number', min: '0', step: 'any', inputmode: 'decimal', 'aria-label': it.tip });
        const f = el('div', { class: 'field', 'data-act': it.act, 'data-tip': it.tip, 'data-key': it.key || undefined }, icon(it.icon || it.act), inp, el('span', { class: 'u' }, it.unit || ''));
        f._input = inp;
        let start = '';
        inp.addEventListener('focus', () => { start = inp.value; hideTip(); setTimeout(() => inp.select(), 0); });
        inp.addEventListener('input', () => { if (opts.onField) opts.onField(it.act, inp.value, { live: true }); });
        inp.addEventListener('keydown', (e) => {
          e.stopPropagation();
          if (e.key === 'Enter') { e.preventDefault(); inp._done = true; if (opts.onField) opts.onField(it.act, inp.value, { commit: true }); inp.blur(); }
          else if (e.key === 'Escape') { e.preventDefault(); inp._done = true; inp.value = start; if (opts.onField) opts.onField(it.act, start, { cancel: true }); inp.blur(); }
        });
        inp.addEventListener('keyup', (e) => e.stopPropagation());
        inp.addEventListener('blur', () => {
          if (!inp._done && inp.value !== start && opts.onField) opts.onField(it.act, inp.value, { commit: true });
          inp._done = false;
          if (opts.onFieldBlur) opts.onFieldBlur(it.act);
        });
        scrub(f, inp, { step: it.step || 0.1, min: 0, onEnd: (v) => { if (opts.onField) opts.onField(it.act, String(v), { commit: true }); } });
        if (state.field.has(it.act)) applyField(f, state.field.get(it.act));
        if (!inFly) items.set(it.act, { it, b: f });
        if (state.dims.has(it.act)) f.classList.add('dim');
        return f;
      }
      const key = it.key !== undefined ? it.key : L(it.act);
      const b = el('div', {
        class: 'btn' + (it.fly ? ' hasfly' : '') + (it.span ? ' span' : '') + (it.cls ? ' ' + it.cls : ''),
        role: 'button', 'data-act': it.act, 'data-tip': state.tips.has(it.act) ? state.tips.get(it.act)[0] : it.tip,
        'data-key': (state.tips.has(it.act) ? state.tips.get(it.act)[1] : key) || undefined, 'aria-label': it.tip,
      }, state.text.has(it.act) ? state.text.get(it.act) : it.text !== undefined ? it.text : it.node ? it.node.cloneNode(true) : icon(state.icon.get(it.act) || it.icon || it.act));
      if (!inFly) items.set(it.act, { it, b });
      if (state.dims.has(it.act)) b.classList.add('dim');
      if (state.on.has(it.act)) b.classList.add('on', 'stay');
      if (state.swatch.has(it.act)) { const c = state.swatch.get(it.act); b.style.setProperty('--sw', c || '#ffffff'); b.classList.toggle('none', !c); }
      return b;
    };
    function applyField(f, v) {
      const inp = f._input;
      if (!inp || (root.activeElement === inp)) return;
      inp.value = v === null || v === undefined ? '' : String(v);
      inp.placeholder = v === null ? '–' : '';
      f.title = v === null ? 'Mixed' : '';
    }

    function render() {
      closeFly();
      items = new Map();
      const kids = [];
      let prevFolded = false;
      sections.forEach((sec, i) => {
        const isFold = folded.has(sec.id) && sec.fold;
        if (i && !sec.mini && !(isFold && prevFolded)) kids.push(el('div', { class: 'sep' }));
        if (isFold) {
          kids.push(makeBtn(Object.assign({ fly: sec.items }, sec.fold)));
        } else {
          sec.items.forEach((it) => kids.push(makeBtn(it)));
        }
        prevFolded = !!isFold;
      });
      rail.replaceChildren(...kids);
    }
    // Fold groups into flyouts, in FOLD_ORDER, until the rail fits.
    function layout(maxH) {
      const want = new Set();
      folded = want;
      render();
      for (const id of FOLD_ORDER) {
        if (rail.offsetHeight <= maxH) break;
        want.add(id);
        render();
      }
    }

    // where: 'rail' (to the right of the rail), 'below', 'above', 'right'.
    function showTip(t, where) {
      const rr = t.getBoundingClientRect();
      tip.replaceChildren(t.dataset.tip || '', ...(t.dataset.key ? [el('span', { class: 'k' }, t.dataset.key)] : []));
      tip.classList.add('show');
      const w = tip.offsetWidth, h = tip.offsetHeight;
      let x, y;
      if (where === 'below' || where === true) { x = rr.left + rr.width / 2 - w / 2; y = (fly.contains(t) ? fly.getBoundingClientRect().bottom : rr.bottom) + 6; }
      else if (where === 'above') { x = rr.left + rr.width / 2 - w / 2; y = rr.top - h - 6; }
      else if (where === 'right') { x = rr.right + 8; y = rr.top + rr.height / 2 - h / 2; }
      else { x = rail.getBoundingClientRect().right + 8; y = rr.top + rr.height / 2 - 12; }
      tip.style.left = Math.max(4, Math.min(innerWidth - w - 4, x)) + 'px';
      tip.style.top = Math.max(4, Math.min(innerHeight - h - 4, y)) + 'px';
    }
    function hideTip() { clearTimeout(tip._t); tip.classList.remove('show'); }
    const hover = (host, below) => {
      host.addEventListener('pointerover', (e) => {
        const t = e.target.closest('[data-tip]');
        if (!t) return;
        clearTimeout(tip._t);
        tip._t = setTimeout(() => { if (!(flyFor && below === 'rail' && t.dataset.act === flyFor) && !(t._input && root.activeElement === t._input) && !scrubbing) showTip(t, below); }, 400);
      });
      host.addEventListener('pointerout', (e) => {
        const to = e.relatedTarget && e.relatedTarget.closest ? e.relatedTarget.closest('[data-tip]') : null;
        if (!to || !host.contains(to)) hideTip();
      });
    };
    hover(rail, 'rail');
    hover(fly, 'below');

    function openFly(act) {
      const rec = items.get(act);
      if (!rec) return;
      flyFor = act;
      fly.replaceChildren(...rec.it.fly.map((f) => (f.sep ? el('div', { class: 'fsep' }) : makeBtn(f, true))));
      items.forEach(({ b }, a) => b.classList.toggle('on', a === act || b.classList.contains('stay')));
      fly.classList.add('show');
      const br = rec.b.getBoundingClientRect();
      fly.style.left = (rail.getBoundingClientRect().right + 6) + 'px';
      fly.style.top = (br.top + br.height / 2 - 20) + 'px';
      hideTip();
    }
    function closeFly() {
      if (!flyFor) return;
      const rec = items.get(flyFor);
      if (rec && !rec.b.classList.contains('stay')) rec.b.classList.remove('on');
      flyFor = null;
      fly.classList.remove('show');
    }

    const down = (e) => {
      if (e.target.tagName === 'INPUT' || scrubbing) { e.stopPropagation(); return; } // fields take focus
      e.preventDefault();
      e.stopPropagation();
      hideTip();
      const t = e.target.closest('.btn, .field');
      if (!t || rail.classList.contains('busy')) return;
      if (t.classList.contains('field')) { t._input.focus(); t._input.select(); return; }
      const act = t.dataset.act;
      const rec = items.get(act);
      if (rec && rec.it.fly && !fly.contains(t)) {
        if (flyFor === act) closeFly(); else openFly(act);
        return;
      }
      const anchor = t.getBoundingClientRect();
      closeFly();
      onAct(act, { anchor, event: e });
    };
    rail.addEventListener('pointerdown', down);
    fly.addEventListener('pointerdown', down);
    [rail, fly].forEach((n) => n.addEventListener('mousedown', (e) => { if (e.target.tagName !== 'INPUT') e.preventDefault(); e.stopPropagation(); }));
    const outside = (e) => {
      if (!flyFor) return;
      const path = e.composedPath ? e.composedPath() : [];
      if (path.includes(fly) || path.includes(rail)) return;
      closeFly();
    };
    window.addEventListener('pointerdown', outside, true);
    rail.addEventListener('pointerenter', () => { if (opts.onEnter) opts.onEnter(); });

    render();
    root.append(rail, fly, tip);
    const each = (act, fn) => { const rec = items.get(act); if (rec) fn(rec.b); fly.querySelectorAll(`[data-act="${act}"]`).forEach(fn); };
    return {
      rail, fly, tip, hideTip, closeFly, layout,
      get items() { return items; },
      attachTips: (node, where) => hover(node, where),
      flyOpen: () => flyFor,
      scheduleIdle() {},
      destroy() { window.removeEventListener('pointerdown', outside, true); },
      // Same left and top in both modes, so the editor's rail swaps in place.
      // The closed toolbar sits exactly where the open one starts, so its
      // button and the open toolbar's first button share one spot.
      place(r) {
        const avail = Math.round(r.bottom - r.top - 24);
        const min = rail.classList.contains('min');
        if (min) rail.classList.remove('min');
        if (avail !== lastAvail) { lastAvail = avail; layout(avail); }
        const h = rail.offsetHeight; // open height, either way
        if (min) rail.classList.add('min');
        rail.style.left = (r.left + 12) + 'px';
        rail.style.top = (r.top + Math.max(12, Math.min(56, (r.bottom - r.top - h) / 2))) + 'px';
      },
      setDim(act, on) {
        if (on) state.dims.add(act); else state.dims.delete(act);
        each(act, (b) => b.classList.toggle('dim', !!on));
        if (act === 'weight') { const rec = items.get(act); if (rec && rec.b._input) rec.b._input.disabled = !!on; }
      },
      setOn(act, on) {
        if (on) state.on.add(act); else state.on.delete(act);
        each(act, (b) => { b.classList.toggle('on', !!on); b.classList.toggle('stay', !!on); });
      },
      setSwatch(act, color) {
        state.swatch.set(act, color || null);
        each(act, (b) => { b.style.setProperty('--sw', color || '#ffffff'); b.classList.toggle('none', !color); });
      },
      setField(act, v) { state.field.set(act, v); const rec = items.get(act); if (rec) applyField(rec.b, v); },
      setText(act, text) { state.text.set(act, text); each(act, (b) => { b.textContent = text; }); },
      setTip(act, text, key) { state.tips.set(act, [text, key]); each(act, (b) => { b.dataset.tip = text; if (key) b.dataset.key = key; else delete b.dataset.key; }); },
      setIcon(act, name) { state.icon.set(act, name); each(act, (b) => b.replaceChildren(icon(name))); },
    };
  }

  // ── ⌥-drag scrubbing for number fields ─────────────────────────────────
  // Hold Option (Alt) and drag left/right over a field to change its value,
  // ⇧ for ×10. The field's own input handler applies it live; onEnd gets
  // the final value.
  let scrubbing = false;
  function scrub(target, input, o = {}) {
    const step = o.step || 1;
    const setCursor = (e) => { target.style.cursor = e.altKey ? 'ew-resize' : ''; input.style.cursor = e.altKey ? 'ew-resize' : ''; };
    target.addEventListener('pointermove', (e) => { if (!scrubbing) setCursor(e); });
    target.addEventListener('pointerleave', () => { if (!scrubbing) { target.style.cursor = ''; input.style.cursor = ''; } });
    target.addEventListener('pointerdown', (e) => {
      if (!e.altKey || e.button !== 0 || input.disabled) return;
      e.preventDefault();
      e.stopPropagation();
      scrubbing = true;
      const x0 = e.clientX;
      const v0 = parseFloat(input.value) || 0;
      let last = v0;
      if (o.onStart) o.onStart(v0);
      const mv = (ev) => {
        const k = ev.shiftKey ? 10 : 1;
        let v = v0 + (ev.clientX - x0) * step * k;
        if (o.min !== undefined) v = Math.max(o.min, v);
        if (o.max !== undefined) v = Math.min(o.max, v);
        v = Math.round(v * 100) / 100;
        if (v === last) return;
        last = v;
        input.value = String(v);
        if (o.onValue) o.onValue(v);
        else input.dispatchEvent(new Event('input', { bubbles: true }));
      };
      const up = () => {
        window.removeEventListener('pointermove', mv, true);
        window.removeEventListener('pointerup', up, true);
        scrubbing = false;
        target.style.cursor = '';
        if (o.onEnd) o.onEnd(last);
      };
      window.addEventListener('pointermove', mv, true);
      window.addEventListener('pointerup', up, true);
    }, true);
  }

  // ── Command palette (⌘\) ───────────────────────────────────────────────
  // commands: [{ act, label, group, key, enabled }]. Type to filter, arrows
  // to move, Enter to run, Escape to close.
  function palette(root, commands, onRun, opts = {}) {
    const box = el('div', { class: 'pal', role: 'dialog', 'aria-label': 'Commands' });
    const input = el('input', { type: 'text', placeholder: 'Type a command', 'aria-label': 'Search commands', spellcheck: 'false' });
    const list = el('div', { class: 'pl', role: 'listbox' });
    const foot = el('div', { class: 'pf' }, '↑↓ to move · ↵ to run · esc to close');
    box.append(el('div', { class: 'ph' }, icon('palette'), input, el('span', { class: 'k' }, L('palette'))), list, foot);
    const veil = el('div', { class: 'veil' });
    let shown = [], at = 0;
    const norm = (t) => t.toLowerCase();
    function draw() {
      const q = norm(input.value.trim()).split(/\s+/).filter(Boolean);
      shown = commands.filter((c) => q.every((w) => norm(c.label + ' ' + (c.group || '')).includes(w)));
      at = Math.max(0, Math.min(at, shown.length - 1));
      let lastGroup = null;
      const rows = [];
      shown.forEach((c, i) => {
        if (!q.length && c.group !== lastGroup) { rows.push(el('div', { class: 'pg' }, c.group || '')); lastGroup = c.group; }
        const r = el('div', { class: 'pi' + (i === at ? ' cur' : '') + (c.enabled === false ? ' off' : ''), role: 'option', 'data-i': String(i) },
          el('span', { class: 'pic' }, icon(c.icon || c.act)), el('span', { class: 'pt' }, c.label), el('span', { class: 'k' }, c.key || ''));
        rows.push(r);
      });
      if (!shown.length) rows.push(el('div', { class: 'pe' }, 'No matching command'));
      list.replaceChildren(...rows);
      const cur = list.querySelector('.cur');
      if (cur) cur.scrollIntoView({ block: 'nearest' });
    }
    function run(i) {
      const c = shown[i];
      if (!c || c.enabled === false) return;
      close();
      onRun(c.act);
    }
    input.addEventListener('input', () => { at = 0; draw(); });
    input.addEventListener('keydown', (e) => {
      e.stopPropagation();
      if (e.key === 'ArrowDown') { e.preventDefault(); at = Math.min(shown.length - 1, at + 1); draw(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); at = Math.max(0, at - 1); draw(); }
      else if (e.key === 'Enter') { e.preventDefault(); run(at); }
      else if (e.key === 'Escape') { e.preventDefault(); close(); }
      else if ((e.metaKey || e.ctrlKey) && !e.altKey && e.code === 'Backslash') { e.preventDefault(); close(); } // ⌘\ again closes
    });
    input.addEventListener('keyup', (e) => e.stopPropagation());
    list.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      const r = e.target.closest('.pi');
      if (r) run(Number(r.dataset.i));
    });
    list.addEventListener('pointermove', (e) => {
      const r = e.target.closest('.pi');
      if (r && Number(r.dataset.i) !== at) { at = Number(r.dataset.i); list.querySelectorAll('.pi').forEach((n) => n.classList.toggle('cur', Number(n.dataset.i) === at)); }
    });
    veil.addEventListener('pointerdown', (e) => { e.preventDefault(); e.stopPropagation(); close(); });
    box.addEventListener('pointerdown', (e) => e.stopPropagation());
    root.append(veil, box);
    const r = opts.rect || { left: 0, top: 0, right: innerWidth, bottom: innerHeight };
    box.style.left = Math.max(8, (r.left + r.right) / 2 - 220) + 'px';
    box.style.top = (r.top + 40) + 'px';
    box.style.maxHeight = Math.max(200, r.bottom - r.top - 80) + 'px';
    draw();
    setTimeout(() => input.focus(), 0);
    let closed = false;
    function close() {
      if (closed) return;
      closed = true;
      box.remove();
      veil.remove();
      if (opts.onClose) opts.onClose();
    }
    return { close };
  }

  // ── Colour popover ─────────────────────────────────────────────────────
  // opts: { title, key, value (hex or null for none), noneLabel, doc (hex[]),
  //         weights (px[] ) , weight (px) }. onPick({ color } | { none } |
  //         { weight }). Returns { el, close }.
  function colorPopover(root, anchor, opts, onPick) {
    const pop = el('div', { class: 'pop', role: 'dialog', 'aria-label': opts.title });
    const cur = (opts.value || '').toLowerCase();
    const sw = (c) => {
      const s = el('div', { class: 'sw' + (c && c.toLowerCase() === cur ? ' cur' : ''), title: c || opts.noneLabel || 'None', role: 'button' });
      if (c) s.style.background = c; else s.classList.add('no');
      s.addEventListener('pointerdown', (e) => { e.preventDefault(); e.stopPropagation(); onPick(c ? { color: c } : { none: true }); close(); });
      return s;
    };
    pop.append(el('div', { class: 'ttl' }, el('span', {}, opts.title), el('span', { class: 'k' }, opts.key || '')));
    if (opts.weights) {
      const wts = el('div', { class: 'wts' });
      opts.weights.forEach((w) => {
        const c = el('div', { class: 'chip' + (opts.strokeOn && Math.abs(w - opts.weight) < 0.26 ? ' cur' : ''), role: 'button' }, w + ' px');
        c.addEventListener('pointerdown', (e) => { e.preventDefault(); e.stopPropagation(); onPick({ weight: w }); close(); });
        wts.append(c);
      });
      pop.append(el('div', { class: 'lab' }, 'Weight'), wts);
    }
    const grid = el('div', { class: 'grid' });
    grid.append(sw(null));
    const doc = [...new Set((opts.doc || []).map((c) => c.toLowerCase()))].filter((c) => !PALETTE.includes(c)).slice(0, 9);
    doc.forEach((c) => grid.append(sw(c)));
    for (let i = doc.length; i < 9; i++) grid.append(el('div'));
    PALETTE.forEach((c) => grid.append(sw(c)));
    const hex = el('input', { type: 'text', value: opts.value || '', placeholder: '#RRGGBB', 'aria-label': 'Hex colour', maxlength: '7', spellcheck: 'false' });
    hex.addEventListener('keydown', (e) => {
      e.stopPropagation();
      if (e.key === 'Enter') {
        e.preventDefault();
        let v = hex.value.trim();
        if (!v.startsWith('#')) v = '#' + v;
        if (/^#[0-9a-f]{3}$/i.test(v)) v = '#' + v.slice(1).split('').map((ch) => ch + ch).join('');
        if (/^#[0-9a-f]{6}$/i.test(v)) { onPick({ color: v.toLowerCase() }); close(); }
      } else if (e.key === 'Escape') { e.preventDefault(); close(); }
    });
    hex.addEventListener('keyup', (e) => e.stopPropagation());
    pop.append(grid, el('div', { class: 'row' }, el('span', { class: 'lab', style: 'margin:0 4px 0 2px' }, 'Hex'), hex));
    pop.addEventListener('pointerdown', (e) => { e.stopPropagation(); if (e.target !== hex) e.preventDefault(); });
    root.append(pop);
    pop.classList.add('show');
    const h = pop.offsetHeight;
    pop.style.left = (anchor.right + 10) + 'px';
    pop.style.top = Math.max(8, Math.min(innerHeight - h - 8, anchor.top - 10)) + 'px';
    const outside = (e) => {
      const path = e.composedPath ? e.composedPath() : [];
      if (!path.includes(pop)) close();
    };
    setTimeout(() => window.addEventListener('pointerdown', outside, true), 0);
    let closed = false;
    function close() {
      if (closed) return;
      closed = true;
      window.removeEventListener('pointerdown', outside, true);
      pop.remove();
      if (opts.onClose) opts.onClose();
    }
    return { el: pop, close, focusHex: () => { hex.focus(); hex.select(); } };
  }

  // ── Paint panel ────────────────────────────────────────────────────────
  // The fill / stroke / text colour panel shared by the Shape tools rail and
  // Edit Shape. Laid out like Figma's: a saturation-and-brightness square,
  // hue and opacity sliders with an eyedropper beside them, a hex field and
  // an opacity field, then the colours already on the slide and recent ones.
  // Fills add Linear and Radial: a stop bar (click adds, drag moves, drag
  // away or Delete removes), angle, where a radial starts, Reverse.
  // opts: { which, title, modes [[mode, label]], state { mode, hex, alpha,
  //   stops, angle, centre }, slide [hex], recent [hex], anchor (rect),
  //   live (call onChange as things move), replace (nothing selected: pick a
  //   colour on the slide, then what it becomes; { deck } offers the whole
  //   presentation), onChange(st), onDone(keep, st), onMenu(), tips(node) }.
  const normHex = (raw) => {
    let h = String(raw || '').trim().replace(/^#/, '');
    if (/^[0-9a-f]{3}$/i.test(h)) h = h.split('').map((c) => c + c).join('');
    if (/^[0-9a-f]{8}$/i.test(h)) return { hex: '#' + h.slice(0, 6).toUpperCase(), alpha: Math.round(parseInt(h.slice(6), 16) / 255 * 100) / 100 };
    return /^[0-9a-f]{6}$/i.test(h) ? { hex: '#' + h.toUpperCase() } : null;
  };
  const mixHex = (a, b, t) => '#' + [1, 3, 5].map((i) => Math.round(parseInt(a.slice(i, i + 2), 16) * (1 - t) + parseInt(b.slice(i, i + 2), 16) * t).toString(16).padStart(2, '0')).join('').toUpperCase();
  function stopColourAt(stops, pos) {
    const st = stops.slice().sort((a, b) => a.pos - b.pos);
    if (pos <= st[0].pos) return st[0].hex;
    for (let i = 1; i < st.length; i++) if (pos <= st[i].pos) return st[i].pos - st[i - 1].pos < 1e-6 ? st[i].hex : mixHex(st[i - 1].hex, st[i].hex, (pos - st[i - 1].pos) / (st[i].pos - st[i - 1].pos));
    return st[st.length - 1].hex;
  }
  function hexToHsv(hex) {
    const r = parseInt(hex.slice(1, 3), 16) / 255, g = parseInt(hex.slice(3, 5), 16) / 255, b = parseInt(hex.slice(5, 7), 16) / 255;
    const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
    let h = 0;
    if (d) h = mx === r ? ((g - b) / d + 6) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
    return { h: h * 60, s: mx ? d / mx : 0, v: mx };
  }
  function hsvToHex(h, s, v) {
    const f = (n) => { const k = (n + h / 60) % 6; return v - v * s * Math.max(0, Math.min(k, 4 - k, 1)); };
    return '#' + [f(5), f(3), f(1)].map((x) => Math.round(x * 255).toString(16).padStart(2, '0')).join('').toUpperCase();
  }
  const PAINT_CSS = `
    .cpop { position: fixed; z-index: 2147483000; width: 272px; box-sizing: border-box; padding: 12px; background: #fff; color: #1f1f1f; border-radius: 12px;
            box-shadow: 0 2px 6px 2px rgba(60,64,67,.15), 0 1px 2px rgba(60,64,67,.3); font: 400 12px/16px ${FONT}; outline: none; overflow-y: auto; overscroll-behavior: contain; }
    .cpop * { box-sizing: border-box; font: inherit; }
    .cpop .hd { display: flex; align-items: center; justify-content: space-between; gap: 8px; font-weight: 500; font-size: 13px; margin-bottom: 10px; }
    .cpop .tabs { display: flex; background: ${GM.surface}; border-radius: 8px; padding: 2px; }
    .cpop .tabs button { border: 0; background: none; padding: 3px 8px; border-radius: 6px; cursor: pointer; color: ${GM.icon}; font-size: 12px; font-weight: 500; }
    .cpop .tabs button[aria-selected="true"] { background: #fff; color: #1f1f1f; box-shadow: 0 1px 2px rgba(60,64,67,.3); }
    .cpop .rep { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; min-height: 28px; color: ${GM.icon}; }
    .cpop .rep .chip { width: 24px; height: 24px; border-radius: 6px; border: 1px solid rgba(0,0,0,.18); flex: none; background: repeating-conic-gradient(#e3e3e3 0% 25%, #fff 0% 50%) 0 0 / 8px 8px; overflow: hidden; }
    .cpop .rep .chip i { display: block; width: 100%; height: 100%; }
    .cpop .rep label { display: flex; align-items: center; gap: 5px; margin-left: auto; cursor: pointer; color: #1f1f1f; }
    .cpop .sv { position: relative; height: 150px; border-radius: 8px; margin-bottom: 12px; cursor: crosshair; touch-action: none; }
    .cpop .sv b, .cpop .sl b { position: absolute; width: 14px; height: 14px; margin: -7px 0 0 -7px; border-radius: 50%; border: 2px solid #fff; box-shadow: 0 0 0 1px rgba(0,0,0,.35), 0 1px 3px rgba(0,0,0,.4); pointer-events: none; }
    .cpop .mix { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
    .cpop .mix .bars { flex: 1; display: grid; gap: 10px; }
    .cpop .sl { position: relative; height: 12px; border-radius: 6px; cursor: pointer; touch-action: none; margin: 0 7px; }
    .cpop .sl b { top: 50%; }
    .cpop .sl.hue { background: linear-gradient(to right, #f00, #ff0, #0f0, #0ff, #00f, #f0f, #f00); }
    .cpop .sl.al { background: repeating-conic-gradient(#d0d0d0 0% 25%, #fff 0% 50%) 0 0 / 8px 8px; }
    .cpop .sl.al i { position: absolute; inset: 0; border-radius: 6px; }
    .cpop .gbar { position: relative; height: 16px; border-radius: 8px; border: 1px solid ${GM.outline}; margin: 0 7px 20px; cursor: copy; touch-action: none; }
    .cpop .st { position: absolute; top: 10px; width: 14px; height: 14px; margin-left: -7px; padding: 0; border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%; border: 2px solid #fff;
                background: var(--c); box-shadow: 0 0 0 1px ${GM.outline}, 0 1px 2px rgba(0,0,0,.3); cursor: ew-resize; }
    .cpop .st.on { box-shadow: 0 0 0 2px #1a73e8, 0 1px 2px rgba(0,0,0,.3); z-index: 1; }
    .cpop .prow { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
    .cpop .prow.g .tx { padding: 0 6px; }
    .cpop .prow.rad { gap: 12px; }
    .cpop input[type="text"], .cpop input[type="number"] { height: 28px; border: 1px solid transparent; border-radius: 6px; padding: 0 8px; background: ${GM.surface}; color: inherit; min-width: 0; }
    .cpop input:focus { outline: 2px solid #a8c7fa; outline-offset: -1px; background: #fff; }
    .cpop input::-webkit-inner-spin-button, .cpop input::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
    .cpop .hexl { border: 1px solid ${GM.outline}; border-radius: 6px; height: 28px; padding: 0 8px; display: flex; align-items: center; color: ${GM.icon}; }
    .cpop .hex { flex: 1; text-transform: uppercase; font-family: 'Roboto Mono', Menlo, monospace; }
    .cpop .f { display: flex; align-items: center; gap: 4px; color: ${GM.icon}; }
    .cpop .f input { width: 46px; text-align: right; }
    .cpop .ib { width: 28px; height: 28px; border: 0; border-radius: 6px; background: none; cursor: pointer; display: grid; place-items: center; color: ${GM.icon}; flex: none; padding: 0; }
    .cpop .ib:hover, .cpop .tx:hover { background: ${GM.hover}; }
    .cpop .ib svg { width: 18px; height: 18px; fill: currentColor; }
    .cpop .tx { border: 1px solid ${GM.outline}; background: none; height: 26px; padding: 0 8px; border-radius: 6px; cursor: pointer; color: #1f1f1f; white-space: nowrap; }
    .cpop .tx[disabled] { opacity: .4; pointer-events: none; }
    .cpop .dial { width: 26px; height: 26px; border-radius: 50%; border: 1px solid ${GM.outline}; position: relative; cursor: grab; flex: none; touch-action: none; }
    .cpop .dial i { position: absolute; left: 50%; top: 50%; width: 11px; height: 2px; margin-top: -1px; background: #1a73e8; border-radius: 1px; transform-origin: 0 50%; }
    .cpop .cgrid { display: grid; grid-template-columns: repeat(3, 14px); grid-template-rows: repeat(3, 14px); gap: 2px; }
    .cpop .cgrid button { border: 1px solid ${GM.outline}; background: #fff; border-radius: 3px; padding: 0; cursor: pointer; }
    .cpop .cgrid button[data-c="1"] { grid-area: 1 / 1; } .cpop .cgrid button[data-c="2"] { grid-area: 1 / 3; } .cpop .cgrid button[data-c="0"] { grid-area: 2 / 2; }
    .cpop .cgrid button[data-c="3"] { grid-area: 3 / 1; } .cpop .cgrid button[data-c="4"] { grid-area: 3 / 3; }
    .cpop .cgrid button[aria-checked="true"] { background: #1a73e8; border-color: #1a73e8; }
    .cpop .sep { height: 1px; background: ${GM.outline}; margin: 4px -12px 10px; opacity: .6; }
    .cpop .cap { color: ${GM.icon}; font-size: 11px; margin: 2px 0 6px; }
    .cpop .sws { display: grid; grid-template-columns: repeat(9, 20px); gap: 8px; margin-bottom: 10px; }
    .cpop .sw { width: 20px; height: 20px; border-radius: 5px; border: 1px solid rgba(0,0,0,.18); padding: 0; cursor: pointer; }
    .cpop .sw:hover { transform: scale(1.15); }
    .cpop .sw.cur { box-shadow: 0 0 0 2px #fff, 0 0 0 4px #1a73e8; }
    .cpop .ft { display: flex; align-items: center; gap: 8px; margin-top: 4px; }
    .cpop .ft .sp { flex: 1; }
    .cpop .pb { width: 28px; height: 28px; border-radius: 50%; border: 0; padding: 0; display: grid; place-items: center; cursor: pointer; background: ${GM.surface}; color: #1f1f1f; }
    .cpop .pb svg { width: 16px; height: 16px; }
    .cpop .pb.ok { background: #0b57d0; color: #fff; }
    .cpop .pb[disabled] { opacity: .4; pointer-events: none; }
    .cpop .pb:hover { filter: brightness(.94); }
    .cpop .gbar, .cpop .prow.g { display: none; }
    .cpop[data-mode="linear"] .gbar, .cpop[data-mode="radial"] .gbar { display: block; }
    .cpop[data-mode="linear"] .prow.g:not(.rad), .cpop[data-mode="radial"] .prow.g:not(.lin) { display: flex; }
    .cpop[data-mode="none"] .sv, .cpop[data-mode="none"] .mix, .cpop[data-mode="none"] .prow.c, .cpop[data-wait="1"] .sv, .cpop[data-wait="1"] .mix, .cpop[data-wait="1"] .prow.c { opacity: .35; pointer-events: none; }
  `;
  function paintPanel(root, opts) {
    const st = Object.assign({ mode: 'solid', hex: '#4285F4', alpha: 1, stops: null, angle: 90, centre: 0, sel: 0, from: null, deck: false }, JSON.parse(JSON.stringify(opts.state || {})));
    if (!st.stops) st.stops = [{ hex: st.hex, pos: 0 }, { hex: mixHex(st.hex, '#000000', 0.45), pos: 1 }];
    const start = JSON.stringify(st);
    const startMode = st.mode;
    const which = opts.which;
    const isGrad = () => st.mode === 'linear' || st.mode === 'radial';
    const cur = () => (isGrad() ? st.stops[st.sel] : st);
    let hsv = hexToHsv(cur().hex);
    const modes = opts.modes || [['solid', 'Solid']];
    const tabs = el('div', { class: 'tabs', role: 'tablist' }, ...modes.map(([m, label]) => el('button', { type: 'button', role: 'tab', 'data-mode': m }, label)));
    if (modes.length < 2) tabs.style.display = 'none';
    const svKnob = el('b'), hueKnob = el('b'), alKnob = el('b'), alFill = el('i');
    const sv2 = el('div', { class: 'sv', 'aria-label': 'Saturation and brightness' }, svKnob);
    const hue = el('div', { class: 'sl hue', 'aria-label': 'Hue' }, hueKnob);
    const al = el('div', { class: 'sl al', 'aria-label': 'Opacity' }, alFill, alKnob);
    const drop = el('button', { type: 'button', class: 'ib', 'aria-label': 'Pick a colour from the screen', 'data-tip': opts.replace ? 'Pick the colour to change from the slide' : 'Pick a colour from the screen' },
      icon('dropper'));
    if (!('EyeDropper' in window)) drop.style.visibility = 'hidden';
    const bar = el('div', { class: 'gbar', 'data-tip': 'Click to add a stop · drag to move · drag away or Delete to remove' });
    const hexIn = el('input', { type: 'text', class: 'hex', spellcheck: 'false', maxlength: '9', 'aria-label': 'Hex colour', 'data-tip': 'Hex: 3, 6 or 8 digits (8 sets opacity too)' });
    const alphaIn = el('input', { type: 'number', min: '0', max: '100', step: '1', 'aria-label': 'Opacity, percent' });
    const posIn = el('input', { type: 'number', min: '0', max: '100', step: '1', 'aria-label': 'Stop position, percent' });
    const angIn = el('input', { type: 'number', step: '1', 'aria-label': 'Angle in degrees' });
    const dial = el('div', { class: 'dial', 'data-tip': 'Drag to turn · ⇧ snaps to 15°' }, el('i'));
    const rev = el('button', { type: 'button', class: 'tx', 'data-tip': 'Reverse the stops' }, 'Reverse');
    const delStop = el('button', { type: 'button', class: 'tx', 'data-tip': 'Remove the selected stop', 'data-key': 'Delete' }, 'Remove stop');
    const centre = el('div', { class: 'cgrid', role: 'radiogroup', 'aria-label': 'Where the gradient starts' },
      ...[[1, 'Top left'], [2, 'Top right'], [0, 'Middle'], [3, 'Bottom left'], [4, 'Bottom right']].map(([v, label]) => el('button', { type: 'button', 'data-c': v, 'aria-label': label, 'data-tip': 'Starts: ' + label.toLowerCase() })));
    const swSlide = el('div', { class: 'sws' }), swRecent = el('div', { class: 'sws' });
    const capSlide = el('div', { class: 'cap' }, opts.replace ? 'On this slide: pick the colour to change' : 'On this slide'), capRecent = el('div', { class: 'cap' }, 'Recent');
    const mkPb = (cls, tipText, key, d) => {
      const b = el('button', { type: 'button', class: 'pb ' + cls, 'aria-label': tipText, 'data-tip': tipText, 'data-key': key });
      const g = sv('svg', { viewBox: '0 0 20 20', 'aria-hidden': 'true' });
      g.append(sv('path', { d, fill: 'none', stroke: 'currentColor', 'stroke-width': '2.2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
      b.append(g);
      return b;
    };
    const bNo = mkPb('no', 'Cancel', 'Esc', 'M5.5 5.5l9 9M14.5 5.5l-9 9'), bOk = mkPb('ok', opts.replace ? 'Replace' : 'Apply', '↵', 'M4.5 10.5l3.6 3.6 7.4-8');
    const more = el('button', { type: 'button', class: 'tx', 'data-tip': 'Open Slides’ own colour menu (theme colours live there)' }, 'Slides menu');
    if (!opts.onMenu) more.style.display = 'none';
    const fromChip = el('i'), toChip = el('i'), repText = el('span', {}, '');
    const deckBox = el('input', { type: 'checkbox' });
    const deckLab = el('label', { 'data-tip': 'Change it on every slide, one slide after another' }, deckBox, 'All slides');
    if (!(opts.replace && opts.replace.deck)) deckLab.style.display = 'none';
    const rep = el('div', { class: 'rep' }, el('span', { class: 'chip' }, fromChip), el('span', {}, '→'), el('span', { class: 'chip' }, toChip), repText, deckLab);
    if (!opts.replace) rep.style.display = 'none';
    if (opts.noAlpha) { al.style.display = 'none'; st.alpha = 1; }
    const alphaLab = el('label', { class: 'f', 'data-tip': 'Opacity · ⌥-drag to scrub' }, alphaIn, el('span', {}, '%'));
    if (opts.noAlpha) alphaLab.style.display = 'none';
    const rowColour = el('div', { class: 'prow c' }, el('span', { class: 'hexl' }, 'Hex'), hexIn, alphaLab);
    const rowStop = el('div', { class: 'prow g' }, el('label', { class: 'f', 'data-tip': 'Position of the selected stop · ⌥-drag to scrub' }, el('span', {}, 'Stop'), posIn, el('span', {}, '%')), delStop, rev);
    const rowLin = el('div', { class: 'prow g lin' }, dial, el('label', { class: 'f', 'data-tip': 'Angle: 0° runs left to right, 90° top to bottom · ⌥-drag to scrub' }, angIn, el('span', {}, '°')),
      ...[0, 45, 90, 180].map((a) => el('button', { type: 'button', class: 'tx', 'data-ang': a }, a + '°')));
    const rowRad = el('div', { class: 'prow g rad' }, el('span', { class: 'cap', style: 'margin:0' }, 'Starts from'), centre);
    const node = el('div', { class: 'cpop', role: 'dialog', 'aria-label': opts.title, tabindex: '-1' },
      el('div', { class: 'hd' }, el('span', {}, opts.title), tabs),
      rep, bar, rowStop, rowLin, rowRad, sv2, el('div', { class: 'mix' }, drop, el('div', { class: 'bars' }, hue, al)), rowColour,
      el('div', { class: 'sep' }), capSlide, swSlide, capRecent, swRecent,
      el('div', { class: 'ft' }, more, el('span', { class: 'sp' }), bNo, bOk));
    const cssStops = () => st.stops.slice().sort((a, b) => a.pos - b.pos).map((x) => `${x.hex} ${Math.round(x.pos * 1000) / 10}%`).join(', ');
    const rgba = (h, a) => `rgba(${parseInt(h.slice(1, 3), 16)}, ${parseInt(h.slice(3, 5), 16)}, ${parseInt(h.slice(5, 7), 16)}, ${a})`;
    const changed = () => JSON.stringify(Object.assign({}, st, { sel: 0 })) !== JSON.stringify(Object.assign(JSON.parse(start), { sel: 0 }));
    let closed = false;
    function place() {
      if (closed) return;
      const a = opts.anchor || { right: 60, top: 80 };
      node.style.maxHeight = Math.max(200, window.innerHeight - 16) + 'px';
      const r = node.getBoundingClientRect();
      let left = a.right + 10;
      if (left + r.width > window.innerWidth - 8) left = Math.max(8, (a.left !== undefined ? a.left : a.right) - r.width - 10);
      node.style.left = Math.max(8, Math.min(window.innerWidth - r.width - 8, left)) + 'px';
      node.style.top = Math.max(8, Math.min(window.innerHeight - r.height - 8, a.top - 12)) + 'px';
    }
    const sync = (quiet) => {
      node.dataset.mode = st.mode;
      node.dataset.wait = opts.replace && !st.from ? '1' : '0';
      tabs.querySelectorAll('button').forEach((b) => b.setAttribute('aria-selected', String(b.dataset.mode === st.mode)));
      const c = cur();
      sv2.style.background = `linear-gradient(to top, #000, rgba(0,0,0,0)), linear-gradient(to right, #fff, rgba(255,255,255,0)), hsl(${hsv.h}, 100%, 50%)`;
      svKnob.style.left = hsv.s * 100 + '%'; svKnob.style.top = (1 - hsv.v) * 100 + '%'; svKnob.style.background = c.hex;
      hueKnob.style.left = hsv.h / 360 * 100 + '%'; hueKnob.style.background = `hsl(${hsv.h}, 100%, 50%)`;
      alKnob.style.left = st.alpha * 100 + '%'; alKnob.style.background = rgba(c.hex, st.alpha);
      alFill.style.background = `linear-gradient(to right, ${rgba(c.hex, 0)}, ${c.hex})`;
      if (root.activeElement !== hexIn) hexIn.value = c.hex.replace('#', '');
      if (root.activeElement !== alphaIn) alphaIn.value = String(Math.round(st.alpha * 100));
      if (isGrad()) {
        if (root.activeElement !== posIn) posIn.value = String(Math.round(c.pos * 100));
        if (root.activeElement !== angIn) angIn.value = String(st.angle);
        dial.firstChild.style.transform = `rotate(${st.angle}deg)`;
        delStop.disabled = st.stops.length <= 2;
        centre.querySelectorAll('button').forEach((b) => b.setAttribute('aria-checked', String(+b.dataset.c === st.centre)));
        bar.style.background = `linear-gradient(to right, ${cssStops()})`;
        bar.replaceChildren(...st.stops.map((x, i) => {
          const h = el('button', { type: 'button', class: 'st' + (i === st.sel ? ' on' : ''), 'data-i': i, 'aria-label': `Stop at ${Math.round(x.pos * 100)}%` });
          h.style.left = x.pos * 100 + '%';
          h.style.setProperty('--c', x.hex);
          return h;
        }));
      }
      if (opts.replace) {
        fromChip.style.background = st.from || 'transparent';
        toChip.style.background = st.from ? rgba(st.hex, st.alpha) : 'transparent';
        repText.textContent = st.from ? '' : 'Nothing selected';
        swSlide.querySelectorAll('.sw').forEach((b) => b.classList.toggle('cur', b.dataset.hex === st.from));
        bOk.disabled = !st.from || (st.from === st.hex && st.alpha >= 0.995);
      }
      if (!quiet && opts.live && opts.onChange) opts.onChange(JSON.parse(JSON.stringify(st)));
    };
    const swatch = (h) => { const b = el('button', { type: 'button', class: 'sw', 'data-hex': h, 'aria-label': h, 'data-tip': h }); b.style.background = h; return b; };
    const setColour = (h, a) => {
      cur().hex = h;
      hsv = Object.assign(hexToHsv(h), hsv.s === 0 || hexToHsv(h).s === 0 ? { h: hexToHsv(h).s === 0 ? hsv.h : hexToHsv(h).h } : {});
      if (a !== undefined) st.alpha = a;
      if (st.mode === 'none') st.mode = 'solid';
      sync();
    };
    const setFrom = (h) => { st.from = h; st.hex = h; st.alpha = 1; hsv = hexToHsv(h); sync(); };
    const fromHsv = () => { cur().hex = hsvToHex(hsv.h, hsv.s, hsv.v); if (st.mode === 'none') st.mode = 'solid'; sync(); };
    const dragOn = (target, fn) => target.addEventListener('pointerdown', (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      const r = target.getBoundingClientRect();
      const at = (ev) => fn(Math.min(1, Math.max(0, (ev.clientX - r.left) / r.width)), Math.min(1, Math.max(0, (ev.clientY - r.top) / r.height)));
      const end = () => { window.removeEventListener('pointermove', at, true); window.removeEventListener('pointerup', end, true); };
      window.addEventListener('pointermove', at, true);
      window.addEventListener('pointerup', end, true);
      at(e);
    });
    dragOn(sv2, (x, y) => { hsv.s = x; hsv.v = 1 - y; fromHsv(); });
    dragOn(hue, (x) => { hsv.h = Math.min(359.9, x * 360); fromHsv(); });
    dragOn(al, (x) => { st.alpha = Math.round(x * 100) / 100; if (st.mode === 'none') st.mode = 'solid'; sync(); });
    tabs.addEventListener('click', (e) => {
      const b = e.target.closest('button');
      if (!b) return;
      const was = st.mode;
      st.mode = b.dataset.mode;
      // Going solid ↔ gradient carries the colour in hand across.
      if (isGrad() && was === 'solid' && st.stops.length === 2 && startMode !== 'linear' && startMode !== 'radial') { st.stops[0].hex = st.hex; st.stops[1].hex = mixHex(st.hex, '#000000', 0.45); }
      if (st.mode === 'solid' && (was === 'linear' || was === 'radial')) st.hex = st.stops[st.sel].hex;
      if (st.mode !== 'none') hsv = hexToHsv(cur().hex);
      sync();
    });
    hexIn.addEventListener('input', () => { const c = normHex(hexIn.value); if (c) setColour(c.hex, c.alpha); });
    hexIn.addEventListener('blur', () => sync(true));
    hexIn.addEventListener('focus', () => setTimeout(() => hexIn.select(), 0));
    alphaIn.addEventListener('input', () => { const v = parseFloat(alphaIn.value); if (Number.isFinite(v)) { st.alpha = Math.min(1, Math.max(0, v / 100)); sync(); } });
    posIn.addEventListener('input', () => { const v = parseFloat(posIn.value); if (Number.isFinite(v)) { st.stops[st.sel].pos = Math.min(1, Math.max(0, v / 100)); sync(); } });
    angIn.addEventListener('input', () => { const v = parseFloat(angIn.value); if (Number.isFinite(v)) { st.angle = v; sync(); } });
    scrub(alphaIn.parentNode, alphaIn, { step: 1, min: 0, max: 100 });
    scrub(posIn.parentNode, posIn, { step: 1, min: 0, max: 100 });
    scrub(angIn.parentNode, angIn, { step: 1 });
    rowLin.addEventListener('click', (e) => { const b = e.target.closest('[data-ang]'); if (b) { st.angle = +b.dataset.ang; sync(); } });
    centre.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) { st.centre = +b.dataset.c; sync(); } });
    rev.addEventListener('click', () => { st.stops.forEach((x) => { x.pos = Math.round((1 - x.pos) * 1e4) / 1e4; }); sync(); });
    const removeStop = () => { if (st.stops.length <= 2) return; st.stops.splice(st.sel, 1); st.sel = Math.min(st.sel, st.stops.length - 1); hsv = hexToHsv(cur().hex); sync(); };
    delStop.addEventListener('click', removeStop);
    dial.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      const r = dial.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
      const turn = (ev) => {
        let a = Math.atan2(ev.clientY - cy, ev.clientX - cx) * 180 / Math.PI;
        a = ev.shiftKey ? Math.round(a / 15) * 15 : Math.round(a);
        st.angle = (a + 360) % 360;
        sync();
      };
      const end = () => { window.removeEventListener('pointermove', turn, true); window.removeEventListener('pointerup', end, true); };
      window.addEventListener('pointermove', turn, true);
      window.addEventListener('pointerup', end, true);
      turn(e);
    });
    bar.addEventListener('pointerdown', (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      const r = bar.getBoundingClientRect();
      const posOf = (ev) => Math.min(1, Math.max(0, (ev.clientX - r.left) / r.width));
      const h = e.target.closest('.st');
      if (h) st.sel = +h.dataset.i;
      else { const pos = Math.round(posOf(e) * 100) / 100; st.stops.push({ hex: stopColourAt(st.stops, pos), pos }); st.sel = st.stops.length - 1; }
      hsv = hexToHsv(cur().hex);
      sync();
      const held = st.stops[st.sel];
      let gone = false;
      const mv = (ev) => {
        const away = Math.abs(ev.clientY - (r.top + r.height / 2)) > 36 && st.stops.length > (gone ? 1 : 2);
        if (away && !gone) { gone = true; st.stops.splice(st.stops.indexOf(held), 1); st.sel = 0; }
        else if (!away && gone) { gone = false; st.stops.push(held); }
        if (!gone) { held.pos = Math.round(posOf(ev) * 1000) / 1000; st.sel = st.stops.indexOf(held); }
        hsv = hexToHsv(cur().hex);
        sync();
      };
      const end = () => { window.removeEventListener('pointermove', mv, true); window.removeEventListener('pointerup', end, true); };
      window.addEventListener('pointermove', mv, true);
      window.addEventListener('pointerup', end, true);
    });
    swSlide.addEventListener('click', (e) => { const b = e.target.closest('.sw'); if (b) { if (opts.replace) setFrom(b.dataset.hex); else setColour(b.dataset.hex); } });
    swRecent.addEventListener('click', (e) => { const b = e.target.closest('.sw'); if (b && !(opts.replace && !st.from)) setColour(b.dataset.hex); });
    drop.addEventListener('click', async () => {
      try {
        const r = await new window.EyeDropper().open();
        const c = normHex(r && r.sRGBHex);
        if (!c) return;
        if (opts.replace && !st.from) {
          // The nearest colour that is really on the slide (the screen's pixel can be a shade off).
          const dist = (a, b) => [1, 3, 5].reduce((t, i) => t + (parseInt(a.slice(i, i + 2), 16) - parseInt(b.slice(i, i + 2), 16)) ** 2, 0);
          const near = (opts.slide || []).map((h) => [dist(h, c.hex), h]).sort((a, b) => a[0] - b[0])[0];
          setFrom(near && near[0] < 1200 ? near[1] : c.hex);
        } else setColour(c.hex);
      } catch { /* closed without a pick */ }
    });
    deckBox.addEventListener('change', () => { st.deck = deckBox.checked; });
    const ro = typeof ResizeObserver === 'function' ? new ResizeObserver(() => place()) : null;
    function close() {
      if (closed) return;
      closed = true;
      window.removeEventListener('pointerdown', away, true);
      window.removeEventListener('resize', place);
      if (ro) ro.disconnect();
      node.remove();
      if (opts.onClose) opts.onClose();
    }
    const done = (keep) => {
      const ch = changed();
      const out = JSON.parse(JSON.stringify(st));
      close();
      if (opts.onDone) opts.onDone(!!keep && ch, out);
    };
    bNo.addEventListener('click', () => done(false));
    bOk.addEventListener('click', () => done(true));
    more.addEventListener('click', () => { done(false); opts.onMenu(); });
    node.addEventListener('keydown', (e) => {
      e.stopPropagation();
      const typing = e.target.tagName === 'INPUT' && e.target.type !== 'checkbox';
      if (e.key === 'Escape') { e.preventDefault(); done(false); }
      else if (e.key === 'Enter') { e.preventDefault(); if (typing) e.target.blur(); if (!bOk.disabled) done(true); }
      else if (!typing && (e.key === 'Delete' || e.key === 'Backspace') && isGrad()) { e.preventDefault(); removeStop(); }
      else if (!typing && (e.key === 'ArrowLeft' || e.key === 'ArrowRight') && isGrad()) {
        e.preventDefault();
        const x = st.stops[st.sel];
        x.pos = Math.min(1, Math.max(0, Math.round((x.pos + (e.key === 'ArrowLeft' ? -1 : 1) * (e.shiftKey ? 0.1 : 0.01)) * 100) / 100));
        sync();
      }
    });
    ['keyup', 'keypress', 'mousedown', 'pointerdown', 'click', 'wheel'].forEach((t) => node.addEventListener(t, (e) => e.stopPropagation()));
    node.addEventListener('mousedown', (e) => { if (e.target.tagName !== 'INPUT') e.preventDefault(); });
    const away = (e) => {
      const path = e.composedPath ? e.composedPath() : [];
      if (closed || path.includes(node) || path.some((n) => n && n.dataset && (n.dataset.act === which || n.dataset.act === opts.act))) return;
      done(false);
    };
    root.append(node);
    if (opts.tips) opts.tips(node);
    const a = (opts.slide || []).map((h) => normHex(h)).filter(Boolean).map((c) => c.hex);
    const b = (opts.recent || []).map((h) => normHex(h)).filter(Boolean).map((c) => c.hex);
    swSlide.replaceChildren(...[...new Set(a)].slice(0, 27).map(swatch));
    swRecent.replaceChildren(...[...new Set(b)].slice(0, 9).map(swatch));
    capSlide.style.display = swSlide.style.display = a.length ? '' : 'none';
    capRecent.style.display = swRecent.style.display = b.length ? '' : 'none';
    sync(true);
    place();
    if (ro) ro.observe(node);
    window.addEventListener('resize', place);
    setTimeout(() => window.addEventListener('pointerdown', away, true), 0);
    node.focus({ preventScroll: true });
    return { node, which, close, done, state: () => JSON.parse(JSON.stringify(st)) };
  }

  // Every command with a label and group, for the palette.
  function commandList(extra = []) {
    const out = [];
    const add = (it, group) => { if (it.act && !it.sep && !it.field) out.push({ act: it.act, label: it.tip.replace(/ \(.*\)$/, ''), group, key: it.key !== undefined ? it.key : L(it.act), icon: it.icon }); };
    extra.forEach((c) => out.push(c));
    SECTIONS.forEach((sec) => sec.items.forEach((it) => {
      const group = { place: 'Arrange and align', combine: 'Combine', group: 'Group', outline: 'Outline', paint: 'Fill and stroke' }[sec.id];
      if (it.fly) it.fly.forEach((f) => add(f, it.act === 'arrange' ? 'Arrange' : it.act === 'align' ? 'Align and distribute' : group));
      else add(it, group);
    }));
    [['rotL15', 'Rotate left 15°'], ['rotR15', 'Rotate right 15°'], ['scaleUp', 'Make larger'], ['scaleDown', 'Make smaller'],
      ['strokeThinner', 'Thinner stroke'], ['strokeThicker', 'Thicker stroke']].forEach(([act, label]) => out.push({ act, label, group: 'Transform and stroke', key: L(act), icon: act === 'rotL15' ? 'rotL' : act === 'rotR15' ? 'rotR' : act }));
    // Keep each group together (an extra can belong to a group listed
    // later), so every heading shows once.
    const rank = new Map();
    out.forEach((c) => { if (!rank.has(c.group)) rank.set(c.group, rank.size); });
    return out.map((c, i) => [c, i]).sort((a, b) => rank.get(a[0].group) - rank.get(b[0].group) || a[1] - b[1]).map(([c]) => c);
  }

  return { ACCENT, FONT, GM, CSS: CSS + PAINT_CSS, el, sv, icon, mountRail, colorPopover, paintPanel, normHex, mixHex, stopColourAt, SECTIONS, PALETTE, label: L, scrub, palette, commandList };
})();
