# Inserting SVG files

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0. Click to place: version 1.2.0 and later. Pasting SVG code: version 1.3.0..

Drag one or more .svg files from your computer onto an open Google Slides tab, then click where they go. Every path lands as its own native shape. Paths from one file arrive as a group.

**To insert an SVG file**

1. Open the presentation in Google Chrome.
2. Drag the .svg file from a folder or the desktop onto the slide. A faint preview of the file follows the pointer, with a green plus badge and the label **Click to Place**.
3. Click the point where the graphic should be centred.

The shapes appear at that point, selected. Nothing needs pasting.

![A slide with a faint palm icon under the pointer, a green plus badge and a grey pill reading Click to Place](https://svgslid.es/static/docs/img/insert-click-to-place.jpg)
Figure 1. After the drop. The preview follows the pointer until you click.

## Size and position

The graphic is fitted to about a fifth of the slide and centred on the point you click. Resize it afterwards with Slides' selection handles.

From version 1.3.0 a graphic keeps all of its detail however small it lands, so it can be enlarged later without loss. See [Point precision](https://svgslid.es/docs/point-precision.md).

## Several files at once

Select up to 25 .svg files and drag them together. They land on the current slide in a grid, each file as its own group.

If the drop holds more than 25 .svg files, nothing is inserted and a message says so. Use the [Web Uploader](https://svgslid.es/docs/web-uploader.md) for larger batches. See [PRB: Nothing is inserted when more than 25 files are dropped](https://svgslid.es/docs/kb/more-than-25-files.md).

## Pasting SVG code

In version 1.3.0, SVG markup copied as text can be pasted onto the slide. Copy the code, click the slide and press Command+V. The same preview appears, and you click to place it.

## Cancelling

Press Esc before you click. The preview disappears and nothing is inserted.

## Files that are not SVG

A drop that holds no .svg file is left to Slides, which handles it as it always does.

## If the extension asks you to press COMMAND+V

The extension hands the shapes to Slides the way a paste does. If Slides does not accept them, the extension shows a prompt to press Command+V. Press it and the shapes land. See [INFO: The extension asks you to press COMMAND+V](https://svgslid.es/docs/kb/press-command-v-prompt.md).

> **Note:** In versions 1.0.0 and 1.0.1 every insert ended with Command+V. The click has inserted directly since version 1.2.0.

## What converts

Paths, basic shapes, arcs, transforms and cut-outs convert. A gradient arrives as its first colour. Text, clip paths, masks, patterns and filters do not convert in the extension. The full table is in [SVG feature support](https://svgslid.es/docs/svg-compatibility.md).

## See also

- [Quick start](https://svgslid.es/docs/quick-start.md)
- [SVG feature support](https://svgslid.es/docs/svg-compatibility.md)
- [Web Uploader](https://svgslid.es/docs/web-uploader.md)
- [How shapes reach the slide](https://svgslid.es/docs/how-shapes-reach-the-slide.md)
- [PRB: An SVG placed in Google Slides becomes a flat image](https://svgslid.es/docs/kb/svg-becomes-a-flat-image.md)
- [Guide: How to insert an SVG into Google Slides](https://svgslid.es/guides/insert-svg-into-google-slides)

Source: https://svgslid.es/docs/insert-svg (SVG to Slides Documentation, User's Guide). Last reviewed November 20, 2026.
