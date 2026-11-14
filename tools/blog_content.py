"""Blog posts for svgslid.es/blog. Body is hand-written HTML; md is the agent twin.

Figures use {fig:name|alt|caption} placeholders, expanded by build_site.py into
<figure><picture>webp+png</picture><figcaption> with intrinsic width/height.
"""

HELP = "https://support.google.com/docs/answer/1663349"
WB_BEFORE = "https://web.archive.org/web/20261005194616/https://support.google.com/docs/answer/1663349?rd=1&visit_id=639268263719815361-3052973569"
WB_AFTER = "https://web.archive.org/web/20261012192940/https://support.google.com/docs/answer/1663349?hl=enGoogle:"
WB_INDEX = "https://web.archive.org/web/2026*/https://support.google.com/docs/answer/1663349*"
LINE_2019 = "https://workspaceupdates.googleblog.com/2019/09/line-spacing-docs-slides.html"

POSTS = [
    {
        "slug": "letter-spacing-google-slides",
        "date": "2026-11-07",
        "date_h": "Nov 7, 2026",
        "updated_h": "Nov 14, 2026",
        "read": "4 min read",
        "jump": ("docs", "<b>Skip ahead:</b> the subtle Google slip-up that hints letter spacing is coming to Docs very soon"),
        "kicker": "New in Slides",
        "title": "Letter Spacing in Google Slides: How to Use the New Tracking Control",
        "h1": "Google Slides finally does letter spacing",
        "dek": "Tracking has landed in Slides. Here's what it is, how to use it well, and why Docs looks next.",
        "desc": "Google Slides now has letter spacing (tracking): a toolbar button and Format › Text › Letter spacing, with presets and custom values. How to use it well, plus clues it's coming to Docs.",
        "hero": ("hero-letter-spacing", "Close-up of the new Letter spacing button in the Google Slides toolbar, with cursor and tooltip"),
        "og": "og-letter-spacing.png",
        "tldr": [
            "Slides now has <b>letter spacing</b>, which type designers call <b>tracking</b>.",
            "Find it in the toolbar (the <b>|A|</b> button next to line spacing) or <b>Format › Text › Letter spacing</b>.",
            "Presets: <b>6, 3, 0, &minus;1.5</b>, plus <b>Custom spacing</b>.",
            "Docs&rsquo; help center already documents it. The Docs editor doesn&rsquo;t show it yet.",
        ],
        "body": f"""
<h2 id="tracking">Tracking, not leading</h2>
<p>Three spacing ideas get mixed up constantly, so let&rsquo;s pin them down.</p>
<ul>
<li><b>Tracking</b> adds or removes the same space after every letter in a selection. This is the new control.</li>
<li><b>Kerning</b> fixes the gap between one specific pair, like <i>AV</i>. The font handles it. Slides doesn&rsquo;t expose it.</li>
<li><b>Leading</b> is the space between lines. In Slides that&rsquo;s the line spacing button right next door.</li>
</ul>
{{fig:tracking-kerning-leading|Diagram comparing tracking, kerning and leading|Tracking is a run-wide setting. Kerning is per pair. Leading is vertical.}}
<p>Google calls it <i>letter spacing</i>. Same thing. If a brand guide says &ldquo;track +50,&rdquo; this is the knob.</p>

<h2 id="where">Where it lives</h2>
<p>Select text or a whole text box. The new button sits between line spacing and bullets.</p>
{{fig:toolbar-letter-spacing|The Letter spacing button in the Google Slides toolbar with its tooltip|Toolbar: the |A| button, tooltip &ldquo;Letter spacing.&rdquo;}}
<p>Prefer menus? It&rsquo;s also under <b>Format › Text › Letter spacing</b>, with the same presets.</p>
{{fig:format-text-letter-spacing|Format menu, Text submenu, Letter spacing submenu showing 6, 3, 0, -1.5 and Custom spacing|Format › Text › Letter spacing.}}

<h2 id="presets">The presets, decoded</h2>
<p>Four presets cover most jobs. Positive opens text up. Negative pulls it in.</p>
{{fig:letter-spacing-presets|Letter spacing menu with presets 6, 3, 0 and -1.5, each annotated with a use case|Our rule of thumb for each preset.}}
<p><b>Custom spacing</b> takes any value, including decimals and negatives. The dialog shows no unit. It&rsquo;s points, so the same value looks bigger on small type.</p>
<p><b>Update, Nov 14:</b> letter spacing survives PDF export exactly, kerning included. <a href="/blog/letter-spacing-google-slides-pdf-export">We tested 10 fonts at six sizes</a>.</p>
{{fig:custom-letter-spacing|Custom letter spacing dialog with a value of 4 entered|Custom spacing: type a value, hit Apply.}}

<h2 id="tips">Use it like a designer</h2>
<p><b>1. Open up all caps.</b> Capitals are designed to sit next to lowercase. Set alone, they feel cramped. A little air fixes it. This is the single best use of the feature.</p>
{{fig:caps-0-vs-3|QUARTERLY REVIEW at 0 letter spacing versus +3|All caps at 0 vs. +3. The tracked version reads calmer and more deliberate.}}
<p><b>2. Tighten big headlines, slightly.</b> Display sizes look loose at default spacing. A small negative value makes a headline feel set, not typed.</p>
{{fig:headline-0-vs-neg|Revenue is up 42% at 0 letter spacing versus -1.5|A display headline at 0 vs. &minus;1.5. Subtle up close, obvious from the back of the room.}}
<p><b>3. Leave body text at 0.</b> Fonts are spaced for reading sizes already. Tracking paragraphs only slows people down.</p>
<p><b>4. The bigger the type, the tighter. The smaller, the looser.</b> That&rsquo;s the whole philosophy in one line.</p>
<p><b>5. Watch the reflow.</b> Positive values widen every line. Recheck line breaks, and make sure text doesn&rsquo;t spill out of its box.</p>
<p><b>6. Pick one value per role.</b> Eyebrows at +3, headlines at &minus;1.5, everything else at 0. Consistency is what reads as polish.</p>
<p><b>7. Check it in Present mode.</b> Spacing that looks right at 50% zoom can look different full screen.</p>

<h2 id="how">Step by step</h2>
<ol class="steps">
<li>Select the text, or click the edge of a text box to select all of it.</li>
<li>Click <b>Letter spacing</b> (<b>|A|</b>) in the toolbar, or go to <b>Format › Text › Letter spacing</b>.</li>
<li>Pick <b>6</b>, <b>3</b>, <b>0</b> or <b>&minus;1.5</b>.</li>
<li>Or choose <b>Custom spacing</b>, enter a value, and click <b>Apply</b>.</li>
<li>To reset, select the text and choose <b>0</b>.</li>
</ol>

<h2 id="docs">The slip-up that points to Docs</h2>
<p><b>Clue 1: the Docs help center already explains it.</b> Google&rsquo;s Docs article <a href="{HELP}">Change how paragraphs &amp; fonts look</a> now has an &ldquo;Adjust letter spacing&rdquo; section. It covers text, text boxes and tables, with the same toolbar button and menu path as Slides.</p>
{{fig:docs-help-letter-spacing|Docs Editors Help article section titled Adjust letter spacing with steps|The new section in the Docs help article.}}
<p><b>Clue 2: it&rsquo;s new.</b> The Wayback Machine shows the section missing on <a href="{WB_BEFORE}">Oct 5, 2026</a> and present by <a href="{WB_AFTER}">Oct 12, 2026</a>. Earlier captures in July, August and September don&rsquo;t have it either. (<a href="{WB_INDEX}">All captures</a>.)</p>
{{fig:wayback-oct5-vs-oct12|Two Wayback Machine snapshots of the help article: Oct 5 without letter spacing, Oct 12 with it|Same article, one week apart.}}
<p><b>Clue 3: the editor isn&rsquo;t there yet.</b> As of today, <b>Format › Text</b> in Docs still stops at Size and Capitalization. Help articles often go up ahead of a staged rollout.</p>
{{fig:docs-format-text-today|Google Docs Format, Text submenu without a Letter spacing option|Google Docs today: no letter spacing in the menu (checked Nov 7, 2026).}}
<p><b>Clue 4: precedent.</b> When Google added custom line spacing in 2019, it <a href="{LINE_2019}">shipped to Docs and Slides together</a>. Shared text features tend to travel as a pair.</p>
<p><b>Our read:</b> strong signal, not a promise. We haven&rsquo;t found a Workspace Updates announcement yet. We&rsquo;ll update this post when Docs gets the button.</p>
""",
        "sources": [
            ("Change how paragraphs & fonts look (Google Docs Editors Help)", HELP),
            ("Wayback Machine capture, Oct 5, 2026 (no letter spacing)", WB_BEFORE),
            ("Wayback Machine capture, Oct 12, 2026 (letter spacing present)", WB_AFTER),
            ("Better line spacing support for branding in Google Docs and Slides (Sept 2019)", LINE_2019),
        ],
        "md": f"""# Google Slides finally does letter spacing

*Nov 7, 2026 · svgslid.es blog*

Tracking has landed in Google Slides. Here's what it is, how to use it well, and why Docs looks next.

## TL;DR
- Slides now has **letter spacing**, which type designers call **tracking**.
- Toolbar: the **|A|** button next to line spacing. Menu: **Format › Text › Letter spacing**.
- Presets: **6, 3, 0, −1.5**, plus **Custom spacing** (any value, decimals and negatives allowed; no unit shown, but it's points).
- Update, Nov 14: letter spacing survives PDF export exactly, kerning included. Test: https://svgslid.es/blog/letter-spacing-google-slides-pdf-export
- The Docs help center documents it; the Docs editor doesn't show it yet (as of Nov 7, 2026).

## Tracking vs. kerning vs. leading
- Tracking: same space added/removed after every letter in a selection (the new control).
- Kerning: space between one specific pair (e.g. AV); set by the font, not exposed in Slides.
- Leading: space between lines; the line spacing button.

## Tips
1. Open up all-caps text and small labels (+3 to +6).
2. Tighten large display headlines slightly (−1.5).
3. Leave body text at 0.
4. Bigger type → tighter; smaller type → looser.
5. Positive values widen lines: recheck line breaks and text box overflow.
6. One value per role (eyebrow, headline, body) for consistency.
7. Check in Present mode.

## Steps
1. Select text or a whole text box.
2. Click Letter spacing (|A|) in the toolbar, or Format › Text › Letter spacing.
3. Pick 6, 3, 0 or −1.5. Or choose Custom spacing, enter a value, Apply.
4. Reset by choosing 0.

## The slip-up that points to Docs
- Docs help article "Change how paragraphs & fonts look" ({HELP}) now has an "Adjust letter spacing" section (text, text boxes, tables; toolbar button and Format › Text › Letter spacing).
- Wayback Machine: absent on Oct 5, 2026 ({WB_BEFORE}); present Oct 12, 2026 ({WB_AFTER}). Not in July–September captures.
- Docs editor Format › Text menu has no Letter spacing yet (checked Nov 7, 2026).
- Precedent: custom line spacing shipped to Docs and Slides together in Sept 2019 ({LINE_2019}).
- No Workspace Updates announcement found yet. Strong signal, not a promise.
""",
    },
]

from blog_collateral import POST as _COLLATERAL
from blog_collateral2 import POST as _COLLATERAL2
POSTS.insert(0, _COLLATERAL)
POSTS.insert(0, _COLLATERAL2)
from blog_pdf_spacing import POST as _PDF_SPACING
POSTS.insert(0, _PDF_SPACING)

import blog_appscript  # noqa: F401  (appends to blog_workspace.POSTS)
from blog_workspace import POSTS as _WORKSPACE
POSTS.extend(_WORKSPACE)
_PRODUCT = {"letter-spacing-google-slides": "slides", "letter-spacing-google-slides-pdf-export": "slides", "google-slides-collateral-messaging-sheet-gemini": "slides",
            "messaging-workshop-brand-style-sheet-google-sheets": "forms"}
_REL = {"letter-spacing-google-slides": ["letter-spacing-google-slides-pdf-export", "on-brand-charts-google-slides", "native-ui-mockups-google-slides"],
        "google-slides-collateral-messaging-sheet-gemini": ["audit-gemini-whole-deck-edits-google-slides", "competitor-matrix-google-sheets-gemini-citations", "workspace-studio-shared-files-messaging-flow"],
        "messaging-workshop-brand-style-sheet-google-sheets": ["gemini-skills-messaging-recipes", "sales-enablement-quiz-google-forms", "native-ui-mockups-google-slides"]}
for _p in POSTS:
    _p.setdefault("product", _PRODUCT.get(_p["slug"]))
    _p.setdefault("related", _REL.get(_p["slug"], []))
    if _p["slug"] == "messaging-workshop-brand-style-sheet-google-sheets":
        _p.setdefault("order", 1)
POSTS.sort(key=lambda p: (p["date"], p.get("order", 0)), reverse=True)


# Search-result title and description, where the on-page ones run past what
# Google shows (~60 chars / ~155 chars). The headline and dek on the page are unchanged.
_META = {
    "native-ui-mockups-google-slides": (None, "Replace product screenshots in Google Slides with UI mockups made of native shapes and live text: built in Figma, brought in as SVG, kept in a library deck."),
    "messaging-workshop-brand-style-sheet-google-sheets": ("Messaging Workshop in Google Forms, Brand Style Sheet in Sheets", "Run a messaging workshop as a Google Form, turn the answers into a five-level messaging architecture, and keep fonts, colours and voice in Google Sheets."),
    "google-slides-collateral-messaging-sheet-gemini": (None, "Gemini in Google Slides can now edit a whole deck from one prompt. Pair it with a messaging sheet, real page sizes, slot tags, copy rules and a starter pack."),
    "letter-spacing-google-slides-pdf-export": ("Google Slides Letter Spacing in PDF Export: Tested on 10 Fonts", "We tested Google Slides letter spacing in PDF export across 10 Google Fonts and six sizes. Tracking and kerning carry over exactly. Three things do change."),
    "letter-spacing-google-slides": (None, "Google Slides now has letter spacing (tracking): a toolbar button and Format › Text › Letter spacing, with presets and custom values. How to use it well."),
    "audit-gemini-whole-deck-edits-google-slides": (None, "Gemini can now edit a whole Google Slides deck from one prompt. An Apps Script snapshots every object before and after, and diffs the two in Google Sheets."),
    "competitor-matrix-google-sheets-gemini-citations": ("Competitor Matrix in Google Sheets Where Every Cell Cites a Source", "Build a competitor matrix in Google Sheets with Fill with Gemini's cell-level web citations: one row per claim, a checked-on date and a staleness flag."),
    "on-brand-charts-google-slides": (None, "Make Google Slides charts match your brand: when to link a Sheets chart, and when to draw it as native shapes, by script or with SVG to Slides."),
    "workspace-studio-shared-files-messaging-flow": ("Workspace Studio Won't Run on Shared Files: Design Around It", "Workspace Studio flows fail on shared drives, shared folders and IMPORTRANGE. A two-sheet pattern mirrors a shared messaging sheet to a private one."),
    "gemini-skills-messaging-recipes": (None, "Package product marketing copy rules as reusable Gemini skills in Google Workspace, invoked with @ in Docs and Slides. What changes for Gems and Studio."),
    "customer-proof-points-expiry-google-sheets": (None, "A Google Sheets proof library for customer logos, quotes and case studies, with permission scope, expiry dates and a flow that warns before one expires."),
    "google-meet-notes-screenshots-slide-objections": (None, "Google Meet's Take notes for me now embeds slide screenshots. Log sales call objections per slide in Google Sheets and find the slides that need work."),
    "sales-enablement-quiz-google-forms": (None, "Turn approved messaging into a Google Forms quiz for sales enablement, with Gemini quiz generation or an Apps Script that uses retired lines as wrong answers."),
    "localize-one-pager-google-slides": (None, "A Sheets-first way to localize Google Slides one-pagers and decks: a budget per slot per language, AI translations held to it, and a fit check."),
}
META = {p["slug"]: (_META[p["slug"]][0] or p["title"], _META[p["slug"]][1]) for p in POSTS if p["slug"] in _META}


# Two lanes on the blog index. "design" is the search-acquisition lane (Slides
# graphics, type and layout, where SVG to Slides is part of the workflow);
# everything else is the wider Workspace-for-product-marketing lane.
LANES = [
    ("design", "Google Slides design and vector graphics",
     "Graphics, type and layout inside Google Slides, and getting vector artwork in.",
     ["letter-spacing-google-slides-pdf-export", "native-ui-mockups-google-slides", "on-brand-charts-google-slides", "letter-spacing-google-slides"]),
    ("pmm", "Product marketing in Google Workspace",
     "Sheets, Slides, Forms and Gemini setups that keep messaging and collateral current.", None),
]

def lane_of(slug):
    for key, _t, _d, slugs in LANES:
        if slugs and slug in slugs:
            return key
    return LANES[-1][0]

def uses_product(p):
    """Show the SVG to Slides call to action only where the post's workflow uses it."""
    text = p.get("md", "") + p.get("body", "")
    return "SVG to Slides" in text
