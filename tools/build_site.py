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

def crumbs_multi(items):
    out = [{"@type": "ListItem", "position": 1, "name": "SVG to Slides", "item": C.SITE + "/"}]
    out += [{"@type": "ListItem", "position": i + 2, "name": plain(n), "item": C.SITE + u} for i, (n, u) in enumerate(items)]
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": out}

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

# ------------------------------------------------------------- homepage FAQ
HOME_FAQ_CSS = ("  <style>/* homefaq */.hfaq{padding-block:72px}.hfaq h2{text-align:center;margin-bottom:28px}"
                ".hfaq .faq{max-width:46em;margin:0 auto}.hfaq details{border-bottom:1px solid var(--rule);padding:16px 0}"
                ".hfaq summary{cursor:pointer;font:600 18px var(--display)}.hfaq details p{color:var(--mute);margin-top:10px;font-size:15px}"
                ".hfaq .gl{max-width:46em;margin:36px auto 0;display:flex;flex-wrap:wrap;gap:10px;justify-content:center;list-style:none;padding:0}"
                ".hfaq .gl a{display:block;border:1.5px solid var(--rule);border-radius:999px;padding:8px 16px;text-decoration:none;font-size:14px}"
                ".hfaq .gl a:hover{border-color:var(--mute)}</style>\n")

def set_home_faq(doc):
    doc = re.sub(r"  <!-- homefaq:start -->.*?<!-- homefaq:end -->\n\n?", "", doc, flags=re.S)
    doc = re.sub(r"  <style>/\* homefaq \*/.*?</style>\n", "", doc, flags=re.S)
    qa = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in C.HOME_FAQ)
    links = "".join(f'<li><a href="/guides/{s}">{t}</a></li>' for s, t in C.HOME_GUIDE_LINKS)
    block = (f'  <!-- homefaq:start -->\n  <section class="wrap hfaq" id="faq"><h2>{C.HOME_FAQ_H2}</h2>'
             f'<div class="faq">{qa}</div><ul class="gl" aria-label="Guides">{links}</ul></section>\n'
             f'  <div class="wrap"><hr class="rule"></div>\n  <!-- homefaq:end -->\n')
    anchor = '  <ul class="wrap trust"'
    doc = doc.replace(anchor, block + "\n" + anchor, 1)
    return doc.replace("</head>", HOME_FAQ_CSS + "</head>", 1)

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
.gfig{max-width:46em;margin:32px auto 0} .gfig img{width:100%;height:auto;border-radius:14px;border:1px solid var(--rule);display:block}
.olist{list-style:decimal;padding-left:1.4em} .olist li::marker{font-family:var(--display);font-weight:700;color:var(--fg)}
.secnote{max-width:46em;margin:18px auto 0;color:var(--mute);font-size:15px}
@media (max-width:760px){ .cards3{grid-template-columns:1fr} }
"""

def OG(slug):
    if (STATIC / "guides" / "img" / f"{slug}.png").exists():
        return f"{C.SITE}/static/guides/img/{slug}.png"
    return f"{C.SITE}/static/og-image.png"

def figure(p):
    slug = p["slug"]
    if not p.get("img_alt") or not (STATIC / "guides" / "img" / f"{slug}.png").exists():
        return ""
    return (f'    <figure class="gfig"><picture><source type="image/webp" srcset="/static/guides/img/{slug}.webp">'
            f'<img src="/static/guides/img/{slug}.png" width="1200" height="630" alt="{esc(p["img_alt"])}" loading="lazy" decoding="async"></picture></figure>\n')

VB = {"svgslides_recolor.json": ' data-viewbox="0 0 2080 1440" style="aspect-ratio:2080/1440"'}

def landing_html(p, css, head_icons):
    slug, path = p["slug"], "/guides/" + p["slug"]
    cta = lambda pos, label="Add to Chrome &mdash; free": (
        f'<a class="btn btn-primary" href="{C.CWS}"><img src="/static/chrome-glyph.svg" alt="">{label}</a>')
    body = []
    if p.get("howto"):
        steps = "".join(f'<div class="step"><div class="n">Step {i+1}</div><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(p["howto"]))
        body.append(f'<section class="wrap steps" id="how"><h2>How to do it</h2><div class="steprow">{steps}</div></section>')
    if p.get("table"):
        th, heads, trs = p["table"]
        hrow = "".join(f"<th>{h}</th>" for h in heads)
        rows = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in trs)
        body.append(f'<section class="wrap sec"><h2>{th}</h2><table class="cmp"><thead><tr>{hrow}</tr></thead><tbody>{rows}</tbody></table></section>')
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
    for sec in p.get("sections", []):
        h, items = sec[0], sec[1]
        lis = "".join(f"<li>{x}</li>" for x in items)
        tag = "ol" if len(sec) > 2 and sec[2] == "ol" else "ul"
        note = f'<p class="secnote">{sec[3]}</p>' if len(sec) > 3 else ""
        body.append(f'<section class="wrap sec"><h2>{h}</h2><{tag} class="list{" olist" if tag == "ol" else ""}">{lis}</{tag}>{note}</section>')
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in p["faq"])
    body.append(f'<section class="wrap sec"><h2>Questions</h2><div class="faq">{faq}</div></section>')
    rel = {x["slug"]: x for x in C.PAGES}
    links = "".join(f'<a href="/guides/{s}">{rel[s]["nav"]}</a>' for s in p["related"] if s in rel)
    body.append(f'<section class="wrap sec"><h2>Related guides</h2><nav class="related" aria-label="Related guides">{links}<a href="/guides">All guides &rarr;</a></nav></section>')
    rule = '\n  <div class="wrap"><hr class="rule"></div>\n  '
    lds = [software_ld(), faq_ld(p["faq"]), crumbs_multi([("Guides", "/guides"), (p["nav"], path)])]
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
  <meta property="og:image" content="{OG(slug)}">
  <meta property="og:url" content="{C.SITE}{path}">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(p["title"])}">
  <meta name="twitter:description" content="{esc(p["desc"])}">
  <meta name="twitter:image" content="{OG(slug)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Overpass:wght@600;700;800&display=swap" rel="stylesheet">
<style>{css}{EXTRA_CSS}{P.SHELL_CSS}</style>
{ld_block(lds)}</head>
<body>
{P.nav_html(slug, LOGO_SVG)}
<div class="wrap"><p class="crumb"><a href="/">SVG to Slides</a> &rsaquo; <a href="/guides">Guides</a> &rsaquo; {p["nav"]}</p></div>
<main>
  <section class="wrap hero">
    <h1>{p["h1"]}</h1>
    <p class="lede">{p["lede"]}</p>
    <div class="ctas">
      {cta("hero")}
      <a class="btn btn-ghost" href="/convert">Convert online instead</a>
    </div>
    <p class="free">{C.FREE_LINE}</p>
    <div class="shot"><div class="lot" data-lottie="/static/lottie/{p["lottie"]}"{VB.get(p["lottie"], "")}></div></div>
    <p class="answer"><b>Short answer:</b> {p["answer"]}</p>
{figure(p)}  </section>
  <div class="wrap"><hr class="rule" style="margin-top:56px"></div>
  {rule.join(body)}
  <div class="wrap"><hr class="rule"></div>
  <section class="wrap close">
    <h2>Bring your SVGs into Google Slides&trade;.</h2>
    {cta("close")}
    <p class="free" style="margin-top:16px">{C.FREE_LINE}</p>
  </section>
</main>
{P.footer_html(LOGO_SVG)}
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
    if p.get("table"):
        th, heads, trs = p["table"]
        out += [f"## {plain(th)}", "", "| " + " | ".join(plain(h) for h in heads) + " |", "|" + "---|" * len(heads)]
        out += ["| " + " | ".join(plain(c) for c in r) + " |" for r in trs] + [""]
    for sec in p.get("sections", []):
        h, items = sec[0], sec[1]
        ol = len(sec) > 2 and sec[2] == "ol"
        out += [f"## {plain(h)}"] + [(f"{i+1}. " if ol else "- ") + plain(x) for i, x in enumerate(items)]
        out += ([plain(sec[3])] if len(sec) > 3 else []) + [""]
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
    var a=lottie.loadAnimation({container:el,renderer:'svg',loop:true,autoplay:false,path:el.dataset.lottie,rendererSettings:Object.assign({preserveAspectRatio:'xMidYMid meet'},el.dataset.viewbox?{viewBoxSize:el.dataset.viewbox}:{})});
    if(el.dataset.viewbox){a.addEventListener('DOMLoaded',function(){var g=el.querySelector('svg > g[clip-path]'); if(g) g.removeAttribute('clip-path');});}
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
import site_pages as P
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
.jump{display:flex;gap:12px;align-items:center;margin:0 0 26px;padding:13px 16px;border-radius:12px;background:#fff6d6;border:1px solid #f5d67a;color:var(--fg)!important;text-decoration:none!important;font-size:15px;line-height:1.45}
.jump b{font-family:var(--display);font-weight:800}
.jump .ar{flex:none;width:28px;height:28px;border-radius:50%;background:var(--yellow);display:grid;place-items:center;font-weight:800}
.jump:hover{border-color:var(--yellow)}
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

PRODUCTS = {  # key: (label, chip bg, chip text, text colour on white)
    "slides": ("Google Slides", "#F4B400", "#1C1E22", "#8A5A00"),
    "sheets": ("Google Sheets", "#188038", "#FFFFFF", "#137333"),
    "gemini": ("Gemini", "#3B5BDB", "#FFFFFF", "#3B5BDB"),
    "studio": ("Workspace Studio", "#E8710A", "#1C1E22", "#B4500A"),
    "meet": ("Google Meet", "#00897B", "#FFFFFF", "#00796B"),
    "forms": ("Google Forms", "#7248B9", "#FFFFFF", "#6A3FB0"),
    "appsscript": ("Apps Script", "#1A73E8", "#FFFFFF", "#1967D2"),
}
BLOG_CSS += """
.pchip{display:inline-block;font-family:var(--display);font-weight:800;font-size:12px;letter-spacing:.08em;text-transform:uppercase;border-radius:999px;padding:3px 10px 2px;margin-right:10px;vertical-align:1px;background:var(--pc,#f9c80e);color:var(--pci,#1c1e22)}
.post .kick,.pcard .kick{color:var(--pct,var(--blue))}
.post .kick .pchip{display:table;margin:0 0 10px}
.pcard .crow{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;margin:0 0 8px}.pcard .crow .pchip{margin:0}.pcard .crow .dt{font-size:13px;color:var(--mute)}
.post .crumb{margin-bottom:12px!important}
.post .tldr{border-left-color:var(--pc,var(--yellow))}
.post ol.steps li::before{background:var(--pc,var(--yellow));color:var(--pci,#1c1e22)}
.pcard{border-top:5px solid var(--pc,var(--rule))}
.pcard+.pcard{margin-top:22px}
.upd{display:block;font-size:14px;color:var(--mute);margin:-18px 0 26px}
.rel{margin:44px 0 0}.rel h2{font-size:20px;margin:0 0 12px}
.rel a.rc{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;padding:12px 0;border-top:1px solid var(--rule);text-decoration:none;color:var(--fg);min-width:0}
.rel a.rc b{order:3;flex:1 1 100%;min-width:0;overflow-wrap:anywhere;line-height:1.35}
.rel a.rc:hover b{text-decoration:underline}
.rel a.rc .pchip{order:1;flex:none;font-size:10.5px;margin-right:0}
.rel a.rc span.d{order:2;margin-left:auto;flex:none;font-size:13px;color:var(--mute)}
.legend{display:flex;flex-wrap:wrap;gap:8px;margin:-14px 0 30px}
.legend .pchip{margin:0}
.post pre{background:var(--tint);border-radius:10px;padding:14px 16px;font-size:13.5px;line-height:1.55;white-space:pre-wrap;overflow-wrap:anywhere;margin:0 0 1.05em}
.post table.t{border-collapse:collapse;width:100%;font-size:15px;margin:0 0 1.2em}
.post table.t th,.post table.t td{border-bottom:1px solid var(--rule);padding:8px 10px;text-align:left;vertical-align:top}
.post table.t th{font-family:var(--display);font-weight:800;font-size:14px}
.post pre.code{background:#1C1E22;color:#E6E6E6;border-radius:12px;padding:16px 18px;font:13px/1.6 "Roboto Mono",ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre;overflow-x:auto;margin:0 0 1.2em}
.post pre.code .kw{color:#C792EA}.post pre.code .st{color:#C3E88D}.post pre.code .nu{color:#F78C6C}.post pre.code .fn{color:#82AAFF}
.post pre.code .cl{color:#FFCB6B}.post pre.code .pr{color:#89DDFF}.post pre.code .cm{color:#7F848E;font-style:italic}
.deckembed{width:min(940px,100vw);position:relative;left:50%;transform:translateX(-50%);margin:30px 0 0}
.deckembed .fr{position:relative;width:100%;padding-top:calc(56.25% + 29px);background:#1c1e22;border-radius:14px;overflow:hidden;border:1px solid var(--rule)}
.deckembed iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
@media (max-width:700px){.deckembed .fr{border-radius:0;border-left:0;border-right:0}}
.deckacts{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 30px}
.deckacts a,.deckacts button{display:inline-flex;align-items:center;gap:8px;font:600 15px var(--body);border:1.5px solid var(--rule);background:#fff;color:var(--fg)!important;text-decoration:none!important;border-radius:999px;padding:9px 16px;cursor:pointer}
.deckacts a:hover,.deckacts button:hover{border-color:var(--mute)}
.deckacts .pri{background:var(--pc,#0066ff);border-color:var(--pc,#0066ff);color:var(--pci,#fff)!important}
.cheat{display:flex;gap:18px;align-items:center;border:1px solid var(--rule);border-radius:16px;padding:18px 20px;margin:26px 0}
.cheat img{width:120px;height:auto;border:1px solid var(--rule);border-radius:6px;flex:none}
.cheat p{margin:0 0 10px}
@media (max-width:560px){.cheat{flex-direction:column;align-items:flex-start}}
.tease{background:#1c1e22;color:#fff;border-radius:16px;padding:22px 24px;margin:34px 0}
.tease h2{color:#fff;margin:0 0 10px!important}.tease ul{margin:0}.tease p{color:#c4c7cc}
"""

def pvars(p):
    k = p.get("product")
    if k not in PRODUCTS:
        return ""
    _, bg, ink, txt = PRODUCTS[k]
    return f' style="--pc:{bg};--pci:{ink};--pct:{txt}"'

def pchip(p):
    k = p.get("product")
    return f'<span class="pchip">{PRODUCTS[k][0]}</span>' if k in PRODUCTS else ""

def related_html(p):
    by = {q["slug"]: q for q in B.POSTS}
    rows = []
    for slug in p.get("related", []):
        q = by.get(slug)
        if not q:
            continue
        rows.append(f'<a class="rc" href="/blog/{slug}"{pvars(q)}>{pchip(q)}<b>{q["h1"]}</b><span class="d">{q["date_h"]}</span></a>')
    return f'<section class="rel"><h2>Related posts</h2>{"".join(rows)}</section>' if rows else ""

def blog_webp():
    for png in BLOG_IMG.glob("*.png"):
        wp = png.with_suffix(".webp")
        if not wp.exists() or wp.stat().st_mtime < png.stat().st_mtime:
            Image.open(png).save(wp, "WEBP", quality=86, method=6)

def fig(name, alt, cap, hero=False):
    w, h = Image.open(BLOG_IMG / f"{name}.png").size
    lazy = '' if hero else ' loading="lazy"'
    pic = (f'<picture><source type="image/webp" srcset="/static/blog/img/{name}.webp">'
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
{P.nav_html(campaign, LOGO_SVG)}
<main>
{body}
</main>
{P.footer_html(LOGO_SVG)}
<script src="/static/site.js" defer></script>
</body>
</html>
"""

def jump(p):
    j = p.get("jump")
    if not j:
        return ""
    return f'<a class="jump" href="#{j[0]}"><span class="ar" aria-hidden="true">&darr;</span><span>{j[1]}</span></a>'

def post_html(p, css, head_icons):
    path = f"/blog/{p['slug']}"
    camp = f"blog-{p['slug']}"
    body_html = FIG_RE.sub(lambda m: fig(m.group(1), m.group(2), m.group(3)), p["body"])
    tldr = "".join(f"<li>{x}</li>" for x in p["tldr"])
    src = "".join(f'<li><a href="{u}">{html.escape(t)}</a></li>' for t, u in p["sources"])
    upd = f'<span class="upd">Updated {p["updated_h"]}</span>' if p.get("updated_h") else ""
    body = f"""  <article class="post"{pvars(p)}>
    <p class="crumb" style="margin:0"><a href="/blog">Blog</a></p>
    <div class="kick">{pchip(p)}{p["kicker"]}</div>
    <h1>{p["h1"]}</h1>
    <p class="dek">{p["dek"]}</p>
    <p class="meta"><time datetime="{p["date"]}">{p["date_h"]}</time> &middot; {p["read"]} &middot; Joe Gelman</p>
    {upd}
    {jump(p)}
    {fig(p["hero"][0], p["hero"][1], "", hero=True)}
    <div class="tldr"><b class="h">TL;DR</b><ul>{tldr}</ul></div>
{body_html}
    <div class="endcta">
      <p><b>Building decks with real design assets?</b> SVG to Slides drops SVG logos and icons into Google Slides as native, editable shapes &mdash; recolor any part, no PNG blur. {C.FREE_LINE}</p>
      <a class="btn btn-primary" href="{cws(camp, 'post-end')}" data-cta="post-end"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome &mdash; free</a>
    </div>
    {related_html(p)}
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
        f'<a class="pcard" href="/blog/{p["slug"]}"{pvars(p)}><picture><source type="image/webp" srcset="/static/blog/img/{p["og"][:-4]}.webp">'
        f'<img src="/static/blog/img/{p["og"]}" width="1200" height="630" alt="{esc(p["hero"][1])}"></picture>'
        f'<div class="in"><div class="crow">{pchip(p)}<span class="dt">{p["date_h"]}</span></div><div class="kick">{p["kicker"]}</div><h2>{p["h1"]}</h2><p>{p["dek"]}</p></div></a>'
        for p in B.POSTS)
    used = []
    for p in B.POSTS:
        if p.get("product") in PRODUCTS and p["product"] not in used:
            used.append(p["product"])
    legend = "".join(f'<span class="pchip" style="--pc:{PRODUCTS[k][1]};--pci:{PRODUCTS[k][2]}">{PRODUCTS[k][0]}</span>' for k in used)
    body = f"""  <section class="bindex">
    <div class="kick">svgslid.es</div>
    <h1>Blog</h1>
    <p>Practical builds for product marketing in Google Workspace: new features, type, layout, and the Sheets, Slides and Gemini setups that keep collateral current.</p>
    <div class="legend">{legend}</div>
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

# --------------------------------------------------------- sitewide polish
LOGO_SVG = re.sub(r'<svg[^>]*>', '<svg class="logo" viewBox="0 0 384 383" aria-hidden="true" focusable="false">',
                  (STATIC / "logo.svg").read_text().strip(), count=1).replace("\n", "")
DARK_RE = re.compile(r'@media \(prefers-color-scheme: dark\)\{ :root:not\(\[data-theme="light"\]\)\{[^}]*\} \}\s*')
def sw_css():
    return ('<style id="sw">.brand svg.logo{width:40px;height:40px;display:block;flex:none}'
            '.nav .sm{display:none}@media (max-width:560px){.nav .lg{display:none}.nav .sm{display:inline}'
            '.nav .btn{padding:0 16px}.nav .brand span{display:none}}html{scroll-behavior:smooth}'
            '.bnav{display:flex;gap:22px;align-items:center}.bnav a.txt{color:#1c1e22;text-decoration:none;font-family:Overpass,Verdana,sans-serif;font-weight:700;font-size:16px}'
            '.bnav a.txt:hover{text-decoration:underline}@media (max-width:560px){.bnav{gap:14px}.bnav a.txt{font-size:15px}}'
            + P.FOOTER_CSS.replace("\n", "")
            + '@media (max-width:560px){.wrap{padding-left:max(24px,env(safe-area-inset-left,0px));padding-right:max(24px,env(safe-area-inset-right,0px))}'
              '.sfoot{padding-left:max(24px,env(safe-area-inset-left,0px));padding-right:max(24px,env(safe-area-inset-right,0px))}'
              '.post{padding-left:24px;padding-right:24px}.about{padding-left:24px;padding-right:24px}.bindex{padding-left:24px;padding-right:24px}'
              '.post figcaption{padding:0 24px}.answer{margin-left:0;margin-right:0}}'
            + '</style>')

HAND_PAGES = {"index.html", "privacy.html", "terms.html", "support.html", "features.html"}

def sitewide_polish(text):
    text = DARK_RE.sub("", text)
    text = text.replace("color-scheme:dark", "color-scheme:light")
    if 'name="color-scheme"' not in text:
        text = text.replace('<meta name="viewport"', '<meta name="color-scheme" content="light only">\n  <meta name="viewport"', 1)
    text = re.sub(r'<img src="/static/mark\.svg" alt="">', lambda m: LOGO_SVG, text)
    text = re.sub(r'(data-cta="nav"><img src="/static/chrome-glyph\.svg" alt="">)Add to Chrome</a>',
                  r'\1<span class="lg">Add to Chrome</span><span class="sm">Add</span></a>', text)
    text = re.sub(r'<style id="sw">.*?</style>\n?', "", text, flags=re.S)
    text = text.replace("</head>", sw_css() + "\n</head>", 1)
    return text

def with_footer(text):
    text = re.sub(r'\s*<footer class="wrap foot">.*?</footer>', "", text, flags=re.S)
    text = re.sub(r'<!-- sitefoot:start -->.*?<!-- sitefoot:end -->\n?', "", text, flags=re.S)
    foot = P.footer_html(LOGO_SVG) + "\n"
    if "</main>" in text:
        return text.replace("</main>", "</main>\n" + foot, 1)
    return text.replace("</body>", foot + "</body>", 1)

def latest_block():
    p = B.POSTS[0]
    return (f'<!-- latest:start --><a class="wrap latest" href="/blog/{p["slug"]}">'
            f'<picture><source type="image/webp" srcset="/static/blog/img/{p["og"][:-4]}.webp">'
            f'<img src="/static/blog/img/{p["og"]}" width="1200" height="630" alt="{esc(p["hero"][1])}" loading="lazy"></picture>'
            f'<div><div class="k">From the blog &middot; {p["kicker"]}</div><h2>{p["h1"]}</h2><p>{p["dek"]}</p>'
            f'<span class="go">Read the post &rarr;</span></div></a><!-- latest:end -->')

def polish_all():
    idx = STATIC / "index.html"
    t = idx.read_text()
    idx.write_text(re.sub(r"<!-- latest:start -->.*?<!-- latest:end -->", lambda m: latest_block(), t, flags=re.S))
    for f in list(STATIC.glob("*.html")) + list((STATIC / "blog").glob("*.html")) + list((STATIC / "guides").glob("*.html")) + list((STATIC / "_lobby").glob("*.html")):
        t = f.read_text()
        n = sitewide_polish(t)
        if f.parent == STATIC and f.name in HAND_PAGES:
            n = with_footer(n)
            if f.name == "index.html":  # hand-built nav -> shared nav
                nav = re.search(r'<nav class="nav">.*?</nav>', P.nav_html("home", LOGO_SVG), re.S).group(0)
                n = re.sub(r'<nav class="nav">.*?</nav>', lambda m: nav, n, count=1, flags=re.S)
        if n != t:
            f.write_text(n)

def main():
    import json, shutil
    MD.mkdir(exist_ok=True)
    index = (STATIC / "index.html").read_text()
    css = re.search(r"<style>(.*?)</style>", index, re.S).group(1)
    head_icons = ('  <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32.png">\n'
                  '  <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">\n')
    ctx = {"common": {"css": css, "head_icons": head_icons, "analytics": analytics_block(), "logo_svg": LOGO_SVG},
           "ld_block": ld_block, "crumbs": crumbs_multi, "software_ld": software_ld, "lottie_js": LOTTIE_JS,
           "extra_css": EXTRA_CSS}

    # 0. retire old flat URLs (301s come from redirects.json)
    for old in ["guide.html", "convert.html.bak"] + [f"{p['slug']}.html" for p in C.PAGES]:
        (STATIC / old).unlink(missing_ok=True)
    for old in ["guide.md"] + [f"{p['slug']}.md" for p in C.PAGES]:
        (MD / old).unlink(missing_ok=True)

    # 1. guides
    (STATIC / "guides").mkdir(exist_ok=True)
    (MD / "guides").mkdir(exist_ok=True)
    for p in C.PAGES:
        path = f"/guides/{p['slug']}"
        doc = landing_html(p, css, head_icons)
        doc = set_meta(doc, path, md=f"{path}.md")
        doc = tag_ctas(doc, p["slug"])
        doc = add_sitejs(doc)
        (STATIC / "guides" / f"{p['slug']}.html").write_text(doc)
        (MD / "guides" / f"{p['slug']}.md").write_text(landing_md(p))
    lobby, lobby_md = P.guides_lobby(ctx, B.POSTS)
    (STATIC / "guides" / "index.html").write_text(lobby)
    (MD / "guides.md").write_text(lobby_md)
    # one prebuilt lobby per possible featured guide; main.py picks one per request
    lob = STATIC / "_lobby"
    shutil.rmtree(lob, ignore_errors=True)
    lob.mkdir()
    for p in C.PAGES:
        (lob / f"{p['slug']}.html").write_text(P.guides_lobby(ctx, B.POSTS, p["slug"], "auto")[0])
    feat, source = P.featured_slug()
    (lob / "featured.json").write_text(json.dumps({"override": feat if source == "override" else None,
                                                   "default": C.DEFAULT_FEATURED,
                                                   "guides": [p["slug"] for p in C.PAGES]}) + "\n")

    # 2. blog, converter, about
    build_blog(css, head_icons)
    (STATIC / "convert.html").write_text(P.convert_page(ctx))
    (MD / "convert.md").write_text(P.CONVERT_MD.format(site=C.SITE, cws=C.CWS, free=C.FREE_LINE))
    (STATIC / "google-slides-addon.html").write_text(P.addon_page(ctx))
    (MD / "google-slides-addon.md").write_text(P.ADDON_MD.format(site=C.SITE, cws=C.CWS, free=C.FREE_LINE))
    about, about_md = P.about_page(ctx)
    (STATIC / "about.html").write_text(about)
    (MD / "about.md").write_text(about_md)

    # 3. hand-maintained pages
    camp = {"index.html": "home", "features.html": "features", "support.html": "support",
            "privacy.html": "privacy", "terms.html": "terms", "chrome.html": "chrome", "addon.html": "addon"}
    for fname, meta in C.EXISTING.items():
        if fname not in camp:
            continue
        f = STATIC / fname
        doc = f.read_text()
        doc = set_analytics(doc)
        doc = set_meta(doc, meta["path"], meta.get("title"), meta.get("desc"), meta.get("noindex", False),
                       "/index.md" if fname == "index.html" else None)
        if fname == "index.html":
            doc = set_home_faq(doc)
            doc = set_ld(doc, [software_ld(), {"@context": "https://schema.org", "@type": "WebSite", "name": "SVG to Slides", "url": C.SITE + "/"},
                               faq_ld(C.HOME_FAQ)])
            doc = re.sub(r"  <!-- guides:start -->.*?<!-- guides:end -->\n", "", doc, flags=re.S)
        if fname != "chrome.html":  # chrome.html's CWS link is a JS redirect, leave its target bare
            doc = tag_ctas(doc, camp[fname])
        doc = add_sitejs(doc)
        f.write_text(doc)
    home_faq_md = "\n\n".join(f"### {plain(q)}\n{plain(a)}" for q, a in C.HOME_FAQ)
    (MD / "index.md").write_text(C.HOME_MD.format(cws=C.CWS, site=C.SITE, faq=home_faq_md))

    # 4. redirects (old flat URLs -> /guides/...), served as 301 by main.py
    redirects = dict(C.LEGACY)
    redirects.update({k + ".md": v + ".md" for k, v in C.LEGACY.items()})
    (STATIC / "redirects.json").write_text(json.dumps(redirects, indent=1, sort_keys=True) + "\n")

    # 5. sitemap
    urls = [("/", "1.0"), ("/convert", "0.8"), ("/google-slides-addon", "0.8"), ("/guides", "0.9")] + [(f"/guides/{p['slug']}", "0.8") for p in C.PAGES] + \
           [("/blog", "0.7")] + [(f"/blog/{p['slug']}", "0.7") for p in B.POSTS] + \
           [("/about", "0.5"), ("/support", "0.4"), ("/privacy", "0.2"), ("/terms", "0.2")]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{C.SITE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>" for u, pr in urls]
    sm.append("</urlset>")
    (STATIC / "sitemap.xml").write_text("\n".join(sm) + "\n")

    # 6. robots
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot",
            "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "CCBot"]
    robots = ["# svgslid.es: all public pages are open to search engines and AI agents.", "User-agent: *", "Allow: /",
              "Disallow: /cleanup", "Disallow: /insert-svg-clip", "Disallow: /insert-svg-clip-at", "Disallow: /static/_lobby/", ""]
    for b in bots:
        robots += [f"User-agent: {b}", "Allow: /", ""]
    robots += [f"Sitemap: {C.SITE}/sitemap.xml", ""]
    (STATIC / "robots.txt").write_text("\n".join(robots))

    # 7. llms.txt / llms-full.txt
    llms = [
        "# SVG to Slides", "",
        "> Free Chrome extension (plus web uploader and Google Slides add-on) that inserts SVG files into Google Slides as native, editable shapes. " + C.FREE_LINE, "",
        "Google Slides doesn't keep SVG files as editable vectors. SVG to Slides converts every SVG path into its own native Slides shape, so users can recolor individual elements, edit points, animate shapes, and resize without losing quality. The shapes also work in Google Drawings.", "",
        f"- Install (Chrome Web Store): {C.CWS}",
        f"- Web uploader, no install: {C.SITE}/convert", "",
        "## Docs",
        f"- [Overview]({C.SITE}/index.md): what it does, how it works, limits",
        f"- [Guides index]({C.SITE}/guides.md)",
    ]
    llms += [f"- [{plain(p['nav'])}]({C.SITE}/guides/{p['slug']}.md): {plain(p['answer'])}" for p in C.PAGES]
    llms += [f"- [Web uploader]({C.SITE}/convert.md): upload SVGs, get a Slides-ready Drive file",
             f"- [Google Slides add-on]({C.SITE}/google-slides-addon.md): insert SVGs from a dialog inside Slides", "",
             "## Blog"] + [f"- [{p['h1']}]({C.SITE}/blog/{p['slug']}.md): {plain(p['dek'])}" for p in B.POSTS] + ["",
             "## Optional",
             f"- [About]({C.SITE}/about.md)",
             f"- [Privacy policy]({C.SITE}/privacy): per-surface data handling",
             f"- [Support]({C.SITE}/support)",
             f"- [Full text of all docs]({C.SITE}/llms-full.txt)", ""]
    (STATIC / "llms.txt").write_text("\n".join(llms))
    full = [(MD / "index.md").read_text(), (MD / "convert.md").read_text()]
    full += [(MD / "guides" / f"{p['slug']}.md").read_text() for p in C.PAGES]
    full += [(MD / "blog" / f"{p['slug']}.md").read_text() for p in B.POSTS]
    full += [(MD / "about.md").read_text()]
    (STATIC / "llms-full.txt").write_text("\n\n---\n\n".join(full))

    # 8. 404
    nf_body = f"""  <section class="wrap close" style="padding-top:80px"><h1>Page not found.</h1><p class="lede" style="margin:20px auto 30px">That page doesn&rsquo;t exist. Here&rsquo;s where to go instead.</p>
  <div class="ctas"><a class="btn btn-primary" href="{P.cws('404', 'hero')}" data-cta="hero"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome, free</a><a class="btn btn-ghost" href="/guides">Browse guides</a></div></section>"""
    nf = P.shell(title="Page not found | SVG to Slides", desc="Page not found.", path="/404", body=nf_body, campaign="404",
                 ld_block="", **ctx["common"]).replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n  <meta name="viewport"', 1)
    (STATIC / "404.html").write_text(nf)
    polish_all()
    print("built", len(C.PAGES), "guides; featured:", P.featured_slug(), "; GA:", GA_ID or "(none)")

if __name__ == "__main__":
    main()
