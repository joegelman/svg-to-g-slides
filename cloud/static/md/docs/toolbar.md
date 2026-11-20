# The toolbar

Applies to: SVG to Slides Chrome extension, version 1.3.0.

Availability: Version 1.3.0 is not in the Chrome Web Store yet. The store installs version 1.2.0. See [what each version has](https://svgslid.es/docs/release-notes.md#matrix).

The toolbar sits at the left edge of the slide canvas. Closed, it is one round button. Click the button or press Option+\ to open it. It holds every tool the extension adds to Slides.

## The toolbar, closed

![The left edge of a Google Slides canvas with one round yellow SVG button beside the slide](https://svgslid.es/static/docs/img/toolbar-closed.jpg)
Figure 1. The toolbar when closed.
1. The svgslid.es button. Click it, or press Option+\, to open the toolbar.

The toolbar starts closed. Once you open or close it, the extension remembers the state on this computer.

## The toolbar, open

![The open toolbar: a two-column strip of icon buttons at the left of the slide, with numbered markers](https://svgslid.es/static/docs/img/toolbar-open.jpg)
Figure 2. The toolbar when open, with the logo selected. Buttons that do not apply to the selection are dimmed.
1. svgslid.es button. Closes the toolbar.
2. **Layers**. Opens the [Layers panel](https://svgslid.es/docs/layers.md).
3. **Edit Shape**. Opens the [point editor](https://svgslid.es/docs/edit-shape.md) on the selection.
4. **Pen**. [Draws a new shape](https://svgslid.es/docs/pen.md).
5. **Commands**. Opens the [command palette](https://svgslid.es/docs/command-palette.md).
6. **Arrange**. Bring forward, send backward, front, back.
7. **Align and distribute**. See [Aligning and distributing](https://svgslid.es/docs/align-distribute.md).
8. **Combine**. Union, subtract, intersect, exclude. See [Combining shapes](https://svgslid.es/docs/combine-shapes.md).
9. **Group**, **Ungroup** and **Mask image with shape**. See [Masking an image](https://svgslid.es/docs/mask-image.md).
10. **Outline stroke** and **Outline text**. See [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md).
11. **Fill colour** and **Stroke colour**.
12. Stroke weight in pixels. Type a value. 0 means no stroke.
13. **Stroke position** and **Stroke on / off**. See [Fill, stroke and exact values](https://svgslid.es/docs/fill-stroke.md).

| Section | Buttons | Shortcuts |
|---|---|---|
| Top | svgslid.es button, Layers, Edit Shape, Pen, Commands | Option+\, Option+1, double-click, Option+Shift+P, Command+\ |
| Place | Arrange, Align and distribute | See [Keyboard shortcuts](https://svgslid.es/docs/keyboard-shortcuts.md#arrange) |
| Combine | Union, Subtract, Intersect, Exclude | Option+Shift+U, Option+Shift+S, Option+Shift+I, Option+Shift+E |
| Group | Group, Ungroup, Mask image with shape | Command+Option+G, Shift+Command+Option+G, Option+Shift+K |
| Outline | Outline stroke, Outline text | Option+Command+O, Option+Command+T |
| Paint | Fill colour, Stroke colour, weight, Stroke position, Stroke on / off | Option+Shift+F, Option+Shift+L, Option+Shift+[ and Option+Shift+], Option+Shift+/ |

## Tooltips

Point at any button, pop-out item or field to see its name and shortcut.

![The pointer over the Pen button with a dark tooltip reading Pen: draw a shape anywhere, Option Shift P](https://svgslid.es/static/docs/img/toolbar-tooltip.jpg)
Figure 3. A tooltip. Every control has one.

## Pop-out menus

Buttons with a small mark in the corner open a row of commands beside the toolbar. Arrange, Align and distribute, and Stroke position work this way.

![The Align and distribute button open, showing eight align and distribute buttons in a row, with a tooltip on Align centres horizontally](https://svgslid.es/static/docs/img/align-flyout.jpg)
Figure 4. The Align and distribute pop-out, with three objects selected.

## Dimmed buttons

A button is dimmed when its command does not apply to what is selected. Outline text, for example, is dimmed unless the selection has text. Clicking a dimmed command shows a short message that says what to select.

## Short screens

When the canvas is too short for the whole toolbar, the Combine buttons fold into one pop-out button, then the Outline buttons do the same.

## While a command runs

While the extension carries out a command the toolbar ignores clicks and the pointer shows the progress cursor. This lasts a moment.

## When the toolbar is hidden

The toolbar is hidden while Edit Shape is open, because the editor has its own toolbar in the same place. It is also hidden in full-screen view.

## See also

- [Keyboard shortcuts](https://svgslid.es/docs/keyboard-shortcuts.md)
- [Command reference](https://svgslid.es/docs/commands.md)
- [The command palette](https://svgslid.es/docs/command-palette.md)
- [The Layers panel](https://svgslid.es/docs/layers.md)
- [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md)

Source: https://svgslid.es/docs/toolbar (SVG to Slides Documentation, User's Guide). Last reviewed November 20, 2026.
