# Drawing with the pen

Applies to: SVG to Slides Chrome extension, version 1.3.0.

The pen draws new shapes point by point, anywhere on the slide. Press Option+Shift+P or click **Pen** on the toolbar. Click for a corner, drag for a curve, and click the first point to close the shape.

**To draw a shape**

1. With nothing selected, press Option+Shift+P or click **Pen** on the toolbar. An empty editor opens over the slide.
2. Click to place a corner point. To make a curve, press, drag and release.
3. Click the first point to close the shape. A ring appears on the first point when the pointer is over it. To leave the path open, press Enter or Esc.
4. Click **Done**. The new shapes are placed on the slide, on top.

![The pen editor over a slide with a grid showing. A speech-bubble outline is half drawn, with a dashed line from the last point to the pointer and a pink mark where it will snap.](https://svgslid.es/static/docs/img/pen-drawing.jpg)
Figure 1. Seven points placed with the grid on. The dashed segment follows the pointer and the pink mark shows where the next point will snap.

## Pen keys

| To do this | Do this |
|---|---|
| Place a corner point | Click. |
| Place a smooth point | Press, drag, release. |
| Make a sharp turn after a curve | Hold Option while dragging to break the handles. |
| Keep to 45° steps | Hold Shift. |
| Close the shape | Click the first point. |
| Leave the path open | Enter or Esc |
| Remove the last point | Delete |
| Undo one point | Command+Z |
| Carry on an open path | Click its end point. |
| Add a point to a path | Click a segment. |
| Remove a point from a path | Click the point. |
| Switch to the Select tool | V |

## What you get

Each path becomes a new shape. The first shape you draw has a 2 pixel dark stroke and no fill. Each later shape starts with the paint of the last one drawn. Set a fill or stroke from the editor's toolbar before you click **Done**, or afterwards on the slide.

**Done** places all the new shapes in one undo step.

## Pen with shapes selected

If shapes are selected when you press Option+Shift+P, the editor opens on those shapes and the pen can both edit them and draw new ones beside them.

## Limits

The pen draws point by point. There is no freehand mode.

## See also

- [Snapping](https://svgslid.es/docs/snapping.md)
- [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md)
- [Fill, stroke and exact values](https://svgslid.es/docs/fill-stroke.md)
- [Combining shapes](https://svgslid.es/docs/combine-shapes.md)
- [Keyboard shortcuts](https://svgslid.es/docs/keyboard-shortcuts.md#editor)

Source: https://svgslid.es/docs/pen (SVG to Slides Documentation, User's Guide). Last reviewed November 20, 2026.
