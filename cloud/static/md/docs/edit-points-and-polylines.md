# Slides' Edit points and polylines

Applies to: SVG to Slides Chrome extension, version 1.2.0 and later; SVG to Slides Workspace Add-on for Google Slides.

Google Slides has an Edit points command of its own, which works on polylines. Inserted shapes with one outline and only straight segments land as polylines, so that command works on them. Curved shapes land as custom shapes. Use Edit Shape for those.

## The rule

A converted shape lands as a polyline when all three are true:

- It has a single outline, with no holes and no separate pieces.
- Every segment is a straight line.
- It has no more than 150 points.

Rectangles, polygons and other straight-edged closed paths meet the rule. Circles, curved icons and shapes with holes land as custom shapes.

## Why curved shapes are not polylines

Slides' point editor has no model for Bézier curves. These results come from inserting test shapes and dragging a point in each.

| Test | Result |
|---|---|
| A polyline that contains curves | It draws correctly when inserted. On the first point drag, Slides rewrites the whole outline as straight lines, and every curve control point becomes a corner. |
| A polyline with several outlines | Slides merges them into one outline, joining the outer and inner parts with stray diagonal edges. |
| A shape of Slides' curve-tool kind, given curve data | Slides ignores the curve data and draws its own smooth line through every coordinate. A circle made of four curves comes out as a lumpy rounded square. |

So only shapes that Slides' editor can represent exactly are marked for it.

## A difference you can see

| Shape | Double-click in Slides |
|---|---|
| Custom shape | Gives a text cursor. The shape can hold text. |
| Polyline | Enters Slides' point editing. |

## Which editor to use

| To edit | Use |
|---|---|
| A straight-edged shape, corner by corner | Slides' own **Edit points**, or [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md). |
| Any shape with curves or holes | [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md). |
| A shape from Slides' shape menu | [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md), which converts it first. See [Editing Slides' own shapes](https://svgslid.es/docs/convert-slides-shapes.md). |

## See also

- [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md)
- [Editing Slides' own shapes](https://svgslid.es/docs/convert-slides-shapes.md)
- [How conversion works](https://svgslid.es/docs/how-conversion-works.md)
- [INFO: Slides' own Edit points is offered for some inserted shapes only](https://svgslid.es/docs/kb/edit-points-missing.md)

Source: https://svgslid.es/docs/edit-points-and-polylines (SVG to Slides Documentation, Technical Notes). Last reviewed November 24, 2026.
