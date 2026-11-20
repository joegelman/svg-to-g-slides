# PRB: A gradient arrives as one solid colour

Article ID: Q100102. Last reviewed: November 20, 2026.

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0; SVG to Slides Workspace Add-on for Google Slides.

The Chrome extension and the add-on fill each shape with the gradient's first colour. To keep gradients, convert the file with the Web Uploader, which carries them through.

## Symptoms

A shape that has a linear or radial gradient in the SVG lands with one flat colour. A radial gradient with a white centre lands white.

## Cause

The extension and the add-on write each shape with a single fill. They use the first colour stop of the gradient.

## Resolution

**To keep the gradient**

1. Convert the file with the [Web Uploader](https://svgslid.es/docs/web-uploader.md). It keeps linear and radial gradients.
2. Open the Drive link and make a copy of the file.
3. Copy the shapes from the copy into your presentation.

## Status

This is a known limit of the extension and the add-on in the versions listed above.

## See also

- [Web Uploader](https://svgslid.es/docs/web-uploader.md)
- [SVG feature support](https://svgslid.es/docs/svg-compatibility.md#partly)
- [How conversion works](https://svgslid.es/docs/how-conversion-works.md#outputs)

Source: https://svgslid.es/docs/kb/gradient-becomes-solid-colour (SVG to Slides Documentation, Knowledge Base). Last reviewed November 20, 2026.
