# SVG in Google Slides: vector vs. flattened PNG

Drop an SVG onto a Slides canvas the normal way and Google flattens it into a raster image. Here's what that costs you, and how to avoid it.

## What you lose when Slides flattens your SVG

| Pasted as PNG (default) | Inserted as vector (svgslid.es) |
|---|---|
| Blurs or pixelates when resized | Resizes at any size, always crisp |
| One flattened image, single object | Every path is its own selectable shape |
| Can't recolor without re-exporting | Recolor any shape directly in Slides |
| Can't animate individual elements | Animate each shape independently |
| Can't edit points/paths | Right-click → Edit points, like any native shape |

## How svgslid.es keeps it a vector

Every `<path>` in your SVG is converted directly into Google Slides' own native shape format. It isn't re-rendered as an image or embedded by a third party. The result behaves exactly like a shape you drew in Slides yourself.

- **Web app** (https://svgslid.es/convert): upload one or more SVGs, get back a Google Drive link to a ready-made Slides deck, one slide per file.
- **Google Slides add-on** (https://svgslid.es/addon): insert SVGs from a dialog inside Slides.
- **Chrome extension** (https://chromewebstore.google.com/detail/svg-to-slides/bdhhnakellmdnbgbdokiojipaebdeioi): drag an SVG file straight onto an open Slides tab.

## Frequently asked

### Does Google Slides support SVG natively?
Not as an editable format. Slides will accept a pasted or inserted SVG, but it rasterizes it into a flattened image on the way in, so you lose the ability to edit individual paths or recolor parts of it. svgslid.es converts it into Slides' native shape format instead, so it stays fully editable.

### What happens to gradients and complex curves?
Solid fills and strokes convert cleanly. Gradients currently collapse to a solid approximate color, and arc commands (A/a) in paths are approximated as straight line segments. Re-exporting with more path segments avoids visibly angular curves.

### Is my file uploaded anywhere?
Depends on the surface. The Chrome extension converts entirely on your device using an embedded WebAssembly engine, so your file usually never leaves the browser. The web app and add-on send the file to our backend for conversion, which discards it immediately afterward.

### Is it free?
Yes. Free forever. Every feature, no daily cap, no account, no Pro tier.
