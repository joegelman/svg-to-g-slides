// ── Config ────────────────────────────────────────────────────────────────────
var BACKEND_URL = 'https://svg-to-slides-jwxfsrfexq-uc.a.run.app';

// ── Add-on lifecycle ──────────────────────────────────────────────────────────

function onOpen(e) {
  try {
    SlidesApp.getUi()
      .createAddonMenu()
      .addItem('Insert SVGs', 'showInsertDialog')
      .addToUi();
  } catch (_) {}
}

function onInstall(e) { onOpen(e); }

// Toolbar icon (uses addOns.common.logoUrl from appsscript.json) — shows a
// single-button card so the dialog is reachable in one click from the
// sidebar icon, instead of only via Extensions > SVG Slides > Insert SVGs
function onHomepage(e) {
  var button = CardService.newTextButton()
    .setText('Insert SVGs')
    .setOnClickAction(CardService.newAction().setFunctionName('showInsertDialogFromCard'));

  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle('SVG Slides'))
    .addSection(CardService.newCardSection().addWidget(button))
    .build();
}

function showInsertDialogFromCard(e) {
  showInsertDialog();
  return CardService.newActionResponseBuilder().build();
}

// ── UI ────────────────────────────────────────────────────────────────────────

function showInsertDialog() {
  var html = HtmlService.createHtmlOutputFromFile('Dialog')
    .setWidth(480)
    .setHeight(460);
  SlidesApp.getUi().showModalDialog(html, 'Insert SVGs');
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
