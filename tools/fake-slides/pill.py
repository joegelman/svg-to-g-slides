"""Edit Shape's value pill on the stand-in page: ✕ puts the shape back, ✓ keeps the change.

    CHROME=/path/to/chrome python3 tools/fake-slides/pill.py [screenshot.png]
"""
import os, sys
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); EXT=os.path.join(HERE,'..','..','extension')
fails=[]
def check(name, ok, detail=''):
    print(('ok   ' if ok else 'FAIL ')+name+(' :: '+str(detail) if detail and not ok else ''))
    if not ok: fails.append(name)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('CHROME') or None)
    pg=b.new_page(viewport={'width':1280,'height':680}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+os.path.join(HERE,'fake.html')); pg.wait_for_function('window.FAKE&&FAKE.ready')
    for f in ['shared.js','slides-bridge.js','rail-kit.js','svg-editor.js','geo-ops.js','fontkit.js','shape-tools.js']:
        pg.add_script_tag(content=open(os.path.join(EXT,f)).read())
    pg.evaluate("()=>{FAKE.objs=[[3,'a',1,[1,0,0,1,60000,40000],[8,80000,9,50000,12,[[1,1,[0,2,1,6,5,0],[0,0,80000,0,80000,50000,0,50000],[],0]],14,1,15,'#4285F4',145,1,60,1,61,[['#4285F4',0],['#0D47A1',1]],62,0.7854,18,0]]];FAKE.sel=['a'];FAKE.render()}")
    pg.wait_for_selector('#svg2slides-shape-tools', state='attached', timeout=8000)
    pg.evaluate("()=>SVG2S_SHAPES.command('edit')"); pg.wait_for_timeout(1200)
    host=pg.evaluate("()=>[...document.documentElement.children].filter(n=>n.shadowRoot&&n.shadowRoot.querySelector('.rpill')).map(n=>n.id||n.tagName)[0]||null")
    check('editor open with its pill', bool(host), host)
    pill=pg.locator('.rpill'); w=pill.locator('input[aria-label="Width in px"]'); no=pill.locator('.pb.no'); ok=pill.locator('.pb.ok')
    # select everything so the pill shows
    pg.keyboard.press('Meta+a'); pg.wait_for_timeout(300)
    if not pill.evaluate("n=>n.classList.contains('show')"): pg.keyboard.press('Control+a'); pg.wait_for_timeout(300)
    check('pill showing', pill.evaluate("n=>n.classList.contains('show')"))
    w0=w.input_value()
    fillOf=lambda: pg.locator('.fills path').first.get_attribute('fill')
    check('gradient shows while editing', pg.locator('defs.egrads linearGradient').count()==1 and (fillOf() or '').startswith('url(#egrad'), fillOf())
    check('buttons idle before a change', no.is_disabled() and ok.is_disabled())
    w.click(); w.fill('300'); pg.wait_for_timeout(150)
    check('buttons live after a change', not no.is_disabled() and not ok.is_disabled())
    if len(sys.argv)>1: pg.screenshot(path=sys.argv[1])
    no.click(); pg.wait_for_timeout(300)
    check('✕ puts the width back', w.input_value()==w0, (w0,w.input_value()))
    w.click(); w.fill('300'); pg.wait_for_timeout(150); ok.click(); pg.wait_for_timeout(300)
    check('✓ keeps the width', abs(float(w.input_value())-300)<0.6, w.input_value())
    w.click(); w.fill('120'); pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    check('Esc in the pill cancels just the pill change', abs(float(w.input_value())-300)<0.6 and pill.count()==1, w.input_value())
    # a colour change while the pill is up belongs to the pill's session
    w.click(); w.fill('280'); pg.wait_for_timeout(150); ok.click(); pg.wait_for_timeout(200)
    check('✓ leaves Edit Shape open and starts a fresh baseline', pill.count()==1 and pill.evaluate("n=>n.classList.contains('show')") and no.is_disabled())
    pg.evaluate("()=>{const h=[...document.documentElement.children].find(n=>n.shadowRoot&&n.shadowRoot.querySelector('.rpill')); const b=h.shadowRoot.querySelector('.rail [data-act=fill]'); const r=b.getBoundingClientRect(); window.__fb=[r.left+r.width/2,r.top+r.height/2,r.width]}"); fb=pg.evaluate('()=>window.__fb'); pg.mouse.click(fb[0],fb[1]); pg.wait_for_timeout(400)
    cp=pg.locator('.cpop'); check('the colour panel opens in Edit Shape on the gradient', cp.count()==1 and cp.get_attribute('data-mode')=='linear', cp.get_attribute('data-mode') if cp.count() else None)
    cp.locator('[data-mode="solid"]').click(); cp.locator('.hex').fill('e91e63'); pg.wait_for_timeout(200)
    check('the shape shows the colour as it is picked', (fillOf() or '').upper()=='#E91E63', fillOf())
    if len(sys.argv)>1: pg.screenshot(path=sys.argv[1].replace('.png','-colour.png'))
    cp.locator('.pb.ok').click(); pg.wait_for_timeout(300)
    check('after ✓ in the panel the pill can still take it back', not no.is_disabled() and (fillOf() or '').upper()=='#E91E63')
    no.click(); pg.wait_for_timeout(300)
    check('✕ on the pill puts the gradient back and stays in Edit Shape', (fillOf() or '').startswith('url(#egrad') and pill.count()==1, fillOf())
    pg.evaluate("()=>{const h=[...document.documentElement.children].find(n=>n.shadowRoot&&n.shadowRoot.querySelector('.rpill')); const b=h.shadowRoot.querySelector('.rail [data-act=fill]'); const r=b.getBoundingClientRect(); window.__fb=[r.left+r.width/2,r.top+r.height/2,r.width]}"); fb=pg.evaluate('()=>window.__fb'); pg.mouse.click(fb[0],fb[1]); pg.wait_for_timeout(400)
    cp.locator('[data-mode="solid"]').click(); cp.locator('.hex').fill('e91e63'); pg.wait_for_timeout(150); cp.locator('.pb.no').click(); pg.wait_for_timeout(300)
    check('✕ in the panel puts the gradient back', (fillOf() or '').startswith('url(#egrad'), fillOf())
    check('no page errors', not errs, errs[:3])
    b.close()
print('%d failed'%len(fails)); sys.exit(1 if fails else 0)
