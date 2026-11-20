import sys, os, json, asyncio
from playwright.async_api import async_playwright
import build as B
CHROME=B.CHROME
LOT=open(B.NODE/'lottie-web/build/player/lottie.min.js').read()
HTML="""<!doctype html><html><head><style>html,body{margin:0;background:#fff;overflow:hidden}#a{width:%dpx;height:%dpx}</style>
<script>%s</script></head><body><div id="a"></div><script>
window.anim=lottie.loadAnimation({container:document.getElementById('a'),renderer:'svg',loop:false,autoplay:false,animationData:%s,rendererSettings:{preserveAspectRatio:'xMidYMid meet'}});
window.ready=new Promise(r=>anim.addEventListener('DOMLoaded',r));
</script></body></html>"""
async def main(path, outdir, W, frames, hide=None):
    d=json.load(open(path))
    if hide:
        d['layers']=[l for l in d['layers'] if not any((l.get('nm') or '').startswith(h) for h in hide)]
    H=round(W*d['h']/d['w'])
    os.makedirs(outdir, exist_ok=True)
    hp=os.path.join(outdir,'_p.html'); open(hp,'w').write(HTML%(W,H,LOT,json.dumps(d)))
    name=os.path.basename(path).replace('svgslides_','').replace('.json','')
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=CHROME)
        pg=await b.new_page(viewport={'width':W,'height':H})
        await pg.goto('file://'+os.path.abspath(hp)); await pg.evaluate('ready')
        await pg.wait_for_timeout(400)
        for f in frames:
            await pg.evaluate(f'anim.goToAndStop({f},true)')
            await pg.wait_for_timeout(60)
            await pg.screenshot(path=f'{outdir}/{name}_{f:04d}.png')
        await b.close()
if __name__=='__main__':
    a=sys.argv
    fr=[int(x) for x in a[4].split(',')]
    hide=a[5].split(',') if len(a)>5 and a[5] else None
    asyncio.run(main(a[1],a[2],int(a[3]),fr,hide))
