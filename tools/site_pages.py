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
    <span class="bnav"><a class="txt" href="/guides">Guides</a><a class="txt" href="/docs">Docs</a><a class="txt" href="/blog">Blog</a><a class="btn btn-primary" href="{cws(campaign, 'nav')}" data-cta="nav"><img src="/static/chrome-glyph.svg" alt=""><span class="lg">Add to Chrome</span><span class="sm">Add</span></a></span>
  </nav>
</div>"""


# --------------------------------------------------------------- footer
FOOTER_COLS = [
    ("Products", [("Chrome Extension", "CWS"), ("Workspace Add-on", "/google-slides-addon"), ("Web Uploader", "/convert")]),
    ("Resources", [("Guides", "/guides"), ("Docs", "/docs"), ("Specs", "/specs"), ("Blog", "/blog")]),
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
.wn .val{margin:.2em 0 .9em;padding:10px 14px;border-left:3px solid var(--blue);background:var(--tint);border-radius:0 10px 10px 0;font-weight:600;font-size:16px;line-height:1.5}
.wnhero{max-width:980px;margin:8px auto 0;padding:0 20px}.wnhero .clip{margin:0}.wnhero .cap{text-align:center;margin-top:10px}
.wnstats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;max-width:980px;margin:18px auto 0;padding:0 20px}
.wnstats div{padding:18px;border-radius:14px;background:var(--tint)}
.wnstats b{display:block;font:800 clamp(28px,4vw,40px)/1 var(--display);color:var(--blue-ink)}
.wnstats span{display:block;margin-top:8px;font-size:14px;line-height:1.4;color:var(--mute)}
.glance{max-width:980px;margin:56px auto 0;padding:0 20px}.glance h2{text-align:center;margin:0 0 6px}.glance .sub{text-align:center;color:var(--mute);margin:0 0 22px}
.glance .gg{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.glance .gt{display:block;text-decoration:none;color:var(--fg);border:1px solid var(--rule);border-radius:14px;overflow:hidden;background:#fff}
.glance .gt:hover,.glance .gt:focus-visible{border-color:var(--blue)}
.glance .gt img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;background:#F9FAFD}
.glance .gt b{display:block;padding:12px 14px 2px;font:800 16px var(--display)}
.glance .gt span{display:block;padding:0 14px 14px;font-size:14px;line-height:1.45;color:var(--mute)}
.wnband{max-width:980px;margin:40px auto 0;padding:0 20px;text-align:center}
.wnband .ctas{justify-content:center}.wnband p{margin:0 0 14px;color:var(--mute)}
.wnp{padding:8px 0 0}.wnp h1{font-size:clamp(30px,4.4vw,48px);line-height:1.08;max-width:none;margin:0 auto 10px}
.wnp .lede{font-size:clamp(16px,1.6vw,19px);max-width:38em}.wnp .ctas{margin-top:20px;justify-content:center}
.glance.top{margin-top:26px;max-width:1120px}.glance.top .gg{gap:16px}
.wnmid{max-width:980px;margin:48px auto 0;padding:0 20px}.wnmid .clip{margin:0}.wnmid .cap{text-align:center;margin-top:10px}
@media (max-width:900px){.glance .gg{grid-template-columns:repeat(2,1fr)}}
@media (max-width:520px){.wnstats{grid-template-columns:1fr}.glance .gg{grid-template-columns:1fr}}
"""

EDITOR_KEYS = [
    ("Select points", "<kbd>A</kbd> or <kbd>V</kbd>, then click, Shift-click or drag a box"),
    ("Pen: add or remove points", "<kbd>P</kbd>, then click a segment to add, a point to remove"),
    ("Smooth or corner point", "Double-click the point"),
    ("Round corners", "Drag a circle inside a corner, or type a value in the pill below the shape. <kbd>Shift</kbd> for 10&nbsp;px steps"),
    ("Constrain to 45&deg;", "Hold <kbd>Shift</kbd> while dragging"),
    ("Break a curve handle", "Hold <kbd>Option</kbd> / <kbd>Alt</kbd> while dragging it"),
    ("Nudge", "Arrow keys, <kbd>Shift</kbd> for 10&times;"),
    ("Select all, delete", "<kbd>&#8984;A</kbd>, <kbd>Delete</kbd>"),
    ("Undo, redo", "<kbd>&#8984;Z</kbd>, <kbd>&#8679;&#8984;Z</kbd>"),
    ("Zoom", "Pinch, <kbd>&#8984;+</kbd> / <kbd>&#8984;&minus;</kbd>, <kbd>&#8984;0</kbd> for 100%"),
    ("Pan", "Hold <kbd>Space</kbd> and drag, or scroll"),
    ("Done", "<kbd>Enter</kbd>, or <kbd>Esc</kbd> with nothing selected"),
]

KEYS_13 = [
    ("Show or hide the toolbar", "<kbd>&#8997;&#92;</kbd>"),
    ("Command palette", "<kbd>&#8984;&#92;</kbd>"),
    ("Layers", "<kbd>&#8997;1</kbd>"),
    ("Theme builder, and back", "<kbd>&#8997;&#8679;M</kbd>"),
    ("Pen: draw anywhere, or edit the selection", "<kbd>&#8997;&#8679;P</kbd>"),
    ("In the editor: pen, select", "<kbd>P</kbd>, <kbd>V</kbd>"),
    ("Snap to grid on or off (editor)", "<kbd>&#8984;'</kbd>; hold <kbd>&#8984;</kbd> to place freely"),
    ("Mask image with shape", "<kbd>&#8997;&#8679;K</kbd>"),
    ("Union, subtract, intersect, exclude", "<kbd>&#8997;&#8679;U</kbd>, <kbd>&#8997;&#8679;S</kbd>, <kbd>&#8997;&#8679;I</kbd>, <kbd>&#8997;&#8679;E</kbd>"),
    ("Outline stroke", "<kbd>&#8997;&#8984;O</kbd>"),
    ("Outline text, or restore it", "<kbd>&#8997;&#8984;T</kbd>"),
    ("Align left, centre, right", "<kbd>&#8997;A</kbd>, <kbd>&#8997;H</kbd>, <kbd>&#8997;D</kbd>"),
    ("Align top, middle, bottom", "<kbd>&#8997;W</kbd>, <kbd>&#8997;V</kbd>, <kbd>&#8997;S</kbd>"),
    ("Distribute horizontally, vertically", "<kbd>&#8997;&#8679;H</kbd>, <kbd>&#8997;&#8679;V</kbd>"),
    ("Group, ungroup", "<kbd>&#8984;&#8997;G</kbd>, <kbd>&#8679;&#8984;&#8997;G</kbd>"),
    ("Bring forward, send backward; to front, to back", "<kbd>&#8984;&uarr;</kbd>, <kbd>&#8984;&darr;</kbd>; <kbd>&#8679;&#8984;&uarr;</kbd>, <kbd>&#8679;&#8984;&darr;</kbd>"),
    ("Rotate 15&deg; or 1&deg;", "<kbd>&#8997;&larr;</kbd> <kbd>&#8997;&rarr;</kbd>; add <kbd>&#8679;</kbd> for 1&deg;"),
    ("Larger, smaller", "<kbd>&#8984;&#8963;K</kbd>, <kbd>&#8984;&#8963;J</kbd>"),
    ("Fill colour, stroke colour", "<kbd>&#8997;&#8679;F</kbd>, <kbd>&#8997;&#8679;L</kbd>"),
    ("Stroke on or off, thinner, thicker", "<kbd>&#8997;&#8679;/</kbd>, <kbd>&#8997;&#8679;[</kbd>, <kbd>&#8997;&#8679;]</kbd>"),
    ("Undo or redo one of the extension&rsquo;s changes in one press", "<kbd>&#8984;Z</kbd>, <kbd>&#8679;&#8984;Z</kbd> or <kbd>&#8984;Y</kbd>"),
    ("Select inside a group", "<kbd>&#8984;</kbd>-click; <kbd>&#8679;&#8984;</kbd>-click adds"),
]


def whats_new_page(ctx):
    video = ('<div class="clip"><video src="/static/whats-new/edit-points.mp4" poster="/static/whats-new/edit-points.jpg" '
             'autoplay muted loop playsinline preload="metadata" aria-label="Double-clicking a palm tree in Google Slides, '
             'then dragging its points and curve handles in the editor"></video></div>'
             '<p class="cap">Double-click, Edit Shape, drag. Recorded in Google Slides.</p>')
    corners = ('<div class="clip"><video src="/static/whats-new/round-corners.mp4" poster="/static/whats-new/round-corners.jpg" '
               'autoplay muted loop playsinline preload="metadata" aria-label="Selecting three cards, dragging a corner handle '
               'to round all twelve corners, then typing 25"></video></div>'
               '<p class="cap">Three cards, twelve corners, one drag. Then type 25 and press Enter.</p>')
    keys = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in EDITOR_KEYS)
    def lot(name, label, cap):
        return (f'<div class="clip"><div class="lot" data-lottie="/static/lottie/svgslides_13_{name}.json" '
                f'style="aspect-ratio:16/9" role="img" aria-label="{label}"></div></div><p class="cap">{cap}</p>')
    keys13 = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in KEYS_13)
    v14 = """  <article class="about wn" id="v14">
    <div class="rel">Version 1.4.0 &middot; November 2026</div>
    <p>Version 1.4 puts colour in the toolbar. It has its own picker, a gradient builder, and a way to swap one colour for another across a slide or the whole deck. The slide shows each change while you pick. Image masks now keep their shape, and the picture under a mask can be moved.</p>
    <h2 id="colour">A colour picker of its own</h2>
    <p>Select a shape and press the paint bucket (<kbd>&#8997;&#8679;F</kbd>), or the stroke button (<kbd>&#8997;&#8679;L</kbd>). The panel has a spectrum, hue and opacity sliders, an eyedropper, a hex field, the colours already on the slide and the ones you used last.</p>
    @@colour|Picking a new fill colour in the panel while the card on the slide changes with it|Open the panel, drag, and the shape follows.@@
    <p>Highlight a stretch of text and the same panel becomes <b>Text colour</b>. It recolours those words and leaves the rest of the box alone.</p>
    <p>A colour change is made on the object itself, so its animation and link stay.</p>
    <h2 id="gradients">Gradients</h2>
    <p>Switch the panel to linear or radial. Add and drag stops on the bar, set the angle on the dial, and pick where a radial gradient starts. The result is a real Slides gradient.</p>
    @@gradient|Switching the panel to Linear, adding a stop on the bar and turning the angle dial|Add a stop on the bar, colour it, turn the dial.@@
    <h2 id="replace">Replace a colour</h2>
    <p>With nothing selected, the paint bucket opens <b>Replace a colour</b>. Pick a colour that is in use, from the list or with the eyedropper, and choose what it becomes. It changes fills, strokes, gradient stops and text, including inside groups.</p>
    <p>Turn on <b>All slides</b> and the list shows every colour in the deck. The change runs across every slide, with a progress bar, and one <kbd>&#8984;Z</kbd> undoes all of it.</p>
    @@replace|Picking teal in Replace a colour and turning every teal shape purple, then running it across all slides|Pick the colour to change, choose the new one, run it across the deck.@@
    <h2 id="preview">Live preview</h2>
    <p>While the panel is open, the slide shows the colour, opacity, gradient or stroke width in hand. &#10003; keeps it. &#10005; puts the slide back.</p>
    @@preview|A highlighted word changing colour as the panel is dragged|Highlighted words take the colour while you are still picking.@@
    <h2 id="mask-adjust">Masks you can keep working with</h2>
    <p><b>Mask image with shape</b> (<kbd>&#8997;&#8679;K</kbd>) now keeps the shape. It sits on top as an outline with no fill, grouped with the masked picture, so you can restyle its stroke afterwards.</p>
    <p>Double-click the group, or press Mask again, to adjust the picture under its mask. Drag to move it, drag a corner to resize, nudge with the arrow keys, type a percentage, or press <b>Fit</b>. <kbd>&#8629;</kbd> keeps the change and <kbd>Esc</kbd> cancels.</p>
    @@mask|Double-clicking a photo masked by an arch, dragging and resizing the whole picture under it, then confirming|Double-click, drag the picture, resize it, confirm.@@
    <h2 id="import-gradients">Gradients and opacity on import</h2>
    <p>Linear and radial gradients in an SVG arrive as Slides gradients. <code>opacity</code>, <code>fill-opacity</code> and <code>stroke-opacity</code> come across too. The <a href="/convert">web uploader</a> still flattens gradients to one colour.</p>
    @@import|An SVG file dropped on a slide becomes shapes with gradients, and one opens in the gradient builder with its three stops|Drop the file. The gradients open in the builder with their stops.@@
    <h2 id="outline-icons">Outline icon sets</h2>
    <p>Icons drawn with strokes, such as Lucide, Feather, Heroicons outline and Tabler, now import as shapes. This arrived in 1.3.1.</p>
    @@icons|An SVG of six outline icons dropped on a slide, then filled orange in one go|Stroke icons land as shapes, so a fill works on them.@@
    <h2 id="limits14">Known limits</h2>
    <ul>
      <li>A gradient on a shape whose text uses more than one style replaces the shape, so its animation is lost. The extension says so when it happens.</li>
      <li>A fill on a whole mask group is refused, because it would cover the picture. Select the shape inside the group to fill it.</li>
      <li>A stroke width that isn&rsquo;t one of Slides&rsquo; own presets replaces the shape.</li>
    </ul>
    <p>1.4 asks for nothing new: access to Google Slides pages, where the tools run, and <b>storage</b>.</p>
  </article>"""
    import re as _re
    v14 = _re.sub(r'@@(\w+)\|([^|]+)\|([^@]+)@@', lambda m: (f'<div class="clip"><div class="lot" data-lottie="/static/lottie/svgslides_14_{m.group(1)}.json" '
                  f'style="aspect-ratio:16/9" role="img" aria-label="{m.group(2)}"></div></div><p class="cap">{m.group(3)}</p>'), v14)
    body = f"""  <div class="wrap"><p class="crumb"><a href="/">SVG to Slides</a> &rsaquo; What&rsquo;s new</p></div>
  <section class="wrap phero wnp">
    <h1>Draw, mask and combine inside Slides.</h1>
    <p class="lede">1.4 adds a colour picker, gradients, replace a colour and masks you can adjust. 1.3 added the pen, masks, layers and shape combining. Free, and nothing is uploaded.</p>
    <div class="ctas"><a class="btn btn-primary" href="{cws('whats-new', 'hero')}" data-cta="hero"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome, free</a><a class="btn btn-ghost" href="#v14">New in 1.4</a></div>
  </section>
{v14}
  <section class="glance top" id="glance">
    <div class="gg"><a class="gt" href="#pen"><img src="/static/whats-new/tile-pen.webp" width="720" height="405" loading="eager" alt="Drawing a curve with the pen in Google Slides"><b>Draw curves</b><span>Draw the shapes the shape menu doesn&rsquo;t have. Points and handles snap to a grid.</span></a><a class="gt" href="#outline"><img src="/static/whats-new/tile-beach.webp" width="720" height="405" loading="eager" alt="Letters of the word BEACH filled with a beach photo"><b>Outline text</b><span>Turn text into shapes, then use the letters as a mask.</span></a><a class="gt" href="#mask"><img src="/static/whats-new/tile-mask.webp" width="720" height="405" loading="eager" alt="A photo masked by an arch shape"><b>Mask with any shape</b><span>Crop a picture to any shape. It stays exactly where it was.</span></a><a class="gt" href="#combine"><img src="/static/whats-new/tile-combine.webp" width="720" height="405" loading="eager" alt="Shapes combined into a cloud"><b>Combine shapes</b><span>Union, subtract, intersect, exclude. Undo in one press.</span></a><a class="gt" href="#layers"><img src="/static/whats-new/tile-layers.webp" width="720" height="405" loading="lazy" alt="The Layers panel open on nested groups"><b>Reach into groups</b><span>Select, rename and hide anything, including objects inside groups.</span></a><a class="gt" href="#theme"><img src="/static/whats-new/tile-theme.webp" width="720" height="405" loading="lazy" alt="A theme object edited on a slide"><b>Jump to theme objects</b><span>Select one in Layers, or &#8984;-click it. The theme builder opens on it.</span></a><a class="gt" href="#palette"><img src="/static/whats-new/tile-palette.webp" width="720" height="405" loading="lazy" alt="The command palette open over a slide"><b>Search every command</b><span>Every command with its shortcut, one search away.</span></a><a class="gt" href="#paste"><img src="/static/whats-new/tile-paste.webp" width="720" height="405" loading="lazy" alt="A logo pasted onto a slide as shapes"><b>Paste SVG code</b><span>Copy SVG from any site. Paste it as editable shapes.</span></a></div>
  </section>
  <div class="wnstats">
    <div><b>92%</b><span>smaller extension: 14&nbsp;MB to 1.1&nbsp;MB installed</span></div>
    <div><b>0 uploads</b><span>SVGs convert in your browser and never leave it</span></div>
    <div><b>Free</b><span>No account, no Pro tier</span></div>
  </div>
  <div class="wn wnmid">{lot('hero', 'SVG to Slides 1.3', 'Every clip on this page is drawn as a vector animation, using the Vacay.com pitch deck we use for demos.')}</div>
  <div class="wnband"><p>Chrome updates the extension on its own. Check chrome://extensions for 1.4.0.</p><div class="ctas"><a class="btn btn-primary" href="{cws('whats-new', 'mid')}" data-cta="mid"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome, free</a></div></div>
  <article class="about wn">
    <p>SVG to Slides started as a way to drop SVG files onto a slide as real shapes. Version 1.3 turns it into a set of drawing tools that work on any shape in the deck: a pen that draws curves and snaps them to a grid, exact stroke weights, text you can outline and use as a mask, union and subtract, a layers panel that reaches into nested groups and theme objects, and a command palette that lists all of it. The extension also got 92% smaller, and it no longer talks to a server.</p>
    <div class="rel">Version 1.3.0 &middot; November 2026</div>
    <h2 id="contents">In this release</h2>
    <ul>
      <li><a href="#toolbar">One toolbar</a> and the <a href="#palette">command palette</a></li>
      <li><a href="#pen">The pen</a>, <a href="#snapping">snapping</a> and <a href="#stroke">exact strokes</a></li>
      <li><a href="#outline">Outline text</a> and <a href="#mask">mask any image with any shape</a></li>
      <li><a href="#combine">Union, subtract, intersect, exclude</a> and <a href="#undo">one-step undo</a></li>
      <li><a href="#align">Instant align</a>, including a single image to the slide edge</li>
      <li><a href="#layers">Layers</a>, nested groups and <a href="#theme">theme objects</a></li>
      <li><a href="#paste">Paste SVG code</a>, <a href="#lossless">sharper small drops</a> and a <a href="#size">92% smaller extension</a></li>
      <li><a href="#how">How it works</a>, <a href="#keys">shortcuts</a>, <a href="#fixes">fixes</a> and <a href="#limits">known limits</a></li>
    </ul>

    <h2 id="toolbar">One toolbar</h2>
    <p class="val">Everything in one place, at the left edge of the canvas.</p>
    <p>Everything sits in one toolbar at the left edge of the slide canvas. Closed, it is a single round button; click it or press <kbd>&#8997;&#92;</kbd>. It remembers whether you left it open.</p>
    <ul>
      <li><b>Top:</b> Layers, Edit Shape, Pen, and the command palette.</li>
      <li><b>Then:</b> Arrange and Align (each opens a row of options), Combine, Group, Outline, and fill and stroke, with a weight field in pixels.</li>
      <li>Every button, pop-out item and field has a tooltip with its shortcut.</li>
      <li>On a short screen, Combine and then Outline fold into one button each.</li>
      <li>While a change is running the toolbar ignores clicks, so nothing gets applied twice.</li>
    </ul>

    <h2 id="pen">Draw with the pen</h2>
    <p class="val">Draw the shapes the shape menu doesn&rsquo;t have, with points and handles that snap to a grid.</p>
    <p>Slides gives you a shape menu. The pen gives you the shapes that aren&rsquo;t in it.</p>
    {lot('pen', 'Drawing a curved wave shape with the pen while points and handles snap to a 20 pixel grid', 'Click for corners, drag for curves. Every point and handle lands on the grid.')}
    <ol>
      <li>With nothing selected, press <kbd>&#8997;&#8679;P</kbd> or click <b>Pen</b>. An empty editor opens over the slide. (With shapes selected, it opens on them and you can still draw.)</li>
      <li><b>Click</b> to place a corner. <b>Click and drag</b> to place a smooth point and pull out its curve handles.</li>
      <li>Hold <kbd>&#8997;</kbd> while dragging to break the handles apart, or <kbd>&#8679;</kbd> to keep them at 45&deg; steps.</li>
      <li>A dashed segment follows the pointer so you can see the next curve before you commit it.</li>
      <li><b>Click the first point</b> (a ring appears on it) to close the shape, or press <kbd>Enter</kbd> or <kbd>Esc</kbd> to leave the path open.</li>
      <li><kbd>Delete</kbd> removes the last point; <kbd>&#8984;Z</kbd> steps back point by point.</li>
      <li>Click <b>Done</b>. Every new path goes onto the slide on top, in one undo step.</li>
    </ol>
    <p>New paths start as a 2&nbsp;px dark stroke with no fill, then take the paint of the last one you drew. Click the end point of any open path to carry on drawing it. Click a middle point to remove it, or a segment to add one.</p>

    <h2 id="snapping">Snapping</h2>
    <p class="val">Clean geometry without eyeballing it: snap to points, whole pixels or a grid you size.</p>
    <p>The magnet button in the editor controls snapping for the pen, for dragged points and for curve handles.</p>
    <ul>
      <li><b>Points:</b> other points, the horizontal and vertical lines through them, and the slide&rsquo;s edges and centre. Pink guides and a small &times; show what caught.</li>
      <li><b>Pixels:</b> rounds to whole pixels.</li>
      <li><b>Grid:</b> shows a grid from the slide&rsquo;s top-left corner and snaps to it. Type a size in pixels; typing one turns the grid on. <kbd>&#8984;'</kbd> shows or hides it. The grid hides itself when its lines would be less than 6 screen pixels apart.</li>
      <li>Points win when one is within 6 screen pixels; otherwise the grid or pixel rounding applies.</li>
      <li>Hold <kbd>&#8984;</kbd> to place a point freely. Points and pixels are on to start; your settings stay on this computer.</li>
    </ul>

    <h2 id="stroke">Exact strokes</h2>
    <p class="val">Exact weights, and a stroke inside or outside the shape without changing its visual size.</p>
    {lot('stroke', 'Filling the wave, scrubbing its stroke weight from 2 to 14 pixels, moving the stroke inside and outside, then typing 8', 'Option-drag to scrub, type to be exact.')}
    <ul>
      <li><b>Weight in pixels.</b> The toolbar&rsquo;s weight field takes any value. Hold <kbd>&#8997;</kbd> and drag on it to scrub; add <kbd>&#8679;</kbd> to move in steps of 10.</li>
      <li><b>Stroke position:</b> inside, centre or outside. Inside and outside move the outline in or out by half the weight, so the shape keeps its visual size. The setting is remembered on this computer.</li>
      <li><b>Stroke on or off, thinner, thicker</b>, and fill and stroke colour all have shortcuts (see <a href="#keys">below</a>).</li>
      <li><b>Exact geometry</b> in Edit Shape: type a width, height, rotation or corner radius in the pill under the shape, and scrub any of them with <kbd>&#8997;</kbd>-drag.</li>
      <li><b>The box in Edit Shape</b> scales from its corners (<kbd>&#8679;</kbd> keeps proportions, <kbd>&#8997;</kbd> scales from the centre), stretches from its edges, rotates from just outside a corner, and skews with <kbd>&#8984;</kbd> on an edge. <kbd>&#8679;</kbd> snaps rotation and skew to 15&deg;.</li>
    </ul>

    <h2 id="outline">Outline text, then use it</h2>
    <p class="val">Text becomes shapes, one per letter, with the font&rsquo;s exact curves.</p>
    {lot('beach', 'Typing BEACH in a heavy condensed font, outlining it, and masking a beach photo with the letters', 'Type, outline (Option-Command-T), select both, mask (Option-Shift-K).')}
    <p><b>Outline text</b> (<kbd>&#8997;&#8984;T</kbd>) turns a text box into shapes with the font&rsquo;s exact curves. From there it&rsquo;s a shape like any other: reshape it in Edit Shape, combine it, or use it as a mask, as above. <b>Outline stroke</b> (<kbd>&#8997;&#8984;O</kbd>) does the same for lines and borders.</p>
    <ul>
      <li>To get the letter shapes, the extension downloads the font file from Google Fonts. That is a public download and needs no permission.</li>
      <li>Changed your mind? On the computer that outlined it, <kbd>&#8997;&#8984;T</kbd> on the outlined shapes puts the editable text back.</li>
    </ul>

    <h2 id="mask">Mask any image with any shape</h2>
    <p class="val">Crop a picture to any shape, or to outlined text. The picture doesn&rsquo;t move.</p>
    <p>Put a shape (or a group of shapes, or outlined text) over a picture, select both, and press <kbd>&#8997;&#8679;K</kbd>. The shape on top cuts out the picture under it.</p>
    {lot('mask', 'Masking a photo of a couple on a beach with an arch shape', 'Any shape works, not just the crop shapes in Slides&rsquo; menu.')}
    <ul>
      <li>The picture stays exactly where it was: not stretched, not re-cropped.</li>
      <li>The result takes the image&rsquo;s place in the stack, and the whole thing is one undo step.</li>
      <li>Edit the mask&rsquo;s points later in Edit Shape; the picture holds still while the outline moves.</li>
      <li>Text needs outlining first. Rotated images aren&rsquo;t supported yet.</li>
    </ul>

    <h2 id="combine">Union, subtract, intersect, exclude</h2>
    <p class="val">Build one shape out of many, then undo it in one press.</p>
    {lot('combine', 'Four shapes combined into one cloud with Union, then undone and redone in one press each', 'Union, then Command-Z and Shift-Command-Z.')}
    <p>Select two or more shapes and pick a combine command from the toolbar or with <kbd>&#8997;&#8679;U</kbd>, <kbd>&#8997;&#8679;S</kbd>, <kbd>&#8997;&#8679;I</kbd> or <kbd>&#8997;&#8679;E</kbd>. Subtract cuts every shape on top out of the bottom one. The commands also work inside Edit Shape, on the shapes you have points selected in, or on every shape in the editor when no points are selected.</p>

    <h2 id="undo">One undo step</h2>
    <p class="val">A change that takes several steps in Slides undoes in one.</p>
    <p>A combine, an outline, a stroke-position change or a whole pen session takes several steps in Slides. Press <kbd>&#8984;Z</kbd> right after one of them and the extension walks Slides back the whole way in one press. <kbd>&#8679;&#8984;Z</kbd> or <kbd>&#8984;Y</kbd> walks forward, through a chain of the extension&rsquo;s changes. It never presses undo more times than the change took, and if you edit the slide yourself in between, Slides&rsquo; own undo takes over. Text editing keeps Slides&rsquo; normal undo.</p>

    <h2 id="align">Align and distribute, instantly</h2>
    <p class="val">Align a single photo to the slide edges. Objects move once, straight to the result.</p>
    {lot('align', 'Aligning a single photo to the left, top and bottom edges of the slide', 'One photo, three edges, no in-between frames.')}
    <p>Align and distribute run Slides&rsquo; own commands behind a still copy of the slide, so objects move once, straight to the result. Because nothing is deleted or pasted, images stay intact. And a single object, image included, now aligns to the slide: left, centre, right, top, middle or bottom.</p>

    <h2 id="layers">Layers and nested groups</h2>
    <p class="val">Select, rename and hide anything on the slide, even deep inside groups.</p>
    {lot('layers', 'Opening three levels of nested groups in the Layers panel, Command-clicking the plane icon on the slide, and renaming it', 'Three levels down, Command-click, rename.')}
    <p>Press <kbd>&#8997;1</kbd> for a list of every object on the slide, front first. It docks over the filmstrip and follows the slide you&rsquo;re on.</p>
    <ul>
      <li><b>Groups fold open and closed.</b> Selecting something inside a group opens the groups around it.</li>
      <li><b>Click</b> a row to select it, even deep inside a group; <b>&#8679;-click</b> adds. Drag top-level rows to restack.</li>
      <li><b>&#8984;-click on the slide</b> selects the innermost object under the pointer, without ungrouping anything. While you hold &#8984;, an outline shows what you&rsquo;d get.</li>
      <li><b>Double-click a name</b> to rename. <kbd>Enter</kbd> keeps it, <kbd>Esc</kbd> cancels, a click elsewhere keeps it.</li>
      <li><b>The eye</b> hides an object while you work on what&rsquo;s behind it.</li>
      <li><b>Tiny objects</b> (under 6 px on screen) say so on the first click; a second click zooms in and selects them.</li>
    </ul>

    <h2 id="theme">Theme objects and the theme builder</h2>
    <p class="val">Pick a theme object in Layers, or &#8984;-click it, and go straight to the editor that holds it.</p>
    {lot('theme', 'Clicking a theme object twice to open it in the theme builder, recolouring it, and seeing every slide update', 'Click a theme object twice and the theme builder opens on it.')}
    <p>Logos, footers and backgrounds that come from the theme can&rsquo;t be selected on a normal slide, which is why they seem stuck. Layers shows them greyed with an <b>M</b>. Click one: a note says it lives on the theme. Click again within five seconds and the theme builder opens on the layout or master that holds it, with the object selected. Change it there, press <kbd>&#8997;&#8679;M</kbd> (or close the builder) to go back, and every slide that uses that layout or master shows the change.</p>

    <h2 id="palette">Command palette</h2>
    <p class="val">Every command, searchable, with its shortcut beside it.</p>
    {lot('palette', 'Opening the command palette, scrolling through every command group, and searching for mask', 'Command-Backslash, type, Enter.')}
    <p><kbd>&#8984;&#92;</kbd> opens a searchable list of every command, grouped the way the toolbar is, with its shortcut beside it. Type to filter, use the arrow keys, press <kbd>Enter</kbd> to run, and <kbd>Esc</kbd> or <kbd>&#8984;&#92;</kbd> again to close.</p>

    <h2 id="paste">Paste SVG code</h2>
    <p class="val">Paste SVG code from any site and get shapes you can recolour and edit.</p>
    {lot('paste', 'Copying a logo&rsquo;s SVG element from browser developer tools and pasting it onto a slide as shapes', 'Copy element in DevTools, Command-V in Slides.')}
    <p>You don&rsquo;t need a file. Copy SVG markup from anywhere (a site&rsquo;s logo via <b>Inspect &rsaquo; Copy &rsaquo; Copy element</b>, a code editor, an icon library&rsquo;s &ldquo;copy SVG&rdquo; button) and press <kbd>&#8984;V</kbd> on a slide. The extension recognises SVG code on the clipboard and sends it through the same converter as a dropped file, so it lands as native shapes you can recolour and edit. Use logos you have the right to use.</p>

    <h2 id="lossless">Small SVGs keep their detail</h2>
    <p class="val">Small icons keep their detail when you enlarge them.</p>
    {lot('lossless', 'A small palm icon dropped on a slide, enlarged, then viewed at 400%', 'Dropped small, enlarged, still sharp.')}
    <p>Slides stores a pasted shape&rsquo;s points exactly as they arrive and resizes it by changing its transform. So an icon dropped at 12&nbsp;px used to carry 12&nbsp;px worth of detail forever, and enlarging it showed lumps on the curves. Now every shape&rsquo;s points are written in a large frame of their own and scaled down to size, so enlarging it later has all the detail it needs.</p>

    <h2 id="size">92% smaller, and nothing leaves your browser</h2>
    <p class="val">14&nbsp;MB to 1.1&nbsp;MB, and your SVGs are never uploaded.</p>
    {lot('light', 'The extension size dropping from 14 megabytes to 1.1', '')}
    <p>Until now the extension carried a copy of Python, compiled to WebAssembly, to run its converter on every Slides tab. The converter is now plain JavaScript inside the extension. The installed extension went from 14&nbsp;MB to 1.1&nbsp;MB, and the download from 5.8&nbsp;MB to under 400&nbsp;KB. The server fallback is gone too, along with the permission it needed: SVGs are converted in your browser and never uploaded. What it asks Chrome for now: access to Google Slides pages, where its tools run, and <b>storage</b>, for your settings.</p>

    <h2 id="how">How it works</h2>
    <p>For the curious, the parts that took the longest to get right:</p>
    <ul>
      <li><b>Masks are pictures in shapes.</b> In Slides, a masked image is a shape whose fill is the picture. The extension builds that shape from your mask&rsquo;s path and places the picture by measuring the path&rsquo;s exact bounds (the true extremes of its curves, not their control points), so the picture lands where it was to four decimal places.</li>
      <li><b>One image, one edge.</b> Slides&rsquo; own Align needs two objects to align a single one to the slide. The extension pastes a 1&nbsp;px invisible square at the corner it needs, aligns, and deletes the square, all in one step. Nothing extra stays in your deck.</li>
      <li><b>No visible steps.</b> Multi-step changes run under a still copy of the slide (and of Slides&rsquo; toolbar), so you see the result, not the steps.</li>
      <li><b>One-press undo</b> counts the Slides steps each change took and replays exactly that many, only while the slide still matches the change.</li>
      <li><b>Theme objects</b> are found with Select all: anything it doesn&rsquo;t reach is on the theme. The check reads until two passes agree, and it never marks an object as theme just because a click missed.</li>
      <li><b>The converter port</b> keeps the old one&rsquo;s exact rounding and parsing rules, and was checked against it on every SVG in our test set plus 3,000 random ones.</li>
    </ul>

    <h2 id="keys">Shortcuts</h2>
    <table><thead><tr><th>Action</th><th>Mac (Windows: Ctrl for &#8984;, Alt for &#8997;)</th></tr></thead><tbody>{keys13}</tbody></table>

    <h2 id="fixes">Smaller fixes</h2>
    <ul>
      <li>Layer tooltips no longer read &ldquo;undefined&rdquo;, and renaming a layer always ends with <kbd>Enter</kbd>, <kbd>Esc</kbd> or a click elsewhere.</li>
      <li>Objects are no longer flagged as theme objects or as too small to see by mistake.</li>
      <li>The align preview measures text boxes and Slides&rsquo; own shapes by their frames, not their drawn pixels.</li>
    </ul>

    <h2 id="limits">Known limits</h2>
    <ul>
      <li>Gradients, pattern fills, transparency and shadows don&rsquo;t carry through combine and outline. Images, video and charts can&rsquo;t be combined or outlined.</li>
      <li>Layer names, hidden layers, outlined-text memory and stroke-position memory are kept on the computer you used.</li>
      <li>Skew is in Edit Shape only. Only top-level layers drag to restack.</li>
      <li>One-press undo stops applying once you change the slide yourself.</li>
      <li>The pen draws point by point; there is no freehand pencil yet.</li>
    </ul>

    <h2 id="update">Getting 1.3</h2>
    <p>Chrome updates extensions on its own, usually within a few hours; check <b>chrome://extensions</b> for version 1.3.0. The update removes a permission, the converter server&rsquo;s address. What&rsquo;s left is access to Google Slides pages, where the tools run, and <b>storage</b>. It still has no access to your Google account.</p>
    <div class="rel">Version 1.2.0 &middot; November 2026</div>
    <p>Slides lets you recolour and resize a shape, but not reshape it. Version 1.2 added a vector editor that opens right on the slide, so you can move the points and curves of any shape and put it back where it was.</p>
    {video}
    <h2>Edit Shape</h2>
    <p>Double-click a shape, then click <b>Edit Shape</b>. The editor opens on top of the slide at the shape&rsquo;s exact size and position. Drag points and curve handles, add or remove points with the pen, and select several at once. Undo, redo and zoom work the way they do in Figma and Illustrator. Click <b>Done</b> and the shape updates in place, at the zoom you were editing at.</p>
    <h2>Round corners</h2>
    <p>On shapes with corners, small circles appear just inside each one. Drag a circle toward the middle to round it; a pill under the shape shows the radius in pixels, and you can type a value there instead. Select the whole shape, or several shapes, and every corner rounds together. Select one or a few points and only those corners change.</p>
    {corners}
    <h2>Layers stay put</h2>
    <p>Shapes that sit on top of the one you&rsquo;re editing stay visible while you work, so you can line things up against them. Click <b>Done</b> and each edited shape goes back to its place in the stack.</p>
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
    <h2>Editor shortcuts (1.2)</h2>
    <table><thead><tr><th>Action</th><th>How</th></tr></thead><tbody>{keys}</tbody></table>
    <p>1.2 added one Chrome permission, <b>storage</b>, used to remember that you had seen the update note.</p>
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
           "about": {"@id": C.SITE + "/#app"}, "dateModified": "2026-11-23"},
          ctx["crumbs"]([("What's new", "/whats-new")])]
    doc = shell(title="What's New in 1.4: Colour Picker, Gradients and Replace Colour in Google Slides | SVG to Slides",
                desc="SVG to Slides 1.4 adds a colour picker with opacity and eyedropper, a gradient builder, replace a colour across a slide or deck, live preview and adjustable image masks to Google Slides. 1.3 added the pen, layers and shape combining.",
                path="/whats-new", body=body, md="/whats-new.md", extra_css=ABOUT_CSS + WHATS_NEW_CSS, campaign="whats-new",
                ld_block=ctx["ld_block"](ld), tail=ctx["lottie_js"], **ctx["common"])
    md = f"""# What's new in SVG to Slides

## 1.4.0 (November 2026)

- Colour picker in the toolbar (Option+Shift+F for fill, Option+Shift+L for stroke): spectrum, hue and opacity sliders, eyedropper, hex field, the slide's colours and recent ones. With text highlighted it sets the colour of those words only. Colour changes are made on the object itself, so animation and links stay.
- Gradient builder: linear and radial, stops on a bar, an angle dial, a start point for radial. Results are native Slides gradients.
- Replace a colour: with nothing selected, pick a colour in use and what it becomes. Changes fills, strokes, gradient stops and text, inside groups too. "All slides" lists the deck's colours and runs across every slide; one Cmd+Z undoes it.
- Live preview: the slide shows the colour, opacity, gradient or stroke width while the panel is open.
- Mask image with shape (Option+Shift+K) keeps the shape on top as an unfilled outline, grouped with the masked picture. Double-click the group, or press Mask again, to move or resize the picture under its mask.
- SVG import: linear and radial gradients arrive as Slides gradients; opacity, fill-opacity and stroke-opacity come across. The web uploader still flattens gradients.
- From 1.3.1: icon sets drawn with strokes (Lucide, Feather, Heroicons outline, Tabler) import as shapes.
- Limits: a gradient on a shape with mixed text styles replaces the shape (animation lost); a fill on a whole mask group is refused; stroke widths outside Slides' presets replace the shape.
- Permissions unchanged: access to Google Slides pages, where the tools run, and storage.

## 1.3.0 (November 2026)

- One toolbar at the left of the slide canvas (Option+Backslash): Layers, Edit Shape, Pen, command palette, Arrange, Align, Combine, Group, Outline, fill and stroke. Tooltips show shortcuts.
- Pen (Option+Shift+P): click for corners, drag for curves (Option breaks handles, Shift constrains to 45 degrees), click the first point to close, Enter or Esc to leave open, Delete removes the last point. New paths start as a 2 px dark stroke with no fill. Done adds them in one undo step.
- Snapping in the editor: points, the lines through them, slide edges and centre (pink guides), whole pixels, and a grid of any size (Cmd+' toggles). Hold Cmd to ignore.
- Exact strokes: weight field in px with Option-drag scrubbing (Shift x10), stroke inside/centre/outside, typed width, height, rotation and corner radius in Edit Shape; Edit Shape's box scales, stretches, rotates and skews.
- Outline text (Option+Cmd+T, restores on the same computer) and outline stroke (Option+Cmd+O).
- Mask image with shape (Option+Shift+K): any shape, group or outlined text over a picture. The picture keeps its exact position and size. Rotated images not yet supported.
- Combine: union, subtract, intersect, exclude, on the slide or in Edit Shape. One-press undo/redo for multi-step changes.
- Align and distribute are instant and keep images intact; a single object, image included, aligns to the slide edges.
- Layers (Option+1): nested groups fold open, Cmd-click selects inside groups, rename, hide, restack, zoom to tiny objects. Theme objects are greyed with an M; a second click opens the theme builder on them (Option+Shift+M), where one change updates every slide using that layout or master.
- Command palette (Cmd+Backslash): every command and shortcut, searchable.
- Paste SVG code: SVG markup on the clipboard pastes as native shapes.
- Small SVGs keep full detail when enlarged later.
- 92% smaller (installed 14 MB to 1.1 MB): the converter is JavaScript now. No server, and the permission for its address is gone; files never leave the browser. Permissions left: access to Google Slides pages, where the tools run, and storage.
- Fixes: layer tooltips, layer rename, false theme and too-small flags, align preview measurement.

## 1.2.0 (November 2026)

- Edit Shape: double-click a shape, then click Edit Shape. A vector editor opens on the slide at the shape's exact size and position. Drag points and curve handles, add or remove points, multi-select, undo, redo, zoom. Done updates the shape in place.
- Round corners: on shapes with corners, drag a circle inside a corner or type a pixel radius. The whole shape or several shapes round every corner together; selected points round only those corners.
- Layers stay put: shapes above the one you're editing stay visible, and Done returns each shape to its place in the stack.
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
    <p>Since version 1.2 the extension also edits shapes. Double-click any shape and a vector editor opens on the slide, so you can move its points and curves. Version 1.3 adds a toolbar with a pen, outline text, image masks, union and subtract, a layers panel and a command palette. <a href="/whats-new">What&rsquo;s new</a>.</p>
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
SVG to Slides writes Google Slides' own clipboard shape format from your SVG's paths and hands it to Slides, which treats the result as native shapes. The extension converts inside your browser. Since 1.2 it also edits shapes: double-click any shape to move its points and curves. Version 1.3 adds a toolbar with a pen, outline text, image masks, union and subtract, a layers panel and a command palette ({C.SITE}/whats-new).

## Who builds it
Joe Gelman, independently. Contact: joe@glmn.co
"""
    return doc, md
