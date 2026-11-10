/**
 * Apply the brand style sheet to tagged text boxes, by role.
 *
 * Setup: add this file to the same Apps Script project as sync_copy.gs
 * (messaging sheet > Extensions > Apps Script). Set STYLE_SHEET_URL below
 * to your copy of the brand style sheet. Reload the sheet: Collateral > Apply style.
 *
 * How it works: each row on the Messages tab has a Key and a Role (headline, body,
 * stat...). Each text box in an asset carries slot:<key> in its alt text. The script
 * looks up the role's font, weight, size and colour on the style sheet's Type and
 * Colors tabs and sets them on the box. Size comes from "Print pt" or "Deck pt",
 * chosen by the Kind column on the Assets tab.
 * It never changes text, position or size of a box.
 */
const STYLE_SHEET_URL = 'PASTE THE URL OF YOUR BRAND STYLE SHEET HERE';

function applyStyle() {
  const ss = SpreadsheetApp.getActive();
  const style = SpreadsheetApp.openByUrl(STYLE_SHEET_URL);
  const colors = {};
  style.getSheetByName('Colors').getDataRange().getValues().slice(1).forEach(function (r) {
    if (r[0]) colors[String(r[0])] = String(r[1]);
  });
  const type = {};
  style.getSheetByName('Type').getDataRange().getValues().slice(1).forEach(function (r) {
    if (r[0]) type[String(r[0])] = { font: String(r[1]), bold: String(r[2]).toLowerCase() !== 'regular', print: Number(r[3]), deck: Number(r[4]), color: colors[String(r[6])] };
  });
  const msg = ss.getSheetByName('Messages').getDataRange().getValues();
  const head = msg[0].map(function (h) { return String(h).trim().toLowerCase(); });
  const k = head.indexOf('key'), ro = head.indexOf('role');
  if (k < 0 || ro < 0) throw new Error('Messages tab needs Key and Role columns.');
  const roles = {};
  msg.slice(1).forEach(function (r) { if (r[k]) roles[String(r[k])] = String(r[ro]); });

  const assets = ss.getSheetByName('Assets').getDataRange().getValues();
  for (let r = 1; r < assets.length; r++) {
    const url = String(assets[r][1]);
    if (assets[r][2] !== true || !url) continue;
    const kind = String(assets[r][6] || 'print').toLowerCase() === 'deck' ? 'deck' : 'print';
    const id = (url.match(/\/d\/([\w-]+)/) || [])[1] || url;
    const deck = SlidesApp.openById(id);
    let n = 0;
    deck.getSlides().forEach(function (slide) {
      slide.getPageElements().forEach(function (el) {
        if (el.getPageElementType() !== SlidesApp.PageElementType.SHAPE) return;
        const tag = ((el.getTitle() || '') + ' ' + (el.getDescription() || '')).match(/slot:([a-z0-9_]+)/i);
        if (!tag) return;
        const t = type[roles[tag[1]]];
        if (!t) return;
        const ts = el.asShape().getText().getTextStyle();
        ts.setFontFamily(t.font).setBold(t.bold).setFontSize(t[kind]);
        if (t.color) ts.setForegroundColor(t.color);
        n++;
      });
    });
    deck.saveAndClose();
    ss.getSheetByName('Assets').getRange(r + 1, 6).setValue('Style applied to ' + n + ' boxes');
  }
}
