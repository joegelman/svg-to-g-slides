# PRB: Mask image with shape shows a message and does not mask

Article ID: Q100112. Last reviewed: November 24, 2026.

Applies to: SVG to Slides Chrome extension, version 1.3.0 and later.

Mask image with shape needs exactly one image and one shape or group selected, an image that is not rotated, and a mask that is a shape and not live text. The message under the toolbar says which condition failed.

## Symptoms

You press Option+Shift+K. The picture is not masked and a message appears under the toolbar.

## Cause and resolution

| Message | Cause | Do this |
|---|---|---|
| Select an image and a shape to mask it with | The selection has no image, or no shape. | Select the picture, then Shift-click the shape. |
| Select an image and the shape to mask it with (two objects) | More than two objects are selected. | Group the shapes first with Command+Option+G, then select the image and the group. |
| Straighten the image first: masking a rotated image isn't supported yet | The image is rotated. | Set the image's rotation back to 0, mask it, then rotate the result. |
| That shape is too thin to mask with | The shape has no width or no height, as a straight line has. | Use a shape that has both. |
| That shape has nothing to mask with | The object has no outline the extension can cut with. | Use a different shape. |
| Outline the text first (⌥⌘T), then mask with it | The mask is live text. | Press Option+Command+T to outline the text, then mask. |
| The mask has to be a shape (the other object is an image too) | Both selected objects are images. | Select one image and one shape. |
| Couldn't get the picture from Slides to mask it | Slides did not hand over the picture. | Try again. If it repeats, copy and paste the image, then mask the pasted copy. |

## Status

Masking rotated images is not supported in version 1.3.0.

## See also

- [Masking an image](https://svgslid.es/docs/mask-image.md)
- [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md#text)
- [Limits and known issues](https://svgslid.es/docs/limits.md#shape-tools)

Source: https://svgslid.es/docs/kb/cannot-mask-image (SVG to Slides Documentation, Knowledge Base). Last reviewed November 24, 2026.
