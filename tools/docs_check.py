"""Check the built docs: internal links and anchors resolve, ids are unique, JSON-LD parses, house rules hold."""
import re, json, sys, html
from pathlib import Path
ST=Path(__file__).resolve().parents[1]/'cloud'/'static'
def page_file(u):
    u=u.split('#')[0].split('?')[0]
    if u in ('','/'): return ST/'index.html'
    p=u.strip('/')
    if p.startswith('static/'): return ST/p[len('static/'):]
    if p.endswith('.md'): return ST/'md'/p
    for c in (ST/f'{p}.html', ST/p/'index.html'):
        if c.is_file(): return c
    if p in ('llms.txt','robots.txt','sitemap.xml','chrome','addon'): return ST/(p if '.' in p else p+'.html')
    return None
ids_cache={}
def ids(f):
    if f not in ids_cache: ids_cache[f]=set(re.findall(r'\bid="([^"]+)"', f.read_text()))
    return ids_cache[f]
bad=0; n=0; pages=sorted((ST/'docs').rglob('*.html'))
for f in pages:
    t=f.read_text()
    all_ids=re.findall(r'\bid="([^"]+)"', t)
    dup={i for i in all_ids if all_ids.count(i)>1}
    if dup: print('DUP ID', f.relative_to(ST), dup); bad+=1
    for m in re.finditer(r'href="([^"]+)"', t):
        h=html.unescape(m.group(1))
        if h.startswith(('http','mailto:','data:')): continue
        n+=1
        if h.startswith('#'):
            if h[1:] not in all_ids: print('BAD ANCHOR', f.relative_to(ST), h); bad+=1
            continue
        tf=page_file(h)
        if not tf or not tf.is_file(): print('BAD LINK', f.relative_to(ST), h); bad+=1; continue
        if '#' in h and tf.suffix=='.html':
            a=h.split('#',1)[1]
            if a not in ids(tf): print('BAD TARGET ANCHOR', f.relative_to(ST), h); bad+=1
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try: json.loads(m.group(1))
        except Exception as e: print('BAD JSON-LD', f.relative_to(ST), e); bad+=1
    body=re.sub(r'<style.*?</style>|<script.*?</script>','',t,flags=re.S)
    art=re.search(r'<article class="dxart">(.*?)</article>', body, re.S).group(1)
    txt=html.unescape(re.sub(r'<[^>]+>',' ',art))
    for pat,name in ((r'—','em dash'),(r'–','en dash'),(r'\bsimply\b','"simply"'),(r'\bseamless','"seamless"'),(r'\bpowerful\b','"powerful"'),(r'\beasily\b','"easily"')):
        for mm in re.finditer(pat, txt):
            print('STYLE', name, f.relative_to(ST), '...'+txt[max(0,mm.start()-50):mm.end()+30].replace('\n',' ')+'...'); bad+=1
    title=re.search(r'<title>(.*?)</title>',t).group(1); desc=re.search(r'<meta name="description" content="([^"]*)"',t).group(1)
    if len(html.unescape(title))>70: print('LONG TITLE', len(html.unescape(title)), f.relative_to(ST), title)
    if not 70<=len(html.unescape(desc))<=175: print('DESC LEN', len(html.unescape(desc)), f.relative_to(ST))
    if t.count('<h1')!=1: print('H1 COUNT', f.relative_to(ST), t.count('<h1')); bad+=1
    if 'rel="canonical"' not in t: print('NO CANONICAL', f); bad+=1
print(len(pages), "pages", n, "internal links checked;", bad, "problems")
sys.exit(1 if bad else 0)
