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
    obj=lambda id: pg.evaluate("(id)=>FAKE.objs.find(o=>o[1]===id)||null",id)
    npaste=lambda: pg.evaluate('()=>FAKE.pastes.length')
    OP='input[aria-label="Opacity, percent"]'
    cmd=lambda a: (pg.evaluate("(a)=>{SVG2S_SHAPES.command(a)}",a), pg.wait_for_timeout(450))
    # ── fill: solid with opacity goes through Slides' own colour dialog; the object is never deleted
    pg.mouse.click(230+40+80,60+30+90); pg.wait_for_timeout(300)
    cmd('fill')
    check('picker opens', sh('.cpop').count()==1)
    check('reads the current fill', sh('.cpop .hex').input_value().upper()=='4285F4', sh('.cpop .hex').input_value() if sh('.cpop').count() else '')
    check('has the spectrum, hue and opacity controls', sh('.cpop .sv').count()==1 and sh('.cpop .sl.hue').count()==1 and sh('.cpop .sl.al').count()==1)
    shot('picker-solid')
    sv=sh('.cpop .sv').bounding_box(); pg.mouse.click(sv['x']+sv['width']*0.9, sv['y']+sv['height']*0.1); pg.wait_for_timeout(80)
    check('spectrum click changes the colour', sh('.cpop .hex').input_value().upper()!='4285F4', sh('.cpop .hex').input_value())
    hu=sh('.cpop .sl.hue').bounding_box(); pg.mouse.click(hu['x']+hu['width']*0.33, hu['y']+hu['height']/2); pg.wait_for_timeout(80)
    h1=sh('.cpop .hex').input_value().upper(); check('hue slider moves to green', int(h1[2:4],16)>int(h1[0:2],16) and int(h1[2:4],16)>int(h1[4:6],16), h1)
    alb=sh('.cpop .sl.al').bounding_box(); pg.mouse.click(alb['x']+alb['width']*0.5, alb['y']+alb['height']/2); pg.wait_for_timeout(80)
    check('opacity slider sets the field', abs(float(sh('.cpop '+OP).input_value())-50)<=2, sh('.cpop '+OP).input_value())
    sh('.cpop .hex').fill('0f9d58'); sh('.cpop '+OP).fill('60'); pg.wait_for_timeout(100)
    n=npaste(); sh('.cpop .pb.ok').click(); pg.wait_for_timeout(1800)
    d=props(obj('a')) if obj('a') else {}
    check('solid fill and opacity set, same object, nothing pasted', d.get(15)=='#0F9D58' and d.get(16)==0.6 and npaste()==n, (d, pg.evaluate('()=>FAKE.native')))
    check('went through the fill dialog with #rrggbbaa, Solid tab found', pg.evaluate('()=>FAKE.native.slice(-1)[0]')=='fill:#0f9d5899' and pg.evaluate('()=>FAKE.tab')=='Solid', pg.evaluate('()=>FAKE.native'))
    check('stroke left alone', d.get(19)=='#202124' and d.get(22)==762, d)
    check('no menu or dialog left open', pg.locator('.goog-menu, .docs-material-gm-dialog').count()==0)
    # ── fill: linear gradient with an added stop, through paint format (the object stays)
    cmd('fill')
    sh('.cpop [data-mode="linear"]').click(); pg.wait_for_timeout(100)
    bar=sh('.cpop .gbar').bounding_box()
    pg.mouse.click(bar['x']+bar['width']*0.5, bar['y']+bar['height']/2); pg.wait_for_timeout(100)
    sh('.cpop .hex').fill('ffffff'); sh('.cpop [data-ang="45"]').click(); pg.wait_for_timeout(100)
    shot('picker-linear')
    bb=sh('.cpop').bounding_box(); check('panel stays inside the window after it grows', bb['y']>=0 and bb['y']+bb['height']<=680 and bb['x']+bb['width']<=1280, bb)
    check('three stops on the bar', sh('.cpop .st').count()==3)
    count=pg.evaluate('()=>FAKE.objs.length'); sh('.cpop .pb.ok').click(); pg.wait_for_timeout(2600)
    d=props(obj('a')) if obj('a') else {}
    check('linear gradient on the same object', d.get(60)==1 and len(d.get(61,[]))==3 and d[61][0][1]==0 and d[61][-1][1]==1 and d[61][1][0]=='#FFFFFF' and abs(d.get(62,0)-0.7854)<1e-3, d)
    check('the temporary copy is gone', pg.evaluate('()=>FAKE.objs.length')==count and pg.evaluate('()=>FAKE.fmtPastes')==1, pg.evaluate('()=>FAKE.objs.map(o=>o[1])'))
    check('the shape is selected again', pg.evaluate('()=>FAKE.sel.join()')=='a', pg.evaluate('()=>FAKE.sel.join()'))
    # ── reopen: state read back; cancel changes nothing; radial from a corner
    cmd('fill')
    check('gradient read back', sh('.cpop').get_attribute('data-mode')=='linear' and sh('.cpop .st').count()==3)
    before=json.dumps(obj('a')); sh('.cpop [data-mode="radial"]').click(); sh('.cpop .pb.no').click(); pg.wait_for_timeout(600)
    check('cancel changes nothing', json.dumps(obj('a'))==before)
    cmd('fill')
    sh('.cpop [data-mode="radial"]').click(); sh('.cpop .cgrid [data-c="4"]').click(); sh('.cpop .st').nth(1).click(); sh('.cpop').press('Delete'); pg.wait_for_timeout(100)
    shot('picker-radial')
    sh('.cpop').press('Enter'); pg.wait_for_timeout(2600)
    d=props(obj('a')) if obj('a') else {}
    check('radial gradient from a corner', d.get(60)==2 and d.get(73)==4 and len(d.get(61,[]))==2, d)
    # ── stroke: none through Transparent, then a colour through the border dialog (#rrggbb)
    cmd('stroke')
    check('stroke picker has no gradient tabs', sh('.cpop [data-mode="linear"]').count()==0)
    sh('.cpop [data-mode="none"]').click(); sh('.cpop .pb.ok').click(); pg.wait_for_timeout(1500)
    d=props(obj('a')); check('stroke off', d.get(18)==0, (d, pg.evaluate('()=>FAKE.native')))
    cmd('stroke')
    sh('.cpop .hex').fill('#f00'); sh('.cpop .pb.ok').click(); pg.wait_for_timeout(1800)
    d=props(obj('a')); check('stroke colour set with a six-digit hex, gradient fill untouched', d.get(18)==1 and d.get(19)=='#FF0000' and d.get(60)==2 and pg.evaluate('()=>FAKE.native.slice(-1)[0]')=='stroke:#ff0000', (d, pg.evaluate('()=>FAKE.native')))
    # ── highlighted text: the colour goes to the text
    pg.evaluate('()=>{FAKE.textRange=true}')
    cmd('fill')
    check('with text highlighted the panel is for text colour', sh('.cpop').get_attribute('aria-label')=='Text colour' and not sh('.cpop .sl.al').is_visible(), sh('.cpop').get_attribute('aria-label') if sh('.cpop').count() else None)
    sh('.cpop .hex').fill('00897b'); sh('.cpop .pb.ok').click(); pg.wait_for_timeout(1500)
    check('text colour set through the text colour dialog', pg.evaluate('()=>FAKE.textColour')=='#00897B', pg.evaluate('()=>FAKE.native'))
    check('the box fill was not touched', props(obj('a')).get(60)==2)
    pg.evaluate('()=>{FAKE.textRange=false}')
    # ── nothing selected: replace a colour everywhere on the slide
    pg.evaluate("()=>{FAKE.objs.push([3,'c',1,[1,0,0,1,130000,90000],[8,80000,9,50000,12,[[1,1,[0,2,1,6,5,0],[0,0,80000,0,80000,50000,0,50000],[],0]],14,1,15,'#34A853',18,1,19,'#EA4335',22,1500]]);FAKE.sel=[];FAKE.render()}")
    pg.wait_for_timeout(300)
    cmd('fill')
    check('with nothing selected the panel offers to replace a colour', sh('.cpop').get_attribute('aria-label')=='Replace a colour' and sh('.cpop .pb.ok').is_disabled(), sh('.cpop').get_attribute('aria-label') if sh('.cpop').count() else None)
    shot('picker-replace-wait')
    check('the slide colours are listed', sh('.cpop .sw[data-hex="#EA4335"]').count()>=1, sh('.cpop .sw').evaluate_all('ns=>ns.map(n=>n.dataset.hex)'))
    sh('.cpop .sw[data-hex="#EA4335"]').first.click(); pg.wait_for_timeout(100); sh('.cpop .hex').fill('00acc1'); pg.wait_for_timeout(100)
    shot('picker-replace')
    n=npaste(); sh('.cpop .pb.ok').click(); pg.wait_for_timeout(3500)
    db=props(obj('b')) if obj('b') else {}; dc=props(obj('c')) if obj('c') else {}
    check('every use changed: a fill and a stroke, same objects', db.get(15)=='#00ACC1' and dc.get(19)=='#00ACC1' and dc.get(15)=='#34A853' and npaste()==n, (db,dc,pg.evaluate('()=>FAKE.native')))
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
