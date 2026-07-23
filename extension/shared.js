// Loaded before content.js — see manifest.json's content_scripts.js.

if (typeof console !== 'undefined') console.log('[svg2slides] shared.js loaded');

const BACKEND = 'https://svg-to-slides-jwxfsrfexq-uc.a.run.app';

function readFilesAsBase64(files) {
  return Promise.all(files.map((file) => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve({ name: file.name, data: e.target.result.split(',')[1] });
    reader.onerror = () => reject(new Error('Could not read ' + file.name));
    reader.readAsDataURL(file);
  })));
}

// ── Cursor/size estimation, no Slides DOM reverse-engineering, no Slides
// API, no Google scope of any kind. Deliberately approximate in two ways:
// position is a fraction-of-assumed-canvas mapped onto an assumed-default
// slide size, which works regardless of real zoom; size is a fraction of
// that same assumed slide size rather than the SVG's own "true" size,
// which is a bad default regardless of measurement precision (a tiny icon
// would paste as a speck, a huge logo would blow past the slide).

const ASSUMED_TOP_CHROME_PX = 120;   // menu bar + toolbar, Slides' default layout
const ASSUMED_LEFT_CHROME_PX = 200;  // filmstrip sidebar, Slides' default layout
const ASSUMED_SLIDE_W_PT = 960;      // Slides' current default "Widescreen" 16:9
const ASSUMED_SLIDE_H_PT = 540;
const INSERT_FIT_FRACTION = 0.2;     // ~20% of the assumed slide size

function estimatePlacement(clientX, clientY, windowWidth, windowHeight) {
  const estCanvasWidth = Math.max(windowWidth - ASSUMED_LEFT_CHROME_PX, 100);
  const estCanvasHeight = Math.max(windowHeight - ASSUMED_TOP_CHROME_PX, 100);

  let fx = 0.5, fy = 0.5; // dead-center fallback if position is unknown/outside the estimated canvas
  if (clientX != null && clientY != null) {
    const rawFx = (clientX - ASSUMED_LEFT_CHROME_PX) / estCanvasWidth;
    const rawFy = (clientY - ASSUMED_TOP_CHROME_PX) / estCanvasHeight;
    if (rawFx >= 0 && rawFx <= 1 && rawFy >= 0 && rawFy <= 1) {
      fx = rawFx; fy = rawFy;
    }
  }

  return {
    x_pt: fx * ASSUMED_SLIDE_W_PT,
    y_pt: fy * ASSUMED_SLIDE_H_PT,
    box_w_pt: ASSUMED_SLIDE_W_PT * INSERT_FIT_FRACTION,
    box_h_pt: ASSUMED_SLIDE_H_PT * INSERT_FIT_FRACTION,
  };
}
