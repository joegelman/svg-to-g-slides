import asyncio, json, sys
from shots import *
from final import ED, ERAIL, PZ, PALM_ID, W, cur
async def main(which):
    allf = not which
    async with async_playwright() as pw:
        if allf or 'layers' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False,'layerNames':NAMES})
            await pg.evaluate("SVG2S_SHAPES.command('layers')"); await pg.wait_for_timeout(1500)
            tw=await rect(pg,'.panel .row:nth-child(3) .tw'); await pg.mouse.click(*mid(tw)); await pg.wait_for_timeout(700)
            await pg.mouse.move(120,360); await pg.wait_for_timeout(500); await cur(pg,150,366)
            X=252
            co=[[1,X,170,214,170],[2,X,210,150,210],[3,X,270,120,270],[4,X,315,110,315],[5,X,360,222,360],[6,X,390,196,390],[7,394,226,359,226]]
            ft=await rect(pg,'.panel .foot'); print('foot',ft)
            if ft: co.append([8,X,ft[1]+ft[3]/2,214,ft[1]+ft[3]/2])
            await pg.evaluate(f"__callouts({json.dumps(co)})")
            await shot(pg,'layers-panel', dict(x=0,y=150,width=760,height=750)); await b.close()
        if allf or 'edit' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False}, **PZ)
            await select(pg, [PALM_ID])
            await pg.evaluate("SVG2S_SHAPES.command('edit')"); await pg.wait_for_timeout(1500)
            pill=await rect(pg,'.rpill',ED); hint=await rect(pg,'.hint',ED); print('pill',pill,'hint',hint)
            L,R=258,392
            co=[[1,L,226,289,226],[2,R,226,359,226],[3,L,260,289,260],[4,L,455,289,455],[5,L,650,289,650],[6,L,688,289,688],[7,L,726,289,726],[8,R,726,359,726]]
            if pill: co.append([9,pill[0]-24,pill[1]+pill[3]/2,pill[0],pill[1]+pill[3]/2])
            if hint: co.append([10,hint[0]-24,hint[1]+hint[3]/2,hint[0],hint[1]+hint[3]/2])
            await pg.evaluate(f"__callouts({json.dumps(co)})")
            await shot(pg,'edit-shape', W)
            # detail: one smooth point selected, its two handles showing
            await pg.evaluate("__callouts([])")
            pts=await pg.evaluate("()=>[..."+ED+".querySelectorAll('g.anchors circle')].map(e=>{const q=e.getBoundingClientRect(); return [q.left+q.width/2,q.top+q.height/2];})")
            cand=[p for p in pts if 800<p[0]<1000 and 280<p[1]<420]
            cand.sort(key=lambda p:(p[1],-p[0])); p=cand[0]; print('pt',p)
            await pg.mouse.click(p[0],p[1]); await pg.wait_for_timeout(500); await cur(pg,p[0]+4,p[1]+5)
            hs=await pg.evaluate("()=>[..."+ED+".querySelectorAll('g.handles *')].map(e=>{const q=e.getBoundingClientRect(); return [e.tagName,Math.round(q.left+q.width/2),Math.round(q.top+q.height/2)];})")
            print('handles',hs[:8])
            await shot(pg,'edit-shape-point', dict(x=p[0]-260,y=p[1]-150,width=520,height=320)); await b.close()
        if allf or 'snap' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await pg.evaluate("__select([])"); await pg.evaluate("SVG2S_SHAPES.command('pen')"); await pg.wait_for_timeout(1300)
            r=await pg.evaluate(ERAIL); x,y=mid(r['snap']); await pg.mouse.click(x,y); await pg.wait_for_timeout(600)
            co=[[1,387,206,387,244],[2,421,206,421,244],[3,455,206,455,244],[4,512,206,512,246]]
            await pg.evaluate(f"__callouts({json.dumps(co)})")
            await shot(pg,'snapping-menu', dict(x=225,y=150,width=700,height=300))
            await pg.evaluate("__callouts([])")
            g=await rect(pg,'.fly.show [data-act="snapGrid"]',ED); await pg.mouse.click(*mid(g)); await pg.wait_for_timeout(400)
            await pg.mouse.click(700,560); await pg.wait_for_timeout(200)   # close the menu / first point? check
            await shot(pg,'pen-probe', W); await b.close()
asyncio.run(main(sys.argv[1:]))
