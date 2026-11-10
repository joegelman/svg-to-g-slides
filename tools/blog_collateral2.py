"""Blog post, part 2 of the collateral series: workshop form, messaging architecture, brand style sheet.

Figures: tools/collateral2_images.py. The SVG to Slides copy quoted here is the brand's
own published copy. Workshop frameworks are described in our own words.
"""
from blog_collateral import PACK, SKILLS, AI_FN, GEM_EDIT, PRE

S = "https://docs.google.com/spreadsheets/d/%s/copy"
ARCH_SHEET = S % "1_KmNCxv005r3ZD9RZz4kwZZO9f2WJ0cBXehgwvlhv0Y"
STYLE_SHEET = S % "18awgdkUBwAs01BCdg0cLWyVBx-jPJVPfEUZvfaNExDo"
EXAMPLE = "https://drive.google.com/drive/folders/1EOSAfzAkwnhXBWwTkqBSMdMxF-BH9t50"
EX_ARCH = "https://docs.google.com/spreadsheets/d/1pqFKmoUejTFxgOmW-TVWAq3HIIl7B6DhzRY1a3qdTYo/edit"
EX_STYLE = "https://docs.google.com/spreadsheets/d/1cFcoXDtE0lmqUklkeU7Zj9uiDA4k4zQE-loNoooriuQ/edit"
EX_ONE = "https://docs.google.com/presentation/d/1xOtwK481gb6sqjOiuqm8Tjg41qPYQ0rYQjYnUCLxgN8/edit"
EX_DECK = "https://docs.google.com/presentation/d/1-_8xMfLHxBo2bo3829dkkL3RmWX_lkwh0OkMlPok_PM/edit"
PART1 = "/blog/google-slides-collateral-messaging-sheet-gemini"

BODY = """
<h2 id="what">What part 2 adds</h2>
<p><a href="%PART1%">Part 1</a> set up a messaging sheet and showed how to push its approved lines into Google Slides&trade; assets. It started with the copy already written.</p>
<p>This part covers what comes before and beside that sheet:</p>
<ul>
<li><b>A workshop, run as a Google Form</b>, that collects the raw material for the messaging.</li>
<li><b>A messaging architecture</b>: five levels of message, drafted from the workshop answers and approved line by line.</li>
<li><b>A brand style sheet</b>: colours, type, layout, logo, imagery, voice and personality in one Google Sheets&trade; file that scripts, agents and Gems can read.</li>
<li><b>A worked example</b>: all of it filled in for SVG to Slides.</li>
</ul>
{fig:flow-workshop-to-assets|Flow diagram: workshop form, workshop tab, architecture, messages, assets, with the brand style sheet and its export block feeding fonts, sizes and colours by role|The messaging sheet carries the words. The style sheet carries how they look and sound.}

<h2 id="workshop">The workshop, as a Google Form</h2>
<p>A messaging workshop is a set of questions asked in a fixed order. A form does that well. People answer on their own time, the answers land in one row, and nobody has to take notes.</p>
{fig:workshop-form|Mockup of a Google Form titled Messaging workshop, on section 3 of 11, Champion, with two answered text questions and a multiple choice question|One section of the workshop form. Mockup.}
<p>The form has 38 questions in 11 sections:</p>
<ol class="steps">
<li><b>Company and focus.</b> What it is, in one sentence. Where it should be in two years.</li>
<li><b>Market.</b> The category you are in, what you get mistaken for, and the alternatives a buyer weighs.</li>
<li><b>Champion.</b> The job title, what they are responsible for, the explicit goal and the personal one.</li>
<li><b>Target organizations.</b> Size, verticals, and what must be true for a fit.</li>
<li><b>Buying scenarios.</b> What is happening when they go looking. One primary, the rest secondary.</li>
<li><b>Awareness.</b> A 1 to 5 scale, from &ldquo;not sure I have this problem&rdquo; to &ldquo;why are you better?&rdquo;</li>
<li><b>Needs.</b> Must have, important to have, nice to have.</li>
<li><b>Selling proposition.</b> What is unique, why it is relevant, what makes it believable.</li>
<li><b>Sweet spot.</b> What you do for customers that rivals cannot.</li>
<li><b>Message raw material.</b> Context, problem, promise, how it works, benefits, secondary points.</li>
<li><b>Personality and tone.</b> One of twelve archetypes, a runner-up, and four tone scales.</li>
</ol>
<p>The questions live on the <b>Workshop</b> tab of the messaging sheet: key, section, question, type and choices. A short script, <code>workshop_form.gs</code>, reads that tab, builds the form, and points its responses at the same spreadsheet. To change a question, change the row and build a new form.</p>
<p>Three columns on the Workshop tab turn responses into inputs:</p>
<ul>
<li><b>Latest response</b> reads the newest row of the Responses tab, matched by question text.</li>
<li><b>Override</b> is where you type a correction or a better answer after the session.</li>
<li><b>Final</b> is the override if there is one, otherwise the response. Everything downstream reads Final.</li>
</ul>
<p>You can skip the form and type straight into Override. The example below was filled that way.</p>

<h2 id="architecture">The messaging architecture</h2>
<p>The workshop produces notes. The architecture turns them into a small set of lines, ordered the way a buyer meets them.</p>
{fig:messaging-architecture-levels|Messaging architecture for SVG to Slides on five levels: lead message, then context, problem and promise, then three how-it-works steps, then benefits and proof, then secondary points|The five levels, filled in for SVG to Slides.}
<ul>
<li><b>Primary.</b> The lead message and a positioning statement.</li>
<li><b>Level 2.</b> Context, problem, promise. The short narrative.</li>
<li><b>Level 3.</b> How it works, in three steps or pillars.</li>
<li><b>Level 4.</b> Benefits, and the proof behind them.</li>
<li><b>Level 5.</b> Secondary points for further down the page.</li>
</ul>
<p>Each of the 17 rows on the <b>Architecture</b> tab names the workshop answers it draws on, joins them into a Source notes cell, and drafts a line from them with <a href="%AI_FN%">the AI function</a>:</p>
%PRE%=AI("Promise. Write this element of a B2B messaging hierarchy from the workshop notes. One or two sentences. Plain, specific, active voice.", E6)</pre>
{fig:architecture-tab|Mockup of the Architecture tab showing source notes, Gemini drafts and approved lines for tagline, positioning, context and problem|Drafts next to approved lines. The drafts shown are the ones Gemini returned in our test. Mockup of the sheet.}
<p>The drafts are a starting point. For the lead message Gemini returned &ldquo;Convert SVG files into editable vector shapes directly inside Google Slides.&rdquo; The approved line is &ldquo;Editable SVGs in Google Slides.&rdquo; Same claim, less than half the length. The Approved line column is typed by a person and it is the only one that moves on.</p>

<h2 id="messages">From architecture to slots</h2>
<p>The <b>Messages</b> tab is the same one from part 1, with three more columns:</p>
<ul>
<li><b>Role:</b> eyebrow, headline, subhead, title, body, stat, label, cta or legal. The style sheet sets type by role.</li>
<li><b>Source:</b> the architecture row this slot draws on, if any.</li>
<li><b>Source line:</b> that row&rsquo;s approved line, looked up by formula.</li>
</ul>
<p>A headline slot takes the lead message and fits it to 40 characters. A subhead slot takes the positioning statement. When an architecture line changes, the source line changes with it and the slot is due for review.</p>
<p>Three adjunct tabs handle what happens after the first version:</p>
<ul>
<li><b>Refinements:</b> a log of every change to a line. Date, key, previous line, new line, reason, source.</li>
<li><b>Audiences:</b> variants of a line for a named reader, drafted by formula from the base line and approved separately.</li>
<li><b>Proof:</b> each claim, its evidence, where the evidence lives, and when it was last checked.</li>
</ul>

<h2 id="style">A style sheet for Workspace</h2>
<p>Web pages keep their look in a style sheet. Collateral in Slides usually keeps it in someone&rsquo;s head. The brand style sheet is a Google Sheets file that writes it down in a form a script can read.</p>
{fig:style-sheet-colors-type|Mockups of the Colors tab with tokens, hex values, roles and swatches, and the Type tab with roles, fonts, weights and point sizes for print and deck|The Colors and Type tabs for SVG to Slides. Mockup.}
<ul>
<li><b>Colors:</b> a token, a hex value, a role, where to use it, and what colour text goes on it.</li>
<li><b>Type:</b> one row per role. Font, weight, size for print, size for decks, line spacing, colour token.</li>
<li><b>Layout:</b> margins, bleed, safe margin, gaps, corner rules.</li>
<li><b>Logo:</b> the file, clear space, minimum size, allowed backgrounds, what not to do.</li>
<li><b>Imagery:</b> style, background, palette, what to avoid, export format.</li>
<li><b>Voice:</b> each rule with a do, a do not, and a before and after.</li>
<li><b>Personality:</b> the archetype and tone scores from the workshop, plus &ldquo;we are&rdquo; and &ldquo;we are not&rdquo;.</li>
</ul>
<p>Roles tie the two sheets together. The Messages tab says a slot is a headline. The Type tab says a headline is Overpass SemiBold at 34 points in ink. <code>apply_style.gs</code> reads both and sets the font, size and colour on every tagged text box, without touching the words.</p>

<h2 id="export">The export block</h2>
<p>The <b>Export</b> tab joins every other tab into one cell of plain text, by formula. Change a hex value on the Colors tab and the block changes.</p>
{fig:style-export-block|A dark code block listing colours, type, voice and personality rules for SVG to Slides, with arrows to three users: Gems, agents and a script|One cell holds the whole style sheet as text.}
<p>That one cell is what you hand to anything that writes or reviews for the brand. An agent reads it before it drafts. A reviewer pastes it next to a deck. A Gem carries it permanently.</p>

<h2 id="gems">Gems</h2>
<p>A Gem is a saved set of instructions in Gemini. The <b>Gems</b> tab holds the instructions for five of them. Paste the instructions into a new Gem, then paste the export block under them.</p>
{fig:gems-tab|Five cards: message drafter, copy editor, image maker, image prep, asset checker|The five Gems in the pack.}
<ul>
<li><b>Message drafter</b> writes a line from a fact, for a role and a budget. It may not add a claim that is not in the fact.</li>
<li><b>Copy editor</b> lists each line that breaks a voice rule and gives a corrected line.</li>
<li><b>Image maker</b> generates images to the Imagery rules: palette only, no text, no logos.</li>
<li><b>Image prep</b> crops a supplied image to a slot and applies the brand treatment.</li>
<li><b>Asset checker</b> compares a deck with both sheets and reports. It changes nothing.</li>
</ul>
<p>Whether Gems and image generation are available depends on your Google plan.</p>

<h2 id="example">Worked example: SVG to Slides</h2>
<p>We filled the whole scaffold in for our own product. The answers come from what SVG to Slides already says about itself on this site and on its store listing.</p>
{fig:svgs-one-pager|The SVG to Slides one-pager: mark, headline Editable SVGs in Google Slides, a problem paragraph, three steps, four benefits, three stats and an Add to Chrome button, with notes on which sheet each slot comes from|The one-pager, built from the two sheets. Rendered from the template file.}
<ul>
<li><a href="%EX_ARCH%">Messaging architecture</a>: workshop answers, 17 architecture lines, 25 slots, proof log.</li>
<li><a href="%EX_STYLE%">Brand style sheet</a>: nine colour tokens, nine type roles, seven voice rules, the export block.</li>
<li><a href="%EX_ONE%">One-pager</a>, US Letter, and a <a href="%EX_DECK%">two-slide deck</a>, 16:9. Every text box is tagged.</li>
</ul>
<p>Three things the exercise showed:</p>
<ul>
<li><b>Most of it already existed.</b> The lead message, the problem statement and the four benefits were on the homepage. The scaffold gave them one address each.</li>
<li><b>Proof needs a date.</b> A store rating is true on the day you check it. The Proof tab records that day.</li>
<li><b>Personality was the gap.</b> The copy rules were written down. The archetype and tone scores were not, so the sheet marks them as proposed until a workshop confirms them.</li>
</ul>

<h2 id="tests">What happened when we ran the formulas</h2>
<ul>
<li><b>The AI function works, with a click.</b> Formulas that arrive by import or through the API show as text until you select them and click <b>Generate and fill</b>. Select a range and one click covers every AI cell in it.</li>
<li><b>There is a monthly limit.</b> Our test account generated five cells and then Sheets reported that the monthly limit for the AI function was reached. Limits depend on your plan.</li>
<li><b>The Slides side panel was not available on that account.</b> It still showed the Try Gemini prompt, so the whole-deck edit from <a href="%PART1%">part 1</a> remains untested by us.</li>
<li><b>The sheet formulas hold.</b> Latest response, Final, Source notes, Source line, Length, Fits and the export block all compute as Google Sheets files.</li>
<li><b>Not yet run:</b> <code>workshop_form.gs</code>, <code>apply_style.gs</code> and <code>sync_copy.gs</code>. Test them on copies.</li>
</ul>

<h2 id="pack">What is new in the starter pack</h2>
<p><a href="%PACK%"><b>Open the Drive folder</b></a>. Everything is view-only. Make your own copies.</p>
<ul>
<li><a href="%ARCH_SHEET%">Messaging architecture</a>: Workshop, Architecture, Messages, Refinements, Audiences, Proof, Assets and Approvals tabs. Sample copy for a fictional product.</li>
<li><a href="%STYLE_SHEET%">Brand style sheet</a>: Colors, Type, Layout, Logo, Imagery, Voice, Personality, Gems and Export tabs.</li>
<li><a href="%SKILLS%">Scripts</a>: <code>workshop_form.gs</code> builds the form, <code>apply_style.gs</code> applies type and colour by role, <code>sync_copy.gs</code> now builds both menus.</li>
<li><a href="%EXAMPLE%">Example: SVG to Slides</a>, the filled-in set described above.</li>
</ul>
<p>To install the scripts: open your copy of the messaging architecture sheet, go to <b>Extensions &rsaquo; Apps Script</b>, add the three files, save, and reload the sheet. <b>Workshop &rsaquo; Build the form</b> creates the form and writes its links to the Workshop tab.</p>
<p style="font-size:14px;color:var(--mute)">The screens in this post are mockups, not captures of Google&rsquo;s products. Google Slides, Google Sheets, Google Forms, Google Drive and Gemini are trademarks of Google LLC.</p>
"""
for k, v in {"PART1": PART1, "AI_FN": AI_FN, "PRE": PRE, "PACK": PACK, "SKILLS": SKILLS, "ARCH_SHEET": ARCH_SHEET, "STYLE_SHEET": STYLE_SHEET,
             "EXAMPLE": EXAMPLE, "EX_ARCH": EX_ARCH, "EX_STYLE": EX_STYLE, "EX_ONE": EX_ONE, "EX_DECK": EX_DECK}.items():
    BODY = BODY.replace(f"%{k}%", v)

TITLE = "Run a messaging workshop in Google Forms and build a brand style sheet in Google Sheets"
MD = f"""# {TITLE}

*Nov 9, 2026 · svgslid.es blog · Part 2 of the collateral series (part 1: https://svgslid.es{PART1})*

## TL;DR
- A messaging workshop runs as a Google Form: 38 questions in 11 sections, built by script from a Workshop tab.
- Answers feed a five-level messaging architecture (primary; context, problem, promise; how; benefits and proof; secondary). Drafts come from =AI(); a person types the approved line.
- The Messages tab gains Role, Source and Source line. Adjunct tabs: Refinements, Audiences, Proof.
- A brand style sheet holds Colors, Type, Layout, Logo, Imagery, Voice, Personality and Gems, and exports itself as one text cell for scripts, agents and Gems.
- Worked example for SVG to Slides: {EXAMPLE}
- Starter pack: {PACK}

## Workshop sections
Company and focus; market; champion; target organizations; buying scenarios; awareness (1 to 5); needs (must, important, nice); selling proposition (unique, relevant, believable); sweet spot; message raw material; personality and tone (twelve archetypes, four tone scales).

Workshop tab columns: Latest response (newest form row, matched by question text), Override, Final. Everything downstream reads Final.

## Architecture
17 rows on five levels. Each row joins its workshop inputs into Source notes and drafts with the AI function ({AI_FN}):

    =AI("Promise. Write this element of a B2B messaging hierarchy from the workshop notes. One or two sentences. Plain, specific, active voice.", E6)

Example from our test: Gemini drafted "Convert SVG files into editable vector shapes directly inside Google Slides." The approved lead message is "Editable SVGs in Google Slides."

## Style sheet
Type is set by role (eyebrow, headline, subhead, title, body, stat, label, cta, legal). The Messages tab gives each slot a role; `apply_style.gs` sets font, size and colour on tagged text boxes. The Export tab joins all tabs into one cell of text.

## Gems
Message drafter, copy editor, image maker, image prep, asset checker. Paste the instructions into a Gem, then the export block. Availability depends on your Google plan.

## Test results
- AI formulas written by import or API show as text until you click Generate and fill. One click covers a selected range.
- Our test account hit the monthly AI function limit after five cells.
- The Slides Gemini side panel was not available on that account, so the whole-deck edit is still untested by us.
- Sheet formulas and the export block compute. The three scripts have not been run yet.

The screens in the post are mockups. Google Slides, Google Sheets, Google Forms, Google Drive and Gemini are trademarks of Google LLC.
"""

POST = {
    "slug": "messaging-workshop-brand-style-sheet-google-sheets",
    "date": "2026-11-09",
    "date_h": "Nov 9, 2026",
    "read": "11 min read",
    "jump": ("example", "<b>Skip ahead:</b> the worked example, with every sheet and template filled in for SVG to Slides"),
    "kicker": "Product marketing in Slides, part 2",
    "title": TITLE,
    "h1": TITLE,
    "dek": "A form collects the answers. One sheet turns them into messaging. A second sheet holds the brand's colours, type and voice in a form scripts and Gems can read.",
    "desc": "Run a messaging workshop as a Google Form, turn the answers into a five-level messaging architecture, and keep fonts, colours and voice in a brand style sheet in Google Sheets.",
    "hero": ("hero-messaging-architecture", "Messaging architecture for SVG to Slides on five levels, from the lead message down to secondary points"),
    "og": "og-messaging-architecture.png",
    "tldr": [
        "A <b>messaging workshop runs as a Google Form</b>: 38 questions in 11 sections, built by script from one tab.",
        "Answers feed a <b>five-level messaging architecture</b>. Gemini drafts each line. A person types the approved one.",
        "A <b>brand style sheet</b> holds colours, type, voice and personality, and exports itself as one cell of text.",
        "<b>Roles</b> tie the two sheets together, so a script can set fonts and colours on tagged text boxes.",
        "The <a href=\"#example\">worked example</a> fills all of it in for SVG to Slides.",
    ],
    "body": BODY,
    "sources": [
        ("Use the AI function in Google Sheets (Google Docs Editors Help)", AI_FN),
        ("Edit entire presentations with Gemini in Google Slides (Google Workspace Updates, Oct 30, 2026)", GEM_EDIT),
    ],
    "md": MD,
}
