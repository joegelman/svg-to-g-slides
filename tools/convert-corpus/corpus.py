"""Real-library corpus: how many icons convert to at least one shape, main vs working tree.

    npm i lucide-static heroicons feather-icons @tabler/icons bootstrap-icons   (in some folder)
    ICONS=/that/folder/node_modules python3 tools/convert-corpus/corpus.py

Counts shapes only. It does not judge how the result looks in Slides.
"""
import glob, json, os, random, subprocess, sys
from playwright.sync_api import sync_playwright
REPO=__import__('os').path.abspath(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','..')); MIME='application/x-vnd.google-docs-drawings-object+wrapped'
random.seed(13)
SETS={'Lucide':'ICONS//lucide-static/icons/*.svg','Feather':'ICONS//feather-icons/dist/icons/*.svg',
'Heroicons outline':'ICONS//heroicons/24/outline/*.svg','Heroicons solid':'ICONS//heroicons/24/solid/*.svg',
'Tabler outline':'ICONS//@tabler/icons/icons/outline/*.svg','Bootstrap Icons':'ICONS//bootstrap-icons/icons/*.svg'}
old=subprocess.check_output(['git','show','main:extension/svg-convert.js'],cwd=REPO).decode()
new=open(REPO+'/extension/svg-convert.js').read()
JS="""([t])=>{try{const by=new TextEncoder().encode(t);const o=SVG2S_CONVERT.buildClipBundleAt([by],480,270,192,108,{});const r=JSON.parse(JSON.parse(o['%s']).data).resolved;return r.filter(e=>e&&e[0]===3).length}catch(e){return -1}}"""%MIME
out={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=__import__('os').environ.get('CHROME') or None)
    pgs={}
    for k,src in (('1.3.0',old),('branch',new)):
        pg=b.new_page(); pg.set_content('<html></html>'); pg.add_script_tag(content=src); pg.add_script_tag(content=open(REPO+'/extension/geo-ops.js').read()); pgs[k]=pg
    for name,pat in SETS.items():
        fs=sorted(glob.glob(pat.replace('ICONS',os.environ.get('ICONS','node_modules')))); fs=random.sample(fs,min(200,len(fs)))
        res={}
        for k,pg in pgs.items():
            n=[pg.evaluate(JS,[open(f,encoding='utf-8').read()]) for f in fs]
            res[k]=(sum(1 for x in n if x>0), sum(1 for x in n if x==0), sum(1 for x in n if x<0))
        out[name]=(len(fs),res); print(name,len(fs),res)
    b.close()

