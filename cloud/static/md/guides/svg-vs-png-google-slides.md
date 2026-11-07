# SVG vs PNG in Google Slides™

When Google Slides flattens an SVG it becomes a single image that blurs when resized and can't be recoloured or edited. SVG to Slides converts every path into Slides' own native shape format instead, so the result behaves like a shape you drew yourself.

_Free forever. Every feature, no daily cap, no account, no Pro tier._

- Install the Chrome extension: https://chromewebstore.google.com/detail/svg-to-slides/bdhhnakellmdnbgbdokiojipaebdeioi
- Online converter: https://svgslid.es/convert

## Flattened vs. converted

| Pasted as PNG (default) | Inserted with SVG to Slides |
|---|---|
| Blurs or pixelates when resized | Resizes at any size, always crisp |
| One flattened image, single object | Every path is its own selectable shape |
| Can't recolour without re-exporting | Recolour any shape directly in Slides |
| Can't animate individual elements | Animate each shape independently |
| Can't edit points or paths | Right-click → Edit points, like any native shape |

## Pick your route
- **Chrome extension** — Drag an SVG file straight onto an open Slides tab and drop it in place. No dialog, no upload step. (https://chromewebstore.google.com/detail/svg-to-slides/bdhhnakellmdnbgbdokiojipaebdeioi)
- **Web Uploader** — Upload one or more SVGs and get back a Google Drive link to a ready-made Slides file, one slide per SVG. (https://svgslid.es/convert)
- **Google Slides add-on** — Insert SVGs into a presentation you're already editing, from a dialog inside Slides itself. (https://svgslid.es/addon)

## How it stays a vector
- Every <path> in your SVG is converted directly into Google Slides' own native shape format. It isn't re-rendered as an image and it isn't a third-party embed.
- The result behaves exactly like a shape you drew in Slides yourself: resizable, recolourable, editable.

## Questions

### Does Google Slides support SVG natively?
Not as an editable format. Slides rasterizes an inserted SVG into a flattened image, so you lose the ability to edit individual paths or recolour parts of it. SVG to Slides converts it into Slides' native shape format instead, so it stays fully editable.

### What happens to gradients and complex curves?
Solid fills and strokes convert cleanly. Arc commands are converted into smooth curves. Gradients come through in the online converter; in the Chrome extension and add-on they currently collapse to a single solid colour.

### Is my file uploaded anywhere?
Depends on the surface. The Chrome extension converts entirely on your device using an embedded WebAssembly engine, so your file usually never leaves the browser. The online converter and add-on send the file to our backend for conversion. See the privacy policy for specifics.

### Is it free?
Yes. Free forever. Every feature, no daily cap, no account, no Pro tier.
