# Outlining strokes and text

Applies to: SVG to Slides Chrome extension, version 1.3.0.

**Outline stroke** turns lines and borders into filled shapes. **Outline text** turns text into shapes whose points you can edit. On the computer that outlined it, the same command puts the text back.

## Outline stroke

**To turn a stroke into a shape**

1. Select a shape or line that has a stroke.
2. Press Option+Command+O, or click **Outline stroke** on the toolbar.

The stroke becomes a filled shape in the stroke's colour, as wide as the stroke was. A shape that had both a fill and a stroke becomes two shapes: the fill, and the outline that was its stroke. Use it when a border has to be reshaped, combined or used as a mask like any other shape.

## Outline text

**To turn text into shapes**

1. Select the text box or the shape that holds the text.
2. Press Option+Command+T, or click **Outline text** on the toolbar.

The text becomes filled shapes in the form of its letters. A shape that held the text stays as it was, without the text. The letter shapes can then be reshaped in [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md), combined, or used as a mask.

## Restoring text

Select the outlined text and press Option+Command+T again, or choose **Restore outlined text** from the [The command palette](https://svgslid.es/docs/command-palette.md). The original text returns as live text, at the place and size the outlines have now.

> **Important:** Text can be restored only on the computer that outlined it. The extension keeps the original text on that computer. The presentation does not hold it.

## Fonts

To outline text the extension needs the font's letter shapes.

| Font | Where the letter shapes come from |
|---|---|
| A Google font | The extension downloads the font from Google Fonts. The request names the font family, weight and style. It carries nothing from your presentation. |
| A font installed on your computer | Chrome asks for permission to read your fonts. Allow it to continue. |
| A system font that cannot be downloaded | The extension uses a font with the same letter widths and shows a note naming it. |

If no source works, the extension reports that it could not get the font. See [PRB: Outline text reports that it could not get the font](https://svgslid.es/docs/kb/outline-text-font.md).

## Stroke position

**Stroke position** on the toolbar sets whether a closed shape's stroke sits inside the outline, centred on it, or outside it. Slides always centres a stroke, so the extension moves the outline by half the stroke weight to get the other two.

The extension remembers the original outline on this computer, so **Centre stroke** returns to it.

## Limits

- Gradients, pattern fills, transparency and shadows are not carried into outlined shapes.
- Images, video and charts cannot be outlined.
- Outlined-text memory and stroke-position memory are kept on the computer you used.

## See also

- [Fill, stroke and exact values](https://svgslid.es/docs/fill-stroke.md)
- [Combining shapes](https://svgslid.es/docs/combine-shapes.md)
- [Masking an image](https://svgslid.es/docs/mask-image.md)
- [PRB: Outline text reports that it could not get the font](https://svgslid.es/docs/kb/outline-text-font.md)
- [Permissions and data](https://svgslid.es/docs/permissions-privacy.md#network)

Source: https://svgslid.es/docs/outline-stroke-text (SVG to Slides Documentation, User's Guide). Last reviewed November 20, 2026.
