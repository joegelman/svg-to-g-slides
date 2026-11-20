# How multi-step changes run and undo

Applies to: SVG to Slides Chrome extension, version 1.3.0.

A combine, an outline, a mask or an Edit Shape session reaches Slides as several steps: remove, insert, restack. The extension shows a still copy of the slide while they run, so you see only the result, and it counts the steps so that one Command+Z undoes them all.

## The still copy

While a change runs, the extension lays a still picture of the slide over the canvas, under its own toolbar. Slides' toolbar is held still too. The copy includes the selection box, so the selection does not blink. When the last step has finished, the copy is removed and the finished slide shows.

Objects hidden in the Layers panel stay hidden in the copy.

For Align and Distribute the copy is drawn with the objects already at their destination. The slide changes once, straight to the result.

## Slides' own commands for moving

Align, Distribute and Center on page are run from Slides' own Arrange menu, which the extension keeps invisible while it uses it. Each is one Slides step. Nothing is deleted or reinserted.

This matters for images. An image that is deleted and reinserted from copied data can lose its picture, so anything that moves an image goes through Slides' own commands.

## One object to a slide edge

Slides' Align needs something to align to. To align a single object to an edge of the slide, the extension inserts a 1 pixel square with no fill and no line at the corner it needs, selects it with the object, runs Slides' Align, takes the object out of the selection and deletes the square. The steps run behind the still copy and undo as one. No extra object is left in the presentation.

## One-press undo

The extension notes the slide before and after each of its changes and counts the Slides steps the change made. If you press Command+Z right after, it walks Slides' own undo back that many steps, behind the still copy. Redo walks forward the same way.

Two rules keep this safe:

- It never presses undo more times than the change made steps.
- It applies only while the slide is as the extension left it. If you have changed the slide since, Slides' own undo is used, one step per press.

## See also

- [Undo and redo](https://svgslid.es/docs/undo-redo.md)
- [Aligning and distributing](https://svgslid.es/docs/align-distribute.md)
- [How shapes reach the slide](https://svgslid.es/docs/how-shapes-reach-the-slide.md)
- [PRB: COMMAND+Z undoes only part of a combine or outline](https://svgslid.es/docs/kb/undo-takes-several-presses.md)

Source: https://svgslid.es/docs/undo-and-still-copy (SVG to Slides Documentation, Technical Notes). Last reviewed November 20, 2026.
