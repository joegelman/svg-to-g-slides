# FIX: Inserted shapes landed away from the pointer in versions 1.0.0 and 1.0.1

Article ID: Q100115. Last reviewed: November 20, 2026.

Applies to: SVG to Slides Chrome extension, versions 1.0.0 and 1.0.1.

Versions 1.0.0 and 1.0.1 estimated the position from the size of the window, which was off when Slides was zoomed or its panels were resized. Version 1.2.0 measures the slide itself and centres the graphic on the point you click.

## Symptoms

In version 1.0.0 or 1.0.1 the shapes land some distance from where you clicked. The error grows when Slides is zoomed in, or when the filmstrip or toolbar is not at its default size.

## Cause

Those versions did not read the slide's position. They estimated it from the window size, assuming Slides' default layout.

## Resolution

Update to version 1.2.0 or later. See [Installing and updating](https://svgslid.es/docs/install.md#updates).

## Status

Fixed in version 1.2.0. The extension now measures the slide you have open. In testing, an inserted graphic was centred within 2 pixels of the point clicked.

## More information

Version 1.2.0 also corrects a related fault in which visiting another slide first could throw off both placement and the editor.

## See also

- [Version 1.2.0](https://svgslid.es/docs/release-notes/1-2-0.md)
- [Inserting SVG files](https://svgslid.es/docs/insert-svg.md#size)

Source: https://svgslid.es/docs/kb/shapes-land-away-from-pointer (SVG to Slides Documentation, Knowledge Base). Last reviewed November 20, 2026.
