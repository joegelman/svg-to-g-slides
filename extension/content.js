// Injected into Google Slides editor tabs only (see manifest.json's
// content_scripts.matches). Deliberately passive: this script never performs
// a privileged action (no clipboard write, no Slides API call) — it only
// tracks mouse position and reports it back to the popup on request. That's
// what lets the popup's own click trigger the actual clipboard write later
// without any user-activation-across-messaging concerns (execCommand('copy')
// needs a fresh gesture in the SAME document it's called from — see
// popup.js).
//
// No DOM inspection of Slides' own editing-surface/zoom-control elements at
// all — popup.js estimates canvas position and slide size from the browser
// window size and an assumed-default Slides layout instead. That's a
// deliberate choice, not a shortcut: reverse-engineering Slides' internal
// rendering DOM would be exactly the kind of fragile, could-break-on-any-
// Google-UI-update dependency this whole clipboard approach was built to
// avoid needing in the first place. See popup.js for the estimation math.

let lastMouse = null; // {x, y} in viewport client coords; null until first move

document.addEventListener('mousemove', (e) => {
  lastMouse = { x: e.clientX, y: e.clientY };
}, { passive: true });

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type !== 'GET_PLACEMENT_CONTEXT') return; // not for us

  sendResponse({
    ok: true,
    windowWidth: window.innerWidth,
    windowHeight: window.innerHeight,
    mouse: lastMouse,
  });
  // Response is synchronous (no async work above) -> no `return true` needed.
});
