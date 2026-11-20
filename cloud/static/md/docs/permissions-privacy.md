# Permissions and data handling

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0; SVG to Slides Web Uploader; SVG to Slides Workspace Add-on for Google Slides.

Availability: Version 1.3.0 is not in the Chrome Web Store yet. The store installs version 1.2.0. See [what each version has](https://svgslid.es/docs/release-notes.md#matrix).

The extension has no access to your Google account and runs only on Google Slides editor pages. Version 1.3.0 holds one Chrome permission, storage, and converts every file inside your browser.

## Chrome permissions by version

| Version | Chrome permissions | Where SVG files are converted |
|---|---|---|
| 1.3.0 | storage | In your browser, always. |
| 1.2.0 | storage, and one host permission for the svgslid.es converter | In your browser. The converter on the server was a fallback if in-browser conversion was unavailable. |
| 1.0.1 | One host permission for the svgslid.es converter | As 1.2.0. |

No version requests a Google sign-in or any Google account permission. The extension cannot read your Drive or reach your presentations through Google's API.

## What the extension reads

- The .svg files you drop on the slide.
- When you use Edit Shape or a shape command, the objects you selected on the open slide: their outlines, fill and stroke. This is read in your browser.

## What is stored on your computer

The storage permission keeps these items in Chrome on the computer you use. None of them is part of the presentation.

| Item | Used by |
|---|---|
| Whether the toolbar is open or closed, and whether Layers is open | [The toolbar](https://svgslid.es/docs/toolbar.md) |
| Snapping settings | [Snapping](https://svgslid.es/docs/snapping.md) |
| Layer names | [The Layers panel](https://svgslid.es/docs/layers.md#stored) |
| The original text of outlined text | [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md#restore) |
| The original outline of shapes whose stroke was moved inside or outside | [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md#position) |
| Whether the update note has been shown | [Installing and updating](https://svgslid.es/docs/install.md#updates) |

## Network requests in version 1.3.0

SVG files are not uploaded. The extension makes one kind of network request: **Outline text** downloads the font it needs from Google Fonts. The request names the font family, weight and style and carries nothing from the presentation. See [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md#fonts).

## Web Uploader

- The SVG files you upload are sent to the svgslid.es server, held while the request runs, and deleted when it finishes.
- The converted file is stored in Google Drive for 7 days and shared with anyone who has the link.
- If you type a Google account address, it is used once, to share the file to that account.

## Workspace Add-on

- The add-on reads the current presentation's page size, shows its dialog, and calls the svgslid.es converter. It has no Drive access.
- The files you select are sent to the server, held in memory while the request runs, and not kept.
- The result is written to your clipboard. You paste it.

> **Note:** The [Privacy Policy](https://svgslid.es/privacy) is the governing statement for all three products. This topic summarises it and adds the per-version detail.

## See also

- [Installing and updating](https://svgslid.es/docs/install.md)
- [How shapes reach the slide](https://svgslid.es/docs/how-shapes-reach-the-slide.md)
- [Version history](https://svgslid.es/docs/release-notes.md)
- [Privacy Policy](https://svgslid.es/privacy)
- [Terms](https://svgslid.es/terms)

Source: https://svgslid.es/docs/permissions-privacy (SVG to Slides Documentation, Reference). Last reviewed November 20, 2026.
