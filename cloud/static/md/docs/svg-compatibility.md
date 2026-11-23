# SVG feature support

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0; SVG to Slides Workspace Add-on for Google Slides; SVG to Slides Web Uploader.

Paths, basic shapes, arcs, nested transforms and even-odd cut-outs convert in every product. Gradients and text convert only in the Web Uploader. Clip paths, masks, patterns, filters and transparency do not convert.

Tested November 11, 2026 on 20 sample files. Per-file table and sample files: https://svgslid.es/specs.md

## Converts

| SVG feature | Chrome extension and add-on | Web Uploader |
|---|---|---|
| One filled path | Converts. | Works |
| Circle, rounded rectangle and path in three colours | Converts. | Works |
| rect, circle, ellipse, polygon, polyline, line | Lines and polylines become filled outline shapes | Works. Lines and polylines become filled outline shapes |
| Arc commands (A and a) | Converts. | Works |
| translate, rotate and scale on nested groups | Converts. | Works |
| fill-rule="evenodd" cut-outs | Converts. | Works |
| Figma-style frame clip and white background | Frame clip and background skipped | Works. Frame clip and background skipped |

## Converts in part

| SVG feature | Chrome extension and add-on | Web Uploader |
|---|---|---|
| Linear gradient fill | Solid fill in the first colour | Works. Kept as a gradient |
| Radial gradient fill | Solid fill in the first colour; a white-centred gradient pastes white | Works. Kept as a gradient |
| Colours set by CSS classes in a <style> block (Illustrator style) | Shapes kept, colours become black | Partly. Shapes kept, colours become black |
| clip-path that crops a shape | Clip ignored; the full shape shows | Partly. Clip ignored; the full shape shows |
| mask that cuts a hole | Mask ignored | Partly. Mask ignored |
| fill-opacity | Shapes kept, transparency lost | Partly. Shapes kept, transparency lost |
| Pattern fill | Shape kept, filled black | Partly. Shape kept, filled black |
| Drop-shadow filter | Shape kept, shadow dropped | Partly. Shape kept, shadow dropped |
| rgb(), named, short hex and hsl() colours | hsl() becomes black; the rest are exact | Partly. hsl() becomes black; the rest are exact |

## Does not convert

| SVG feature | Chrome extension and add-on | Web Uploader |
|---|---|---|
| Line icon with the stroke set on the root <svg> (Lucide and Feather style) | Nothing pastes | Works. Strokes become filled outline shapes |
| <text> element | Not converted | Works. Outlined into shapes, not editable text |
| <use> referencing a <symbol> (icon sprites) | Not converted | Not converted. Not converted |
| stroke="currentColor" | Not converted | Partly. Converted, but black instead of the inherited colour |


## Reading the table

The extension and the add-on share one converter, so they give the same result. The JavaScript converter in version 1.3.0 was checked against the earlier one and gives the same output for these files. See [How conversion works](https://svgslid.es/docs/how-conversion-works.md#javascript).

## Getting a file to convert

| Problem | What to do |
|---|---|
| A gradient arrives as one colour | Use the [Web Uploader](https://svgslid.es/docs/web-uploader.md), which keeps gradients. |
| Text is missing | Convert the text to outlines in your design tool before exporting, or use the [Web Uploader](https://svgslid.es/docs/web-uploader.md). |
| A line icon inserts nothing | Use the [Web Uploader](https://svgslid.es/docs/web-uploader.md), or outline the strokes before exporting. See [PRB: A line icon inserts nothing](https://svgslid.es/docs/kb/line-icon-inserts-nothing.md). |
| Colours arrive black | Export with colours written on each element. See [PRB: Shapes arrive black](https://svgslid.es/docs/kb/colours-arrive-black.md). |
| A clipped or masked shape shows in full | Apply the clip in your design tool before exporting, or mask it on the slide with [Masking an image](https://svgslid.es/docs/mask-image.md) and [Combining shapes](https://svgslid.es/docs/combine-shapes.md). |

Have a file that does not convert? Send it to the address on the [Support](https://svgslid.es/support) page.

## See also

- [How conversion works](https://svgslid.es/docs/how-conversion-works.md)
- [Inserting SVG files](https://svgslid.es/docs/insert-svg.md)
- [Web Uploader](https://svgslid.es/docs/web-uploader.md)
- [Limits and known issues](https://svgslid.es/docs/limits.md)
- [Specs: tested compatibility table](https://svgslid.es/specs#compatibility)

Source: https://svgslid.es/docs/svg-compatibility (SVG to Slides Documentation, Reference). Last reviewed November 20, 2026.
