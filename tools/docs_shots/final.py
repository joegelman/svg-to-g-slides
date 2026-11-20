"""Capture every docs figure from the mock page (real extension UI)."""
import asyncio, json, sys
from shots import *
ED="document.getElementById('svg2slides-editor').shadowRoot"
ERAIL="()=>{const r="+ED+"; const out={}; r.querySelectorAll('[data-act]').forEach(b=>{const q=b.getBoundingClientRect(); if(q.width&&!out[b.dataset.act]) out[b.dataset.act]=[q.left,q.top,q.width,q.height];}); return out;}"
PALM=dict(svg=B.PALM, cx=205, cy=500, w=150, h=150)
PZ=dict(sx=-126, sy=-1216, sw=2600, extra=[PALM])
PALM_ID='ga0000000004'
W=dict(x=225,y=150,width=975,height=750)

async def cur(pg,x,y): await pg.evaluate(f"__cursor({x},{y})")

async def main(which):
    allf = not which
    async with async_playwright() as pw:
        if allf or 'closed' in which:
            b,pg=await page(pw, {})
            await pg.evaluate("__callouts([[1,246,226,275,226]])")
            await shot(pg,'toolbar-closed', dict(x=225,y=150,width=700,height=300)); await b.close()
        if allf or 'open' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await select(pg, [LOGO_ID])
            L,R=258,390
            co=[[1,L,226,289,226],[3,L,260,289,260],[5,L,294,289,294],[6,L,337,289,337],[8,L,397,289,397],[9,L,475,289,475],[10,L,534,289,534],[11,L,577,289,577],[12,L,609,289,609],[13,L,641,289,641],
                [2,R,226,359,226],[4,R,260,359,260],[7,R,337,359,337]]
            await pg.evaluate(f"__callouts({json.dumps(co)})")
            await shot(pg,'toolbar-open', dict(x=225,y=150,width=700,height=540)); await b.close()
        if allf or 'tip' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await select(pg, [LOGO_ID])
            r=await pg.evaluate(RAIL_JS); x,y=mid(r['pen']); await pg.mouse.move(x,y); await pg.wait_for_timeout(900); await cur(pg,x+3,y+4)
            await shot(pg,'toolbar-tooltip', dict(x=225,y=150,width=700,height=300)); await b.close()
        if allf or 'align' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await select(pg, ['g_title','g_date', LOGO_ID])
            r=await pg.evaluate(RAIL_JS); x,y=mid(r['align']); await pg.mouse.click(x,y); await pg.wait_for_timeout(400)
            f=await rect(pg,'.fly [data-act="alignHCenter"]')
            await pg.mouse.move(*mid(f)); await pg.wait_for_timeout(800); await cur(pg,mid(f)[0]+3,mid(f)[1]+4)
            await shot(pg,'align-flyout', dict(x=225,y=150,width=700,height=420)); await b.close()
        if allf or 'palette' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await select(pg, [LOGO_ID])
            await pg.evaluate("SVG2S_SHAPES.command('palette')"); await pg.wait_for_timeout(600)
            await shot(pg,'command-palette', W); await b.close()
        if allf or 'layers' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False,'layerNames':NAMES})
            await pg.evaluate("SVG2S_SHAPES.command('layers')"); await pg.wait_for_timeout(1500)
            tw=await rect(pg,'.panel .row:nth-child(3) .tw'); print('tw',tw)
            if tw: await pg.mouse.click(*mid(tw)); await pg.wait_for_timeout(700)
            rows=await pg.evaluate("()=>[..."+SR+".querySelectorAll('.panel .row')].map(r=>{const q=r.getBoundingClientRect(); return [r.textContent.trim().slice(0,30), r.className, Math.round(q.top), Math.round(q.height)];})")
            print(rows)
            photo=[r for r in rows if r[0].startswith('Beach')]
            if photo:
                y=photo[0][2]+photo[0][3]/2; await pg.mouse.move(120,y); await pg.wait_for_timeout(500)
                eye=await pg.evaluate("()=>{const e=[..."+SR+".querySelectorAll('.panel .row')].find(r=>r.textContent.includes('Beach')); const b=e&&[...e.querySelectorAll('*')].map(x=>[x.className, Math.round(x.getBoundingClientRect().left), Math.round(x.getBoundingClientRect().width), getComputedStyle(x).opacity, getComputedStyle(x).visibility]); return b;}")
                print('eye',eye)
            await shot(pg,'layers-raw', dict(x=0,y=150,width=925,height=520)); await b.close()
        if allf or 'edit' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False}, **PZ)
            await select(pg, [PALM_ID])
            await pg.evaluate("SVG2S_SHAPES.command('edit')"); await pg.wait_for_timeout(1500)
            pts=await pg.evaluate("()=>[..."+ED+".querySelectorAll('g.anchors circle, g.anchors rect')].map(e=>{const q=e.getBoundingClientRect(); return [q.left+q.width/2,q.top+q.height/2,e.tagName];})")
            print(len(pts), 'anchors')
            # pick a smooth point (circle) on the right side of the shape, away from clutter
            cs=sorted([p for p in pts if p[2]=='circle'], key=lambda p:-p[0])
            p=cs[0]; await pg.mouse.click(p[0],p[1]); await pg.wait_for_timeout(500)
            await cur(pg,p[0]+4,p[1]+5)
            r=await pg.evaluate(ERAIL); print(json.dumps({k:[round(v) for v in val] for k,val in r.items()}))
            await shot(pg,'edit-shape-raw', W); await b.close()
        if allf or 'snap' in which:
            b,pg=await page(pw, {'shapeToolsCollapsed':False})
            await pg.evaluate("__select([])"); await pg.evaluate("SVG2S_SHAPES.command('pen')"); await pg.wait_for_timeout(1300)
            r=await pg.evaluate(ERAIL); x,y=mid(r['snap']); await pg.mouse.click(x,y); await pg.wait_for_timeout(600)
            fl=await pg.evaluate("()=>{const f="+ED+".querySelector('.fly.show'); if(!f) return null; return [...f.querySelectorAll('[data-act]')].map(b=>{const q=b.getBoundingClientRect(); return [b.dataset.act,b.dataset.tip,Math.round(q.left),Math.round(q.top),Math.round(q.width)];});}")
            print('snapfly',fl)
            await shot(pg,'snap-raw', dict(x=225,y=150,width=700,height=420)); await b.close()
if __name__=="__main__": asyncio.run(main(sys.argv[1:]))
