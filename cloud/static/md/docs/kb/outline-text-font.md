# PRB: Outline text reports that it could not get the font

Article ID: Q100113. Last reviewed: November 20, 2026.

Applies to: SVG to Slides Chrome extension, version 1.3.0.

Availability: Version 1.3.0 is not in the Chrome Web Store yet. The store installs version 1.2.0. See [what each version has](https://svgslid.es/docs/release-notes.md#matrix).

Outline text reads letter shapes from the font. It downloads Google fonts from Google Fonts and asks Chrome for access to fonts installed on your computer. If neither works, allow font access when Chrome asks, or set the text in a Google font and outline it again.

## Symptoms

You press Option+Command+T. The text is not outlined, and a message says the extension could not get the font and suggests allowing font access or using a Google font.

## Cause

The font is not one that Google Fonts serves, and the extension could not read it from your computer. Either Chrome's font access prompt was declined, or the font is not installed.

## Resolution

Use either method.

- Press Option+Command+T again and choose **Allow** when Chrome asks for access to your fonts.
- Change the text to a Google font, then outline it.

## More information

For some system fonts that cannot be downloaded, the extension outlines the text with a font that has the same letter widths, and a note names the font it used. The outline then matches the text's spacing but not every letter shape.

## See also

- [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md#fonts)
- [Permissions and data](https://svgslid.es/docs/permissions-privacy.md#network)

Source: https://svgslid.es/docs/kb/outline-text-font (SVG to Slides Documentation, Knowledge Base). Last reviewed November 20, 2026.
