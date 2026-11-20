# Snapping

Applies to: SVG to Slides Chrome extension, version 1.3.0.

Availability: Version 1.3.0 is not in the Chrome Web Store yet. The store installs version 1.2.0. See [what each version has](https://svgslid.es/docs/release-notes.md#matrix).

Snapping pulls pen points and dragged points onto other points, the slide's edges and centre, whole pixels, or a grid. The magnet button in the editor's toolbar sets it. Points and pixels are on to start.

![The Snapping pop-out beside the editor toolbar with three toggle buttons and a grid size field reading 10 px](https://svgslid.es/static/docs/img/snapping-menu.jpg)
Figure 1. The Snapping pop-out.
1. **Snap to points**, the lines through them, and the slide's edges and centre.
2. **Snap to whole pixels**.
3. **Snap to the grid**. Turning it on shows the grid.
4. Grid size in pixels.

## Snap to points

A point being placed or dragged snaps to other points, to the horizontal and vertical lines through them, and to the slide's edges and centre. Pink guides and a pink cross show what caught it. A point wins over the grid and pixels when it is within 6 screen pixels.

## Snap to whole pixels

Positions are rounded to whole pixels.

## Snap to the grid

The grid starts at the slide's top-left corner. The size is 10 pixels to start. Type a size in the field to change it, which also turns the grid on. Press Command+' to show or hide the grid. The grid is not drawn when its lines would be less than 6 pixels apart on screen.

## What snaps

- Pen points and their handles, and the dashed preview segment.
- Dragged points. The point you grab snaps and the rest of the selection follows.
- Dragged handles.

## Turning snapping off for one move

Hold Command while placing or dragging to ignore snapping. Shift still keeps a move to 45° steps.

## Where the settings are kept

Snapping settings are kept on this computer. They are not part of the presentation.

## See also

- [Drawing with the pen](https://svgslid.es/docs/pen.md)
- [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md)
- [Keyboard shortcuts](https://svgslid.es/docs/keyboard-shortcuts.md#editor)
- [Permissions and data](https://svgslid.es/docs/permissions-privacy.md#storage)

Source: https://svgslid.es/docs/snapping (SVG to Slides Documentation, User's Guide). Last reviewed November 20, 2026.
