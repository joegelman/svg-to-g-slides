# How conversion works

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0; SVG to Slides Web Uploader; SVG to Slides Workspace Add-on for Google Slides.

Availability: Version 1.3.0 is not in the Chrome Web Store yet. The store installs version 1.2.0. See [what each version has](https://svgslid.es/docs/release-notes.md#matrix).

Conversion turns every drawable element of the SVG into a path, and every path into one Slides shape with one fill. The extension and the add-on write the shapes in Slides' own form. The Web Uploader writes a presentation file.

## Stages

| Stage | What happens |
|---|---|
| 1. Read | The SVG is parsed. Definitions, clip paths and masks are set aside, and so is a rectangle that only fills the canvas as a background. |
| 2. Paint | Fill and stroke are worked out for each element, including values inherited from the groups around it. |
| 3. Shapes to paths | `rect`, `circle`, `ellipse`, `line`, `polyline` and `polygon` become path data. |
| 4. Arcs to curves | Arc commands are converted into cubic Bézier curves. |
| 5. Strokes to outlines | A stroke with a width is expanded into a filled outline, because the shape that lands has one fill. |
| 6. Transforms | `translate`, `rotate` and `scale` on the element and on its groups are applied to the points. |
| 7. Write | Each path becomes one shape with a tight bounding box. Shapes from one file are grouped. |

## Two outputs

|  | Extension and add-on | Web Uploader |
|---|---|---|
| Output | Slides' own shape data, handed to the open slide. See [How shapes reach the slide](https://svgslid.es/docs/how-shapes-reach-the-slide.md). | A presentation file with one slide per SVG, each path a custom-geometry shape. |
| Gradients | The first colour stop becomes a solid fill. | Kept as gradients. |
| Text and some strokes | Not converted. | Outlined on the server before conversion. |

## The JavaScript converter in version 1.3.0

Up to version 1.2.0 the extension carried a Python runtime compiled to WebAssembly and ran the same Python converter the server runs. That runtime was most of the installed size.

Version 1.3.0 replaces it with a JavaScript converter that follows the Python one line for line, including its rounding rules and its error cases. The two were compared before release:

| Check | Result |
|---|---|
| All 138 SVG files in the project's repository, and multi-file drops | Output identical, byte for byte. |
| 3,000 randomly generated SVG files | Identical except for 3 files with a perfect half-ellipse arc, where the last bit of a floating-point result decides whether the same shape is written as two curve pieces or three. |

The installed size fell from 14 MB to 1.1 MB. With no runtime to fall back from, the server fallback and its host permission were removed. See [Version 1.3.0](https://svgslid.es/docs/release-notes/1-3-0.md#packaging).

## Why some features do not convert

A Slides shape has one outline and one fill. SVG features that depend on something else, such as a clip path, a mask, a filter, a pattern or per-element transparency, have no place to go and are dropped or ignored. Colours written as `hsl()` are not parsed and arrive black. The tested results are in [SVG feature support](https://svgslid.es/docs/svg-compatibility.md).

## See also

- [SVG feature support](https://svgslid.es/docs/svg-compatibility.md)
- [How shapes reach the slide](https://svgslid.es/docs/how-shapes-reach-the-slide.md)
- [Point precision](https://svgslid.es/docs/point-precision.md)
- [Edit points and polylines](https://svgslid.es/docs/edit-points-and-polylines.md)

Source: https://svgslid.es/docs/how-conversion-works (SVG to Slides Documentation, Technical Notes). Last reviewed November 20, 2026.
