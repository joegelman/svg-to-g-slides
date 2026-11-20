# Aligning and distributing

Applies to: SVG to Slides Chrome extension, version 1.3.0.

The align and distribute commands move objects in one step, straight to the result, and leave images intact. One object on its own, an image included, aligns to the slide's edges.

## Commands

| Command | Shortcut | Needs |
|---|---|---|
| Align left | Option+A | One object or more |
| Align centres horizontally | Option+H | One object or more |
| Align right | Option+D | One object or more |
| Align top | Option+W | One object or more |
| Align middles vertically | Option+V | One object or more |
| Align bottom | Option+S | One object or more |
| Distribute horizontal spacing | Option+Shift+H | Three objects or more |
| Distribute vertical spacing | Option+Shift+V | Three objects or more |

**To align objects**

1. Select the objects.
2. Click **Align and distribute** on the toolbar and choose a command, or press its shortcut.

![The Align and distribute pop-out with eight buttons and a tooltip reading Align centres horizontally, Option H](https://svgslid.es/static/docs/img/align-flyout.jpg)
Figure 1. The pop-out, with a title, a date and a logo selected.

With two or more objects selected, the objects align to each other.

## One object aligns to the slide

With one object selected, the align commands use the slide. Left, right, top and bottom move the object to that edge of the slide. Centre and middle centre it on the page.

This works for images. The extension places a 1 pixel helper at the corner of the slide it needs, runs Slides' own Align, and removes the helper, all in one undo step. Nothing extra is left in the presentation.

![Two views of the left half of a slide. A small photograph sits in the middle on the left view and in the bottom-left corner on the right view.](https://svgslid.es/static/docs/img/align-edge-before-after.jpg)
Figure 2. A single photograph before and after Align left and Align bottom. *Illustration.*

## How the commands run

The extension runs Slides' own Align, Distribute and Center on page commands behind a still copy of the slide. You see the objects move once. Because the objects are moved by Slides and not deleted and pasted, images stay intact. See [Multi-step changes and undo](https://svgslid.es/docs/undo-and-still-copy.md).

## See also

- [The toolbar](https://svgslid.es/docs/toolbar.md#pop-outs)
- [The Layers panel](https://svgslid.es/docs/layers.md)
- [Undo and redo](https://svgslid.es/docs/undo-redo.md)
- [Multi-step changes and undo](https://svgslid.es/docs/undo-and-still-copy.md)
- [Keyboard shortcuts](https://svgslid.es/docs/keyboard-shortcuts.md#align)

Source: https://svgslid.es/docs/align-distribute (SVG to Slides Documentation, User's Guide). Last reviewed November 20, 2026.
