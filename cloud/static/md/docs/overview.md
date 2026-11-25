# What SVG to Slides does

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.4.0; SVG to Slides Web Uploader; SVG to Slides Workspace Add-on for Google Slides.

Google Slides has no SVG import. An SVG placed on a slide is flattened into a picture. SVG to Slides converts each path of the SVG into a native Slides shape, so the result can be selected, recoloured, resized and reshaped like a shape drawn in Slides.

## The three products

| Product | How you use it | Where conversion runs | What you get |
|---|---|---|---|
| **Chrome extension** | Drag .svg files onto an open Slides tab and click where they go. | In your browser. | Native shapes on the slide you have open. See [Inserting SVG files](https://svgslid.es/docs/insert-svg.md). |
| **Web Uploader** | Upload files on a web page. No install. | On the svgslid.es server. | A Google Drive link to a file with one slide per SVG. See [Web Uploader](https://svgslid.es/docs/web-uploader.md). |
| **Workspace Add-on** | Pick files in a dialog inside Slides, copy, paste. | On the svgslid.es server. | Native shapes on the current slide. See [Workspace Add-on](https://svgslid.es/docs/add-on.md). |

The shapes are ordinary Slides objects. They take the standard fill picker, resize without loss of quality, work in themes, and work in Google Drawings.

## What the extension adds on the slide

From version 1.2.0 the extension edits shapes as well as importing them. Version 1.3.0 adds a toolbar and the tools below.

| Tool | What it is for | Topic |
|---|---|---|
| Edit Shape | Move the points and curves of any shape. | [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md) |
| Round corners | Drag or type a corner radius. | [Rounding corners](https://svgslid.es/docs/round-corners.md) |
| Pen | Draw new shapes point by point. | [Drawing with the pen](https://svgslid.es/docs/pen.md) |
| Snapping | Snap points to other points, pixels or a grid. | [Snapping](https://svgslid.es/docs/snapping.md) |
| Mask | Cut a picture to any shape. | [Masking an image](https://svgslid.es/docs/mask-image.md) |
| Combine | Union, subtract, intersect, exclude. | [Combining shapes](https://svgslid.es/docs/combine-shapes.md) |
| Align and distribute | Instant, images included. | [Aligning and distributing](https://svgslid.es/docs/align-distribute.md) |
| Layers | List, rename, hide and restack objects. | [The Layers panel](https://svgslid.es/docs/layers.md) |
| Outline | Turn strokes and text into shapes. | [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md) |
| Command palette | Every command and its shortcut. | [The command palette](https://svgslid.es/docs/command-palette.md) |

## Price and account

SVG to Slides is free. There is no account, no daily cap and no paid tier. The extension asks for no access to your Google account. See [Permissions and data](https://svgslid.es/docs/permissions-privacy.md).

## What does not convert

Some SVG features have no Slides equivalent or are not handled yet. Clip paths, masks, pattern fills, filters and transparency are examples. The tested list is in [SVG feature support](https://svgslid.es/docs/svg-compatibility.md).

## See also

- [Installing and updating](https://svgslid.es/docs/install.md)
- [Quick start](https://svgslid.es/docs/quick-start.md)
- [How conversion works](https://svgslid.es/docs/how-conversion-works.md)
- [Specs: product facts](https://svgslid.es/specs#facts)
- [Guide: Does Google Slides support SVG?](https://svgslid.es/guides/does-google-slides-support-svg)

Source: https://svgslid.es/docs/overview (SVG to Slides Documentation, Getting Started). Last reviewed November 24, 2026.
