"""Mock Google Slides page that loads the real extension scripts (1.3.0) so the
toolbar, Layers panel, command palette and Edit Shape editor render as shipped.
The backdrop is Joe's shared shell; the slide is the Vacay cover."""
import base64, json, os, re
from pathlib import Path
# SVGX_TREE: the working tree that holds extension/ and svgslides_pmm_lottie_assets/ (default: this repo).
# SVGX_NODE: a node_modules folder with @fontsource/{roboto,nunito,overpass} and lottie-web.
REPO = Path(__file__).resolve().parents[2]
UP = Path(os.environ.get('SVGX_TREE', REPO))
NODE = Path(os.environ.get('SVGX_NODE', REPO / 'node_modules'))
OUT = Path(os.environ.get('SVGX_OUT', REPO / 'tools' / 'docs_shots' / 'out'))
CHROME = os.environ.get('SVGX_CHROME') or None  # None: Playwright's own Chromium
EXT = UP / 'extension'
AS = UP / 'svgslides_pmm_lottie_assets'
NM = NODE / '@fontsource'

def uri(p, mime=None):
    p = Path(p)
    mime = mime or {'png': 'image/png', 'svg': 'image/svg+xml', 'woff2': 'font/woff2', 'jpg': 'image/jpeg'}[p.suffix[1:]]
    return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()

from PIL import Image
import io
def photo(p, w):
    im = Image.open(p).convert('RGB'); im.thumbnail((w, w * 3))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=88)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

FONTS = ''.join(
    f"@font-face{{font-family:'{fam}';font-weight:{w};src:url({uri(NM / d / 'files' / f'{d}-latin-{w}-normal.woff2')})}}"
    for fam, d, ws in [('Roboto', 'roboto', (400, 500)), ('Google Sans', 'roboto', (400, 500)), ('Nunito', 'nunito', (400, 600, 800)), ('Overpass', 'overpass', (600, 700, 800))]
    for w in ws)

SCRIPTS = ['shared.js', 'svg-convert.js', 'slides-bridge.js', 'rail-kit.js', 'content.js', 'svg-editor.js', 'geo-ops.js', 'fontkit.js', 'shape-tools.js']
def script(name):
    return '<script>' + (EXT / name).read_text().replace('</script', '<\\/script') + '</script>'

LOGO = (AS / 'primary_graphics' / '20a_logo-full-original.svg').read_text()
PALM = (AS / 'primary_graphics' / '24_palm-edited.svg').read_text()
BEACH = photo(AS / 'beach-cover.png', 900)
COUPLE = photo(AS / 'couple-cover.png', 700)
T2 = uri(AS / 'vacay_slides_825x660' / '02_couple_825x660.png')
T3 = uri(AS / 'vacay_slides_825x660' / '03_stats_825x660.png')

HTML = r"""<!doctype html><html><head><meta charset="utf-8"><style>
%(fonts)s
html,body{margin:0;width:1200px;height:900px;overflow:hidden;background:#fff;font-family:Roboto,Arial,sans-serif}
#shell{position:absolute;left:0;top:0;width:1200px;height:900px}
#filmstrip{position:absolute;left:0;top:150px;width:225px;height:750px}
.th{position:absolute;left:52px;width:150px;height:120px;border-radius:6px;background:#fff center/cover;box-shadow:0 0 0 1px #d5d8dd}
.th.cur{box-shadow:0 0 0 3px #1a73e8}
.tn{position:absolute;left:30px;font:500 11px Roboto;color:#5f6368}
#workspace-container{position:absolute;left:275px;top:150px;width:925px;height:750px;overflow:hidden}
#workspace{position:relative;width:925px;height:750px;background:#F9FAFD}
#pages svg{position:absolute;left:0;top:0}
#selsvg{position:absolute;left:0;top:0;pointer-events:none}
.docs-texteventtarget-iframe{position:absolute;left:-2000px;top:0;width:10px;height:10px;border:0}
#callouts{position:fixed;inset:0;z-index:2147483647;pointer-events:none}
.co{position:absolute;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%%;background:#FFC700;color:#1c1e22;font:700 15px/27px Overpass,sans-serif;text-align:center;box-shadow:0 0 0 2px #fff,0 1px 4px rgba(0,0,0,.35)}
.cl{position:absolute;height:2px;background:#1c1e22;transform-origin:0 50%%;box-shadow:0 0 0 1px #fff}
#cursor{position:fixed;z-index:2147483646;width:22px;height:22px;pointer-events:none;display:none}
</style></head><body>
<img id="shell" src="%(shell)s" alt="">
<div id="filmstrip" class="filmstrip">
  <span class="tn" style="top:38px">1</span><div class="th cur" id="th1" style="top:32px"></div>
  <span class="tn" style="top:178px">2</span><div class="th" style="top:172px;background-image:url(%(t2)s)"></div>
  <span class="tn" style="top:318px">3</span><div class="th" style="top:312px;background-image:url(%(t3)s)"></div>
</div>
<div id="workspace-container"><div id="workspace"><div id="pages">
  <svg id="canvas" width="925" height="750" xmlns="http://www.w3.org/2000/svg"></svg>
  <svg id="selsvg" width="925" height="750" xmlns="http://www.w3.org/2000/svg"></svg>
</div></div></div>
<iframe class="docs-texteventtarget-iframe" srcdoc="<div contenteditable='true' role='textbox' aria-label='Document content'></div>"></iframe>
<div id="callouts"></div>
<svg id="cursor" viewBox="0 0 20 20"><path d="M4.5 1.5v15.3l3.9-3.7 2.6 5.8 2.2-1-2.6-5.6h5.3Z" fill="#111" stroke="#fff" stroke-width="1.2" stroke-linejoin="round"/></svg>
<script>
window.__ICON = "%(icon)s";
window.__STORE = %(store)s;
window.chrome = { storage: { local: {
  get(k, cb) { const o = {}; [].concat(k).forEach((x) => { if (x in __STORE) o[x] = __STORE[x]; }); setTimeout(() => cb && cb(o), 0); },
  set(o) { Object.assign(__STORE, o); }, remove(k) { delete __STORE[k]; } } },
  runtime: { getURL: () => __ICON } };
try { Object.defineProperty(navigator, 'platform', { get: () => '%(platform)s' }); } catch (e) {}
window.__SLIDE_X=%(sx)s; window.__SLIDE_Y=%(sy)s; window.__SLIDE_W=%(sw)s; window.__EXTRA=%(extra)s;
window.__LOGO = %(logo)s; window.__PALM = %(palm)s; window.__BEACH = "%(beach)s"; window.__COUPLE = "%(couple)s";
</script>
%(scripts)s
<script>
(function(){
  const NS='http://www.w3.org/2000/svg';
  const U=12700/30, PW=750*U, PH=600*U, S=__SLIDE_W/PW;      // page units, px per unit
  const px=(v)=>v/(825/PW);                             // design px (825-wide slide) -> units
  const canvas=document.getElementById('canvas');
  const page=document.createElementNS(NS,'g'); page.id='editor-p'; page.setAttribute('transform',`translate(${__SLIDE_X} ${__SLIDE_Y}) scale(${S})`);
  const bg=document.createElementNS(NS,'g'); bg.id='editor-p-bg';
  const bgp=document.createElementNS(NS,'path'); bgp.setAttribute('d',`M0 0H${PW}V${PH}H0Z`); bgp.setAttribute('fill','#ffffff'); bgp.setAttribute('stroke','#cccccc'); bgp.setAttribute('stroke-width',1.5/S); bg.append(bgp); page.append(bg); canvas.append(page);
  const M={ entries:new Map(), theme:new Set(), order:[] };
  window.__M=M; window.__sel=[];
  function g(id){ const e=document.createElementNS(NS,'g'); e.id='editor-'+id; return e; }
  function addText(id, txt, cx, y, size, weight, fill, theme){
    const e=g(id), p=g(id+'-paragraph-0'), t=document.createElementNS(NS,'text');
    t.textContent=txt; t.setAttribute('x',px(cx)); t.setAttribute('y',px(y)); t.setAttribute('text-anchor','middle');
    t.setAttribute('font-family','Nunito'); t.setAttribute('font-weight',weight); t.setAttribute('font-size',px(size)); t.setAttribute('fill',fill);
    if(/[A-Z]{4}/.test(txt)) t.setAttribute('letter-spacing',px(size*0.04));
    p.append(t); e.append(p); page.append(e);
    M.entries.set(id,[[3,id,108,[1,0,0,1,0,0],[]]]); if(theme) M.theme.add(id);
    return e;
  }
  function addImage(id, href, x,y,w,h){
    const e=g(id), im=document.createElementNS(NS,'image');
    im.setAttribute('href',href); im.setAttribute('x',px(x)); im.setAttribute('y',px(y)); im.setAttribute('width',px(w)); im.setAttribute('height',px(h));
    im.setAttribute('preserveAspectRatio','xMidYMid slice'); e.append(im); page.append(e);
    M.entries.set(id,[[3,id,3,[1,0,0,1,px(x),px(y)],[8,w,9,h]]]);
    return e;
  }
  function addRect(id,x,y,w,h,fill,theme){
    const e=g(id), p=document.createElementNS(NS,'path');
    p.setAttribute('d',`M${px(x)} ${px(y)}h${px(w)}v${px(h)}h${-px(w)}Z`); p.setAttribute('fill',fill); e.append(p); page.append(e);
    M.entries.set(id,[[3,id,1,[1,0,0,1,0,0],[]]]); if(theme) M.theme.add(id); return e;
  }
  function addSvg(svgText, cx, cy, w, h, parent){
    const pt=(v)=>v*750/825; // design px -> pt
    const resolved=SB.unwrap(SVG2S_CONVERT.buildClipBundleAt([svgText], pt(cx), pt(cy), pt(w), pt(h))[SB.MIME]);
    const by=new Map(resolved.map((e)=>[e[1],e]));
    const kidsOf=new Set(); resolved.forEach((e)=>{ if(e[0]===2) e[2].forEach((k)=>kidsOf.add(k)); });
    const build=(e)=>{
      const el=g(e[1]);
      if(e[0]===2){ e[2].forEach((k)=>el.append(build(by.get(k)))); return el; }
      // Slides draws every path in absolute page units, with no transform on the object's group.
      const rec=SB.pathRecord(e); const subs=SB.decodePath(rec[2],rec[3]);
      const p=document.createElementNS(NS,'path'); p.setAttribute('d',SB.svgPathD(subs,SB.localToPage(resolved,e)));
      const fill=SB.getProp(e[4],15); p.setAttribute('fill', SB.getProp(e[4],14)===0?'none':(fill||'#000'));
      p.setAttribute('fill-rule','nonzero'); el.append(p); return el;
    };
    const tops=resolved.filter((e)=>!kidsOf.has(e[1]));
    tops.forEach((e)=>{ (parent||page).append(build(e));
      const all=[]; const walk=(x)=>{ all.push(x); if(x[0]===2) x[2].forEach((k)=>walk(by.get(k))); }; walk(e); M.entries.set(e[1],all); });
    return tops.map((e)=>e[1]);
  }
  let idn=0; SVG2S_CONVERT._setIdSource(()=> 'ga'+String(++idn).padStart(10,'0'));
  // Theme objects first (bottom of the stack), then the slide's own.
  addRect('h_theme_bar', 40, 612, 325, 2, '#d9eef1', true);
  addText('h_theme_foot','vacay.com  ·  Confidential', 118, 636, 11, 600, '#7fa9b0', true);
  addImage('g_photo', __BEACH, 405, 0, 420, 660);
  M.logo = addSvg(__LOGO, 205, 215, 250, 120)[0];
  addText('g_title','INVESTOR PITCH DECK', 205, 340, 24, 800, '#302318');
  addText('g_date','AUGUST 2026', 205, 378, 17, 400, '#3E3027');
  (__EXTRA||[]).forEach((x)=>{ if(x.svg) addSvg(x.svg,x.cx,x.cy,x.w,x.h); });
  window.__addSvg=addSvg;
  // thumbnail of slide 1
  const th=document.getElementById('th1'); th.style.background='#fff';
  th.innerHTML=''; const ts=canvas.cloneNode(true); ts.removeAttribute('id'); ts.querySelectorAll('[id]').forEach((n)=>n.removeAttribute('id'));
  ts.setAttribute('viewBox',`${__SLIDE_X} ${__SLIDE_Y} ${__SLIDE_W} ${__SLIDE_W*0.8}`); ts.setAttribute('width','150'); ts.setAttribute('height','120'); ts.style.borderRadius='6px'; th.append(ts);

  // ── selection model ──
  const selsvg=document.getElementById('selsvg');
  const topId=(el)=>{ let n=el; let top=null; while(n&&n!==page){ if(n.id&&/^editor-/.test(n.id)&&!/-bg$|-paragraph/.test(n.id)) top=n; n=n.parentNode; } return top?top.id.slice(7):null; };
  function drawSel(){
    selsvg.textContent='';
    const wr=document.getElementById('workspace').getBoundingClientRect();
    __sel.forEach((id)=>{ const el=document.getElementById('editor-'+id); if(!el) return; const r=el.getBoundingClientRect();
      const x=r.left-wr.left,y=r.top-wr.top; const b=document.createElementNS(NS,'rect');
      b.setAttribute('x',x);b.setAttribute('y',y);b.setAttribute('width',r.width);b.setAttribute('height',r.height);b.setAttribute('fill','none');b.setAttribute('stroke','#1a73e8');b.setAttribute('stroke-width','1.5'); selsvg.append(b);
      [[0,0],[.5,0],[1,0],[0,.5],[1,.5],[0,1],[.5,1],[1,1]].forEach(([fx,fy])=>{ const h=document.createElementNS(NS,'rect'); h.setAttribute('x',x+fx*r.width-3.5);h.setAttribute('y',y+fy*r.height-3.5);h.setAttribute('width',7);h.setAttribute('height',7);h.setAttribute('fill','#fff');h.setAttribute('stroke','#1a73e8');h.setAttribute('stroke-width','1.5'); selsvg.append(h); });
    });
  }
  window.__select=(ids)=>{ window.__sel=ids.slice(); drawSel(); };
  document.getElementById('workspace-container').addEventListener('mousedown',(e)=>{
    const hit=document.elementsFromPoint(e.clientX,e.clientY).find((n)=>page.contains(n)&&n!==bgp);
    const id=hit&&topId(hit);
    if(!id||M.theme.has(id)){ if(!e.shiftKey) __select([]); return; }
    if(e.shiftKey){ if(!__sel.includes(id)) __select(__sel.concat(id)); } else __select([id]);
  },true);
  const ifr=document.querySelector('.docs-texteventtarget-iframe');
  const hook=()=>{ const d=ifr.contentDocument; const tb=d&&d.querySelector('[contenteditable]'); if(!tb){ setTimeout(hook,50); return; }
    d.addEventListener('copy',(e)=>{ if(!__sel.length) return; const res=[]; __sel.forEach((id)=>(M.entries.get(id)||[]).forEach((x)=>res.push(x)));
      e.clipboardData.setData(SB.MIME, SB.wrap(res)); e.preventDefault(); });
    d.addEventListener('keydown',(e)=>{ const own=SB.topLevelOrder().filter((id)=>!M.theme.has(id));
      if((e.metaKey||e.ctrlKey)&&(e.key==='a'||e.code==='KeyA')) __select(own);
      else if(e.key==='Escape') __select([]);
      else if(e.key==='Tab'){ const i=own.indexOf(__sel[0]); __select([own[(i+1)%%own.length]]); } });
  }; hook();
  // ── callouts and a pointer for figures ──
  window.__callouts=(list)=>{ const c=document.getElementById('callouts'); c.textContent='';
    list.forEach(([n,x,y,tx,ty])=>{ if(tx!=null){ const l=document.createElement('div'); l.className='cl'; const dx=tx-x,dy=ty-y; l.style.left=x+'px'; l.style.top=(y-1)+'px'; l.style.width=Math.hypot(dx,dy)+'px'; l.style.transform=`rotate(${Math.atan2(dy,dx)}rad)`; c.append(l); }
      const d=document.createElement('div'); d.className='co'; d.textContent=n; d.style.left=x+'px'; d.style.top=y+'px'; c.append(d); }); };
  window.__cursor=(x,y)=>{ const c=document.getElementById('cursor'); if(x==null){ c.style.display='none'; return; } c.style.display='block'; c.style.left=(x-4)+'px'; c.style.top=(y-2)+'px'; };
})();
</script></body></html>"""

def build(platform='MacIntel', store=None, sx=100, sy=61, sw=750, extra=None):
    return HTML % dict(fonts=FONTS, shell=uri(AS / 'shared_shell' / '08_composition 1.svg'), t2=T2, t3=T3,
                       icon=uri(EXT / 'icons' / 'icon48.png'), store=json.dumps(store or {}), platform=platform, sx=sx, sy=sy, sw=sw, extra=json.dumps(extra or []),
                       logo=json.dumps(LOGO), palm=json.dumps(PALM), beach=BEACH, couple=COUPLE,
                       scripts='\n'.join(script(s) for s in SCRIPTS))

if __name__ == '__main__':
    Path('harness.html').write_text(build(store={'shapeToolsCollapsed': False}))
    print('ok', Path('harness.html').stat().st_size)
