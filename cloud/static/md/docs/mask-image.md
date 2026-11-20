# Masking an image with a shape

Applies to: SVG to Slides Chrome extension, version 1.3.0.

Availability: Version 1.3.0 is not in the Chrome Web Store yet. The store installs version 1.2.0. See [what each version has](https://svgslid.es/docs/release-notes.md#matrix).

Put a shape over a picture, select both, and press Option+Shift+K. The shape cuts out the picture under it. Any shape or group of shapes can be the mask, and the picture stays exactly where it was.

**To mask an image with a shape**

1. Place the shape over the picture, where the picture should show through.
2. Select the picture and the shape. Click one, then Shift-click the other.
3. Press Option+Shift+K, or click **Mask image with shape** in the Group section of the toolbar.

The picture is cut to the shape. It is neither stretched nor re-cropped, and the result takes the picture's place in the stack. The change is one undo step.

![Two views of a slide. On the left a yellow arch sits over a beach photograph. On the right the photograph shows only inside the arch.](https://svgslid.es/static/docs/img/mask-before-after.jpg)
Figure 1. Before and after. An arch over a photograph, then the photograph cut to the arch. *Illustration.*

## Editing the mask afterwards

Open the masked picture in [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md) and move its points. The picture holds still while the outline changes. The editor draws the shape grey while you edit, and the picture returns when you click **Done**.

## Requirements and limits

| Condition | Result |
|---|---|
| The mask is a group of shapes | Works. The group counts as one mask. |
| The mask is text | Outline the text first with Option+Command+T. See [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md). |
| The image is rotated | Not supported yet. Straighten the image first. |
| The shape is very thin | The extension reports that the shape is too thin to mask with. |
| More or fewer than two objects are selected | Select one image and one shape, or one image and one group. |

See [PRB: Mask image with shape shows a message and does not mask](https://svgslid.es/docs/kb/cannot-mask-image.md) for the messages and what each one means.

## See also

- [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md)
- [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md)
- [Combining shapes](https://svgslid.es/docs/combine-shapes.md)
- [Undo and redo](https://svgslid.es/docs/undo-redo.md)
- [PRB: Mask image with shape shows a message and does not mask](https://svgslid.es/docs/kb/cannot-mask-image.md)

Source: https://svgslid.es/docs/mask-image (SVG to Slides Documentation, User's Guide). Last reviewed November 20, 2026.
