# PRB: A line icon inserts nothing

Article ID: Q100104. Last reviewed: November 20, 2026.

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0; SVG to Slides Workspace Add-on for Google Slides.

Icons that set their stroke once on the root svg element, or use stroke="currentColor", are not converted by the extension. Convert them with the Web Uploader, or outline the strokes in your design tool before exporting.

## Symptoms

You drop a line icon and click to place it. Nothing lands on the slide. Icon sets drawn with strokes, in the style of Lucide and Feather, are the usual case.

## Cause

These icons do not put a stroke on each path. They set it once on the root `<svg>` element, often as `stroke="currentColor"`. The extension's converter does not pick up a stroke set there, and it does not resolve `currentColor`, so it finds nothing to draw.

Strokes written on the elements themselves, with a stated colour, do convert. They land as filled outline shapes.

## Resolution

Use either method.

- Convert the icons with the [Web Uploader](https://svgslid.es/docs/web-uploader.md). It converts strokes set on the whole SVG into filled outline shapes. A `currentColor` stroke comes out black, and you can recolour it in Slides.
- In your design tool, outline the strokes, then export again.

## Status

This is a known limit of the extension and the add-on. Test files 04 and 17 on the [Specs page](https://svgslid.es/specs#compatibility) cover it.

## See also

- [SVG feature support](https://svgslid.es/docs/svg-compatibility.md)
- [Web Uploader](https://svgslid.es/docs/web-uploader.md)
- [How conversion works](https://svgslid.es/docs/how-conversion-works.md#stages)
- [Guide: SVG logos and icons in Slides themes](https://svgslid.es/guides/svg-logos-icons-google-slides)

Source: https://svgslid.es/docs/kb/line-icon-inserts-nothing (SVG to Slides Documentation, Knowledge Base). Last reviewed November 20, 2026.
