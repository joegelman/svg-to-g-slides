console.log('[svg2slides] content.js loaded, isPyodideReady() =', typeof isPyodideReady === 'function' ? isPyodideReady() : '(isPyodideReady undefined — pyodide-bridge.js may not have loaded)');

// Injected into Google Slides editor tabs only (see manifest.json's
// content_scripts.matches). shared.js (BACKEND, readFilesAsBase64,
// estimatePlacement, ASSUMED_* constants) and pyodide-bridge.js load first —
// see manifest.json.
//
// Flow: dropping an .svg shows a small 50%-opacity ghost preview (+ a
// neutral "+" badge) that follows the mouse, cursor 'grabbing', and starts
// conversion immediately in the background. Click anywhere to place it —
// cursor briefly flashes 'grab' to confirm, then 'progress' while the
// ghost sits frozen in place waiting for the second click. Click again
// anywhere — that second click runs execCommand('copy'), removes the
// ghost, and shows a small "Click ⌘V to insert" tooltip, which clears once
// a paste is detected (or after a timeout).
//
// Back to execCommand('copy') (not the async Clipboard API) after directly
// confirming, via a clipboard read-back, that the async API's mandatory
// "web " MIME-type prefix is NOT stripped on read — meaning it's
// structurally incapable of writing the exact unprefixed custom type
// Slides' own paste handler looks for. That was a dead end, not a focus
// problem.
//
// execCommand('copy') requires briefly focusing our own hidden
// contenteditable div, which steals focus from Slides' real paste target —
// a hidden, off-screen iframe (confirmed live via DevTools:
// docs-texteventtarget-iframe). Neither of the two click events here is
// intercepted (preventDefault/stopPropagation) — both are left to reach
// Slides' own canvas normally. Live document.activeElement logging around
// the copy operation (see writeClipBundleLogged) has since CONFIRMED this
// focus/restore sequence works correctly end to end (iframe stays focused
// before, during the brief steal, after restore, and through the eventual
// paste) — so focus was a red herring, not the actual remaining bug.
//
// The actual remaining bug found: eagerBundle/eagerError were shared
// mutable state written by whichever conversion promise resolved last,
// with no protection against a second drop starting before the first
// one's conversion (and dangling click-2 listener) had been cleaned up —
// symptoms live matched this exactly (an earlier file's data appearing
// after starting a newer one). Fixed via insertGeneration, which tags each
// beginInsertFlow call and discards/ignores anything from a superseded one.
//
// Diverting a drop away from Slides' own native image-drop handling only
// happens for .svg files — a capture-phase listener on `document`
// structurally fires before any listener Slides has attached to a more
// specific element, regardless of script load order, but non-.svg drops
// are left completely untouched (no preventDefault/stopPropagation) so
// Slides' normal drop handling is unaffected.

// ── Off-screen clipboard-write target ─────────────────────────────────────

let clipTargetEl = null;
function ensureClipTarget() {
  if (clipTargetEl) return clipTargetEl;
  clipTargetEl = document.createElement('div');
  clipTargetEl.setAttribute('contenteditable', 'true');
  clipTargetEl.style.cssText = 'position:fixed; left:-9999px; top:-9999px;';
  clipTargetEl.textContent = 'x';
  document.documentElement.appendChild(clipTargetEl);
  return clipTargetEl;
}

function describeElement(el) {
  if (!el) return String(el);
  const cls = el.className ? '.' + String(el.className).trim().replace(/\s+/g, '.') : '';
  const id = el.id ? '#' + el.id : '';
  const src = el.tagName === 'IFRAME' ? ' src=' + el.src : '';
  return el.tagName + id + cls + src;
}

// Focusing the outer iframe element controls whether keystrokes get routed
// into its browsing context at all, but there's likely a SPECIFIC element
// within the iframe's own document that needs to be focused for paste to
// actually land — same-origin (about:blank on the same top-level origin),
// so we can inspect it directly rather than guessing.
function describeIframeInner(el) {
  if (!el || el.tagName !== 'IFRAME') return '(not an iframe)';
  try {
    const innerDoc = el.contentDocument;
    if (!innerDoc) return '(no contentDocument — cross-origin or not yet loaded)';
    return 'inner activeElement: ' + describeElement(innerDoc.activeElement) +
      ', inner body children: ' + innerDoc.body.children.length +
      ', inner body innerHTML len: ' + innerDoc.body.innerHTML.length;
  } catch (err) {
    return '(threw reading contentDocument: ' + err.message + ')';
  }
}

// Confirmed live: Slides' actual paste target, when paste works (e.g. via
// manual Tab-navigation), is NOT just the outer iframe — it's a specific
// `contenteditable="true" role="textbox"` div INSIDE the iframe's own
// document (aria-label="Document content"). Focusing the outer iframe
// element from the parent page does not cascade down to focus this inner
// element automatically (it was observed sitting on plain BODY instead),
// which is exactly why paste kept failing despite document.activeElement
// looking correct at the outer level. Reaches into the same-origin iframe
// document and focuses it directly.
function focusSlidesTextbox(iframeEl) {
  if (!iframeEl || iframeEl.tagName !== 'IFRAME') return false;
  try {
    const innerDoc = iframeEl.contentDocument;
    if (!innerDoc) return false;
    const textbox = innerDoc.querySelector('[contenteditable="true"][role="textbox"]');
    if (!textbox) return false;
    textbox.focus();
    return true;
  } catch (err) {
    console.warn('[svg2slides] focusSlidesTextbox threw:', err);
    return false;
  }
}

// Deliberately NOT shared.js's writeClipBundle for this diagnostic round —
// same core logic, but with document.activeElement logged at every step so
// we can see directly what's actually focused, instead of guessing.
function writeClipBundleLogged(bundle) {
  const previousActive = document.activeElement;
  console.log('[svg2slides] activeElement BEFORE copy steal:', describeElement(previousActive), '|', describeIframeInner(previousActive));

  const clipTarget = ensureClipTarget();
  let pending = bundle;
  const onCopy = (e) => {
    e.preventDefault();
    if (!pending) return;
    Object.keys(pending).forEach((mime) => e.clipboardData.setData(mime, pending[mime]));
  };
  clipTarget.addEventListener('copy', onCopy);

  clipTarget.focus();
  const range = document.createRange();
  range.selectNodeContents(clipTarget);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
  const ok = document.execCommand('copy');

  clipTarget.removeEventListener('copy', onCopy);
  pending = null;

  console.log('[svg2slides] execCommand("copy") returned', ok, '— activeElement right after (pre-restore):', describeElement(document.activeElement));

  // Clear the selection we made over clipTarget — document.activeElement
  // was the only thing being restored before, but window.getSelection()
  // was left dangling on our hidden off-screen div even after focus moved
  // back to Slides' iframe. If Slides' paste logic consults the current
  // selection (not just activeElement) to decide where/whether to paste,
  // a stale selection on an unrelated invisible element would explain
  // paste silently failing despite focus looking correct.
  sel.removeAllRanges();

  if (previousActive && typeof previousActive.focus === 'function' && previousActive !== document.body) {
    previousActive.focus();
  }

  // Restoring the outer iframe's focus alone leaves its inner document
  // sitting on plain BODY, not Slides' actual text-input target — focus
  // that specific element directly (see focusSlidesTextbox above).
  const textboxFocused = focusSlidesTextbox(previousActive);

  console.log(
    '[svg2slides] activeElement immediately after restore attempt:', describeElement(document.activeElement),
    '— selection range count:', window.getSelection().rangeCount,
    '— inner textbox focus succeeded?', textboxFocused,
    '|', describeIframeInner(document.activeElement)
  );

  setTimeout(() => {
    console.log('[svg2slides] activeElement +50ms (after this click event has fully finished dispatching):', describeElement(document.activeElement), '|', describeIframeInner(document.activeElement));
  }, 50);
  setTimeout(() => {
    console.log('[svg2slides] activeElement +500ms:', describeElement(document.activeElement), '|', describeIframeInner(document.activeElement));
  }, 500);

  return ok;
}

function setGlobalCursor(cursor) {
  document.documentElement.style.cursor = cursor || '';
}

function isMac() {
  return /Mac|iPod|iPhone|iPad/.test(navigator.platform || navigator.userAgent || '');
}
function pasteKeyLabel() {
  return isMac() ? '⌘ + V' : 'Ctrl + V';
}

// ── Minimal graphical cues ──────────────────────────────────────────────
// Layered back in after confirming the earlier paste failures were a real
// missing-focus bug (see focusSlidesTextbox), not DOM-insertion
// interference — so it's safe to have visible elements again. Styled per
// a user-provided mockup: bold black/white "HUD" pills, a green "+" badge
// mimicking a native copy-cursor decoration, and the ghost dimming further
// (50% -> 33% opacity) once placed. Two pieces:
//  - A ghost preview + badge + "Double Click to Place" label while
//    following the mouse; the label hides once placed (waiting on the
//    second/copy click), leaving just the dimmed ghost + badge.
//  - A "⌘/Ctrl + V to Confirm" pill once copy succeeds — a real visible
//    element rather than relying on the 'wait' cursor, which becomes
//    unreliable once Slides sets its own cursor styling on the canvas/
//    shapes after a paste (that styling overrides a page-level
//    documentElement cursor for anything nested under it).

let ghostEl = null;
let ghostMoveHandler = null;
let ghostObjectUrl = null;

// Shared "HUD" look for both text prompts (the placement label and the
// final insert tooltip) — bold white-on-black pill, matching the user's
// mockup exactly rather than the smaller white card tried before.
const _HUD_CSS = `
  background: #1a1a1a; color: #fff; padding: 10px 20px; border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.35); font-size: 15px; font-weight: 800;
  white-space: nowrap; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
`;

function createGhost(file, startX, startY) {
  removeGhost();
  const size = 56; // px — deliberately small, "system-seeming" not showy
  ghostObjectUrl = URL.createObjectURL(file);
  ghostEl = document.createElement('div');
  ghostEl.id = 'svg2slides-ghost';
  ghostEl.innerHTML = `
    <style>
      #svg2slides-ghost {
        position: fixed; z-index: 2147483000; pointer-events: none;
        width: ${size}px; height: ${size}px; opacity: 0.5;
        transition: opacity .15s;
      }
      #svg2slides-ghost.placed { opacity: 0.33; }
      #svg2slides-ghost img { width: 100%; height: 100%; object-fit: contain; }
      #svg2slides-ghost .badge {
        position: absolute; right: -6px; bottom: -6px; width: 20px; height: 20px;
        border-radius: 50%; background: #34c759; color: #fff;
        display: flex; align-items: center; justify-content: center;
        font-size: 15px; font-weight: 700; line-height: 1; font-family: -apple-system, sans-serif;
        box-shadow: 0 1px 4px rgba(0,0,0,0.3);
      }
      #svg2slides-ghost .label {
        position: absolute; left: 50%; top: calc(100% + 10px); transform: translateX(-50%);
        ${_HUD_CSS}
      }
    </style>
    <img src="${ghostObjectUrl}" alt="">
    <span class="badge">+</span>
    <span class="label">Double Click to Place</span>
  `;
  document.documentElement.appendChild(ghostEl);
  positionGhost(startX, startY);

  ghostMoveHandler = (e) => positionGhost(e.clientX, e.clientY);
  document.addEventListener('mousemove', ghostMoveHandler);
}

function positionGhost(x, y) {
  if (!ghostEl) return;
  const size = 56;
  ghostEl.style.left = (x - size / 2) + 'px';
  ghostEl.style.top = (y - size / 2) + 'px';
}

function freezeGhost() {
  if (ghostMoveHandler) { document.removeEventListener('mousemove', ghostMoveHandler); ghostMoveHandler = null; }
  if (ghostEl) {
    ghostEl.classList.add('placed'); // dims further (0.5 -> 0.33), per mockup
    // "Double Click to Place" no longer applies once it's been placed and
    // is waiting on the second (copy) click — hide rather than leave it stale.
    const label = ghostEl.querySelector('.label');
    if (label) label.style.display = 'none';
  }
}

function removeGhost() {
  freezeGhost();
  if (ghostEl) { ghostEl.remove(); ghostEl = null; }
  if (ghostObjectUrl) { URL.revokeObjectURL(ghostObjectUrl); ghostObjectUrl = null; }
}

let insertTooltipEl = null;
function showInsertTooltip(x, y) {
  removeInsertTooltip();
  insertTooltipEl = document.createElement('div');
  insertTooltipEl.id = 'svg2slides-insert-tooltip';
  insertTooltipEl.innerHTML = `
    <style>
      #svg2slides-insert-tooltip {
        position: fixed; z-index: 2147483000; transform: translate(-50%, -100%);
        ${_HUD_CSS}
      }
    </style>
  `;
  insertTooltipEl.append(pasteKeyLabel() + ' to Confirm');
  insertTooltipEl.style.left = x + 'px';
  insertTooltipEl.style.top = (y - 16) + 'px';
  document.documentElement.appendChild(insertTooltipEl);
}
function removeInsertTooltip() {
  if (insertTooltipEl) { insertTooltipEl.remove(); insertTooltipEl = null; }
}

// Small plain error toast — used only for the >25-files case below.
function showErrorToast(msg) {
  const el = document.createElement('div');
  el.innerHTML = `
    <style>
      .svg2slides-error-toast {
        position: fixed; right: 20px; bottom: 20px; z-index: 2147483000;
        background: #202124; color: #fff; padding: 10px 14px; border-radius: 8px;
        font-size: 13px; max-width: 280px; box-shadow: 0 2px 12px rgba(0,0,0,0.3);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      }
    </style>
  `;
  el.className = 'svg2slides-error-toast';
  el.append(msg);
  document.documentElement.appendChild(el);
  setTimeout(() => el.remove(), 6000);
}

// ── Bundle position shift ──────────────────────────────────────────────────
// Shifts every shape entry's baked x/y by a delta expressed in points,
// converted to the same "Slides-internal unit" the bundle's coordinates
// are already in. Mirrors slides_clip.py's own constants exactly
// (_PT_TO_EMU=12700, EMU_PER_UNIT=30) — see cloud/slides_clip.py's
// _build_shape_entry: shape entries are `[3, id, 1, [1,0,0,1,x,y], props]`,
// group entries are `[2, id, [childIds], [1,0,0,1,0,0]]` (identity
// transform — their children already carry absolute positions, so groups
// themselves need no shift).
const _PT_TO_EMU = 12700;
const _EMU_PER_UNIT = 30;
const _CLIP_MIME = 'application/x-vnd.google-docs-drawings-object+wrapped';

function shiftBundlePosition(bundle, deltaXPt, deltaYPt) {
  const dxUnit = Math.round((deltaXPt * _PT_TO_EMU) / _EMU_PER_UNIT);
  const dyUnit = Math.round((deltaYPt * _PT_TO_EMU) / _EMU_PER_UNIT);

  const wrapper = JSON.parse(bundle[_CLIP_MIME]);
  const data = JSON.parse(wrapper.data);
  data.resolved.forEach((entry) => {
    if (entry[0] === 3) { // shape entry: [3, id, 1, [1,0,0,1,x,y], props]
      entry[3][4] += dxUnit;
      entry[3][5] += dyUnit;
    }
  });
  wrapper.data = JSON.stringify(data);
  return { [_CLIP_MIME]: JSON.stringify(wrapper) };
}

function convertViaServer(files, placement) {
  return readFilesAsBase64(files).then((payload) => {
    return fetch(BACKEND + '/insert-svg-clip-at', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ files: payload, ...placement }),
    });
  }).then(async (res) => {
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || 'Server error');
    return json.clip;
  });
}

// ── Main flow: two clicks, zero DOM elements, cursor-only feedback ────────
// Click 1 places (starts eager conversion, no gesture needed for that).
// Click 2, once ready, triggers the actual copy — kept as a genuinely
// separate click (not collapsed into click 1) specifically so
// execCommand('copy') always runs inside a fresh, real, synchronous click
// handler with the bundle already resolved, which is the one pattern this
// session has clear evidence for (as opposed to calling it from inside a
// conversion promise's .then(), confirmed broken twice).

let pendingMousedownHandler = null;
let pendingSecondClickHandler = null;
let eagerBundle = null;
let eagerError = null;
let placeholderPlacement = null;

// Bumped on every beginInsertFlow call; each call captures its own value
// and checks it before ever writing to the shared eagerBundle/eagerError
// state. Without this, dropping a second file before the first one's
// conversion resolves left BOTH conversions racing to set the same shared
// variable — whichever finished later won, regardless of which file the
// user actually meant, which is exactly the "pasted the earlier file"
// symptom reported live.
let insertGeneration = 0;

function beginInsertFlow(files, startX, startY) {
  console.log('[svg2slides] beginInsertFlow, isPyodideReady() =', isPyodideReady());
  const myGeneration = ++insertGeneration;

  if (pendingMousedownHandler) {
    document.removeEventListener('mousedown', pendingMousedownHandler, true);
    pendingMousedownHandler = null;
  }
  if (pendingSecondClickHandler) {
    document.removeEventListener('mousedown', pendingSecondClickHandler, true);
    pendingSecondClickHandler = null;
  }
  if (pendingPasteCleanup) {
    // Cancels any still-armed paste-detection listener/timer from an
    // unfinished previous flow (e.g. its 30s timeout hadn't fired yet) —
    // otherwise multiple armPasteDetection instances can pile up across
    // successive drops, each still listening/ticking down independently.
    pendingPasteCleanup();
  }
  removeGhost();
  removeInsertTooltip();
  eagerBundle = null;
  eagerError = null;

  createGhost(files[0], startX, startY);

  // Eager conversion at a fixed placeholder position — box_w_pt/box_h_pt
  // don't depend on where the user ends up clicking, only x_pt/y_pt do,
  // and those get shifted synchronously once the real click position is
  // known (see shiftBundlePosition above).
  placeholderPlacement = {
    x_pt: ASSUMED_SLIDE_W_PT / 2,
    y_pt: ASSUMED_SLIDE_H_PT / 2,
    box_w_pt: ASSUMED_SLIDE_W_PT * INSERT_FIT_FRACTION,
    box_h_pt: ASSUMED_SLIDE_H_PT * INSERT_FIT_FRACTION,
  };
  const convert = isPyodideReady()
    ? convertViaPyodide(files, placeholderPlacement)
    : convertViaServer(files, placeholderPlacement);
  convert.then((b) => {
    if (myGeneration !== insertGeneration) {
      console.log('[svg2slides] conversion for a superseded drop resolved — discarding');
      return;
    }
    eagerBundle = b;
  }).catch((err) => {
    if (myGeneration !== insertGeneration) return;
    eagerError = err;
  });

  setGlobalCursor('grabbing');

  pendingMousedownHandler = (e) => {
    document.removeEventListener('mousedown', pendingMousedownHandler, true);
    pendingMousedownHandler = null;
    console.log('[svg2slides] click 1 (placement) fired at', e.clientX, e.clientY, '— activeElement:', describeElement(document.activeElement));
    // Not intercepted: letting this reach Slides' own canvas is what lets
    // its own bubble-phase click handling focus its hidden iframe.
    freezeGhost();
    setGlobalCursor('grab'); // brief "click registered" cue, purely cosmetic
    const placement = estimatePlacement(e.clientX, e.clientY, window.innerWidth, window.innerHeight);
    const deltaXPt = placement.x_pt - placeholderPlacement.x_pt;
    const deltaYPt = placement.y_pt - placeholderPlacement.y_pt;

    setTimeout(() => {
      console.log('[svg2slides] activeElement 50ms after click 1 (post-dispatch):', describeElement(document.activeElement));
    }, 50);

    // Arms the actual click-2 listener immediately (no functional delay) —
    // only the cosmetic cursor transition below is deferred, so the brief
    // 'grab' flash is actually visible rather than instantly overwritten.
    armSecondClick(myGeneration, deltaXPt, deltaYPt);
    setTimeout(() => setGlobalCursor('progress'), 150);
  };
  document.addEventListener('mousedown', pendingMousedownHandler, true);
}

function armSecondClick(myGeneration, deltaXPt, deltaYPt) {
  const onSecondClick = (e) => {
    document.removeEventListener('mousedown', onSecondClick, true);
    pendingSecondClickHandler = null;

    if (myGeneration !== insertGeneration) {
      console.log('[svg2slides] click 2 fired for a superseded drop — ignoring');
      return;
    }

    console.log('[svg2slides] click 2 (copy) fired at', e.clientX, e.clientY, '— activeElement before:', describeElement(document.activeElement), '— eagerBundle ready?', !!eagerBundle);

    if (!eagerBundle) {
      console.log('[svg2slides] eagerBundle not ready yet at click 2 — this click is wasted; try again shortly');
      // Re-arm so the next click still works once conversion finishes.
      pendingSecondClickHandler = onSecondClick;
      document.addEventListener('mousedown', onSecondClick, true);
      return;
    }

    const bundle = shiftBundlePosition(eagerBundle, deltaXPt, deltaYPt);
    const ok = writeClipBundleLogged(bundle);
    setGlobalCursor('');
    removeGhost();
    if (ok) {
      showInsertTooltip(e.clientX, e.clientY);
      // document.activeElement is the iframe again by now (writeClipBundleLogged
      // restores it) — pass it through so paste-detection can listen on its
      // own inner document too, not just the top-level one.
      armPasteDetection(document.activeElement);
    }
  };
  pendingSecondClickHandler = onSecondClick;
  document.addEventListener('mousedown', onSecondClick, true);
}

// Arms a one-time listener for the actual paste completing, as the signal
// to reset the cursor right away instead of always waiting out the full
// timeout. A listener on the top-level `document` alone never actually
// caught this: paste lands inside docs-texteventtarget-iframe's own
// contenteditable, and events don't cross an iframe boundary via bubbling
// — every prior "gave up after 30s timeout" log, including on inserts that
// visibly worked, was this exact gap. Listens on the iframe's own
// same-origin contentDocument too, not just the top-level one.
let pendingPasteCleanup = null;

function armPasteDetection(iframeEl) {
  if (pendingPasteCleanup) pendingPasteCleanup();

  const startedAt = Date.now();
  const onPaste = () => cleanup(true);
  const timer = setTimeout(() => cleanup(false), 30000);

  let innerDoc = null;
  if (iframeEl && iframeEl.tagName === 'IFRAME') {
    try { innerDoc = iframeEl.contentDocument; } catch { innerDoc = null; }
  }

  function cleanup(actuallyPasted) {
    document.removeEventListener('paste', onPaste, true);
    if (innerDoc) innerDoc.removeEventListener('paste', onPaste, true);
    clearTimeout(timer);
    console.log(
      '[svg2slides]', actuallyPasted ? 'paste EVENT detected' : 'gave up after 30s timeout (no paste event seen)',
      Math.round((Date.now() - startedAt) / 1000) + 's after copy — activeElement:', describeElement(document.activeElement)
    );
    setGlobalCursor('');
    removeInsertTooltip();
    pendingPasteCleanup = null;
  }

  document.addEventListener('paste', onPaste, true);
  if (innerDoc) innerDoc.addEventListener('paste', onPaste, true);
  pendingPasteCleanup = cleanup;
}

// Cancel a pending (not-yet-placed) insert with Escape.
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && pendingMousedownHandler) {
    document.removeEventListener('mousedown', pendingMousedownHandler, true);
    pendingMousedownHandler = null;
    setGlobalCursor('');
    removeGhost();
  }
}, true);

// ── Drop interception ─────────────────────────────────────────────────────
// Capture phase + document-level: structurally fires before any listener
// Slides has attached to a more specific element, so this claims .svg drops
// ahead of Slides' own native image-drop handler. Non-.svg drops are left
// completely untouched — no preventDefault, no stopPropagation — so Slides'
// normal drop handling (images, etc.) is unaffected.

document.addEventListener('dragover', (e) => {
  e.preventDefault(); // required to permit dropping at all; harmless no-op if Slides already does this itself
}, { capture: true });

const MAX_INSERT_FILES = 25; // grid layout is only reasonable up to this many at once — matches cloud/main.py's MAX_INSERT_FILES

document.addEventListener('drop', (e) => {
  const dropped = Array.from((e.dataTransfer && e.dataTransfer.files) || []);
  console.log('[svg2slides] drop event fired, files:', dropped.map((f) => f.name));
  const svgFiles = dropped.filter((f) => f.name.toLowerCase().endsWith('.svg'));
  if (!svgFiles.length) {
    console.log('[svg2slides] no .svg in this drop — leaving it for Slides');
    return;
  }

  e.preventDefault();
  e.stopPropagation();

  if (svgFiles.length > MAX_INSERT_FILES) {
    showErrorToast(`Too many files at once (max ${MAX_INSERT_FILES}) — use the bulk uploader at svgslid.es instead.`);
    return;
  }

  beginInsertFlow(svgFiles, e.clientX, e.clientY);
}, { capture: true });

// NOTE: the floating "Insert SVG" button and the "graphical guides"
// on/off toggle (plus its pro-tip toast) have been pulled for now at the
// user's request while the core drop -> place -> paste flow itself was
// still being debugged. Drag-and-drop is the only entry point until those
// come back.
