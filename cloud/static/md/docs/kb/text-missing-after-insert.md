# PRB: Text in an SVG does not appear on the slide

Article ID: Q100103. Last reviewed: November 20, 2026.

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0; SVG to Slides Workspace Add-on for Google Slides.

The extension and the add-on do not convert SVG text elements. Convert the text to outlines in your design tool before exporting, or use the Web Uploader, which outlines text into shapes.

## Symptoms

The shapes of the SVG land on the slide. Words that were text in the SVG are not there.

## Cause

The extension and the add-on convert paths and basic shapes. They do not convert `<text>` elements.

## Resolution

Use either method.

- In your design tool, convert the text to outlines, then export the SVG again. The letters are then paths, and paths convert.
- Convert the file with the [Web Uploader](https://svgslid.es/docs/web-uploader.md). It outlines text on the server.

Either way the words arrive as shapes. They look the same but cannot be retyped. To have editable text, add a Slides text box.

## Status

This is a known limit of the extension and the add-on.

## See also

- [SVG feature support](https://svgslid.es/docs/svg-compatibility.md#not-converted)
- [Web Uploader](https://svgslid.es/docs/web-uploader.md)
- [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md)

Source: https://svgslid.es/docs/kb/text-missing-after-insert (SVG to Slides Documentation, Knowledge Base). Last reviewed November 20, 2026.
