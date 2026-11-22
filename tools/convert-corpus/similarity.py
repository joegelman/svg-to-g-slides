"""How closely does each converted icon match its source? Renders both, crops to the ink, and reports
intersection over union per library (150 icons from each outline set), with conversion time.

    ICONS=/path/to/node_modules python3 tools/convert-corpus/similarity.py

Filled icon sets, which the stroke code does not touch, score 0.83 to 0.97 on this measure, so read
anything above about 0.8 as a match.
"""
import os
REPO=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
ICONS=os.environ.get("ICONS","node_modules")
import json,glob,random,base64,io
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
MIME='application/x-vnd.google-docs-drawings-object+wrapped'
random.seed(5)
SETS={'lucide':''+ICONS+'/lucide-static/icons/*.svg','feather':''+ICONS+'/feather-icons/dist/icons/*.svg','hero-outline':''+ICONS+'/heroicons/24/outline/*.svg','tabler':''+ICONS+'/@tabler/icons/icons/outline/*.svg','hero-solid':''+ICONS+'/heroicons/24/solid/*.svg','bootstrap':''+ICONS+'/bootstrap-icons/icons/*.svg'}
new=open(REPO+'/extension/svg-convert.js').read(); geo=open(REPO+'/extension/geo-ops.js').read()
def tight(im):
    g=im.convert('L').point(lambda v:255 if v<140 else 0)
    bb=g.getbbox()
    return g.crop(bb).resize((96,96)) if bb else None
res={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('CHROME') or None)
    cv=b.new_page(); cv.set_content('<html></html>'); cv.add_script_tag(content=new); cv.add_script_tag(content=geo)
    pg=b.new_page(viewport={'width':300,'height':150})
    for name,pat in SETS.items():
        fs=random.sample(sorted(glob.glob(pat)),150 if name in('lucide','feather','hero-outline','tabler') else 0); ious=[]; worst=[]
        import time; TT=[]
        if not fs: continue
        for f in fs:
            t=open(f,encoding='utf-8').read().replace('currentColor','#000')
            t0=time.time(); r=cv.evaluate("([t])=>JSON.parse(JSON.parse(SVG2S_CONVERT.buildClipBundleAt([new TextEncoder().encode(t)],480,270,192,108,{})['%s']).data).resolved"%MIME,[t])
            TT.append(time.time()-t0)
            paths=[]; XS=[]; YS=[]
            for e in r:
                if e[0]!=3: continue
                x,y,k=e[3][4],e[3][5],e[3][0]; pr=e[4]; d=dict(zip(pr[0::2],pr[1::2])); meta,co=d[12][0][2],[v*k for v in d[12][0][3]]
                XS+=[v+x for v in co[0::2]]; YS+=[v+y for v in co[1::2]]
                i=0; s=''
                for op,n in zip(meta[0::2],meta[1::2]):
                    c=co[i:i+n]; i+=n
                    if op==0: s+='M%s %s'%(c[0]+x,c[1]+y)
                    elif op==1: s+=''.join('L%s %s'%(c[q]+x,c[q+1]+y) for q in range(0,n,2))
                    elif op==3: s+=''.join('C%s %s %s %s %s %s'%tuple(c[q+j]+(x if j%2==0 else y) for j in range(6)) for q in range(0,n,6))
                    elif op==5: s+='Z'
                paths.append('<path d="%s" fill="#000" fill-rule="evenodd"/>'%s); dbg=s
            html='<html><body style="margin:0;background:#fff"><img style="position:absolute;left:10px;top:10px;width:128px;height:128px" src="data:image/svg+xml;base64,%s"><svg style="position:absolute;left:160px;top:10px" width="128" height="128" viewBox="%s %s %s %s">%s</svg></body></html>'%(base64.b64encode(t.encode()).decode(),min(XS or [0]),min(YS or [0]),(max(XS or [1])-min(XS or [0])) or 1,(max(YS or [1])-min(YS or [0])) or 1,''.join(paths))
            pg.set_content(html, wait_until="load"); pg.wait_for_timeout(120); (im0:=None)
            im=Image.open(io.BytesIO(pg.screenshot())).convert("RGB"); 
            a=tight(im.crop((0,0,150,150))); c=tight(im.crop((150,0,300,150)))
            if a is None or c is None: ious.append(0); worst.append((0,f)); continue
            inter=ImageChops.multiply(a,c).histogram()[255]; uni=ImageChops.lighter(a,c).histogram()[255]
            v=inter/max(uni,1); ious.append(v); worst.append((v,f.split('/')[-1]))
        worst.sort(); res[name]=(sum(ious)/len(ious), min(ious), worst[:3]); print(name, '%.3f'%res[name][0], '%.3f'%res[name][1], worst[:4], 'below0.8:',sum(1 for v in ious if v<0.8), 'ms avg/max: %d/%d'%(1000*sum(TT)/len(TT),1000*max(TT)))
    b.close()

