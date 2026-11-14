// SVG to Slides — one-time "What's new" card.
// background.js sets storage.whatsNew when an existing install updates
// across an announced release. Show a small card in the corner of the
// Slides workspace once, then clear the flag. It never takes focus, so
// it can't get in the way of Slides' paste target.
(() => {
  const FONT = "'Google Sans', Roboto, Arial, sans-serif";
  const URL_WHATS_NEW = 'https://svgslid.es/whats-new';

  function el(tag, attrs = {}, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    n.append(...kids);
    return n;
  }

  function show(version) {
    const r = (typeof SB !== 'undefined' && SB.visibleWorkspaceRect) ? SB.visibleWorkspaceRect()
      : { left: 0, top: 0, right: innerWidth, bottom: innerHeight };
    const host = el('div', { id: 'svg2slides-whats-new' });
    const root = host.attachShadow({ mode: 'open' });
    const style = document.createElement('style');
    style.textContent = `
      .c { position: fixed; z-index: 2147483000; width: 300px; box-sizing: border-box;
           background: #fff; color: #1f1f1f; border-radius: 16px; padding: 16px 16px 12px;
           font: 400 13px/19px ${FONT};
           box-shadow: 0 1px 3px rgba(60,64,67,.3), 0 4px 8px 3px rgba(60,64,67,.15);
           animation: in .18s ease-out; }
      @keyframes in { from { opacity: 0; transform: translateY(8px); } }
      .t { font: 500 15px/20px ${FONT}; margin: 0 24px 6px 0; }
      .v { color: #444746; font-size: 12px; margin-bottom: 8px; }
      ul { margin: 0 0 12px; padding-left: 18px; }
      li { margin: 0 0 4px; }
      b { font-weight: 500; }
      .row { display: flex; justify-content: flex-end; gap: 8px; }
      .btn { font: 500 13px/1 ${FONT}; height: 32px; padding: 0 14px; border-radius: 16px;
             display: inline-flex; align-items: center; cursor: pointer; user-select: none;
             text-decoration: none; }
      .text { color: #0b57d0; }
      .text:hover { background: rgba(11,87,208,.08); }
      .tonal { background: #c2e7ff; color: #004a77; }
      .tonal:hover { filter: brightness(.97); }
      .x { position: absolute; top: 10px; right: 10px; width: 28px; height: 28px; border-radius: 14px;
           display: flex; align-items: center; justify-content: center; cursor: pointer; color: #444746;
           font-size: 18px; line-height: 1; }
      .x:hover { background: rgba(68,71,70,.08); }`;
    const close = el('div', { class: 'x', role: 'button', 'aria-label': 'Close' }, '×');
    const more = el('a', { class: 'btn text', href: URL_WHATS_NEW, target: '_blank', rel: 'noopener' }, 'See it in action');
    const ok = el('div', { class: 'btn tonal', role: 'button' }, 'Got it');
    const card = el('div', { class: 'c', role: 'dialog', 'aria-label': "What's new in SVG to Slides" },
      close,
      el('div', { class: 't' }, 'SVG to Slides got an upgrade'),
      el('div', { class: 'v' }, 'Version ' + version),
      el('ul', {},
        el('li', {}, el('b', {}, 'Edit Shape. '), 'Double-click any shape to drag its points and curve handles.'),
        el('li', {}, el('b', {}, 'Any shape. '), 'Works on Slides’ own shapes, lines and WordArt too.'),
        el('li', {}, el('b', {}, 'One click to insert. '), 'Drop an SVG, click where it goes. It lands right there.')),
      el('div', { class: 'row' }, more, ok));
    root.append(style, card);
    card.style.left = Math.max(12, r.left + 16) + 'px';
    card.style.bottom = Math.max(12, innerHeight - r.bottom + 16) + 'px';
    // Clicks on the card must not move focus out of Slides.
    card.addEventListener('mousedown', (e) => { if (!e.target.closest('a')) e.preventDefault(); });
    const dismiss = () => host.remove();
    close.addEventListener('click', dismiss);
    ok.addEventListener('click', dismiss);
    more.addEventListener('click', () => setTimeout(dismiss, 0));
    document.documentElement.appendChild(host);
  }

  if (!chrome.storage || !chrome.storage.local) return;
  chrome.storage.local.get('whatsNew', ({ whatsNew }) => {
    if (!whatsNew) return;
    // Clear first so it can only ever show once, even across tabs.
    chrome.storage.local.remove('whatsNew');
    // Let Slides finish laying out the workspace before measuring it.
    setTimeout(() => show(whatsNew), 2500);
  });
})();
