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
EX_ONE = "https://docs.google.com/presentation/d/1QTHRDkswETR8h4Bg4v1VbhZdk6-UUg8lbwojTUuo8aw/edit"
EX_DECK = "https://docs.google.com/presentation/d/1v-oovKABw9tOm4Kdp7A7uU1Ae9je-rt2rEEpcNK53pY/edit"
LIB_ICON = "https://docs.google.com/presentation/d/1aiPHjI3cdyQO8QnRu5GYpR2mLv0aFSCbSKramv4vOc0/edit"
LIB_UI = "https://docs.google.com/presentation/d/1YiYVc8NgGR9VfWS5ySz5-0LwCbhVUtaRYRRBHdKrTpE/edit"
RECIPES = "https://docs.google.com/spreadsheets/d/1ehY-jZ3Tq1q7070H8WEEniZr_yqYNPwik_4nHf-OCQE/edit"
PAGE_SOL = "https://docs.google.com/presentation/d/11x2sGv4ZbPbD1BBlyp9bVaXt2fYli2Ki6l2XpgXgY08/edit"
PAGE_PROD = "https://docs.google.com/presentation/d/1cG0kRn9CByAw4vw6dv9H9lJBDx8SfAqwn8-bsuzlybA/edit"
PART1 = "/blog/google-slides-collateral-messaging-sheet-gemini"

BODY = """
<h2 id="what">What part 2 adds</h2>
<p><a href="%PART1%">Part 1</a> set up a messaging sheet and showed how to push its lines into Google Slides&trade; assets. It started with the briefs already written.</p>
<p>This part covers what comes before and beside that sheet:</p>
<ul>
<li><b>A workshop, run as a Google Form</b>, that collects the raw material for the messaging.</li>
<li><b>A messaging architecture</b>: five levels of message, drafted from the workshop answers. It supplies the briefs for the Messages tab.</li>
<li><b>A brand style sheet</b>: colours, type, layout, logo, imagery, voice and personality in one Google Sheets&trade; file that scripts, agents and Gems can read.</li>
<li><b>Icon and UI libraries</b>: master decks of native shapes that asset decks pull from.</li>
<li><b>Page recipes</b>: block formulas taken from seven live solution and product pages.</li>
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
<p>The questions live on the <b>Workshop</b> tab of the messaging sheet: key, section, question, type and choices. The <b>Workshop &rsaquo; Build the form</b> menu item reads that tab, builds the form, and points its responses at the same spreadsheet. To change a question, change the row and build a new form.</p>
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
{fig:architecture-tab|Mockup of the Architecture tab showing source notes, Gemini drafts and the line a person set for tagline, positioning, context and problem|Drafts next to the lines we kept. The drafts shown are the ones Gemini returned in our test. Mockup of the sheet.}
<p>The drafts are a starting point. For the lead message Gemini returned &ldquo;Convert SVG files into editable vector shapes directly inside Google Slides.&rdquo; The line we kept is &ldquo;Editable SVGs in Google Slides.&rdquo; Same claim, less than half the length. The architecture is the one place a person still sets the line. There are 17 of them, and every brief downstream is taken from them.</p>

<h2 id="messages">From architecture to slots</h2>
<p>The <b>Messages</b> tab is the one from <a href="%PART1%">part 1</a>: Key, Role, Source, Brief, Prompt, Line, Budget. Two of its columns connect it to the rest:</p>
<ul>
<li><b>Role:</b> eyebrow, headline, subhead, title, body, stat, label, cta or legal. The Rules tab holds a recipe per role, and the style sheet sets type by role.</li>
<li><b>Source:</b> the architecture row this slot draws on, if any. The Brief is then that row&rsquo;s line, looked up by formula. Slots with no source get a brief typed by hand.</li>
</ul>
<p>A headline slot takes the lead message as its brief. The AI function fits it to 40 characters under the headline recipe. A subhead slot takes the positioning statement. When an architecture line changes, the brief changes with it and the line is generated again.</p>
<p>There is no approval column. Part 1 explains what replaced it and what that gives up.</p>
<p>Three adjunct tabs handle what happens after the first version:</p>
<ul>
<li><b>Refinements:</b> a log of every change to a line. Date, key, previous line, new line, reason, source.</li>
<li><b>Audiences:</b> variants of a line for a named reader, drafted by formula from the base line.</li>
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
<p>Roles tie the two sheets together. The Messages tab says a slot is a headline. The Type tab says a headline is Overpass SemiBold at 34 points in ink. The <b>Apply style</b> menu item reads both and sets the font, size and colour on every tagged text box, without touching the words.</p>

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
<li><a href="%EX_ARCH%">Messaging architecture</a>: workshop answers, 17 architecture lines, 82 slots, rules, proof log.</li>
<li><a href="%EX_STYLE%">Brand style sheet</a>: nine colour tokens, nine type roles, seven voice rules, the export block.</li>
<li><a href="%EX_ONE%">One-pager</a>, US Letter, and a <a href="%EX_DECK%">three-slide deck</a>, 16:9. Every text box and icon is tagged.</li>
</ul>
<p>The graphics follow the same rule as the copy: native objects, tagged by name, pulled from one source.</p>

<h3 id="libraries">Icon and UI libraries</h3>
<p>The Google Slides API cannot create a custom shape. Apps Script can copy one from another deck. So icons and mockups live in two master decks, and asset decks pull from them and keep their file IDs.</p>
<ul>
<li><a href="%LIB_ICON%">Icon library</a>: 85 icons from Phosphor Icons, an MIT-licensed set, one per slide, placed as native shapes by the SVG to Slides converter.</li>
<li><a href="%LIB_UI%">UI library</a>: 13 mockups, one per slide. Shapes are native and labels are ordinary text boxes.</li>
<li><b>Tags.</b> Every element of a library item carries <code>lib:&lt;name&gt;</code> in its alt text. An icon slot in an asset carries <code>icon:step_1</code>. A mockup slot carries <code>ui:fill-picker</code>.</li>
<li><b>Search.</b> Each library slide has a 6 point white text box next to the item with its name and keywords. Ctrl+F in the deck finds it.</li>
<li><b>Icons tab.</b> One row per icon slot: key, icon, colour token, size. The Icon cell is a dropdown of every icon in the library. Type to filter.</li>
<li><b>Place icons and UIs</b> replaces each tagged slot with the library item, scaled to the slot and coloured from the style sheet.</li>
<li><b>Add to library</b> takes the link from <a href="/convert">the web converter</a>, appends each converted slide to a library, tags it, and adds it to the dropdown.</li>
</ul>
{fig:vector-ui-mock|Deck slide titled In your deck showing a simple editor mockup made of native shapes, with notes that the shapes came from Gemini's SVG and the labels are text boxes|The first mockup. Gemini wrote the SVG. The shapes are native and the labels are text boxes. Rendered from the template file.}
<p>The first mockup was drawn by Gemini as code. We asked the Slides side panel for SVG code of an editor mockup, limited to the brand palette and to rectangles, circles and text. It returned 16 elements, and the converter turned them into native shapes and two text boxes. The other twelve were drawn the same way, as plain SVG.</p>
<p>Two things went wrong with mockup text, and both are fixed in the script:</p>
<ul>
<li><b>Labels wrapped.</b> Slides always wraps at the edge of a text box, and it renders Verdana wider than we estimated. The boxes are now half again as wide.</li>
<li><b>Text did not scale.</b> A mockup placed smaller than its library size kept its full-size type. The script now sets mockup type from the height of its box.</li>
</ul>

<h3 id="recipes">Page recipes</h3>
<p>To get past a one-pager we read seven live pages block by block: three solution pages (Pitch for sales teams, Ramp for consulting firms, Gong for revenue enablement) and four product pages (Ramp corporate cards, Pitch, Riskified Policy Intelligence, Close communication).</p>
<ul>
<li><b>Twelve blocks</b> cover all seven: hero, proof bar, problem, pillar trio, feature row, benefit list, feature grid, how it works, FAQ, closing CTA, fact columns, testimonial.</li>
<li><b>The feature row is the repeating unit.</b> A title of 3 to 7 words, a body of 17 to 28 words, and one UI crop that shows what the body names.</li>
<li><b>Solution pages</b> keep feature names out of headlines until a grid near the end. Headlines state the reader&rsquo;s result.</li>
<li><b>Product pages</b> name the feature in the hero and explain the mechanism before the gain. Flat fact lists carry terms and limits.</li>
</ul>
<p>The <a href="%RECIPES%">page recipes sheet</a> has a headline formula, a body formula, lengths and a visual for each block, and the block order for both page types. We filled them in for SVG to Slides as two decks, one block per slide: a <a href="%PAGE_SOL%">solution page</a> for product marketing teams and a <a href="%PAGE_PROD%">product page</a> for the Chrome extension. Their 57 lines sit on the same Messages tab as everything else. We left the testimonial block out. We have no customer quotes on file.</p>

<p>The example sheet also has a <b>Home</b> tab: one row per tab with what it holds, who edits it, and a live count. Tabs are coloured by stage: inputs, working copy, output, logs.</p>
<p>Three things the exercise showed:</p>
<ul>
<li><b>Most of it already existed.</b> The lead message, the problem statement and the four benefits were on the homepage. The scaffold gave them one address each.</li>
<li><b>Proof needs a date.</b> A store rating is true on the day you check it. The Proof tab records that day.</li>
<li><b>Personality was the gap.</b> The copy rules were written down. The archetype and tone scores were not, so the sheet marks them as proposed until a workshop confirms them.</li>
</ul>

<h2 id="tests">What happened when we ran it</h2>
<p><i>Updated Nov 10, 2026.</i></p>
<ul>
<li><b>The AI function works, with a click.</b> Formulas written by a script, an import or the API show as text until you select them and click <b>Generate and fill</b>. Select a range and one click covers every AI cell in it.</li>
<li><b>There is a monthly limit.</b> Our first test account generated five cells and then Sheets reported that the monthly limit for the AI function was reached. Limits depend on your plan.</li>
<li><b>The Line formulas are not proven yet.</b> All 82 were waiting for Generate and fill when we wrote this. We have not seen how well Gemini holds the character limits.</li>
<li><b>Gemini in Slides edits one slide for us today.</b> On a Workspace account with Gemini, a prompt with three lines changed the one-pager word for word and kept fonts, sizes and slot tags. The whole-deck prompt from <a href="/blog/google-slides-collateral-messaging-sheet-gemini">part 1</a> was refused: the rollout had not reached the account.</li>
<li><b>Gemini writes usable SVG.</b> With the palette and the allowed elements spelled out in the prompt, the code converted without edits. It shortened the label we asked for.</li>
<li><b>The sheet formulas hold.</b> Latest response, Final, Source notes, Brief, Prompt, Length, Fits and the export block all compute as Google Sheets files.</li>
<li><b>The form builder works.</b> It built the 38-question form for the example on its first run and added the Responses tab.</li>
<li><b>Dry run works.</b> It opened four decks and reported between zero and three slots to change in each, with no flags.</li>
<li><b>Place icons and UIs works</b>, after the two text fixes above. Decks kept their file IDs.</li>
<li><b>Scripts need the right owner.</b> A personal Google account refused the permission request with &ldquo;This app is blocked&rdquo;. A sheet owned by a different account showed an unverified-app warning. A copy owned by the Workspace account that runs it worked.</li>
<li><b>Link chips break the Assets tab.</b> Two deck URLs had been turned into chips, and the script could not open them. Keep them as plain text.</li>
<li><b>Not yet run end to end:</b> Sync all with generated lines, and Add to library.</li>
</ul>

<h2 id="pack">What is new in the starter pack</h2>
<p><a href="%PACK%"><b>Open the Drive folder</b></a>. Everything is view-only. Make your own copies.</p>
<ul>
<li><a href="%EXAMPLE%">Example: SVG to Slides</a>, the filled-in set described above. Start here.</li>
<li><a href="%EX_ARCH%">Messaging sheet</a> with the script attached, <a href="%EX_STYLE%">brand style sheet</a>, <a href="%LIB_ICON%">icon library</a>, <a href="%LIB_UI%">UI library</a>, <a href="%RECIPES%">page recipes</a>, and the two page decks.</li>
<li><a href="%ARCH_SHEET%">Messaging architecture</a> and <a href="%STYLE_SHEET%">brand style sheet</a> for a fictional product. These two are the first version: the architecture sheet still has Draft and Approved line columns and no script.</li>
<li><a href="%SKILLS%">Scripts</a> as separate files. These are also the first versions. The current script is the one attached to the example sheet.</li>
</ul>
<p>To set up: copy the example messaging sheet. The script comes with it. Reload, and the Collateral and Workshop menus appear. Point <code>STYLE_SHEET_URL</code>, <code>ICON_LIBRARY_URL</code> and <code>UI_LIBRARY_URL</code> in the script at your own copies. <b>Workshop &rsaquo; Build the form</b> creates the form and writes its links to the Workshop tab.</p>
<p style="font-size:14px;color:var(--mute)">The screens in this post are mockups, not captures of Google&rsquo;s products. Google Slides, Google Sheets, Google Forms, Google Drive and Gemini are trademarks of Google LLC.</p>
"""
for k, v in {"PART1": PART1, "AI_FN": AI_FN, "PRE": PRE, "PACK": PACK, "SKILLS": SKILLS, "ARCH_SHEET": ARCH_SHEET, "STYLE_SHEET": STYLE_SHEET,
             "EXAMPLE": EXAMPLE, "EX_ARCH": EX_ARCH, "EX_STYLE": EX_STYLE, "EX_ONE": EX_ONE, "EX_DECK": EX_DECK, "LIB_ICON": LIB_ICON, "LIB_UI": LIB_UI, "RECIPES": RECIPES, "PAGE_SOL": PAGE_SOL, "PAGE_PROD": PAGE_PROD}.items():
    BODY = BODY.replace(f"%{k}%", v)

TITLE = "Run a messaging workshop in Google Forms and build a brand style sheet in Google Sheets"
MD = f"""# {TITLE}

*Nov 9, 2026 · svgslid.es blog · Part 2 of the collateral series (part 1: https://svgslid.es{PART1})*

## TL;DR
- A messaging workshop runs as a Google Form: 38 questions in 11 sections, built by script from a Workshop tab.
- Answers feed a five-level messaging architecture (primary; context, problem, promise; how; benefits and proof; secondary). Drafts come from =AI(); a person sets each of the 17 lines.
- The Messages tab takes each brief from the architecture and has Gemini write the line under a recipe per role and a character limit. No approval column. Adjunct tabs: Refinements, Audiences, Proof.
- Icons and UI mockups live in two master library decks of native shapes; asset decks pull from them by tag.
- Page recipes: twelve block formulas from seven live solution and product pages, filled in as two decks.
- A brand style sheet holds Colors, Type, Layout, Logo, Imagery, Voice, Personality and Gems, and exports itself as one text cell for scripts, agents and Gems.
- Worked example for SVG to Slides: {EXAMPLE}
- Starter pack: {PACK}

## Workshop sections
Company and focus; market; champion; target organizations; buying scenarios; awareness (1 to 5); needs (must, important, nice); selling proposition (unique, relevant, believable); sweet spot; message raw material; personality and tone (twelve archetypes, four tone scales).

Workshop tab columns: Latest response (newest form row, matched by question text), Override, Final. Everything downstream reads Final.

## Architecture
17 rows on five levels. Each row joins its workshop inputs into Source notes and drafts with the AI function ({AI_FN}):

    =AI("Promise. Write this element of a B2B messaging hierarchy from the workshop notes. One or two sentences. Plain, specific, active voice.", E6)

Example from our test: Gemini drafted "Convert SVG files into editable vector shapes directly inside Google Slides." The line we kept is "Editable SVGs in Google Slides."

## Style sheet
Type is set by role (eyebrow, headline, subhead, title, body, stat, label, cta, legal). The Messages tab gives each slot a role; the Apply style menu item sets font, size and colour on tagged text boxes. The Export tab joins all tabs into one cell of text.

## Gems
Message drafter, copy editor, image maker, image prep, asset checker. Paste the instructions into a Gem, then the export block. Availability depends on your Google plan.

## Libraries and page recipes
- Icon library ({LIB_ICON}): 85 Phosphor icons (MIT), one per slide, native shapes tagged lib:<name>, with a small white keyword label for Ctrl+F. UI library ({LIB_UI}): 13 mockups.
- Asset slots are tagged icon:<key> and ui:<name>. Place icons and UIs swaps them for library shapes and keeps the deck's file ID. Add to library appends converted slides from svgslid.es/convert. The Icons tab has a searchable dropdown of library names.
- Page recipes ({RECIPES}): hero, proof bar, problem, pillar trio, feature row, benefit list, feature grid, how it works, FAQ, closing CTA, fact columns, testimonial. Solution pages keep feature names out of headlines until a grid; product pages name the feature first and explain the mechanism. Filled in as a solution page deck ({PAGE_SOL}) and a product page deck ({PAGE_PROD}).

## Test results (Nov 10, 2026)
- AI formulas written by script, import or API show as text until you click Generate and fill. One click covers a selected range. The 82 Line formulas had not been generated when this was written.
- Our first test account hit the monthly AI function limit after five cells.
- Gemini in Slides, on a Workspace account: a single-slide prompt applied three lines word for word and kept fonts, sizes and slot tags. The whole-deck prompt was refused; the rollout had not reached the account.
- Gemini in the Slides side panel wrote a 16-element SVG UI mockup to a palette-and-elements brief; it converted to native shapes plus two text boxes without edits.
- Dry run opened four decks and reported zero to three slots to change in each. Place icons and UIs worked after two fixes to mockup text (box width, type scaled from box height).
- Scripts ran on a sheet owned by the Workspace account that runs them. A personal account refused ("This app is blocked"); a sheet owned by another account showed an unverified-app warning. Link chips on the Assets tab break the script.
- Not yet run end to end: Sync all with generated lines, Add to library.

The screens in the post are mockups. Google Slides, Google Sheets, Google Forms, Google Drive and Gemini are trademarks of Google LLC.
"""

POST = {
    "slug": "messaging-workshop-brand-style-sheet-google-sheets",
    "date": "2026-11-09",
    "date_h": "Nov 9, 2026, updated Nov 10",
    "read": "15 min read",
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
        "Answers feed a <b>five-level messaging architecture</b> of 17 lines. Those lines are the briefs Gemini writes every slot from.",
        "<b>Icons and UI mockups</b> live in two library decks of native shapes. Asset decks pull from them by tag.",
        "<b>Page recipes</b> from seven live pages give a formula for each block of a solution or product page.",
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
