# Update Google Slides collateral from one messaging sheet with Gemini

*Nov 9, 2026 · svgslid.es blog*

Write the message once in a sheet. Update every one-pager, brief, whitepaper and battlecard from it.

## TL;DR
- Since Oct 30, 2026, Gemini in Google Slides can edit a whole presentation from one prompt, grounded in a Drive file (https://workspaceupdates.googleblog.com/2026/10/edit-entire-presentations-with-gemini-in-Google-Slides.html).
- Point that prompt at a messaging sheet and one asset updates in one step.
- For exact wording across many assets, tag text boxes with `slot:<key>` in alt text and use a script or an agent.
- Approve the sheet once. Give every slot a character budget. Look at every changed page.
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
Columns: Key, Fact, Draft, Approved line, Budget, Length, Fits, Used in. Draft can use the Sheets AI function (https://support.google.com/docs/answer/15877199):

    =AI("Write one line of product marketing copy from this fact. Plain, specific, active voice. No superlatives.", B2)

Needs a Google plan with Gemini. Nested AI functions are not supported. Only Approved line reaches an asset.

## Linked tables and charts
Copy in Sheets, paste in Slides, choose Link to spreadsheet. Tools › Linked objects › Update all. Updates are manual. Tables over 400 cells paste unlinked (https://support.google.com/docs/answer/7009814). Updates override edits made in Slides.

## Update one asset with Gemini
Prompt in the Slides side panel, with the sheet referenced:

    Update this presentation from the Approved line column of @Messaging sheet.
    Each row's Used in column says which asset it belongs to.
    Use the approved wording exactly. Do not rephrase, add or remove sentences.
    Keep every layout, font, colour and image as it is.
    Do not add or delete pages.

Limits: Gemini chooses which slides change; one file per prompt; availability depends on rollout and plan.

## Named slots and a script
Right-click a text box › Alt text › Title: `slot:headline`. The key matches the sheet. The pack's Apps Script (`sync_copy.gs`) adds Dry run and Sync copy to assets. Over-budget lines are skipped and flagged. Untagged boxes are never touched. Instruction files for Gemini, Claude and Codex follow one agent contract.

## Approvals
File › Approvals on the sheet (https://support.google.com/drive/answer/9387535). Lock for review. Unlocking during an approval resets approvals; edits after approval leave it attached to the previous version. So: finish words, approve, update assets, lock released assets. Approvals need an eligible work or school account.

## Layout shift
Slides does not shrink text to fit. Budget every slot, fix length in the sheet, skip over-budget lines, look at every changed page, update linked objects last.

## Tested / not tested
Checked: templates keep page sizes and slot tags as Slides files; budget formulas work. Not yet run by us: the whole-deck Gemini prompt (rolling out), the sync script end to end, the AI formula in this workbook. Run the dry run first, on copies.

The screens in the post are mockups. Google Slides, Google Sheets, Google Drive and Gemini are trademarks of Google LLC.
