// Injected into Google Slides editor tabs only (see manifest.json's
// content_scripts.matches). Deliberately passive: this script never performs
// a privileged action (no clipboard write, no Slides API call) — it only
// tracks mouse position and reports DOM geometry back to the popup on
// request. That's what lets the popup's own click trigger the actual
// clipboard write later without any user-activation-across-messaging
// concerns (execCommand('copy') needs a fresh gesture in the SAME document
// it's called from — see popup.js).

// ── PLACEHOLDER — Stage 0 live validation required before trusting these ──
// These selectors and the pixel->point formula below are not yet confirmed
// against a real Slides tab. Open a real presentation, inspect the actual
// editing-surface element (don't assume it's SVG — Slides has changed its
// rendering internals before) and the zoom-percent control, and replace
// these placeholders with what's actually found. See the "Stage 0" section
// of the project plan for the exact validation steps (constancy check
// across zoom levels, cross-check against a presentation of known size).
const CANVAS_SELECTOR = '[TODO: fill in from live DOM inspection]';
const ZOOM_SELECTOR = '[TODO: fill in from live DOM inspection]';
// ────────────────────────────────────────────────────────────────────────

let lastMouse = null; // {x, y} in viewport client coords; null until first move

document.addEventListener('mousemove', (e) => {
  lastMouse = { x: e.clientX, y: e.clientY };
}, { passive: true });

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type !== 'GET_PLACEMENT_CONTEXT') return; // not for us

  const canvas = document.querySelector(CANVAS_SELECTOR);
  if (!canvas) {
    sendResponse({ ok: false, reason: 'canvas-not-found' });
    return;
  }

  const rect = canvas.getBoundingClientRect();
  const zoomEl = document.querySelector(ZOOM_SELECTOR);
  const zoomPercent = zoomEl ? parseFloat(zoomEl.textContent) : null;

  sendResponse({
    ok: true,
    canvasRect: { left: rect.left, top: rect.top, width: rect.width, height: rect.height },
    mouse: lastMouse,
    zoomPercent: Number.isFinite(zoomPercent) ? zoomPercent : null,
  });
  // Response is synchronous (no async work above) -> no `return true` needed.
});
