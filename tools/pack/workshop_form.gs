/**
 * Build the messaging workshop as a Google Form from the Workshop tab.
 *
 * Setup (once): open the messaging architecture sheet, Extensions > Apps Script,
 * add this file next to sync_copy.gs (which builds the menus), save, reload the sheet.
 * Then Workshop > Build the form.
 * The first run asks for permission to create a form and edit this spreadsheet.
 *
 * What it does:
 *  - Reads Key, Section, Question, Type and Choices from the Workshop tab.
 *  - Creates one form page per section, one question per row.
 *  - Sends responses to this spreadsheet, in a tab named Responses.
 *  - Writes the form links to the Workshop tab (cells J1:K2).
 * The Workshop tab's "Latest response" column reads the newest row of Responses
 * by matching question text, so do not reword a question in the form itself.
 * Reword it on the Workshop tab and build a new form.
 */
function buildWorkshopForm() {
  const ss = SpreadsheetApp.getActive();
  const ws = ss.getSheetByName('Workshop');
  const rows = ws.getRange(2, 1, ws.getLastRow() - 1, 5).getValues();
  const brand = String(rows[0][0] === 'name' ? ws.getRange(2, 8).getValue() : '') || ss.getName();

  const form = FormApp.create('Messaging workshop: ' + brand);
  form.setDescription('Answer in plain words. Short is fine. One response per workshop; submit again to revise.');
  form.setCollectEmail(false);

  let section = '';
  rows.forEach(function (r) {
    const sec = String(r[1]), q = String(r[2]), type = String(r[3]), choices = String(r[4]);
    if (!q) return;
    if (sec !== section) {
      if (section) form.addPageBreakItem().setTitle(sec); else form.addSectionHeaderItem().setTitle(sec);
      section = sec;
    }
    if (type === 'short') {
      form.addTextItem().setTitle(q);
    } else if (type === 'choice') {
      form.addMultipleChoiceItem().setTitle(q).setChoiceValues(choices.split('|'));
    } else if (type === 'scale') {
      const b = choices.split('|');
      form.addScaleItem().setTitle(q).setBounds(Number(b[0]) || 1, Number(b[1]) || 5);
    } else {
      form.addParagraphTextItem().setTitle(q);
    }
  });

  const before = ss.getSheets().map(function (s) { return s.getSheetId(); });
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  SpreadsheetApp.flush();
  const old = ss.getSheetByName('Responses');
  if (old) old.setName('Responses (old ' + new Date().toISOString().slice(0, 10) + ')');
  ss.getSheets().forEach(function (s) {
    if (before.indexOf(s.getSheetId()) < 0) s.setName('Responses');
  });

  ws.getRange('J1:K2').setValues([
    ['Form (share this)', form.getPublishedUrl()],
    ['Form (edit)', form.getEditUrl()]
  ]);
  SpreadsheetApp.getUi().alert('Form built. Links are in Workshop!K1:K2.');
}
