#!/usr/bin/env python3
"""Build svgslid.es SEO/AEO assets. Idempotent: safe to re-run.

Generates into cloud/static/:
  - <slug>.html keyword landing pages (from tools/site_content.py)
  - md/<page>.md agent-readable markdown for every content page
  - sitemap.xml, robots.txt, llms.txt, llms-full.txt, 404.html
and patches existing pages in place:
  - title/description/OG/Twitter, canonical, robots noindex, markdown alternate link
  - JSON-LD, analytics head block, UTM-tagged + data-cta Chrome Web Store links,
    guides footer nav, /static/site.js

Usage: python3 tools/build_site.py   (reads GA4 measurement ID from tools/ga_id.txt if present)
"""
import datetime as dt
import html
import json
import re
from pathlib import Path

import site_content as C

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "cloud" / "static"
MD = STATIC / "md"
TODAY = dt.date.today().isoformat()
GA_FILE = ROOT / "tools" / "ga_id.txt"
GA_ID = GA_FILE.read_text().strip() if GA_FILE.exists() else ""
GTM_ID = "GTM-MTPNJHCL"

def esc(s):  # attribute-safe text from strings that may contain entities
    return html.escape(html.unescape(re.sub(r"<[^>]+>", "", s)), quote=True)

def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))

# ---------------------------------------------------------------- head pieces
def analytics_block():
    ga = ""
    if GA_ID:
        ga = (f'  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
              f"  <script>gtag('config', '{GA_ID}');</script>\n")
    return ("  <!-- analytics:start -->\n"
            "  <script>\n"
            "    window.dataLayer = window.dataLayer || [];\n"
            "    function gtag(){dataLayer.push(arguments);}\n"
            "    gtag('js', new Date());\n"
            "  </script>\n"
            f'  <script async src="https://www.googletagmanager.com/gtm.js?id={GTM_ID}"></script>\n'
            f"{ga}"
            "  <!-- analytics:end -->\n")

ANALYTICS_RE = re.compile(r"  <!-- (?:Google tag|analytics:start) -->.*?(?:</script>\n(?=  <meta name=\"viewport\")|<!-- analytics:end -->\n)", re.S)

def set_analytics(doc):
    if ANALYTICS_RE.search(doc):
        return ANALYTICS_RE.sub(lambda m: analytics_block(), doc, count=1)
    return doc.replace('<meta charset="utf-8">\n', '<meta charset="utf-8">\n' + analytics_block(), 1)

def software_ld():
    return {
        "@context": "https://schema.org", "@type": "SoftwareApplication",
        "name": "SVG to Slides", "url": C.SITE + "/",
        "applicationCategory": "DesignApplication", "operatingSystem": "Chrome",
        "description": "Free Chrome extension that inserts SVG files into Google Slides as native, editable shapes.",
        "downloadUrl": C.CWS, "installUrl": C.CWS,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "image": C.SITE + "/static/og-image.png",
    }

def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": plain(q),
                            "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in faq]}

def crumbs_ld(name, path):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "SVG to Slides", "item": C.SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": plain(name), "item": C.SITE + path}]}

def howto_ld(name, steps):
    return {"@context": "https://schema.org", "@type": "HowTo", "name": plain(name),
            "tool": [{"@type": "HowToTool", "name": "SVG to Slides Chrome extension"}],
            "step": [{"@type": "HowToStep", "position": i + 1, "name": plain(t), "text": plain(d)}
                     for i, (t, d) in enumerate(steps)]}

def ld_block(objs):
    body = "\n".join(f'  <script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>' for o in objs)
    return f"  <!-- ld:start -->\n{body}\n  <!-- ld:end -->\n"

def set_ld(doc, objs):
    doc = re.sub(r"  <!-- ld:start -->.*?<!-- ld:end -->\n", "", doc, flags=re.S)
    return doc.replace("</head>", ld_block(objs) + "</head>", 1) if objs else doc

def set_meta(doc, path, title=None, desc=None, noindex=False, md=None):
    url = C.SITE + path
    if title:
        doc = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title, quote=False)}</title>", doc, count=1, flags=re.S)
        for prop in ("og:title", "twitter:title"):
            attr = "property" if prop.startswith("og") else "name"
            doc = re.sub(rf'<meta {attr}="{prop}" content="[^"]*">', f'<meta {attr}="{prop}" content="{esc(title)}">', doc)
    if desc:
        doc = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', doc)
        doc = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(desc)}">', doc)
        doc = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{esc(desc)}">', doc)
    doc = re.sub(r'  <link rel="canonical" href="[^"]*">\n', "", doc)
    doc = re.sub(r'  <meta name="robots" content="[^"]*">\n', "", doc)
    doc = re.sub(r'  <link rel="alternate" type="text/markdown" href="[^"]*">\n', "", doc)
    extra = f'  <link rel="canonical" href="{url}">\n'
    if noindex:
        extra += '  <meta name="robots" content="noindex, follow">\n'
    if md:
        extra += f'  <link rel="alternate" type="text/markdown" href="{md}">\n'
    return doc.replace("  <meta name=\"viewport\"", extra + "  <meta name=\"viewport\"", 1)

# ------------------------------------------------------------- CTA tagging
CWS_HREF = re.compile(r'href="' + re.escape(C.CWS) + r'(?:\?[^"]*)?"(?: data-cta="[^"]*")?')

def tag_ctas(doc, campaign):
    """UTM-tag every Chrome Web Store link. Position by order: nav, hero, body-N..., close (last)."""
    total = len(CWS_HREF.findall(doc))
    n = {"i": 0}
    def rep(m):
        i = n["i"]; n["i"] += 1
        has_nav = 'class="nav"' in doc[:m.start()] and i == 0
        pos = "nav" if has_nav else ("hero" if i == 1 or (i == 0 and total == 1) else
              ("close" if i == total - 1 and total >= 3 else f"body{i}"))
        q = f"utm_source=svgslid.es&amp;utm_medium=web&amp;utm_campaign={campaign}&amp;utm_content={pos}"
        return f'href="{C.CWS}?{q}" data-cta="{pos}"'
    return CWS_HREF.sub(rep, doc)

def add_sitejs(doc):
    if "/static/site.js" in doc:
        return doc
    return doc.replace("</body>", '<script src="/static/site.js" defer></script>\n</body>', 1)

# ------------------------------------------------------------- footer guides nav
def guides_nav():
    links = " &nbsp;&middot;&nbsp; ".join(f'<a href="/{p["slug"]}">{p["nav"]}</a>' for p in C.PAGES)
    return (f'  <!-- guides:start -->\n  <nav class="wrap foot guides" aria-label="Guides"><span>Guides: '
            f'<a href="/guide">SVG vs PNG in Slides</a> &nbsp;&middot;&nbsp; {links} &nbsp;&middot;&nbsp; <a href="/blog">Blog</a></span></nav>\n  <!-- guides:end -->\n')

def set_guides(doc):
    doc = re.sub(r"  <!-- guides:start -->.*?<!-- guides:end -->\n", "", doc, flags=re.S)
    return doc.replace("</main>", guides_nav() + "</main>", 1) if "</main>" in doc else doc

# ------------------------------------------------------------- landing pages
EXTRA_CSS = """
/* landing */
.crumb{font-size:13px;color:var(--mute);padding-top:8px} .crumb a{color:var(--mute);text-decoration:none} .crumb a:hover{text-decoration:underline}
.answer{max-width:46em;margin:56px auto 0;padding:22px 26px;border-left:4px solid var(--yellow);background:var(--tint);border-radius:0 14px 14px 0;font-size:17px;line-height:1.6}
.answer b{font-family:var(--display);font-weight:600}
.sec{padding-block:56px}
.sec h2{text-align:center;margin-bottom:32px}
.list{max-width:46em;margin:0 auto;padding:0;list-style:none;display:grid;gap:16px}
.list li{font-size:16px;line-height:1.55;color:var(--mute)} .list li b{color:var(--fg)}
.cmp{width:100%;max-width:46em;margin:0 auto;border-collapse:collapse;font-size:15px}
.cmp th,.cmp td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--rule);vertical-align:top}
.cmp th{font:600 15px var(--display)} .cmp td:first-child{color:var(--mute)}
.cards3{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.cards3 .card{padding:28px} .cards3 .card .btn{margin-top:auto;align-self:flex-start;height:44px;font-size:15px;padding:0 18px}
.faq{max-width:46em;margin:0 auto}
.faq details{border-bottom:1px solid var(--rule);padding:16px 0}
.faq summary{cursor:pointer;font:600 18px var(--display)}
.faq details p{color:var(--mute);margin-top:10px;font-size:15px}
.related{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.related a{border:1.5px solid var(--rule);border-radius:999px;padding:8px 16px;text-decoration:none;font-size:14px} .related a:hover{border-color:var(--mute)}
@media (max-width:760px){ .cards3{grid-template-columns:1fr} }
"""

def landing_html(p, css, head_icons):
    slug, path = p["slug"], "/" + p["slug"]
    cta = lambda pos, label="Add to Chrome &mdash; free": (
        f'<a class="btn btn-primary" href="{C.CWS}"><img src="/static/chrome-glyph.svg" alt="">{label}</a>')
    body = []
    if p.get("howto"):
        steps = "".join(f'<div class="step"><div class="n">Step {i+1}</div><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(p["howto"]))
        body.append(f'<section class="wrap steps" id="how"><h2>How to do it</h2><div class="steprow">{steps}</div></section>')
    if p.get("compare"):
        rows = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in p["compare"])
        body.append(f'<section class="wrap sec"><h2>Flattened vs. converted</h2><table class="cmp"><thead><tr><th>Pasted as PNG (default)</th><th>Inserted with SVG to Slides</th></tr></thead><tbody>{rows}</tbody></table></section>')
    if p.get("cards"):
        cards = "".join(
            f'<article class="card"><h3>{t}</h3><p>{d}</p>'
            + (f'<a class="btn btn-primary" href="{C.CWS}"><img src="/static/chrome-glyph.svg" alt="">{lbl}</a>' if href == C.CWS
               else f'<a class="btn btn-ghost" href="{href}">{lbl}</a>')
            + "</article>" for t, d, href, lbl in p["cards"])
        body.append(f'<section class="wrap sec"><h2>Pick your route</h2><div class="cards3">{cards}</div></section>')
    if p.get("points"):
        items = "".join(f"<li><b>{t}</b> {d}</li>" for t, d in p["points"])
        body.append(f'<section class="wrap sec"><h2>What you can do</h2><ul class="list">{items}</ul></section>')
    for h, items in p.get("sections", []):
        lis = "".join(f"<li>{x}</li>" for x in items)
        body.append(f'<section class="wrap sec"><h2>{h}</h2><ul class="list">{lis}</ul></section>')
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in p["faq"])
    body.append(f'<section class="wrap sec"><h2>Questions</h2><div class="faq">{faq}</div></section>')
    rel = {x["slug"]: x for x in C.PAGES}
    links = "".join(f'<a href="/{s}">{rel[s]["nav"]}</a>' for s in p["related"])
    body.append(f'<section class="wrap sec"><h2>Related</h2><nav class="related" aria-label="Related guides"><a href="/guide">SVG vs PNG in Google Slides</a>{links}</nav></section>')
    rule = '\n  <div class="wrap"><hr class="rule"></div>\n  '
    lds = [software_ld(), faq_ld(p["faq"]), crumbs_ld(p["nav"], path)]
    if p.get("howto"):
        lds.append(howto_ld(p["h1"], p["howto"]))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
{analytics_block()}  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{html.escape(p["title"], quote=False)}</title>
  <meta name="description" content="{esc(p["desc"])}">
{head_icons}  <meta property="og:title" content="{esc(p["title"])}">
  <meta property="og:description" content="{esc(p["desc"])}">
  <meta property="og:image" content="https://svgslid.es/static/og-image.png">
  <meta property="og:url" content="{C.SITE}{path}">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(p["title"])}">
  <meta name="twitter:description" content="{esc(p["desc"])}">
  <meta name="twitter:image" content="https://svgslid.es/static/og-image.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Overpass:wght@600&display=swap" rel="stylesheet">
<style>{css}{EXTRA_CSS}</style>
</head>
<body>
<div class="wrap">
  <nav class="nav">
    <a class="brand" href="/"><img src="/static/mark.svg" alt=""><span>SVG to Slides</span></a>
    {cta("nav", "Add to Chrome")}
  </nav>
  <p class="crumb"><a href="/">SVG to Slides</a> &rsaquo; {p["nav"]}</p>
</div>
<main>
  <section class="wrap hero">
    <h1>{p["h1"]}</h1>
    <p class="lede">{p["lede"]}</p>
    <div class="ctas">
      {cta("hero")}
      <a class="btn btn-ghost" href="/convert">Convert online instead</a>
    </div>
    <p class="free">{C.FREE_LINE}</p>
    <div class="shot"><div class="lot" data-lottie="/static/lottie/{p["lottie"]}"></div></div>
    <p class="answer"><b>Short answer:</b> {p["answer"]}</p>
  </section>
  <div class="wrap"><hr class="rule" style="margin-top:56px"></div>
  {rule.join(body)}
  <div class="wrap"><hr class="rule"></div>
  <section class="wrap close">
    <h2>Bring your SVGs into Google Slides&trade;.</h2>
    {cta("close")}
    <p class="free" style="margin-top:16px">{C.FREE_LINE}</p>
  </section>
  <div class="wrap"><hr class="rule"></div>
  <footer class="wrap foot">
    <span>svgslid.es &nbsp;&middot;&nbsp; <a href="/privacy">Privacy</a> &nbsp;&middot;&nbsp; <a href="/terms">Terms</a> &nbsp;&middot;&nbsp; <a href="/support">Support</a> &nbsp;&middot;&nbsp; Built by Joe Gelman</span>
    <span>Google Slides&trade; and Google Drawings&trade; are trademarks of Google LLC.</span>
  </footer>
</main>
{LOTTIE_JS}
</body>
</html>
"""

def landing_md(p):
    out = [f"# {plain(p['h1'])}", "", p_answer(p), "", f"_{C.FREE_LINE}_", "",
           f"- Install the Chrome extension: {C.CWS}", f"- Online converter: {C.SITE}/convert", ""]
    if p.get("howto"):
        out += ["## How to do it"] + [f"{i+1}. **{plain(t)}** {plain(d)}" for i, (t, d) in enumerate(p["howto"])] + [""]
    if p.get("compare"):
        out += ["## Flattened vs. converted", "", "| Pasted as PNG (default) | Inserted with SVG to Slides |", "|---|---|"]
        out += [f"| {plain(a)} | {plain(b)} |" for a, b in p["compare"]] + [""]
    if p.get("cards"):
        out += ["## Pick your route"] + [f"- **{t}** — {plain(d)} ({h if h.startswith('http') else C.SITE + h})" for t, d, h, _ in p["cards"]] + [""]
    if p.get("points"):
        out += ["## What you can do"] + [f"- **{plain(t)}** {plain(d)}" for t, d in p["points"]] + [""]
    for h, items in p.get("sections", []):
        out += [f"## {h}"] + [f"- {plain(x)}" for x in items] + [""]
    out += ["## Questions", ""]
    for q, a in p["faq"]:
        out += [f"### {plain(q)}", plain(a), ""]
    return "\n".join(out)

def p_answer(p):
    return plain(p["answer"])

LOTTIE_JS = """<script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
<script>
(function(){
  if(!window.lottie||matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var anims=[];
  document.querySelectorAll('.lot[data-lottie]').forEach(function(el){
    var a=lottie.loadAnimation({container:el,renderer:'svg',loop:true,autoplay:false,path:el.dataset.lottie,rendererSettings:{preserveAspectRatio:'xMidYMid meet'}});
    anims.push({el:el,a:a});
  });
  var io=new IntersectionObserver(function(es){es.forEach(function(e){var x=anims.find(function(z){return z.el===e.target}); if(!x)return; e.isIntersecting?x.a.play():x.a.pause();})},{threshold:.25});
  anims.forEach(function(x){io.observe(x.el)});
})();
</script>"""

GUIDE_FAQ = [
    ("Does Google Slides support SVG natively?", "Not as an editable format. Slides will accept a pasted or inserted SVG, but it rasterizes it into a flattened image on the way in, so you lose the ability to edit individual paths or recolor parts of it. svgslid.es converts it into Slides' native shape format instead, so it stays fully editable."),
    ("What happens to gradients and complex curves?", "Solid fills and strokes convert cleanly. Gradients currently collapse to a solid approximate color, and arc commands (A/a) in paths are approximated as straight line segments. Re-exporting with more path segments avoids visibly angular curves."),
    ("Is my file uploaded anywhere?", "Depends on the surface. The Chrome extension converts entirely on your device using an embedded WebAssembly engine, so your file usually never leaves the browser. The web app and add-on send the file to our backend for conversion, which discards it immediately afterward."),
    ("Is it free?", "Yes. " + C.FREE_LINE),
]

GUIDE_MD = """# SVG in Google Slides: vector vs. flattened PNG

Drop an SVG onto a Slides canvas the normal way and Google flattens it into a raster image. Here's what that costs you, and how to avoid it.

## What you lose when Slides flattens your SVG

| Pasted as PNG (default) | Inserted as vector (svgslid.es) |
|---|---|
| Blurs or pixelates when resized | Resizes at any size, always crisp |
| One flattened image, single object | Every path is its own selectable shape |
| Can't recolor without re-exporting | Recolor any shape directly in Slides |
| Can't animate individual elements | Animate each shape independently |
| Can't edit points/paths | Right-click → Edit points, like any native shape |

## How svgslid.es keeps it a vector

Every `<path>` in your SVG is converted directly into Google Slides' own native shape format. It isn't re-rendered as an image or embedded by a third party. The result behaves exactly like a shape you drew in Slides yourself.

- **Web app** ({site}/convert): upload one or more SVGs, get back a Google Drive link to a ready-made Slides deck, one slide per file.
- **Google Slides add-on** ({site}/addon): insert SVGs from a dialog inside Slides.
- **Chrome extension** ({cws}): drag an SVG file straight onto an open Slides tab.

## Frequently asked
"""

CONVERT_MD = """# SVG to Google Slides converter (online)

Upload SVG files at {site}/convert and get a Slides-ready file with real, editable vector shapes.

1. Upload one or more .svg files.
2. Every `<path>` becomes a discrete, individually selectable vector shape in Google Slides, not a flattened image. Each SVG becomes one slide.
3. The file is uploaded to Google Drive and a shareable link is returned, optionally shared to a Google account email you provide.

The link is deleted after 7 days. To keep a file, open it in Drive and choose File → Make a copy.

Note: arc commands (A/a) in SVG paths are approximated as straight lines.

Prefer to drop SVGs straight onto a slide? Install the free Chrome extension: {cws}

_{free}_
"""

# ------------------------------------------------------------- main

# ------------------------------------------------------------------- blog
import blog_content as B
from PIL import Image

BLOG_IMG = STATIC / "blog" / "img"
BLOG_FONTS = '<link href="https://fonts.googleapis.com/css2?family=Overpass:wght@600;700;800&display=swap" rel="stylesheet">'
BLOG_CSS = """
.bnav{display:flex;gap:22px;align-items:center}
.bnav a.txt{color:var(--fg);text-decoration:none;font-family:var(--display);font-weight:700;font-size:16px}
.post{max-width:62ch;margin:0 auto;padding:8px 20px 0;font-family:var(--body);font-size:17px;line-height:1.7}
.post h1,.post h2,.post h3,.bindex h1,.pcard h2{font-family:var(--display);font-weight:800;letter-spacing:-.02em;text-align:left}
.post h1{font-size:clamp(34px,5.4vw,52px);line-height:1.06;margin:14px 0 16px;max-width:none}
.post h2{font-size:clamp(24px,3.2vw,30px);line-height:1.15;margin:2.2em 0 .5em;scroll-margin-top:24px}
.post p,.post ul,.post ol{margin:0 0 1.05em}
.post ul,.post ol{padding-left:1.25em}.post li{margin:.35em 0}
.post a{color:var(--blue-ink);text-underline-offset:3px;text-decoration-thickness:1px}
.kick{font-family:var(--display);font-weight:800;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--blue)}
.dek{font-size:19px;line-height:1.55;color:var(--mute);margin:0 0 18px}
.meta{font-size:14px;color:var(--mute);margin:0 0 28px}
.tldr{background:var(--tint);border-left:5px solid var(--yellow);border-radius:0 12px 12px 0;padding:18px 22px 6px;margin:30px 0 8px}
.tldr b.h{display:block;font-family:var(--display);font-weight:800;letter-spacing:.1em;font-size:13px;text-transform:uppercase;margin-bottom:6px}
.tldr ul{margin:0 0 12px}
.post figure,.post .herofig{width:min(940px,calc(100vw - 24px));position:relative;left:50%;transform:translateX(-50%);margin:30px 0 34px}
.post figure img,.post .herofig img{width:100%;height:auto;display:block;border-radius:14px}
.post .herofig img{border:1px solid var(--rule)}
.post figure img{border-radius:0}
.post figcaption{max-width:62ch;margin:10px auto 0;padding:0 20px;font-size:14px;line-height:1.5;color:var(--mute);text-align:center}
.post ol.steps{counter-reset:s;list-style:none;padding:0}
.post ol.steps li{counter-increment:s;position:relative;padding:12px 0 12px 48px;border-bottom:1px solid var(--rule);margin:0}
.post ol.steps li::before{content:counter(s);position:absolute;left:0;top:10px;width:32px;height:32px;border-radius:50%;background:var(--yellow);color:#1c1e22;font-family:var(--display);font-weight:800;display:grid;place-items:center;font-size:16px}
.post a.btn{color:#fff;text-decoration:none}
.post figure.narrow{width:min(680px,calc(100vw - 24px))}
.endcta{margin:48px 0 0;padding:24px;border:1px solid var(--rule);border-radius:16px}
.endcta p{margin:0 0 14px}
.sources{font-size:14px;line-height:1.6;color:var(--mute);margin-top:40px}
.sources h2{font-size:18px;margin:0 0 6px}
.bindex{max-width:760px;margin:0 auto;padding:10px 20px 40px}
.bindex h1{font-size:clamp(38px,6vw,60px);margin:10px 0 6px;max-width:none}
.bindex>p{font-size:18px;color:var(--mute);margin:0 0 34px;line-height:1.6}
.pcard{display:block;text-decoration:none;color:inherit;border:1px solid var(--rule);border-radius:18px;overflow:hidden;transition:transform .15s,box-shadow .15s}
.pcard:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(0,0,0,.08)}
.pcard img{width:100%;height:auto;display:block;border-bottom:1px solid var(--rule)}
.pcard .in{padding:20px 24px 24px;font-size:16px;line-height:1.6}
.pcard h2{font-size:28px;line-height:1.12;margin:6px 0 8px}
.pcard p{margin:0;color:var(--mute)}
"""

def blog_webp():
    for png in BLOG_IMG.glob("*.png"):
        wp = png.with_suffix(".webp")
        if not wp.exists() or wp.stat().st_mtime < png.stat().st_mtime:
            Image.open(png).save(wp, "WEBP", quality=86, method=6)

def fig(name, alt, cap, hero=False):
    w, h = Image.open(BLOG_IMG / f"{name}.png").size
    lazy = '' if hero else ' loading="lazy"'
    dk = (BLOG_IMG / f"{name}-dark.png").exists()
    dsrc = f'<source media="(prefers-color-scheme: dark)" type="image/webp" srcset="/static/blog/img/{name}-dark.webp">' if dk else ''
    pic = (f'<picture>{dsrc}<source type="image/webp" srcset="/static/blog/img/{name}.webp">'
           f'<img src="/static/blog/img/{name}.png" width="{w}" height="{h}" alt="{esc(alt)}"{lazy} decoding="async"></picture>')
    if hero:
        return f'<div class="herofig">{pic}</div>'
    cls = ' class="narrow"' if w < 1300 else ''
    return f'<figure{cls}><a href="/static/blog/img/{name}.png">{pic}</a><figcaption>{cap}</figcaption></figure>'

FIG_RE = re.compile(r"\{fig:([^|}]+)\|([^|}]+)\|([^}]*)\}")

def cws(campaign, pos):
    return f'{C.CWS}?utm_source=svgslid.es&amp;utm_medium=web&amp;utm_campaign={campaign}&amp;utm_content={pos}'

def blog_shell(title, desc, path, og, ld, body, css, head_icons, campaign, md, og_type="article"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
{analytics_block()}  <link rel="canonical" href="{C.SITE}{path}">
  <link rel="alternate" type="text/markdown" href="{md}">
  <link rel="alternate" type="application/rss+xml" title="SVG to Slides blog" href="/blog/feed.xml">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{html.escape(title, quote=False)}</title>
  <meta name="description" content="{esc(desc)}">
{head_icons}  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:image" content="{C.SITE}/static/{og}">
  <meta property="og:url" content="{C.SITE}{path}">
  <meta property="og:type" content="{og_type}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{C.SITE}/static/{og}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  {BLOG_FONTS}
{ld_block(ld)}<style>{css}{EXTRA_CSS}{BLOG_CSS}</style>
</head>
<body>
<div class="wrap">
  <nav class="nav">
    <a class="brand" href="/"><img src="/static/mark.svg" alt=""><span>SVG to Slides</span></a>
    <span class="bnav"><a class="txt" href="/blog">Blog</a><a class="btn btn-primary" href="{cws(campaign, 'nav')}" data-cta="nav"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome</a></span>
  </nav>
</div>
<main>
{body}
  <div class="wrap"><hr class="rule" style="margin-top:64px"></div>
  <footer class="wrap foot">
    <span>svgslid.es &nbsp;&middot;&nbsp; <a href="/blog">Blog</a> &nbsp;&middot;&nbsp; <a href="/privacy">Privacy</a> &nbsp;&middot;&nbsp; <a href="/terms">Terms</a> &nbsp;&middot;&nbsp; <a href="/support">Support</a> &nbsp;&middot;&nbsp; Built by Joe Gelman</span>
    <span>Google Slides&trade; and Google Docs&trade; are trademarks of Google LLC. Not affiliated with Google.</span>
  </footer>
</main>
<script src="/static/site.js" defer></script>
</body>
</html>
"""

def post_html(p, css, head_icons):
    path = f"/blog/{p['slug']}"
    camp = f"blog-{p['slug']}"
    body_html = FIG_RE.sub(lambda m: fig(m.group(1), m.group(2), m.group(3)), p["body"])
    tldr = "".join(f"<li>{x}</li>" for x in p["tldr"])
    src = "".join(f'<li><a href="{u}">{html.escape(t)}</a></li>' for t, u in p["sources"])
    body = f"""  <article class="post">
    <p class="crumb" style="margin:0"><a href="/blog">Blog</a></p>
    <div class="kick">{p["kicker"]}</div>
    <h1>{p["h1"]}</h1>
    <p class="dek">{p["dek"]}</p>
    <p class="meta"><time datetime="{p["date"]}">{p["date_h"]}</time> &middot; {p["read"]} &middot; Joe Gelman</p>
    {fig(p["hero"][0], p["hero"][1], "", hero=True)}
    <div class="tldr"><b class="h">TL;DR</b><ul>{tldr}</ul></div>
{body_html}
    <div class="endcta">
      <p><b>Building decks with real design assets?</b> SVG to Slides drops SVG logos and icons into Google Slides as native, editable shapes &mdash; recolor any part, no PNG blur. {C.FREE_LINE}</p>
      <a class="btn btn-primary" href="{cws(camp, 'post-end')}" data-cta="post-end"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome &mdash; free</a>
    </div>
    <section class="sources"><h2>Sources</h2><ul>{src}</ul></section>
  </article>"""
    ld = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["h1"], "description": plain(p["desc"]),
           "datePublished": p["date"], "dateModified": TODAY, "image": f"{C.SITE}/static/blog/img/{p['og']}",
           "author": {"@type": "Person", "name": "Joe Gelman"},
           "publisher": {"@type": "Organization", "name": "SVG to Slides", "url": C.SITE + "/",
                         "logo": {"@type": "ImageObject", "url": C.SITE + "/static/favicon.png"}},
           "mainEntityOfPage": C.SITE + path},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "SVG to Slides", "item": C.SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "Blog", "item": C.SITE + "/blog"},
              {"@type": "ListItem", "position": 3, "name": p["h1"], "item": C.SITE + path}]}]
    return blog_shell(p["title"], p["desc"], path, f"blog/img/{p['og']}", ld, body, css, head_icons, camp, f"{path}.md")

def blog_index_html(css, head_icons):
    cards = "".join(
        f'<a class="pcard" href="/blog/{p["slug"]}"><picture><source media="(prefers-color-scheme: dark)" type="image/webp" srcset="/static/blog/img/{p["og"][:-4]}-dark.webp"><source type="image/webp" srcset="/static/blog/img/{p["og"][:-4]}.webp">'
        f'<img src="/static/blog/img/{p["og"]}" width="1200" height="630" alt="{esc(p["hero"][1])}"></picture>'
        f'<div class="in"><div class="kick">{p["kicker"]} &middot; {p["date_h"]}</div><h2>{p["h1"]}</h2><p>{p["dek"]}</p></div></a>'
        for p in B.POSTS)
    body = f"""  <section class="bindex">
    <div class="kick">svgslid.es</div>
    <h1>Blog</h1>
    <p>Short notes on making Google Workspace look designed: new features, type, and layout craft for Slides and Docs.</p>
    {cards}
  </section>"""
    ld = [{"@context": "https://schema.org", "@type": "Blog", "name": "SVG to Slides blog", "url": C.SITE + "/blog",
           "blogPost": [{"@type": "BlogPosting", "headline": p["h1"], "url": f"{C.SITE}/blog/{p['slug']}", "datePublished": p["date"]} for p in B.POSTS]}]
    return blog_shell("Blog — Design notes for Google Slides & Docs | SVG to Slides",
                      "Short, design-minded notes on Google Slides and Docs: new features, typography and layout craft.",
                      "/blog", f"blog/img/{B.POSTS[0]['og']}", ld, body, css, head_icons, "blog", "/blog.md", og_type="website")

def build_blog(css, head_icons):
    blog_webp()
    (STATIC / "blog").mkdir(exist_ok=True)
    (MD / "blog").mkdir(exist_ok=True)
    (STATIC / "blog" / "index.html").write_text(blog_index_html(css, head_icons))
    idx_md = ["# SVG to Slides blog", "", "Short, design-minded notes on Google Slides and Docs.", ""]
    items = []
    for p in B.POSTS:
        (STATIC / "blog" / f"{p['slug']}.html").write_text(post_html(p, css, head_icons))
        (MD / "blog" / f"{p['slug']}.md").write_text(p["md"])
        idx_md.append(f"- [{p['h1']}]({C.SITE}/blog/{p['slug']}.md) ({p['date']}): {p['dek']}")
        d = dt.datetime.fromisoformat(p["date"] + "T12:00:00+00:00").strftime("%a, %d %b %Y %H:%M:%S +0000")
        items.append(f"<item><title>{html.escape(p['h1'])}</title><link>{C.SITE}/blog/{p['slug']}</link>"
                     f"<guid>{C.SITE}/blog/{p['slug']}</guid><pubDate>{d}</pubDate><description>{html.escape(plain(p['dek']))}</description></item>")
    (MD / "blog.md").write_text("\n".join(idx_md) + "\n")
    feed = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>SVG to Slides blog</title>'
            f"<link>{C.SITE}/blog</link><description>Design notes for Google Slides and Docs.</description>"
            + "".join(items) + "</channel></rss>\n")
    (STATIC / "blog" / "feed.xml").write_text(feed)

def main():
    MD.mkdir(exist_ok=True)
    index = (STATIC / "index.html").read_text()
    css = re.search(r"<style>(.*?)</style>", index, re.S).group(1)
    head_icons = ('  <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32.png">\n'
                  '  <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">\n')

    # 1. landing pages
    for p in C.PAGES:
        doc = landing_html(p, css, head_icons)
        doc = set_meta(doc, "/" + p["slug"], md=f"/{p['slug']}.md")
        doc = tag_ctas(doc, p["slug"])
        doc = add_sitejs(doc)
        (STATIC / f"{p['slug']}.html").write_text(doc)
        (MD / f"{p['slug']}.md").write_text(landing_md(p))

    build_blog(css, head_icons)

    # 2. existing pages
    md_for = {"index.html": "/index.md", "guide.html": "/guide.md", "convert.html": "/convert.md"}
    camp = {"index.html": "home", "guide.html": "guide", "convert.html": "convert", "features.html": "features",
            "support.html": "support", "privacy.html": "privacy", "terms.html": "terms", "chrome.html": "chrome", "addon.html": "addon"}
    for fname, meta in C.EXISTING.items():
        f = STATIC / fname
        doc = f.read_text()
        doc = set_analytics(doc)
        doc = set_meta(doc, meta["path"], meta.get("title"), meta.get("desc"), meta.get("noindex", False), md_for.get(fname))
        if fname == "index.html":
            doc = set_ld(doc, [software_ld(), {"@context": "https://schema.org", "@type": "WebSite", "name": "SVG to Slides", "url": C.SITE + "/"}])
            doc = set_guides(doc)
        elif fname == "guide.html":
            doc = doc.replace("<h1>SVG vs PNG in Google Slides</h1>", "<h1>SVG in Google Slides: vector vs. flattened PNG</h1>")
            doc = doc.replace("Yes, all three surfaces are free.", "Yes. " + C.FREE_LINE)
            doc = doc.replace('<p><strong>Try it on your own SVG</strong> — no account needed for the web app.</p>\n    <a href="/">Open svgslid.es →</a>',
                              f'<p><strong>Try it on your own SVG.</strong> {C.FREE_LINE}</p>\n    <a href="{C.CWS}">Add to Chrome — free →</a> &nbsp; <a href="/convert">Or convert online →</a>')
        if fname == "convert.html":
            doc = doc.replace('<h1 style="margin:0">svgslid.es</h1>', '<h1 style="margin:0">SVG to Google Slides converter</h1>')
            if "cta-ext" not in doc:
                doc = doc.replace('<p class="tagline">SVG files &rarr; editable vector shapes in Google Slides</p>',
                                  '<p class="tagline">SVG files &rarr; editable vector shapes in Google Slides</p>\n'
                                  f'  <p class="tagline cta-ext">Rather drop files straight onto a slide? <a href="{C.CWS}">Get the free Chrome extension &rarr;</a></p>')
            doc = set_ld(doc, [software_ld(), faq_ld(GUIDE_FAQ), crumbs_ld("SVG vs PNG in Google Slides", "/guide")])
            doc = set_guides(doc)
        elif fname == "convert.html":
            doc = set_ld(doc, [software_ld(), crumbs_ld("SVG to Google Slides converter", "/convert")])
        if fname != "chrome.html":  # chrome.html's CWS link is a JS redirect, leave its target bare
            doc = tag_ctas(doc, camp[fname])
        doc = add_sitejs(doc)
        f.write_text(doc)

    # 3. markdown for agents
    (MD / "index.md").write_text(C.HOME_MD.format(cws=C.CWS, site=C.SITE))
    gmd = GUIDE_MD.format(site=C.SITE, cws=C.CWS) + "\n".join(f"\n### {q}\n{a}" for q, a in GUIDE_FAQ) + "\n"
    (MD / "guide.md").write_text(gmd)
    (MD / "convert.md").write_text(CONVERT_MD.format(site=C.SITE, cws=C.CWS, free=C.FREE_LINE))

    # 4. sitemap
    urls = [("/", "1.0"), ("/convert", "0.8"), ("/guide", "0.8")] + [("/" + p["slug"], "0.8") for p in C.PAGES] + \
           [("/blog", "0.7")] + [(f"/blog/{p['slug']}", "0.7") for p in B.POSTS] + \
           [("/features", "0.5"), ("/support", "0.4"), ("/privacy", "0.2"), ("/terms", "0.2")]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{C.SITE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>" for u, pr in urls]
    sm.append("</urlset>")
    (STATIC / "sitemap.xml").write_text("\n".join(sm) + "\n")

    # 5. robots
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot",
            "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "CCBot"]
    robots = ["# svgslid.es — all public pages are open to search engines and AI agents.", "User-agent: *", "Allow: /",
              "Disallow: /cleanup", "Disallow: /insert-svg-clip", "Disallow: /insert-svg-clip-at", ""]
    for b in bots:
        robots += [f"User-agent: {b}", "Allow: /", ""]
    robots += [f"Sitemap: {C.SITE}/sitemap.xml", ""]
    (STATIC / "robots.txt").write_text("\n".join(robots))

    # 6. llms.txt / llms-full.txt
    llms = [
        "# SVG to Slides", "",
        "> Free Chrome extension (plus online converter and Google Slides add-on) that inserts SVG files into Google Slides as native, editable shapes. " + C.FREE_LINE, "",
        "Google Slides doesn't keep SVG files as editable vectors. SVG to Slides converts every SVG path into its own native Slides shape, so users can recolor individual elements, edit points, animate shapes, and resize without losing quality. The shapes also work in Google Drawings.", "",
        f"- Install (Chrome Web Store): {C.CWS}",
        f"- Online converter, no install: {C.SITE}/convert", "",
        "## Docs",
        f"- [Overview]({C.SITE}/index.md): what it does, how it works, limits",
        f"- [SVG vs PNG in Google Slides]({C.SITE}/guide.md): what flattening costs, three ways to convert, FAQ",
    ]
    llms += [f"- [{plain(p['nav'])}]({C.SITE}/{p['slug']}.md): {plain(p['answer'])}" for p in C.PAGES]
    llms += [f"- [Online converter]({C.SITE}/convert.md): upload SVGs, get a Slides-ready Drive file", "",
             "## Blog"] + [f"- [{p['h1']}]({C.SITE}/blog/{p['slug']}.md): {plain(p['dek'])}" for p in B.POSTS] + ["",
             "## Optional",
             f"- [Privacy policy]({C.SITE}/privacy): per-surface data handling",
             f"- [Support]({C.SITE}/support)",
             f"- [Full text of all docs]({C.SITE}/llms-full.txt)", ""]
    (STATIC / "llms.txt").write_text("\n".join(llms))
    full = [(MD / "index.md").read_text(), (MD / "guide.md").read_text(), (MD / "convert.md").read_text()]
    full += [(MD / f"{p['slug']}.md").read_text() for p in C.PAGES]
    full += [(MD / "blog" / f"{p['slug']}.md").read_text() for p in B.POSTS]
    (STATIC / "llms-full.txt").write_text("\n\n---\n\n".join(full))

    # 7. 404
    nf = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
{analytics_block()}<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Page not found — SVG to Slides</title>
<link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
<link href="https://fonts.googleapis.com/css2?family=Overpass:wght@600&display=swap" rel="stylesheet">
<style>{css}</style></head>
<body><main class="wrap close"><h1>Page not found.</h1><p class="lede" style="margin:20px auto 30px">That page doesn&rsquo;t exist. Here&rsquo;s where to go instead.</p>
<div class="ctas"><a class="btn btn-primary" href="{C.CWS}?utm_source=svgslid.es&amp;utm_medium=web&amp;utm_campaign=404&amp;utm_content=hero" data-cta="hero"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome &mdash; free</a><a class="btn btn-ghost" href="/">Home</a></div></main>
<script src="/static/site.js" defer></script></body></html>
"""
    (STATIC / "404.html").write_text(nf)
    print("built", len(C.PAGES), "landing pages; GA:", GA_ID or "(none)")

if __name__ == "__main__":
    main()
