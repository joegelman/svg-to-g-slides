# How shapes reach the slide

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.4.0; SVG to Slides Workspace Add-on for Google Slides.

The extension never calls a Google API. It hands shapes to Slides in the form Slides itself uses when you copy and paste a shape, so Slides treats them as its own. That is why the extension needs no Google permission.

## The route

When you copy a shape in Google Slides, Slides writes it to the clipboard in a form of its own. Paste that data back and Slides rebuilds the shape. SVG to Slides writes the same form from an SVG's paths and gives it to Slides. Slides accepts it as if it had copied the shapes itself.

No request goes to the Slides API or to Drive, and no OAuth scope is involved.

## How the hand-over is made

| Product and version | Hand-over |
|---|---|
| Extension 1.0.0 and 1.0.1 | The extension placed the data on your clipboard at your click. You pressed Command+V. |
| Extension 1.2.0 and later | The extension delivers the data to the Slides tab the way a paste does. If Slides does not accept it, the extension falls back to your clipboard and asks for Command+V. |
| Add-on | You click **Copy**, then press Command+V. A dialog in a web page cannot paste for you. |

## Reading the selection

Edit Shape and the shape commands need to know what is selected. They read it the way a copy does: Slides hands over the same shape data, inside your browser. Nothing is sent anywhere.

## Replacing a shape

An edit, a combine or an outline ends by removing the original objects and handing Slides the result in the same place, then restoring its place in the stack. Slides records that as several steps. See [Multi-step changes and undo](https://svgslid.es/docs/undo-and-still-copy.md) for how those steps are hidden and undone as one.

## What follows from this route

- Shapes land on the slide you have open. The route cannot create slides.
- The result is a native object. A masked image, for example, is the same kind of object Slides makes when you crop an image to a shape: a shape filled with the picture.
- The form Slides uses is internal to Google and can change. The extension is built so that if a scripted hand-over stops working, it falls back to copy and Command+V.

## See also

- [How conversion works](https://svgslid.es/docs/how-conversion-works.md)
- [Permissions and data](https://svgslid.es/docs/permissions-privacy.md)
- [Multi-step changes and undo](https://svgslid.es/docs/undo-and-still-copy.md)
- [INFO: The extension asks you to press COMMAND+V](https://svgslid.es/docs/kb/press-command-v-prompt.md)

Source: https://svgslid.es/docs/how-shapes-reach-the-slide (SVG to Slides Documentation, Technical Notes). Last reviewed November 24, 2026.
