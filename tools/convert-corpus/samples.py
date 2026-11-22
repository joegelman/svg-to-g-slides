"""Run the 20 /specs samples through extension/svg-convert.js and print shapes and fill colours per file."""
import glob, json, os, re
from playwright.sync_api import sync_playwright
REPO=__import__('os').path.abspath(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','..')); MIME='application/x-vnd.google-docs-drawings-object+wrapped'
src=open(REPO+'/extension/svg-convert.js').read()
files=sorted(glob.glob(REPO+'/cloud/static/specs/samples/*.svg'))
rows=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=__import__('os').environ.get('CHROME') or None); pg=b.new_page(); pg.set_content('<html></html>'); pg.add_script_tag(content=src); pg.add_script_tag(content=open(REPO+'/extension/geo-ops.js').read())
    for f in files:
        t=open(f,'rb').read().decode('latin-1')
        for legacy in (False,):
            r=pg.evaluate("""([t,legacy])=>{try{const by=Uint8Array.from(t,c=>c.charCodeAt(0));const o=SVG2S_CONVERT.buildClipBundleAt([by],480,270,192,108,legacy?{legacy:true}:{});return {ok:o['%s']}}catch(e){return {err:e.constructor.name+': '+String(e.message).slice(0,140)}}}"""%MIME,[t,legacy])
        name=os.path.basename(f)[:-4]
        if 'err' in r: rows.append((name,'ERROR',r['err'],'')); continue
        try:
            res=json.loads(json.loads(r['ok'])['data'])['resolved']
        except Exception as e:
            rows.append((name,'?',str(e)[:80],r['ok'][:80])); continue
        shapes=[e for e in res if e and e[0]==3]
        cols=sorted(set(re.findall(r'#[0-9a-fA-F]{6}', json.dumps(shapes))))
        rows.append((name,len(shapes),','.join(cols)[:70],''))
    b.close()
for r in rows: print(r)

