"""Blog post: Apps Script for GTM, part 1. Deck embed, share and copy links, cheat sheet download.

Content comes from tools/gtm_appscript.py (also used by gtm_deck.py and gtm_cheatsheet.py).
"""
import gtm_appscript as G
from blog_workspace import post, POSTS, TM, S_PROOF, S_LOC, S_AUDIT, S_STUDIO, P1

DECK_ID = "1MW2JGarOCNQnrnOQB96S4jwry3sLnud6JhM42LrvjK0"
DECK = f"https://docs.google.com/presentation/d/{DECK_ID}"
EMBED = f"{DECK}/embed?start=false&loop=false&delayms=5000"
CHEAT = "/static/blog/files/apps-script-for-gtm-part-1-cheat-sheet.pdf"

SHARE_JS = """<script>
(function(){var b=document.getElementById('sharedeck');if(!b)return;
b.addEventListener('click',function(){var u=b.getAttribute('data-url'),t=b.getAttribute('data-title');
if(navigator.share){navigator.share({title:t,url:u}).catch(function(){});return;}
var done=function(){var o=b.textContent;b.textContent='Link copied';setTimeout(function(){b.textContent=o},1800)};
if(navigator.clipboard){navigator.clipboard.writeText(u).then(done)}else{prompt('Copy this link',u)}});})();
</script>"""

ICON_SHARE = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg>'
ICON_DL = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3v12M7 10l5 5 5-5M5 21h14"/></svg>'

c = G.code_html

BODY = f"""
<p>Launch work in Google Workspace is mostly the same few moves, repeated: copy a deck, change the company name, paste a line from a sheet, draft the same email twenty times. Apps Script does those moves for you. It&rsquo;s JavaScript that runs inside Workspace, it&rsquo;s already in your account, and it needs no server.</p>
<p>Part 1 is five scripts a product marketer can run this week. The deck below walks through them. The post has the same code to copy, and the cheat sheet puts all of it on two pages.</p>

<div class="deckembed"><div class="fr"><iframe src="{EMBED}" title="Apps Script for GTM, part 1: slides" allowfullscreen loading="lazy"></iframe></div></div>
<div class="deckacts">
<a class="pri" href="{CHEAT}" download>{ICON_DL}Download the cheat sheet (PDF)</a>
<button id="sharedeck" type="button" data-url="{DECK}/edit?usp=sharing" data-title="Apps Script for GTM, part 1">{ICON_SHARE}Share the deck</button>
<a href="{DECK}/copy">Make a copy</a>
<a href="{DECK}/present">Present full screen</a>
</div>

<h2 id="where">Where it lives</h2>
<p>Open any Google Sheet and choose <b>Extensions &rsaquo; Apps Script</b>. That opens a script bound to the sheet: it can add menus to that sheet and react when someone edits it. Standalone scripts live at script.google.com and suit jobs that span many files. Everything here is bound to a sheet.</p>

<h2 id="menu">First script: a GTM menu</h2>
{c("menu")}
<ol class="steps">
<li>Paste the code and click <b>Save</b>.</li>
<li>Pick a function in the toolbar dropdown and click <b>Run</b>.</li>
<li>The first run asks for permission. Read what it asks for, then allow.</li>
<li>Reload the sheet. The <b>GTM</b> menu appears next to Help.</li>
</ol>

<h2 id="fits">Superpower 1: a formula that checks copy length</h2>
<p>A function marked <code>@customfunction</code> works in a cell like any built-in formula. This one compares a line with its character budget, so overflow shows up in the sheet before it reaches a slide. It&rsquo;s the check behind <a href="{S_LOC}">localizing a one-pager without breaking the layout</a>.</p>
{c("fits")}
<p>In a cell: <code>=FITS(D2, E2)</code>. Google&rsquo;s <a href="{G.CUSTOM_FN}">custom functions guide</a> covers what they can and can&rsquo;t do.</p>

<h2 id="decks">Superpower 2: one deck per account, from a template</h2>
<p>Put tokens like <code>{{{{Company}}}}</code>, <code>{{{{Pain}}}}</code> and <code>{{{{Champion}}}}</code> on your template slides. Give the Accounts tab matching column headers. One run copies the template for every row and fills in the tokens.</p>
{c("decks")}
<p>Logos and icons on the template should be vectors so every copy stays sharp: here&rsquo;s <a href="/guides/svg-logos-icons-google-slides">how to add a logo to Google Slides as an editable shape</a>.</p>

<h2 id="drafts">Superpower 3: follow-ups as drafts, not sends</h2>
<p>Rows marked Ready on a Follow-ups tab become Gmail drafts. Nothing is sent. A person reads every draft and clicks Send.</p>
{c("drafts")}

<h2 id="weekly">Superpower 4: run it every Monday</h2>
<p>A time-driven trigger runs a function on a schedule, with the sheet closed. Run <code>installWeekly</code> once. The digest checks the Days left column of a <a href="{S_PROOF}">proof library</a> and emails you what expires within 30 days.</p>
{c("weekly")}
<p>Google&rsquo;s <a href="{G.TRIGGERS}">triggers guide</a> lists every kind of trigger.</p>

<h2 id="stamp">Superpower 5: stamp every messaging change</h2>
<p><code>onEdit</code> is a simple trigger: name a function that, and it runs on every edit, no setup. This one writes the time into column I whenever a row on the Messages tab changes.</p>
{c("stamp")}

<h2 id="debug">Test small</h2>
{c("debug")}
<p>Run the test function from the editor. <code>console.log</code> output shows in the execution log, and <b>View &rsaquo; Executions</b> lists every run.</p>

<h2 id="safety">Before you share a script</h2>
<ul>
<li>Read the permission screen. It lists exactly what the script can touch.</li>
<li>Scripts run as whoever runs them, with that person&rsquo;s access.</li>
<li>Draft before you send. Copy before you overwrite. Test on copies of real files.</li>
<li>Quotas apply: one run stops at 6 minutes, and email has daily limits. See Google&rsquo;s <a href="{G.QUOTAS}">quotas page</a>.</li>
</ul>

<div class="cheat"><a href="{CHEAT}" download><img src="/static/blog/img/cheat-appscript-1.png" width="816" height="1056" alt="Page 1 of the Apps Script for GTM cheat sheet" loading="lazy"></a>
<div><p><b>The cheat sheet.</b> Two pages: where scripts live, how to run them, all five superpowers with code, the safety checklist. Print it or keep it next to the editor.</p>
<div class="deckacts" style="margin:0"><a class="pri" href="{CHEAT}" download>{ICON_DL}Download the PDF</a></div></div></div>

<div class="tease"><h2 id="part2">Coming in part 2: talk to everything else</h2>
<p>Part 1 stays inside your Google account. Part 2 reaches out:</p>
<ul>
<li><b>UrlFetchApp</b> to pull CRM and product data into Sheets.</li>
<li>Launch updates posted to a Google Chat space.</li>
<li>Gemini, called from a script, drafting copy to a character budget.</li>
<li>A tiny internal web app with <code>doGet()</code>.</li>
</ul></div>

<h2 id="status">What we have tested</h2>
<ul>
<li><b>Checked:</b> <code>FITS()</code> returns OK and Over by 9 for the two test lines above (run in JavaScript outside Apps Script). Every snippet passes a JavaScript syntax check.</li>
<li><b>Not yet run by us in Apps Script:</b> the menu, deck, draft, trigger and onEdit scripts. They&rsquo;re written against Google&rsquo;s <a href="{G.REF}">Apps Script reference</a>. Run them on copies first.</li>
</ul>
<p>More builds on the same sheet: <a href="{P1}">update collateral from one messaging sheet</a>, <a href="{S_STUDIO}">Workspace Studio flows on shared files</a>, <a href="{S_AUDIT}">diffing Gemini&rsquo;s deck edits</a>.</p>
{SHARE_JS}
""" + TM.replace("Google Workspace are", "Google Workspace and Apps Script are")

post(
    slug="apps-script-for-gtm-part-1",
    product="appsscript",
    date="2026-11-10", date_h="Nov 10, 2026", order=3,
    kicker="Apps Script for GTM, part 1",
    title="Google Apps Script for GTM: 5 Scripts Product Marketers Can Run This Week (Part 1)",
    h1="Apps Script for GTM superpowers, part 1",
    dek="Five scripts that turn Sheets into a launch control panel: a copy-length formula, one deck per account, follow-up drafts, a Monday digest and a change log. Slides, code and a cheat sheet.",
    desc="A practical Google Apps Script guide for product marketing and GTM teams: custom menus, a copy-length formula, personalised decks from a template, Gmail drafts from a sheet, time triggers and onEdit. Embedded slides, copyable code and a two-page cheat sheet.",
    hero=("hero-appscript-1", "Apps Script code that builds one Google Slides deck per account from a template"),
    og="og-appscript-1.png",
    tldr=[
        "Apps Script is JavaScript inside Google Workspace. Open a sheet, then <b>Extensions &rsaquo; Apps Script</b>.",
        "Five scripts: <code>FITS()</code> for copy length, <code>buildDecks()</code>, <code>draftFollowUps()</code>, a Monday trigger, an <code>onEdit</code> change stamp.",
        "Draft before you send, copy before you overwrite, read the permission screen.",
        "Slides embedded below, plus a two-page cheat sheet. Part 2 connects scripts to outside APIs.",
    ],
    body=BODY,
    sources=[("Apps Script reference (Google for Developers)", G.REF),
             ("Custom functions in Google Sheets (Apps Script guide)", G.CUSTOM_FN),
             ("Triggers (Apps Script guide)", G.TRIGGERS),
             ("Quotas for Google services (Apps Script guide)", G.QUOTAS)],
    related=["customer-proof-points-expiry-google-sheets", "localize-one-pager-google-slides", "google-slides-collateral-messaging-sheet-gemini"],
)
