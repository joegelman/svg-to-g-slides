#!/usr/bin/env python3
"""Render the mocked screens for /blog/google-slides-collateral-messaging-sheet-gemini.

Every figure is an HTML mockup drawn here and screenshotted with headless Chrome
(playwright). They are illustrations, not captures of Google's UI.

Usage: python3 tools/collateral_images.py   (needs playwright + Chrome, Overpass + Roboto fonts)
Outputs PNGs into cloud/static/blog/img/.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cloud" / "static" / "blog" / "img"

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Roboto,Arial,sans-serif;font-size:13px;color:#1c1e22;background:#f6f7f9}
#f{padding:36px;background:#f6f7f9}
.h{font-family:Overpass,sans-serif;font-weight:800}
.b{font-family:Verdana,'DejaVu Sans',sans-serif}
.win{background:#fff;border:1px solid #dee1e6;border-radius:14px;overflow:hidden;box-shadow:0 14px 40px rgba(20,24,40,.13)}
.top{display:flex;align-items:center;gap:10px;padding:10px 14px 4px}
.ico{width:26px;height:32px;border-radius:5px;flex:none;position:relative}
.ico.s{background:#f9c80e}.ico.g{background:#2fa565}
.ico:after{content:"";position:absolute;left:6px;right:6px;top:9px;bottom:9px;border:2px solid #fff;border-radius:2px}
.ttl{font-size:17px;color:#1c1e22}.ttl small{display:block;font-size:11px;color:#6b6f76;margin-top:1px}
.sp{flex:1}
.share{background:#c2e7ff;border-radius:20px;padding:8px 20px;font-weight:500;color:#04315c}
.av{width:30px;height:30px;border-radius:50%;background:#1c1e22;color:#fff;display:grid;place-items:center;font-weight:500;font-size:12px}
.menus{display:flex;gap:16px;padding:0 14px 8px 50px;color:#3c4043;font-size:13px}
.menus b{background:#e8eaed;border-radius:4px;padding:1px 6px;margin:-1px -6px;font-weight:400}
.tb{display:flex;align-items:center;gap:9px;background:#edf2fa;margin:0 12px;border-radius:22px;padding:7px 16px;color:#444746;font-size:13px}
.tb i{width:15px;height:15px;border-radius:3px;background:#444746;opacity:.55;display:block}
.tb i.r{border-radius:50%}.tb u{width:1px;height:18px;background:#c4c7c5}
.tb .pill{border:1px solid #c4c7c5;border-radius:4px;padding:2px 8px;background:#fff}
.tb .gem{margin-left:auto;display:flex;align-items:center;gap:6px;background:#fff;border:1px solid #c4c7c5;border-radius:16px;padding:3px 12px;font-weight:500;color:#1c1e22}
.tb .gem.on{background:#d3e3fd;border-color:#a8c7fa}
.star{width:14px;height:14px;background:#0066ff;clip-path:polygon(50% 0,62% 38%,100% 50%,62% 62%,50% 100%,38% 62%,0 50%,38% 38%)}
.work{display:flex;background:#f0f4f9;margin-top:10px;border-top:1px solid #e3e5e8}
.film{width:118px;padding:14px 10px;display:flex;flex-direction:column;gap:12px;flex:none}
.film div{display:flex;gap:6px;font-size:11px;color:#444746}
.film span{flex:1;background:#fff;border:1px solid #c4c7c5;border-radius:3px;display:block}
.film .cur span{outline:2px solid #0b57d0;border-color:#0b57d0}
.stage{flex:1;display:grid;place-items:center;padding:26px;position:relative}
.side{width:340px;background:#fff;border-left:1px solid #e3e5e8;flex:none;display:flex;flex-direction:column}
.side .sh{display:flex;align-items:center;gap:8px;padding:14px 16px;font-size:16px;font-weight:500;border-bottom:1px solid #eef0f2}
.side .sh .x{margin-left:auto;color:#6b6f76;font-size:18px}
.side .bd{padding:14px 16px;display:flex;flex-direction:column;gap:12px;flex:1}
.bub{background:#e9eef6;border-radius:16px 16px 4px 16px;padding:10px 12px;font-size:12.5px;line-height:1.5;margin-left:28px}
.chip{display:inline-block;background:#d3e3fd;color:#0842a0;border-radius:6px;padding:0 6px;font-weight:500}
.ans{font-size:12.5px;line-height:1.5;color:#1c1e22}
.ans h5{font-size:12px;font-weight:500;color:#6b6f76;margin:8px 0 4px}
.ch{display:flex;gap:8px;padding:6px 0;border-bottom:1px solid #eef0f2;font-size:12px}
.ch em{font-style:normal;color:#6b6f76;flex:none;width:52px}
.ch s{color:#9aa0a6}.ch b{font-weight:500}
.ask{margin:0 16px 16px;border:1px solid #c4c7c5;border-radius:22px;padding:10px 14px;color:#6b6f76;display:flex}
.btnrow{display:flex;gap:8px}.gbtn{border:1px solid #c4c7c5;border-radius:16px;padding:5px 14px;font-weight:500;color:#0b57d0}
.gbtn.p{background:#0b57d0;color:#fff;border-color:#0b57d0}
/* page */
.pg{background:#fff;box-shadow:0 1px 3px rgba(60,64,67,.3);position:relative;overflow:hidden}
.pg *{position:absolute}
.pg .flow,.pg .flow *{position:static}
.sel{outline:2px solid #0b57d0;outline-offset:2px}
.sel:before,.sel:after{content:"";position:absolute;width:7px;height:7px;background:#fff;border:1.5px solid #0b57d0;top:-6px}
.sel:before{left:-6px}.sel:after{right:-6px}
.tag{font-family:'Roboto Mono',monospace;font-size:10px;background:#f9c80e;color:#1c1e22;border-radius:4px;padding:1px 5px;white-space:nowrap;z-index:5}
/* dialogs + menus */
.scrim{position:absolute;inset:0;background:rgba(32,33,36,.38)}
.dlg{position:absolute;background:#fff;border-radius:12px;box-shadow:0 12px 40px rgba(0,0,0,.3);padding:22px 24px;width:330px}
.dlg h4{font-size:19px;font-weight:400;margin-bottom:16px}
.fld{border:1px solid #747775;border-radius:4px;padding:8px 10px;font-size:13px;display:flex;justify-content:space-between}
.fld.f{border:2px solid #0b57d0;padding:7px 9px}
.menu{position:absolute;background:#fff;border-radius:6px;box-shadow:0 4px 14px rgba(0,0,0,.25);padding:6px 0;width:250px;font-size:13px;z-index:9}
.menu div{padding:6px 16px;display:flex;justify-content:space-between;color:#1c1e22}
.menu div.on{background:#e8eaed}.menu hr{border:0;border-top:1px solid #e3e5e8;margin:5px 0}
.menu small{color:#6b6f76}
.ring{position:absolute;border:4px solid #ffc700;border-radius:12px;z-index:20}
.note{position:absolute;background:#0066ff;color:#fff;font-family:Overpass,sans-serif;font-weight:700;font-size:13px;border-radius:14px;padding:3px 12px;z-index:21;white-space:nowrap}
/* sheets */
.fx{display:flex;align-items:center;gap:10px;border-top:1px solid #e3e5e8;border-bottom:1px solid #e3e5e8;margin-top:8px;padding:6px 12px;font-size:12.5px}
.fx .ref{width:56px;border-right:1px solid #e3e5e8;color:#444746}.fx .f{font-family:'Roboto Mono',monospace;font-size:11.5px}
.fx i{font-family:serif;color:#9aa0a6}
table.g{border-collapse:collapse;width:100%;font-size:12px;table-layout:fixed}
table.g th{background:#f8f9fa;border:1px solid #e1e3e6;color:#5f6368;font-weight:400;height:22px;font-size:11px}
table.g td{border:1px solid #e1e3e6;padding:5px 7px;vertical-align:top;line-height:1.4;height:26px;overflow:hidden}
table.g tr.hd td{background:#f4f5f7;font-weight:700}
table.g td.rn{background:#f8f9fa;color:#5f6368;text-align:center;font-size:11px;padding:5px 0}
table.g td.cur{outline:2px solid #0b57d0;outline-offset:-1px}
.ok{color:#188038;font-weight:500}.over{background:#fbd5d0;color:#b3261e;font-weight:500}
.tabs{display:flex;gap:2px;background:#f8f9fa;border-top:1px solid #e3e5e8;padding:0 12px;font-size:12.5px;color:#444746}
.tabs span{padding:8px 14px}.tabs .on{background:#e1ecfb;color:#0b57d0;font-weight:500}
.cb{width:14px;height:14px;border-radius:2px;background:#0b57d0;display:inline-grid;place-items:center;color:#fff;font-size:10px}
/* diagrams */
.dia{background:#fff;border:1px solid #dee1e6;border-radius:14px;padding:34px;position:relative}
.cap{font-family:Overpass,sans-serif;font-weight:800;letter-spacing:.12em;font-size:12px;text-transform:uppercase;color:#0066ff}
.box{border:1.5px solid #1c1e22;border-radius:10px;padding:12px 14px;background:#fff}
.box h6{font-family:Overpass,sans-serif;font-weight:800;font-size:15px}
.box p{font-family:Verdana,'DejaVu Sans',sans-serif;font-size:11px;color:#6b6f76;line-height:1.45;margin-top:3px}
.arr{height:2px;background:#1c1e22;position:relative;flex:1;min-width:26px}
.arr:after{content:"";position:absolute;right:-1px;top:-5px;border-left:9px solid #1c1e22;border-top:6px solid transparent;border-bottom:6px solid transparent}
"""

MENUS = ["File", "Edit", "View", "Insert", "Format", "Slide", "Arrange", "Tools", "Extensions", "Help"]
SMENUS = ["File", "Edit", "View", "Insert", "Format", "Data", "Tools", "Extensions", "Help"]


def chrome(title, kind, menus, on=None, gem=False, sub="Collateral starter pack"):
    m = "".join(f"<span>{'<b>'+x+'</b>' if x == on else x}</span>" for x in menus)
    return f"""<div class="top"><div class="ico {kind}"></div><div class="ttl">{title}<small>{sub}</small></div><div class="sp"></div>
<div class="share">Share</div><div class="av">JG</div></div><div class="menus">{m}</div>
<div class="tb"><i></i><i></i><i class="r"></i><u></u><span class="pill">100%</span><u></u><i></i><i class="r"></i><i></i><i></i><u></u>
<span>Overpass</span><u></u><span class="pill">30</span><u></u><b>B</b><i style="background:none;font-style:italic;opacity:1">I</i><i></i><i></i>
<span class="gem {'on' if gem else ''}"><span class="star"></span>Ask Gemini</span></div>"""


def onepager(s=0.5, headline="Send large files without opening a ticket", b1="SSO on every plan", sel=None, tags=False, spill=False, bleed=False):
    """Mini one-pager. s = px per pt / 72... here px per 1/100 in."""
    W, H = 850 * s, 1100 * s
    def t(key, x, y, w, h, txt, fs, col="#1c1e22", cls="h", extra=""):
        c = " sel" if sel == key else ""
        tg = f'<span class="tag" style="left:{x*s}px;top:{(y-0.2)*s*100/100 - 13}px">slot:{key}</span>' if tags else ""
        return (f'{tg}<div class="{cls}{c}" style="left:{x*s}px;top:{y*s}px;width:{w*s}px;height:{h*s}px;font-size:{fs*s*1.39:.1f}px;'
                f'color:{col};line-height:1.12;{extra}">{txt}</div>')
    o = [f'<div style="left:0;top:0;width:{W}px;height:{355*s}px;background:#1c1e22"></div>',
         f'<div style="left:{60*s}px;top:{55*s}px;width:{150*s}px;height:{45*s}px;border:1px dashed #9aa0a6;background:#2b2e34"></div>',
         t("eyebrow", 60, 130, 730, 30, "Secure file transfer", 11, "#f9c80e"),
         t("headline", 60, 162, 730, 105, headline, 30, "#fff", "h", "overflow:visible;" if spill else ""),
         t("subhead", 60, 272, 660, 62, "Relay moves files of any size between teams and partners, with access controls your security team sets once.", 11.5, "#fff", "b", "line-height:1.3;" + ("top:%spx;" % (272 * s) if not spill else ""))]
    for i, (a, b) in enumerate([(b1, "Sign in with the identity provider you already use. No add-on fee."),
                                ("Links that expire", "Set an expiry date and a download limit on every transfer."),
                                ("A full audit trail", "See who sent, opened and downloaded each file.")]):
        x = 60 + i * 250
        o.append(f'<div style="left:{x*s}px;top:{405*s}px;width:{42*s}px;height:{42*s}px;border-radius:50%;background:#f9c80e"></div>')
        o.append(t(f"benefit_{i+1}_title", x, 462, 220, 32, a, 14))
        o.append(t(f"benefit_{i+1}_body", x, 498, 220, 95, b, 10, "#6b6f76", "b", "line-height:1.35;"))
    o.append(f'<div style="left:{60*s}px;top:{630*s}px;width:{730*s}px;height:{145*s}px;background:#f4f5f7"></div>')
    for i, (v, l) in enumerate([("10 GB", "per transfer"), ("5 min", "to set up a workspace"), ("All", "plans include SSO")]):
        x = 90 + i * 240
        o.append(t(f"stat_{i+1}_value", x, 652, 210, 60, v, 30, "#0066ff"))
        o.append(t(f"stat_{i+1}_label", x, 720, 210, 30, l, 10, "#6b6f76", "b"))
    o.append(f'<div style="left:{60*s}px;top:{805*s}px;width:{730*s}px;height:{145*s}px;border:1px dashed #9aa0a6;background:#f4f5f7"></div>')
    o.append(f'<div style="left:{60*s}px;top:{985*s}px;width:{230*s}px;height:{50*s}px;border-radius:{25*s}px;background:#0066ff"></div>')
    o.append(t("cta", 60, 1001, 230, 30, "Start a free trial", 12, "#fff", "h", "text-align:center;"))
    o.append(t("cta_url", 310, 1001, 300, 30, "example.com/relay", 11, "#1c1e22", "b"))
    return f'<div class="pg" style="width:{W}px;height:{H}px">{"".join(o)}</div>'


def film(n=1, sel=1, ar="8.5/11"):
    return '<div class="film">' + "".join(
        f'<div class="{"cur" if i == sel else ""}">{i}<span style="aspect-ratio:{ar}"></span></div>' for i in range(1, n + 1)) + "</div>"


def gemini_panel(done=True):
    summary = """<div class="ans"><div style="display:flex;gap:6px;align-items:center;margin-bottom:6px"><span class="star"></span><b style="font-weight:500">Updated 4 text boxes on 1 slide</b></div>
<h5>Summary of changes</h5>
<div class="ch"><em>Benefit 1</em><span><s>SSO on Team and up</s><br><b>SSO on every plan</b></span></div>
<div class="ch"><em>Body</em><span><s>Available on Team and Enterprise.</s><br><b>Sign in with the identity provider you already use. No add-on fee.</b></span></div>
<div class="ch"><em>Stat 3</em><span><s>2 of 3</s> &rarr; <b>All</b></span></div>
<div class="ch"><em>Label</em><span><s>plans include SSO*</s> &rarr; <b>plans include SSO</b></span></div>
<div class="btnrow" style="margin-top:12px"><span class="gbtn">Undo</span><span class="gbtn">Version history</span></div></div>""" if done else ""
    return f"""<div class="side"><div class="sh"><span class="star"></span>Gemini<span class="x">&times;</span></div><div class="bd">
<div class="bub">Update this presentation from the Approved line column of <span class="chip">@01 Messaging sheet</span>. Use the approved wording exactly. Keep every layout, font, colour and image as it is. Do not add or delete pages.</div>
{summary}</div><div class="ask">Ask Gemini<span class="sp"></span>&#x27A4;</div></div>"""


def slides_win(stage, side="", n=1, on=None, gem=False, title="One-pager (Letter)", extra=""):
    return f"""<div class="win" style="position:relative">{chrome(title, "s", MENUS, on, gem)}
<div class="work">{film(n)}<div class="stage">{stage}</div>{side}</div>{extra}</div>"""


def sheet_win(grid, tabs, on_tab, fx_ref, fx, side="", menu_on=None, extra="", title="01 Messaging sheet", menus=SMENUS):
    t = "".join(f'<span class="{"on" if x == on_tab else ""}">{x}</span>' for x in tabs)
    return f"""<div class="win" style="position:relative">{chrome(title, "g", menus, menu_on)}
<div class="fx"><span class="ref">{fx_ref}</span><i>fx</i><span class="f">{fx}</span></div>
<div style="display:flex"><div style="flex:1;overflow:hidden">{grid}</div>{side}</div><div class="tabs">{t}</div>{extra}</div>"""


def grid(cols, widths, rows, cur=None, hl=None):
    cg = '<col style="width:34px">' + "".join(f'<col style="width:{w}px">' for w in widths)
    hd = "<tr><th></th>" + "".join(f"<th>{chr(65+i)}</th>" for i in range(len(cols))) + "</tr>"
    out = [f'<tr class="hd"><td class="rn">1</td>' + "".join(f'<td style="background:#f9c80e">{c}</td>' if j == hl else f"<td>{c}</td>" for j, c in enumerate(cols)) + "</tr>"]
    for i, r in enumerate(rows, start=2):
        tds = []
        for j, c in enumerate(r):
            cls = []
            if isinstance(c, str) and c.startswith("Over by"): cls.append("over")
            if c == "OK": cls.append("ok")
            if cur == (i, j): cls.append("cur")
            tds.append(f'<td class="{" ".join(cls)}">{c}</td>')
        out.append(f'<tr><td class="rn">{i}</td>{"".join(tds)}</tr>')
    return f'<table class="g"><colgroup>{cg}</colgroup>{hd}{"".join(out)}</table>'


TABS = ["Messages", "Voice", "Assets", "Data", "Sizes", "Approvals"]
MSG_COLS = ["Key", "Fact", "Draft", "Approved line", "Budget", "Length", "Fits", "Used in"]
MSG_W = [118, 210, 210, 230, 58, 58, 78, 150]
MSG_ROWS = [
    ["eyebrow", "Category we sell in: secure file transfer.", "Secure file transfer", "Secure file transfer", 28, 20, "OK", "One-pager, Solution brief"],
    ["headline", "People can send large files without asking IT for help.", "Send large files without opening a ticket", "Send large files without opening a ticket", 48, 41, "OK", "One-pager, Solution brief"],
    ["subhead", "Relay moves files between teams and partners. Security controls are admin-managed.", "Relay moves files of any size between teams and partners, with access controls your security team sets once.", "Relay moves files of any size between teams and partners, with access controls your security team sets once.", 120, 108, "OK", "One-pager, Solution brief"],
    ["benefit_1_title", "SSO is included on every plan.", "Single sign-on, included on every plan", "SSO on every plan", 24, 17, "OK", "One-pager, Battlecard"],
    ["benefit_1_body", "Customers sign in with their existing identity provider. No extra fee for SSO.", "Sign in with the identity provider you already use. No add-on fee.", "Sign in with the identity provider you already use. No add-on fee.", 80, 66, "OK", "One-pager"],
    ["benefit_2_title", "Transfer links can expire.", "Links that expire when you say so", "Links that expire when you say so", 24, 33, "Over by 9", "One-pager, Battlecard"],
    ["stat_3_value", "Plans that include SSO.", "All", "All", 8, 3, "OK", "One-pager"],
]

FIGS = {}


def fig(name, width=1200):
    def deco(fn):
        FIGS[name] = (fn, width)
        return fn
    return deco


@fig("hero-collateral-gemini")
def hero():
    stage = onepager(0.47, sel="benefit_1_title")
    return slides_win(stage, gemini_panel(), gem=True)


@fig("gemini-side-panel-update")
def gem():
    stage = onepager(0.56, sel="benefit_1_title")
    ring = '<div class="note" style="right:356px;top:196px">1. Prompt, with the sheet referenced &rarr;</div>' \
           '<div class="note" style="right:356px;top:330px">2. Read the change summary &rarr;</div>'
    return slides_win(stage, gemini_panel(), gem=True, extra=ring)


@fig("flow-sheet-to-assets")
def flow():
    assets = "".join(f'<div class="box" style="width:230px"><h6>{a}</h6><p>{b}</p></div>' for a, b in [
        ("One-pager", "Letter, 1 page"), ("Solution brief", "Letter, 2 pages"), ("Whitepaper", "Letter, cover + inside + back"),
        ("Battlecard", "Letter landscape"), ("Sales deck", "16:9")])
    return f"""<div class="dia"><div class="cap">One source, many assets</div>
<div style="display:flex;align-items:center;gap:18px;margin-top:22px">
<div class="box" style="width:215px;background:#f4f5f7"><h6>1. Plain fact</h6><p>&ldquo;SSO is included on every plan.&rdquo; One row per message.</p></div><div class="arr"></div>
<div class="box" style="width:215px"><h6>2. Draft</h6><p>=AI() in the sheet, or written by hand. Checked against a character budget.</p></div><div class="arr"></div>
<div class="box" style="width:215px;border-color:#0066ff;border-width:2.5px"><h6 style="color:#0066ff">3. Approved line</h6><p>Signed off once, in the sheet. The only column that reaches an asset.</p></div><div class="arr"></div>
<div style="display:flex;flex-direction:column;gap:8px"><div class="cap" style="color:#1c1e22">4. Update</div>
<div class="box" style="width:230px;background:#fff6d6;border-color:#f9c80e"><h6>Gemini prompt</h6><p>One asset at a time, no code.</p></div>
<div class="box" style="width:230px;background:#fff6d6;border-color:#f9c80e"><h6>Script or agent</h6><p>Every asset, exact wording, by slot.</p></div></div><div class="arr"></div>
<div style="display:flex;flex-direction:column;gap:8px">{assets}</div></div>
<div class="b" style="margin-top:22px;font-size:12px;color:#6b6f76">Data takes a separate route: tables and charts are linked from the sheet and refreshed with Tools &rsaquo; Linked objects &rsaquo; Update all.</div></div>"""


@fig("page-setup-custom", 1100)
def pagesetup():
    stage = '<div class="pg" style="width:560px;height:315px"></div>'
    dlg = """<div class="scrim"></div><div class="dlg" style="left:50%;top:150px;margin-left:-165px"><h4>Page setup</h4>
<div class="fld f"><span>Custom</span><span>&#9662;</span></div>
<div style="display:flex;gap:8px;align-items:center;margin-top:12px"><div class="fld" style="width:64px">8.5</div>&times;<div class="fld" style="width:64px">11</div>
<div class="fld" style="flex:1"><span>Inches</span><span>&#9662;</span></div></div>
<div class="btnrow" style="justify-content:flex-end;margin-top:22px"><span class="gbtn">Cancel</span><span class="gbtn p">Apply</span></div></div>
<div class="note" style="left:50%;top:372px;margin-left:-250px">File &rsaquo; Page setup &rsaquo; Custom. Units: inches, centimetres, points or pixels.</div>"""
    return slides_win(stage, on="File", title="Untitled presentation", extra=dlg)


@fig("bleed-trim-safe", 1100)
def bleed():
    s = 0.5
    b = 12.5 * s
    return f"""<div class="dia" style="display:flex;gap:44px;align-items:center"><div style="position:relative;width:{875*s}px;height:{1125*s}px;flex:none;background:#1c1e22;overflow:hidden">
<div style="position:absolute;left:0;top:{367*s}px;width:100%;bottom:0;background:#fff"></div>
<div style="position:absolute;left:{b}px;top:{b}px;width:{850*s}px;height:{1100*s}px;border:2px dashed #e24034"></div>
<div style="position:absolute;left:{b+25*s}px;top:{b+25*s}px;width:{800*s}px;height:{1050*s}px;border:2px dashed #0066ff"></div>
<div class="h" style="position:absolute;left:{72*s}px;top:{170*s}px;color:#fff;font-size:21px;line-height:1.1;width:300px">Send large files without opening a ticket</div></div>
<div style="flex:1"><div class="cap">Print one-pager, US Letter</div>
<div class="h" style="font-size:26px;margin:8px 0 18px">Canvas 8.75 &times; 11.25 in</div>
<div style="display:flex;flex-direction:column;gap:14px" class="b">
<div style="display:flex;gap:12px"><span style="width:34px;border-top:3px solid #1c1e22;margin-top:8px;flex:none"></span><div><b>Bleed: 0.125 in per side.</b><br><span style="color:#6b6f76">Colour blocks and images run to the canvas edge. This strip is cut off.</span></div></div>
<div style="display:flex;gap:12px"><span style="width:34px;border-top:3px dashed #e24034;margin-top:8px;flex:none"></span><div><b>Trim: 8.5 &times; 11 in.</b><br><span style="color:#6b6f76">The finished page. Draw it as a guide, delete it before export.</span></div></div>
<div style="display:flex;gap:12px"><span style="width:34px;border-top:3px dashed #0066ff;margin-top:8px;flex:none"></span><div><b>Safe margin: 0.25 in inside the trim.</b><br><span style="color:#6b6f76">Text and logos stay inside this line.</span></div></div>
</div><div class="b" style="margin-top:20px;font-size:12px;color:#6b6f76">Slides has no bleed setting. You make the page bigger and draw the guides yourself. Ask your printer for their bleed; 0.125 in (3 mm) is common.</div></div></div>"""


@fig("asset-sizes")
def sizes():
    s = 22
    items = [("One-pager", "8.5 &times; 11 in", 8.5, 11), ("Solution brief", "8.5 &times; 11 in, 2 pages", 8.5, 11), ("Whitepaper", "8.5 &times; 11 in, 4+ pages", 8.5, 11),
             ("A4 one-pager", "21 &times; 29.7 cm", 8.27, 11.69), ("Battlecard", "11 &times; 8.5 in", 11, 8.5), ("Sales deck", "10 &times; 5.625 in (16:9)", 10, 5.625)]
    cells = "".join(f"""<div style="display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:10px">
<div style="width:{w*s*0.62}px;height:{h*s*0.62}px;background:#fff;border:1.5px solid #1c1e22;position:relative">
<div style="position:absolute;left:0;top:0;right:0;height:30%;background:{'#1c1e22' if i%2==0 else '#f9c80e'}"></div></div>
<div style="text-align:center"><div class="h" style="font-size:14px">{n}</div><div class="b" style="font-size:11px;color:#6b6f76">{d}</div></div></div>""" for i, (n, d, w, h) in enumerate(items))
    return f'<div class="dia"><div class="cap">Page sizes to scale</div><div style="display:flex;gap:26px;align-items:flex-end;justify-content:space-between;margin-top:20px">{cells}</div></div>'


@fig("layout-patterns")
def patterns():
    def wire(title, sub, blocks, w=156, h=202):
        bl = "".join(f'<div style="position:absolute;left:{x}%;top:{y}%;width:{bw}%;height:{bh}%;background:{c};{e}"></div>' for x, y, bw, bh, c, e in blocks)
        return f"""<div style="display:flex;flex-direction:column;gap:10px;align-items:center"><div style="position:relative;width:{w}px;height:{h}px;background:#fff;border:1.5px solid #1c1e22">{bl}</div>
<div style="text-align:center;max-width:166px"><div class="h" style="font-size:14px">{title}</div><div class="b" style="font-size:11px;color:#6b6f76;line-height:1.4">{sub}</div></div></div>"""
    K, T, Y, B, G = "#1c1e22", "#f4f5f7", "#f9c80e", "#0066ff", "#c9cdd3"
    line = lambda x, y, w, c=G, h=2.2: (x, y, w, h, c, "")
    ws = [
        wire("Hero block", "Dark band, eyebrow, headline, subhead. Top third of page one.", [(0, 0, 100, 32, K, ""), line(7, 12, 30, Y), line(7, 17, 70, "#fff", 5), line(7, 25, 55, "#8d9199"), line(7, 42, 86), line(7, 47, 80), line(7, 52, 60)]),
        wire("Three up", "Icon, short title, two lines of body. Benefits or steps.", [(7, 10, 10, 8, Y, "border-radius:50%"), (38, 10, 10, 8, Y, "border-radius:50%"), (69, 10, 10, 8, Y, "border-radius:50%")] + [line(x, y, w, c) for x in (7, 38, 69) for y, w, c in ((22, 22, K), (27, 24, G), (31, 20, G))]),
        wire("Proof strip", "Tinted band with big numbers and small labels.", [(7, 30, 86, 26, T, ""), (12, 36, 16, 8, B, ""), (40, 36, 16, 8, B, ""), (68, 36, 16, 8, B, ""), line(12, 48, 20), line(40, 48, 20), line(68, 48, 20)]),
        wire("Problem / answer", "Two equal cards. Light for the problem, dark for the answer.", [(7, 20, 41, 44, T, ""), (52, 20, 41, 44, K, ""), line(11, 26, 20, K), line(11, 33, 32), line(11, 38, 30), line(56, 26, 20, Y), line(56, 33, 32, "#8d9199"), line(56, 38, 30, "#8d9199")]),
        wire("Two columns + pull line", "Running text in fixed boxes, one line pulled out.", [line(7, 10, 50, K, 4)] + [line(x, y, 38) for x in (7, 55) for y in range(20, 46, 5)] + [(7, 52, 86, 18, T, ""), line(12, 59, 60, B, 4)]),
        wire("Closing strip", "Button, URL, legal line. Same place on every asset.", [(7, 78, 30, 7, B, "border-radius:20px"), line(42, 80.5, 26, K), line(7, 92, 70)]),
    ]
    return f'<div class="dia"><div class="cap">Six blocks that cover most collateral</div><div style="display:flex;justify-content:space-between;gap:14px;margin-top:22px">{"".join(ws)}</div></div>'


@fig("messaging-sheet")
def msheet():
    g = grid(MSG_COLS, MSG_W, MSG_ROWS, cur=(5, 2), hl=3)
    extra = ''
    return sheet_win(g, TABS, "Messages", "C5",
                     '=AI("Write one line of product marketing copy from this fact. Plain, specific, active voice. No superlatives.", B5)', extra=extra)


@fig("linked-objects-update")
def linked():
    tbl = """<div class="pg" style="width:470px;height:360px"><div class="h" style="left:26px;top:22px;font-size:18px">Capabilities by plan</div>
<div class="sel" style="left:26px;top:60px;width:418px;height:186px"><table class="g flow" style="font-size:11px"><tr class="hd"><td>Capability</td><td>Starter</td><td>Team</td><td>Enterprise</td></tr>
<tr><td>Transfer size limit</td><td>2 GB</td><td>10 GB</td><td>10 GB</td></tr><tr><td>Single sign-on</td><td>Included</td><td>Included</td><td>Included</td></tr>
<tr><td>Link expiry</td><td>Included</td><td>Included</td><td>Included</td></tr><tr><td>Audit log export</td><td>Not included</td><td>Included</td><td>Included</td></tr></table></div>
<div style="left:360px;top:36px;background:#fff;border:1px solid #c4c7c5;border-radius:4px;padding:3px 10px;font-size:11px;color:#0b57d0;font-weight:500;box-shadow:0 1px 3px rgba(0,0,0,.2)">&#8635; Update</div></div>"""
    side = """<div class="side"><div class="sh">Linked objects<span class="x">&times;</span></div><div class="bd">
<div style="border:1px solid #e3e5e8;border-radius:8px;padding:10px 12px"><b style="font-weight:500">Table</b> &middot; Slide 2<div style="color:#6b6f76;font-size:12px;margin:3px 0 8px">01 Messaging sheet &rsaquo; Data!A1:D6</div><span class="gbtn">Update</span></div>
<div style="border:1px solid #e3e5e8;border-radius:8px;padding:10px 12px"><b style="font-weight:500">Chart</b> &middot; Slide 2<div style="color:#6b6f76;font-size:12px;margin:3px 0 8px">01 Messaging sheet &rsaquo; Data</div><span style="color:#188038;font-size:12px">Up to date</span></div>
<div class="sp" style="flex:1"></div><span class="gbtn p" style="text-align:center">Update all</span></div></div>"""
    return slides_win(tbl, side, n=2, on="Tools", title="Solution brief (Letter, 2 pages)")


@fig("slot-alt-text")
def slot():
    stage = onepager(0.56, sel="headline", tags=False)
    side = """<div class="side"><div class="sh">Alt text<span class="x">&times;</span></div><div class="bd">
<div style="font-size:12px;color:#6b6f76">Advanced options</div><div style="font-size:12px">Title</div>
<div class="fld f" style="font-family:'Roboto Mono',monospace">slot:headline</div>
<div style="font-size:12px;margin-top:6px">Description</div><div class="fld" style="height:70px;color:#9aa0a6">Leave empty for text boxes</div>
<div style="font-size:12px;color:#6b6f76;line-height:1.5;margin-top:8px">The key after <b>slot:</b> matches the Key column on the Messages tab. A script or an agent finds the box by this name.</div></div></div>"""
    extra = '<div class="note" style="left:600px;top:176px">Right-click &rsaquo; Alt text</div>'
    return slides_win(stage, side, extra=extra)


@fig("sync-menu-assets")
def sync():
    rows = [["One-pager (Letter)", "docs.google.com/presentation/d/1fei&hellip;", '<span class="cb">&#10003;</span>', "2026-11-09 19:40", 4, "None"],
            ["Solution brief", "docs.google.com/presentation/d/1E4R&hellip;", '<span class="cb">&#10003;</span>', "2026-11-09 19:40", 1, "None"],
            ["Whitepaper", "docs.google.com/presentation/d/1-2c&hellip;", '<span class="cb">&#10003;</span>', "2026-11-09 19:40", 0, "None"],
            ["Battlecard", "docs.google.com/presentation/d/14sT&hellip;", '<span class="cb">&#10003;</span>', "2026-11-09 19:40", 1, "Page 1: benefit_2_title is 9 over budget, skipped"]]
    g = grid(["Asset", "Deck URL", "Sync?", "Last synced", "Slots changed", "Flags"], [190, 270, 60, 140, 100, 350], rows)
    menu = '<div class="menu" style="left:598px;top:76px"><div>Dry run (report only)</div><div class="on">Sync copy to assets</div></div>'
    return sheet_win(g, TABS, "Assets", "A1", "Asset", menu_on="Collateral", extra=menu, menus=SMENUS + ["Collateral"])


@fig("approvals-sidebar")
def approvals():
    g = grid(MSG_COLS[:5], [118, 200, 200, 230, 58], [r[:5] for r in MSG_ROWS[:6]])
    side = """<div class="side"><div class="sh">Approvals<span class="x">&times;</span></div><div class="bd">
<div style="background:#fff6d6;border-radius:8px;padding:10px 12px"><b style="font-weight:500">Pending approval</b><div style="font-size:12px;color:#6b6f76;margin-top:2px">Due Nov 12, 2026 &middot; File locked</div></div>
<div style="display:flex;gap:10px;align-items:center"><div class="av" style="background:#0066ff">PM</div><div><b style="font-weight:500">Product marketing lead</b><div style="font-size:12px;color:#188038">Approved</div></div></div>
<div style="display:flex;gap:10px;align-items:center"><div class="av" style="background:#6b6f76">LG</div><div><b style="font-weight:500">Legal</b><div style="font-size:12px;color:#6b6f76">Awaiting review</div></div></div>
<div style="font-size:12px;color:#6b6f76;line-height:1.5;border-top:1px solid #eef0f2;padding-top:10px">&ldquo;SSO moved to every plan. Rows changed: benefit_1_title, benefit_1_body, stat_3_value, win_1.&rdquo;</div>
<div class="sp" style="flex:1"></div><div class="btnrow"><span class="gbtn p">Approve</span><span class="gbtn">Reject</span></div></div></div>"""
    return sheet_win(g, TABS, "Messages", "D5", "SSO on every plan", side=side, menu_on="File")


@fig("layout-shift-before-after")
def shift():
    a = onepager(0.42)
    b = onepager(0.42, headline="Send files of any size to anyone, inside or outside your company, without opening a ticket", spill=True)
    return f"""<div class="dia"><div class="cap">Layout shift: the same box, a longer line</div><div style="display:flex;gap:40px;margin-top:20px;align-items:flex-start;justify-content:center">
<div><div class="b" style="margin-bottom:10px"><b>41 characters.</b> Budget 48. Fits.</div><div style="border:1px solid #dee1e6">{a}</div></div>
<div style="position:relative"><div class="b" style="margin-bottom:10px;color:#b3261e"><b>88 characters.</b> Budget 48. Spills into the subhead.</div><div style="border:1px solid #dee1e6">{b}</div>
<div class="ring" style="left:14px;top:92px;width:330px;height:86px;border-color:#e24034"></div></div>
<div class="b" style="width:300px;font-size:13px;line-height:1.6"><b>Slides does not shrink text to fit.</b><br><br>Give every slot a character budget in the sheet.<br><br>Skip a line that is over budget. Do not squeeze it in.<br><br>After every update, look at each changed page.</div></div></div>"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for name, (fn, width) in FIGS.items():
            pg = br.new_page(viewport={"width": width, "height": 800}, device_scale_factor=2)
            pg.set_content(f"<html><head><style>{CSS}</style></head><body><div id=\"f\">{fn()}</div></body></html>")
            pg.wait_for_timeout(150)
            if name.startswith("hero"):
                pg.set_viewport_size({"width": 1200, "height": 630})
                pg.screenshot(path=str(OUT / f"{name}.png"))
                from PIL import Image
                Image.open(OUT / f"{name}.png").resize((1200, 630), Image.LANCZOS).save(OUT / "og-collateral-gemini.png", optimize=True)
            else:
                pg.locator("#f").screenshot(path=str(OUT / f"{name}.png"))
            pg.close()
            print(name)
        br.close()


if __name__ == "__main__":
    main()
