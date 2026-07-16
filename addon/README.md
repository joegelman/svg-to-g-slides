# SVG Slides — Google Slides Add-on

Adds an **Extensions → SVG Slides → Insert SVG…** menu item to Google Slides that converts local SVG files into fully editable vector shapes and copies them onto the active slide.

## How it works

1. User picks one or more `.svg` files from the dialog, clicks **Convert**.
2. The add-on sends them to the svgslid.es backend (`/insert-svg-clip`), along with the active presentation's width/height.
3. The backend converts each SVG path into Google Slides' own internal clipboard object format (see `cloud/slides_clip.py`) — the same format Slides itself writes when you copy a shape — and returns it as a small JSON bundle. No PPTX, no Drive, no Slides API call anywhere in this step.
4. User clicks **Copy shapes to clipboard**; the dialog's JS writes that bundle to the OS clipboard (via the legacy `copy`-event `clipboardData.setData()` API — the modern async Clipboard API blocks custom MIME types like this one).
5. User clicks the slide, presses Cmd/Ctrl+V. Slides recognizes its own format and creates real, individually editable vector shapes.

Nothing is written to Drive, and no Slides API scope is used for the insert step at all — the add-on only touches `SlidesApp.getActivePresentation()` to read the current slide's dimensions, which needs just the narrow `presentations.currentonly` scope. This is what let the app clear Google's OAuth verification: the previous design (PPTX → Drive → `SlidesApp.openById()` on a second file → clone elements) required the full, restricted `presentations` scope, which Google rejected as disproportionate to the app's actual behavior.

## Prerequisites

- Node.js (any recent LTS)
- [clasp](https://github.com/google/clasp): `npm install -g @google/clasp`
- A Google account that can access the Apps Script project

## One-time setup

### 1. Authenticate clasp

```bash
clasp login
```

### 2. Create the Apps Script project

From inside the `addon/` directory:

```bash
cd addon
clasp create --type standalone --title "SVG Slides"
```

This writes a `.clasp.json` file. **Do not commit it** — it contains your script ID.

### 3. Set the backend URL

Open `Code.gs` and confirm `BACKEND_URL` at the top matches your deployed Cloud Run URL:

```js
var BACKEND_URL = 'https://svg-to-slides-jwxfsrfexq-uc.a.run.app';
```

### 4. Push to Apps Script

```bash
clasp push
```

### 5. Remove the Drive Advanced Service, if previously enabled

Earlier versions of this add-on used `Drive.Files.copy()` and required the
Drive API v3 advanced service to be enabled in the script editor. The current
clipboard-based flow doesn't call Drive or the Slides API at all, so if your
script has it enabled from before:

1. Open the script: `clasp open`
2. Click **Services** (the wrench/list icon in the left sidebar)
3. Find **Drive API**, click the trash icon to remove it

If you're setting this project up fresh, there's nothing to add here.

### 6. Create a test deployment and install it

You cannot test the menu by running `onOpen` in the editor — it needs a real presentation context. Use a test deployment instead:

1. In the Apps Script editor: **Deploy → Test deployments**
2. Click **Install**, then **Done**

(The older "Extensions → Add-ons → Manage add-ons → Test with latest code" path
is gone/greyed out in current Slides — the Install button in the Test
deployments dialog is the current mechanism and installs directly for your
account.)

3. Refresh any open Google Slides tab in the same account — the menu appears under **Extensions → SVG Slides → Insert SVG…**

After pushing code changes (`clasp push`), re-open **Deploy → Test deployments**
and click **Install** again to pick up the latest version — no need to refresh
the tab a second time unless the menu itself changed.

### 7. Authorise scopes on first use

The first time you click **Insert SVG…**, Google will ask you to approve
permissions — external requests, plus `presentations.currentonly` (access to
the current presentation only, not "See, edit, create, and delete all your
Google Slides presentations"). No Drive permission should appear. Click
through — this only happens once.

## Publishing (optional)

To make the add-on installable by others:

1. In the Apps Script editor: **Deploy → New deployment → Add-on**
2. Follow the Workspace Marketplace wizard
3. Users install it from **Extensions → Add-ons → Get add-ons**

## Notes

- Shapes are laid out relative to the active presentation's actual dimensions (width × height are passed to the backend), so content fits correctly regardless of 4:3 vs 16:9.
- Multiple SVGs selected at once combine onto the current slide as a row of shapes, rather than each becoming a separate slide (the old PPTX-based flow could append new slides via the Slides API; the clipboard-paste flow can only place content wherever the user pastes, i.e. the current slide).
- The add-on is completely independent of the main svgslid.es web service — it calls the same backend but through a separate endpoint (`/insert-svg-clip`) that has no Drive/Slides API side-effects of its own.
- Gradients collapse to a solid fill (the first gradient stop's color) for now — full gradient fidelity in the clipboard format is a fast-follow.
