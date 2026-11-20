import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright
import build as B
CHROME=B.CHROME
JS="""()=>{ const ex=[
 { act: 'edit', label: 'Edit Shape', group: 'Shape tools', key: 'Double-click' },
 { act: 'pen', label: 'Pen: draw new shapes (or edit the selected ones)', group: 'Shape tools', key: SB.SHORTCUT_LABEL.pen },
 { act: 'layers', label: 'Show layers', group: 'Shape tools', key: SB.SHORTCUT_LABEL.layers },
 { act: 'toggleRail', label: 'Hide the toolbar', group: 'Shape tools', key: SB.SHORTCUT_LABEL.toggleRail },
 { act: 'themeBuilder', label: 'Theme builder (layouts and master)', group: 'Shape tools', key: SB.SHORTCUT_LABEL.themeBuilder },
 { act: 'restoreText', label: 'Restore outlined text', group: 'Outline', key: SB.SHORTCUT_LABEL.outlineText }];
 return {cmds: RK.commandList(ex).map(c=>({act:c.act,label:c.label,group:c.group,key:c.key||''})), labels: SB.SHORTCUT_LABEL, mac: SB.IS_MAC}; }"""
async def main():
    out={}
    async with async_playwright() as pw:
        for plat in ['MacIntel','Win32']:
            B.OUT.mkdir(parents=True, exist_ok=True); p=B.OUT/'_c.html'; p.write_text(B.build(platform=plat, store={}))
            b=await pw.chromium.launch(executable_path=CHROME); pg=await b.new_page(viewport={'width':1200,'height':900})
            await pg.goto('file://'+str(p)); await pg.wait_for_timeout(1500)
            out[plat]=await pg.evaluate(JS); await b.close()
    json.dump(out, open(B.OUT/'commands.json','w'), ensure_ascii=False, indent=1)
    m=out['MacIntel']['cmds']; w={c['act']:c for c in out['Win32']['cmds']}
    print(out['MacIntel']['mac'], out['Win32']['mac'])
    for c in m: print(f"{c['group']:24} | {c['label']:50} | {c['key']:10} | {w[c['act']]['key']}")
asyncio.run(main())
