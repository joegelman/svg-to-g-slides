# PRB: An SVG placed in Google Slides becomes a flat image

Article ID: Q100101. Last reviewed: November 20, 2026.

Applies to: Google Slides; SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0; SVG to Slides Web Uploader; SVG to Slides Workspace Add-on for Google Slides.

Google Slides has no SVG import, so an SVG placed on a slide is flattened into a picture. To keep it as vectors, insert it with SVG to Slides: drag the file onto the slide with the Chrome extension, or convert it with the Web Uploader.

## Symptoms

An SVG placed on a slide without SVG to Slides behaves as one picture:

- It blurs or shows pixels when enlarged.
- Its parts cannot be selected or recoloured.
- Slides offers it picture options only.

## Cause

Google Slides does not keep SVG files as vectors. It flattens the drawing into a picture on the way in.

## Resolution

Insert the file as native shapes with one of the three products.

| Product | Do this |
|---|---|
| Chrome extension | Drag the .svg file onto the slide and click where it goes. See [Inserting SVG files](https://svgslid.es/docs/insert-svg.md). |
| Web Uploader | Upload the file and open the Drive link. See [Web Uploader](https://svgslid.es/docs/web-uploader.md). |
| Workspace Add-on | Choose **Insert SVGs** from the Extensions menu. See [Workspace Add-on](https://svgslid.es/docs/add-on.md). |

## Status

This is how Google Slides behaves.

## More information

There are two manual routes that need no extension: convert the SVG to EMF, open it in Google Drawings and copy the shapes across; or insert it in PowerPoint, convert it to a shape, save, and open the file in Slides. The guide [How to insert an SVG into Google Slides](https://svgslid.es/guides/insert-svg-into-google-slides) walks through both.

## See also

- [Inserting SVG files](https://svgslid.es/docs/insert-svg.md)
- [What SVG to Slides does](https://svgslid.es/docs/overview.md)
- [SVG feature support](https://svgslid.es/docs/svg-compatibility.md)
- [Guide: Does Google Slides support SVG?](https://svgslid.es/guides/does-google-slides-support-svg)
- [Guide: SVG vs PNG in Google Slides](https://svgslid.es/guides/svg-vs-png-google-slides)

Source: https://svgslid.es/docs/kb/svg-becomes-a-flat-image (SVG to Slides Documentation, Knowledge Base). Last reviewed November 20, 2026.
