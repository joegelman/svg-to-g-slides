# PRB: Layer names are missing on another computer

Article ID: Q100110. Last reviewed: November 20, 2026.

Applies to: SVG to Slides Chrome extension, version 1.3.0.

Layer names are kept in Chrome on the computer where you set them. They are not saved in the presentation, so other people and other computers show the default names.

## Symptoms

You renamed objects in the Layers panel. On another computer, or for a colleague who opens the same presentation, the rows show their default names such as "Shape", "Image" or "Group of 3".

## Cause

The extension has no way to save a name inside the presentation without changing the objects. It keeps the names in Chrome's storage on the computer you used.

## Resolution

There is none. Rename the layers on the other computer if you need the names there.

## Status

This behaviour is by design.

## More information

The same applies to snapping settings, the memory that restores outlined text, and stroke position memory. Objects hidden with the eye are hidden only in your view. See [Permissions and data](https://svgslid.es/docs/permissions-privacy.md#storage).

## See also

- [The Layers panel](https://svgslid.es/docs/layers.md#stored)
- [Permissions and data](https://svgslid.es/docs/permissions-privacy.md#storage)
- [Limits and known issues](https://svgslid.es/docs/limits.md#local)

Source: https://svgslid.es/docs/kb/layer-names-missing (SVG to Slides Documentation, Knowledge Base). Last reviewed November 20, 2026.
