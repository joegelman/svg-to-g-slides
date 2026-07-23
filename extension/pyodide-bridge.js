// Loaded after pyodide/pyodide.js (defines the global `loadPyodide`) and
// shared.js, before content.js — see manifest.json's content_scripts.js.
//
// Runs the actual, unmodified svg_to_slides.py + slides_clip.py in Pyodide
// (Python-in-WASM), entirely locally — no network call. This is what makes
// a fully-automatic drop -> convert -> copy possible: execCommand('copy')
// only succeeds inside a fresh, synchronous-enough user gesture, and this
// session proved a network round-trip breaks that gesture window while a
// local file read + a Pyodide call does not (confirmed via the standalone
// browser-convert-test.html harness in the repo root before wiring this in
// for real). The one thing that harness couldn't test — since it ran in a
// plain unrestricted page — is whether WASM instantiation from inside a
// content script actually works the same way once injected into Slides'
// own page. That's what actually loading this in Chrome will tell us.
//
// Pyodide's own init takes a few seconds, so it's kicked off immediately
// below rather than waited on lazily — by the time a user actually drops a
// file (well after page load), it should already be warm. If it isn't
// ready yet, or failed to init at all (e.g. blocked by Slides' CSP),
// isPyodideReady() reports false and content.js falls back to the
// original server-conversion + manual-Copy-click flow — nothing breaks,
// it just doesn't get the zero-click upgrade for that one drop.

console.log('[svg2slides] pyodide-bridge.js loaded, starting Pyodide init…');

let _pyodideInstance = null;
let _pyodideReadyPromise = null;

function initPyodideOnce() {
  if (_pyodideReadyPromise) return _pyodideReadyPromise;

  _pyodideReadyPromise = (async () => {
    const pyodide = await loadPyodide({ indexURL: chrome.runtime.getURL('pyodide/') });

    // svg_to_slides.py imports python-pptx and lxml at module scope purely
    // for its (unused-by-us) PPTX-generation code path — collect()/
    // expand_path()/extract_gradients()/normalize_arcs() never touch
    // either (verified by reading the source). Stubbing both as fake
    // modules lets the real, unmodified file import cleanly under Pyodide
    // with zero source changes, rather than hand-porting/duplicating any
    // of the already-proven parsing/path logic.
    pyodide.runPython(`
import sys, types
fake_pptx = types.ModuleType('pptx')
fake_pptx.Presentation = object
fake_pptx_util = types.ModuleType('pptx.util')
fake_pptx_util.Emu = object
fake_pptx.util = fake_pptx_util
sys.modules['pptx'] = fake_pptx
sys.modules['pptx.util'] = fake_pptx_util

fake_lxml = types.ModuleType('lxml')
fake_lxml_etree = types.ModuleType('lxml.etree')
fake_lxml.etree = fake_lxml_etree
sys.modules['lxml'] = fake_lxml
sys.modules['lxml.etree'] = fake_lxml_etree
    `);

    const [svgToSlidesSrc, slidesClipSrc] = await Promise.all([
      fetch(chrome.runtime.getURL('svg_to_slides.py')).then((r) => r.text()),
      fetch(chrome.runtime.getURL('slides_clip.py')).then((r) => r.text()),
    ]);
    pyodide.FS.writeFile('/svg_to_slides.py', svgToSlidesSrc);
    pyodide.FS.writeFile('/slides_clip.py', slidesClipSrc);
    pyodide.runPython(`
import sys
sys.path.insert(0, '/')
import slides_clip
    `);

    _pyodideInstance = pyodide;
    console.log('[svg2slides] Pyodide ready');
    return pyodide;
  })();

  _pyodideReadyPromise.catch((err) => {
    console.warn('[svg2slides] Pyodide init failed — falling back to server conversion for this session:', err);
  });

  return _pyodideReadyPromise;
}

function isPyodideReady() {
  return !!_pyodideInstance;
}

// files: array of File objects (already filtered to .svg). placement: same
// {x_pt, y_pt, box_w_pt, box_h_pt} shape /insert-svg-clip-at takes. Throws
// if Pyodide isn't ready — callers must check isPyodideReady() first.
async function convertViaPyodide(files, placement) {
  if (!_pyodideInstance) throw new Error('Pyodide not ready');
  const pyodide = _pyodideInstance;

  const sources = [];
  for (const f of files) {
    const buf = await f.arrayBuffer();
    sources.push([f.name, Array.from(new Uint8Array(buf))]);
  }

  pyodide.globals.set('_sources_raw', sources);
  pyodide.globals.set('_x_pt', placement.x_pt);
  pyodide.globals.set('_y_pt', placement.y_pt);
  pyodide.globals.set('_box_w_pt', placement.box_w_pt);
  pyodide.globals.set('_box_h_pt', placement.box_h_pt);

  const clipJson = pyodide.runPython(`
import json
sources = [(name, bytes(b)) for name, b in _sources_raw.to_py()]
bundle = slides_clip.build_clip_bundle_at(sources, _x_pt, _y_pt, _box_w_pt, _box_h_pt)
json.dumps(bundle)
  `);
  return JSON.parse(clipJson);
}

initPyodideOnce();
