import asyncio, sys, base64
from pathlib import Path
from playwright.async_api import async_playwright
import build as B
CHROME=B.CHROME
NM=B.NODE/'@fontsource/overpass/files'
FONT=''.join(f"@font-face{{font-family:'Overpass';font-weight:{w};src:url(data:font/woff2;base64,{base64.b64encode((NM/f'overpass-latin-{w}-normal.woff2').read_bytes()).decode()})}}" for w in (600,700,800))
async def shot(url, out, selector=None, width=1200, height=900, dpr=2, full=False, clip=None, pad=0):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=CHROME)
        pg=await b.new_page(viewport={'width':width,'height':height}, device_scale_factor=dpr)
        await pg.route('**/*', lambda r: r.abort() if any(h in r.request.url for h in ('googleapis','gstatic','googletagmanager','cdnjs')) else r.continue_())
        await pg.goto(url); await pg.add_style_tag(content=FONT); await pg.wait_for_timeout(700)
        if selector:
            el=await pg.query_selector(selector); bb=await el.bounding_box()
            await pg.screenshot(path=out, clip=dict(x=max(0,bb['x']-pad),y=max(0,bb['y']-pad),width=bb['width']+2*pad,height=bb['height']+2*pad), full_page=True)
        else:
            await pg.screenshot(path=out, full_page=full, clip=clip)
        await b.close()
if __name__=='__main__':
    a=sys.argv
    asyncio.run(shot(a[1], a[2], a[3] if len(a)>3 and a[3] else None, int(a[4]) if len(a)>4 else 1200, int(a[5]) if len(a)>5 else 900, pad=int(a[6]) if len(a)>6 else 0))
