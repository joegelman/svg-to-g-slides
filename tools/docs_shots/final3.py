import asyncio, json, sys
from shots import *
from final import ED, ERAIL, W, cur
async def main(which):
    async with async_playwright() as pw:
        if 'pen' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await pg.evaluate("__select([])"); await pg.evaluate("SVG2S_SHAPES.command('pen')"); await pg.wait_for_timeout(1300)
            r=await pg.evaluate(ERAIL); sx,sy=mid(r['snap']); await pg.mouse.click(sx,sy); await pg.wait_for_timeout(500)
            g=await rect(pg,'.fly.show [data-act="snapGrid"]',ED); await pg.mouse.click(*mid(g)); await pg.wait_for_timeout(300)
            await pg.mouse.click(sx,sy); await pg.wait_for_timeout(400)   # close the snapping menu
            fly=await rect(pg,'.fly.show',ED); print('fly open?',fly)
            pts=[(470,612),(642,612),(642,702),(556,702),(522,748),(522,702),(470,702)]
            for (x,y) in pts:
                await pg.mouse.move(x-8,y-6); await pg.mouse.move(x,y); await pg.mouse.down(); await pg.mouse.up(); await pg.wait_for_timeout(180)
            await pg.mouse.move(476,640, steps=6); await pg.wait_for_timeout(500)
            n=await pg.evaluate("()=>"+ED+".querySelectorAll('g.anchors circle, g.anchors rect').length"); print('anchors',n)
            await shot(pg,'pen-drawing', dict(x=225,y=150,width=700,height=680)); await b.close()
        if 'drop' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await pg.mouse.move(560,640)
            await pg.evaluate("""()=>{ const dt=new DataTransfer(); dt.items.add(new File([__PALM],'palm.svg',{type:'image/svg+xml'}));
              document.dispatchEvent(new DragEvent('drop',{dataTransfer:dt,clientX:560,clientY:640,bubbles:true,cancelable:true})); }""")
            await pg.wait_for_timeout(600); await pg.mouse.move(566,646); await pg.mouse.move(560,640); await pg.wait_for_timeout(500)
            gh=await pg.evaluate("()=>{const g=document.getElementById('svg2slides-ghost'); return g?g.getBoundingClientRect().toJSON():null}"); print('ghost',gh)
            await cur(pg,560,640)
            await shot(pg,'insert-click-to-place', dict(x=225,y=150,width=700,height=680)); await b.close()
asyncio.run(main(sys.argv[1:]))
