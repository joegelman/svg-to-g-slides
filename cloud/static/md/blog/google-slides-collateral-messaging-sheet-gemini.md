# Update Google Slides collateral from one messaging sheet with Gemini

*Nov 9, 2026 · svgslid.es blog*

Write the brief once in a sheet. Gemini writes each line to a recipe and a character limit, and a script puts it in every asset. Updated Nov 10, 2026.

## TL;DR
- Since Oct 30, 2026, Gemini in Google Slides can edit a whole presentation from one prompt, grounded in a Drive file (https://workspaceupdates.googleblog.com/2026/10/edit-entire-presentations-with-gemini-in-Google-Slides.html).
- Point that prompt at a messaging sheet and one asset updates in one step.
- For exact wording across many assets, tag text boxes with `slot:<key>` in alt text and use a script or an agent.
- Gemini writes each line under a recipe, voice rules and a hard character limit. No approval column. Look at every changed page.
- Starter pack (templates, sheet, prompts, script): https://drive.google.com/drive/folders/12DEX6TnEHQ8goCO29j9ubwYfHP5K72-q

## What changed
Slides could link charts and tables to Sheets, but not the text in a text box. Gemini's whole-deck editing takes one instruction, decides which slides it applies to, edits them in place as native text and shapes, and lists what it changed. Undo and version history work. Rollout began Oct 29, 2026 and may take longer than 15 days.

## Page sizes
- One-pager, solution brief, whitepaper: 8.5 x 11 in (US Letter) or 21 x 29.7 cm (A4).
- Battlecard: 11 x 8.5 in landscape. Sales deck: Widescreen 16:9.
- File › Page setup › Custom. Units: inches, centimetres, points, pixels. Set size before designing. One size per file.

## Bleed
Slides has no bleed setting. Add the bleed to every side of the canvas (Letter + 0.125 in = 8.75 x 11.25 in). Run colour blocks to the canvas edge, keep text 0.25 in inside the trim, draw trim and safe guides, delete them before export. Ask the printer for their bleed.

## Layout patterns
Six blocks: hero block, three up, proof strip, problem/answer, two columns with pull line, closing strip. Text boxes: fixed size with room to spare, one job per box, one style per role. Logos and icons as vectors (SVG to Slides).

## Messaging sheet
Columns: Key, Role, Source, Brief, Prompt, Line, Budget, Length, Fits, Used in. A person writes the Brief. The Prompt column joins the role's recipe, the voice and the row's budget from a Rules tab. The Line column is the Sheets AI function (https://support.google.com/docs/answer/15877199):

    =AI(E2, D2)

Rules tab: one recipe per role (eyebrow, headline, subhead, title, body, stat, label, cta, legal), the voice, "use only facts in the brief", "return the line only", and the budget as a hard character limit. There is no Draft or Approved line column (removed Nov 10, 2026). Needs a Google plan with Gemini. Nested AI functions are not supported. AI formulas written by script, import or API wait for a Generate and fill click. Only the Line column reaches an asset.

## Linked tables and charts
Copy in Sheets, paste in Slides, choose Link to spreadsheet. Tools › Linked objects › Update all. Updates are manual. Tables over 400 cells paste unlinked (https://support.google.com/docs/answer/7009814). Updates override edits made in Slides.

## Update one asset with Gemini
Prompt in the Slides side panel, with the sheet referenced:

    Update this presentation from the Line column of @Messaging sheet.
    Each row's Used in column says which asset it belongs to.
    Use the wording exactly. Do not rephrase, add or remove sentences.
    Keep every layout, font, colour and image as it is.
    Do not add or delete pages.

Limits: Gemini chooses which slides change; one file per prompt; availability depends on rollout and plan.

## Named slots and a script
Right-click a text box › Alt text › Title: `slot:headline`. The key matches the sheet. The script attached to the starter sheet adds a Collateral menu: Sync all (copy, style, icons and UIs), Sync copy to assets, Apply style, Place icons and UIs, Dry run. Over-budget lines and lines not yet generated are skipped and flagged. Untagged boxes are never touched. Deck URLs on the Assets tab must be plain text, not link chips. Instruction files for Gemini, Claude and Codex follow one agent contract.

## Rules, with approvals optional
There is no per-line approval step. Review the Rules tab and the briefs, read the Line column, run Dry run, sync, look at every changed page. Trade-off: nobody signs each sentence. For sign-off, File › Approvals on the sheet (https://support.google.com/drive/answer/9387535): lock for review; unlocking during an approval resets approvals; edits after approval leave it attached to the previous version. Approvals need an eligible work or school account.

## Layout shift
Slides does not shrink text to fit. Budget every slot, fix length in the sheet, skip over-budget lines, look at every changed page, update linked objects last.

## Tested / not tested (Nov 10, 2026)
Checked: templates keep page sizes and slot tags; budget formulas work; Dry run opened four decks and reported zero to three slots to change in each, no flags; Place icons and UIs swapped tagged icons and a mockup for library shapes and kept file IDs (mockup text sizing was fixed afterwards). Earlier: the AI function works after a Generate and fill click; a test account hit its monthly limit after five cells. On a Workspace account with Gemini, a single-slide prompt with three lines applied them word for word and kept fonts, sizes and slot tags; the whole-deck prompt was refused ("only able to edit the single currently active slide"). Not yet checked: the 82 new Line formulas (waiting for Generate and fill), and Sync all end to end. Part 2: https://svgslid.es/blog/messaging-workshop-brand-style-sheet-google-sheets

The screens in the post are mockups. Google Slides, Google Sheets, Google Drive and Gemini are trademarks of Google LLC.
