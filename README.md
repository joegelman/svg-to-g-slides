![svg-to-slides_icon](https://github.com/joegelman/svg-to-g-slides/blob/main/assets/icon_desc.png)
# svg-to-g-slides

Convert SVG files to editable vector shapes in Google Slides.

**svgslid.es** · github.com/joegelman/svg-to-g-slides · built by Joe Gelman

---

## CHROME EXTENSION (v1.2.0)

The main product. [Chrome Web Store](https://chromewebstore.google.com/detail/svg-to-slides/bdhhnakellmdnbgbdokiojipaebdeioi) · release notes at [svgslid.es/whats-new](https://svgslid.es/whats-new)

- **Insert:** drag `.svg` files onto an open Google Slides tab and click where they go. Conversion runs in the browser (Pyodide); the result is handed to Slides through a synthetic paste of its own clipboard format, so nothing needs pasting by hand. If Slides refuses, it falls back to a `⌘/Ctrl+V` prompt.
- **Edit Shape:** double-click any shape, then click *Edit Shape*. A vector editor overlays the slide at the shape's exact size: drag points and handles, pen tool, multi-select, undo/redo, zoom. *Done* deletes the original and pastes the edited shape in place at the editor's zoom.
- **Any shape:** presets, lines, text boxes and WordArt are converted first by reading the SVG Slides itself renders (`g#editor-<id>`) into custom shapes. Preset handles, connector glue, 3D shading and live WordArt text don't survive; *Cancel* restores the original.
- **Permissions:** `storage` (one-time "what's new" card after an update) and one host permission for the converter fallback. No Google account access.

| File | Role |
|---|---|
| `extension/content.js` | Drop handling, ghost preview, click-to-place, direct insert |
| `extension/slides-bridge.js` | Clipboard round trip, selection, page geometry, path model, rendered-shape conversion |
| `extension/svg-editor.js` | The Edit Shape overlay editor |
| `extension/background.js`, `whats-new.js` | One-time update card |
| `extension/slides_clip.py`, `svg_to_slides.py` | Converter (copies of `cloud/slides_clip.py` and the root converter) |

To test locally: `chrome://extensions` → Developer mode → Load unpacked → `extension/`. Keep `__pycache__` out of the folder or Chrome refuses to load it.

---

## WEB APP

**svgslid.es** — drop SVGs in a browser, get a Google Drive link back. No install, no OAuth, no API keys.

Every `<path>` in your SVG becomes a discrete, selectable DrawingML shape in Slides. Upload one or multiple SVGs; each becomes one slide in the output PPTX. Optionally provide a Google account email and the file is shared directly to that account.

---

## HOW IT WORKS

1. Upload one or more `.svg` files via the web interface
2. The server converts each SVG to a PPTX slide — every path element becomes an individually editable `<a:custGeom>` vector shape
3. The PPTX is uploaded to a shared Google Drive folder
4. A shareable "anyone with the link" Drive link is returned instantly
5. Open the link → File → Save to Drive → File → Make a copy to edit as a native Slides file

---

## COMMAND LINE (local)

```sh
git clone https://github.com/joegelman/svg-to-g-slides.git
cd svg-to-g-slides
./install.sh
```

**Install does:**
- Installs `python-pptx` and `lxml` to `~/.local/share/svg-to-slides/lib/`
- Copies scripts to `~/.local/bin/`
- Detects Google Drive and creates `…/My Drive/SVG to Slides/`
- Creates a drop folder and loads a launchd agent (polls every 5s)
- Adds a Desktop alias pointing at the drop folder

**Dependencies:** Python 3, pip3 (Xcode CLT). For PNG tracing: `brew install imagemagick potrace`. Google Drive for Desktop installed and signed in.

**Usage:**

```sh
svg_to_slides.py a.svg b.svg c.svg
# → slides.pptx alongside the input files, one slide per SVG

png_to_svg.sh icons/*.png
# → ../svgs/<name>.svg relative to each input
```

**Drop zone:** Drag `.svg` files onto **SVG to Slides Drop** on the Desktop. Output appears in the configured Drive folder within 10 seconds.

---

## CLOUD DEPLOY

The web app runs on Google Cloud Run. See `cloud/deploy.sh` for the full setup script.

```sh
bash cloud/deploy.sh
```

**Stack:** FastAPI · Python · Google Drive API (Shared Drive) · Cloud Run · Workload Identity

**Redeploy after changes:**

```sh
git add -A && git commit -m "your message" && git push
```

Pushes to `main` auto-deploy via Cloud Build trigger.

---

## CLOUD FILES

| Path | |
|---|---|
| `cloud/main.py` | FastAPI app, `/convert` endpoint |
| `cloud/slides_clip.py` | Builds the Slides add-on's clipboard payload (`/insert-svg-clip`) — no Drive/Slides API involved |
| `cloud/drive.py` | Drive upload + sharing |
| `cloud/static/index.html` | Frontend |
| `cloud/Dockerfile` | Container definition |
| `cloud/deploy.sh` | GCP setup + deploy script |
| `cloudbuild.yaml` | Cloud Build config |

---

## LOCAL FILES

| Path | |
|---|---|
| `~/.local/bin/svg_to_slides.py` | converter |
| `~/.local/bin/png_to_svg.sh` | PNG tracer |
| `~/Library/Scripts/svg_to_slides_watch.sh` | watcher |
| `~/Library/LaunchAgents/com.$USER.svg-to-slides.plist` | launchd agent |
| `~/Library/Application Support/svg-to-slides-drop/` | drop folder |
| `~/.config/svg-to-slides.conf` | config |
| `/tmp/svg-to-slides.log` | log |

---

## NOTES

Arc commands (`A`/`a`) in SVG paths fall back to straight lines. Re-export with more path segments if arcs appear angular.

Folder Actions and `WatchPaths` are silently broken on macOS Sequoia. `StartInterval` polling is used instead.

macOS TCC blocks launchd from reading `~/Documents`, `~/Desktop`, and `~/Library/CloudStorage`. The drop folder lives in `~/Library/Application Support/` where launchd has access.

---

## LICENSE

MIT
