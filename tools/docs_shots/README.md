# Docs figures

Scripts that made the UI figures in `/docs`. They load the extension's own
content scripts into a mock Google Slides page in headless Chromium, so the
toolbar, flyouts, command palette, Layers panel and Edit Shape editor are the
real interface. No Google account or live presentation is involved.

| File | Purpose |
|---|---|
| `build.py` | Builds the mock page: shared Slides shell, Vacay cover slide, `chrome` stub, selection model. |
| `shots.py` | Page launch, selection, callout and cursor helpers. |
| `final.py`, `final2.py`, `final3.py` | One block per figure. Pass the block names to capture some, nothing for all. |
| `cmds.py` | Dumps the command list and shortcut labels for Mac and Windows to `out/commands.json`. `docs_reference.py` was checked against it. |
| `lottie_still.py` | Renders single frames of the release animations (the figures captioned *Illustration*). |
| `siteshot.py` | Screenshots a page of the built site (Web Uploader, Add-on figures, page review). |
| `publish.py` | Converts `out/<name>.png` into `cloud/static/docs/img/<name>.jpg` and `.webp`. |

## Running

    pip install playwright pillow && playwright install chromium
    npm install @fontsource/roboto @fontsource/nunito @fontsource/overpass lottie-web
    python3 final.py closed open tooltip
    python3 publish.py toolbar-closed toolbar-open toolbar-tooltip
    cd .. && python3 build_site.py

Environment:

- `SVGX_TREE`: working tree with `extension/` and `svgslides_pmm_lottie_assets/`. Default: this repository. The assets folder is not in git.
- `SVGX_NODE`: `node_modules` folder holding the fonts and lottie-web. Default: `node_modules` at the repository root.
- `SVGX_OUT`: where PNGs are written. Default: `tools/docs_shots/out` (ignored by git).
- `SVGX_CHROME`: a Chromium binary. Default: the one Playwright installs.

The figures in `/docs` were captured from extension version 1.3.0. Capture
again when the toolbar or editor changes, and keep the callout numbers in step
with the `@fig` legends in `tools/docs_*.py`.
