"""Do converted gradients look like their source? Converts a set of SVG gradient cases, redraws each
result the way Slides draws its gradient fills (line through the middle of the frame, w|cos|+h|sin|
long; radial from the middle or a corner), and reports the mean colour difference (0 to 255) between
the two renders, each cropped to its ink.

    CHROME=/path/to/chrome python3 tools/convert-corpus/gradients.py [out.png]
"""
import os, sys, json, math, base64, io
from PIL import Image, ImageChops, ImageStat
from playwright.sync_api import sync_playwright
REPO=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
MIME='application/x-vnd.google-docs-drawings-object+wrapped'
S=lambda body,vb='0 0 200 120': '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="%s">%s</svg>'%(vb,body)
CASES={
 'linear, left to right': S('<defs><linearGradient id="g"><stop offset="0" stop-color="#ff0000"/><stop offset="1" stop-color="#0000ff"/></linearGradient></defs><rect x="10" y="10" width="180" height="100" fill="url(#g)"/>'),
 'linear, diagonal, three stops': S('<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffcc00"/><stop offset=".4" stop-color="#ff0066"/><stop offset="1" stop-color="#3300aa"/></linearGradient></defs><rect x="10" y="10" width="180" height="100" rx="20" fill="url(#g)"/>'),
 'linear, user space, partial span': S('<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="60" y1="0" x2="120" y2="0"><stop offset="0" stop-color="#00aa55"/><stop offset="1" stop-color="#002244"/></linearGradient></defs><rect x="10" y="10" width="180" height="100" fill="url(#g)"/>'),
 'linear, gradientTransform rotate': S('<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="10" y1="60" x2="190" y2="60" gradientTransform="rotate(30 100 60)"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#cc0000"/></linearGradient></defs><ellipse cx="100" cy="60" rx="90" ry="50" fill="url(#g)"/>'),
 'linear, top to bottom, percent': S('<defs><linearGradient id="g" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" style="stop-color:#4285f4"/><stop offset="100%" style="stop-color:#0b3d91"/></linearGradient></defs><path d="M100 10 190 110H10Z" fill="url(#g)"/>'),
 'href chain': S('<defs><linearGradient id="a"><stop offset="0" stop-color="#111111"/><stop offset="1" stop-color="#eeeeee"/></linearGradient><linearGradient id="g" xlink:href="#a" x1="1" y1="0" x2="0" y2="0"/></defs><rect x="10" y="10" width="180" height="100" fill="url(#g)"/>'),
 'element transform': S('<defs><linearGradient id="g"><stop offset="0" stop-color="#ff8800"/><stop offset="1" stop-color="#220066"/></linearGradient></defs><rect x="-40" y="-25" width="80" height="50" transform="translate(100 60) rotate(90) scale(1.6)" fill="url(#g)"/>'),
 'radial, centred': S('<defs><radialGradient id="g"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#0044cc"/></radialGradient></defs><circle cx="100" cy="60" r="50" fill="url(#g)"/>'),
 'radial, small radius': S('<defs><radialGradient id="g" r=".3"><stop offset="0" stop-color="#ffee00"/><stop offset="1" stop-color="#aa0000"/></radialGradient></defs><rect x="40" y="10" width="100" height="100" fill="url(#g)"/>'),
 'radial, corner': S('<defs><radialGradient id="g" cx="0" cy="0" r="1.2"><stop offset="0" stop-color="#00ffcc"/><stop offset="1" stop-color="#001133"/></radialGradient></defs><rect x="40" y="10" width="100" height="100" fill="url(#g)"/>'),
 'stroke gradient': S('<defs><linearGradient id="g"><stop offset="0" stop-color="#ff0000"/><stop offset="1" stop-color="#0000ff"/></linearGradient></defs><path d="M20 100 100 20 180 100" fill="none" stroke="url(#g)" stroke-width="14" stroke-linejoin="round" stroke-linecap="round"/>'),
}
def slides_svg(r):
    out=[]; defs=[]; XS=[]; YS=[]
    for n,e in enumerate(r):
        if e[0]!=3: continue
        x,y,k=e[3][4],e[3][5],e[3][0]; d=dict(zip(e[4][0::2],e[4][1::2])); meta,co=d[12][0][2],d[12][0][3]
        w,h=d[8],d[9]; XS+=[x,x+w*k]; YS+=[y,y+h*k]
        i=0; s=''
        for op,c in zip(meta[0::2],meta[1::2]):
            q=co[i:i+c]; i+=c
            if op==0: s+='M%s %s'%(q[0],q[1])
            elif op==1: s+=''.join('L%s %s'%(q[j],q[j+1]) for j in range(0,c,2))
            elif op==3: s+=''.join('C%s %s %s %s %s %s'%tuple(q[j:j+6]) for j in range(0,c,6))
            elif op==5: s+='Z'
        fill=d[15]
        if 60 in d:
            st=''.join('<stop offset="%s" stop-color="%s"/>'%(p,c) for c,p in d[61])
            if d[60]==1:
                a=d[62]; L=w*abs(math.cos(a))+h*abs(math.sin(a)); cx,cy=w/2,h/2
                defs.append('<linearGradient id="s%d" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>'%(n,cx-L/2*math.cos(a),cy-L/2*math.sin(a),cx+L/2*math.cos(a),cy+L/2*math.sin(a),st))
            else:
                c=d.get(73,0); D=math.hypot(w,h); cx,cy,R=[(w/2,h/2,D/2),(0,0,D),(w,0,D),(0,h,D),(w,h,D)][c]
                defs.append('<radialGradient id="s%d" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s">%s</radialGradient>'%(n,cx,cy,R,st))
            fill='url(#s%d)'%n
        out.append('<path transform="translate(%s %s) scale(%s)" d="%s" fill="%s" fill-rule="evenodd"/>'%(x,y,k,s,fill))
    return out,defs,XS,YS
conv=open(REPO+'/extension/svg-convert.js').read(); geo=open(REPO+'/extension/geo-ops.js').read()
tiles=[]; worst=0
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('CHROME') or None)
    cv=b.new_page(); cv.set_content('<html></html>'); cv.add_script_tag(content=geo); cv.add_script_tag(content=conv)
    pg=b.new_page(viewport={'width':420,'height':130})
    for name,t in CASES.items():
        # the box has the viewBox's 200:120 shape, and maps 1 SVG unit to 1 pt
        r=cv.evaluate("([t])=>JSON.parse(JSON.parse(SVG2S_CONVERT.buildClipBundleAt([new TextEncoder().encode(t)],100,60,200,120,{})['%s']).data).resolved"%MIME,[t])
        paths,defs,XS,YS=slides_svg(r)
        kinds=sorted(set(dict(zip(e[4][0::2],e[4][1::2])).get(60,0) for e in r if e[0]==3))
        u=12700/25.0  # units per pt
        html='<html><body style="margin:0;background:#fff"><img style="position:absolute;left:5px;top:5px;width:200px;height:120px" src="data:image/svg+xml;base64,%s"><svg style="position:absolute;left:215px;top:5px" width="200" height="120" viewBox="0 0 %s %s"><defs>%s</defs>%s</svg></body></html>'%(base64.b64encode(t.encode()).decode(),200*u,120*u,''.join(defs),''.join(paths))
        pg.set_content(html, wait_until='load'); pg.wait_for_timeout(120)
        im=Image.open(io.BytesIO(pg.screenshot())).convert('RGB')
        def ink(t):
            bb=t.convert('L').point(lambda v:255 if v<250 else 0).getbbox()
            return t.crop(bb).resize((160,100)) if bb else t.resize((160,100))
        a=ink(im.crop((0,0,210,130))); c=ink(im.crop((210,0,420,130)))
        diff=sum(ImageStat.Stat(ImageChops.difference(a,c)).mean)/3
        worst=max(worst,diff); tiles.append(im)
        print('%-34s kinds %s  mean diff %.1f'%(name,kinds,diff))
    b.close()
print('worst %.1f'%worst)
if len(sys.argv)>1:
    sheet=Image.new('RGB',(420,130*len(tiles)),'white')
    for i,t in enumerate(tiles): sheet.paste(t,(0,130*i))
    sheet.save(sys.argv[1])
