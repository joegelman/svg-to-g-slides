"""Shared chrome (nav, footer, page shell) and the generated hub pages:
/guides (lobby), /convert (online converter), /about.

Imported by build_site.py, which passes in the helpers it owns.
"""
import html
import json
import re
from pathlib import Path

import site_content as C

ROOT = Path(__file__).resolve().parent.parent
FEATURED_FILE = ROOT / "tools" / "featured.json"


def cws(campaign, pos):
    return f"{C.CWS}?utm_source=svgslid.es&amp;utm_medium=web&amp;utm_campaign={campaign}&amp;utm_content={pos}"


# ------------------------------------------------------------------ nav
def nav_html(campaign, logo_svg):
    return f"""<div class="wrap">
  <nav class="nav">
    <a class="brand" href="/" aria-label="SVG to Slides home">{logo_svg}<span>SVG to Slides</span></a>
    <span class="bnav"><a class="txt" href="/guides">Guides</a><a class="txt" href="/blog">Blog</a><a class="btn btn-primary" href="{cws(campaign, 'nav')}" data-cta="nav"><img src="/static/chrome-glyph.svg" alt=""><span class="lg">Add to Chrome</span><span class="sm">Add</span></a></span>
  </nav>
</div>"""


# --------------------------------------------------------------- footer
FOOTER_COLS = [
    ("Products", [("Chrome Extension", "CWS"), ("Workspace Add-on", "/google-slides-addon"), ("Web Uploader", "/convert")]),
    ("Resources", [("Guides", "/guides"), ("Specs", "/specs"), ("Blog", "/blog")]),
    ("Details", [("Privacy", "/privacy"), ("Terms", "/terms")]),
    ("About", [("About", "/about")]),
    ("Contact", [("joe@glmn.co", "mailto:joe@glmn.co"), ("Support", "/support")]),
]

FOOTER_CSS = """
.sfoot{max-width:1040px;margin:0 auto;padding:44px max(16px,env(safe-area-inset-right,0px)) 40px max(16px,env(safe-area-inset-left,0px));font-family:Verdana,Geneva,sans-serif;color:#1c1e22}
.sfoot .cols{display:grid;grid-template-columns:1.4fr repeat(5,1fr);gap:28px}
.sfoot .brandcol{display:flex;flex-direction:column;gap:10px;font-size:13px;line-height:1.5;color:#6b6f76}
.sfoot .brandcol b{font-family:Overpass,Verdana,sans-serif;font-weight:700;font-size:16px;color:#1c1e22;display:flex;align-items:center;gap:8px}
.sfoot .brandcol svg.logo{width:28px;height:28px}
.sfoot .fh{margin:0 0 12px;font:800 12px/1 Overpass,Verdana,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#6b6f76}
.sfoot ul{list-style:none;margin:0;padding:0;display:grid;gap:9px}
.sfoot a{color:#1c1e22;text-decoration:none;font-size:14px}
.sfoot a:hover{text-decoration:underline}
.sfoot .legal{margin-top:36px;padding-top:18px;border-top:1px solid #e6e7ea;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:12px;color:#6b6f76}
@media (max-width:820px){.sfoot .cols{grid-template-columns:repeat(3,1fr)}.sfoot .brandcol{grid-column:1/-1}}
@media (max-width:480px){.sfoot .cols{grid-template-columns:repeat(2,1fr)}}
"""


def footer_html(logo_svg):
    cols = []
    for head, links in FOOTER_COLS:
        lis = "".join(
            f'<li><a href="{cws("footer", "footer") if href == "CWS" else href}"'
            + (' data-cta="footer"' if href == "CWS" else "") + f">{label}</a></li>"
            for label, href in links)
        cols.append(f"<div><p class=\"fh\">{head}</p><ul>{lis}</ul></div>")
    return f"""<!-- sitefoot:start --><footer class="sfoot" aria-label="Site">
  <div class="cols">
    <div class="brandcol"><b>{logo_svg}SVG to Slides</b><span>Editable SVGs in Google Slides&trade;. {C.FREE_LINE}</span></div>
    {''.join(cols)}
  </div>
  <div class="legal"><span>&copy; 2026 svgslid.es &middot; Built by Joe Gelman</span><span>Google Slides&trade;, Google Docs&trade; and Google Drawings&trade; are trademarks of Google LLC. Not affiliated with Google.</span></div>
</footer><!-- sitefoot:end -->"""


# ----------------------------------------------------------- page shell
SHELL_CSS = """
.bnav{display:flex;gap:22px;align-items:center}
.bnav a.txt{color:var(--fg);text-decoration:none;font-family:var(--display);font-weight:700;font-size:16px}
.bnav a.txt:hover{text-decoration:underline}
@media (max-width:560px){.bnav{gap:14px}.bnav a.txt{font-size:15px}}
.kick{font-family:var(--display);font-weight:800;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--blue)}
.crumb{font-size:13px;color:var(--mute);padding-top:8px} .crumb a{color:var(--mute);text-decoration:none} .crumb a:hover{text-decoration:underline}
.phero{padding:40px 0 8px;text-align:center}
.phero h1{max-width:18ch;margin:10px auto 14px}
.phero .lede{max-width:40em;margin:0 auto}
"""


def shell(*, title, desc, path, body, css, head_icons, ld_block, analytics, campaign, logo_svg,
          md=None, og_image="https://svgslid.es/static/og-image.png", og_type="website", extra_css="", tail=""):
    md_link = f'  <link rel="alternate" type="text/markdown" href="{md}">\n' if md else ""
    e = lambda s: html.escape(re.sub(r"<[^>]+>", "", s), quote=True)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
{analytics}  <meta name="color-scheme" content="light only">
  <link rel="canonical" href="{C.SITE}{path}">
{md_link}  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{html.escape(title, quote=False)}</title>
  <meta name="description" content="{e(desc)}">
{head_icons}  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:url" content="{C.SITE}{path}">
  <meta property="og:type" content="{og_type}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Overpass:wght@600;700;800&display=swap" rel="stylesheet">
{ld_block}<style>{css}{SHELL_CSS}{extra_css}</style>
</head>
<body>
{nav_html(campaign, logo_svg)}
<main>
{body}
</main>
{footer_html(logo_svg)}
<script src="/static/site.js" defer></script>
{tail}
</body>
</html>
"""


# ------------------------------------------------------------- guides lobby
def featured_slug():
    """Static default for /guides: override (manual) > DEFAULT_FEATURED.
    The server swaps in the week's top guide at request time unless an override is set."""
    slugs = {p["slug"] for p in C.PAGES}
    try:
        f = json.loads(FEATURED_FILE.read_text())
    except (OSError, ValueError):
        f = {}
    if f.get("override") in slugs:
        return f["override"], "override"
    return C.DEFAULT_FEATURED, "default"


LOBBY_CSS = """
.feat{display:grid;grid-template-columns:1.15fr 1fr;gap:0;border-radius:22px;overflow:hidden;background:var(--tint);text-decoration:none;color:inherit;margin:36px 0 8px;transition:transform .15s,box-shadow .15s}
.feat:hover{transform:translateY(-2px);box-shadow:0 14px 36px rgba(0,0,0,.08)}
.feat .lot{aspect-ratio:16/9;background:#F9FAFD;width:100%;margin:0}
.feat .in{padding:34px 34px 30px;display:flex;flex-direction:column;gap:12px;justify-content:center}
.feat h2{font-size:clamp(26px,3vw,34px);line-height:1.1;margin:0;text-align:left}
.feat p{margin:0;color:var(--mute);font-size:16px;line-height:1.55}
.feat .go,.gcard .go{font-family:var(--display);font-weight:800;color:var(--blue);font-size:15px}
.badge{align-self:flex-start;background:var(--yellow);color:#1c1e22;border-radius:999px;padding:5px 12px;font:800 12px/1 var(--display);letter-spacing:.1em;text-transform:uppercase}
.ggroup{padding-block:44px}
.ggroup header{display:flex;justify-content:space-between;align-items:baseline;gap:16px;margin-bottom:20px;flex-wrap:wrap}
.ggroup h2{margin:0;text-align:left;font-size:clamp(24px,3vw,30px)}
.ggroup header p{margin:0;color:var(--mute);font-size:15px}
.ggrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px}
.gcard{display:flex;flex-direction:column;gap:10px;padding:24px;border:1px solid var(--rule);border-radius:18px;text-decoration:none;color:inherit;background:#fff;transition:transform .15s,box-shadow .15s,border-color .15s}
.gcard:hover{transform:translateY(-2px);box-shadow:0 10px 26px rgba(0,0,0,.07);border-color:#d8dade}
.gcard .thumb{display:block;margin:-24px -24px 6px;border-bottom:1px solid var(--rule);overflow:hidden;border-radius:17px 17px 0 0;background:#fffbea}
.gcard .thumb img{display:block;width:100%;height:auto;transition:transform .25s}
.gcard:hover .thumb img{transform:scale(1.025)}
.gcard .thumb + .e{display:none}
.gcard .e{font-size:28px;line-height:1;height:32px}
.gcard h3{margin:0;font-size:20px;line-height:1.2}
.gcard p{margin:0;color:var(--mute);font-size:14.5px;line-height:1.55;flex:1}
.gcard .meta{display:flex;justify-content:space-between;align-items:center;font-size:13px;color:var(--mute)}
.gcard.blogc{background:var(--tint);border-color:transparent}
@media (max-width:820px){.feat{grid-template-columns:1fr}.feat .in{padding:24px 22px 26px}}
@media (max-width:560px){.gcard{padding:20px}.gcard .thumb{margin:-20px -20px 6px}}
"""


def _short(p, n=150):
    t = re.sub(r"<[^>]+>", "", p["answer"])
    t = html.unescape(t)
    if len(t) <= n:
        return html.escape(t)
    cut = t[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return html.escape(cut) + "&hellip;"


GIMG = ROOT / "cloud" / "static" / "guides" / "img"


def thumb(slug):
    if not (GIMG / f"{slug}.png").exists():
        return ""
    alt = next((html.escape(p.get("img_alt", ""), quote=True) for p in C.PAGES if p["slug"] == slug), "")
    return (f'<picture class="thumb"><source type="image/webp" srcset="/static/guides/img/{slug}.webp">'
            f'<img src="/static/guides/img/{slug}.png" width="1200" height="630" alt="{alt}" loading="lazy" decoding="async"></picture>')


def guides_lobby(ctx, posts, feat=None, source="variant"):
    if feat is None:
        feat, source = featured_slug()
    by = {p["slug"]: p for p in C.PAGES}
    fp = by[feat]
    g, emoji, mins = C.GUIDE_META.get(feat, ("more", "📘", 3))
    featured = f"""<a class="feat" href="/guides/{feat}" data-featured-source="{source}">
      <div class="lot" data-lottie="/static/lottie/{fp['lottie']}"{' data-viewbox="0 0 2080 1440" style="aspect-ratio:2080/1440"' if fp['lottie'] == 'svgslides_recolor.json' else ''}></div>
      <div class="in"><span class="badge">Featured guide</span><h2>{fp['h1']}</h2><p>{_short(fp, 220)}</p><span class="go">Read the guide &rarr; <span style="color:var(--mute);font-weight:600">&middot; {mins} min</span></span></div>
    </a>"""
    groups = list(C.GUIDE_GROUPS) + [("more", "More guides", "")]
    sections = []
    for gid, gname, gdesc in groups:
        items = [p for p in C.PAGES if C.GUIDE_META.get(p["slug"], ("more",))[0] == gid]
        if not items:
            continue
        cards = "".join(
            f'<a class="gcard" href="/guides/{p["slug"]}">{thumb(p["slug"])}<span class="e" aria-hidden="true">{C.GUIDE_META.get(p["slug"], ("", "📘", 3))[1]}</span>'
            f'<h3>{p["h1"]}</h3><p>{_short(p)}</p><span class="meta"><span>{C.GUIDE_META.get(p["slug"], ("", "", 3))[2]} min read</span><span class="go">Read &rarr;</span></span></a>'
            for p in items)
        sub = f"<p>{gdesc}</p>" if gdesc else ""
        sections.append(f'<section class="wrap ggroup" id="{gid}"><header><h2>{gname}</h2>{sub}</header><div class="ggrid">{cards}</div></section>')
    blog_cards = "".join(
        f'<a class="gcard blogc" href="/blog/{b["slug"]}"><span class="kick">{b["kicker"]} &middot; {b["date_h"]}</span>'
        f'<h3>{b["h1"]}</h3><p>{b["dek"]}</p><span class="meta"><span>{b["read"]}</span><span class="go">Read &rarr;</span></span></a>'
        for b in posts[:3])
    sections.append(f'<section class="wrap ggroup" id="blog"><header><h2>From the blog</h2><p><a href="/blog">All posts &rarr;</a></p></header><div class="ggrid">{blog_cards}</div></section>')
    rule = '\n  <div class="wrap"><hr class="rule"></div>\n  '
    body = f"""  <div class="wrap"><p class="crumb"><a href="/">SVG to Slides</a> &rsaquo; Guides</p></div>
  <section class="wrap phero">
    <div class="kick">Guides</div>
    <h1>SVGs in Google Slides&trade;, start to finish.</h1>
    <p class="lede">Short, practical guides to getting vector graphics into Slides and keeping them editable.</p>
  </section>
  <section class="wrap">{featured}</section>
  {rule.join(sections)}"""
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "SVG to Slides guides", "url": C.SITE + "/guides",
           "hasPart": [{"@type": "Article", "headline": re.sub(r"<[^>]+>|&\w+;", "", p["h1"]), "url": f"{C.SITE}/guides/{p['slug']}"} for p in C.PAGES]},
          ctx["crumbs"]([("Guides", "/guides")])]
    doc = shell(title="Guides: SVGs in Google Slides | SVG to Slides",
                desc="Practical guides to inserting, converting, recolouring and reusing SVGs in Google Slides as native, editable shapes.",
                path="/guides", body=body, md="/guides.md", extra_css=LOBBY_CSS, campaign="guides",
                ld_block=ctx["ld_block"](ld), tail=ctx["lottie_js"], **ctx["common"])
    md = ["# SVG to Slides guides", "", f"Featured: [{re.sub(r'<[^>]+>|&\\w+;', '', fp['h1'])}]({C.SITE}/guides/{feat}.md)", ""]
    for gid, gname, _ in groups:
        items = [p for p in C.PAGES if C.GUIDE_META.get(p["slug"], ("more",))[0] == gid]
        if items:
            md += [f"## {gname}"] + [f"- [{re.sub(r'<[^>]+>|&\\w+;', '', p['h1'])}]({C.SITE}/guides/{p['slug']}.md): {html.unescape(re.sub(r'<[^>]+>', '', p['answer']))}" for p in items] + [""]
    return doc, "\n".join(md)


# ------------------------------------------------------------ converter
CONVERT_CSS = """
.tool{max-width:640px;margin:34px auto 0;background:#fff;border:1px solid var(--rule);border-radius:22px;padding:28px;box-shadow:0 18px 48px rgba(20,24,40,.07);text-align:left}
#dropzone{position:relative;border:2px dashed #cfd3da;border-radius:16px;background:var(--tint);padding:38px 20px;text-align:center;cursor:pointer;transition:border-color .15s,background .15s}
#dropzone:hover,#dropzone.over{border-color:var(--yellow);background:#fff6d6}
#dropzone input{position:absolute;inset:0;opacity:0;cursor:pointer}
#dropzone .ic{width:54px;height:54px;margin:0 auto 12px;border-radius:14px;background:var(--yellow);display:grid;place-items:center}
#dropzone .ic svg{width:28px;height:28px}
#dropzone p{margin:0;font-size:16px}
#dropzone small{display:block;margin-top:6px;color:var(--mute);font-size:13px}
#file-list{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.file-row{display:inline-flex;align-items:center;gap:8px;padding:6px 8px 6px 12px;border:1px solid var(--rule);border-radius:999px;font-size:13px;background:#fff;max-width:100%}
.file-row .fname{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:220px}
.file-row button{border:0;background:#f1f2f4;border-radius:50%;width:22px;height:22px;cursor:pointer;font-size:11px;line-height:22px;padding:0;color:#555}
.file-row button:hover{background:#e3e5e8}
.tool label{display:block;margin:22px 0 6px;font:700 14px var(--display)}
.tool label span{font-weight:600;color:var(--mute)}
.tool input[type=email]{width:100%;height:46px;border:1.5px solid var(--rule);border-radius:12px;padding:0 14px;font:15px var(--body);box-sizing:border-box}
.tool input[type=email]:focus{outline:none;border-color:var(--blue)}
.tool .hint{margin:8px 0 0;font-size:13px;color:var(--mute);line-height:1.5}
#submit{margin-top:22px;width:100%;height:52px;border:0;border-radius:999px;background:var(--blue);color:#fff;font:800 17px var(--display);cursor:pointer;transition:opacity .15s}
#submit:disabled{opacity:.35;cursor:not-allowed}
#status{margin-top:14px;text-align:center;font-size:14px;color:var(--mute);min-height:1px}
#status.error{color:#c62828}
#status.busy::before{content:"";display:inline-block;width:14px;height:14px;margin-right:8px;vertical-align:-2px;border:2px solid #cfd3da;border-top-color:var(--blue);border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
#result{display:none;margin-top:18px;padding:18px 20px;border-radius:14px;background:#eaf7ee;border:1px solid #bfe3c9}
#result p{margin:0 0 12px;font-size:14.5px;line-height:1.5}
#result a{display:inline-flex;align-items:center;height:42px;padding:0 18px;border-radius:999px;background:#1e8e3e;color:#fff;text-decoration:none;font:800 15px var(--display)}
.xsell{max-width:640px;margin:18px auto 0;display:flex;gap:14px;align-items:center;justify-content:space-between;padding:16px 20px;border-radius:16px;background:var(--tint);text-align:left;font-size:14.5px;line-height:1.45;flex-wrap:wrap}
.xsell b{font-family:var(--display)}
.xsell .btn{height:40px;font-size:14px;padding:0 16px}
.facts{max-width:46em;margin:0 auto;display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.facts div{padding:20px;border:1px solid var(--rule);border-radius:16px;font-size:14.5px;line-height:1.55;color:var(--mute)}
.facts b{display:block;color:var(--fg);font-family:var(--display);font-size:16px;margin-bottom:6px}
@media (max-width:760px){.facts{grid-template-columns:1fr}.tool{padding:20px}}
"""

UPLOAD_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="#1c1e22" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4"/><path d="m6 10 6-6 6 6"/><path d="M4 20h16"/></svg>'

CONVERT_JS = r"""<script>
(function(){
  const dropzone=document.getElementById('dropzone'), fileInput=document.getElementById('file-input'),
        fileList=document.getElementById('file-list'), emailInput=document.getElementById('email'),
        submitBtn=document.getElementById('submit'), statusEl=document.getElementById('status'),
        resultEl=document.getElementById('result'), resultLink=document.getElementById('result-link'),
        resultMessage=document.getElementById('result-message');
  let files=[];
  const esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  function render(){
    fileList.innerHTML='';
    files.forEach((f,i)=>{const r=document.createElement('div');r.className='file-row';
      r.innerHTML=`<span class="fname">${esc(f.name)}</span><button type="button" data-i="${i}" aria-label="Remove ${esc(f.name)}">&#10005;</button>`;fileList.appendChild(r);});
    submitBtn.disabled=!files.length;
    submitBtn.textContent=files.length>1?`Convert ${files.length} files`:'Convert';
  }
  const add=list=>{files=[...files,...[...list].filter(f=>f.name.toLowerCase().endsWith('.svg'))];render();};
  fileList.addEventListener('click',e=>{const b=e.target.closest('button[data-i]');if(b){files.splice(+b.dataset.i,1);render();}});
  fileInput.addEventListener('change',()=>{add(fileInput.files);fileInput.value='';});
  dropzone.addEventListener('dragover',e=>{e.preventDefault();dropzone.classList.add('over');});
  dropzone.addEventListener('dragleave',()=>dropzone.classList.remove('over'));
  dropzone.addEventListener('drop',e=>{e.preventDefault();dropzone.classList.remove('over');add(e.dataTransfer.files);});
  submitBtn.addEventListener('click',async()=>{
    if(!files.length)return;
    submitBtn.disabled=true;resultEl.style.display='none';statusEl.className='busy';statusEl.textContent='Converting…';
    const fd=new FormData();files.forEach(f=>fd.append('files',f));fd.append('email',emailInput.value.trim());
    try{
      const res=await fetch('/convert',{method:'POST',body:fd});const json=await res.json();
      if(!res.ok)throw new Error(json.detail||'Server error');
      statusEl.className='';statusEl.textContent='';resultLink.href=json.link;
      resultMessage.textContent=json.retention_days
        ?`Done. Your file is ready in Google Drive. The link stays active for ${json.retention_days} days; use File → Make a copy in Drive to keep it.`
        :'Done. Your file is ready in Google Drive.';
      resultEl.style.display='block';files=[];render();emailInput.value='';
      if(window.gtag)gtag('event','convert_success');
    }catch(err){statusEl.className='error';statusEl.textContent=err.message;submitBtn.disabled=false;}
  });
})();
</script>"""


def convert_page(ctx):
    body = f"""  <section class="wrap phero">
    <div class="kick">Web Uploader</div>
    <h1>Convert SVG to Google Slides&trade; online</h1>
    <p class="lede">Upload SVG files and get a Slides-ready file in Google Drive, with every path as a real, editable vector shape. One slide per SVG.</p>
    <div class="tool">
      <div id="dropzone">
        <input type="file" id="file-input" accept=".svg,image/svg+xml" multiple aria-label="Choose SVG files">
        <div class="ic" aria-hidden="true">{UPLOAD_SVG}</div>
        <p><b>Drop SVG files here</b> or click to browse</p>
        <small>Multiple files welcome. Each one becomes its own slide.</small>
      </div>
      <div id="file-list" aria-live="polite"></div>
      <label for="email">Google account <span>(optional)</span></label>
      <input type="email" id="email" placeholder="you@example.com" autocomplete="email">
      <p class="hint">If you add an address, the file is shared straight to that account. Either way, the link stays active for 7 days.</p>
      <button id="submit" disabled>Convert</button>
      <div id="status" role="status"></div>
      <div id="result"><p id="result-message">Done. Your file is ready in Google Drive.</p><a id="result-link" href="#" target="_blank" rel="noopener">Open in Drive &#8599;</a></div>
    </div>
    <div class="xsell"><span><b>Working in a deck already?</b> The Chrome extension drops SVGs straight onto your slide.</span><a class="btn btn-primary" href="{cws('convert', 'xsell')}" data-cta="xsell"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome</a></div>
  </section>
  <div class="wrap"><hr class="rule" style="margin-top:56px"></div>
  <section class="wrap steps" id="how"><h2>How it works</h2><div class="steprow">
    <div class="step"><div class="n">Step 1</div><h3>Upload your SVGs.</h3><p>Drop one file or a batch. Each SVG becomes one slide.</p></div>
    <div class="step"><div class="n">Step 2</div><h3>Get a Drive link.</h3><p>Every <code>&lt;path&gt;</code> becomes its own native shape, not a flattened image.</p></div>
    <div class="step"><div class="n">Step 3</div><h3>Make a copy to keep it.</h3><p>In Drive, choose File &rarr; Make a copy. The copy is yours, with no expiry.</p></div>
  </div></section>
  <div class="wrap"><hr class="rule"></div>
  <section class="wrap sec"><h2>Good to know</h2><div class="facts">
    <div><b>7-day links</b>Converted files are deleted after 7 days. Make a copy in Drive to keep one.</div>
    <div><b>Gradients kept</b>Solid fills, strokes and gradients come through. Arcs are converted into smooth curves.</div>
    <div><b>Free, no account</b>{C.FREE_LINE}</div>
  </div></section>
  <div class="wrap"><hr class="rule"></div>
  <section class="wrap sec"><h2>What the online converter keeps</h2><ul class="list">
    <li>Paths, basic shapes, arcs, transforms and even-odd cut-outs become native Slides shapes.</li>
    <li>Gradients stay gradients. Text is outlined into shapes, so it keeps its look but isn't editable text.</li>
    <li>Strokes become filled outline shapes, including line icons that set the stroke on the whole SVG.</li>
    <li>Clip paths, masks, patterns, filters and transparency don't come through. <a href="/specs#compatibility">See results for 20 tested SVG features</a>.</li>
  </ul></section>
  <div class="wrap"><hr class="rule"></div>
  <section class="wrap sec"><h2>Online converter or Chrome extension?</h2><ul class="list">
    <li><b>Use the online converter</b> to convert a batch, keep gradients, turn text into shapes, or build an icon library deck.</li>
    <li><b>Use the <a href="{cws('convert', 'compare')}">Chrome extension</a></b> to drop SVGs straight onto a slide you're editing. It converts in your browser.</li>
  </ul></section>
  <div class="wrap"><hr class="rule"></div>
  <section class="wrap sec faq" id="faq"><h2>Questions</h2>
    {"".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in CONVERT_FAQ)}
  </section>"""
    ld = [ctx["software_ld"](), ctx["crumbs"]([("Web Uploader", "/convert")])]
    return shell(title="Convert SVG to Google Slides Online (Free) | SVG to Slides",
                 desc="Convert SVG files to Google Slides online: upload, get a Google Drive file with editable vector shapes, one slide per SVG. Free, no account required.",
                 path="/convert", body=body, md="/convert.md", extra_css=CONVERT_CSS + ctx["extra_css"], campaign="convert",
                 ld_block=ctx["ld_block"](ld), tail=CONVERT_JS, og_type="website", **ctx["common"])


CONVERT_FAQ = [
    ("How do I convert an SVG to Google Slides online?", "Upload one or more SVG files on this page and press Convert. You get a Google Drive link to a file with one slide per SVG, every path a native shape."),
    ("Does the converted file open in Google Slides?", "Yes. Open the Drive link and the file opens in Google Slides. To keep it, choose File &rarr; Make a copy."),
    ("Do I need a Google account?", "No. Adding an email is optional; it shares the file straight to that account."),
    ("How many SVGs can I convert at once?", "Upload a batch. Each SVG becomes its own slide in the same file."),
]

CONVERT_MD = """# Convert SVG to Google Slides online

Upload SVG files at {site}/convert and get a Slides-ready file in Google Drive with real, editable vector shapes.

1. Upload one or more .svg files. Each SVG becomes one slide.
2. Every `<path>` becomes its own native, individually selectable shape in Google Slides, not a flattened image.
3. The file is uploaded to Google Drive and a link is returned, optionally shared to a Google account you provide.

- Links are deleted after 7 days. To keep a file, open it in Drive and choose File → Make a copy.
- Solid fills, strokes and gradients come through. Arc commands are converted into smooth curves. Text is outlined into shapes.
- Clip paths, masks, patterns, filters and transparency don't come through. Tested results: {site}/specs

Working in a deck already? The free Chrome extension drops SVGs straight onto a slide: {cws}

_{free}_
"""


# ---------------------------------------------------------------- about
ABOUT_CSS = """
.about{max-width:62ch;margin:0 auto;padding:0 20px;font-size:17px;line-height:1.7}
.about h2{font-size:clamp(22px,3vw,28px);margin:2em 0 .4em;text-align:left}
.about p{margin:0 0 1em}
.about a{color:var(--blue-ink);text-underline-offset:3px}
.about .facts3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:28px 0 8px}
.about .facts3 div{padding:16px;border-radius:14px;background:var(--tint);font-size:14px;line-height:1.45;color:var(--mute)}
.about .facts3 b{display:block;color:var(--fg);font-family:var(--display);font-size:16px;margin-bottom:4px}
@media (max-width:560px){.about .facts3{grid-template-columns:1fr}}
"""



# ---------------------------------------------------------- what's new
WHATS_NEW_CSS = """
.wn .rel{font:600 13px var(--display);letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin:2.4em 0 .2em}
.wn h2{margin-top:.2em}
.wn .clip{margin:24px 0 8px;border-radius:14px;overflow:hidden;border:1px solid var(--rule);background:#fff}
.wn .clip video{display:block;width:100%;height:auto}
.wn .cap{font-size:14px;color:var(--mute);margin:0 0 1.4em}
.wn table{width:100%;border-collapse:collapse;font-size:15px;margin:8px 0 1.4em}
.wn th,.wn td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--rule);vertical-align:top}
.wn th{font:600 13px var(--display);color:var(--mute)}
.wn kbd{font:500 13px/1 ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--tint);border-radius:6px;padding:3px 6px;white-space:nowrap}
.wn ul{padding-left:1.2em}.wn li{margin:0 0 .5em}
"""

EDITOR_KEYS = [
    ("Select points", "<kbd>A</kbd> or <kbd>V</kbd>, then click, Shift-click or drag a box"),
    ("Pen: add or remove points", "<kbd>P</kbd>, then click a segment to add, a point to remove"),
    ("Smooth or corner point", "Double-click the point"),
    ("Constrain to 45&deg;", "Hold <kbd>Shift</kbd> while dragging"),
    ("Break a curve handle", "Hold <kbd>Option</kbd> / <kbd>Alt</kbd> while dragging it"),
    ("Nudge", "Arrow keys, <kbd>Shift</kbd> for 10&times;"),
    ("Select all, delete", "<kbd>&#8984;A</kbd>, <kbd>Delete</kbd>"),
    ("Undo, redo", "<kbd>&#8984;Z</kbd>, <kbd>&#8679;&#8984;Z</kbd>"),
    ("Zoom", "Pinch, <kbd>&#8984;+</kbd> / <kbd>&#8984;&minus;</kbd>, <kbd>&#8984;0</kbd> for 100%"),
    ("Pan", "Hold <kbd>Space</kbd> and drag, or scroll"),
    ("Done", "<kbd>Enter</kbd>, or <kbd>Esc</kbd> with nothing selected"),
]


def whats_new_page(ctx):
    clip = ROOT / "cloud" / "static" / "whats-new" / "edit-as-svg.mp4"
    video = ""
    if clip.exists():
        video = ('<div class="clip"><video src="/static/whats-new/edit-as-svg.mp4" poster="/static/whats-new/edit-as-svg.jpg" '
                 'autoplay muted loop playsinline preload="metadata" aria-label="Double-clicking a star in Google Slides, '
                 'dragging its points in the SVG editor, then clicking Done"></video></div>'
                 '<p class="cap">Double-click, drag the points, Done. Recorded in Google Slides.</p>')
    keys = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in EDITOR_KEYS)
    body = f"""  <div class="wrap"><p class="crumb"><a href="/">SVG to Slides</a> &rsaquo; What&rsquo;s new</p></div>
  <section class="wrap phero">
    <div class="kick">What&rsquo;s new</div>
    <h1>Edit any shape in Google Slides&trade; as SVG.</h1>
  </section>
  <article class="about wn">
    <p>Slides lets you recolour and resize a shape, but not reshape it. Version 1.2 of the Chrome extension adds a vector editor that opens right on the slide, so you can move the points and curves of any shape and put it back where it was.</p>
    {video}
    <div class="rel">Version 1.2.0 &middot; November 2026</div>
    <h2>Edit as SVG</h2>
    <p>Double-click a shape, then click <b>Edit as SVG</b>. The editor opens on top of the slide at the shape&rsquo;s exact size and position. Drag points and curve handles, add or remove points with the pen, and select several at once. Undo, redo and zoom work the way they do in Figma and Illustrator. Click <b>Done</b> and the shape updates in place, at the zoom you were editing at.</p>
    <h2>Works on Slides&rsquo; own shapes</h2>
    <p>The editor also opens on shapes you didn&rsquo;t bring in with SVG to Slides: the shape menu, arrows, callouts, lines, text boxes and WordArt. It converts them into custom shapes first, and the button tells you what that costs:</p>
    <ul>
      <li>Shapes lose their adjustment handles (the small yellow diamonds).</li>
      <li>Lines lose their connection points, and arrowheads become separate shapes.</li>
      <li>3D shapes like the cube and can keep their shading as flat colours.</li>
      <li>WordArt becomes outlined letters, so you can reshape them but not retype them.</li>
    </ul>
    <p>Text inside a shape stays editable. Cancel puts the original back.</p>
    <h2>Click to insert</h2>
    <p>Drop an SVG onto a slide and click where it goes. It lands there as native shapes, with nothing to paste. If Slides ever turns the insert down, the extension asks you to press &#8984;/Ctrl + V instead.</p>
    <h2>Smaller fixes</h2>
    <ul>
      <li>SVG shapes made only of straight lines now land as Slides polylines, so Slides&rsquo; own <b>Edit points</b> works on them too.</li>
      <li>Placement and the editor now measure the slide you have open. Before, visiting another slide first could throw both off.</li>
    </ul>
    <h2>Editor shortcuts</h2>
    <table><thead><tr><th>Action</th><th>How</th></tr></thead><tbody>{keys}</tbody></table>
    <h2>Getting the update</h2>
    <p>Chrome updates extensions on its own, usually within a few hours. To check your version, open <b>chrome://extensions</b> and find SVG to Slides. The first time you open Slides after the update, a short note in the corner points out what changed. It shows once.</p>
    <p>The update adds one Chrome permission, <b>storage</b>, used only to remember that you have seen that note. The extension still asks for no access to your Google account.</p>
    <div class="rel">Version 1.0.1 &middot; July 2026</div>
    <p>Removed an unused permission flagged in Chrome Web Store review.</p>
    <div class="rel">Version 1.0.0 &middot; July 2026</div>
    <p>First release. Drag SVG files onto a Google Slides tab and they land as native, editable shapes, converted inside your browser.</p>
  </article>
  <div class="wrap"><hr class="rule" style="margin-top:56px"></div>
  <section class="wrap close">
    <h2>Bring your SVGs into Google Slides&trade;.</h2>
    <div class="ctas"><a class="btn btn-primary" href="{cws('whats-new', 'close')}" data-cta="close"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome, free</a><a class="btn btn-ghost" href="/guides/insert-svg-into-google-slides">Read the guide</a></div>
  </section>"""
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": "What's new in SVG to Slides", "url": C.SITE + "/whats-new",
           "about": {"@id": C.SITE + "/#app"}, "dateModified": "2026-11-14"},
          ctx["crumbs"]([("What's new", "/whats-new")])]
    doc = shell(title="What's New: Edit Any Shape in Google Slides as SVG | SVG to Slides",
                desc="SVG to Slides 1.2 adds a vector editor inside Google Slides. Double-click any shape to move its points and curves, including Slides' own shapes, lines and WordArt.",
                path="/whats-new", body=body, md="/whats-new.md", extra_css=ABOUT_CSS + WHATS_NEW_CSS, campaign="whats-new",
                ld_block=ctx["ld_block"](ld), **ctx["common"])
    md = f"""# What's new in SVG to Slides

## 1.2.0 (November 2026)

- Edit as SVG: double-click a shape, then click Edit as SVG. A vector editor opens on the slide at the shape's exact size and position. Drag points and curve handles, add or remove points, multi-select, undo, redo, zoom. Done updates the shape in place.
- Works on Slides' own shapes, lines, text boxes and WordArt by converting them to custom shapes first. Adjustment handles, connection points, automatic 3D shading and editable WordArt text don't carry over. Text inside a shape stays editable. Cancel restores the original.
- Click to insert: drop an SVG and click where it goes. It lands as native shapes with nothing to paste. Falls back to Cmd/Ctrl+V if Slides refuses the insert.
- Straight-line SVG shapes land as Slides polylines, so Slides' own Edit points works on them.
- Placement and the editor measure the slide you have open.
- Adds the Chrome "storage" permission, used only to show the update note once. Still no access to your Google account.

## 1.0.1 (July 2026)
Removed an unused permission flagged in Chrome Web Store review.

## 1.0.0 (July 2026)
First release: drag SVG files onto a Google Slides tab and they land as native, editable shapes.

Get it: {C.CWS}
"""
    return doc, md


# ---------------------------------------------------------- add-on page
ADDON_CSS = """
.tool.demo{padding:0;overflow:hidden}
.demo .dh{padding:18px 24px;border-bottom:1px solid var(--rule);font:800 17px var(--display)}
.demo .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;padding:20px 24px 6px}
.demo .cell{aspect-ratio:4/3;border-radius:12px;background:var(--tint);display:grid;place-items:center}
.demo .cell svg{width:38%;height:auto}
.demo .ready{margin:14px 24px 0;text-align:center;font:700 15px var(--display)}
.demo .copy{display:block;margin:12px auto 22px;width:200px;height:44px;line-height:44px;border-radius:999px;background:var(--blue);color:#fff;text-align:center;font:800 16px/44px var(--display)}
.democap{max-width:640px;margin:10px auto 0;font-size:13px;color:var(--mute);text-align:center}
.getrow{margin-top:26px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
@media (max-width:520px){.demo .grid{grid-template-columns:repeat(2,1fr)}}
"""
_SHAPES = [
    '<svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="16" fill="#1c1e22"/></svg>',
    '<svg viewBox="0 0 40 40"><rect x="5" y="5" width="30" height="30" rx="7" fill="#0066ff"/></svg>',
    '<svg viewBox="0 0 40 40"><path d="M20 4l16 30H4z" fill="#f9c80e"/></svg>',
    '<svg viewBox="0 0 40 40"><path d="M20 3l5 11 12 1-9 8 3 12-11-6-11 6 3-12-9-8 12-1z" fill="#1c1e22"/></svg>',
]


def addon_page(ctx):
    cells = "".join(f'<div class="cell">{s}</div>' for s in _SHAPES)
    body = f"""  <section class="wrap phero">
    <div class="kick">Workspace Add-on</div>
    <h1>SVG add-on for Google Slides&trade;</h1>
    <p class="lede">Insert SVG files from a dialog inside Slides. Pick your files, copy, paste. Every path lands as a real, editable vector shape.</p>
    <div class="getrow"><a class="btn btn-primary" href="/addon" data-cta="addon-hero">Get the add-on</a></div>
    <div class="tool demo" aria-hidden="true">
      <div class="dh">Insert SVGs</div>
      <div class="grid">{cells}</div>
      <p class="ready">Ready, click below or press Enter to copy</p>
      <span class="copy">Copy</span>
    </div>
    <p class="democap">The add-on dialog. Illustration.</p>
    <div class="xsell"><span><b>Prefer drag and drop?</b> The Chrome extension drops SVGs straight onto your slide.</span><a class="btn btn-primary" href="{cws('addon', 'xsell')}" data-cta="xsell"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome</a></div>
  </section>
  <div class="wrap"><hr class="rule" style="margin-top:56px"></div>
  <section class="wrap steps" id="how"><h2>How it works</h2><div class="steprow">
    <div class="step"><div class="n">Step 1</div><h3>Open it in Slides.</h3><p>Choose Insert SVGs from the Extensions menu, or click the add-on&rsquo;s icon in the side panel.</p></div>
    <div class="step"><div class="n">Step 2</div><h3>Pick your SVGs.</h3><p>They convert as you select them. Click Copy or press Enter.</p></div>
    <div class="step"><div class="n">Step 3</div><h3>Paste.</h3><p>Press Cmd/Ctrl+V. The shapes land on the slide you have open.</p></div>
  </div></section>
  <div class="wrap"><hr class="rule"></div>
  <section class="wrap sec"><h2>Good to know</h2><div class="facts">
    <div><b>Several at once</b>Select more than one file and they land side by side on the current slide.</div>
    <div><b>Solid colours</b>A gradient comes through as its first colour. For full gradients, use the <a href="/convert">web uploader</a>.</div>
    <div><b>Free</b>{C.FREE_LINE}</div>
  </div></section>"""
    ld = [ctx["software_ld"](), ctx["crumbs"]([("Workspace Add-on", "/google-slides-addon")])]
    return shell(title="SVG Add-on for Google Slides (Free) | SVG to Slides",
                 desc="A free Google Slides add-on that inserts SVG files as real, editable vector shapes. Pick files in a dialog, copy, and paste into your slide.",
                 path="/google-slides-addon", body=body, md="/google-slides-addon.md", extra_css=CONVERT_CSS + ADDON_CSS + ctx["extra_css"], campaign="addon",
                 ld_block=ctx["ld_block"](ld), og_type="website", **ctx["common"])


ADDON_MD = """# SVG add-on for Google Slides

A Google Slides add-on that inserts SVG files as real, editable vector shapes. Get it from the Google Workspace Marketplace: {site}/addon

## How it works
1. In Slides, choose Insert SVGs from the Extensions menu, or click the add-on's icon in the side panel.
2. Pick your SVG files. They convert as you select them. Click Copy or press Enter.
3. Press Cmd/Ctrl+V. The shapes land on the slide you have open.

## Good to know
- Select several files and they land side by side on the current slide.
- A gradient comes through as its first colour. For full gradients use the web uploader: {site}/convert
- {free}

## Other ways in
- Chrome extension (drag and drop onto the slide): {cws}
- Web uploader (one slide per SVG, as a Drive file): {site}/convert

Google Slides is a trademark of Google LLC.
"""


def about_page(ctx):
    body = f"""  <div class="wrap"><p class="crumb"><a href="/">SVG to Slides</a> &rsaquo; About</p></div>
  <section class="wrap phero">
    <div class="kick">About</div>
    <h1>Crisp graphics belong in Google Slides&trade;.</h1>
  </section>
  <article class="about">
    <p>SVG to Slides turns SVG files into native, editable shapes inside Google Slides. Every path becomes its own shape, so you can select it, recolour it with the standard fill picker, and resize it without losing quality.</p>
    <div class="facts3">
      <div><b>3 ways in</b>Chrome extension, web uploader and Slides add-on.</div>
      <div><b>0 Google permissions</b>The extension asks for no access to your Google account.</div>
      <div><b>$0, forever</b>No daily cap, no account, no Pro tier.</div>
    </div>
    <h2>Why it exists</h2>
    <p>Product marketing runs on decks, one-pagers and docs, and most of them are built in Google Workspace. Slides has no way to import an SVG. Paste one and it flattens into an image. Where there should be crisp icons and logos, there are crunchy PNGs.</p>
    <p>The great graphic designers of the last century built their work on crisp, clean marks. Everyday business documents deserve the same, without the long way through EMF conversion, Google Drawings and copy-paste every time.</p>
    <h2>How it works</h2>
    <p>When you copy a shape in Slides, Google writes it to the clipboard in its own internal format. SVG to Slides writes that same format from your SVG&rsquo;s paths and hands it to Slides, which treats the result as if you had drawn it yourself. The Chrome extension does the whole conversion inside your browser, so your file usually never leaves your device.</p>
    <p>Since version 1.2 the extension also edits shapes. Double-click any shape and a vector editor opens on the slide, so you can move its points and curves. <a href="/whats-new">What&rsquo;s new</a>.</p>
    <h2>Who builds it</h2>
    <p>SVG to Slides is designed and built by Joe Gelman, a copywriter and competitive strategist. It&rsquo;s an independent side project, kept free on purpose.</p>
    <h2>Get in touch</h2>
    <p>Bugs, ideas and odd SVGs that don&rsquo;t convert: <a href="mailto:joe@glmn.co">joe@glmn.co</a>. Help with common problems lives on the <a href="/support">support page</a>.</p>
  </article>
  <div class="wrap"><hr class="rule" style="margin-top:56px"></div>
  <section class="wrap close">
    <h2>Bring your SVGs into Google Slides&trade;.</h2>
    <div class="ctas"><a class="btn btn-primary" href="{cws('about', 'close')}" data-cta="close"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome, free</a><a class="btn btn-ghost" href="/convert">Use the web uploader</a></div>
  </section>"""
    ld = [{"@context": "https://schema.org", "@type": "AboutPage", "name": "About SVG to Slides", "url": C.SITE + "/about",
           "about": {"@type": "SoftwareApplication", "name": "SVG to Slides"},
           "author": {"@type": "Person", "name": "Joe Gelman", "email": "joe@glmn.co"}},
          ctx["crumbs"]([("About", "/about")])]
    doc = shell(title="About SVG to Slides", desc="SVG to Slides turns SVG files into native, editable Google Slides shapes. Free, independent, built by Joe Gelman.",
                path="/about", body=body, md="/about.md", extra_css=ABOUT_CSS, campaign="about",
                ld_block=ctx["ld_block"](ld), **ctx["common"])
    md = f"""# About SVG to Slides

SVG to Slides turns SVG files into native, editable shapes inside Google Slides. Every path becomes its own shape: select it, recolour it with the standard fill picker, resize it without losing quality.

- Three ways in: Chrome extension ({C.CWS}), web uploader ({C.SITE}/convert), Google Slides add-on ({C.SITE}/addon).
- The extension asks for no access to your Google account.
- {C.FREE_LINE}

## Why it exists
Slides has no way to import an SVG; pasted SVGs flatten into images. Where there should be crisp icons and logos, there are crunchy PNGs.

## How it works
SVG to Slides writes Google Slides' own clipboard shape format from your SVG's paths and hands it to Slides, which treats the result as native shapes. The extension converts inside your browser. Since 1.2 it also edits shapes: double-click any shape to move its points and curves ({C.SITE}/whats-new).

## Who builds it
Joe Gelman, independently. Contact: joe@glmn.co
"""
    return doc, md
