"""Drive the shape tools against tools/fake-slides/fake.html (a stand-in for the Slides page).
Checks the colour picker, gradient builder and the adjust-picture-under-mask mode end to end:
what shows, and what would be pasted back into the deck.

    CHROME=/path/to/chrome python3 tools/fake-slides/run.py [screenshot-dir]
"""
import os, sys, json
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); EXT=os.path.join(HERE,'..','..','extension')
OUT=sys.argv[1] if len(sys.argv)>1 else None
fails=[]
def check(name, ok, detail=''):
    print(('ok   ' if ok else 'FAIL ')+name+(' :: '+str(detail) if detail and not ok else ''))
    if not ok: fails.append(name)
RECT=lambda id,x,y,props:[3,id,1,[1,0,0,1,x,y],[8,80000,9,50000,12,[[1,1,[0,2,1,6,5,0],[0,0,80000,0,80000,50000,0,50000],[],0]]]+props]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('CHROME') or None)
    pg=b.new_page(viewport={'width':1280,'height':680})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.goto('file://'+os.path.join(HERE,'fake.html')); pg.wait_for_function('window.FAKE&&FAKE.ready')
    for f in ['shared.js','slides-bridge.js','rail-kit.js','svg-editor.js','geo-ops.js','fontkit.js','shape-tools.js']:
        pg.add_script_tag(content=open(os.path.join(EXT,f)).read())
    objs=[RECT('a',20000,20000,[14,1,15,'#4285F4',19,'#202124',22,762]), RECT('b',130000,20000,[14,1,15,'#EA4335',18,0]),
          RECT('pic',240000,20000,[49,'blob1',86,1,87,300,88,400,79,1.6,80,1.92,84,-0.3,85,-0.46])]
    pg.evaluate('(o)=>{FAKE.objs=o;FAKE.render()}',objs)
    pg.wait_for_selector('#svg2slides-shape-tools', state='attached', timeout=8000)
    sh=lambda sel: pg.locator('#svg2slides-shape-tools').locator(sel)
    shot=lambda n: OUT and pg.screenshot(path=os.path.join(OUT,n+'.png'))
    pasted=lambda: pg.evaluate('()=>FAKE.pastes[FAKE.pastes.length-1]')
    props=lambda e: dict(zip(e[4][0::2],e[4][1::2]))
    # ── fill: solid with opacity
    pg.mouse.click(230+40+80,60+30+90); pg.wait_for_timeout(300)
    pg.evaluate("()=>SVG2S_SHAPES.command('fill')"); pg.wait_for_timeout(400)
    check('picker opens', sh('.cpop').count()==1)
    check('reads the current fill', sh('.cpop .hex').input_value().upper()=='4285F4', sh('.cpop .hex').input_value() if sh('.cpop').count() else '')
    shot('picker-solid')
    sh('.cpop .hex').fill('0f9d58'); sh('.cpop .f input').first.fill('60'); pg.wait_for_timeout(100)
    sh('.cpop .pb.ok').click(); pg.wait_for_timeout(2500)
    d=props(pasted()[0]) if pasted() else {}
    check('solid fill and opacity pasted', d.get(15)=='#0F9D58' and d.get(16)==0.6 and d.get(14)==1, d)
    check('stroke left alone', d.get(19)=='#202124' and d.get(22)==762, d)
    # ── fill: linear gradient with an added stop
    pg.evaluate("()=>SVG2S_SHAPES.command('fill')"); pg.wait_for_timeout(400)
    sh('.cpop [data-mode="linear"]').click(); pg.wait_for_timeout(100)
    bar=sh('.cpop .gbar').bounding_box()
    pg.mouse.click(bar['x']+bar['width']*0.5, bar['y']+bar['height']/2); pg.wait_for_timeout(100)
    sh('.cpop .hex').fill('ffffff'); sh('.cpop [data-ang="45"]').click(); pg.wait_for_timeout(100)
    shot('picker-linear')
    check('three stops on the bar', sh('.cpop .st').count()==3)
    sh('.cpop .pb.ok').click(); pg.wait_for_timeout(2500)
    d=props(pasted()[0])
    check('linear gradient pasted', d.get(60)==1 and len(d.get(61,[]))==3 and d[61][0][1]==0 and d[61][-1][1]==1 and d[61][1][0]=='#FFFFFF' and abs(d.get(62,0)-0.7854)<1e-3 and d.get(145)==1, d)
    # ── reopen: state read back; radial from a corner; remove a stop; cancel changes nothing
    pg.evaluate("()=>SVG2S_SHAPES.command('fill')"); pg.wait_for_timeout(400)
    check('gradient read back', sh('.cpop').get_attribute('data-mode')=='linear' and sh('.cpop .st').count()==3)
    n=pg.evaluate('()=>FAKE.pastes.length'); sh('.cpop [data-mode="radial"]').click(); sh('.cpop .pb.no').click(); pg.wait_for_timeout(600)
    check('cancel pastes nothing', pg.evaluate('()=>FAKE.pastes.length')==n)
    pg.evaluate("()=>SVG2S_SHAPES.command('fill')"); pg.wait_for_timeout(400)
    sh('.cpop [data-mode="radial"]').click(); sh('.cpop .cgrid [data-c="4"]').click(); sh('.cpop .st').nth(1).click(); sh('.cpop').press('Delete'); pg.wait_for_timeout(100)
    shot('picker-radial')
    sh('.cpop').press('Enter'); pg.wait_for_timeout(2500)
    d=props(pasted()[0])
    check('radial gradient from a corner pasted', d.get(60)==2 and d.get(73)==4 and len(d.get(61,[]))==2, d)
    # ── stroke: none, then a colour
    pg.evaluate("()=>SVG2S_SHAPES.command('stroke')"); pg.wait_for_timeout(400)
    check('stroke picker has no gradient tabs', sh('.cpop [data-mode="linear"]').count()==0)
    sh('.cpop [data-mode="none"]').click(); sh('.cpop .pb.ok').click(); pg.wait_for_timeout(2500)
    d=props(pasted()[0]); check('stroke off pasted', d.get(18)==0 and 19 not in d, d)
    pg.evaluate("()=>SVG2S_SHAPES.command('stroke')"); pg.wait_for_timeout(400)
    sh('.cpop .hex').fill('#f00'); sh('.cpop .pb.ok').click(); pg.wait_for_timeout(2500)
    d=props(pasted()[0]); check('stroke colour pasted, weight kept', d.get(18)==1 and d.get(19)=='#FF0000' and d.get(22)==762 and d.get(60)==2, d)
    # ── mask adjust
    pg.mouse.click(230+40+240000*0.0026246719+60,60+30+20000*0.0026246719+40); pg.wait_for_timeout(300)
    check('masked picture selected', pg.evaluate('()=>FAKE.sel.join()')=='pic', pg.evaluate('()=>FAKE.sel.join()'))
    pg.evaluate("()=>SVG2S_SHAPES.command('mask')"); pg.wait_for_timeout(500)
    check('adjust mode opens', sh('.madj').count()==1 and sh('.apill').count()==1)
    shot('mask-adjust')
    n=pg.evaluate('()=>FAKE.pastes.length')
    cx=230+40+(240000+40000)*0.0026246719; cy=60+30+(20000+25000)*0.0026246719
    pg.mouse.move(cx,cy); pg.mouse.down(); pg.mouse.move(cx+30,cy+12,steps=4); pg.mouse.up(); pg.wait_for_timeout(100)
    shot('mask-adjust-moved')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(600)
    check('Esc closes and pastes nothing', sh('.madj').count()==0 and pg.evaluate('()=>FAKE.pastes.length')==n)
    check('picture shows again after cancel', pg.evaluate("()=>document.getElementById('editor-pic').style.visibility")!='hidden')
    pg.evaluate("()=>SVG2S_SHAPES.command('mask')"); pg.wait_for_timeout(500)
    pg.mouse.move(cx,cy); pg.mouse.down(); pg.mouse.move(cx+30,cy+12,steps=4); pg.mouse.up(); pg.wait_for_timeout(100)
    sh('.apill .pb.ok').click(); pg.wait_for_timeout(2500)
    d=props(pasted()[0]); dx=30/0.0026246719/80000; dy=12/0.0026246719/50000
    check('move saved as new offsets, size unchanged', abs(d.get(84,9)-(-0.3+dx))<0.01 and abs(d.get(85,9)-(-0.46+dy))<0.01 and d.get(79)==1.6 and d.get(80)==1.92 and d.get(49)=='blob1', d)
    pg.evaluate("()=>SVG2S_SHAPES.command('mask')"); pg.wait_for_timeout(500)
    sh('.apill .tx').click(); pg.wait_for_timeout(100); shot('mask-adjust-fit'); pg.keyboard.press('Enter'); pg.wait_for_timeout(2500)
    d=props(pasted()[0])
    check('Fit covers the mask, centred, same proportions', abs(d.get(79,0)-1.0)<0.01 and abs(d.get(80,0)-1.2)<0.01 and abs(d.get(84,9))<0.01 and abs(d.get(85,9)+0.1)<0.01, d)
    real=[e for e in errs if 'favicon' not in e and 'Failed to load resource' not in e]
    check('no page errors', not real, real[:4])
    b.close()
print('%d failed'%len(fails)); sys.exit(1 if fails else 0)
