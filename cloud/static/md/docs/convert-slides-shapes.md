# Editing Slides' own shapes

Applies to: SVG to Slides Chrome extension, version 1.2.0 and later.

Edit Shape also opens on objects you did not bring in as SVG: shapes from Slides' shape menu, arrows, callouts, lines, text boxes and WordArt. It converts the object into custom shapes first, and tells you what that costs before you start.

## How it works

Double-click the object. Slides does what it always does: it starts text editing or steps into the group. The **Edit Shape** button also appears, with a note of the cost in grey beside it, for example "text becomes outlines". Click the button to convert the object and open the editor.

The result looks the same as the original. It is a drawing made of custom shapes and is no longer the original preset, line or WordArt.

## What each object becomes

| Object | After conversion | What is lost |
|---|---|---|
| A shape-menu shape with one outline: arrow, callout, star, rounded rectangle | One shape | Adjustment handles, the small yellow diamonds. |
| A shaded shape: cube, can | A group. A cube becomes 4 shapes, a can 3. | Automatic shading. The shades are kept as flat colours. |
| A line or connector with ends | A group: the stroke and each arrowhead | Connection points. Arrowheads become separate shapes. |
| A shape with text in it | One shape, text kept |  |
| A text box | One shape with no fill and no stroke, text kept |  |
| WordArt | A group of letter outlines | The text. The letters can be reshaped but not retyped. |

Text inside a shape stays editable after conversion.

## Cancel and Done

**Cancel** puts the original object back. **Done** keeps the converted shapes.

> **Caution:** After **Done** the conversion is one-way. To get the original back, undo.

## Not handled

- Gradient and pattern fills, fill transparency, dash styles and shadows are not carried over.
- Images, video and charts cannot be converted.

## See also

- [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md)
- [Rounding corners](https://svgslid.es/docs/round-corners.md)
- [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md)
- [Edit points and polylines](https://svgslid.es/docs/edit-points-and-polylines.md)

Source: https://svgslid.es/docs/convert-slides-shapes (SVG to Slides Documentation, User's Guide). Last reviewed November 24, 2026.
