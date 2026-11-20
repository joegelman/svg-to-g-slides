"""Writes random SVGs (every path command, arcs, strokes, transforms, colours,
gradients, bad values) for check.py --fuzz."""
import random, json, os
random.seed(7)
import sys
R = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
def num(kind=None):
    k = R.random()
    if k < 0.3: return str(R.randint(-50, 150))
    if k < 0.5: return str(R.randint(-100, 300) / 2)
    if k < 0.6: return '%.3f' % R.uniform(-100, 200)
    if k < 0.7: return '%.1e' % R.uniform(1, 100)
    if k < 0.8: return '.%d' % R.randint(1, 99)
    return '%.6f' % R.uniform(-20, 120)
def pnum(): return str(abs(float(num()))) if R.random() < 0.9 else '0'
CMDS = 'MLHVCSQTAZmlhvcsqtaz'
ARGC = dict(M=2,L=2,H=1,V=1,C=6,S=4,Q=4,T=2,A=7,Z=0)
def path():
    out = ['M', num(), num()]
    for _ in range(R.randint(1, 14)):
        c = R.choice(CMDS)
        n = ARGC[c.upper()]
        out.append(c)
        reps = R.choice([1, 1, 1, 2, 3])
        for _ in range(reps if n else 1):
            if c.upper() == 'A':
                out += [pnum(), pnum(), str(R.choice([0, 30, 45, -60, 90.5, 180])), str(R.randint(0, 1)), str(R.randint(0, 1)), num(), num()]
            else:
                out += [num() for _ in range(n)]
    sep = R.choice([' ', ',', ' , '])
    s = sep.join(out)
    if R.random() < 0.2: s = s.replace(' -', '-')
    return s
COLORS = ['red', 'navy', '#abc', '#A1B2C3', '#12345', 'rgb(10, 20, 300)', 'rgb(10%, 50%, 99.5%)', 'none', 'transparent', 'currentColor', 'url(#g1)', 'url(#nope)', 'URL(#g1)', 'hsl(10,20%,30%)', 'Tomato', '']
def paint(el):
    a = []
    if R.random() < 0.7: a.append('fill="%s"' % R.choice(COLORS))
    if R.random() < 0.5: a.append('stroke="%s"' % R.choice(COLORS))
    if R.random() < 0.4: a.append('stroke-width="%s"' % R.choice(['2', '0', '1.5px', '3.5', '0.25', 'abc', '1.2.3', '10']))
    if R.random() < 0.3: a.append('style="%s"' % R.choice(['fill:blue', 'stroke: #0f0; stroke-width: 4', 'fill:none;stroke:black', 'FILL : Red ;', 'stroke-width:2']))
    return ' '.join(a)
def xform():
    opts = ['translate(%s %s)' % (num(), num()), 'translate(%s)' % num(), 'scale(%s)' % R.choice(['2', '0.5', '-1', '1.25']),
            'scale(%s,%s)' % (R.choice(['2', '0.5', '-1']), R.choice(['3', '0.75'])), 'rotate(%s)' % R.choice(['30', '-45', '90', '12.5']),
            'rotate(%s %s %s)' % (R.choice(['30', '-15', '180']), num(), num()), 'matrix(1 0.2 -0.3 1 %s %s)' % (num(), num()), 'skewX(20)']
    return ' '.join(R.choice(opts) for _ in range(R.randint(1, 3)))
def shape():
    t = R.choice(['path'] * 5 + ['rect', 'rect', 'circle', 'ellipse', 'polygon', 'polyline', 'line'])
    tr = (' transform="%s"' % xform()) if R.random() < 0.3 else ''
    p = paint(None)
    if t == 'path': return '<path d="%s" %s%s/>' % (path(), p, tr)
    if t == 'rect':
        rx = (' rx="%s"' % pnum()) if R.random() < 0.4 else ''
        ry = (' ry="%s"' % pnum()) if R.random() < 0.2 else ''
        return '<rect x="%s" y="%s" width="%s" height="%s"%s%s %s%s/>' % (num(), num(), pnum(), pnum(), rx, ry, p, tr)
    if t == 'circle': return '<circle cx="%s" cy="%s" r="%s" %s%s/>' % (num(), num(), pnum(), p, tr)
    if t == 'ellipse': return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" %s%s/>' % (num(), num(), pnum(), pnum(), p, tr)
    if t in ('polygon', 'polyline'): return '<%s points="%s" %s%s/>' % (t, ' '.join(num() for _ in range(R.randint(3, 12))), p, tr)
    return '<line x1="%s" y1="%s" x2="%s" y2="%s" %s%s/>' % (num(), num(), num(), num(), p, tr)
def group(depth):
    parts = []
    for _ in range(R.randint(1, 5)):
        if depth < 3 and R.random() < 0.3:
            tr = (' transform="%s"' % xform()) if R.random() < 0.6 else ''
            parts.append('<g%s %s>%s</g>' % (tr, paint(None), group(depth + 1)))
        else: parts.append(shape())
    return ''.join(parts)
GRAD = ['<linearGradient id="g1"><stop offset="0" stop-color="#ff0000"/><stop offset="50%" style="stop-color:blue;stop-opacity:0.5"/></linearGradient>',
        '<radialGradient id="g1" gradientUnits="userSpaceOnUse" cx="5" cy="5"><stop offset="1" stop-color="green"/><stop offset="0.2" stop-color="#123"/></radialGradient>',
        '<linearGradient id="g1" x1="0%" x2="100%" y2="30%"><stop offset=".3" stop-color="rgb(1,2,3)"/></linearGradient>']
VB = ['0 0 100 100', '0 0 200 50', '-50 -50 100 100', '10 20 37.5 81.25', '0 0 24 24', '0 0 1000 700', '  0 0  64 64 ']
OUT = sys.argv[2] if len(sys.argv) > 2 else 'fuzz'
os.makedirs(OUT, exist_ok=True)
names = []
for i in range(1500):
    vb = R.choice(VB)
    defs = ('<defs>%s<clipPath id="c"><rect width="10" height="10"/></clipPath></defs>' % R.choice(GRAD)) if R.random() < 0.5 else ''
    bg = '<rect x="%s" y="%s" width="%s" height="%s" fill="white"/>' % tuple(vb.split()) if R.random() < 0.2 else ''
    root_attr = ('viewBox="%s"' % vb) if R.random() < 0.95 else ''
    rp = paint(None) if R.random() < 0.3 else ''
    svg = '<svg xmlns="http://www.w3.org/2000/svg" %s %s>%s%s%s</svg>' % (root_attr, rp, defs, bg, group(0))
    fn = os.path.join(OUT, 'f%04d.svg' % i)
    open(fn, 'w').write(svg); names.append(os.path.abspath(fn))
# Error cases
errs = {
 'e_px.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10px" height="5"/></svg>',
 'e_vbcomma.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0,0,10,10"><rect width="1" height="5"/></svg>',
 'e_tr.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="1" height="5" transform="translate()"/></svg>',
 'e_vb0.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 0 10"><rect x="1" width="1" height="5"/></svg>',
 'e_xml.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="1" height="5"></svg>',
 'e_ent.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><text>&nbsp;</text></svg>',
 'ok_bgpx.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect x="1" width="2" height="5"/><path d="M0 0L5 5"/></svg>',
 'ok_ns.svg': '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE svg [<!ENTITY ns_svg "http://www.w3.org/2000/svg">]><svg xmlns="&ns_svg;" xmlns:i="urn:x" viewBox="0 0 10 10"><i:path d="M0 0 L 1 1 L 0 2Z"/><g i:foo="1"><path d="M1 1h3v3z" fill="#fc0"/></g></svg>',
 'ok_unicode.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><path d="M0 0h5v5z" fill="#ééé"/></svg>',
 'ok_empty.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>',
 'ok_inf.svg': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect x="inf" width="1" height="2"/></svg>',
}
for k, v in errs.items():
    open(os.path.join(OUT, k), 'w', encoding='utf-8').write(v); names.append(os.path.abspath(os.path.join(OUT, k)))
print(len(names))
