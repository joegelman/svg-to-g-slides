# Release notes and version history

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.4.0; SVG to Slides Web Uploader; SVG to Slides Workspace Add-on.

Version 1.4.0 is the current release of the Chrome extension. It adds a colour panel with opacity and an eyedropper, a gradient builder, Replace a colour across a slide or the whole presentation, live preview, and image masks that keep their shape. SVG gradients and transparency now come across on import. Each release has a technical changelog below.

## Chrome extension versions

| Version | Date | What it added | Download | Installed | Chrome permissions |
|---|---|---|---|---|---|
| [1.4.0](https://svgslid.es/docs/release-notes/1-4-0.md) | November 24, 2026 | Colour panel, gradient builder, text colour, Replace a colour, live preview, masks that keep their shape, the picture adjustable under its mask, gradients and transparency on import | 434 KB | 1.3 MB | storage |
| 1.3.1 | November 2026 | Outline icon sets convert (strokes set on the root element), round caps and joins, colours from CSS classes, currentColor, hsl(), clip paths, use and symbol | 399 KB | 1.1 MB | storage |
| [1.3.0](https://svgslid.es/docs/release-notes/1-3-0.md) | November 2026 | Toolbar, pen, snapping, image masks, combine, one-press undo, instant align, Layers, outline stroke and text, command palette, full-precision points, JavaScript converter | 392 KB | 1.1 MB | storage |
| [1.2.0](https://svgslid.es/docs/release-notes/1-2-0.md) | November 2026 | Edit Shape, round corners, editing Slides' own shapes, click to insert, exact placement | 5.8 MB | 14 MB | storage, one host permission |
| [1.0.1](https://svgslid.es/docs/release-notes/1-0.md) | July 2026 | Removed an unused permission |  |  | One host permission |
| [1.0.0](https://svgslid.es/docs/release-notes/1-0.md) | July 2026 | First release: drag SVG files onto a slide |  |  |  |

Version 1.1.0 was an internal build and was not released. Its changes shipped in 1.2.0.

> **Note:** A new version reaches installed copies through the Chrome Web Store's automatic update, once the store has published it. To see which version you have, see [Installing and updating](https://svgslid.es/docs/install.md#check-version).

## Feature availability by version

| Feature | 1.0 | 1.2 | 1.3 | 1.4 |
|---|---|---|---|---|
| Insert SVG files by drag and drop | Yes | Yes | Yes | Yes |
| Up to 25 files per drop | Yes | Yes | Yes | Yes |
| Converts in the browser | Yes | Yes | Yes | Yes |
| Click places the shapes, with no Command+V |  | Yes | Yes | Yes |
| Placement measured from the slide |  | Yes | Yes | Yes |
| [Edit Shape](https://svgslid.es/docs/edit-shape.md) |  | Yes | Yes | Yes |
| [Round corners](https://svgslid.es/docs/round-corners.md) |  | Yes | Yes | Yes |
| [Edit Slides' own shapes](https://svgslid.es/docs/convert-slides-shapes.md) |  | Yes | Yes | Yes |
| Straight-edged shapes work with Slides' Edit points |  | Yes | Yes | Yes |
| [Toolbar](https://svgslid.es/docs/toolbar.md) and [command palette](https://svgslid.es/docs/command-palette.md) |  |  | Yes | Yes |
| [Pen](https://svgslid.es/docs/pen.md) and [snapping](https://svgslid.es/docs/snapping.md) |  |  | Yes | Yes |
| [Mask image with shape](https://svgslid.es/docs/mask-image.md) |  |  | Yes | Yes |
| [Union, subtract, intersect, exclude](https://svgslid.es/docs/combine-shapes.md) |  |  | Yes | Yes |
| [Align and distribute commands](https://svgslid.es/docs/align-distribute.md) |  |  | Yes | Yes |
| [Layers panel](https://svgslid.es/docs/layers.md) and theme builder shortcut |  |  | Yes | Yes |
| [Outline stroke, outline text, stroke position](https://svgslid.es/docs/outline-stroke-text.md) |  |  | Yes | Yes |
| [One-press undo](https://svgslid.es/docs/undo-redo.md) |  |  | Yes | Yes |
| Paste SVG code |  |  | Yes | Yes |
| [Full-precision points](https://svgslid.es/docs/point-precision.md) |  |  | Yes | Yes |
| Server fallback for conversion | Yes | Yes | Removed | Removed |
| Outline icon sets, CSS class colours, clip paths, use and symbol |  |  | 1.3.1 | Yes |
| [Colour panel with opacity and eyedropper](https://svgslid.es/docs/fill-stroke.md#panel) |  |  |  | Yes |
| [Gradient builder](https://svgslid.es/docs/fill-stroke.md#gradients) |  |  |  | Yes |
| [Text colour for highlighted words](https://svgslid.es/docs/fill-stroke.md#text) |  |  |  | Yes |
| [Replace a colour, one slide or all](https://svgslid.es/docs/fill-stroke.md#replace) |  |  |  | Yes |
| [Live preview](https://svgslid.es/docs/fill-stroke.md#preview) |  |  |  | Yes |
| [Mask keeps the shape as an outline](https://svgslid.es/docs/mask-image.md#result) |  |  |  | Yes |
| [Move the picture under its mask](https://svgslid.es/docs/mask-image.md#adjust) |  |  |  | Yes |
| [Gradients and transparency on import](https://svgslid.es/docs/insert-svg.md#converts) |  |  |  | Yes |

## Web Uploader and Workspace Add-on

| Product | Available since |
|---|---|
| [Web Uploader](https://svgslid.es/docs/web-uploader.md) | June 2026 |
| [Workspace Add-on](https://svgslid.es/docs/add-on.md) | July 2026, on the Google Workspace Marketplace |

Both are updated in place and carry no version number in these notes.

## How to read a changelog

| Mark | Meaning |
|---|---|
| NEW | Added in this version. |
| CHG | Behaviour that changed. |
| FIX | A fault corrected. |
| REM | Removed. |

## Release posts

The illustrated release posts, with animations of each feature, are on the [What's new](https://svgslid.es/whats-new) page.

## See also

- [Version 1.4.0](https://svgslid.es/docs/release-notes/1-4-0.md)
- [Version 1.3.0](https://svgslid.es/docs/release-notes/1-3-0.md)
- [Version 1.2.0](https://svgslid.es/docs/release-notes/1-2-0.md)
- [Versions 1.0.0 and 1.0.1](https://svgslid.es/docs/release-notes/1-0.md)
- [Installing and updating](https://svgslid.es/docs/install.md#updates)
- [What's new: release posts](https://svgslid.es/whats-new)

Source: https://svgslid.es/docs/release-notes (SVG to Slides Documentation, Release Notes). Last reviewed November 24, 2026.
