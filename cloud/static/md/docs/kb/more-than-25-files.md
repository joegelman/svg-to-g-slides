# PRB: Nothing is inserted when more than 25 files are dropped

Article ID: Q100107. Last reviewed: November 24, 2026.

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.4.0.

The extension inserts up to 25 SVG files per drop. A larger drop inserts nothing and shows a message. Drop the files in batches of 25, or use the Web Uploader, which makes one slide per SVG.

## Symptoms

You drag more than 25 .svg files onto a slide. A message says there are too many files at once, and nothing lands.

## Cause

Files from one drop are laid out in a grid on the current slide. Past 25 files the grid stops being useful, so the extension refuses the drop.

## Resolution

- Drop the files in batches of 25 or fewer.
- Or convert the whole set with the [Web Uploader](https://svgslid.es/docs/web-uploader.md). It makes a file with one slide per SVG.

## Status

This behaviour is by design.

## See also

- [Inserting SVG files](https://svgslid.es/docs/insert-svg.md#several)
- [Web Uploader](https://svgslid.es/docs/web-uploader.md)
- [Limits and known issues](https://svgslid.es/docs/limits.md#inserting)

Source: https://svgslid.es/docs/kb/more-than-25-files (SVG to Slides Documentation, Knowledge Base). Last reviewed November 24, 2026.
