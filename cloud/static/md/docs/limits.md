# Limits and known issues

Applies to: SVG to Slides Chrome extension, version 1.3.0; SVG to Slides Web Uploader; SVG to Slides Workspace Add-on for Google Slides.

The limits stated across this library, gathered in one place. Each one links to the topic that explains it.

## Inserting

| Limit | Detail |
|---|---|
| Files per drop | 25 in the extension. See [Inserting SVG files](https://svgslid.es/docs/insert-svg.md#several). |
| Where shapes land | On the slide you have open. The extension and the add-on cannot create slides. |
| Gradients | First colour only in the extension and the add-on. Kept by the Web Uploader. |
| SVG text | Not converted by the extension or the add-on. Outlined by the Web Uploader. |
| Clip paths, masks, patterns, filters, transparency | Not converted. See [SVG feature support](https://svgslid.es/docs/svg-compatibility.md). |

## Shape tools

| Limit | Detail |
|---|---|
| Combine and outline | Gradients, pattern fills, transparency and shadows are not carried into the result. Images, video and charts are refused. |
| Mask | Rotated images are not supported yet. Text must be outlined first. See [Masking an image](https://svgslid.es/docs/mask-image.md#limits). |
| Pen | Point by point only. No freehand mode. |
| Skew | Available in Edit Shape only. |
| Layers | Only top-level rows can be dragged to restack. |
| Edit Shape | **Done** replaces the object, so animations and links on the original are not kept. See [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md#done). |
| Converting Slides' own shapes | One-way. See [Editing Slides' own shapes](https://svgslid.es/docs/convert-slides-shapes.md). |

## Kept on one computer

Layer names, snapping settings, the memory that restores outlined text, and the memory of stroke position are kept on the computer you used. They do not travel with the presentation. Hiding an object in Layers affects only your view and ends when the page is reloaded. See [Permissions and data](https://svgslid.es/docs/permissions-privacy.md#storage).

## Undo

One-press undo applies right after one of the extension's changes. If you change the slide in between, Slides' own undo takes over. See [Undo and redo](https://svgslid.es/docs/undo-redo.md#slides-undo).

## Web Uploader and add-on

| Limit | Detail |
|---|---|
| Web Uploader links | Deleted after 7 days. Make a copy to keep the file. |
| Add-on gradients | First colour only. |
| Add-on insert | Always ends with Command+V. A web page cannot paste for you. |

## See also

- [SVG feature support](https://svgslid.es/docs/svg-compatibility.md)
- [All articles](https://svgslid.es/docs/kb.md)
- [Version 1.3.0](https://svgslid.es/docs/release-notes/1-3-0.md#limits)

Source: https://svgslid.es/docs/limits (SVG to Slides Documentation, Reference). Last reviewed November 20, 2026.
