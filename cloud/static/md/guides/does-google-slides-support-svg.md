# Does Google Slides™ support SVG?

No. Google Slides doesn't keep SVG files as editable vectors. Your options are to flatten the SVG into a PNG, or convert it through EMF and Google Drawings. SVG to Slides converts the file into Slides' native shape format, so it stays editable.

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

## Why Google Slides can't keep an SVG
- Slides builds everything from its own shapes, text boxes and images. It has no SVG import, so an SVG can only arrive as an image.
- An image is one object. You can't select its parts, recolour them, or edit their points.
- Resizing an image resizes its pixels, so edges blur.
- To stay editable, the SVG's paths have to become Slides' own shape format. That's the conversion SVG to Slides does.

## Which SVG features survive conversion
- Paths, basic shapes, arcs, transforms and even-odd cut-outs convert everywhere.
- Gradients and text convert on the web uploader, not in the extension or add-on.
- Clip paths, masks, patterns, filters and transparency are dropped. Full results for 20 tested SVG features.

## Questions

### Can you import an SVG into Google Slides?
Not as editable vector shapes. Install the SVG to Slides Chrome extension and drag the file onto a slide, or upload it at svgslid.es/convert. Both turn every path into a native Slides shape.

### Why does my SVG look blurry in Google Slides?
It's been flattened into a raster image, so it pixelates when you resize it. Converted with SVG to Slides, it stays a vector and every edge stays sharp.

### What happens to gradients and complex curves?
Solid fills and strokes convert cleanly. Arc commands are converted into smooth curves. Gradients come through in the online converter; in the Chrome extension and add-on they currently collapse to a single solid colour. Tested results are on the specs page.

### Do the converted shapes work in Google Drawings?
Yes. The native shapes also work in Google Drawings.
