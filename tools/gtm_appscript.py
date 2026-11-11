"""Apps Script for GTM, part 1: one content source for the deck, the cheat sheet and the post.

Code samples are written against Google's Apps Script reference. None has been run in
Apps Script by us; FITS() logic is checked with node in tools/gtm_build.py.
"""
import html
import re

QUOTAS = "https://developers.google.com/apps-script/guides/services/quotas"
REF = "https://developers.google.com/apps-script/reference"
CUSTOM_FN = "https://developers.google.com/apps-script/guides/sheets/functions"
TRIGGERS = "https://developers.google.com/apps-script/guides/triggers"

CODE = {}

CODE["menu"] = """function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('GTM')
    .addItem('Build account decks', 'buildDecks')
    .addItem('Draft follow-ups', 'draftFollowUps')
    .addToUi();
}"""

CODE["fits"] = """/**
 * Says whether a line fits its character budget.
 * @customfunction
 */
function FITS(text, budget) {
  const n = String(text).length;
  return n <= budget ? 'OK' : 'Over by ' + (n - budget);
}"""

CODE["decks"] = """const TEMPLATE_ID = 'paste-your-template-deck-id';

function buildDecks() {
  const [head, ...rows] = SpreadsheetApp.getActive()
    .getSheetByName('Accounts').getDataRange().getValues();
  rows.forEach(row => {
    const copy = DriveApp.getFileById(TEMPLATE_ID)
      .makeCopy('Pitch - ' + row[0]);
    const deck = SlidesApp.openById(copy.getId());
    head.forEach((key, i) =>
      deck.replaceAllText('{{' + key + '}}', String(row[i])));
  });
}"""

CODE["drafts"] = """// Columns: Name, Email, Company, Status
function draftFollowUps() {
  const rows = SpreadsheetApp.getActive()
    .getSheetByName('Follow-ups').getDataRange().getValues();
  rows.slice(1).filter(r => r[3] === 'Ready').forEach(r => {
    const body = 'Hi ' + r[0] + ',\\n\\nThanks for the time today.';
    GmailApp.createDraft(r[1], 'Next steps for ' + r[2], body);
  });
}"""

CODE["weekly"] = """function installWeekly() {
  ScriptApp.newTrigger('weeklyDigest').timeBased()
    .onWeekDay(ScriptApp.WeekDay.MONDAY).atHour(9).create();
}

// Proof tab: column G holds days left.
function weeklyDigest() {
  const rows = SpreadsheetApp.getActive()
    .getSheetByName('Proof').getDataRange().getValues();
  const soon = rows.filter(r => r[6] >= 0 && r[6] < 30);
  if (!soon.length) return;
  MailApp.sendEmail(Session.getEffectiveUser().getEmail(),
    soon.length + ' proof points expire within 30 days',
    soon.map(r => r[1] + ': ' + r[0]).join('\\n'));
}"""

CODE["stamp"] = """// Stamps column I when a row on Messages changes.
function onEdit(e) {
  const sheet = e.range.getSheet();
  if (sheet.getName() !== 'Messages') return;
  if (e.range.getRow() === 1) return;
  sheet.getRange(e.range.getRow(), 9).setValue(new Date());
}"""

CODE["debug"] = """function testFits() {
  console.log(FITS('SSO on every plan', 24));
  // OK
  console.log(FITS('Links that expire when you say so', 24));
  // Over by 9
}"""

# ------------------------------------------------------------------ slides
# kind: title | text | code | steps | split | recap | next
SLIDES = [
    dict(kind="title", title="Apps Script for GTM", sub="Part 1: five scripts a product marketer can run this week",
         foot="svgslid.es/blog"),
    dict(kind="text", eyebrow="Why", title="Your GTM stack already has a scripting language",
         bullets=["Launches mean the same copy-paste across Sheets, Slides, Docs and Gmail.",
                  "Apps Script is JavaScript that runs inside Google Workspace. It's built in.",
                  "It can read and write Sheets, Slides, Docs, Gmail, Drive, Calendar and Forms.",
                  "No server, no deploy. Write it in the browser, run it from a menu."]),
    dict(kind="split", eyebrow="Where it lives", title="Two kinds of script",
         left=("Bound to a file", ["Open a sheet, then Extensions › Apps Script.",
                                    "Can add menus to that file and react to edits.",
                                    "Start here. Everything in this deck is bound to a sheet."]),
         right=("Standalone", ["Lives at script.google.com, on its own.",
                               "Good for jobs that span many files.",
                               "Same language, same services."])),
    dict(kind="code", eyebrow="First script", title="A GTM menu in your sheet", code="menu",
         bullets=["onOpen runs every time the sheet opens.",
                  "Each item calls a function by name.",
                  "Reload the sheet and the GTM menu appears next to Help."]),
    dict(kind="steps", eyebrow="Run it", title="Save, run, allow, reload",
         steps=["Extensions › Apps Script. Paste the code. Save.",
                "Pick a function in the toolbar dropdown and click Run.",
                "First run: Google asks for permission. Read what it asks for, then allow.",
                "Reload the sheet. Your menu is there.",
                "View › Executions shows every run and its log."]),
    dict(kind="code", eyebrow="Superpower 1", title="A formula that checks copy length", code="fits",
         bullets=["@customfunction makes it usable in a cell.",
                  "Type =FITS(D2, E2) next to any line of copy.",
                  "Catch layout shift in the sheet, before it hits a slide."]),
    dict(kind="code", eyebrow="Superpower 2", title="One deck per account, from a template", code="decks",
         bullets=["Template slides hold tokens like {{Company}} and {{Pain}}.",
                  "Sheet headers match the tokens: Company, Pain, Champion.",
                  "One run copies the template per row and fills it in."]),
    dict(kind="code", eyebrow="Superpower 3", title="Follow-ups as drafts, not sends", code="drafts",
         bullets=["Rows marked Ready become Gmail drafts.",
                  "Nothing is sent. A person reads every draft first.",
                  "Swap the body for your own template."]),
    dict(kind="code", eyebrow="Superpower 4", title="Run it every Monday", code="weekly",
         bullets=["Run installWeekly once. It schedules weeklyDigest.",
                  "The digest emails you proof points close to expiry.",
                  "Triggers run as you, even with the sheet closed."]),
    dict(kind="code", eyebrow="Superpower 5", title="Stamp every messaging change", code="stamp",
         bullets=["onEdit is a simple trigger. No setup.",
                  "Each edit on Messages writes the time in column I.",
                  "Sort by it to see what changed since the last launch."]),
    dict(kind="code", eyebrow="Debug", title="Test small, read the log", code="debug",
         bullets=["Write a tiny test function. Run it from the editor.",
                  "console.log output shows in the execution log.",
                  "Fix one thing at a time."]),
    dict(kind="text", eyebrow="Before you share it", title="Safety checklist",
         bullets=["Read the permission screen. It lists exactly what the script can touch.",
                  "Scripts run as whoever runs them, with that person's access.",
                  "Draft before you send. Copy before you overwrite.",
                  "Test on copies of real files.",
                  "Quotas apply: one run stops at 6 minutes, and email has daily limits."]),
    dict(kind="recap", eyebrow="Recap", title="Five superpowers",
         items=[("FITS()", "Checks copy against a character budget, in a cell."),
                ("buildDecks()", "One personalised deck per row, from a template."),
                ("draftFollowUps()", "Gmail drafts from a sheet. A person sends."),
                ("weeklyDigest()", "A Monday email, on a time trigger."),
                ("onEdit()", "A timestamp on every messaging change.")]),
    dict(kind="next", eyebrow="Coming in part 2", title="Talk to everything else",
         bullets=["UrlFetchApp: pull CRM and product data into Sheets.",
                  "Post launch updates to a Google Chat space.",
                  "Call Gemini from a script to draft copy to a budget.",
                  "Ship a tiny internal web app with doGet()."],
         foot="Cheat sheet and part 2: svgslid.es/blog"),
]

# ------------------------------------------------------------------ highlighting
KW = {"function", "const", "let", "var", "return", "if", "else", "for", "of", "in", "new", "typeof",
      "true", "false", "null", "undefined", "while", "break", "continue"}
TOKEN = re.compile(r"(?P<cm>//[^\n]*|/\*.*?\*/)|(?P<st>'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`[^`]*`)"
                   r"|(?P<nu>\b\d+(?:\.\d+)?\b)|(?P<id>[A-Za-z_$][\w$]*)|(?P<ws>\s+)|(?P<pu>.)", re.S)


def tokens(src):
    """Yield (kind, text). kind: cm st nu kw fn cl pr tx."""
    out = []
    for m in TOKEN.finditer(src):
        k = m.lastgroup
        t = m.group()
        if k == "id":
            rest = src[m.end():]
            prev = src[:m.start()].rstrip()[-1:] if m.start() else ""
            if t in KW:
                k = "kw"
            elif rest.lstrip(" ").startswith("("):
                k = "fn"
            elif src[:m.start()].endswith("..."):
                k = "tx"
            elif t[0].isupper() and prev != ".":
                k = "cl"
            elif prev == ".":
                k = "pr"
            else:
                k = "tx"
        elif k in ("ws", "pu"):
            k = "tx"
        out.append((k, t))
    return out


DARK = {"bg": "#1C1E22", "tx": "#E6E6E6", "kw": "#C792EA", "st": "#C3E88D", "nu": "#F78C6C",
        "fn": "#82AAFF", "cl": "#FFCB6B", "pr": "#89DDFF", "cm": "#7F848E"}


def code_html(key_or_src, cls="code"):
    src = CODE.get(key_or_src, key_or_src)
    spans = "".join(t if k == "tx" else f'<span class="{k}">{t}</span>' for k, t in ((k, html.escape(t, quote=False)) for k, t in tokens(src)))
    return f'<pre class="{cls}"><code>{spans}</code></pre>'
