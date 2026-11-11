#!/usr/bin/env python3
"""Render the Apps Script for GTM part 1 cheat sheet (2-page US Letter PDF) and a cover thumbnail.

Usage: python3 tools/gtm_cheatsheet.py
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gtm_appscript as G  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "cloud" / "static" / "blog" / "files"
IMG = ROOT / "cloud" / "static" / "blog" / "img"
PDF = FILES / "apps-script-for-gtm-part-1-cheat-sheet.pdf"
POST = "svgslid.es/blog/apps-script-for-gtm-part-1"

CSS = """
@page{size:Letter;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Verdana,'DejaVu Sans',sans-serif;color:#1c1e22;font-size:8pt;line-height:1.38}
.pg{width:8.5in;height:11in;padding:.4in .5in .4in;position:relative;page-break-after:always;overflow:hidden}
.pg:last-child{page-break-after:auto}
h1{font-family:Overpass,sans-serif;font-weight:800;font-size:26pt;letter-spacing:-.02em;line-height:1}
h2{font-family:Overpass,sans-serif;font-weight:800;font-size:11.5pt;margin:0 0 3pt;letter-spacing:-.01em}
.eb{font-family:Overpass,sans-serif;font-weight:800;font-size:7.5pt;letter-spacing:.14em;text-transform:uppercase;color:#1a73e8}
.bar{width:28pt;height:4pt;background:#1a73e8;margin-bottom:6pt}
.sub{color:#6b6f76;font-size:9.5pt;margin:5pt 0 10pt}
.grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:7pt 12pt}
.card{border:1px solid #dadce0;border-radius:8pt;padding:7pt 10pt}
.card.full{grid-column:1/-1}
ul{padding-left:11pt}li{margin:1.5pt 0}
ol{padding-left:13pt}
pre.code{background:#1C1E22;color:#E6E6E6;border-radius:6pt;padding:7pt 9pt;font:6.2pt/1.25 'Roboto Mono',monospace;white-space:pre;margin-top:5pt;overflow:hidden}
.kw{color:#C792EA}.st{color:#C3E88D}.nu{color:#F78C6C}.fn{color:#82AAFF}.cl{color:#FFCB6B}.pr{color:#89DDFF}.cm{color:#7F848E;font-style:italic}
code.i{font-family:'Roboto Mono',monospace;font-size:7.8pt;background:#f1f3f4;border-radius:3pt;padding:0 3pt}
.num{display:inline-grid;place-items:center;width:13pt;height:13pt;border-radius:50%;background:#1a73e8;color:#fff;font:800 7pt Overpass,sans-serif;margin-right:4pt;vertical-align:1pt}
.foot{position:absolute;left:.5in;right:.5in;bottom:.28in;display:flex;justify-content:space-between;color:#6b6f76;font-size:7pt;border-top:1px solid #dadce0;padding-top:5pt}
.next{background:#1c1e22;color:#fff;border-radius:8pt;padding:11pt 13pt}
.next h2{color:#fff}.next .eb{color:#f9c80e}.next li{color:#e6e6e6}
.recap td{padding:2.5pt 5pt;border-bottom:1px solid #eef0f2;vertical-align:top}.recap td:first-child{font-family:'Roboto Mono',monospace;color:#1a73e8;font-weight:700;white-space:nowrap}
"""


def sp(n, title, key, notes):
    li = "".join(f"<li>{x}</li>" for x in notes)
    return f'<div class="card"><div class="eb">Superpower {n}</div><h2>{title}</h2><ul>{li}</ul>{G.code_html(key)}</div>'


def wide(eb, title, notes, key):
    li = "".join(f"<li>{x}</li>" for x in notes)
    return (f'<div class="card full"><div class="eb">{eb}</div><h2>{title}</h2><div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.75fr);gap:12pt;align-items:start">'
            f'<ul>{li}</ul>{G.code_html(key)}</div></div>')


def page1():
    steps = "".join(f'<div style="margin:2.5pt 0"><span class="num">{i}</span>{s}</div>' for i, s in enumerate([
        "Open a sheet. <b>Extensions › Apps Script</b>.", "Paste the code. <b>Save</b>.",
        "Pick a function in the toolbar dropdown. <b>Run</b>.", "First run: read the permission screen, then allow.",
        "Reload the sheet. Your menu appears next to Help."], 1))
    return f"""<div class="pg">
<div class="bar"></div><div class="eb">Cheat sheet &middot; Part 1</div>
<h1 style="margin-top:4pt">Apps Script for GTM</h1>
<div class="sub">Five scripts a product marketer can run this week. JavaScript that runs inside Google Workspace: Sheets, Slides, Docs, Gmail, Drive, Calendar, Forms.</div>
<div class="grid">
<div class="card"><div class="eb">Where it lives</div><h2>Bound vs standalone</h2><ul>
<li><b>Bound:</b> attached to one file. Extensions › Apps Script. Can add menus and react to edits. Start here.</li>
<li><b>Standalone:</b> script.google.com. For jobs across many files.</li></ul></div>
<div class="card"><div class="eb">Run it</div><h2>Save, run, allow, reload</h2>{steps}</div>
{wide("First script", "A GTM menu in your sheet", ["<code class='i'>onOpen</code> runs every time the sheet opens.", "Each item calls a function by name.", "Reload the sheet to see the menu."], "menu")}
{sp(1, "A formula that checks copy length", "fits", ["Use in a cell: <code class='i'>=FITS(D2, E2)</code>. Catch overflow before it hits a slide."])}
<div class="card"><div class="eb">Debug</div><h2>Test small, read the log</h2><ul><li>Run a tiny test function from the editor.</li><li><code class="i">console.log</code> output shows in the execution log.</li><li>View › Executions lists every run.</li></ul></div>
<div class="card"><div class="eb">Before you share it</div><h2>Safety checklist</h2><ul>{SAFETY()}</ul></div>
<div class="card"><div class="eb">Recap</div><h2>Five superpowers</h2><table class="recap" style="border-collapse:collapse;width:100%">{RECAP()}</table></div>
</div>
<div class="foot"><span>Apps Script for GTM &middot; Part 1 &middot; {POST}</span><span>1 / 2</span></div></div>"""


def RECAP():
    return "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in next(s for s in G.SLIDES if s["kind"] == "recap")["items"])


def SAFETY():
    return "".join(f"<li>{b}</li>" for b in next(s for s in G.SLIDES if s.get("eyebrow") == "Before you share it")["bullets"])


def page2():
    nxt = "".join(f"<li>{b}</li>" for b in next(s for s in G.SLIDES if s["kind"] == "next")["bullets"])
    safety = "".join(f"<li>{b}</li>" for b in next(s for s in G.SLIDES if s.get("eyebrow") == "Before you share it")["bullets"])
    return f"""<div class="pg">
<div class="grid">
{wide("Superpower 2", "One deck per account, from a template", ["Template slides hold tokens like <code class='i'>{{Company}}</code>.", "Sheet headers match the tokens.", "One run copies the template per row and fills it in."], "decks")}
{wide("Superpower 4", "Run it every Monday", ["Run <code class='i'>installWeekly</code> once. It schedules the digest.", "The digest emails you proof points close to expiry.", "Triggers run as you, sheet closed or not."], "weekly")}
{wide("Superpower 3", "Follow-ups as drafts, not sends", ["Rows marked Ready become Gmail drafts.", "Nothing is sent. A person reads each one."], "drafts")}
{wide("Superpower 5", "Stamp every messaging change", ["<code class='i'>onEdit</code> is a simple trigger. No setup.", "Sort by column I to see what changed."], "stamp")}
<div class="card full next"><div class="eb">Coming in part 2</div><h2>Talk to everything else</h2><ul style="columns:2;column-gap:18pt">{nxt}</ul>
<div style="margin-top:6pt;font-size:6.8pt;color:#9aa0a6">Reference: developers.google.com/apps-script &middot; Quotas: developers.google.com/apps-script/guides/services/quotas &middot; 2 / 2</div></div>
</div></div>"""


def main():
    FILES.mkdir(parents=True, exist_ok=True)
    doc = f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{page1()}{page2()}</body></html>'
    (Path("/tmp") / "cheat.html").write_text(doc)
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = br.new_page()
        pg.set_content(doc)
        pg.wait_for_timeout(300)
        pg.pdf(path=str(PDF), format="Letter", print_background=True, prefer_css_page_size=True)
        shot = br.new_page(viewport={"width": 816, "height": 1056}, device_scale_factor=2)
        shot.set_content(doc)
        shot.wait_for_timeout(300)
        shot.locator(".pg").nth(0).screenshot(path=str(IMG / "cheat-appscript-1.png"))
        shot.locator(".pg").nth(1).screenshot(path="/tmp/cheat-p2.png")
        br.close()
    print(PDF, PDF.stat().st_size)


if __name__ == "__main__":
    main()
