# Undo and redo

Applies to: SVG to Slides Chrome extension, version 1.3.0 and later.

One press of Command+Z undoes a whole change made by the extension, even when the change took several steps inside Slides. Shift+Command+Z or Command+Y redoes it in one press.

## Changes that undo in one press

- Union, Subtract, Intersect and Exclude.
- Mask image with shape.
- Outline stroke, Outline text and Restore outlined text.
- Stroke position, a typed stroke weight, Thinner stroke and Thicker stroke.
- A colour, opacity or gradient set in the colour panel, and text colour.
- Replace a colour, on one slide or across all slides.
- Moving the picture under its mask.
- Restacking in the Layers panel.
- Aligning one object to a slide edge.
- A whole Edit Shape or pen session, from opening the editor to **Done**.

Align and distribute with several objects are a single Slides step to begin with.

## How to undo and redo

| To do this | Press |
|---|---|
| Undo the extension's last change | Command+Z |
| Redo it | Shift+Command+Z or Command+Y |

Slides' own **Undo** and **Redo** buttons do the same. You can undo and redo back and forth through a chain of the extension's changes, one press each.

## When Slides' own undo takes over

The one-press undo applies while the slide is as the extension left it. If you change the slide yourself after one of the extension's changes, Slides' own undo takes over from there, and a change that took several steps then takes several presses to undo. See [PRB: COMMAND+Z undoes only part of a combine or outline](https://svgslid.es/docs/kb/undo-takes-several-presses.md).

While you are typing in a text box, Command+Z is always Slides' own.

## Inside Edit Shape

Inside the editor, Command+Z undoes one edit at a time: one moved point, one pen point. After **Done**, the whole session is one step on the slide.

## See also

- [Multi-step changes and undo](https://svgslid.es/docs/undo-and-still-copy.md)
- [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md#done)
- [PRB: COMMAND+Z undoes only part of a combine or outline](https://svgslid.es/docs/kb/undo-takes-several-presses.md)

Source: https://svgslid.es/docs/undo-redo (SVG to Slides Documentation, User's Guide). Last reviewed November 24, 2026.
