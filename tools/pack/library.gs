/**
 * Shape library: icons and UI mockups live in master decks, one item per slide.
 * Asset decks pull shapes from there. Add this file to the same project as sync_copy.gs.
 *
 * Library slide: every element titled lib:<name> is the item. A small white text box
 * titled lib-label holds the name and keywords, so Ctrl+F in the library finds it.
 * Asset deck: a shape titled icon:<key> is an icon slot (Icons tab maps key to name,
 * colour token and size). A shape titled ui:<name> is a mockup slot (uses lib:ui-<name>).
 *
 * Collateral > Place icons and UIs: replaces each slot with the library item.
 * Collateral > Add to library: copies the slides of a converted deck into a library.
 */
const ICON_LIBRARY_URL = 'https://docs.google.com/presentation/d/1aiPHjI3cdyQO8QnRu5GYpR2mLv0aFSCbSKramv4vOc0/edit';
const UI_LIBRARY_URL = 'https://docs.google.com/presentation/d/1PXa6UyYlUmmOuVKfwG31Q9cTOVepx12RvStoABeY_8Q/edit';

function deckId_(url) { return (String(url).match(/\/d\/([\w-]+)/) || [])[1] || String(url); }

function box_(els) {
  let l = Infinity, t = Infinity, r = -Infinity, b = -Infinity;
  els.forEach(function (e) {
    l = Math.min(l, e.getLeft()); t = Math.min(t, e.getTop());
    r = Math.max(r, e.getLeft() + e.getWidth()); b = Math.max(b, e.getTop() + e.getHeight());
  });
  return { l: l, t: t, w: r - l, h: b - t };
}

function libIndex_(url) {
  const out = {};
  SlidesApp.openById(deckId_(url)).getSlides().forEach(function (slide) {
    slide.getPageElements().forEach(function (el) {
      const m = (el.getTitle() || '').match(/^lib:([a-z0-9_-]+)/i);
      if (m) (out[m[1].toLowerCase()] = out[m[1].toLowerCase()] || []).push(el);
    });
  });
  return out;
}

function fill_(el, hex) {
  const type = el.getPageElementType();
  if (type === SlidesApp.PageElementType.GROUP) el.asGroup().getChildren().forEach(function (c) { fill_(c, hex); });
  else if (type === SlidesApp.PageElementType.SHAPE) el.asShape().getFill().setSolidFill(hex);
}

/** Copy library elements onto slide, scaled to fit (w x h) and centred on box b. */
function drop_(slide, src, b, w, h, title, hex) {
  const sb = box_(src);
  const s = Math.min(w / sb.w, h / sb.h);
  const ox = b.l + (b.w - sb.w * s) / 2, oy = b.t + (b.h - sb.h * s) / 2;
  src.forEach(function (e) {
    const n = slide.insertPageElement(e);
    n.setWidth(e.getWidth() * s).setHeight(e.getHeight() * s);
    n.setLeft(ox + (e.getLeft() - sb.l) * s).setTop(oy + (e.getTop() - sb.t) * s);
    n.setTitle(title);
    if (hex) fill_(n, hex);
    if (s !== 1 && n.getPageElementType() === SlidesApp.PageElementType.SHAPE) {
      const tx = n.asShape().getText();
      if (tx.asString().trim()) {
        const fs = e.asShape().getText().getTextStyle().getFontSize();
        if (fs) tx.getTextStyle().setFontSize(Math.max(Math.round(fs * s * 10) / 10, 1));
      }
    }
  });
}

function placeFromLibrary() {
  const ss = SpreadsheetApp.getActive();
  const colors = {};
  SpreadsheetApp.openByUrl(STYLE_SHEET_URL).getSheetByName('Colors').getDataRange().getValues().slice(1)
    .forEach(function (r) { if (r[0]) colors[String(r[0])] = String(r[1]); });
  const icons = {};
  ss.getSheetByName('Icons').getDataRange().getValues().slice(1).forEach(function (r) {
    if (r[0] && r[2]) icons[String(r[0])] = {
      name: String(r[1]).replace(/\s*\(.*\)\s*$/, '').trim().toLowerCase(),
      hex: colors[String(r[4])], size: (Number(r[5]) || 0.26) * 72
    };
  });
  const iconLib = libIndex_(ICON_LIBRARY_URL), uiLib = libIndex_(UI_LIBRARY_URL);
  const sh = ss.getSheetByName('Assets');
  const rows = sh.getDataRange().getValues();
  for (let r = 1; r < rows.length; r++) {
    const url = String(rows[r][1]);
    if (rows[r][2] !== true || !url) continue;
    let placed = 0; const flags = [];
    try {
      const deck = SlidesApp.openById(deckId_(url));
      deck.getSlides().forEach(function (slide, i) {
        const slots = {};
        slide.getPageElements().forEach(function (el) {
          const m = (el.getTitle() || '').match(/^(icon|ui):([a-z0-9_-]+)/i);
          if (m) (slots[m[1].toLowerCase() + ':' + m[2]] = slots[m[1].toLowerCase() + ':' + m[2]] || []).push(el);
        });
        Object.keys(slots).forEach(function (tag) {
          const kind = tag.split(':')[0], key = tag.split(':')[1], old = slots[tag], b = box_(old);
          let src, w, h, hex;
          if (kind === 'icon') {
            const row = icons[key];
            if (!row) { flags.push('Page ' + (i + 1) + ': no Icons row for ' + key); return; }
            src = iconLib[row.name]; w = h = row.size; hex = row.hex;
            if (!src) { flags.push('Page ' + (i + 1) + ': ' + row.name + ' is not in the icon library'); return; }
          } else {
            src = uiLib['ui-' + key.replace(/_/g, '-').toLowerCase()]; w = b.w; h = b.h;
            if (!src) { flags.push('Page ' + (i + 1) + ': ui-' + key + ' is not in the UI library'); return; }
            slide.getPageElements().forEach(function (el) {  // untagged text left inside the old mockup
              if (el.getPageElementType() !== SlidesApp.PageElementType.SHAPE || el.getTitle()) return;
              if (el.asShape().getShapeType() !== SlidesApp.ShapeType.TEXT_BOX) return;
              if (el.getLeft() >= b.l - 1 && el.getTop() >= b.t - 1 && el.getLeft() + el.getWidth() <= b.l + b.w + 1 &&
                  el.getTop() + el.getHeight() <= b.t + b.h + 1) el.remove();
            });
          }
          drop_(slide, src, b, w, h, tag, hex);
          old.forEach(function (e) { e.remove(); });
          placed++;
        });
      });
      deck.saveAndClose();
    } catch (e) { flags.push('Could not finish: ' + e.message); }
    sh.getRange(r + 1, 6).setValue('Placed ' + placed + ' from library' + (flags.length ? '\n' + flags.join('\n') : ''));
  }
}

function addToLibrary() {
  const ui = SpreadsheetApp.getUi();
  const ask = function (q) {
    const a = ui.prompt('Add to library', q, ui.ButtonSet.OK_CANCEL);
    return a.getSelectedButton() === ui.Button.OK ? a.getResponseText().trim() : null;
  };
  const url = ask('Link to the converted deck (Google Slides, or the .pptx link from svgslid.es/convert):');
  if (!url) return;
  const kind = (ask('Type: icon or ui') || '').toLowerCase() === 'ui' ? 'ui' : 'icon';
  const names = ask('Name per slide, comma separated, lowercase with dashes (e.g. data-flow, pricing-table):');
  if (!names) return;
  const words = ask('Search keywords (optional):') || '';
  let id = deckId_(url), temp = null;
  DriveApp.getRootFolder();  // Drive scope, needed to convert a .pptx
  const meta = JSON.parse(UrlFetchApp.fetch('https://www.googleapis.com/drive/v3/files/' + id + '?fields=mimeType',
    { headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() } }).getContentText());
  if (meta.mimeType !== 'application/vnd.google-apps.presentation') {
    const copy = JSON.parse(UrlFetchApp.fetch('https://www.googleapis.com/drive/v3/files/' + id + '/copy', {
      method: 'post', contentType: 'application/json',
      headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() },
      payload: JSON.stringify({ name: 'library import (temp)', mimeType: 'application/vnd.google-apps.presentation' })
    }).getContentText());
    id = temp = copy.id;
  }
  const lib = SlidesApp.openById(deckId_(kind === 'ui' ? UI_LIBRARY_URL : ICON_LIBRARY_URL));
  const list = names.split(',').map(function (n) { return n.trim().toLowerCase().replace(/[^a-z0-9-]+/g, '-'); });
  const pageW = lib.getPageWidth();
  let added = 0;
  SlidesApp.openById(id).getSlides().forEach(function (src, i) {
    const name = (kind === 'ui' ? 'ui-' : '') + (list[i] || list[0] + '-' + (i + 1));
    const slide = lib.appendSlide(src);
    const els = slide.getPageElements();
    if (!els.length) { slide.remove(); return; }
    els.forEach(function (e) { e.setTitle('lib:' + name); });
    const b = box_(els);
    const lx = b.l + b.w + 12 < pageW - 150 ? b.l + b.w + 12 : 6;
    const text = [(kind === 'ui' ? 'ui:' : 'icon:') + name.replace(/^ui-/, ''), name, name.replace(/-/g, ' '), words].join(' ').trim();
    const label = slide.insertTextBox(text, lx, b.l + b.w + 12 < pageW - 150 ? b.t : 2, 150, 14);
    label.setTitle('lib-label');
    label.getText().getTextStyle().setFontSize(6).setFontFamily('Verdana').setForegroundColor('#FFFFFF');
    added++;
  });
  lib.saveAndClose();
  if (temp) DriveApp.getFileById(temp).setTrashed(true);
  ui.alert('Added ' + added + ' slide(s) to the ' + kind + ' library.');
}
