#!/usr/bin/env python3
"""Check that extension/svg-convert.js converts SVGs exactly like the Python.

    python3 tools/convert-parity/check.py [file.svg | folder ...]
    python3 tools/convert-parity/check.py --fuzz 1500

Runs cloud/slides_clip.py (with the root svg_to_slides.py) and
extension/svg-convert.js (in headless Chrome) on the same files with the same
placement and fixed ids, and compares the clipboard payloads byte for byte.
With no paths it checks every .svg in the repo. --fuzz N also checks N random
SVGs from fuzz_gen.py.

Needs: pip install playwright && playwright install chromium

Expect a handful of fuzz files to differ: arcs whose radii are exactly too
small give a half-ellipse where the last bit of pow() decides between two and
three curve pieces (the same shape either way). The server's Python and the
old in-browser Python already disagreed on those.
"""
import glob, json, os, sys, tempfile, types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
PLACE = (480, 270, 192, 108)  # content.js's placeholder placement
MIME = 'application/x-vnd.google-docs-drawings-object+wrapped'


def python_side(cases):
    sys.path[:0] = [os.path.join(REPO, 'cloud'), REPO]
    for m in ('pptx', 'pptx.util', 'lxml', 'lxml.etree'):  # PowerPoint half only
        sys.modules.setdefault(m, types.ModuleType(m))
    sys.modules['pptx'].Presentation = object
    sys.modules['pptx.util'].Emu = object
    import secrets
    import slides_clip
    n = [0]
    def tok(_k):
        n[0] += 1
        return '%010x' % n[0]
    secrets.token_hex = tok
    out = {}
    for name, files in cases:
        n[0] = 0
        try:
            srcs = [(f, open(f, 'rb').read()) for f in files]
            out[name] = {'ok': slides_clip.build_clip_bundle_at(srcs, *PLACE)[MIME]}
        except Exception as e:
            out[name] = {'err': type(e).__name__ + ': ' + str(e)[:160]}
    return out


def js_side(cases):
    from playwright.sync_api import sync_playwright
    src = open(os.path.join(REPO, 'extension', 'svg-convert.js')).read()
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROME') or None)  # CHROME=/path/to/chrome to use your own
        pg = b.new_page()
        pg.set_content('<html></html>')
        pg.add_script_tag(content=src)
        pg.evaluate("""() => { self.__n = 0; SVG2S_CONVERT._setIdSource(() => 'ga' + (++self.__n).toString(16).padStart(10, '0')); }""")
        out = {}
        for name, files in cases:
            texts = [open(f, 'rb').read().decode('latin-1') for f in files]
            out[name] = pg.evaluate("""([texts, place]) => {
                self.__n = 0;
                try {
                  const bytes = texts.map((t) => Uint8Array.from(t, (c) => c.charCodeAt(0)));
                  return { ok: SVG2S_CONVERT.buildClipBundleAt(bytes, ...place, { legacy: true })['%s'] };
                } catch (e) { return { err: e.constructor.name + ': ' + String(e.message).slice(0, 160) }; }
            }""" % MIME, [texts, list(PLACE)])
        b.close()
    return out


def main(argv):
    paths, fuzz = [], 0
    it = iter(argv)
    for a in it:
        if a == '--fuzz': fuzz = int(next(it))
        else: paths.append(a)
    files = []
    for p in paths or [REPO]:
        if os.path.isdir(p):
            files += [f for f in glob.glob(os.path.join(p, '**', '*.svg'), recursive=True)
                      if '/_to_delete/' not in f and '/node_modules/' not in f]
        else:
            files.append(p)
    if fuzz:
        d = tempfile.mkdtemp(prefix='svgfuzz-')
        os.system('%s %s 7 %s > /dev/null' % (sys.executable, os.path.join(HERE, 'fuzz_gen.py'), d))
        files += sorted(glob.glob(os.path.join(d, '*.svg')))[:fuzz + 11]
    files = sorted(set(files))
    cases = [[f, [f]] for f in files]
    for k in (2, 3, 5):  # several files dropped at once
        for i in range(0, min(len(files), 30) - k + 1, k):
            cases.append(['%d files from %s' % (k, os.path.basename(files[i])), files[i:i + k]])
    py, js = python_side(cases), js_side(cases)
    same, bad = 0, []
    for name, _ in cases:
        a, b = py[name], js[name]
        if 'err' in a or 'err' in b:
            if ('err' in a) == ('err' in b): same += 1
            else: bad.append((name, a.get('err', 'converted'), b.get('err', 'converted')))
        elif a['ok'] == b['ok']: same += 1
        else: bad.append((name, 'payload differs', ''))
    print('%d of %d match' % (same, len(cases)))
    for name, x, y in bad: print('  DIFFERS', os.path.relpath(name, REPO) if name.startswith(REPO) else os.path.basename(name), x, y)
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
