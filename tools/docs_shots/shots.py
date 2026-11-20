import asyncio, json, sys, os
from pathlib import Path
from playwright.async_api import async_playwright
import build as B
CHROME=B.CHROME
OUT=B.OUT; OUT.mkdir(parents=True, exist_ok=True)
LOGO_ID='ga0000000003'
NAMES={'deck':{LOGO_ID:'Vacay logo','g_photo':'Beach photo'}}
SR="document.getElementById('svg2slides-shape-tools').shadowRoot"
RAIL_JS="()=>{const r="+SR+"; const out={}; r.querySelectorAll('.rail [data-act]').forEach(b=>{const q=b.getBoundingClientRect(); if(q.width) out[b.dataset.act]=[q.left,q.top,q.width,q.height];}); return out;}"

async def page(pw, store, **kw):
    p=OUT/'_h.html'; p.write_text(B.build(store=store, **kw))
    b=await pw.chromium.launch(executable_path=CHROME)
    pg=await b.new_page(viewport={'width':1200,'height':900}, device_scale_factor=2)
    pg.on('pageerror', lambda e: print('PAGEERROR', str(e)[:300]))
    await pg.goto('file://'+str(p)); await pg.wait_for_timeout(1800)
    return b,pg

async def shot(pg, name, clip=None):
    await pg.screenshot(path=str(OUT/f'{name}.png'), clip=clip); print('shot', name)

async def select(pg, ids):
    await pg.evaluate(f"__select({json.dumps(ids)})")
    await pg.mouse.move(1190,160); await pg.mouse.down(); await pg.mouse.up()   # trusted mouseup -> the toolbar refreshes its states
    await pg.evaluate(f"__select({json.dumps(ids)})"); await pg.wait_for_timeout(500)

async def rect(pg, sel, root=SR):
    return await pg.evaluate("(s)=>{const e="+root+".querySelector(s); if(!e) return null; const q=e.getBoundingClientRect(); return [q.left,q.top,q.width,q.height];}", sel)

def mid(r): return (r[0]+r[2]/2, r[1]+r[3]/2)

async def main(which):
    async with async_playwright() as pw:
        if 'closed' in which:
            b,pg=await page(pw, {})
            await pg.evaluate("__callouts([[1,246,226,275,226]])")
            await shot(pg,'toolbar-closed', dict(x=225,y=150,width=700,height=300)); await b.close()
        if 'open' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await select(pg, ['g_photo', LOGO_ID])
            L,R=258,390
            co=[[1,L,226,289,226],[3,L,260,289,260],[5,L,294,289,294],[6,L,337,289,337],[8,L,397,289,397],[9,L,475,289,475],[10,L,534,289,534],[11,L,577,289,577],[12,L,609,289,609],[13,L,641,289,641],
                [2,R,226,359,226],[4,R,260,359,260],[7,R,337,359,337]]
            await pg.evaluate(f"__callouts({json.dumps(co)})")
            await shot(pg,'toolbar-open', dict(x=225,y=150,width=700,height=540)); await b.close()
        if 'align' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await select(pg, ['g_title','g_date', LOGO_ID])
            r=await pg.evaluate(RAIL_JS); x,y=mid(r['align']); await pg.mouse.click(x,y); await pg.wait_for_timeout(400)
            f=await rect(pg,'.fly [data-act="alignHCenter"]'); print('fly',f)
            if f: await pg.mouse.move(*mid(f)); await pg.wait_for_timeout(700); await pg.evaluate(f"__cursor({mid(f)[0]},{mid(f)[1]})")
            await shot(pg,'align-flyout', dict(x=225,y=150,width=700,height=420)); await b.close()
        if 'tip' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await select(pg, [LOGO_ID])
            r=await pg.evaluate(RAIL_JS); x,y=mid(r['pen']); await pg.mouse.move(x,y); await pg.wait_for_timeout(800); await pg.evaluate(f"__cursor({x},{y})")
            await shot(pg,'toolbar-tooltip', dict(x=225,y=150,width=700,height=300)); await b.close()
        if 'palette' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await select(pg, [LOGO_ID])
            await pg.evaluate("SVG2S_SHAPES.command('palette')"); await pg.wait_for_timeout(600)
            await shot(pg,'command-palette', dict(x=225,y=150,width=975,height=750))
            await pg.keyboard.type('al'); await pg.wait_for_timeout(400)
            await shot(pg,'command-palette-filter', dict(x=225,y=150,width=975,height=750)); await b.close()
        if 'layers' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False,'layerNames':NAMES})
            await pg.evaluate("SVG2S_SHAPES.command('layers')"); await pg.wait_for_timeout(1500)
            rows=await pg.evaluate("()=>[..."+SR+".querySelectorAll('.panel .row')].map(r=>{const q=r.getBoundingClientRect(); return [r.textContent.trim().slice(0,40), r.className, q.left,q.top,q.width,q.height, r.innerHTML.slice(0,300)];})")
            for r_ in rows: print(r_[:6])
            print(rows[0][6] if rows else None)
            await shot(pg,'layers-raw', dict(x=0,y=150,width=925,height=560)); await b.close()
if __name__=="__main__": asyncio.run(main(sys.argv[1:]))
