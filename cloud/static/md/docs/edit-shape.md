# Edit Shape: points and curves

Applies to: SVG to Slides Chrome extension, versions 1.2.0 and 1.3.0. The box, exact values and the two-column editor toolbar: version 1.3.0..

Edit Shape opens a vector editor on the slide at the shape's exact size and position. Drag points and curve handles, add or remove points, then click **Done**. The shape updates in place and returns to its place in the stack.

**To edit a shape's points**

1. Double-click the shape, then click **Edit Shape**. In version 1.3.0 you can also select the shape and click **Edit Shape** on the toolbar.
2. Drag a point to move it. Click a point to see its curve handles, and drag a handle to change the curve.
3. Click **Done**, or press Enter.

![The Edit Shape editor open on a palm tree icon. Every point of the outline is marked, a box with handles surrounds the shape, and the editor toolbar is at the left.](https://svgslid.es/static/docs/img/edit-shape.jpg)
Figure 1. Edit Shape open on a palm icon, version 1.3.0. Round marks are smooth points and square marks are corner points.
1. **Select** tool. V
2. **Pen** tool. Adds and removes points, and draws. P
3. **Snapping**. See [Snapping](https://svgslid.es/docs/snapping.md).
4. The same command groups as the main toolbar: Arrange, Align, Combine, Group, Outline, fill and stroke.
5. Undo and redo, point by point.
6. Zoom. Click to return to 100%.
7. **Cancel**. Discards the edit.
8. **Done**. Applies the edit.
9. Size pill: width, height and rotate-by. On shapes with corners it also shows the corner radius.
10. The hint line names the keys for the current tool.

## Points and handles

| To do this | Do this |
|---|---|
| Move a point | Drag it. Hold Shift to keep to 45° steps. |
| Change a curve | Click the point, then drag one of its handles. |
| Move one handle only | Hold Option while dragging the handle. |
| Switch a point between smooth and corner | Double-click the point. |
| Add a point | Press P, then click the outline where the point should be. |
| Remove a point | Press P, then click the point. |
| Select several points | Shift-click each one, or drag a box around them. |
| Select every point of a shape | Click the shape. |
| Select all points | Command+A |
| Nudge | Arrow keys. Hold Shift for ten times the step. |
| Delete the selected points | Delete |
| Undo, redo | Command+Z, Shift+Command+Z |
| Zoom | Pinch, or Command+Plus and Command+Minus. Command+0 returns to 100%. |
| Pan | Hold Spacebar and drag, or scroll. |

![A palm tree outline with one point selected and its two curve handles extended, the pointer on a handle](https://svgslid.es/static/docs/img/edit-points-1-2.jpg)
Figure 2. A selected point and its two handles. Recorded in Google Slides with version 1.2.0, whose editor toolbar had one column.

## The box

In version 1.3.0 a box surrounds the selection inside the editor. Dragging it transforms the shape while its points stay editable.

| Drag | Result |
|---|---|
| A corner | Scale. Shift keeps the proportions. Option scales from the centre. |
| An edge | Stretch in one direction. Option stretches from the centre. |
| Command + an edge | Skew. Shift snaps to 15°. |
| Command + a corner, or just outside a corner | Rotate. Shift snaps to 15°. |

## Typing exact values

The pill under the shape holds the width and height in pixels, a rotate-by field and, on shapes with corners, the corner radius. Type a value and press Enter. Hold Option and drag across any number to change it by dragging. Add Shift for steps of ten.

## Commands inside the editor

The editor's toolbar repeats the command groups of the main toolbar. Inside the editor a command acts on the shapes that have selected points, or on every shape in the editor when no point is selected. Combine, group, ungroup, outline, fill and stroke are held in the editor and applied when you click **Done**.

## Done and Cancel

**Done** replaces the shape on the slide with the edited one, in the same place in the stack. Shapes above it stay visible while you edit, so you can line points up against them. In version 1.3.0 the whole session is one undo step. See [Undo and redo](https://svgslid.es/docs/undo-redo.md).

**Cancel** discards the edit. Esc clears the selection first. With nothing selected, Esc applies the edit the same as **Done**.

> **Important:** **Done** puts a new object in place of the original. Animations and links attached to the original do not carry over. A shape edited from inside a group comes back just above that group.

## What can be edited

Edit Shape opens directly on shapes inserted by SVG to Slides. On Slides' own shapes, lines, text boxes and WordArt it converts the object first. See [Editing Slides' own shapes](https://svgslid.es/docs/convert-slides-shapes.md). Images, video and charts cannot be edited as shapes.

## See also

- [Rounding corners](https://svgslid.es/docs/round-corners.md)
- [Drawing with the pen](https://svgslid.es/docs/pen.md)
- [Snapping](https://svgslid.es/docs/snapping.md)
- [Editing Slides' own shapes](https://svgslid.es/docs/convert-slides-shapes.md)
- [Undo and redo](https://svgslid.es/docs/undo-redo.md)
- [Keyboard shortcuts](https://svgslid.es/docs/keyboard-shortcuts.md#editor)
- [Edit points and polylines](https://svgslid.es/docs/edit-points-and-polylines.md)

Source: https://svgslid.es/docs/edit-shape (SVG to Slides Documentation, User's Guide). Last reviewed November 20, 2026.
