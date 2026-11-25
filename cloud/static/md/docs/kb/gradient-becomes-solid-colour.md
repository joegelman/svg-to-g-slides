# FIX: A gradient arrives as one solid colour

Article ID: Q100102. Last reviewed: November 24, 2026.

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.3.1; SVG to Slides Workspace Add-on for Google Slides.

Versions of the Chrome extension before 1.4.0, and the add-on, fill each shape with the gradient's first colour. Version 1.4.0 of the extension keeps linear and radial gradients. The Web Uploader has always kept them.

## Symptoms

A shape that has a linear or radial gradient in the SVG lands with one flat colour. A radial gradient with a white centre lands white.

## Cause

Extension versions before 1.4.0 and the add-on write each shape with a single fill. They use the first colour stop of the gradient.

## Resolution

**To keep the gradient**

1. Update the extension to version 1.4.0 or later. Chrome does this on its own. To check, see [HOWTO: Find which version of the extension is installed](https://svgslid.es/docs/kb/which-version.md).
2. Insert the file again. Linear and radial gradients arrive as Slides gradients, and transparency is kept.

If you use the add-on, or cannot update, convert the file with the [Web Uploader](https://svgslid.es/docs/web-uploader.md), make a copy of the Drive file, and copy the shapes into your presentation.

## Status

Fixed in version 1.4.0 of the Chrome extension. The add-on still fills with the first colour. A `gradientTransform` on the gradient is not applied.

## See also

- [Inserting SVG files](https://svgslid.es/docs/insert-svg.md#converts)
- [Web Uploader](https://svgslid.es/docs/web-uploader.md)
- [SVG feature support](https://svgslid.es/docs/svg-compatibility.md#partly)
- [How conversion works](https://svgslid.es/docs/how-conversion-works.md#outputs)
- [Version 1.4.0](https://svgslid.es/docs/release-notes/1-4-0.md)

Source: https://svgslid.es/docs/kb/gradient-becomes-solid-colour (SVG to Slides Documentation, Knowledge Base). Last reviewed November 24, 2026.
