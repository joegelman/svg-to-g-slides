/**
 * Sync copy: push approved lines from the messaging sheet into tagged text boxes.
 *
 * Setup (once): open the messaging sheet, Extensions > Apps Script, paste this file,
 * save, reload the sheet. "Collateral" and "Workshop" menus appear. This file owns onOpen;
 * add apply_style.gs and workshop_form.gs as extra files in the same project. The first run asks for
 * permission to edit your Slides files.
 *
 * How it finds a text box: alt text. Right-click a text box in Slides > Alt text,
 * and put slot:<key> in the Title (or Description), for example slot:headline.
 * <key> must match the Key column on the Messages tab.
 *
 * Rules:
 *  - Only the "Approved line" column is written. Drafts never reach an asset.
 *  - A line longer than its budget is skipped and flagged, never squeezed in.
 *  - Text boxes without a slot tag are never touched.
 */
const MESSAGES = 'Messages';
const ASSETS = 'Assets';

function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Collateral')
    .addItem('Dry run (report only)', 'dryRun')
    .addItem('Sync copy to assets', 'syncCopy')
    .addItem('Apply style (needs apply_style.gs)', 'applyStyle')
    .addToUi();
  ui.createMenu('Workshop')
    .addItem('Build the form (needs workshop_form.gs)', 'buildWorkshopForm')
    .addToUi();
}

function dryRun() { run_(true); }
function syncCopy() { run_(false); }

function readMessages_(ss) {
  const rows = ss.getSheetByName(MESSAGES).getDataRange().getValues();
  const head = rows[0].map(function (h) { return String(h).trim().toLowerCase(); });
  const col = function (name) {
    const i = head.indexOf(name);
    if (i < 0) throw new Error('Messages tab is missing the column: ' + name);
    return i;
  };
  const k = col('key'), l = col('approved line'), b = col('budget');
  const out = {};
  rows.slice(1).forEach(function (r) {
    const key = String(r[k]).trim();
    if (key) out[key] = { line: String(r[l]).trim(), budget: Number(r[b]) || 0 };
  });
  return out;
}

function run_(dry) {
  const ss = SpreadsheetApp.getActive();
  const msgs = readMessages_(ss);
  const sh = ss.getSheetByName(ASSETS);
  const rows = sh.getDataRange().getValues();
  for (let r = 1; r < rows.length; r++) {
    const url = String(rows[r][1]);
    if (rows[r][2] !== true || !url) continue;
    const id = (url.match(/\/d\/([\w-]+)/) || [])[1] || url;
    const out = { changed: 0, flags: [] };
    try {
      const deck = SlidesApp.openById(id);
      deck.getSlides().forEach(function (slide, i) {
        walk_(slide.getPageElements(), msgs, dry, out, i + 1);
      });
      if (!dry) deck.saveAndClose();
    } catch (e) {
      out.flags.push('Could not open: ' + e.message);
    }
    const stamp = Utilities.formatDate(new Date(), ss.getSpreadsheetTimeZone(), 'yyyy-MM-dd HH:mm');
    sh.getRange(r + 1, 4, 1, 3).setValues([[
      (dry ? 'Dry run ' : '') + stamp,
      out.changed,
      out.flags.join('\n') || 'None'
    ]]);
  }
}

function walk_(elements, msgs, dry, out, slideNo) {
  elements.forEach(function (el) {
    const type = el.getPageElementType();
    if (type === SlidesApp.PageElementType.GROUP) {
      walk_(el.asGroup().getChildren(), msgs, dry, out, slideNo);
      return;
    }
    if (type !== SlidesApp.PageElementType.SHAPE) return;
    const tag = ((el.getTitle() || '') + ' ' + (el.getDescription() || '')).match(/slot:([a-z0-9_]+)/i);
    if (!tag) return;
    const key = tag[1];
    const m = msgs[key];
    if (!m) { out.flags.push('Page ' + slideNo + ': no row for slot:' + key); return; }
    if (!m.line) { out.flags.push('Page ' + slideNo + ': ' + key + ' has no approved line'); return; }
    if (m.budget && m.line.length > m.budget) {
      out.flags.push('Page ' + slideNo + ': ' + key + ' is ' + (m.line.length - m.budget) + ' over budget, skipped');
      return;
    }
    const text = el.asShape().getText();
    if (text.asString().replace(/\n$/, '') === m.line) return;
    if (!dry) text.setText(m.line);
    out.changed++;
  });
}
