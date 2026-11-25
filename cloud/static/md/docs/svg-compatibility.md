# SVG feature support

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.4.0; SVG to Slides Workspace Add-on for Google Slides; SVG to Slides Web Uploader.

Paths, basic shapes, arcs, nested transforms and even-odd cut-outs convert in every product. Gradients convert in the Web Uploader and, since version 1.4.0, in the extension, which also keeps transparency. Text converts only in the Web Uploader. Masks, patterns and filters do not convert.

Tested November 11, 2026 on 20 sample files. Per-file table and sample files: https://svgslid.es/specs.md

## Converts

| SVG feature | Chrome extension and add-on | Web Uploader |
|---|---|---|
| One filled path | Converts. | Works |
| Circle, rounded rectangle and path in three colours | Converts. | Works |
| rect, circle, ellipse, polygon, polyline, line | Lines and polylines become filled outline shapes | Works. Lines and polylines become filled outline shapes |
| Line icon with the stroke set on the root <svg> (Lucide and Feather style) | Strokes become filled outline shapes | Works. Strokes become filled outline shapes |
| Arc commands (A and a) | Converts. | Works |
| translate, rotate and scale on nested groups | Converts. | Works |
| fill-rule="evenodd" cut-outs | Converts. | Works |
| Linear gradient fill | Kept as a gradient | Works. Kept as a gradient |
| Radial gradient fill | Kept as a gradient | Works. Kept as a gradient |
| Colours set by CSS classes in a <style> block (Illustrator style) | Converts. | Partly. Shapes kept, colours become black |
| Figma-style frame clip and white background | Frame clip and background skipped | Works. Frame clip and background skipped |
| clip-path that crops a shape | Cropped to the clip shape | Partly. Clip ignored; the full shape shows |
| <use> referencing a <symbol> (icon sprites) | Converts. | Not converted. Not converted |
| fill-opacity | Transparency kept | Partly. Shapes kept, transparency lost |
| stroke="currentColor" | Strokes become filled outline shapes | Partly. Converted, but black instead of the inherited colour |
| rgb(), named, short hex and hsl() colours | Converts. | Partly. hsl() becomes black; the rest are exact |

## Converts in part

| SVG feature | Chrome extension and add-on | Web Uploader |
|---|---|---|
| mask that cuts a hole | Mask ignored | Partly. Mask ignored |
| Pattern fill | Shape kept, filled black | Partly. Shape kept, filled black |
| Drop-shadow filter | Shape kept, shadow dropped | Partly. Shape kept, shadow dropped |

## Does not convert

| SVG feature | Chrome extension and add-on | Web Uploader |
|---|---|---|
| <text> element | Not converted | Works. Outlined into shapes, not editable text |


## Reading the table

The extension column is for version 1.4.0. Version 1.3.1 added outline icon sets, colours from CSS classes, clip paths and use with symbol. Version 1.4.0 added gradients and transparency. The Workspace Add-on runs the earlier converter: it fills a gradient with its first colour and does not keep transparency. See [How conversion works](https://svgslid.es/docs/how-conversion-works.md#javascript).

## Getting a file to convert

| Problem | What to do |
|---|---|
| A gradient arrives as one colour | Update the extension to version 1.4.0, which keeps gradients, or use the [Web Uploader](https://svgslid.es/docs/web-uploader.md). See [FIX: A gradient arrives as one solid colour](https://svgslid.es/docs/kb/gradient-becomes-solid-colour.md). |
| Text is missing | Convert the text to outlines in your design tool before exporting, or use the [Web Uploader](https://svgslid.es/docs/web-uploader.md). |
| A line icon inserts nothing | Update the extension to version 1.3.1 or later. See [PRB: A line icon inserts nothing](https://svgslid.es/docs/kb/line-icon-inserts-nothing.md). |
| Colours arrive black | Export with colours written on each element. See [PRB: Shapes arrive black](https://svgslid.es/docs/kb/colours-arrive-black.md). |
| A masked shape shows in full | Apply the mask in your design tool before exporting, or mask it on the slide with [Masking an image](https://svgslid.es/docs/mask-image.md) and [Combining shapes](https://svgslid.es/docs/combine-shapes.md). |

Have a file that does not convert? Send it to the address on the [Support](https://svgslid.es/support) page.

## See also

- [How conversion works](https://svgslid.es/docs/how-conversion-works.md)
- [Inserting SVG files](https://svgslid.es/docs/insert-svg.md)
- [Web Uploader](https://svgslid.es/docs/web-uploader.md)
- [Limits and known issues](https://svgslid.es/docs/limits.md)
- [Specs: tested compatibility table](https://svgslid.es/specs#compatibility)

Source: https://svgslid.es/docs/svg-compatibility (SVG to Slides Documentation, Reference). Last reviewed November 24, 2026.
