#!/usr/bin/env python3
"""Render figures for the ten Workspace-for-PMM posts (tools/blog_workspace.py).

Every figure is an HTML mockup screenshotted with headless Chrome. Each post's
figures use its product colour (PRODUCTS in build_site.py) as the dominant accent.
They are illustrations, not captures of Google's UI.

Usage: python3 tools/workspace_images.py [name ...]   (needs playwright, Chrome, Overpass + Roboto)
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import collateral_images as CI  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cloud" / "static" / "blog" / "img"

PC = {  # dominant colour, darker tone, light tint, ink on dominant
    "slides": ("#F4B400", "#8A5A00", "#FEF4D6", "#1C1E22"),
    "sheets": ("#188038", "#0D652D", "#E3F3E8", "#FFFFFF"),
    "gemini": ("#3B5BDB", "#2A44B0", "#E6EBFC", "#FFFFFF"),
    "studio": ("#E8710A", "#B4500A", "#FDEBDC", "#1C1E22"),
    "meet": ("#00897B", "#00695C", "#DDF2EF", "#FFFFFF"),
    "forms": ("#7248B9", "#56338F", "#EEE7F8", "#FFFFFF"),
    "appsscript": ("#1A73E8", "#1557B0", "#E8F0FE", "#FFFFFF"),
}
LABEL = {"slides": "Google Slides", "sheets": "Google Sheets", "gemini": "Gemini", "studio": "Workspace Studio",
         "meet": "Google Meet", "forms": "Google Forms", "appsscript": "Apps Script"}

EXTRA = """
.ico.d{background:#4285f4}.ico.f{background:#7248b9}.ico.m{background:#00897b}.ico.c{background:#188038}.ico.w{background:#e8710a}
.dia .cap{color:var(--pcd)}
.ring{border-color:var(--pc)!important}
.note{background:var(--pcd)}
.pcbox{border:2.5px solid var(--pc);background:var(--pct)}
.hl{background:var(--pct)!important}
.hlc{background:var(--pc)!important;color:var(--pci)!important}
.hero{width:1200px;height:630px;background:var(--pc);position:relative;overflow:hidden}
.hero .lab{position:absolute;left:44px;top:34px;background:#fff;color:#1c1e22;font-family:Overpass,sans-serif;font-weight:800;font-size:15px;letter-spacing:.1em;text-transform:uppercase;border-radius:999px;padding:7px 16px 5px}
.hero .ttl2{position:absolute;left:44px;top:84px;width:380px;font-family:Overpass,sans-serif;font-weight:800;font-size:40px;line-height:1.05;letter-spacing:-.02em;color:var(--pci)}
.hero .cw{position:absolute;left:460px;top:0;bottom:0;right:-60px;display:flex;align-items:center}
.sf{position:relative;background:#fff;box-shadow:0 1px 3px rgba(60,64,67,.3);overflow:hidden}.sf .ab{position:absolute}
.hero .foot{position:absolute;left:44px;bottom:36px;font-family:Overpass,sans-serif;font-weight:700;font-size:16px;color:var(--pci);opacity:.85}
.pill{display:inline-block;border-radius:999px;padding:2px 10px;font-size:11px;font-weight:500}
.doc{background:#fff;width:560px;margin:0 auto;box-shadow:0 1px 3px rgba(60,64,67,.3);padding:40px 48px;font-family:Roboto,Arial,sans-serif;font-size:12.5px;line-height:1.55;color:#1c1e22}
.doc h3{font-size:20px;font-weight:400;margin-bottom:10px}.doc h4{font-size:14px;font-weight:500;margin:14px 0 6px}
.doc li{margin-left:18px}
.flowcard{background:#fff;border:1px solid #dadce0;border-radius:12px;padding:12px 16px;width:430px;box-shadow:0 1px 2px rgba(0,0,0,.08)}
.flowcard small{display:block;font-size:11px;color:#5f6368;text-transform:uppercase;letter-spacing:.06em;font-weight:500}
.flowcard b{font-weight:500;font-size:14px}.flowcard p{font-size:12px;color:#5f6368;margin-top:3px;line-height:1.45}
.vline{width:2px;height:22px;background:#9aa0a6;margin:0 auto}
.chat{background:#fff;border:1px solid #dadce0;border-radius:14px;width:620px;padding:16px 18px;font-size:13px;line-height:1.5}
.chat .who{display:flex;gap:10px;align-items:center;margin-bottom:8px}.chat .who b{font-weight:500}
.chat .ln{border-left:3px solid var(--pc);padding:4px 10px;margin:8px 0;background:#f8f9fa;border-radius:0 6px 6px 0}
.mono{font-family:'Roboto Mono',monospace;font-size:11px}
.thumb{background:#fff;border:1px solid #dadce0;border-radius:6px;aspect-ratio:16/9;position:relative;overflow:hidden}
.badge{position:absolute;right:6px;top:6px;border-radius:999px;min-width:24px;height:24px;display:grid;place-items:center;font-weight:700;font-size:12px;padding:0 6px}
.q{background:#fff;border:1px solid #dadce0;border-radius:8px;padding:22px 24px;width:560px}
.opt{display:flex;gap:10px;align-items:center;padding:7px 0;font-size:13px}
.rad{width:16px;height:16px;border-radius:50%;border:2px solid #5f6368;flex:none}
.rad.on{border-color:var(--pc);box-shadow:inset 0 0 0 3px #fff;background:var(--pc)}
.ui{position:relative;background:#fff;border:1px solid #dadce0;border-radius:10px;overflow:hidden}
.ui *{position:absolute}
"""

FIGS = {}


def fig(name, product, width=1200):
    def deco(fn):
        FIGS[name] = (fn, width, product)
        return fn
    return deco


def css_vars(k):
    c, d, t, i = PC[k]
    return f"--pc:{c};--pcd:{d};--pct:{t};--pci:{i}"


def hero(product, title, card, scale=1.0, foot="svgslid.es/blog"):
    return (f'<div class="hero"><span class="lab">{LABEL[product]}</span><div class="ttl2">{title}</div>'
            f'<div class="cw"><div style="zoom:{scale}">{card}</div></div><div class="foot">{foot}</div></div>')


def win(kind, title, inner, menus=None, sub="svgslid.es example", gem=False, on=None):
    menus = menus or ["File", "Edit", "View", "Insert", "Format", "Tools", "Extensions", "Help"]
    return f'<div class="win" style="position:relative">{CI.chrome(title, kind, menus, on, gem, sub)}{inner}</div>'


def sheet(title, cols, widths, rows, tabs, on_tab, fx_ref="A1", fx="", side="", cur=None, sub="svgslid.es example", rowcls=None):
    g = CI.grid(cols, widths, rows, cur=cur)
    if rowcls:
        for i, c in rowcls.items():
            g = g.replace(f'<td class="rn">{i}</td>', f'<td class="rn {c}">{i}</td>', 1)
    t = "".join(f'<span class="{"on" if x == on_tab else ""}">{x}</span>' for x in tabs)
    return f"""<div class="win" style="position:relative">{CI.chrome(title, "g", CI.SMENUS, None, False, sub)}
<div class="fx"><span class="ref">{fx_ref}</span><i>fx</i><span class="f">{fx}</span></div>
<div style="display:flex"><div style="flex:1;overflow:hidden">{g}</div>{side}</div><div class="tabs">{t}</div></div>"""


def colorize(html, cells):
    """cells: list of (text, css) - wrap first <td> with exact text in a style."""
    for txt, style in cells:
        html = html.replace(f'<td class="">{txt}</td>', f'<td class="" style="{style}">{txt}</td>', 1)
    return html


def gside(prompt, answer, title="Gemini"):
    return f"""<div class="side"><div class="sh"><span class="star"></span>{title}<span class="x">&times;</span></div><div class="bd">
<div class="bub">{prompt}</div><div class="ans">{answer}</div></div><div class="ask">Ask Gemini<span class="sp"></span>&#x27A4;</div></div>"""


def mini_page(lines, w=230, h=300, accent="#1c1e22", over=None, font="Overpass"):
    """A small one-pager: dark hero band with headline, three columns below."""
    hl = lines[0]
    style = "color:#fff;font-family:%s,sans-serif;font-weight:800;font-size:17px;line-height:1.08" % font
    ov = ""
    if over:
        ov = f'<div style="position:absolute;left:10px;right:10px;top:34px;height:66px;border:3px solid #d93025;border-radius:6px"></div>'
    cols = "".join(f'<div style="position:absolute;left:{14 + i*70}px;top:150px;width:58px"><div style="width:18px;height:18px;border-radius:50%;background:{accent}"></div>'
                   f'<div style="margin-top:6px;font:700 9px Overpass,sans-serif;line-height:1.15">{lines[1+i] if len(lines) > 1+i else ""}</div>'
                   f'<div style="margin-top:4px;height:5px;background:#e3e5e8;border-radius:2px"></div><div style="margin-top:3px;height:5px;width:80%;background:#e3e5e8;border-radius:2px"></div></div>' for i in range(3))
    return (f'<div style="position:relative;width:{w}px;height:{h}px;background:#fff;box-shadow:0 1px 3px rgba(60,64,67,.3);overflow:hidden">'
            f'<div style="position:absolute;left:0;top:0;right:0;height:120px;background:#1c1e22"></div>'
            f'<div style="position:absolute;left:14px;top:14px;width:40px;height:6px;background:{accent}"></div>'
            f'<div style="position:absolute;left:14px;top:38px;width:{w-28}px;{style}">{hl}</div>{ov}{cols}'
            f'<div style="position:absolute;left:14px;bottom:16px;width:80px;height:18px;border-radius:9px;background:#0066ff"></div></div>')


# ================================================================ 1. localization (sheets)
LOC_COLS = ["Key", "English", "Budget", "German", "Budget", "Fits", "Japanese", "Budget", "Fits"]
LOC_W = [104, 200, 52, 230, 52, 78, 140, 52, 50]
LOC_ROWS = [
    ["headline", "Send large files without opening a ticket", 48, "Große Dateien senden, ohne ein IT-Ticket zu eröffnen", 44, "Over by 8", "チケット不要で大容量ファイルを送信", 22, "OK"],
    ["benefit_1_title", "SSO on every plan", 24, "SSO in jedem Tarif", 24, "OK", "全プランでSSO", 12, "OK"],
    ["benefit_2_title", "Links that expire", 24, "Links mit Ablaufdatum", 24, "OK", "期限付きリンク", 12, "OK"],
    ["benefit_3_title", "A full audit trail", 24, "Lückenloses Audit-Protokoll", 24, "Over by 3", "完全な監査ログ", 12, "OK"],
    ["cta", "Start a free trial", 22, "Kostenlos testen", 22, "OK", "無料で試す", 10, "OK"],
]


@fig("hero-loc", "sheets")
def hero_loc():
    pages = "".join(f'<div style="position:relative">{mini_page(l, over=o, font=f)}<div style="margin-top:8px;font:700 13px Overpass;color:#fff">{n}</div></div>'
                    for l, o, f, n in [(["Send large files without opening a ticket", "SSO on every plan", "Links that expire", "A full audit trail"], False, "Overpass", "en-US"),
                                       (["Große Dateien senden, ohne ein IT-Ticket zu eröffnen", "SSO in jedem Tarif", "Links mit Ablaufdatum", "Lückenloses Audit-Protokoll"], True, "Overpass", "de-DE &middot; over budget"),
                                       (["チケット不要で大容量ファイルを送信", "全プランでSSO", "期限付きリンク", "完全な監査ログ"], False, "sans-serif", "ja-JP")])
    card = f'<div style="display:flex;gap:22px;margin-top:40px">{pages}</div>'
    return hero("sheets", "Localize without breaking the layout", card, foot="One budget per slot, per language")


@fig("loc-sheet", "sheets")
def loc_sheet():
    s = sheet("Localization: One-pager", LOC_COLS, LOC_W, LOC_ROWS, ["Messages", "Glossary", "Fonts", "Approvals"], "Messages",
              "F2", '=IF(LEN(D2)&lt;=E2,"OK","Over by "&amp;(LEN(D2)-E2))', cur=(2, 5))
    return s


@fig("loc-expansion", "sheets")
def loc_exp():
    rows = [("English", "Send large files without opening a ticket", 41, 48), ("French", "Envoyez de gros fichiers sans ouvrir de ticket", 46, 50),
            ("German", "Große Dateien senden, ohne ein IT-Ticket zu eröffnen", 52, 44), ("Japanese", "チケット不要で大容量ファイルを送信", 17, 22)]
    out = []
    for lang, line, n, b in rows:
        over = n > b
        pct = min(100, n / max(b, n) * 100)
        out.append(f"""<div style="display:flex;gap:20px;align-items:center;margin-top:14px">
<div class="b" style="width:80px;font-weight:700;font-size:12px">{lang}</div>
<div style="width:430px;height:64px;background:#1c1e22;border-radius:6px;padding:10px 14px;color:#fff;font:800 19px Overpass,sans-serif;line-height:1.1;{'outline:3px solid #d93025' if over else ''}">{line}</div>
<div style="flex:1"><div style="height:14px;background:#eef0f2;border-radius:7px;position:relative;overflow:hidden"><div style="position:absolute;left:0;top:0;bottom:0;width:{pct}%;background:{'#d93025' if over else 'var(--pc)'}"></div></div>
<div class="b" style="font-size:11px;color:{'#b3261e' if over else '#5f6368'};margin-top:4px">{n} of {b} characters{' &middot; over by ' + str(n-b) if over else ''}</div></div></div>""")
    return f'<div class="dia"><div class="cap">One headline box, four languages</div>{"".join(out)}<div class="b" style="margin-top:18px;font-size:12px;color:#6b6f76">Budgets are measured per language in that language&rsquo;s font. Character counts are illustrative.</div></div>'


# ================================================================ 2. quiz (forms)
def quiz_q(title, opts, sel=0, num="3 of 10"):
    o = "".join(f'<div class="opt"><span class="rad {"on" if i == sel else ""}"></span>{t}</div>' for i, t in enumerate(opts))
    return f'<div class="q"><div style="display:flex;justify-content:space-between;font-size:12px;color:#5f6368"><span>Question {num}</span><span>1 point</span></div><div style="font-size:15px;margin:8px 0 10px">{title}</div>{o}</div>'


@fig("hero-quiz", "forms")
def hero_quiz():
    head = '<div style="background:#fff;border-top:10px solid var(--pc);border-radius:8px;padding:18px 24px;width:560px;margin-bottom:12px"><div style="font-size:24px">Messaging check: SSO launch</div><div style="font-size:12px;color:#5f6368;margin-top:4px">10 questions &middot; pass mark 8</div></div>'
    q = quiz_q("How do we describe SSO pricing on calls?", ["SSO on every plan.", "SSO is available on Team and Enterprise.", "SSO is a paid add-on for larger teams.", "Enterprise-grade SSO at no extra cost for qualifying plans."])
    card = f'<div style="background:var(--pct);padding:24px;border-radius:14px;width:610px">{head}{q}</div>'
    return hero("forms", "Certify reps on the new message", card, foot="Approved line right, retired lines wrong")


@fig("quiz-from-sheet", "forms")
def quiz_sheet():
    rows = [["benefit_1", "How do we describe SSO pricing?", "SSO on every plan.", "SSO is available on Team and Enterprise.", "SSO is a paid add-on."],
            ["headline", "Which headline leads the one-pager?", "Send large files without opening a ticket", "Secure file sharing for modern teams", "File transfer, reinvented"]]
    g = CI.grid(["Key", "Question", "Approved line", "Retired 1", "Retired 2"], [80, 190, 190, 190, 140], rows)
    g = g.replace('<td class="">SSO on every plan.</td>', '<td class="" style="background:var(--pct);font-weight:700">SSO on every plan.</td>', 1)
    q = quiz_q("How do we describe SSO pricing?", ["SSO is a paid add-on.", "SSO on every plan.", "SSO is available on Team and Enterprise."], sel=1, num="1 of 10")
    return f"""<div class="dia"><div class="cap">The Messages tab becomes the quiz</div>
<div style="display:flex;gap:26px;align-items:center;margin-top:18px"><div style="width:830px;border:1px solid #dee1e6;border-radius:8px;overflow:hidden">{g}</div></div>
<div style="font:700 22px Overpass;color:var(--pcd);margin:10px 0 0 380px">&darr;</div>
<div style="display:flex;gap:28px;margin-top:22px;align-items:center"><div style="transform:scale(.92);transform-origin:left top">{q}</div>
<div class="b" style="font-size:13px;line-height:1.6;width:420px"><b>Approved line</b> is the correct answer.<br><b>Retired lines</b> are the wrong ones: plausible, because the team used to say them.<br>Options are shuffled per question.</div></div></div>"""


@fig("quiz-results", "forms")
def quiz_results():
    rows = [["Dana R.", "dana@example.com", 10, "Pass"], ["Marco P.", "marco@example.com", 9, "Pass"], ["Lee K.", "lee@example.com", 6, "Follow up"],
            ["Sam T.", "sam@example.com", 8, "Pass"], ["Ari N.", "ari@example.com", 7, "Follow up"], ["Jo W.", "jo@example.com", 10, "Pass"]]
    s = sheet("Messaging check (Responses)", ["Name", "Email", "Score", "Status"], [160, 230, 80, 140], rows, ["Messages", "Form Responses 1", "By question"], "Form Responses 1", "D2", '=IF(C2&gt;=8,"Pass","Follow up")')
    s = s.replace('<td class="">Follow up</td>', '<td class="" style="background:var(--pct);color:var(--pcd);font-weight:700">Follow up</td>')
    return s


# ================================================================ 3. meet (meet)
def slide_img(n, title, body="", accent="#0066ff", w=300):
    return (f'<div class="thumb" style="width:{w}px"><div style="position:absolute;left:8%;top:12%;font:800 {w/14:.0f}px Overpass,sans-serif">{n} &middot; {title}</div>'
            f'<div style="position:absolute;left:8%;top:36%;width:40%;height:8%;background:#e3e5e8;border-radius:3px"></div>'
            f'<div style="position:absolute;left:8%;top:50%;width:52%;height:8%;background:#e3e5e8;border-radius:3px"></div>'
            f'<div style="position:absolute;right:8%;top:34%;width:28%;height:44%;background:{accent};border-radius:4px;opacity:.85"></div>{body}</div>')


def notes_doc(scale=1):
    return f"""<div class="doc"><div style="font-size:11px;color:#5f6368">Notes by Gemini</div><h3>Acme &middot; Relay demo &middot; Aug 11</h3>
<h4>Summary</h4><p>Walked through the deck; questions on pricing and SSO, then a short demo of expiring links.</p>
<h4>Details</h4><div style="margin:8px 0;border:1px solid #dadce0;border-radius:6px;padding:8px;display:inline-block">{slide_img(7, "Pricing", accent="var(--pc)", w=320)}<div style="font-size:10.5px;color:#5f6368;margin-top:4px">Screenshot of presented content</div></div>
<ul><li style="background:var(--pct);border-radius:3px"><b style="font-weight:500">Objection:</b> Dana thought SSO was an extra cost on the Team plan.</li>
<li>Asked whether links can expire after one download.</li><li style="background:var(--pct);border-radius:3px"><b style="font-weight:500">Objection:</b> wants a case study from a regulated industry.</li></ul></div>"""


@fig("hero-meet", "meet")
def hero_meet():
    card = f'<div style="background:#f0f4f9;padding:22px;border-radius:14px;width:650px">{notes_doc()}</div>'
    return hero("meet", "Find the slide that draws objections", f'<div style="zoom:.86;">{card}</div>', foot="Meet notes now capture the slide on screen")


@fig("meet-notes-doc", "meet")
def meet_doc():
    return win("d", "Acme · Relay demo · Notes by Gemini", f'<div style="background:#f0f4f9;padding:26px;margin-top:10px;border-top:1px solid #e3e5e8">{notes_doc()}</div>', sub="Meeting notes")


@fig("objection-tab", "meet")
def obj_tab():
    rows = [["Aug 11", "Acme", "7 · Pricing", "Thinks SSO costs extra on Team", "Price", "“So SSO is another line item?”"],
            ["Aug 11", "Acme", "9 · Customers", "Wants a regulated-industry case study", "Proof", "“Anyone like us using it?”"],
            ["Aug 12", "Northwind", "7 · Pricing", "Compares per-seat price with Box", "Competitor", ""],
            ["Aug 12", "Northwind", "4 · How it works", "Unclear who sets link expiry", "Fit", "“Is that the admin or the sender?”"],
            ["Aug 13", "Globex", "7 · Pricing", "Thinks SSO costs extra", "Price", ""]]
    s = sheet("Deck feedback: Relay sales deck", ["Date", "Deal", "Slide", "Objection", "Category", "Quote"], [70, 100, 130, 270, 90, 260], rows,
              ["Objections", "Summary", "Slides"], "Objections", "C2", "7 · Pricing")
    return s.replace('<td class="">7 · Pricing</td>', '<td class="" style="background:var(--pct);font-weight:700">7 · Pricing</td>')


@fig("objection-heatmap", "meet")
def heatmap():
    titles = ["Title", "Problem", "Why now", "How it works", "Demo", "Security", "Pricing", "Integrations", "Customers", "Competition", "Rollout", "Next steps"]
    counts = [0, 1, 0, 3, 1, 2, 9, 1, 4, 2, 0, 0]
    cells = []
    for i, (t, c) in enumerate(zip(titles, counts), start=1):
        a = min(1, c / 9)
        bg = f"rgba(0,137,123,{0.12 + a*0.88:.2f})" if c else "#fff"
        col = "#fff" if a > .45 else "#1c1e22"
        cells.append(f'<div class="thumb" style="width:240px;background:{bg}"><div style="position:absolute;left:12px;top:12px;font:800 15px Overpass,sans-serif;color:{col}">{i} &middot; {t}</div>'
                     f'<div class="badge" style="background:#fff;color:#00695c;border:1px solid #00897b">{c}</div></div>')
    return f'<div class="dia"><div class="cap">Objections per slide, ten calls</div><div style="display:grid;grid-template-columns:repeat(4,240px);gap:16px;margin-top:18px">{"".join(cells)}</div><div class="b" style="margin-top:14px;font-size:12px;color:#6b6f76">Illustrative counts. Darker = more objections logged while that slide was on screen.</div></div>'


# ================================================================ 4. proof (studio)
PROOF_COLS = ["Claim", "Customer", "Scope", "Approved by", "Source", "Expires", "Days left", "Used in"]
PROOF_W = [210, 90, 110, 110, 90, 82, 70, 160]
PROOF_ROWS = [["Cut file transfer tickets by 60%", "Acme", "Quote, web, print", "J. Ortiz, IT", "email", "2026-09-21", 12, "One-pager, Deck"],
              ["Logo", "Northwind", "Logo, web only", "Brand team", "form", "2027-03-01", 173, "Homepage"],
              ["Case study: rollout in 2 weeks", "Globex", "Case study", "M. Chen, CIO", "doc", "2026-11-30", 82, "Deck, Battlecard"],
              ["Logo", "Initech", "Logo, all", "Legal", "email", "", "No date", "One-pager"],
              ["“Our partners stopped emailing zip files.”", "Umbrella", "Quote, events", "R. Patel", "email", "2027-06-15", 279, "Event booth"]]


def proof_sheet(cur=None):
    s = sheet("Proof library", PROOF_COLS, PROOF_W, PROOF_ROWS, ["Proof", "Retired", "Scopes"], "Proof", "G2", '=IF(F2="","No date",F2-TODAY())', cur=cur)
    s = s.replace('<td class="">12</td>', '<td class="" style="background:#fbd5d0;color:#b3261e;font-weight:700">12</td>', 1)
    s = s.replace('<td class="">82</td>', '<td class="" style="background:#feefc3;color:#8a5a00;font-weight:700">82</td>', 1)
    s = s.replace('<td class="">No date</td>', '<td class="" style="background:var(--pct);color:var(--pcd);font-weight:700">No date</td>', 1)
    return s


@fig("hero-proof", "studio")
def hero_proof():
    return hero("studio", "Proof points expire. Track them.", f'<div style="zoom:.68;width:1120px">{proof_sheet()}</div>', foot="Scope, source and expiry for every logo and quote")


@fig("proof-columns", "studio")
def proof_cols():
    return proof_sheet(cur=(2, 6))


def flow(cards, title="Weekly proof check"):
    inner = '<div class="vline"></div>'.join(f'<div class="flowcard" style="{"border-color:var(--pc);border-width:2px" if i == 0 else ""}"><small>{a}</small><b>{b}</b><p>{c}</p></div>' for i, (a, b, c) in enumerate(cards))
    return f"""<div class="win" style="position:relative;width:640px"><div class="top"><div class="ico w"></div><div class="ttl">{title}<small>Workspace Studio &middot; Flow</small></div><div class="sp"></div><div class="share" style="background:var(--pc);color:var(--pci)">Turn on</div></div>
<div style="background:#f8f9fa;border-top:1px solid #e3e5e8;padding:24px;display:flex;flex-direction:column;align-items:center;margin-top:10px">{inner}</div></div>"""


@fig("proof-flow", "studio")
def proof_flow():
    f = flow([("Starter", "On a schedule", "Every Monday at 9:00"),
              ("Step &middot; Ask Gemini", "List proof points expiring within 30 days", "Source: Proof library. Return claim, customer, days left and Used in."),
              ("Step &middot; Notify me in Chat", "Post to #proof-owners", "Message: [Step 2: Gemini response]"),
              ("Step &middot; Move Drive file", "Move expired logo files to Retired", "Optional. New in September.")])
    return f'<div class="dia" style="display:flex;justify-content:center;background:var(--pct)">{f}</div>'


@fig("proof-on-asset", "studio")
def proof_asset():
    ring = '<div style="position:absolute;inset:-7px;border:3px solid #d93025;border-radius:12px"></div>'
    logos = "".join(f'<div style="width:150px;height:56px;border-radius:8px;background:#fff;border:1px solid #dadce0;display:grid;place-items:center;font:800 18px Overpass,sans-serif;color:#5f6368;position:relative">{n}'
                    f'{ring if n == "INITECH" else ""}</div>' for n in ["ACME", "NORTHWIND", "GLOBEX", "INITECH", "UMBRELLA"])
    return f"""<div class="dia"><div class="cap">Customer logo strip, one-pager</div>
<div style="margin-top:18px;background:#f4f5f7;border-radius:10px;padding:22px"><div class="h" style="font-size:16px;margin-bottom:14px">Trusted by teams at</div><div style="display:flex;gap:16px">{logos}</div></div>
<div style="display:flex;gap:30px;margin-top:18px;align-items:flex-start"><div class="note" style="position:static;display:inline-block">Initech: no expiry date on file. Check the approval before the next print run.</div>
<div class="b" style="font-size:12px;color:#6b6f76;line-height:1.6">Each logo is a native SVG shape with an alt text tag like <span class="mono">proof:initech-logo</span>, so every use can be found.</div></div></div>"""


# ================================================================ 5. skills (gemini)
SKILL_LINES = ["Start from the approved fact. Add no claims.", "Lead with what the customer can do. Active voice.",
               "6 to 9 words. Never over the budget.", "No superlatives, exclamation marks or em dashes.", "Return three options with character counts."]


@fig("hero-skills", "gemini")
def hero_skills():
    page = '<div class="doc" style="width:420px;padding:30px 34px"><div style="font-size:11px;color:#5f6368">Launch brief</div><h3>Relay: SSO on every plan</h3><p><b>Fact:</b> SSO is included on every plan. Customers sign in with their existing identity provider.</p><h4>Headline</h4><p style="background:var(--pct);padding:4px 6px;border-radius:4px">Sign in with the login your team already uses</p></div>'
    side = gside('<span class="chip">@Headline recipe</span> SSO is included on every plan. Customers sign in with their existing identity provider.',
                 '<div style="display:flex;gap:6px;align-items:center;margin-bottom:6px"><span class="star"></span><b style="font-weight:500">Using skill: Headline recipe</b></div>'
                 '<div class="ch"><em>40</em><span>Sign in with the login your team already uses</span></div><div class="ch"><em>33</em><span>Single sign-on on every Relay plan</span></div><div class="ch"><em>41</em><span>Your identity provider, on every plan we sell</span></div>')
    w = f'<div class="win" style="position:relative">{CI.chrome("Launch brief: SSO", "d", ["File","Edit","View","Insert","Format","Tools","Extensions","Help"], None, True, "Docs")}<div class="work" style="min-height:420px"><div class="stage">{page}</div>{side}</div></div>'
    return hero("gemini", "Your copy rules, as Gemini skills", f'<div style="zoom:.62;width:1180px">{w}</div>', foot="Call them with @ in Docs, Slides and Gmail")


@fig("skills-recipe-anatomy", "gemini", 1100)
def skills_anat():
    lines = "".join(f'<div style="display:flex;gap:10px;margin:6px 0"><span class="hlc" style="width:20px;height:20px;border-radius:50%;display:grid;place-items:center;font-size:11px;font-weight:700;flex:none">{i}</span><span>{t}</span></div>' for i, t in enumerate(SKILL_LINES, 1))
    card = f"""<div style="background:#fff;border:1px solid #dadce0;border-radius:14px;width:560px;padding:22px 24px;font-size:13px;line-height:1.5">
<div style="display:flex;align-items:center;gap:8px"><span class="star" style="background:var(--pc)"></span><b style="font-size:18px;font-weight:500">Headline recipe</b></div>
<div style="color:#5f6368;margin:6px 0 14px"><b style="font-weight:500;color:#1c1e22">When to use:</b> writing or rewriting a headline for a one-pager, brief, deck title or landing page.</div>
<div style="font-weight:500;margin-bottom:4px">Instructions</div>{lines}
<div style="margin-top:12px"><b style="font-weight:500">Banned:</b> <span class="pill" style="background:#f1f3f4">seamless</span> <span class="pill" style="background:#f1f3f4">unlock</span> <span class="pill" style="background:#f1f3f4">empower</span> <span class="pill" style="background:#f1f3f4">revolutionary</span></div>
<div style="margin-top:12px;display:flex;gap:8px;align-items:center"><div class="ico g" style="width:18px;height:22px"></div>Reference: <span class="chip">@Brand style sheet</span></div></div>"""
    notes = [("Name", "Short, findable with @"), ("When to use", "Lets Gemini pick the skill on its own"), ("Instructions", "The recipe: structure, length, voice"), ("Banned words", "What you never say"), ("Reference file", "Voice and Type tabs of the style sheet")]
    side = "".join(f'<div style="margin:0 0 16px"><div class="h" style="font-size:15px;color:var(--pcd)">{a}</div><div class="b" style="font-size:12px;color:#6b6f76">{b}</div></div>' for a, b in notes)
    return f'<div class="dia"><div class="cap">Anatomy of a copy skill</div><div style="display:flex;gap:40px;margin-top:18px;align-items:flex-start">{card}<div style="padding-top:10px">{side}</div></div></div>'


@fig("skills-three", "gemini")
def skills_three():
    cards = [("Headline recipe", "6 to 9 words from an approved fact. Three options with counts.", "Docs, Slides"),
             ("Proof line", "Turns a customer result into one line with the number first and the source named.", "Docs, Slides, Gmail"),
             ("Battlecard rewrite", "Rewrites a competitor claim as a talk track: acknowledge, reframe, prove.", "Docs, Chat")]
    c = "".join(f'<div class="box pcbox" style="width:330px;padding:18px"><h6 style="font-size:18px">@{a}</h6><p style="font-size:12px;margin-top:8px">{b}</p><div style="margin-top:12px;font:700 11px Overpass;letter-spacing:.08em;text-transform:uppercase;color:var(--pcd)">Used in: {d}</div></div>' for a, b, d in cards)
    return f'<div class="dia"><div class="cap">One job per skill</div><div style="display:flex;gap:22px;margin-top:18px">{c}</div></div>'


@fig("skills-migration", "gemini")
def skills_mig():
    pts = [("Sep 30", "Skills announced", "Google sets the timeline"), ("Oct 5", "Workspace rollout begins", "Docs, Slides, Gmail, Chat, Drive"),
           ("Oct 13", "Gemini app rollout", "Personal and Workspace accounts"), ("Later", "Gems phased out", "App Gems migrate to draft skills"),
           ("Then", "Ask a Gem steps stop", "Rebuild Studio flows with skills")]
    items = "".join(f'<div style="flex:1;position:relative;padding-top:34px"><div style="position:absolute;top:8px;left:0;width:18px;height:18px;border-radius:50%;background:{"var(--pc)" if i < 3 else "#9aa0a6"}"></div>'
                    f'<div class="h" style="font-size:15px;color:{"var(--pcd)" if i < 3 else "#5f6368"}">{d}</div><div class="h" style="font-size:16px;margin-top:2px">{a}</div><div class="b" style="font-size:11.5px;color:#6b6f76;margin-top:3px;padding-right:14px">{b}</div></div>'
                    for i, (d, a, b) in enumerate(pts))
    return f'<div class="dia"><div class="cap">From Gems to skills</div><div style="position:relative;margin-top:16px"><div style="position:absolute;left:9px;right:40px;top:16px;height:2px;background:#dadce0"></div><div style="display:flex">{items}</div></div><div class="b" style="margin-top:18px;font-size:12px;color:#6b6f76">Dates from Google&rsquo;s announcement and transition guide. Skills don&rsquo;t sync between the Gemini app and Workspace apps.</div></div>'


# ================================================================ 6. studio (studio)
def chat_msg():
    lines = [("benefit_1_title", "SSO on every plan", "One-pager, Battlecard"), ("stat_3_value", "All", "One-pager"), ("headline", "Send large files without opening a ticket", "One-pager, Solution brief")]
    l = "".join(f'<div class="ln"><span class="mono">{k}</span> &rarr; <b style="font-weight:500">{v}</b><div style="font-size:11.5px;color:#5f6368">Update: {u}</div></div>' for k, v, u in lines)
    return f"""<div class="chat"><div class="who"><div class="av" style="background:var(--pc);color:var(--pci)">WS</div><div><b>Messaging changes</b> <span style="color:#5f6368;font-size:11.5px">Flow &middot; 10:42</span></div></div>
<div>3 approved lines changed in the messaging sheet:</div>{l}<div style="font-size:11.5px;color:#5f6368;margin-top:6px">Summary by Gemini. Check each line against the sheet.</div></div>"""


@fig("hero-studio", "studio")
def hero_studio():
    f = flow([("Starter", "When a sheet changes", "Messaging (private mirror) &middot; column: Approved line"),
              ("Step &middot; Ask Gemini", "Summarise what changed", "Key, old and new line, and the assets in Used in"),
              ("Step &middot; Notify in Chat", "Post to #launch", "Message: [Step 2: Gemini response]")], title="Messaging changes")
    return hero("studio", "Studio flows need private files", f'<div style="zoom:.95;">{f}</div>', foot="Mirror the shared sheet, watch the private copy")


@fig("studio-two-zones", "studio")
def two_zones():
    return f"""<div class="dia"><div class="cap">Shared for people, private for the flow</div>
<div style="display:flex;gap:18px;align-items:center;margin-top:22px">
<div style="border:2px dashed #9aa0a6;border-radius:14px;padding:18px;width:330px"><div class="h" style="font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:#5f6368">Shared drive</div>
<div class="box" style="margin-top:12px"><h6>Messaging sheet</h6><p>The team writes and approves lines here. Shared with everyone who needs it.</p></div>
<div style="display:flex;gap:6px;margin-top:10px">{''.join(f'<div class="av" style="background:{c};width:26px;height:26px;font-size:10px">{n}</div>' for c, n in [("#0066ff","PM"),("#6b6f76","LG"),("#188038","PR"),("#7248b9","SE")])}</div></div>
<div style="flex:1;text-align:center"><div class="arr" style="min-width:120px"></div><div class="b" style="font-size:11px;color:#5f6368;margin-top:8px">Apps Script, every 15 min<br>values only, only when changed</div></div>
<div class="pcbox" style="border-radius:14px;padding:18px;width:300px"><div class="h" style="font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:var(--pcd)">My Drive, flow owner</div>
<div class="box" style="margin-top:12px"><h6>Private mirror</h6><p>Shared with nobody. No IMPORTRANGE. The only file the flow touches.</p></div></div>
<div class="arr" style="min-width:50px;flex:none;width:60px"></div>
<div style="width:250px">{''.join(f'<div class="flowcard" style="width:250px;margin-bottom:8px"><small>{a}</small><b>{b}</b></div>' for a, b in [("Starter","When a sheet changes"),("Step","Ask Gemini"),("Step","Notify in Chat")])}</div>
</div></div>"""


@fig("studio-chat-message", "studio", 1000)
def studio_chat():
    return f'<div class="dia" style="display:flex;justify-content:center;background:var(--pct)">{chat_msg()}</div>'


# ================================================================ 7. charts (sheets)
DATA = [("Relay", 92), ("Acme", 61), ("Northwind", 48), ("Globex", 35), ("Initech", 22)]


def native_bars(w=420, hl=0, grey=True, font="Verdana,'DejaVu Sans',sans-serif", sel=None):
    mx = max(v for _, v in DATA)
    rows = []
    for i, (n, v) in enumerate(DATA):
        c = "var(--pc)" if i == hl else ("#c4c7cc" if grey else "var(--pc)")
        s = ' outline:2px solid #0b57d0;outline-offset:2px' if sel == i else ""
        rows.append(f'<div style="display:flex;align-items:center;gap:10px;margin:6px 0"><div style="width:90px;text-align:right;font:13px {font}">{n}</div>'
                    f'<div style="height:22px;width:{v/mx*w:.0f}px;background:{c};{s}"></div><div style="font:700 13px {font}">{v}%</div></div>')
    return "".join(rows)


def default_chart():
    mx = max(v for _, v in DATA)
    bars = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:170px;width:56px"><div style="font:11px Arial;color:#444">{v}</div><div style="width:40px;height:{v/mx*140:.0f}px;background:{c}"></div><div style="font:11px Arial;color:#444;margin-top:4px">{n}</div></div>'
                   for (n, v), c in zip(DATA, ["#4285f4", "#ea4335", "#fbbc04", "#34a853", "#ff6d01"]))
    grid_ = "".join(f'<div style="position:absolute;left:0;right:0;top:{y}px;border-top:1px solid #e0e0e0"></div>' for y in (20, 55, 90, 125, 160))
    return f'<div style="background:#fff;border:1px solid #dadce0;padding:14px 18px;width:400px"><div style="font:15px Arial;color:#444;margin-bottom:6px">Tickets avoided (%)</div><div style="position:relative;display:flex;gap:16px;align-items:flex-end;padding:0 10px">{grid_}{bars}</div></div>'


def slide_frame(inner, w=560, title="Fewer tickets with Relay"):
    return f'<div class="sf" style="width:{w}px;height:{w*9/16:.0f}px"><div class="ab" style="left:28px;top:22px;font:800 22px Overpass,sans-serif">{title}</div><div class="ab" style="left:28px;top:70px">{inner}</div></div>'


@fig("hero-charts", "sheets")
def hero_charts():
    picker = ('<div class="menu" style="left:420px;top:150px;width:190px;padding:10px"><div style="font-size:12px;color:#5f6368;padding:0 0 6px">Fill color</div>'
              '<div style="display:grid;grid-template-columns:repeat(6,22px);gap:6px">' + "".join(f'<span style="width:22px;height:22px;border-radius:50%;background:{c};display:block;padding:0;{"outline:2px solid #1c1e22;outline-offset:2px" if c == "#188038" else ""}"></span>' for c in ["#1c1e22", "#6b6f76", "#c4c7cc", "#0066ff", "#188038", "#f9c80e", "#d93025", "#7248b9", "#00897b", "#e8710a", "#ffffff", "#fef4d6"]) + '</div></div>')
    st = f'<div style="position:relative">{slide_frame(native_bars(300, sel=0), 620)}{picker}</div>'
    w = CI.slides_win(st, title="Sales deck: Relay")
    return hero("sheets", "On-brand charts, as native shapes", f'<div style="zoom:.72;width:1060px">{w}</div>', foot="Every bar a shape, every label live text")


@fig("chart-default-vs-brand", "sheets")
def chart_cmp():
    return f"""<div class="dia"><div class="cap">Same data, two charts</div><div style="display:flex;gap:30px;margin-top:18px;align-items:flex-start">
<div><div class="b" style="font-size:12px;margin-bottom:8px"><b>Linked Sheets chart</b>: Sheets&rsquo; fonts, palette and gridlines</div>{slide_frame(default_chart(), 520)}</div>
<div><div class="b" style="font-size:12px;margin-bottom:8px"><b>Native shapes</b>: your type, one accent colour, one point</div>{slide_frame(native_bars(270), 520)}</div></div></div>"""


@fig("chart-pipeline", "sheets")
def chart_pipe():
    st = [("Sheets range", "Label and value columns. The numbers are final."), ("Chart tool", "Brand colours, flat fills. Export as SVG."),
          ("SVG to Slides", "Drag the file onto the Slides tab, Cmd/Ctrl+V."), ("On the slide", "Native shapes, plus labels as Slides text boxes.")]
    b = '<div class="arr"></div>'.join(f'<div class="box {"pcbox" if i == 2 else ""}" style="width:220px"><h6>{i+1}. {a}</h6><p>{c}</p></div>' for i, (a, c) in enumerate(st))
    return f'<div class="dia"><div class="cap">Lines, areas and donuts: data to SVG to shapes</div><div style="display:flex;align-items:center;gap:14px;margin-top:22px">{b}</div><div class="b" style="margin-top:16px;font-size:12px;color:#6b6f76">Bars skip the SVG step: a short Apps Script draws them as rectangles and text boxes.</div></div>'


@fig("chart-recolor", "sheets", 1000)
def chart_recolor():
    return f'<div class="dia"><div class="cap">Grey everything, colour the point</div><div style="display:flex;gap:30px;margin-top:18px">{slide_frame(native_bars(230, hl=-1), 430, "Before")}{slide_frame(native_bars(230, hl=0, sel=0), 430, "After: one click")}</div></div>'


# ================================================================ 8. matrix (sheets)
M_COLS = ["Competitor", "Capability", "Value", "Evidence", "Source", "Checked on", "Status"]
M_W = [100, 170, 70, 230, 170, 90, 90]
M_ROWS = [["Acme", "SSO on all plans", "No", "SSO listed under Enterprise only", "acme.example/pricing", "2026-10-28", "OK"],
          ["Acme", "Link expiry", "Yes", "Expiring links on every plan", "acme.example/docs/links", "2026-10-28", "OK"],
          ["Northwind", "SSO on all plans", "Partial", "SSO on Business and up", "northwind.example/plans", "2026-06-02", "Recheck"],
          ["Northwind", "Audit log export", "Unclear", "Docs mention logs; export not stated", "", "", "Not checked"],
          ["Globex", "SSO on all plans", "Yes", "SSO included on all tiers", "globex.example/pricing", "2026-10-27", "OK"]]


def matrix(cur=None, side=""):
    s = sheet("Competitive matrix", M_COLS, M_W, M_ROWS, ["Matrix", "By competitor", "Battlecard"], "Matrix", "G2",
              '=IF(F2="","Not checked",IF(TODAY()-F2&gt;90,"Recheck","OK"))', cur=cur, side=side)
    s = s.replace('<td class="">Recheck</td>', '<td class="" style="background:#feefc3;color:#8a5a00;font-weight:700">Recheck</td>')
    s = s.replace('<td class="">Not checked</td>', '<td class="" style="background:#fbd5d0;color:#b3261e;font-weight:700">Not checked</td>')
    s = s.replace('<td class="ok">OK</td>', '<td class="ok" style="background:var(--pct)">OK</td>')
    return s


@fig("hero-matrix", "sheets")
def hero_matrix():
    pop = """<div class="menu" style="left:300px;top:170px;width:330px;padding:12px 14px"><div style="display:flex;gap:6px;align-items:center;padding:0;font-weight:500"><span class="star"></span>Sources for C2</div>
<div style="display:block;padding:8px 0 0"><div style="font-size:12px;color:#0b57d0">acme.example/pricing</div><div style="font-size:11px;color:#5f6368">Pricing and plans</div></div>
<div style="display:block;padding:6px 0 0"><div style="font-size:12px;color:#0b57d0">acme.example/docs/sso</div><div style="font-size:11px;color:#5f6368">Configure single sign-on</div></div></div>"""
    w = f'<div style="position:relative">{matrix(cur=(2, 2))}{pop}</div>'
    return hero("sheets", "Every cell cites its source", f'<div style="zoom:.7;width:1100px">{w}</div>', foot="Fill with Gemini, now with cell-level citations")


@fig("matrix-layout", "sheets")
def matrix_layout():
    return matrix(cur=(4, 6))


@fig("matrix-to-battlecard", "sheets")
def matrix_card():
    rows = "".join(f'<div style="display:flex;gap:10px;margin:8px 0;font-size:13px"><span class="hlc" style="border-radius:4px;padding:0 6px;font-weight:700;height:20px">{i}</span><span>{t}</span></div>'
                   for i, t in [(1, "SSO is Enterprise-only at Acme. Ours is on every plan."), (2, "Both offer expiring links. Ours add a download limit.")])
    card = f"""<div class="sf" style="width:520px;height:340px"><div class="ab" style="left:0;top:0;right:0;height:64px;background:#1c1e22"></div>
<div class="ab" style="left:24px;top:18px;color:#fff;font:800 22px Overpass">Relay vs Acme</div>
<div class="ab" style="right:24px;top:20px;width:90px;height:26px;border-radius:6px;background:#fff;display:grid;place-items:center;font:800 13px Overpass;color:#5f6368">ACME</div>
<div class="ab" style="left:24px;top:84px;width:470px"><div class="h" style="font-size:15px">Where we win</div><div>{rows}</div></div>
<div class="ab" style="left:24px;bottom:18px;width:470px;font-size:10px;color:#6b6f76;line-height:1.5;border-top:1px solid #dadce0;padding-top:8px">1 acme.example/pricing, checked 2026-10-28 &nbsp; 2 acme.example/docs/links, checked 2026-10-28</div></div>"""
    g = CI.grid(["Competitor", "Capability", "Value", "Status"], [90, 150, 70, 70], [r[:3] + [r[6]] for r in M_ROWS[:2]])
    g = g.replace('<td class="ok">OK</td>', '<td class="ok" style="background:var(--pct)">OK</td>')
    return f'<div class="dia"><div class="cap">Only confirmed rows reach the card</div><div style="display:flex;gap:24px;align-items:center;margin-top:18px"><div style="width:420px;border:1px solid #dee1e6;border-radius:8px;overflow:hidden">{g}</div><div class="arr"></div>{card}</div></div>'


# ================================================================ 9. audit (slides)
def deck_mini(changed=False):
    hl = "Send large files without opening a ticket" if not changed else "Move big files without waiting on IT"
    return mini_page([hl, "SSO on every plan", "Links that expire", "A full audit trail"], 200, 260, accent="#f9c80e" if not changed else "#0066ff",
                     font="Overpass" if not changed else "Georgia")


AUDIT_ROWS = [[1, "g1a2_headline", "slot:headline", "Text", "Send large files without opening a ticket", "Move big files without waiting on IT"],
              [1, "g1a2_headline", "slot:headline", "Font", "Overpass", "Georgia"],
              [1, "g1a2_subhead", "slot:subhead", "Top", 272, 290],
              [2, "g2b7_quote", "slot:quote", "Deleted", "“Our partners stopped emailing zip files.”", ""],
              [2, "SLIDES_API_118", "", "New object", "", "Customer stories"]]


def audit_sheet():
    s = sheet("Deck audit", ["Slide", "Object ID", "Tag", "Change", "Before", "After"], [56, 130, 120, 90, 270, 260], AUDIT_ROWS,
              ["Audit", "Snap 11-03 101502", "Snap 11-03 102244", "Diff"], "Diff", "D2", "Text")
    for t in ("Deleted", "New object"):
        s = s.replace(f'<td class="">{t}</td>', f'<td class="" style="background:#fbd5d0;color:#b3261e;font-weight:700">{t}</td>')
    for t in ("Text", "Font", "Top"):
        s = s.replace(f'<td class="">{t}</td>', f'<td class="" style="background:var(--pct);color:var(--pcd);font-weight:700">{t}</td>')
    return s


@fig("hero-audit", "slides")
def hero_audit():
    pair = f'<div style="display:flex;gap:16px;align-items:center;margin-bottom:16px"><div>{deck_mini()}<div style="font:700 12px Overpass;margin-top:6px">Before</div></div><div class="arr" style="min-width:40px"></div><div>{deck_mini(True)}<div style="font:700 12px Overpass;margin-top:6px">After the prompt</div></div></div>'
    return hero("slides", "Audit what Gemini changed", f'<div><div style="zoom:.8">{pair}</div><div style="zoom:.6;width:1000px">{audit_sheet()}</div></div>', foot="Snapshot, edit, snapshot, diff")


@fig("audit-flow", "slides")
def audit_flow():
    st = [("Snapshot", "Every object on every slide, to a sheet tab"), ("Edit", "Run the prompt in the Gemini side panel"),
          ("Snapshot", "Same deck, new tab"), ("Diff", "Changed text, font, size, position; new and deleted objects")]
    b = '<div class="arr"></div>'.join(f'<div class="box {"pcbox" if i in (1,) else ""}" style="width:220px"><h6>{i+1}. {a}</h6><p>{c}</p></div>' for i, (a, c) in enumerate(st))
    return f'<div class="dia"><div class="cap">The audit loop</div><div style="display:flex;align-items:center;gap:14px;margin-top:22px">{b}</div></div>'


@fig("audit-diff-sheet", "slides")
def audit_diff():
    return audit_sheet()


# ================================================================ 10. UI mockups (slides)
def ui_mock(label="Share", scale=1.0, blurry=False, old=False):
    s = scale
    lab = "Export" if old else label
    blur = "filter:blur(1.1px);" if blurry else ""
    acc = "#0066ff" if old else "var(--pc)"
    ink = "#fff" if old else "var(--pci)"
    return f"""<div class="ui" style="width:{420*s}px;height:{270*s}px;{blur}">
<div style="left:0;top:0;right:0;height:{40*s}px;background:#f4f5f7;border-bottom:1px solid #dadce0"></div>
<div style="left:{14*s}px;top:{13*s}px;width:{70*s}px;height:{14*s}px;background:#c4c7cc;border-radius:3px"></div>
<div style="right:{14*s}px;top:{8*s}px;width:{92*s}px;height:{24*s}px;background:{acc};border-radius:{12*s}px;color:{ink};font:700 {12*s}px Verdana,'DejaVu Sans',sans-serif;display:grid;place-items:center">{lab}</div>
<div style="left:{14*s}px;top:{58*s}px;width:{120*s}px;bottom:{14*s}px;background:#f4f5f7;border-radius:6px"></div>
{''.join(f'<div style="left:{24*s}px;top:{(70+i*24)*s}px;width:{90*s}px;height:{10*s}px;background:#dadce0;border-radius:3px"></div>' for i in range(5))}
<div style="left:{150*s}px;top:{58*s}px;right:{14*s}px;height:{86*s}px;border:1px solid #dadce0;border-radius:8px"></div>
<div style="left:{164*s}px;top:{72*s}px;width:{34*s}px;height:{40*s}px;background:#dadce0;border-radius:4px"></div>
<div style="left:{210*s}px;top:{76*s}px;width:{140*s}px;height:{11*s}px;background:#c4c7cc;border-radius:3px"></div>
<div style="left:{210*s}px;top:{96*s}px;width:{90*s}px;height:{9*s}px;background:#dadce0;border-radius:3px"></div>
<div style="left:{150*s}px;top:{156*s}px;right:{14*s}px;height:{86*s}px;border:1px solid #dadce0;border-radius:8px"></div>
<div style="left:{164*s}px;top:{170*s}px;width:{34*s}px;height:{40*s}px;background:#dadce0;border-radius:4px"></div>
<div style="left:{210*s}px;top:{174*s}px;width:{120*s}px;height:{11*s}px;background:#c4c7cc;border-radius:3px"></div></div>"""


@fig("hero-ui", "slides")
def hero_ui():
    st = f'<div class="pg" style="width:620px;height:349px"><div style="left:30px;top:24px;font:800 22px Overpass,sans-serif">Share with partners in one click</div><div style="left:30px;top:66px">{ui_mock(scale=.98)}</div>' \
         f'<div style="left:340px;top:68px;width:100px;height:32px;outline:2px solid #0b57d0;outline-offset:2px"></div><div class="tag" style="left:330px;top:44px">ui:button-primary</div></div>'
    w = CI.slides_win(st, title="Sales deck: Relay", n=3)
    return hero("slides", "Native UI mockups don&rsquo;t go stale", f'<div style="zoom:.72;width:1060px">{w}</div>', foot="Shapes and live text, from one library deck")


@fig("ui-screenshot-vs-native", "slides")
def ui_cmp():
    return f"""<div class="dia"><div class="cap">Screenshot vs native mockup</div><div style="display:flex;gap:40px;margin-top:18px;align-items:flex-start">
<div><div class="b" style="font-size:12px;margin-bottom:8px"><b>Screenshot (PNG)</b>: old label, soft at print size, not searchable</div><div style="position:relative">{ui_mock(scale=1.2, blurry=True, old=True)}<div class="ring" style="right:6px;top:2px;width:128px;height:44px;border-color:#d93025!important"></div></div></div>
<div><div class="b" style="font-size:12px;margin-bottom:8px"><b>Native shapes + text box</b>: current label, sharp, recolourable</div><div style="position:relative">{ui_mock(scale=1.2)}<div class="ring" style="right:6px;top:2px;width:128px;height:44px"></div></div></div></div></div>"""


@fig("ui-library-deck", "slides")
def ui_lib():
    filmstrip = "".join(f'<div style="display:flex;gap:6px;font-size:11px;color:#444746"><span style="width:12px">{i}</span><span style="flex:1;background:#fff;border:1px solid {"#0b57d0" if i == 2 else "#c4c7c5"};{"outline:2px solid #0b57d0;" if i == 2 else ""}border-radius:3px;display:block;aspect-ratio:16/9;position:relative"></span></div>' for i in range(1, 8))
    stage = f"""<div class="pg" style="width:600px;height:338px"><div style="left:30px;top:24px;font:800 18px Overpass,sans-serif">Button, primary</div><div style="left:30px;top:52px;font:12px Verdana,'DejaVu Sans',sans-serif;color:#6b6f76">Updated Nov 10, 2026 &middot; matches app v4.2</div>
<div style="left:200px;top:140px;width:200px;height:52px;border-radius:26px;background:var(--pc);color:var(--pci);font:700 18px Verdana,'DejaVu Sans',sans-serif;display:grid;place-items:center">Share</div>
<div style="left:30px;top:300px;font:11px Verdana,'DejaVu Sans',sans-serif;color:#9aa0a6;background:#fff;outline:2px dashed var(--pcd);outline-offset:3px">ui:button-primary</div></div>"""
    find = '<div class="menu" style="right:24px;top:96px;width:280px;padding:10px 12px"><div style="padding:0;font-size:12px;color:#5f6368">Find</div><div class="fld f" style="margin-top:6px">ui:button<span style="color:#5f6368">2 of 14</span></div></div>'
    return f"""<div class="win" style="position:relative">{CI.chrome("UI library", "s", CI.MENUS, None, False, "Shared drive &rsaquo; Brand")}
<div class="work"><div class="film" style="width:130px">{filmstrip}</div><div class="stage">{stage}</div></div>{find}</div>"""


@fig("ui-rename-flow", "slides")
def ui_rename():
    dlg = """<div class="dlg" style="position:static;width:330px"><h4>Find and replace</h4><div class="b" style="font-size:12px;margin-bottom:4px">Find</div><div class="fld">Export</div>
<div class="b" style="font-size:12px;margin:10px 0 4px">Replace with</div><div class="fld f">Share</div>
<div style="margin-top:10px;font-size:12px;color:#5f6368">Replaced 9 occurrences on 3 slides</div><div class="btnrow" style="justify-content:flex-end;margin-top:14px"><span class="gbtn">Replace</span><span class="gbtn p">Replace all</span></div></div>"""
    minis = "".join(f'<div>{ui_mock(scale=.55)}<div class="b" style="font-size:11px;margin-top:4px;color:#6b6f76">Slide {n}</div></div>' for n in (4, 7, 11))
    return f'<div class="dia"><div class="cap">One rename, every mockup</div><div style="display:flex;gap:30px;margin-top:18px;align-items:center">{dlg}<div class="arr" style="min-width:40px;flex:none"></div><div style="display:flex;gap:16px">{minis}</div></div></div>'


# ================================================================ 11. Apps Script part 1
@fig("hero-appscript-1", "appsscript")
def hero_appscript():
    import gtm_appscript as G
    css = "".join(f".hc .{k}{{color:{v}}}" for k, v in G.DARK.items() if k not in ("bg", "tx"))
    code = G.code_html("decks", "hc")
    card = (f'<style>{css}.hc{{background:#1C1E22;color:#E6E6E6;border-radius:16px;padding:46px 26px 24px;font:14px/1.6 "Roboto Mono",monospace;white-space:pre;position:relative;margin:0}}'
            f'.dots{{position:absolute;left:22px;top:18px;display:flex;gap:8px}}.dots i{{width:11px;height:11px;border-radius:50%;display:block}}</style>'
            f'<div style="position:relative"><div class="dots" style="z-index:2"><i style="background:#FF5F57"></i><i style="background:#FEBC2E"></i><i style="background:#28C840"></i></div>{code}</div>')
    return hero("appsscript", "Apps Script for GTM, part 1", f'<div style="zoom:.95">{card}</div>', foot="Five scripts to run this week")


# ================================================================ render
def main(only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    css = CI.CSS + EXTRA
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for name, (fn, width, product) in FIGS.items():
            if only and name not in only:
                continue
            body = fn()
            hero_ = name.startswith("hero-")
            pg = br.new_page(viewport={"width": 1200 if hero_ else width, "height": 630 if hero_ else 800}, device_scale_factor=2)
            pad = "padding:0" if hero_ else ""
            pg.set_content(f'<html><head><meta charset="utf-8"><style>{css}</style></head><body style="{css_vars(product)}"><div id="f" style="{pad}">{body}</div></body></html>')
            pg.wait_for_timeout(200)
            if hero_:
                pg.locator(".hero").screenshot(path=str(OUT / f"{name}.png"))
                og = "og-" + name[5:]
                Image.open(OUT / f"{name}.png").resize((1200, 630), Image.LANCZOS).save(OUT / f"{og}.png", optimize=True)
            else:
                pg.locator("#f").screenshot(path=str(OUT / f"{name}.png"))
            pg.close()
            print(name)
        br.close()


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
