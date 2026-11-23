"""Render the 1.4 What's new images: the real toolbar and panels from extension/, run over the
stand-in Slides page (fake.html) with a demo layout. The slide behind the panels is not Google Slides.

    CHROME=/path/to/chrome python3 tools/fake-slides/shots14.py out-dir
"""
import os, sys, json, base64
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); EXT = os.path.join(HERE, '..', '..', 'extension')
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
U = 381  # page units per stage pixel
K = 0.5523

def cubics(pts):
    """pts: start (x,y) then segments: ('L',x,y) or ('C',x1,y1,x2,y2,x,y). All as cubic curves."""
    x0, y0 = pts[0]; co = [x0, y0]; cx, cy = x0, y0; n = 0
    for s in pts[1:]:
        if s[0] == 'L':
            x, y = s[1], s[2]; co += [cx + (x - cx) / 3, cy + (y - cy) / 3, cx + 2 * (x - cx) / 3, cy + 2 * (y - cy) / 3, x, y]
        else:
            co += list(s[1:]); x, y = s[5], s[6]
        cx, cy = x, y; n += 1
    return [0, 2, 3, 6 * n, 5, 0], [round(v * U) for v in co]

def shape(id, x, y, w, h, pts, fill=None, stroke=None, sw=0, extra=None):
    meta, co = cubics(pts)
    pr = [8, round(w * U), 9, round(h * U), 12, [[1, 1, meta, co, [], 0]]]
    pr += [14, 1, 15, fill] if fill else [14, 0]
    pr += [18, 1, 19, stroke, 22, sw] if stroke else [18, 0]
    return [3, id, 1, [1, 0, 0, 1, round(x * U), round(y * U)], pr + (extra or [])]

def rrect(w, h, r):
    k = r * (1 - K)
    return [(r, 0), ('L', w - r, 0), ('C', w - k, 0, w, k, w, r), ('L', w, h - r), ('C', w, h - k, w - k, h, w - r, h),
            ('L', r, h), ('C', k, h, 0, h - k, 0, h - r), ('L', 0, r), ('C', 0, k, k, 0, r, 0)]

def circ(r):
    k = r * K
    return [(r, 0), ('C', r + k, 0, 2 * r, r - k, 2 * r, r), ('C', 2 * r, r + k, r + k, 2 * r, r, 2 * r),
            ('C', r - k, 2 * r, 0, r + k, 0, r), ('C', 0, r - k, r - k, 0, r, 0)]

def wave(w, h, top, r):
    k = r * (1 - K); a = w / 6
    return [(0, top), ('C', a, top - 26, 2 * a, top + 26, 3 * a, top), ('C', 4 * a, top - 26, 5 * a, top + 26, w, top),
            ('L', w, h - r), ('C', w, h - k, w - k, h, w - r, h), ('L', r, h), ('C', k, h, 0, h - k, 0, h - r), ('L', 0, top)]

def arch(w, h):
    r = w / 2; k = r * K
    return [(0, h), ('L', 0, r), ('C', 0, r - k, r - k, 0, r, 0), ('C', r + k, 0, w, r - k, w, r), ('L', w, h), ('L', 0, h)]

TEAL, SUN, SEA, FOAM, CORAL, NAVY, SAND = '#00897B', '#FFB300', '#4DB6AC', '#B2DFDB', '#FF7043', '#1A237E', '#FFE0B2'
OX, OY = 372, 126  # where the layout sits on the 960 x 540 stage

def layout():
    o = []
    o.append(shape('card', OX, OY, 324, 270, rrect(324, 270, 26), TEAL))
    o.append(shape('sun', OX + 196, OY + 42, 84, 84, circ(42), SUN))
    o.append(shape('sea', OX, OY, 324, 270, wave(324, 270, 172, 26), SEA))
    o.append(shape('foam', OX, OY, 324, 270, wave(324, 270, 214, 26), FOAM))
    for i, (c, d) in enumerate([(CORAL, SAND), (NAVY, SUN), (TEAL, FOAM)]):
        y = OY + i * 97
        o.append(shape('pill%d' % i, OX + 360, y, 204, 76, rrect(204, 76, 18), c))
        o.append(shape('dot%d' % i, OX + 380, y + 20, 36, 36, circ(18), d))
    return o

PHOTO = ('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1">'
         '<stop stop-color="#4FC3F7"/><stop offset="1" stop-color="#FFE0B2"/></linearGradient></defs><rect width="800" height="600" fill="url(#s)"/>'
         '<circle cx="590" cy="170" r="70" fill="#FFF59D"/><rect y="330" width="800" height="120" fill="#0288D1"/>'
         '<path d="M0 372 C100 352 200 392 300 372 C400 352 500 392 600 372 C700 352 760 380 800 372 V450 H0Z" fill="#29B6F6"/>'
         '<path d="M0 440 C200 410 500 420 800 450 V600 H0Z" fill="#FFE082"/>'
         '<path d="M210 520 C214 430 226 360 262 290 L278 296 C246 366 238 432 236 520Z" fill="#6D4C41"/>'
         '<path d="M268 292 C200 250 140 262 96 300 C150 276 210 280 268 292Z M268 292 C250 220 200 190 150 186 C200 206 240 244 268 292Z M268 292 C300 226 360 206 410 216 C356 226 310 250 268 292Z M268 292 C340 268 400 290 430 330 C384 300 330 290 268 292Z" fill="#2E7D32"/></svg>')

GRAD_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 270"><defs>'
            '<linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FF7043"/><stop offset="1" stop-color="#FFB300"/></linearGradient>'
            '<linearGradient id="b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A237E"/><stop offset=".55" stop-color="#00897B"/><stop offset="1" stop-color="#B2DFDB"/></linearGradient>'
            '<radialGradient id="c" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFF59D"/><stop offset="1" stop-color="#FF7043"/></radialGradient></defs>'
            '<rect x="0" y="0" width="170" height="270" rx="24" fill="url(#a)"/><rect x="195" y="0" width="170" height="270" rx="24" fill="url(#b)"/>'
            '<circle cx="475" cy="135" r="85" fill="url(#c)"/><rect x="390" y="230" width="170" height="40" rx="20" fill="#1A237E" fill-opacity=".35"/></svg>')

def icon(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1A237E" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>')
ICONS = [icon('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>'),
         icon('<path d="M3 12c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/><path d="M3 18c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/><path d="M3 6c2-3 4-3 6 0s4 3 6 0 4-3 6 0"/>'),
         icon('<path d="M4 20h16"/><path d="M6 20V10l6-6 6 6v10"/><path d="M10 20v-6h4v6"/>'),
         icon('<rect x="3" y="6" width="18" height="14" rx="2"/><circle cx="12" cy="13" r="4"/><path d="M8 6l1.5-3h5L16 6"/>'),
         icon('<circle cx="12" cy="10" r="3"/><path d="M12 21c-4-5-7-8-7-11a7 7 0 0 1 14 0c0 3-3 6-7 11z"/>'),
         icon('<path d="M12 21C7 17 3 13.5 3 9.5A4.5 4.5 0 0 1 12 7a4.5 4.5 0 0 1 9 2.5c0 4-4 7.500-9 11.500z"/>')]

CSS = """html,body{background:#f8fafd!important}#tb,.filmstrip{opacity:0!important}
#workspace-container{background:#f1f3f4!important;left:230px!important;top:60px!important;right:20px!important;bottom:20px!important}
#stage{box-shadow:0 1px 3px rgba(60,64,67,.3),0 4px 8px 3px rgba(60,64,67,.12)}"""
ICON = 'data:image/png;base64,' + base64.b64encode(open(os.path.join(EXT, 'icons', 'icon48.png'), 'rb').read()).decode()

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('CHROME') or None)
    pg = b.new_page(viewport={'width': 1280, 'height': 700}, device_scale_factor=2)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.join(HERE, 'fake.html')); pg.wait_for_function('window.FAKE&&FAKE.ready')
    pg.add_style_tag(content=CSS)
    for f in ['shared.js', 'svg-convert.js', 'slides-bridge.js', 'rail-kit.js', 'svg-editor.js', 'geo-ops.js', 'fontkit.js', 'shape-tools.js']:
        pg.add_script_tag(content=open(os.path.join(EXT, f)).read())
    pg.evaluate("(s)=>{FAKE.img='data:image/svg+xml;base64,'+btoa(s)}", PHOTO)
    setobjs = lambda o: (pg.evaluate('(o)=>{FAKE.objs=o;FAKE.sel=[];FAKE.render()}', o), pg.wait_for_timeout(350))
    setobjs(layout())
    pg.wait_for_selector('#svg2slides-shape-tools', state='attached', timeout=8000)
    sh = lambda sel: pg.locator('#svg2slides-shape-tools').locator(sel)
    cmd = lambda a: (pg.evaluate("(a)=>{SVG2S_SHAPES.command(a)}", a), pg.wait_for_timeout(450))
    cmd('toggleRail')
    pg.evaluate("""(icon)=>{const r=document.querySelector('#svg2slides-shape-tools').shadowRoot; r.querySelectorAll('img').forEach(i=>i.src=icon);
      const s=document.createElement('style'); s.id='shotcss'; s.textContent='.hint{display:none!important}'; r.appendChild(s);}""", ICON)
    hint = lambda on: pg.evaluate("(on)=>{document.querySelector('#svg2slides-shape-tools').shadowRoot.getElementById('shotcss').textContent=on?'':'.hint{display:none!important}'}", on)
    CLIP = {'x': 230, 'y': 60, 'width': 1030, 'height': 620}
    def shot(n):
        pg.mouse.move(1255, 655); pg.wait_for_timeout(250); pg.screenshot(path=os.path.join(OUT, n + '.png'), clip=CLIP)
    def click_obj(id, shift=False):
        bb = pg.evaluate("(id)=>{const r=document.getElementById('editor-'+id).getBoundingClientRect();return [r.left+r.width*0.5,r.top+r.height*0.2]}", id)
        if shift: pg.keyboard.down('Shift')
        pg.mouse.click(bb[0], bb[1]); pg.wait_for_timeout(250)
        if shift: pg.keyboard.up('Shift')
    def blank():
        pg.evaluate("()=>{FAKE.sel=[];FAKE.render()}"); pg.wait_for_timeout(300)
    close = lambda: (sh('.cpop .pb.no').click(), pg.wait_for_timeout(300))

    # 1. colour picker: a new colour for the card, previewed on the slide
    click_obj('card'); cmd('fill')
    sh('.cpop .hex').fill('1565C0'); sh('.cpop input[aria-label="Opacity, percent"]').fill('90'); pg.wait_for_timeout(200)
    shot('14-colour'); close()

    # 2. gradient builder
    click_obj('card'); cmd('fill')
    sh('.cpop [data-mode="linear"]').click(); pg.wait_for_timeout(150)
    bar = sh('.cpop .gbar').bounding_box(); pg.mouse.click(bar['x'] + bar['width'] * 0.5, bar['y'] + bar['height'] / 2); pg.wait_for_timeout(150)
    sh('.cpop .hex').fill('4DD0E1'); pg.wait_for_timeout(100)
    if sh('.cpop [data-ang="45"]').count(): sh('.cpop [data-ang="45"]').click()
    pg.wait_for_timeout(250)
    shot('14-gradient'); close()

    # 3. replace a colour: teal becomes coral wherever it is used
    blank(); cmd('fill')
    sh('.cpop .sw[data-hex="%s"]' % TEAL).first.click(); pg.wait_for_timeout(120); sh('.cpop .hex').fill('5E35B1'); pg.wait_for_timeout(250)
    shot('14-replace'); close()

    # 4. live preview: stroke width while the field is scrubbed
    setobjs([o if o[1] != 'pill1' else shape('pill1', OX + 360, OY + 97, 204, 76, rrect(204, 76, 18), NAVY, SUN, 762) for o in layout()])
    click_obj('pill1'); pg.wait_for_timeout(300)
    wf = sh('.rail [data-act="weight"] input')
    wf.click(); wf.fill('8'); pg.wait_for_timeout(300)
    shot('14-preview')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)

    # 5. mask: the shape on top as an outline, the picture adjustable under it
    aw, ah = 250, 300; ax, ay = OX + 170, OY - 20
    pic = shape('pic', ax, ay, aw, ah, arch(aw, ah), None, None, 0, [49, 'blob1', 86, 1, 87, 600, 88, 800, 79, 1.7, 80, 1.0625, 84, -0.22, 85, -0.03])
    pic[4] = [v for v in pic[4]]
    out = shape('outl', ax, ay, aw, ah, arch(aw, ah), None, NAVY, 1524)
    setobjs([pic, out])
    shot('14-mask')
    pg.evaluate("()=>{FAKE.sel=['pic'];FAKE.render()}"); pg.wait_for_timeout(300)
    hint(True); cmd('mask'); pg.wait_for_timeout(500)
    shot('14-mask-adjust')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300); hint(False)

    # 6. gradients on import: what the converter makes of an SVG with gradients, opened in the builder
    conv = lambda svg, x, y, w, h: pg.evaluate("""([svg,x,y,w,h])=>{const r=SVG2S_CONVERT.buildClipBundleAt([svg],x,y,w,h);const k=Object.keys(r)[0];return JSON.parse(JSON.parse(r[k]).data).resolved}""", [svg, x, y, w, h])
    PT = 0.75  # stage px to points
    def place(ents, x, y):
        mx = min(e[3][4] for e in ents); my = min(e[3][5] for e in ents)
        for e in ents: e[3][4] += round(x * U) - mx; e[3][5] += round(y * U) - my
        return ents
    ents = place(conv(GRAD_SVG, 0, 0, 560 * PT, 270 * PT), OX, OY)
    setobjs(ents)
    ids = pg.evaluate("()=>FAKE.objs.map(o=>o[1])")
    shot('14-import')
    pg.evaluate("(id)=>{FAKE.sel=[id];FAKE.render()}", ids[1]); pg.wait_for_timeout(300); cmd('fill'); pg.wait_for_timeout(200)
    shot('14-import-open')
    if sh('.cpop').count(): close()

    # 7. outline icon sets: stroke icons arrive as shapes
    ents = []
    for i, ic in enumerate(ICONS):
        ents += place(conv(ic, 0, 0, 110 * PT, 110 * PT), OX + 40 + (i % 3) * 180, OY + 10 + (i // 3) * 150)
    setobjs(ents)
    shot('14-icons')
    print('errors:', errs[:3]); print('done')
    b.close()
