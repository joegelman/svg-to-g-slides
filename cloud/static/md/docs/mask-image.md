# Masking an image with a shape

Applies to: SVG to Slides Chrome extension, version 1.3.0 and later. The shape kept on top, and moving the picture under its mask: version 1.4.0..

Put a shape over a picture, select both, and press Option+Shift+K. The shape cuts out the picture under it and stays on top as an outline. Any shape or group of shapes can be the mask. Double-click the result to move or resize the picture under its mask.

**To mask an image with a shape**

1. Place the shape over the picture, where the picture should show through.
2. Select the picture and the shape. Click one, then Shift-click the other.
3. Press Option+Shift+K, or click **Mask image with shape** in the Group section of the toolbar.

The picture is cut to the shape. It is neither stretched nor re-cropped. The change is one undo step.

![Two views of a slide. On the left a yellow arch sits over a beach photograph. On the right the photograph shows only inside the arch.](https://svgslid.es/static/docs/img/mask-before-after.jpg)
Figure 1. Before and after. An arch over a photograph, then the photograph cut to the arch. *Illustration.*

## What you get

In version 1.4.0 the result is a group of two objects:

| Object | What it is |
|---|---|
| The masked picture | The picture, cut to the shape. It takes the place in the stack of whichever of the two objects was higher. |
| The shape | The shape you used, on top of the picture, with its fill set to none. Its stroke stays, so it reads as an outline. |

A mask made of several shapes (a group, or outlined text) has each of its shapes emptied the same way.

> **Note:** In version 1.3.0 the shape is used up and only the masked picture remains.

## Moving the picture under its mask

**To move or resize the picture under its mask**

1. Double-click the mask group, or select it and press Option+Shift+K again. The whole picture shows, faded where the mask hides it, with a bar under the mask.
2. Drag the picture to move it. Drag a corner to resize it. The arrow keys nudge it.
3. To set an exact size, type a percentage in the **Picture** field. **Fit** sizes the picture to cover the mask.
4. Press Enter or click the tick to keep the change. Press Esc or click the cross to cancel.

The mask and the outline shape stay where they are. Only the picture moves. The change is one undo step.

![A photograph masked by an arch on a slide. The whole photograph shows faded around the arch, with a dashed frame, corner handles, and a dark bar under the arch holding a Picture percentage field, Fit, a cross and a tick.](https://svgslid.es/static/docs/img/mask-adjust.jpg)
Figure 2. Adjusting the picture. The part the mask hides is shown faded. *Illustration.*

## Changing the outline afterwards

Select the masked picture inside the group (click the group, then click the picture) and open it in [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md). The picture holds still while the outline changes. The editor draws the shape grey while you edit, and the picture returns when you click **Done**.

The outline shape on top is a separate object. It does not follow the edit. Reshape it the same way, or delete it.

## Colour on a mask group

| Action | Result |
|---|---|
| Stroke colour or weight on the group | Applied to the shape. The picture is left alone. |
| Fill on the group | Refused, because a fill would cover the picture. Select the shape inside the group to fill it on its own. |

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
- [Colour, gradients and stroke](https://svgslid.es/docs/fill-stroke.md)
- [Undo and redo](https://svgslid.es/docs/undo-redo.md)
- [PRB: Mask image with shape shows a message and does not mask](https://svgslid.es/docs/kb/cannot-mask-image.md)

Source: https://svgslid.es/docs/mask-image (SVG to Slides Documentation, User's Guide). Last reviewed November 24, 2026.
