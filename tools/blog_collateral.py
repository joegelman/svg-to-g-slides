"""Blog post: Update Google Slides collateral from one messaging sheet with Gemini.

Figures are mockups rendered by tools/collateral_images.py. Claims are limited to
Google's own announcement and help pages (see SOURCES) and to what the starter pack does.
"""

PACK = "https://drive.google.com/drive/folders/12DEX6TnEHQ8goCO29j9ubwYfHP5K72-q"
SHEET = "https://docs.google.com/spreadsheets/d/1HVRcSGWf__JwbNXzMrdkw0SuXM7Z2aQJrM_QJFU3uuA/copy"
DECK = "https://docs.google.com/presentation/d/%s/copy"
T_ONE = DECK % "1feiCP4d4Gi_crzSQFDib4JgMrdq8pxt6BdLs9JHTucU"
T_BLEED = DECK % "11p2Rb2uAxAQ0Kw4kKt4Rs84bWL3ccV8miyxrEyRlj8A"
T_BRIEF = DECK % "1E4RW38YNuj7lZER7ZM88fDFJtJCFT7kdL01XRPXK5vc"
T_WP = DECK % "1-2caooSTgUQduoKtqya8wmM-9mIW8ncb3NlDu6B6NFQ"
T_BATTLE = DECK % "14sTC645cIijFziQDjfOjiobxQWDKRHECai6jj8d8LW4"
SKILLS = "https://drive.google.com/drive/folders/1nLE-gRlhLr7hRUhoTTagoFaJzTZ3TT7U"

GEM_EDIT = "https://workspaceupdates.googleblog.com/2026/10/edit-entire-presentations-with-gemini-in-Google-Slides.html"
LINKED = "https://support.google.com/docs/answer/7009814"
APPROVALS = "https://support.google.com/drive/answer/9387535"
AI_FN = "https://support.google.com/docs/answer/15877199"

PRE = '<pre style="background:var(--tint);border-radius:10px;padding:14px 16px;font-size:13.5px;line-height:1.55;white-space:pre-wrap;overflow-wrap:anywhere;margin:0 0 1.05em">'

BODY = """
<h2 id="what">What changed on October 30</h2>
<p>Product messaging changes. A capability ships or a competitor moves, and every solution brief, one-pager, sales deck and battlecard that mentions it is out of date.</p>
<p>The fix is to write the message in one place and have every asset take its copy from there. Google Slides&trade; was missing a piece for this. It can link a chart or a table to Google Sheets&trade;, but a headline in a text box is linked to nothing, so a copy change meant opening every file.</p>
<p>On October 30, 2026, Google announced that <a href="%GEM_EDIT%">Gemini in Google Slides can edit an entire presentation from one prompt</a>. You type one instruction. Gemini decides which slides it applies to and edits them in place, as ordinary text and shapes. The instruction can point at a file in Drive. Google&rsquo;s own example prompt is &ldquo;Update this presentation to include more details based on [reference file].&rdquo;</p>
<p>Make the reference file your messaging sheet, and updating an asset is one prompt. The rest of this post is the setup that makes that prompt worth running, and what to use when you need more control than a prompt gives you.</p>
<p>This is part 1 of a series. <a href="/blog/messaging-workshop-brand-style-sheet-google-sheets">Part 2</a> covers where the messaging comes from, with a workshop form, a messaging architecture and a brand style sheet.</p>

<h2 id="setup">The setup in one picture</h2>
{fig:flow-sheet-to-assets|Flow diagram: plain fact, draft, approved line, then update by Gemini prompt or script into one-pager, solution brief, whitepaper, battlecard and sales deck|Copy flows left to right. The approved line is the only thing that reaches an asset.}
<p>Four parts:</p>
<ul>
<li><b>Templates at real page sizes</b>, with text boxes built to take new copy.</li>
<li><b>A messaging sheet</b>: one row per message, with a plain fact, a finished line and a character budget.</li>
<li><b>An update step</b>: a Gemini prompt for one asset, or a script or agent for all of them.</li>
<li><b>An approval gate</b> on the sheet, so words are signed off once.</li>
</ul>

<h2 id="sizes">Build each asset at its real size</h2>
<p>A one-pager made on a 16:9 slide and stretched at export looks like a slide. Set the page size first.</p>
{fig:asset-sizes|Six page outlines to scale: one-pager, solution brief, whitepaper, A4 one-pager, battlecard, sales deck|Common collateral sizes, to scale.}
<ul>
<li><b>One-pager:</b> 8.5 &times; 11 in (US Letter) or 21 &times; 29.7 cm (A4). One page.</li>
<li><b>Solution brief:</b> same page, two pages. Front and back.</li>
<li><b>Whitepaper:</b> same page, one page per slide. Cover, inside pages, back.</li>
<li><b>Battlecard:</b> 11 &times; 8.5 in, landscape. Read on screen.</li>
<li><b>Sales deck:</b> Widescreen 16:9, the Slides default.</li>
</ul>
<ol class="steps">
<li>Open <b>File &rsaquo; Page setup</b>.</li>
<li>Choose <b>Custom</b>.</li>
<li>Enter width and height. Pick inches, centimetres, points or pixels.</li>
<li>Click <b>Apply</b>.</li>
</ol>
{fig:page-setup-custom|Mockup of the Google Slides Page setup dialog set to Custom, 8.5 by 11 inches|Page setup, set to US Letter. Mockup.}
<p>Set the size before you design. Changing it later can move and rescale what is already on the page. Page size applies to the whole file, so each asset size is its own file.</p>

<h2 id="bleed">Add bleed if it goes to a printer</h2>
<p>Slides has no bleed setting. You make the page bigger and keep important content away from the edge.</p>
{fig:bleed-trim-safe|Diagram of an 8.75 by 11.25 inch canvas with a red trim line at 8.5 by 11 and a blue safe margin 0.25 inch inside it|Bleed, trim and safe margin for a US Letter one-pager.}
<ul>
<li><b>Canvas:</b> add the bleed to every side. For Letter with 0.125 in bleed, that is 8.75 &times; 11.25 in.</li>
<li><b>Colour blocks and images</b> that touch the edge run all the way to the canvas edge.</li>
<li><b>Text and logos</b> stay 0.25 in inside the trim.</li>
<li><b>Guides:</b> draw the trim and safe lines as dashed rectangles. Delete them before you download the PDF.</li>
</ul>
<p>Ask the printer what bleed they want. 0.125 in (3 mm) is common.</p>

<h2 id="patterns">Layout patterns that survive a copy change</h2>
<p>Most collateral is built from the same few blocks. Reuse them across assets so a message has the same shape wherever it appears.</p>
{fig:layout-patterns|Six wireframes: hero block, three up, proof strip, problem and answer, two columns with pull line, closing strip|The six blocks used in the starter templates.}
<p>Rules for the text boxes inside them:</p>
<ul>
<li><b>Fixed boxes, with room to spare.</b> Size each box for the longest line you will allow, not for today&rsquo;s copy.</li>
<li><b>One job per box.</b> A headline box holds a headline. If a bold lead-in and body text share a box, split them.</li>
<li><b>One style per role.</b> Eyebrow, headline, subhead, body, stat, label, legal. Same font, size and colour everywhere that role appears.</li>
<li><b>Colour blocks carry the layout.</b> A dark band, a tinted strip and one accent colour are enough. They do not move when the copy changes.</li>
<li><b>Logos and icons as vectors.</b> Drop them in as SVG with SVG to Slides so they stay sharp at print size and can be recoloured.</li>
</ul>

<h2 id="sheet">The messaging sheet</h2>
<p>One row per message. The sheet is the only place copy is written.</p>
{fig:messaging-sheet|Mockup of the Messages tab with columns Key, Fact, Draft, Approved line, Budget, Length, Fits and Used in; one row is flagged Over by 9|The Messages tab. The Approved line column is the only one that reaches an asset. Mockup.}
<ul>
<li><b>Key:</b> the name of the slot, like <code>headline</code> or <code>benefit_1_title</code>.</li>
<li><b>Fact:</b> the plain statement. &ldquo;SSO is included on every plan.&rdquo; This is what product and legal agree on.</li>
<li><b>Draft:</b> a first pass at the finished line.</li>
<li><b>Approved line:</b> the finished line, pasted as plain text once someone has signed it off.</li>
<li><b>Budget, Length, Fits:</b> the character limit for the slot, <code>=LEN()</code> of the approved line, and a flag when it runs over.</li>
<li><b>Used in:</b> which assets carry this line.</li>
</ul>
<p>The Draft column can be a formula. <a href="%AI_FN%">Sheets has an AI function</a> that takes a prompt and a cell:</p>
%PRE%=AI("Write one line of product marketing copy from this fact. Plain, specific, active voice. No superlatives.", B2)</pre>
<p>It needs a Google plan that includes Gemini. Keep the formula simple: Google&rsquo;s help page says nested AI functions are not supported. A formula that arrives by import or through the API shows as text until you select it and click <b>Generate and fill</b>. Select a range and one click covers every AI cell in it. Without Gemini, write the draft by hand. The rest of the sheet works the same.</p>
<p>Keep Draft and Approved line separate. A formula can change. An approved line must not.</p>

<h2 id="data">Tables and charts: link them</h2>
<p>Data is the part Slides already handles. Copy a range or a chart in Sheets, paste it into Slides, and choose <b>Link to spreadsheet</b>.</p>
{fig:linked-objects-update|Mockup of a linked table on a slide with an Update button, and the Linked objects sidebar listing a table and a chart with Update all|A linked table and the Linked objects sidebar. Mockup.}
<ul>
<li>When the sheet changes, the object shows an <b>Update</b> button.</li>
<li><b>Tools &rsaquo; Linked objects</b> lists every linked object in the file, with <b>Update all</b>.</li>
<li>Updates are manual. Someone opens the file and clicks.</li>
<li><a href="%LINKED%">Google&rsquo;s help page</a> says a table with more than 400 cells pastes unlinked.</li>
<li>An update pulls the sheet&rsquo;s version over any edits made to the object in Slides. Style linked tables in the sheet.</li>
</ul>
<p>Use this for plan comparisons, spec tables, pricing and charts. A one-cell linked table can also carry a short fixed line such as a price or a date. It is still a table, so it has no text styles from your theme and no autofit. For headlines and body copy, use text boxes.</p>

<h2 id="gemini">Update one asset with Gemini</h2>
<p>This is the no-code route. Open the asset, open the Gemini side panel, reference the messaging sheet, and ask for the update.</p>
%PRE%Update this presentation from the Approved line column of @Messaging sheet.
Each row's Used in column says which asset it belongs to.
Use the approved wording exactly. Do not rephrase, add or remove sentences.
Keep every layout, font, colour and image as it is.
Do not add or delete pages.</pre>
{fig:gemini-side-panel-update|Mockup of the Gemini side panel in Google Slides with an update prompt referencing the messaging sheet and a summary of four changed text boxes|The prompt and the change summary. Mockup.}
<p>When Gemini finishes, the side panel lists what it changed. The edits are applied as if you made them, so undo and version history work.</p>
<p>What to plan around:</p>
<ul>
<li><b>Gemini chooses.</b> It decides which slides change. Compare every changed line with the sheet.</li>
<li><b>One file per prompt.</b> Ten assets means ten prompts.</li>
<li><b>Rollout.</b> Google began rolling the feature out on October 29 and said it could take longer than 15 days to appear. On November 9 our Workspace account did not have it yet: Gemini edited the active slide only.</li>
<li><b>Plan.</b> Gemini features depend on your Google plan. Check Google&rsquo;s help pages for current availability.</li>
</ul>

<h2 id="slots">Exact placement: named slots and a script</h2>
<p>When every word has to land in a specific box, across a folder of assets, give the boxes names.</p>
{fig:slot-alt-text|Mockup of a headline text box selected in Google Slides with the Alt text panel open and the title set to slot:headline|A slot tag in the alt text title. Mockup.}
<ol class="steps">
<li>Right-click a text box and choose <b>Alt text</b>.</li>
<li>Put <code>slot:headline</code> in the Title. The key matches the Key column in the sheet.</li>
<li>Repeat for every box that takes copy. The starter templates are already tagged.</li>
</ol>
<p>A script can now find each box by name and set its text to the approved line. The starter pack includes one, written in Apps Script and attached to the messaging sheet. It adds a menu:</p>
{fig:sync-menu-assets|Mockup of the Assets tab with a Collateral menu offering Dry run and Sync copy to assets, and a Flags column reporting one line skipped for being over budget|The Assets tab after a sync. One line was skipped for being over budget. Mockup.}
<ul>
<li><b>Dry run</b> reports what would change and writes nothing.</li>
<li><b>Sync copy to assets</b> writes approved lines into tagged boxes in every deck on the Assets tab.</li>
<li>A line over its budget is skipped and flagged. The script never shrinks type or resizes a box.</li>
<li>Boxes without a tag are never touched.</li>
</ul>
<p>An agent can do the same job. The pack has a short <a href="%SKILLS%">agent contract</a> and thin instruction files for Gemini, Claude and Codex that all point to it. The contract is seven rules: write only approved lines, only into tagged boxes, skip anything over budget, keep the styling, leave the pages alone, look at every changed page, and do not touch a locked asset.</p>
<p>Use Gemini&rsquo;s side panel when one person updates one asset and reads the result. Use slots when the wording is fixed and the assets are many.</p>

<h2 id="approvals">Approve the sheet once</h2>
<p>If ten assets carry the same line, approving ten files is ten chances to disagree. Approve the row once.</p>
{fig:approvals-sidebar|Mockup of the messaging sheet with the Approvals sidebar showing a pending approval, one approver done and one awaiting review|An approval request on the messaging sheet. Mockup.}
<ol class="steps">
<li>Change the rows. Log what changed on the Approvals tab.</li>
<li>In the sheet, open <b>File &rsaquo; Approvals</b>. Add approvers and a due date.</li>
<li>Lock the file for the review.</li>
<li>After approval, unlock, update the assets, and check every changed page.</li>
<li>Lock each released asset so it changes only through the sheet.</li>
</ol>
<p>Two things from <a href="%APPROVALS%">Google&rsquo;s help page</a> shape this order. Unlocking a file during an approval resets the approvals already given. And edits made after approval leave the approval attached to the previous version. So finish the words first, approve, then update.</p>
<p>Approvals are available on eligible work or school accounts. Without them, assign a comment to the approver on the changed rows and record the decision on the Approvals tab.</p>

<h2 id="shift">Layout shift</h2>
<p>Slides does not shrink text to fit a box. A longer line spills out or runs into the element below it.</p>
{fig:layout-shift-before-after|Two versions of the same one-pager: a 41 character headline that fits and an 88 character headline that spills into the subhead|The same headline box with a line inside its budget and a line over it.}
<ul>
<li><b>Budget every slot.</b> Fill the box with the longest line that still looks right, count the characters, and put that number in the sheet.</li>
<li><b>Fix length in the sheet.</b> The Fits column shows the problem before any asset changes.</li>
<li><b>Skip, do not squeeze.</b> An over-budget line stays out until someone shortens it.</li>
<li><b>Look after every update.</b> A character count is an estimate. Wide letters and long words still break lines differently.</li>
<li><b>Update linked objects last</b>, then check the pages they sit on. A table with a new row is taller.</li>
</ul>

<h2 id="pack">The starter pack</h2>
<p><a href="%PACK%"><b>Open the Drive folder</b></a>. Everything is view-only. Make your own copies.</p>
<ul>
<li><a href="%SHEET%">Messaging sheet</a>: Messages, Voice, Assets, Data, Sizes and Approvals tabs.</li>
<li><a href="%T_ONE%">One-pager</a>, US Letter.</li>
<li><a href="%T_BLEED%">One-pager with print bleed</a>, 8.75 &times; 11.25 in, with trim and safe guides.</li>
<li><a href="%T_BRIEF%">Solution brief</a>, two pages.</li>
<li><a href="%T_WP%">Whitepaper</a>: cover, inside page, back.</li>
<li><a href="%T_BATTLE%">Battlecard</a>, Letter landscape.</li>
<li><a href="%SKILLS%">Skills and script</a>: the agent contract, Gemini prompts, a Claude skill, a Codex AGENTS.md and <code>sync_copy.gs</code>.</li>
<li>An approvals checklist and a start-here page.</li>
<li>Added with <a href="/blog/messaging-workshop-brand-style-sheet-google-sheets">part 2</a>: a messaging architecture sheet, a brand style sheet, two more scripts, and a filled-in example for SVG to Slides.</li>
</ul>
<p>The sample copy is for a fictional product called Relay. Replace it with yours.</p>
<p>To install the script: open your copy of the sheet, go to <b>Extensions &rsaquo; Apps Script</b>, paste <code>sync_copy.gs</code>, save, and reload the sheet. Put the URLs of your own template copies on the Assets tab.</p>

<h2 id="status">What we have and have not tested</h2>
<p><i>Updated Nov 9, 2026, after a first round of tests.</i></p>
<ul>
<li><b>Checked:</b> the templates keep their page sizes and slot tags as Google Slides files. The sheet&rsquo;s budget formulas work.</li>
<li><b>Checked:</b> the AI function returns a draft from a fact once you click Generate and fill. Our test account then hit the monthly limit for the AI function after five cells. Limits depend on your plan.</li>
<li><b>Checked, one slide at a time:</b> on a Workspace account with Gemini, we gave the side panel three approved lines for the one-pager and told it to use the words exactly. It showed a preview, we clicked Replace, and all three lines landed word for word. Fonts, sizes, page size and slot tags were unchanged.</li>
<li><b>Whole-deck edit not available to us yet:</b> the same account refused the prompt that pointed at the messaging sheet. Gemini answered that it could only edit the currently active slide. Google said the rollout could take longer than 15 days. Until it reaches you, paste the approved lines into the prompt, one slide at a time.</li>
<li><b>Not yet run end to end:</b> the sync script. Run the dry run first, on copies.</li>
</ul>
<p>We will keep updating this post as we test each part. <a href="/blog/messaging-workshop-brand-style-sheet-google-sheets">Part 2</a> adds the workshop form, the messaging architecture, the brand style sheet and a worked example.</p>
<p style="font-size:14px;color:var(--mute)">The screens in this post are mockups, not captures of Google&rsquo;s products. Google Slides, Google Sheets, Google Drive and Gemini are trademarks of Google LLC.</p>
"""

for k, v in {"GEM_EDIT": GEM_EDIT, "LINKED": LINKED, "APPROVALS": APPROVALS, "AI_FN": AI_FN, "PRE": PRE, "PACK": PACK,
             "SHEET": SHEET, "T_ONE": T_ONE, "T_BLEED": T_BLEED, "T_BRIEF": T_BRIEF, "T_WP": T_WP, "T_BATTLE": T_BATTLE, "SKILLS": SKILLS}.items():
    BODY = BODY.replace(f"%{k}%", v)

MD = f"""# Update Google Slides collateral from one messaging sheet with Gemini

*Nov 9, 2026 · svgslid.es blog*

Write the message once in a sheet. Update every one-pager, brief, whitepaper and battlecard from it.

## TL;DR
- Since Oct 30, 2026, Gemini in Google Slides can edit a whole presentation from one prompt, grounded in a Drive file ({GEM_EDIT}).
- Point that prompt at a messaging sheet and one asset updates in one step.
- For exact wording across many assets, tag text boxes with `slot:<key>` in alt text and use a script or an agent.
- Approve the sheet once. Give every slot a character budget. Look at every changed page.
- Starter pack (templates, sheet, prompts, script): {PACK}

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
Columns: Key, Fact, Draft, Approved line, Budget, Length, Fits, Used in. Draft can use the Sheets AI function ({AI_FN}):

    =AI("Write one line of product marketing copy from this fact. Plain, specific, active voice. No superlatives.", B2)

Needs a Google plan with Gemini. Nested AI functions are not supported. Only Approved line reaches an asset.

## Linked tables and charts
Copy in Sheets, paste in Slides, choose Link to spreadsheet. Tools › Linked objects › Update all. Updates are manual. Tables over 400 cells paste unlinked ({LINKED}). Updates override edits made in Slides.

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
File › Approvals on the sheet ({APPROVALS}). Lock for review. Unlocking during an approval resets approvals; edits after approval leave it attached to the previous version. So: finish words, approve, update assets, lock released assets. Approvals need an eligible work or school account.

## Layout shift
Slides does not shrink text to fit. Budget every slot, fix length in the sheet, skip over-budget lines, look at every changed page, update linked objects last.

## Tested / not tested
Checked: templates keep page sizes and slot tags as Slides files; budget formulas work. The AI function works after a Generate and fill click; our test account hit its monthly limit after five cells. On a Workspace account with Gemini, a single-slide prompt with three approved lines applied them word for word and kept fonts, sizes and slot tags. The whole-deck prompt that references the sheet was refused there ("only able to edit the single currently active slide"); the rollout had not reached the account on Nov 9. The sync script has not been run end to end. Part 2: https://svgslid.es/blog/messaging-workshop-brand-style-sheet-google-sheets

The screens in the post are mockups. Google Slides, Google Sheets, Google Drive and Gemini are trademarks of Google LLC.
"""

POST = {
    "slug": "google-slides-collateral-messaging-sheet-gemini",
    "date": "2026-11-09",
    "date_h": "Nov 9, 2026",
    "read": "14 min read",
    "jump": ("pack", "<b>Skip ahead:</b> the Drive starter pack with templates, the messaging sheet, prompts and the sync script"),
    "kicker": "Product marketing in Slides",
    "title": "Update Google Slides collateral from one messaging sheet with Gemini",
    "h1": "Update Google Slides collateral from one messaging sheet with Gemini",
    "dek": "Write the message once in a sheet. Update every one-pager, brief, whitepaper and battlecard from it. Templates, prompts and a script included.",
    "desc": "Gemini in Google Slides can now edit a whole deck from one prompt. How to pair it with a messaging sheet, real page sizes, slot tags, approvals and a free starter pack.",
    "hero": ("hero-collateral-gemini", "Mockup of a one-pager in Google Slides with the Gemini side panel showing an update prompt and a summary of changed text boxes"),
    "og": "og-collateral-gemini.png",
    "tldr": [
        "Since Oct 30, 2026, <b>Gemini in Google Slides can edit a whole presentation from one prompt</b>, grounded in a Drive file.",
        "Point that prompt at a <b>messaging sheet</b> and one asset updates in one step.",
        "For exact wording across many assets, <b>tag text boxes with a slot name</b> and use a script or an agent.",
        "<b>Approve the sheet once.</b> Give every slot a character budget. Look at every changed page.",
        "The <a href=\"#pack\">starter pack</a> has five templates, the sheet, prompts and the script.",
    ],
    "body": BODY,
    "sources": [
        ("Edit entire presentations with Gemini in Google Slides (Google Workspace Updates, Oct 30, 2026)", GEM_EDIT),
        ("Link a chart, table, or slides to Google Docs or Slides (Google Docs Editors Help)", LINKED),
        ("Get approvals on files in Google Drive (Google Drive Help)", APPROVALS),
        ("Use the AI function in Google Sheets (Google Docs Editors Help)", AI_FN),
    ],
    "md": MD,
}
