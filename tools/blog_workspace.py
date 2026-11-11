"""Workspace-for-PMM posts on svgslid.es/blog (ten posts, Jul to Nov 2026).

Each post is dated shortly after the Google feature it builds on. Body links only
point back to posts dated earlier; links to later posts live in "related" (rendered
as a Related posts block) or in a clearly labelled update note.

Figures are mockups rendered by tools/workspace_images.py, coloured by the post's
product (see PRODUCTS in build_site.py). Claims stay within the linked sources.
Scripts are written against Google's Apps Script reference; each post says what
we have and have not run.
"""
import re
import html as _html

# ---------------------------------------------------------------- links
SITE_HOME = "/"
G_INSERT = "/guides/insert-svg-into-google-slides"
G_SUPPORT = "/guides/does-google-slides-support-svg"
G_RECOLOR = "/guides/recolor-svg-in-google-slides"
G_LOGOS = "/guides/svg-logos-icons-google-slides"
G_VS = "/guides/svg-vs-png-google-slides"
G_CONVERT = "/guides/svg-to-google-slides-converter"
P1 = "/blog/google-slides-collateral-messaging-sheet-gemini"
P2 = "/blog/messaging-workshop-brand-style-sheet-google-sheets"
LS = "/blog/letter-spacing-google-slides"

S_UI = "/blog/native-ui-mockups-google-slides"
S_AUDIT = "/blog/audit-gemini-whole-deck-edits-google-slides"
S_MATRIX = "/blog/competitor-matrix-google-sheets-gemini-citations"
S_CHARTS = "/blog/on-brand-charts-google-slides"
S_STUDIO = "/blog/workspace-studio-shared-files-messaging-flow"
S_SKILLS = "/blog/gemini-skills-messaging-recipes"
S_PROOF = "/blog/customer-proof-points-expiry-google-sheets"
S_MEET = "/blog/google-meet-notes-screenshots-slide-objections"
S_QUIZ = "/blog/sales-enablement-quiz-google-forms"
S_LOC = "/blog/localize-one-pager-google-slides"

LINUS = "https://www.youtube.com/channel/UCSb-xYOELhIqVr2n9s-b_4w"
WILL = "https://www.youtube.com/@WillPaterson"
FUTUR = "https://thefutur.com/"

U_WHOLE = "https://workspaceupdates.googleblog.com/2026/10/edit-entire-presentations-with-gemini-in-Google-Slides.html"
U_CITE = "https://workspaceupdates.googleblog.com/2026/10/fill-with-gemini-now-provides-cell-level-citations-for-web-sources-and-supports-larger-requests.html"
U_AI_FN = "https://support.google.com/docs/answer/15877199"
U_SKILLS = "https://workspaceupdates.googleblog.com/2026/09/skills-gemini-app-workspace.html"
U_SKILLS_T = "https://knowledge.workspace.google.com/admin/generative-ai/gemini-app/about-the-transition-to-skills"
U_STUDIO = "https://support.google.com/workspace-studio/answer/16444479"
U_STUDIO_STEPS = "https://support.google.com/workspace-studio/answer/16765661"
U_STUDIO_OCT = "https://workspaceupdates.googleblog.com/2026/10/new-logic-and-search-steps-in-workspace-Studio-help-expand-automation-capabilities.html"
U_STUDIO_SEP = "https://workspaceupdates.googleblog.com/2026/09/automate-drive-gmail-and-google-chat-actions-with-new-steps-in-Workspace-Studio.html"
U_MEET = "https://workspaceupdates.googleblog.com/2026/08/visual-screenshots-now-included-in-Google-Meet-meeting-notes.html"
U_MEET_HELP = "https://support.google.com/meet/answer/14754724"
U_QUIZ = "https://workspaceupdates.googleblog.com/2026/07/use-gemini-in-google-forms-to-quickly-create-a-new-quiz.html"
U_FORMAPP = "https://developers.google.com/apps-script/reference/forms"
U_FILL_LANG = "https://workspaceupdates.googleblog.com/2026/07/fill-with-gemini-in-sheets-now-available-in-11-additional-languages.html"
U_BOX = "https://androidauthority.com/google-sheets-adds-box-plot-support-3726846"
U_COMBO = "https://workspaceupdates.googleblog.com/2026/07/import-and-create-combo-charts-in-Google-Sheets.html"
U_SCATTER = "https://workspaceupdates.googleblog.com/2026/07/create-and-import-scatter-charts-with-multiple-x-series-in-Google-Sheets.html"
U_LINKED = "https://support.google.com/docs/answer/7009814"
U_SLIDESAPP = "https://developers.google.com/apps-script/reference/slides"
U_FIGMA_SVG = "https://help.figma.com/hc/en-us/articles/13402894554519"

TM = '<p style="font-size:14px;color:var(--mute)">The screens in this post are mockups, not captures of Google&rsquo;s products. Google Slides, Google Sheets, Google Docs, Google Forms, Google Meet, Google Chat, Google Drive, Gemini and Google Workspace are trademarks of Google LLC.</p>'


def _sub(body, extra=None):
    keys = {k: v for k, v in globals().items() if k.isupper() and isinstance(v, str)}
    for k in list(keys):
        for suf in ("_GS", "_TXT"):
            if k.endswith(suf):
                keys[k[: -len(suf)]] = _html.escape(keys[k], quote=False)
    keys.update(extra or {})
    return re.sub(r"%([A-Z0-9_]+)%", lambda m: keys.get(m.group(1), m.group(0)), body)


def _md(p):
    """Plain markdown twin built from the HTML body."""
    b = p["body"]
    b = re.sub(r"\{fig:[^|}]+\|[^|}]+\|([^}]*)\}", lambda m: f"\n[Figure: {m.group(1)}]\n", b)
    b = re.sub(r"<pre[^>]*>(.*?)</pre>", lambda m: "\n" + "\n".join("    " + l for l in m.group(1).strip("\n").split("\n")) + "\n", b, flags=re.S)
    b = re.sub(r'<a href="([^"]+)">(.*?)</a>', lambda m: f"{m.group(2)} ({m.group(1) if m.group(1).startswith('http') else 'https://svgslid.es' + m.group(1)})", b)
    b = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n## \1\n", b)
    b = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n### \1\n", b)
    b = re.sub(r"<li>", "- ", b)
    b = re.sub(r"<tr>(.*?)</tr>", lambda m: "| " + " | ".join(re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", m.group(1))) + " |\n", b, flags=re.S)
    b = re.sub(r"</?(b|strong)>", "**", b)
    b = re.sub(r"</?(i|em)>", "*", b)
    b = re.sub(r"</?code>", "`", b)
    b = re.sub(r"<[^>]+>", "", b)
    b = _html.unescape(b)
    b = re.sub(r"\n{3,}", "\n\n", b).strip()
    tl = "\n".join("- " + _html.unescape(re.sub(r"<[^>]+>", "", x)) for x in p["tldr"])
    return f"# {_html.unescape(p['h1'])}\n\n*{p['date_h']} · svgslid.es blog*\n\n{_html.unescape(p['dek'])}\n\n## TL;DR\n{tl}\n\n{b}\n"


def _read(body):
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    return f"{max(3, round(words / 230))} min read"


POSTS = []


def post(**kw):
    kw["body"] = _sub(kw["body"])
    kw["tldr"] = [_sub(x) for x in kw["tldr"]]
    kw.setdefault("read", _read(kw["body"]))
    kw["md"] = _md(kw)
    POSTS.append(kw)


# ====================================================================== 1. Localization (Sheets, Jul 31)
post(
    slug="localize-one-pager-google-slides",
    product="sheets",
    date="2026-07-31", date_h="Jul 31, 2026",
    kicker="Localization",
    title="Localize a One-Pager in Google Slides Without Breaking the Layout",
    h1="Localize a one-pager without breaking the layout",
    dek="Translations run long. Give every slot a budget per language, draft in Sheets, and catch the overflow before it reaches the page.",
    desc="A Sheets-first way to localize Google Slides one-pagers and decks: a budget per slot per language, AI-drafted translations held to that budget, and a fit check before anything lands on the page.",
    hero=("hero-loc", "Three versions of the same one-pager in English, German and Japanese, with the German headline flagged as over budget"),
    og="og-loc.png",
    tldr=[
        "Translated copy is a layout problem first. German and French lines often run longer than English; Japanese is shorter in characters but wider per character.",
        "Keep one row per slot in Sheets and one column per language, each with its own <b>character budget</b>.",
        "Draft with the Sheets AI function. Fill with Gemini now works in 11 more languages. A native speaker approves.",
        "Flag anything over budget in the sheet. Fix length there, never by shrinking type on the page.",
    ],
    body="""
<h2 id="problem">The page breaks before the translation does</h2>
<p>A one-pager is built around its English copy. The headline box is sized for eight words. The three benefit columns are sized for two short lines each. Then the German version arrives and every box overflows.</p>
<p>You can fix it slide by slide, file by file, every launch. Or you can treat length as data and catch it before it reaches a page. The second way takes one sheet.</p>

<h2 id="sheet">One row per slot, one column per language</h2>
<p>Every text box on the page is a slot with a key: <code>headline</code>, <code>subhead</code>, <code>benefit_1_title</code>. The sheet has one row per key. Each language gets a copy column and a budget column.</p>
{fig:loc-sheet|Mockup of a localization sheet with Key, English, Budget, German, German budget, Fits columns and one German headline flagged over budget|One row per slot. The German headline is 11 characters over. Mockup.}
<ul>
<li><b>Key:</b> the slot name. It never changes between languages.</li>
<li><b>Source line:</b> the approved English line.</li>
<li><b>Budget per language:</b> the most characters that slot can hold in that language, at that size, in that font. Set it by filling the box until it looks full, then counting.</li>
<li><b>Fits:</b> <code>=IF(LEN(D2)&lt;=E2,"OK","Over by "&amp;(LEN(D2)-E2))</code></li>
</ul>
<p>Budgets differ by language for two reasons. Some languages need more letters to say the same thing. And a character count is a stand-in for width: a Japanese character takes far more room than a Latin <i>i</i>. Measure each language in its own font.</p>

<h2 id="draft">Draft the translation in the sheet</h2>
<p>Google announced on July 7 that <a href="%U_FILL_LANG%">Fill with Gemini in Sheets works in 11 more languages</a>. Fill with Gemini runs on the <a href="%U_AI_FN%">AI function</a>, so you can write the budget into the prompt:</p>
<pre>=AI("Translate this product marketing line into German. Keep it under "&amp;E2&amp;" characters. Plain, specific, no exclamation marks.", B2)</pre>
<p>Three rules keep this safe:</p>
<ul>
<li><b>A draft is a draft.</b> A native speaker who knows the product approves every line. Machine drafts miss product terms and register.</li>
<li><b>Keep a glossary tab.</b> Product names, feature names and terms you never translate. Paste the relevant terms into the prompt.</li>
<li><b>Keep draft and approved separate.</b> A formula can recalculate. An approved line must not. Paste approved lines as values.</li>
</ul>

<h2 id="fit">Catch overflow in the sheet, not on the page</h2>
{fig:loc-expansion|The same headline box filled with English, French, German and Japanese versions of one line, with bars comparing each line to its budget|One headline, four languages, one box. Budgets are set per language.}
<p>When a line is over budget, shorten the line. Do not shrink the font for one language. A German headline set smaller than the English one breaks the type system you built for every other asset, and readers notice.</p>
<p>Some fixes that work:</p>
<ul>
<li><b>Write a shorter source line.</b> If three languages run over, the English line is too long for the layout.</li>
<li><b>Allow a two-line headline</b> in the layout, and budget for two lines in every language.</li>
<li><b>Split long compounds</b> with your translator, or choose a shorter term from the glossary.</li>
</ul>

<h2 id="fonts">Fonts per language</h2>
<p>Your brand font may not cover every script. Overpass, our headline font, has no Japanese glyphs. Pick a fallback per language and record it in the sheet, so everyone uses the same one. Google Fonts has Noto families for most scripts. Re-measure budgets in the fallback font.</p>
<p>Check letter spacing too. A tracked-out all-caps eyebrow in English can look wrong in a script with no capitals. Set tracking per language.</p>

<h2 id="pages">One file per language</h2>
<ul>
<li>Make a copy of the finished English file for each language. Keep page size, layout and slot names identical.</li>
<li>Name files the same way: <code>One-pager - Relay - de-DE</code>.</li>
<li>Paste approved lines slot by slot. If you tag text boxes with their key in the alt text title, a script can do this for every language at once.</li>
<li>Look at every page after the copy lands. A count is an estimate; line breaks still surprise.</li>
</ul>
<p>Logos and icons should not change between languages. Keep them as vectors so one file serves every version: see <a href="%G_LOGOS%">how to add a logo to Google Slides as an editable SVG</a>.</p>

<h2 id="status">What we have tested</h2>
<ul>
<li><b>Checked in Sheets:</b> the LEN-based fit formula.</li>
<li><b>Not checked by us:</b> translation quality from the AI function in each of the 11 new languages. Google&rsquo;s post lists them; treat every draft as a draft.</li>
</ul>
<p><i>Update, Nov 2026:</i> the slot-and-sync approach mentioned above is now written up in full in <a href="%P1%">Update Google Slides collateral from one messaging sheet with Gemini</a>.</p>
""" + TM,
    sources=[("Fill with Gemini in Sheets now available in 11 additional languages (Google Workspace Updates, Jul 7, 2026)", U_FILL_LANG),
             ("Use the AI function in Google Sheets (Google Docs Editors Help)", U_AI_FN)],
    related=["google-slides-collateral-messaging-sheet-gemini", "letter-spacing-google-slides", "on-brand-charts-google-slides"],
)

# ====================================================================== 2. Forms quiz (Forms, Aug 4)
QUIZ_GS = """function buildMessagingQuiz() {
  const sheet = SpreadsheetApp.getActive().getSheetByName('Messages');
  const rows = sheet.getDataRange().getValues().slice(1);   // Key, Question, Approved line, Retired 1, Retired 2, Retired 3
  const form = FormApp.create('Messaging check: ' + new Date().toDateString());
  form.setIsQuiz(true);
  rows.filter(r => r[1] && r[2]).forEach(r => {
    const item = form.addMultipleChoiceItem();
    const options = [item.createChoice(r[2], true)]
      .concat(r.slice(3, 6).filter(String).map(t => item.createChoice(t, false)));
    item.setTitle(r[1]).setChoices(shuffle(options)).setPoints(1).setRequired(true);
  });
  form.setDestination(FormApp.DestinationType.SPREADSHEET, SpreadsheetApp.getActive().getId());
  Logger.log(form.getPublishedUrl());
}

function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}"""

post(
    slug="sales-enablement-quiz-google-forms",
    product="forms",
    date="2026-08-04", date_h="Aug 4, 2026",
    kicker="Sales enablement",
    title="Certify Reps on New Messaging with a Google Forms Quiz",
    h1="Certify reps on the new message with a Forms quiz",
    dek="A launch isn't landed until the people selling it can say it. Build a short quiz from the messaging, score it in Sheets, and follow up with whoever missed.",
    desc="Turn approved product messaging into a Google Forms quiz for sales enablement, with Gemini's new quiz generation or a short Apps Script that uses retired lines as wrong answers.",
    hero=("hero-quiz", "Google Forms quiz question asking which line leads the SSO story, with the approved line selected"),
    og="og-quiz.png",
    tldr=[
        "Since July 30, <b>Help me create</b> in Google Forms can generate a quiz, with correct answers, from a prompt and files.",
        "The best wrong answers are your own retired lines. They are plausible because you used to say them.",
        "Score in Sheets, set a pass mark, and follow up one to one.",
        "Keep it to ten questions. It checks recall of the message, not product knowledge.",
    ],
    body="""
<h2 id="why">A message nobody can repeat isn't launched</h2>
<p>Product marketing ships the new positioning, the deck, the one-pager. Two weeks later a rep describes the product the old way on a call. The assets changed. The words in people&rsquo;s mouths didn&rsquo;t.</p>
<p>A ten-question quiz after the enablement session tells you who has the new message and who needs a second pass. Google Forms has done quizzes for years. What changed is how fast you can build one.</p>

<h2 id="gemini">Route 1: let Gemini draft the quiz</h2>
<p>On July 30, Google announced that <a href="%U_QUIZ%">Help me create in Google Forms now generates quizzes</a>. You describe the quiz in a prompt and point it at files, including PDFs. Gemini drafts the questions, sets quiz settings and marks the correct answers.</p>
<pre>Create a 10-question multiple choice quiz for account executives on our new SSO messaging.
Use only the approved lines in the attached messaging doc as correct answers.
Each question gets three wrong answers that sound plausible. Do not invent product facts.</pre>
<p>Read every question before you send it. Gemini decides what to ask, and it may test a detail that doesn&rsquo;t matter. Delete those. Check every correct answer against the messaging doc word for word.</p>
<p>Availability per Google&rsquo;s post: Business Standard and Plus, Enterprise Standard and Plus, Education Plus.</p>

<h2 id="script">Route 2: build it from the messaging sheet</h2>
<p>If your messages already live in a sheet, a script gives you exact control. The trick is the wrong answers. Generic distractors are easy to spot. Your <b>retired lines</b> are not: they are what the team said last quarter, and they are what a rep will say if the new message didn&rsquo;t stick.</p>
{fig:quiz-from-sheet|Diagram: sheet rows with Question, Approved line and three Retired lines become a multiple choice question with one correct answer|Approved line becomes the correct answer. Retired lines become the wrong ones.}
<p>Add a Question column and up to three Retired columns to the Messages tab. Then, in the sheet, open <b>Extensions &rsaquo; Apps Script</b> and paste:</p>
<pre>%QUIZ%</pre>
<p>Run <code>buildMessagingQuiz</code>. It creates a quiz form, one question per row, with the approved line marked correct and the options shuffled, and sends responses to a new tab in the same spreadsheet. The <a href="%U_FORMAPP%">FormApp reference</a> covers every call it uses.</p>

<h2 id="score">Score it and follow up</h2>
{fig:quiz-results|Mockup of a Form responses tab with name, score and pass columns; two reps below the pass mark are highlighted|Responses land in the sheet with a score. Mockup.}
<ul>
<li><b>Pass mark:</b> 8 of 10 is a reasonable start. Add a column: <code>=IF(C2&gt;=8,"Pass","Follow up")</code>.</li>
<li><b>Look at the misses by question,</b> not only by person. If half the team picks the same retired line, the message is the problem, not the reps.</li>
<li><b>Follow up one to one.</b> A short call beats a public leaderboard.</li>
<li><b>Re-run after a change.</b> When a line changes, it moves to a Retired column and becomes a wrong answer in the next quiz.</li>
</ul>

<h2 id="status">What we have tested</h2>
<ul>
<li><b>Not yet run by us:</b> the script above. It is written against the FormApp reference. Run it on a copy of your sheet first.</li>
<li><b>Not yet tried by us:</b> quiz generation with Help me create. Our account did not have it when we wrote this.</li>
</ul>
""" + TM,
    sources=[("Use Gemini in Google Forms to quickly create a new quiz (Google Workspace Updates, Jul 30, 2026)", U_QUIZ),
             ("Forms Service reference (Google Apps Script)", U_FORMAPP)],
    related=["messaging-workshop-brand-style-sheet-google-sheets", "gemini-skills-messaging-recipes", "workspace-studio-shared-files-messaging-flow"],
)

# ====================================================================== 3. Meet objections (Meet, Aug 12)
post(
    slug="google-meet-notes-screenshots-slide-objections",
    product="meet",
    date="2026-08-12", date_h="Aug 12, 2026",
    kicker="Deck feedback",
    title="Find Which Slide Draws Objections with Google Meet Notes Screenshots",
    h1="Find which slide draws the objections",
    dek="Meet notes now capture the slide on screen. Log each objection against that slide and the weak spots in your deck show up in a week.",
    desc="Google Meet's Take notes for me now embeds screenshots of presented slides. Use them to log sales call objections per slide in Google Sheets and find which slides of a sales deck need work.",
    hero=("hero-meet", "Meet notes document with an embedded slide screenshot and two objections logged next to it"),
    og="og-meet.png",
    tldr=[
        "Since August 3, Meet&rsquo;s <b>Take notes for me</b> can embed screenshots of presented content, such as slides, in the notes doc.",
        "That ties what was said to the slide on screen. Log each objection with the slide it came up on.",
        "A simple Objections tab plus COUNTIFS shows which slides draw pushback.",
        "Presenters are notified and can turn capture off. Tell prospects notes are being taken.",
    ],
    body="""
<h2 id="gap">Call notes lose the slide</h2>
<p>Call notes say &ldquo;pricing concern&rdquo; or &ldquo;asked about SSO.&rdquo; They rarely say which slide was up. So when product marketing asks which part of the deck isn&rsquo;t working, the answer is a guess.</p>
<p>On August 3, Google <a href="%U_MEET%">started including screenshots of presented content in Meet&rsquo;s meeting notes</a>. When you present during a call with <b>Take notes for me</b> on, Gemini can capture slides, charts and diagrams into the notes document, next to the summary. Now the notes know which slide was on screen.</p>
{fig:meet-notes-doc|Mockup of a Google Docs meeting notes document with a captured slide image, summary bullets and an objection highlighted|Meeting notes with a captured slide. Mockup.}

<h2 id="setup">Before the call</h2>
<ul>
<li><b>Present from Slides inside Meet.</b> Screenshots cover presented content.</li>
<li><b>Number your slides</b> and give each a short title in the speaker notes or on the slide. A screenshot is easier to log when the slide says &ldquo;7 &middot; Pricing.&rdquo;</li>
<li><b>Tell the prospect notes are being taken.</b> Meet notifies the presenter that Gemini may capture screenshots, and the feature can be turned off from the notes panel. Admins can also require consent before notes start.</li>
</ul>

<h2 id="log">After the call: one row per objection</h2>
<p>Open the notes doc. For each objection, add a row to an Objections tab in your deck-feedback sheet.</p>
{fig:objection-tab|Mockup of an Objections tab with Date, Deal, Slide, Objection, Category and Quote columns|One row per objection, keyed to the slide. Mockup.}
<ul>
<li><b>Slide:</b> the number and title from the screenshot.</li>
<li><b>Objection:</b> one plain sentence. &ldquo;Thinks SSO costs extra.&rdquo;</li>
<li><b>Category:</b> a short fixed list: price, security, fit, proof, competitor, timing.</li>
<li><b>Quote:</b> the prospect&rsquo;s words, if the notes have them.</li>
</ul>
<p>Gemini in the Docs side panel can draft this for you from the notes. Ask for a table with those columns, then check each row against the notes before you paste it.</p>

<h2 id="heat">Count by slide</h2>
<p>On a Summary tab, list the slides and count:</p>
<pre>=COUNTIFS(Objections!C:C, A2)</pre>
<p>Add a colour scale to the count column and you have a heat map of the deck. After ten calls the pattern is usually obvious: one or two slides draw most of the pushback.</p>
{fig:objection-heatmap|Grid of twelve slide thumbnails with objection counts; slide 7 Pricing has the most and is shaded darkest|Objections per slide after ten calls. Illustrative numbers.}
<p>Read the hot slides with the quotes next to them. Often the fix is a missing proof point or an unclear line, not a missing feature. Those are product marketing fixes.</p>

<h2 id="later">Automating the log</h2>
<p>Workspace Studio has a starter that runs when a meeting transcript is ready, and steps that can ask Gemini and add rows to a sheet. That could write the Objections tab for you. Google&rsquo;s <a href="%U_STUDIO_STEPS%">starter guide</a> notes that this starter fires on the transcript, not on Gemini&rsquo;s notes, so whether a flow sees the slide screenshots is something to test. We haven&rsquo;t yet.</p>

<h2 id="status">What we have tested</h2>
<ul>
<li><b>Checked in Sheets:</b> the COUNTIFS summary formula.</li>
<li><b>Not yet checked by us:</b> screenshot capture itself. It was rolling out when we wrote this; availability depends on your Workspace edition and admin settings.</li>
</ul>
""" + TM,
    sources=[("Visual screenshots now included in Google Meet meeting notes (Google Workspace Updates, Aug 3, 2026)", U_MEET),
             ("Take notes for me in Google Meet (Google Meet Help)", U_MEET_HELP),
             ("Guide to Starters & Steps in Workspace Studio", U_STUDIO_STEPS)],
    related=["workspace-studio-shared-files-messaging-flow", "customer-proof-points-expiry-google-sheets", "sales-enablement-quiz-google-forms"],
)

# ====================================================================== 4. Proof expiry (Studio, Sep 9)
post(
    slug="customer-proof-points-expiry-google-sheets",
    product="studio",
    date="2026-09-09", date_h="Sep 9, 2026",
    kicker="Proof library",
    title="Customer Proof Points Expire. Track Them in Google Sheets.",
    h1="Customer proof points expire. Track them.",
    dek="Logos, quotes and case studies come with permission, and permission has an end date. Keep a proof library in Sheets and get warned before a quote goes stale.",
    desc="A Google Sheets proof library for customer logos, quotes and case studies, with permission scope and expiry dates, plus a Workspace Studio flow that warns you before a proof point expires.",
    hero=("hero-proof", "Proof library sheet with permission scope and days-left columns; one customer quote flagged as expiring in 12 days"),
    og="og-proof.png",
    tldr=[
        "Every customer logo and quote you use was approved by someone, for some use, until some date. Write all three down.",
        "One row per proof point: claim, customer, scope, source of approval, expiry, days left, used in.",
        "A Workspace Studio flow can check the sheet weekly and post what is about to expire to Chat.",
        "September&rsquo;s new Studio steps (Move Drive file, Copy Drive file) can also move retired assets out of the way.",
    ],
    body="""
<h2 id="risk">The logo strip nobody re-checked</h2>
<p>A customer agreed to a logo on the website two years ago. Their champion left. The logo is still on the homepage, in four decks and on a printed one-pager. Nobody knows whether the permission covered print.</p>
<p>Proof points are borrowed. Treat them like anything else with a licence: record the terms, and track the end date.</p>

<h2 id="sheet">The proof library</h2>
{fig:proof-columns|Mockup of a Proof tab with Claim, Customer, Scope, Approved by, Source, Expires, Days left and Used in columns|One row per proof point. Mockup.}
<ul>
<li><b>Claim:</b> the exact words you use. &ldquo;Cut file transfer tickets by 60%.&rdquo;</li>
<li><b>Customer</b> and <b>contact</b> who approved it.</li>
<li><b>Scope:</b> logo, name only, quote, case study, website, print, events. A dropdown keeps it consistent.</li>
<li><b>Source:</b> a link to the approval: an email, a signed form, a comment in a doc.</li>
<li><b>Expires:</b> the date the permission ends, or a review date if it has none. One year is a sensible default.</li>
<li><b>Days left:</b> <code>=IF(G2="","No date",G2-TODAY())</code>, with red under 30 and amber under 90.</li>
<li><b>Used in:</b> every asset that carries it.</li>
</ul>
<p>The <b>Used in</b> column is what makes expiry cheap to handle. When a quote ends, you already know which files to open.</p>

<h2 id="flow">Get warned before it expires</h2>
<p>Workspace Studio builds flows from starters and steps, without code. A weekly flow with two steps is enough here:</p>
{fig:proof-flow|Workspace Studio flow: on a schedule every Monday, read rows from the Proof sheet, ask Gemini to list rows with fewer than 30 days left, notify the proof owner in Chat|A weekly check, built from a starter and three steps. Mockup.}
<ol class="steps">
<li><b>Starter:</b> on a schedule, every Monday morning.</li>
<li><b>Step:</b> ask Gemini, with the Proof sheet as its source, to list rows with fewer than 30 days left, with the claim, customer and Used in.</li>
<li><b>Step:</b> notify the proof owner in Chat.</li>
</ol>
<p>On September 2, Google added <a href="%U_STUDIO_SEP%">four new Studio steps</a>: Move Drive file, Copy Drive file, Send a Chat reply and Reply to email. Move Drive file lets the same flow move an expired logo file from your shared assets folder to a Retired folder, so nobody drops it into a new deck.</p>
<p>One constraint to plan around: <a href="%U_STUDIO%">Google&rsquo;s getting-started guide</a> says flows fail on files in shared drives or shared folders, and on spreadsheets that use IMPORTRANGE. Keep the sheet the flow reads private to the flow owner.</p>

<h2 id="assets">On the page</h2>
{fig:proof-on-asset|One-pager logo strip with five customer logos; one logo outlined in red with a note that permission expired|An expired logo, caught before the next print run.}
<ul>
<li><b>Logos as vectors.</b> A customer logo pasted as a PNG goes soft in print and can&rsquo;t be recoloured for a one-colour strip. <a href="%G_LOGOS%">Add the logo to Google Slides as an SVG</a> and <a href="%G_RECOLOR%">recolour it</a> to match the strip.</li>
<li><b>Tag each logo</b> in its alt text title with the proof row key, such as <code>proof:acme-logo</code>. Then a search, by hand or by script, finds every use.</li>
<li><b>Quotes keep their attribution</b> exactly as approved: name, title, company.</li>
</ul>

<h2 id="status">What we have tested</h2>
<ul>
<li><b>Checked in Sheets:</b> the Days left formula.</li>
<li><b>Not yet built by us:</b> the Studio flow above. Starter and step names follow Google&rsquo;s help pages; your Studio may label them slightly differently.</li>
</ul>
""" + TM,
    sources=[("Automate Drive, Gmail, and Google Chat actions with new steps in Workspace Studio (Google Workspace Updates, Sep 2, 2026)", U_STUDIO_SEP),
             ("Get started with Google Workspace Studio (Workspace Studio Help)", U_STUDIO),
             ("Guide to Starters & Steps in Workspace Studio", U_STUDIO_STEPS)],
    related=["workspace-studio-shared-files-messaging-flow", "competitor-matrix-google-sheets-gemini-citations", "google-slides-collateral-messaging-sheet-gemini"],
)

# ====================================================================== 5. Skills (Gemini, Oct 8)
SKILL_TXT = """Name: Headline recipe
When to use: writing or rewriting a headline for a one-pager, solution brief, deck title slide or landing page.

Instructions:
1. Start from the approved fact the user gives you. Do not add claims.
2. Lead with what the customer can do, in their words. Active voice.
3. 6 to 9 words. Never over the character budget if one is given.
4. No superlatives, no exclamation marks, no em dashes.
5. Banned: "seamless", "revolutionary", "unlock", "empower", "next-generation".
6. Return three options, each with its character count.

Reference: @Brand style sheet (Voice and Type tabs)"""

post(
    slug="gemini-skills-messaging-recipes",
    product="gemini",
    date="2026-10-08", date_h="Oct 8, 2026",
    kicker="Brand voice",
    title="Turn Your Messaging Recipes into Gemini Skills for Docs and Slides",
    h1="Turn your messaging recipes into Gemini skills",
    dek="Skills are replacing Gems as the way to give Gemini standing instructions. Write your copy rules once and call them with @ in Docs, Slides and Gmail.",
    desc="Package product marketing copy rules (headline recipes, proof lines, battlecard rewrites) as reusable Gemini skills in Google Workspace, invoked with @ in Docs and Slides. What changes for Gems and Workspace Studio.",
    hero=("hero-skills", "Google Docs with the Gemini side panel open and the Headline recipe skill invoked with @, returning three headline options with character counts"),
    og="og-skills.png",
    tldr=[
        "Google is rolling out <b>skills</b>: reusable instructions for Gemini that work across the Gemini app and Workspace apps. Rollout in Workspace began October 5.",
        "A copy recipe is an ideal skill: fixed structure, length limits, banned words, a reference file.",
        "Call a skill with @ in the Gemini side panel. Gemini can also pick one when it fits the prompt.",
        "Gems are being phased out. Studio flows with an Ask a Gem step will stop working; rebuild them with skills.",
    ],
    body="""
<h2 id="what">Skills, in one paragraph</h2>
<p>On September 30, Google <a href="%U_SKILLS%">introduced skills in the Gemini app and Workspace</a>, with Workspace rollout from October 5. A skill is a named set of instructions, optionally with reference files, that Gemini applies when you call it. Google&rsquo;s <a href="%U_SKILLS_T%">transition guide</a> says skills work in the Gemini app and in Workspace apps, while Gems can&rsquo;t be used in Workspace apps, and that skills will replace Gems.</p>
<p>For product marketing, that is the missing piece. Your copy rules stop living in a doc people forget to open and start living where the writing happens.</p>

<h2 id="recipe">A recipe is already a skill</h2>
<p>A messaging recipe says how a kind of line is built: what it starts with, how long it is, what it never says. That is exactly the shape of a skill.</p>
{fig:skills-recipe-anatomy|Card showing the anatomy of a skill: name, when to use, numbered instructions, banned words and a reference file|Anatomy of a copy skill.}
<p>Here is one for headlines:</p>
<pre>%SKILL%</pre>
<p>Keep each skill to one job. A headline skill, a proof line skill and a battlecard rewrite skill beat one &ldquo;brand voice&rdquo; skill that tries to do all three.</p>
{fig:skills-three|Three skill cards: Headline recipe, Proof line, Battlecard rewrite, each with its job and the apps it is used in|Three skills, one job each.}

<h2 id="use">Using a skill</h2>
<ol class="steps">
<li>Open the Gemini side panel in Docs, Slides, Gmail, Chat or Drive.</li>
<li>Type <b>@</b> and the skill&rsquo;s name, then the fact or draft you want worked on.</li>
<li>Gemini applies the skill&rsquo;s instructions and any reference files.</li>
<li>Check the output against the fact. A skill sets the rules; it doesn&rsquo;t check the claim.</li>
</ol>
<p>Gemini can also recognise when a skill applies and use it without the @. That is convenient for writers and a reason to make each skill&rsquo;s &ldquo;when to use&rdquo; line precise.</p>
<p>Admins switch skills on in the Admin console under Workspace Studio. If you don&rsquo;t see them, ask your admin.</p>

<h2 id="gems">What happens to Gems</h2>
{fig:skills-migration|Timeline: Sept 30 skills announced, Oct 5 Workspace rollout begins, Oct 13 Gemini app rollout, Gems phased out over the following months, Ask a Gem steps stop working|The transition, from Google&rsquo;s timeline.}
<ul>
<li><b>Gems in the Gemini app</b> will be migrated to draft skills automatically, per Google&rsquo;s transition guide.</li>
<li><b>Workspace Studio flows</b> with an <b>Ask a Gem</b> step will stop working. Rebuild those steps with skills or other actions.</li>
<li><b>Skills don&rsquo;t sync</b> between the Gemini app and Workspace apps. To use one in both, create it in both.</li>
</ul>

<h2 id="strategy">The recipe comes after the strategy</h2>
<p>A skill makes rules repeatable. It doesn&rsquo;t decide what you stand for. If the rules aren&rsquo;t settled, settle them first: positioning, audience, the one thing you lead with. If you want an outside primer on brand strategy before you write recipes, <a href="%FUTUR%">The Futur</a> has a deep library on it.</p>
<p>Then write the recipes from your real best lines. Take three headlines you would ship today and describe what they have in common. That description is the skill.</p>
<p>Related: if your proof points feed these skills, keep their permissions current with a <a href="%S_PROOF%">proof library in Sheets</a>. If you train reps on the result, <a href="%S_QUIZ%">a Forms quiz</a> checks the message stuck.</p>

<h2 id="status">What we have tested</h2>
<ul>
<li><b>Not yet tried by us:</b> skills in Workspace. They had not reached our account when we wrote this.</li>
</ul>
<p><i>Update, Oct 2026:</i> Google later said the skills rollout in Workspace was running slightly behind its original schedule. Check the <a href="%U_SKILLS%">announcement</a> for current dates.</p>
""" + TM,
    sources=[("Introducing skills in the Gemini app and Workspace, plus what's next for Gems (Google Workspace Updates, Sep 30, 2026)", U_SKILLS),
             ("About the transition from Gems to skills (Google Workspace Admin Help)", U_SKILLS_T)],
    related=["google-slides-collateral-messaging-sheet-gemini", "messaging-workshop-brand-style-sheet-google-sheets", "workspace-studio-shared-files-messaging-flow"],
)

# ====================================================================== 6. Studio shared files (Studio, Oct 13)
MIRROR_GS = """// In the SHARED messaging sheet. Copies the Messages tab into a private sheet that the Studio flow watches.
const PRIVATE_ID = 'paste-the-private-sheet-id';

function mirrorMessages() {
  const src = SpreadsheetApp.getActive().getSheetByName('Messages').getDataRange().getValues();
  const dst = SpreadsheetApp.openById(PRIVATE_ID).getSheetByName('Messages');
  const old = dst.getDataRange().getValues();
  if (JSON.stringify(old) === JSON.stringify(src)) return;   // write only when something changed
  dst.clearContents();
  dst.getRange(1, 1, src.length, src[0].length).setValues(src);
}

// Run once to mirror every 15 minutes.
function installMirror() {
  ScriptApp.newTrigger('mirrorMessages').timeBased().everyMinutes(15).create();
}"""

post(
    slug="workspace-studio-shared-files-messaging-flow",
    product="studio",
    date="2026-10-13", date_h="Oct 13, 2026",
    kicker="Automation",
    title="Workspace Studio Won't Run on Shared Files. Design Your Messaging Flow Around It.",
    h1="Workspace Studio won't run on shared files. Design around it.",
    dek="Studio flows fail on shared drives, shared folders and IMPORTRANGE. Messaging sheets are shared by definition. Here is the two-sheet pattern that works.",
    desc="Google Workspace Studio flows fail on shared drives, shared folders and IMPORTRANGE. A two-sheet pattern for product marketing: a shared messaging sheet mirrored to a private sheet that a Studio flow watches, summarising changes into Google Chat.",
    hero=("hero-studio", "Workspace Studio flow: when a sheet changes, ask Gemini to summarise the changed messaging lines, notify the launch space in Chat"),
    og="og-studio.png",
    tldr=[
        "Google&rsquo;s Studio guide: flows fail on Shared Drives, shared folders and sheets with IMPORTRANGE. Files must be private to you.",
        "Keep the team&rsquo;s messaging sheet shared. Mirror it to a <b>private sheet</b> the flow owner owns, with a short script.",
        "The flow watches the private sheet, asks Gemini what changed and which assets it touches, and posts to Chat.",
        "October&rsquo;s nested conditionals let one flow route headline changes and proof changes to different people.",
    ],
    body="""
<h2 id="wall">The wall</h2>
<p>The obvious product marketing flow: when the messaging sheet changes, tell the team what changed and which assets need updating. Workspace Studio has a starter for &ldquo;when a sheet changes&rdquo; and steps to ask Gemini and notify a Chat space. It should take five minutes.</p>
<p>Then it fails. <a href="%U_STUDIO%">Google&rsquo;s getting-started guide</a> lists the file restrictions: flows fail if you use Shared Drives, shared folders or spreadsheets with the IMPORTRANGE function, and files must be private to you. A messaging sheet that only one person can see isn&rsquo;t a messaging sheet.</p>

<h2 id="pattern">Two sheets: shared for people, private for the flow</h2>
{fig:studio-two-zones|Diagram: a shared messaging sheet edited by the team, a script copying it every 15 minutes into a private sheet owned by the flow owner, and a Studio flow watching the private sheet|People edit the shared sheet. The flow only ever touches the private copy.}
<ul>
<li><b>Shared sheet:</b> where the team writes and approves lines. Stays in your shared drive or folder.</li>
<li><b>Private sheet:</b> owned by the flow owner, shared with nobody, in My Drive. Holds a copy of the Messages tab.</li>
<li><b>Mirror script:</b> runs from the shared sheet and writes values into the private one. Values only, no IMPORTRANGE.</li>
</ul>
<p>In the shared sheet, open <b>Extensions &rsaquo; Apps Script</b> and paste:</p>
<pre>%MIRROR%</pre>
<p>Run <code>installMirror</code> once, as the flow owner. The script runs with that person&rsquo;s access, so it can write to their private sheet.</p>

<h2 id="flow">The flow</h2>
<ol class="steps">
<li><b>Starter:</b> when a sheet changes. Pick the private sheet and, if you like, only the Approved line column.</li>
<li><b>Step:</b> ask Gemini. &ldquo;List the messaging rows that changed. For each, give the key, the old and new line, and the assets in its Used in column.&rdquo;</li>
<li><b>Step:</b> notify the launch space in Chat with Gemini&rsquo;s answer.</li>
</ol>
{fig:studio-chat-message|Google Chat message from a flow: three approved lines changed, with keys, new wording and the assets each one appears in|What the launch space sees. Mockup.}
<p>On October 9, Google added <a href="%U_STUDIO_OCT%">nested conditionals and new search steps</a> to Studio. Use a condition to route by row type: headline and positioning changes to the PMM lead, proof changes to whoever owns the <a href="%S_PROOF%">proof library</a>.</p>

<h2 id="limits">Limits to plan for</h2>
<ul>
<li><b>Delay:</b> a 15-minute mirror plus the flow&rsquo;s own timing. Fine for messaging; wrong for anything urgent. The script only writes when the Messages tab actually changed, so the flow doesn&rsquo;t fire every 15 minutes.</li>
<li><b>One owner:</b> the private sheet and the flow belong to one person. Document who, and what happens when they leave.</li>
<li><b>Usage limits:</b> Studio has per-user limits that depend on your plan.</li>
<li><b>Gems:</b> if an older flow uses an Ask a Gem step, it will stop working as Gems are phased out. See <a href="%S_SKILLS%">turning your messaging recipes into Gemini skills</a>.</li>
</ul>
<p>For the meeting side of the same idea, see <a href="%S_MEET%">logging objections per slide from Meet notes</a>.</p>

<h2 id="status">What we have tested</h2>
<ul>
<li><b>Not yet run by us:</b> the mirror script and the flow together. The script is written against the Apps Script reference. Test on copies.</li>
</ul>
""" + TM,
    sources=[("Get started with Google Workspace Studio (Workspace Studio Help)", U_STUDIO),
             ("Guide to Starters & Steps in Workspace Studio", U_STUDIO_STEPS),
             ("New logic and search steps in Workspace Studio (Google Workspace Updates, Oct 9, 2026)", U_STUDIO_OCT)],
    related=["google-slides-collateral-messaging-sheet-gemini", "customer-proof-points-expiry-google-sheets", "gemini-skills-messaging-recipes"],
)

# ====================================================================== 7. Charts (Sheets, Oct 26)
BARS_GS = """// Draws a bar chart on the current slide as native rectangles and text boxes.
// Data: a two-column range (label, value) in the sheet named below.
const SHEET_ID = 'paste-your-sheet-id', RANGE = 'Chart!A2:B6';
const BAR = '#0066FF', INK = '#1C1E22', FONT = 'Verdana';

function drawBars() {
  const rows = SpreadsheetApp.openById(SHEET_ID).getRange(RANGE).getValues().filter(r => r[0] !== '');
  const slide = SlidesApp.getActivePresentation().getSelection().getCurrentPage().asSlide();
  const max = Math.max(...rows.map(r => r[1]));
  const left = 60, top = 80, rowH = 44, labelW = 150, maxW = 420;     // points
  rows.forEach((r, i) => {
    const y = top + i * rowH, w = Math.max(2, (r[1] / max) * maxW);
    const bar = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, left + labelW, y, w, rowH - 14);
    bar.getFill().setSolidFill(BAR); bar.getBorder().setTransparent();
    text(slide, String(r[0]), left, y, labelW - 10, rowH - 14, 'END');
    text(slide, String(r[1]), left + labelW + w + 8, y, 80, rowH - 14, 'START');
  });
}

function text(slide, s, x, y, w, h, align) {
  const box = slide.insertTextBox(s, x, y, w, h);
  box.getText().getTextStyle().setFontFamily(FONT).setFontSize(12).setForegroundColor(INK);
  box.getText().getParagraphStyle().setParagraphAlignment(SlidesApp.ParagraphAlignment[align]);
  box.setContentAlignment(SlidesApp.ContentAlignment.MIDDLE);
}"""

post(
    slug="on-brand-charts-google-slides",
    product="sheets",
    date="2026-10-26", date_h="Oct 26, 2026",
    kicker="Data design",
    title="On-Brand Charts in Google Slides: From Sheets Data to Native Shapes",
    h1="On-brand charts in Slides, from Sheets data to native shapes",
    dek="Sheets keeps adding chart types. None of them look like your brand once they're in a deck. Draw the chart as shapes instead, and every bar takes your colours and type.",
    desc="Make charts in Google Slides match your brand: when to link a Sheets chart, and when to draw it as native shapes and text boxes, by script for bars or with SVG to Slides for lines, areas and donuts.",
    hero=("hero-charts", "Slide with a bar chart built from native shapes in brand colours, one bar selected with the fill colour picker open"),
    og="og-charts.png",
    tldr=[
        "Sheets added box and whisker, combo and multi-series scatter charts this year. Linked into Slides, they still carry Sheets&rsquo; look.",
        "Linked charts are right when numbers change weekly. For launch decks and printed collateral, draw the chart as <b>native shapes</b>.",
        "Bar charts need only rectangles and text boxes: a short Apps Script draws them on the current slide.",
        "Curves (lines, areas, donuts) come in as SVG with SVG to Slides. Labels stay as live text boxes.",
    ],
    body="""
<h2 id="look">More chart types, same look</h2>
<p>Sheets has had a busy year for charts: <a href="%U_COMBO%">combo charts</a> and <a href="%U_SCATTER%">scatter charts with multiple x-series</a> in July, and <a href="%U_BOX%">native box and whisker charts</a> rolling out in October. All useful for analysis.</p>
<p>Paste one into Slides and it still looks like Sheets: its own fonts, gridlines and colours. In a sales deck built on your type and palette, a default chart is the one thing on the slide that isn&rsquo;t yours. (For why default type reads as default, <a href="%LINUS%">Linus Boman&rsquo;s video essays on typography</a> are a good watch.)</p>
{fig:chart-default-vs-brand|Two versions of the same chart on a slide: a default linked Sheets chart, and the same data drawn as native shapes in brand colours and type|Same data. Left: linked chart. Right: native shapes.}

<h2 id="when">When to link, when to draw</h2>
<table class="t"><tr><th>Use a linked chart when</th><th>Draw native shapes when</th></tr>
<tr><td>The numbers change weekly and someone clicks Update</td><td>The numbers are final for this launch or print run</td></tr>
<tr><td>It&rsquo;s an internal review deck</td><td>It&rsquo;s a customer-facing deck or one-pager</td></tr>
<tr><td>Accuracy matters more than look</td><td>It must match your type, colours and spacing</td></tr></table>
<p>Linked charts update from <b>Tools &rsaquo; Linked objects</b>. <a href="%U_LINKED%">Google&rsquo;s help page</a> covers how. Everything below is for the right-hand column.</p>

<h2 id="bars">Bars: rectangles and text boxes, by script</h2>
<p>A bar chart is rectangles and labels. Slides draws both natively, so a script can build one on the current slide from a range in Sheets. Every bar is then a shape you can recolour, and every label is text in your font.</p>
<pre>%BARS%</pre>
<p>Open your deck, go to <b>Extensions &rsaquo; Apps Script</b>, paste the code, set the sheet ID and range, select a slide and run <code>drawBars</code>. Change <code>BAR</code>, <code>INK</code> and <code>FONT</code> to your brand values. The <a href="%U_SLIDESAPP%">SlidesApp reference</a> covers each call.</p>

<h2 id="curves">Lines, areas, donuts: SVG to Slides</h2>
<p>Curves need custom geometry, which a script can&rsquo;t add to an existing deck. Draw them as SVG instead, in any tool that exports SVG, and bring them in with SVG to Slides.</p>
{fig:chart-pipeline|Pipeline: Sheets data, a chart tool that exports SVG in brand colours, SVG to Slides, native shapes plus text box labels on the slide|Data to SVG to native shapes.}
<ol class="steps">
<li>Style the chart in brand colours before export. Flat fills, no gradients or shadows.</li>
<li>Export as SVG.</li>
<li>Drag the file onto your Slides tab with SVG to Slides and press Cmd/Ctrl+V. Every path lands as a native shape. See <a href="%G_INSERT%">how to insert an SVG into Google Slides</a>.</li>
<li>Add labels as Slides text boxes, in your type styles. SVG text is not converted, and live labels are easier to edit and translate anyway.</li>
</ol>
<p>Native shapes stay sharp at any size, which matters when the same chart goes on a printed one-pager. The <a href="%G_VS%">SVG vs PNG comparison</a> shows the difference.</p>

<h2 id="highlight">Highlight one bar</h2>
{fig:chart-recolor|A native-shape bar chart with one bar selected and recoloured with the fill colour picker to highlight it|Click a bar, pick a colour. It&rsquo;s a shape.}
<p>The best reason to draw charts as shapes: you can make the point of the chart obvious. Grey every bar, then recolour the one that matters. <a href="%G_RECOLOR%">Recolouring a shape in Google Slides</a> is one click in the fill picker.</p>

<h2 id="status">What we have tested</h2>
<ul>
<li>SVG to Slides converts rects, circles and paths, which is all a flat chart SVG contains. Text and gradients are the parts to check after import.</li>
<li><b>Not yet run by us:</b> the <code>drawBars</code> script. It&rsquo;s written against the SlidesApp reference. Run it on a copy.</li>
</ul>
<p>If localized decks carry these charts, give the labels budgets too: see <a href="%S_LOC%">localizing a one-pager without breaking the layout</a>.</p>
""" + TM,
    sources=[("Google Sheets adds box and whisker charts (Android Authority, Oct 22, 2026)", U_BOX),
             ("Import and create combo charts in Google Sheets (Google Workspace Updates, Jul 20, 2026)", U_COMBO),
             ("Create and import scatter charts with multiple x-series in Google Sheets (Google Workspace Updates, Jul 29, 2026)", U_SCATTER),
             ("Linked objects in Google Docs, Sheets and Slides (Google Docs Editors Help)", U_LINKED),
             ("Slides Service reference (Google Apps Script)", U_SLIDESAPP)],
    related=["native-ui-mockups-google-slides", "competitor-matrix-google-sheets-gemini-citations", "localize-one-pager-google-slides"],
)

# ====================================================================== 8. Competitor matrix (Sheets, Oct 29)
post(
    slug="competitor-matrix-google-sheets-gemini-citations",
    product="sheets",
    date="2026-10-29", date_h="Oct 29, 2026",
    kicker="Competitive intel",
    title="Build a Competitor Matrix in Google Sheets Where Every Cell Cites Its Source",
    h1="A competitor matrix where every cell cites its source",
    dek="AI-filled competitive research was unusable because nobody could check it. As of this week, Fill with Gemini attaches a web source to each cell. Build the matrix around that.",
    desc="Build a competitive analysis matrix in Google Sheets with Fill with Gemini's new cell-level web citations: one row per claim, a checked-on date, a staleness flag, and only cited, verified cells on the battlecard.",
    hero=("hero-matrix", "Google Sheets competitor matrix with a cell selected and a popover listing the web sources Gemini used for that value"),
    og="og-matrix.png",
    tldr=[
        "Since October 28, values generated with Fill with Gemini carry <b>web citations per cell</b> in Sheets on the web. Requests can cover up to 3,000 cells.",
        "Lay the matrix out long: one row per competitor and claim. It sorts, filters and cites cleanly.",
        "Add a Checked on date and a staleness flag. A citation tells you where to look, not that the claim is true.",
        "Only cited cells that a person has opened and confirmed reach the battlecard.",
    ],
    body="""
<h2 id="what">What changed on October 28</h2>
<p>Competitive matrices go stale fast and are tedious to fill. AI could fill them, but an uncited &ldquo;Yes&rdquo; in a pricing column is worse than a blank: someone repeats it on a call.</p>
<p>On October 28, Google announced that <a href="%U_CITE%">Fill with Gemini now provides cell-level citations for web sources</a>. Each generated value gets its sources attached, and you can open them per cell in Sheets on the web. The same update lets one request cover far more cells: up to 3,000, according to coverage of the announcement.</p>
<p>That turns the AI-filled matrix from a liability into a first draft you can audit.</p>

<h2 id="layout">Lay it out long, not wide</h2>
<p>The classic matrix has competitors across the top and features down the side. It reads well and maintains badly. Use one row per competitor and claim instead.</p>
{fig:matrix-layout|Mockup of a long-format competitor matrix: Competitor, Capability, Value, Evidence, Source, Checked on, Status columns, with one stale row flagged|One row per competitor and claim. Mockup.}
<ul>
<li><b>Competitor</b> and <b>Capability:</b> &ldquo;Acme&rdquo;, &ldquo;SSO on all plans&rdquo;.</li>
<li><b>Value:</b> Yes, No, Partial, Unclear.</li>
<li><b>Evidence:</b> one short phrase from the source.</li>
<li><b>Source:</b> the URL you confirmed, pasted by hand during review.</li>
<li><b>Checked on</b> and <b>Status:</b> who confirmed it, and when.</li>
</ul>
<p>Long format sorts by competitor, filters by capability, and pivots back into the wide view for a slide whenever you need it.</p>

<h2 id="fill">Fill with Gemini</h2>
<p>Select the empty Value cells and use Fill with Gemini, or write the <a href="%U_AI_FN%">AI function</a> directly:</p>
<pre>=AI("Using the vendor's public pricing or documentation pages, does "&amp;A2&amp;" offer "&amp;B2&amp;"? Answer Yes, No, Partial or Unclear, then a short phrase of evidence.")</pre>
<p>Open the citations on a few cells before you trust the rest. You are checking two things: that the source is the vendor&rsquo;s own page, not a reseller or a forum, and that it says what the cell says.</p>

<h2 id="stale">Make staleness visible</h2>
<pre>=IF(F2="","Not checked",IF(TODAY()-F2&gt;90,"Recheck","OK"))</pre>
<ul>
<li><b>Not checked:</b> AI value, nobody opened the source. Never leaves the sheet.</li>
<li><b>Recheck:</b> confirmed more than 90 days ago. Pricing pages change.</li>
<li><b>Unclear</b> values are research tasks. Assign them.</li>
</ul>

<h2 id="card">From matrix to battlecard</h2>
{fig:matrix-to-battlecard|Matrix rows marked OK feeding a battlecard; each claim on the card has a numbered footnote that matches a source URL|Only confirmed rows reach the card, each with its footnote.}
<p>Filter the matrix to Status = OK for one competitor. Those rows, and only those, go on the battlecard, each with a numbered footnote to its source. Reps can open the source in front of a prospect, which is the point. Put the competitor&rsquo;s logo on the card as a vector so it prints cleanly: here is <a href="%G_LOGOS%">how to add a logo to Google Slides</a>.</p>
<p>Customer proof on the same card has its own expiry dates. Track those in a <a href="%S_PROOF%">proof library</a>. Charts that compare you with the competitor should match your brand: <a href="%S_CHARTS%">draw them as native shapes</a>.</p>

<h2 id="status">What we have tested</h2>
<ul>
<li><b>Checked in Sheets:</b> the staleness formula.</li>
<li><b>Not yet checked by us:</b> cell-level citations. They were rolling out when we wrote this. We also don&rsquo;t know yet whether a script can read the citations, so the Source column is filled by hand.</li>
</ul>
""" + TM,
    sources=[("Fill with Gemini now provides cell-level citations for web sources and supports larger requests (Google Workspace Updates, Oct 28, 2026)", U_CITE),
             ("Use the AI function in Google Sheets (Google Docs Editors Help)", U_AI_FN)],
    related=["google-slides-collateral-messaging-sheet-gemini", "customer-proof-points-expiry-google-sheets", "on-brand-charts-google-slides"],
)

# ====================================================================== 9. Audit (Slides, Nov 3)
AUDIT_GS = """// Bound to a sheet. Put the deck URL in Audit!B1. Menu: Audit > Snapshot / Diff last two.
function onOpen() {
  SpreadsheetApp.getUi().createMenu('Audit')
    .addItem('Snapshot deck', 'snapshot').addItem('Diff last two snapshots', 'diff').addToUi();
}

function snapshot() {
  const ss = SpreadsheetApp.getActive();
  const deck = SlidesApp.openByUrl(ss.getSheetByName('Audit').getRange('B1').getValue());
  const rows = [['Slide', 'Object ID', 'Type', 'Tag', 'Left', 'Top', 'Width', 'Height', 'Font', 'Size', 'Text']];
  deck.getSlides().forEach((slide, i) => slide.getPageElements().forEach(el => {
    let font = '', size = '', text = '';
    if (el.getPageElementType() === SlidesApp.PageElementType.SHAPE) {
      const t = el.asShape().getText();
      text = t.asString().trim();
      if (text) { font = t.getTextStyle().getFontFamily() || 'mixed'; size = t.getTextStyle().getFontSize() || 'mixed'; }
    }
    rows.push([i + 1, el.getObjectId(), String(el.getPageElementType()), el.getTitle() || '',
               Math.round(el.getLeft()), Math.round(el.getTop()), Math.round(el.getWidth()), Math.round(el.getHeight()), font, size, text]);
  }));
  const sh = ss.insertSheet('Snap ' + Utilities.formatDate(new Date(), ss.getSpreadsheetTimeZone(), 'MM-dd HHmmss'));
  sh.getRange(1, 1, rows.length, rows[0].length).setValues(rows);
}

function diff() {
  const ss = SpreadsheetApp.getActive();
  const snaps = ss.getSheets().filter(s => s.getName().startsWith('Snap ')).sort((x, y) => x.getName() < y.getName() ? -1 : 1).slice(-2);
  if (snaps.length < 2) throw new Error('Take two snapshots first.');
  const [a, b] = snaps.map(s => new Map(s.getDataRange().getValues().slice(1).map(r => [r[1], r])));
  const head = ['Slide', 'Object ID', 'Type', 'Tag', 'Left', 'Top', 'Width', 'Height', 'Font', 'Size', 'Text'];
  const out = [['Slide', 'Object ID', 'Tag', 'Change', 'Before', 'After']];
  a.forEach((r, id) => {
    const n = b.get(id);
    if (!n) { out.push([r[0], id, r[3], 'Deleted', r[10], '']); return; }
    for (let k = 4; k < head.length; k++) if (String(r[k]) !== String(n[k])) out.push([n[0], id, n[3], head[k], r[k], n[k]]);
  });
  b.forEach((n, id) => { if (!a.has(id)) out.push([n[0], id, n[3], 'New object', '', n[10]]); });
  const sh = ss.getSheetByName('Diff') || ss.insertSheet('Diff');
  sh.clearContents().getRange(1, 1, out.length, out[0].length).setValues(out);
}"""

post(
    slug="audit-gemini-whole-deck-edits-google-slides",
    product="slides",
    date="2026-11-03", date_h="Nov 3, 2026",
    kicker="Quality control",
    title="Audit Gemini's Whole-Deck Edits in Google Slides: Snapshot, Edit, Diff",
    h1="Audit what Gemini's whole-deck edit changed",
    dek="Gemini can now edit an entire presentation from one prompt. It tells you what it changed. Here is how to check, object by object, with a snapshot before and a diff after.",
    desc="Gemini in Google Slides can now edit a whole deck from one prompt. An Apps Script that snapshots every object (text, font, size, position, alt text tag) before and after, and diffs the two in Google Sheets.",
    hero=("hero-audit", "Two snapshots of the same deck side by side with a diff sheet listing changed text, a changed font and a moved text box"),
    og="og-audit.png",
    tldr=[
        "Since October 30, Gemini in Slides can <b>edit multiple slides or a whole deck</b> from one prompt, and it lists what it changed.",
        "For collateral with approved copy, check the list against the deck: text, fonts, sizes, positions, new and deleted objects, alt text tags.",
        "A short Apps Script snapshots every object to a sheet. Snapshot, run the prompt, snapshot again, diff.",
        "Anything in the diff you didn&rsquo;t ask for gets undone.",
    ],
    body="""
<h2 id="what">One prompt, many slides</h2>
<p>On October 30, Google announced that <a href="%U_WHOLE%">Gemini in Google Slides can edit multiple slides or an entire presentation at once</a>. You can refresh fonts, backgrounds and colour schemes across a deck, restyle it to match another file, or condense and expand slides. Gemini decides which slides need to change and lists the changes in the side panel.</p>
<p>For a pitch draft, the list is enough. For a solution brief with approved wording, slot tags and a print layout, you want to know exactly which objects moved and which words changed. That takes a before and an after.</p>

<h2 id="loop">The loop</h2>
{fig:audit-flow|Four steps: snapshot the deck to a sheet, run the Gemini prompt, snapshot again, diff the two snapshots|Snapshot, edit, snapshot, diff.}
<ol class="steps">
<li><b>Snapshot.</b> Record every object on every slide.</li>
<li><b>Edit.</b> Run your prompt in the Gemini side panel.</li>
<li><b>Snapshot again.</b></li>
<li><b>Diff.</b> List every object whose text, font, size or position changed, and every object added or deleted.</li>
</ol>

<h2 id="script">The script</h2>
<p>Make a sheet with a tab called <b>Audit</b> and paste the deck URL into B1. Then <b>Extensions &rsaquo; Apps Script</b>, paste this, save and reload:</p>
<pre>%AUDIT%</pre>
<p>The <b>Audit</b> menu appears in the sheet. Each snapshot gets its own tab. <b>Diff last two snapshots</b> writes a Diff tab.</p>
{fig:audit-diff-sheet|Mockup of a Diff tab listing a changed text line, a font change, a moved text box and a new object, with slide numbers and alt text tags|A Diff tab after a restyle prompt. Mockup.}

<h2 id="read">Reading the diff</h2>
<ul>
<li><b>Text:</b> compare each changed line with your approved copy. Paraphrase is the most common drift.</li>
<li><b>Font and size:</b> a restyle prompt should change these. A copy prompt shouldn&rsquo;t.</li>
<li><b>Left, top, width, height:</b> moved boxes cause layout shift. Check the page.</li>
<li><b>New object / Deleted:</b> a deleted object loses its object ID and its alt text tag. If scripts find boxes by tag, re-tag the replacement.</li>
<li><b>Tag:</b> the alt text title. If you tag boxes like <code>slot:headline</code>, the diff shows which slot changed.</li>
</ul>
<p>Two limits: the snapshot reads top-level objects, so shapes inside a group appear as one group; and it records the style of the text as a whole, shown as &ldquo;mixed&rdquo; when a box has more than one font or size.</p>

<h2 id="fix">When something changed that shouldn&rsquo;t have</h2>
<p>Gemini&rsquo;s edits work like your own: undo and version history both apply. Undo straight away, or restore the version from before the prompt and rerun with a tighter instruction. &ldquo;Do not change any text&rdquo; and &ldquo;do not move or resize any object&rdquo; are worth stating outright.</p>
<p>If your decks are localized, run the diff on every language version: a font change that fits English may break German. See <a href="%S_LOC%">localizing a one-pager without breaking the layout</a>. If a skill drives the prompt, the diff is how you test it: see <a href="%S_SKILLS%">Gemini skills for messaging recipes</a>.</p>

<h2 id="status">What we have tested</h2>
<ul>
<li><b>Not yet run by us against a Gemini edit:</b> whole-deck editing hadn&rsquo;t reached our account when we wrote this. Google said rollout could take longer than 15 days.</li>
<li>The script is written against the <a href="%U_SLIDESAPP%">SlidesApp reference</a>. Run it on copies.</li>
</ul>
<p><i>Update, Nov 2026:</i> part 1 of our collateral series puts this to work: <a href="%P1%">update Google Slides collateral from one messaging sheet with Gemini</a>.</p>
""" + TM,
    sources=[("Edit entire presentations with Gemini in Google Slides (Google Workspace Updates, Oct 30, 2026)", U_WHOLE),
             ("Slides Service reference (Google Apps Script)", U_SLIDESAPP)],
    related=["google-slides-collateral-messaging-sheet-gemini", "native-ui-mockups-google-slides", "gemini-skills-messaging-recipes"],
)

# ====================================================================== 10. UI mockups (Slides, Nov 10)
post(
    slug="native-ui-mockups-google-slides",
    product="slides",
    date="2026-11-10", date_h="Nov 10, 2026", order=2,
    kicker="Product visuals",
    title="Product UI Mockups in Google Slides That Don't Go Stale",
    h1="Product screenshots go stale. Native UI mockups don't.",
    dek="Every release breaks the screenshots in your decks. Build simplified product UI as native shapes and live text instead, kept in one library deck, and a renamed button is a find and replace.",
    desc="Replace product screenshots in Google Slides decks and one-pagers with simplified UI mockups made of native shapes and live text: built in Figma, brought in as SVG with SVG to Slides, kept in a searchable library deck.",
    hero=("hero-ui", "Google Slides with a simplified product UI mockup built from native shapes; one button is selected and its label is a live text box"),
    og="og-ui.png",
    tldr=[
        "Screenshots go stale every release, blur in print, and can&rsquo;t be searched, recoloured or translated.",
        "A <b>simplified UI mockup</b> shows the one thing the slide is about, in your brand colours, at any size.",
        "Build components in Figma, export SVG, drop them into Slides with SVG to Slides. Shapes land native; labels go in as Slides text boxes.",
        "Keep every component in one <b>library deck</b> with a searchable label, so anyone can copy the current version.",
    ],
    body="""
<h2 id="stale">Why screenshots rot</h2>
<p>A screenshot is a picture of one build of your product, on one screen, at one size. The next release renames a button and it&rsquo;s wrong. Printed on a one-pager, it&rsquo;s soft. Put in a German deck, the UI is still in English. And nobody can find which twelve decks use it.</p>
{fig:ui-screenshot-vs-native|Side by side: a product screenshot pasted as an image, blurry and showing an old Export label, and the same screen as a native mockup with crisp shapes and a live Share label|Left: a screenshot. Right: the same screen as native shapes and text.}
<p>A simplified mockup fixes all four. It shows only what the slide is about, built from shapes and live text. It scales cleanly, takes your colours, translates like any text box, and a find and replace updates every label.</p>

<h2 id="simplify">Simplify first</h2>
<p>A mockup is a diagram of the product, not a copy of it. For each slide, decide the one thing the viewer should see, and draw that.</p>
<ul>
<li><b>Keep:</b> the layout, the element being talked about, the labels that explain it.</li>
<li><b>Drop:</b> real data, menus nobody looks at, avatars, timestamps, scroll bars.</li>
<li><b>Grey everything</b> except the element the slide is about. Colour that one.</li>
<li><b>Eight to twenty elements</b> per mockup. More, and it&rsquo;s a screenshot again.</li>
</ul>

<h2 id="build">Build in Figma, bring in as SVG</h2>
<ol class="steps">
<li><b>Draw components in Figma:</b> button, input, toggle, card, nav bar, table row. Flat fills and strokes. No shadows, blurs or gradients.</li>
<li><b>Keep text out of the SVG,</b> or delete it after export. Labels go in as Slides text boxes so they stay editable.</li>
<li><b>Export each component as SVG.</b> Figma&rsquo;s <a href="%U_FIGMA_SVG%">export settings</a> cover the options.</li>
<li><b>Drop it into Slides with SVG to Slides.</b> Drag the file onto your Slides tab, click where it goes, press Cmd/Ctrl+V. Every path becomes a native shape. Step by step: <a href="%G_INSERT%">how to insert an SVG into Google Slides</a>.</li>
<li><b>Add the labels</b> as text boxes in your type styles, on top of the shapes. Group them.</li>
</ol>
<p>Why flat: SVG to Slides converts paths, shapes, fills and strokes. Filters, clip paths, patterns and gradient transforms don&rsquo;t convert. <a href="%G_SUPPORT%">What Google Slides supports from SVG</a> has the details.</p>

<h2 id="library">One library deck</h2>
<p>Put every component on its own slide in a single deck: the UI library. Under each one, add a small text label in white or light grey with its name, like <code>ui:button-primary</code>. Nobody sees it in use, but <b>Ctrl+F</b> finds it.</p>
{fig:ui-library-deck|A library deck in Google Slides: filmstrip of UI components, one slide showing a primary button with its search label ui:button-primary highlighted|The UI library. Each slide holds one component and a searchable label. Mockup.}
<ul>
<li>When the product changes, update the component in the library. Note the date on the slide.</li>
<li>To use one, copy it from the library. Don&rsquo;t copy from an old deck.</li>
<li>The same deck holds your icons. Convert an open-licence set once, one icon per slide, each with its label. That answers &ldquo;where do I get <a href="%G_LOGOS%">icons for Google Slides</a>?&rdquo; for the whole team.</li>
</ul>

<h2 id="rename">A renamed button is a find and replace</h2>
{fig:ui-rename-flow|Find and replace dialog in Google Slides replacing Export with Share across all slides, and three mockups updated|One rename, every mockup in the deck. Mockup.}
<p>Labels are live text, so <b>Edit &rsaquo; Find and replace</b> updates every mockup in a deck at once. Colours are fills, so a rebrand is a recolour: <a href="%G_RECOLOR%">change the colour of any shape or icon in Google Slides</a> with the fill picker. And the same mockup works in Docs and Drawings, since it&rsquo;s native shapes.</p>
<p>Logo designers build marks as vectors so one file works at every size. If you want to see that discipline up close, <a href="%WILL%">Will Paterson&rsquo;s logo design channel</a> walks through it. Your product visuals deserve the same treatment: one source, every size, no blur. That&rsquo;s the <a href="%G_VS%">SVG vs PNG</a> argument in practice.</p>

<h2 id="series">Where this fits</h2>
<p>This is the visual side of the collateral system in <a href="%P1%">part 1</a> and <a href="%P2%">part 2</a>: copy comes from the messaging sheet, visuals come from the library. Charts follow the same rule: <a href="%S_CHARTS%">draw them as native shapes</a>. And after any Gemini restyle, <a href="%S_AUDIT%">diff the deck</a> to check the mockups weren&rsquo;t touched.</p>

<h2 id="status">What we have tested</h2>
<ul>
<li><b>Checked:</b> a 16-element UI mockup SVG converted to 12 native shapes and 2 text boxes with the SVG to Slides converter and our placement script, and the shapes recolour with the fill picker.</li>
<li><b>Note:</b> the Chrome extension doesn&rsquo;t convert SVG text. Add labels as text boxes, as above.</li>
</ul>
""" + TM,
    sources=[("Export formats and settings (Figma Help Center)", U_FIGMA_SVG)],
    related=["on-brand-charts-google-slides", "audit-gemini-whole-deck-edits-google-slides", "google-slides-collateral-messaging-sheet-gemini"],
)
