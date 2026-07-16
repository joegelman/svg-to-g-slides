// ── Config ────────────────────────────────────────────────────────────────────
var BACKEND_URL = 'https://svg-to-slides-jwxfsrfexq-uc.a.run.app';

// ── Add-on lifecycle ──────────────────────────────────────────────────────────

function onOpen(e) {
  try {
    SlidesApp.getUi()
      .createAddonMenu()
      .addItem('Insert SVG…', 'showInsertDialog')
      .addToUi();
  } catch (_) {}
}

function onInstall(e) { onOpen(e); }

// ── UI ────────────────────────────────────────────────────────────────────────

function showInsertDialog() {
  var html = HtmlService.createHtmlOutputFromFile('Dialog')
    .setWidth(440)
    .setHeight(380);
  SlidesApp.getUi().showModalDialog(html, 'Insert SVG');
}

// ── Convert on backend, return the Slides clipboard payload ──────────────────
//
// No Drive/Slides API call happens anywhere in this flow — the backend builds
// Google Slides' own internal clipboard format directly (see
// cloud/slides_clip.py), and Dialog.html's client-side JS writes it to the OS
// clipboard for the user to paste with Cmd/Ctrl+V. This is why the add-on no
// longer needs the `presentations` OAuth scope: getPageWidth()/getPageHeight()
// below only touch the presentation this script is bound to, which only
// requires `presentations.currentonly`.

function fetchClipFromBackend(filesPayload) {
  var pres          = SlidesApp.getActivePresentation();
  var slideWidthPt  = pres.getPageWidth();
  var slideHeightPt = pres.getPageHeight();

  var response = UrlFetchApp.fetch(BACKEND_URL + '/insert-svg-clip', {
    method:             'post',
    contentType:        'application/json',
    payload:            JSON.stringify({
      files:            filesPayload,
      slide_width_pt:   slideWidthPt,
      slide_height_pt:  slideHeightPt
    }),
    muteHttpExceptions: true
  });

  if (response.getResponseCode() !== 200) {
    throw new Error('Backend error ' + response.getResponseCode() + ': ' +
                    response.getContentText());
  }

  return JSON.parse(response.getContentText()).clip;
}
