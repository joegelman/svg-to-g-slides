#!/usr/bin/env python3
"""Figures for /blog/messaging-workshop-brand-style-sheet-google-sheets (part 2 of the collateral series).

Reuses the mock chrome from collateral_images.py. Screens are mockups; the one-pager
figure is a render of the real SVG to Slides template (blog/img/src/svgs-one-pager.png).
Usage: python3 tools/collateral2_images.py
"""
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright
import collateral_images as ci

OUT = ci.OUT
SRC = OUT / "src"
FIGS = {}

CSS2 = """
.lvl{display:grid;grid-template-columns:118px 1fr;gap:14px;align-items:stretch;padding:12px 0;border-top:1px dashed #c9cdd3}
.lvl:first-of-type{border-top:0}
.lvl>b{font-family:Overpass,sans-serif;font-weight:800;font-size:13px;color:#6b6f76;align-self:center}
.cells{display:flex;gap:10px}
.cell{flex:1;border:1.5px solid #1c1e22;border-radius:8px;padding:9px 11px;background:#fff}
.cell h6{font-family:Overpass,sans-serif;font-weight:800;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#0066ff;margin-bottom:3px}
.cell p{font-family:Verdana,'DejaVu Sans',sans-serif;font-size:11px;line-height:1.4;color:#1c1e22}
.cell.pri{background:#fff6d6;border-color:#f9c80e}.cell.pri p{font-family:Overpass,sans-serif;font-weight:800;font-size:19px}
.form{background:#eef1f6;border-radius:14px;padding:26px 0;border:1px solid #dee1e6}
.fcard{background:#fff;border:1px solid #dadce0;border-radius:8px;width:640px;margin:0 auto 12px;padding:20px 24px;position:relative}
.fcard.t{border-top:9px solid #0066ff}.fcard h3{font-size:25px;font-weight:400;margin-bottom:6px}
.fcard .q{font-size:14.5px;margin-bottom:12px}.fcard .a{border-bottom:1px solid #dadce0;color:#1c1e22;font-size:13px;padding:4px 0 6px;line-height:1.5}
.fcard .a.e{color:#9aa0a6}.sec{background:#0066ff;color:#fff;border-radius:8px 8px 0 0;width:640px;margin:0 auto;padding:8px 24px;font-size:13px}
.radio{display:flex;align-items:center;gap:10px;font-size:13.5px;padding:5px 0}.radio i{width:16px;height:16px;border:2px solid #5f6368;border-radius:50%;display:block}
.radio.on i{border-color:#0066ff;box-shadow:inset 0 0 0 3px #fff;background:#0066ff}
.prog{width:640px;margin:14px auto 0;display:flex;align-items:center;gap:14px;font-size:12px;color:#5f6368}
.prog .bar{flex:1;height:8px;border-radius:4px;background:#d5d9e0;position:relative;overflow:hidden}.prog .bar:after{content:"";position:absolute;left:0;top:0;bottom:0;width:72%;background:#0066ff}
.sw{display:inline-block;width:100%;height:16px;border-radius:3px;border:1px solid #e1e3e6}
pre.blk{font-family:'Roboto Mono',monospace;font-size:11px;line-height:1.55;background:#1c1e22;color:#e8eaed;border-radius:10px;padding:16px 18px;white-space:pre-wrap}
pre.blk b{color:#f9c80e;font-weight:500}

.gemc{border:1.5px solid #1c1e22;border-radius:10px;padding:12px 14px;background:#fff;flex:1}
.gemc h6{font-family:Overpass,sans-serif;font-weight:800;font-size:15px;display:flex;gap:7px;align-items:center}
.gemc p{font-family:Verdana,'DejaVu Sans',sans-serif;font-size:11px;color:#6b6f76;line-height:1.45;margin-top:4px}
"""


def fig(name, width=1200):
    def deco(fn):
        FIGS[name] = (fn, width)
        return fn
    return deco


ARCH = [
    ("Primary", [("Lead message", "Editable SVGs in Google Slides.", "pri")]),
    ("Level 2", [("Context", "Product marketing runs on decks and documents. Where there should be crisp icons and logos there are crunchy PNGs.", ""),
                 ("Problem", "Google Slides doesn&rsquo;t support SVG files. Your options are to flatten them into PNGs or take the long way round.", ""),
                 ("Promise", "Every SVG path becomes a shape that behaves like one drawn in Slides.", "")]),
    ("Level 3<br>How", [("Drag", "Drag an .svg file onto an open Google Slides tab.", ""), ("Place", "Click where you want it.", ""), ("Paste", "Press Cmd/Ctrl+V. It lands as native shapes.", "")]),
    ("Level 4<br>Benefits", [("True vectors", "Native to Google Workspace.", ""), ("Import once", "Reuse the shape in themes, Docs and Drawings.", ""),
                             ("Build more", "Animate elements, make templates and letterheads.", ""), ("Proof", "5.0 rating. No Google permissions.", "")]),
    ("Level 5<br>Secondary", [("Add-on", "Also a Google Slides add-on.", ""), ("Converter", "SVGs to a PPTX in Drive.", ""), ("Batch", "Up to 25 files per drop.", ""), ("Price", "Free. No sign-up.", "")]),
]


def arch_html(cap="Messaging architecture: SVG to Slides"):
    rows = "".join(f'<div class="lvl"><b>{lvl}</b><div class="cells">' + "".join(
        f'<div class="cell {c}"><h6>{h}</h6><p>{p}</p></div>' for h, p, c in cells) + "</div></div>" for lvl, cells in ARCH)
    return f'<div class="dia"><div class="cap">{cap}</div><div style="margin-top:12px">{rows}</div></div>'


@fig("hero-messaging-architecture")
def hero():
    return arch_html()


@fig("messaging-architecture-levels")
def levels():
    return arch_html("Five levels, top of funnel to bottom")


@fig("flow-workshop-to-assets")
def flow():
    b = lambda h, p, st="": f'<div class="box" style="width:176px;{st}"><h6>{h}</h6><p>{p}</p></div>'
    arr = '<div class="arr"></div>'
    return f"""<div class="dia"><div class="cap">Two sheets feed every asset</div>
<div style="display:flex;align-items:center;gap:12px;margin-top:22px">
{b("1. Workshop form", "38 questions in 11 sections. Google Forms.", "background:#f4f5f7")}{arr}
{b("2. Workshop tab", "Latest response per question, with an override column.")}{arr}
{b("3. Architecture", "17 elements on 5 levels. =AI() drafts, approved lines.")}{arr}
{b("4. Messages", "One row per slot. Role, budget, approved line.", "border-color:#0066ff;border-width:2.5px")}{arr}
{b("Assets", "One-pager, deck, brief. Tagged text boxes.", "background:#1c1e22;color:#fff")}</div>
<div style="display:flex;align-items:center;gap:12px;margin-top:16px;justify-content:flex-end">
{b("Brand style sheet", "Colors, Type, Layout, Logo, Imagery, Voice, Personality.", "background:#fff6d6;border-color:#f9c80e;width:260px")}{arr}
{b("Export block", "One cell that scripts, agents and Gems read.", "background:#fff6d6;border-color:#f9c80e;width:230px")}{arr}
<div style="width:176px;text-align:center" class="b"><span style="font-size:11px;color:#6b6f76">fonts, sizes and colours by role</span></div></div>
<div class="b" style="margin-top:18px;font-size:12px;color:#6b6f76">Adjunct tabs on the messaging sheet: Refinements (change log), Audiences (variants per reader), Proof (evidence for each claim).</div></div>"""


@fig("workshop-form", 1000)
def form():
    radios = "".join(f'<div class="radio {"on" if a == "Do excellent work" else ""}"><i></i>{a}</div>' for a in
                     ["Be in control", "Be accepted by the team", "Do excellent work", "Be seen as the expert", "Save effort"])
    return f"""<div class="form"><div class="fcard t"><h3>Messaging workshop: SVG to Slides</h3><div style="font-size:13px;color:#5f6368">Answer in plain words. Short is fine.</div></div>
<div class="sec">Section 3 of 11 &middot; Champion</div>
<div class="fcard" style="border-radius:0 0 8px 8px"><div class="q">Who is the champion? Give the job title.</div><div class="a">Product marketer or designer who builds decks and collateral in Google Slides</div></div>
<div class="fcard"><div class="q">Explicit goal: what direct result do they want from a product like this?</div><div class="a">Put a logo or an icon in a deck and keep it crisp and editable.</div></div>
<div class="fcard"><div class="q">Implicit goal: what is the personal motivation behind the purchase?</div>{radios}</div>
<div class="prog"><span class="gbtn">Back</span><span class="gbtn p">Next</span><div class="bar"></div>Page 3 of 11</div></div>"""


@fig("architecture-tab")
def archtab():
    rows = [["Primary", "tagline", "Turns SVG files into real, individually editable vector shapes inside Google Slides. | Native, editable shapes from an SVG, with one drag&hellip;",
             "Convert SVG files into editable vector shapes directly inside Google Slides.", "Editable SVGs in Google Slides.", 48, 31, "OK"],
            ["Primary", "positioning", "Chrome extension for Google Slides: SVG import | Product marketer or designer&hellip; | Every SVG path becomes a native Slides shape&hellip;",
             "Import SVG files directly into Google Slides as editable vector shapes.", "Drag an SVG into your deck. SVG to Slides converts it into native Google Slides shapes, so you can edit individual elements&hellip;", 220, 175, "OK"],
            ["Level 2", "context", "Product marketing runs on decks and documents. Where there should be crisp icons and logos there are crunchy PNGs.",
             "Product marketing teams rely heavily on presentations and documents to pitch their offerings. However, they frequently settle for low-resolution, pixelated images&hellip;", "Product marketing runs on decks and documents. Where there should be crisp icons and logos there are crunchy PNGs.", 200, 114, "OK"],
            ["Level 2", "problem", "Google Slides doesn&rsquo;t support SVG files. Your options are to flatten them into PNGs&hellip; | Flatten the SVG into a PNG&hellip;",
             "Google Slides does not natively support SVG files, forcing users to rely on tedious workarounds or lose quality by flattening them into PNGs.", "Google Slides doesn&rsquo;t support SVG files. Your options are to flatten them into PNGs or take the long way through EMF conversion&hellip;", 200, 157, "OK"]]
    g = ci.grid(["Level", "Key", "Source notes", "Draft", "Approved line", "Budget", "Length", "Fits"], [70, 90, 260, 260, 270, 56, 56, 56], rows, cur=(2, 3), hl=4)
    return ci.sheet_win(g, ["Workshop", "Architecture", "Messages", "Refinements", "Audiences", "Proof", "Assets", "Approvals"], "Architecture", "D2",
                        '=AI("Lead message / tagline. Write this element of a B2B messaging hierarchy from the workshop notes. One line. Plain, specific, active voice. No superlatives.", C2)',
                        title="SVG to Slides - Messaging architecture", )


COLORS = [("ink", "#1C1E22", "Text", "Headlines and body on white"), ("grey", "#6B6F76", "Secondary text", "Body, labels, legal"), ("white", "#FFFFFF", "Background", "Every page. White backgrounds only."),
          ("amber", "#F9C80E", "Accent", "Step badges, rules, highlights"), ("blue", "#0066FF", "Action", "Buttons, stats, eyebrow"), ("tint", "#F4F5F7", "Soft block", "Proof strip only")]
TYPE = [("eyebrow", "Overpass", "SemiBold", 11, 14, "blue"), ("headline", "Overpass", "SemiBold", 34, 44, "ink"), ("subhead", "Verdana", "Regular", 12, 16, "grey"),
        ("title", "Overpass", "SemiBold", 15, 22, "ink"), ("body", "Verdana", "Regular", 10, 14, "grey"), ("stat", "Overpass", "SemiBold", 30, 44, "blue"), ("cta", "Overpass", "SemiBold", 12, 16, "white")]


@fig("style-sheet-colors-type")
def style():
    tabs = ["Colors", "Type", "Layout", "Logo", "Imagery", "Voice", "Personality", "Gems", "Export"]
    g1 = ci.grid(["Token", "Hex", "Role", "Use for", "Swatch"], [110, 100, 150, 330, 110], [[t, h, r, u, f'<span class="sw" style="background:{h}"></span>'] for t, h, r, u in COLORS])
    g2 = ci.grid(["Role", "Font", "Weight", "Print pt", "Deck pt", "Colour token"], [130, 150, 130, 100, 100, 190], [list(r) for r in TYPE])
    a = ci.sheet_win(g1, tabs, "Colors", "A1", "Token", title="SVG to Slides - Brand style sheet")
    b = ci.sheet_win(g2, tabs, "Type", "A1", "Role", title="SVG to Slides - Brand style sheet")
    return f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:26px;zoom:.62">{a}{b}</div>'


@fig("style-export-block")
def export():
    blk = """<b>/* SVG to Slides style block */</b>
<b>colors {</b>
  --ink: #1C1E22;  /* Text */
  --amber: #F9C80E;  /* Accent */
  --blue: #0066FF;  /* Action */
<b>}</b>
<b>type {</b>
  headline: Overpass SemiBold, print 34pt, deck 44pt, color ink;
  body: Verdana Regular, print 10pt, deck 14pt, color grey;
<b>}</b>
<b>voice {</b>
  No em dashes. Do: Use a full stop or a comma.
  Tighten. Do: Cut until every word carries something. Do not: Get cute.
<b>}</b>
<b>personality {</b>
  Archetype: Creator
  We are: Plain, exact, useful.
<b>}</b>"""
    users = "".join(f'<div class="box" style="width:250px"><h6>{h}</h6><p>{p}</p></div>' for h, p in [
        ("Gems", "Paste it under each Gem&rsquo;s instructions: copy editor, image maker, asset checker."),
        ("Agents", "Claude, Codex or Gemini read the cell before they write or review."),
        ("Script", "apply_style.gs reads the same tabs and sets fonts, sizes and colours by role.")])
    return f"""<div class="dia"><div class="cap">Export tab: the whole style sheet in one cell</div>
<div style="display:flex;gap:26px;align-items:center;margin-top:18px"><pre class="blk" style="flex:1">{blk}</pre><div class="arr" style="flex:none;width:44px"></div>
<div style="display:flex;flex-direction:column;gap:10px">{users}</div></div></div>"""


@fig("gems-tab")
def gems():
    star = '<span class="star"></span>'
    g = "".join(f'<div class="gemc"><h6>{star}{h}</h6><p>{p}</p></div>' for h, p in [
        ("Message drafter", "Turns a plain fact into a line that fits its role and character budget."),
        ("Copy editor", "Checks a draft against the voice rules and gives a corrected line."),
        ("Image maker", "Generates images in the brand&rsquo;s imagery style, palette only, no text."),
        ("Image prep", "Crops a supplied image to a slot, applies the treatment, reports the size."),
        ("Asset checker", "Compares a deck with both sheets and reports differences. Changes nothing.")])
    return f'<div class="dia"><div class="cap">Five Gems, one style block</div><div style="display:flex;gap:12px;margin-top:18px">{g}</div></div>'


@fig("svgs-one-pager", 1100)
def onepager():
    img = base64.b64encode((SRC / "svgs-one-pager.png").read_bytes()).decode()
    notes = "".join(f'<div style="display:flex;gap:10px;margin-bottom:12px"><span class="tag" style="position:static;align-self:flex-start">{t}</span><span class="b" style="font-size:12px;line-height:1.5">{d}</span></div>' for t, d in [
        ("slot:headline", "Architecture &rsaquo; tagline. Overpass SemiBold 34 pt, ink."), ("slot:subhead", "Architecture &rsaquo; positioning. Verdana 12 pt, grey."),
        ("slot:step_1_body", "Architecture &rsaquo; how_1. Verdana 10 pt, grey."), ("slot:stat_1_value", "Proof tab. Overpass SemiBold 30 pt, blue."),
        ("slot:cta", "Overpass SemiBold 12 pt, white on a blue pill."), ("slot:legal", "Carries the Google trademark line.")])
    return f"""<div class="dia" style="display:flex;gap:36px;align-items:center"><img src="data:image/png;base64,{img}" style="width:470px;border:1px solid #dee1e6;box-shadow:0 8px 26px rgba(20,24,40,.12)">
<div style="flex:1"><div class="cap">Built from the two sheets</div><div class="h" style="font-size:24px;margin:8px 0 18px">SVG to Slides one-pager</div>{notes}
<div class="b" style="font-size:12px;color:#6b6f76;margin-top:8px">25 tagged text boxes. Copy from the Messages tab, type and colour from the style sheet.</div></div></div>"""


def main():
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        for name, (fn, width) in FIGS.items():
            pg = br.new_page(viewport={"width": width, "height": 800}, device_scale_factor=2)
            pg.set_content(f'<html><head><style>{ci.CSS}{CSS2}</style></head><body><div id="f">{fn()}</div></body></html>')
            pg.wait_for_timeout(200)
            pg.locator("#f").screenshot(path=str(OUT / f"{name}.png"))
            if name.startswith("hero"):
                from PIL import Image
                im = Image.open(OUT / f"{name}.png").convert("RGB")
                w, h = im.size
                th = int(w * 630 / 1200)
                canvas = Image.new("RGB", (w, max(h, th)), (246, 247, 249)); canvas.paste(im, (0, (max(h, th) - h) // 2))
                canvas.crop((0, (canvas.height - th) // 2, w, (canvas.height - th) // 2 + th)).resize((1200, 630), Image.LANCZOS).save(OUT / "og-messaging-architecture.png", optimize=True)
            pg.close(); print(name)
        br.close()


if __name__ == "__main__":
    main()
