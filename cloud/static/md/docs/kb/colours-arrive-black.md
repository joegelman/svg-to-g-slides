# PRB: Shapes arrive black

Article ID: Q100105. Last reviewed: November 20, 2026.

Applies to: SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0; SVG to Slides Workspace Add-on for Google Slides; SVG to Slides Web Uploader.

Colours set by CSS classes in a style block, colours written as hsl(), and pattern fills are not read by the converter, so those shapes arrive black. Export with colours written on each element, or recolour the shapes in Slides.

## Symptoms

The shapes land with the right outlines but filled black.

## Cause

| In the SVG | Result |
|---|---|
| Colours set by CSS classes in a `<style>` block, as some Illustrator exports write them | Shapes kept, colours black. |
| Colours written as `hsl()` | Black. `rgb()`, named colours and short hex values are exact. |
| A pattern fill | Shape kept, filled black. |

## Resolution

- In your design tool's SVG export settings, choose the option that writes each colour on its own element instead of in a style sheet. It is often called presentation attributes.
- Or select the shapes in Slides and set their colours with the fill picker. Each path is its own shape.

## Status

This is a known limit in all three products.

## See also

- [SVG feature support](https://svgslid.es/docs/svg-compatibility.md#partly)
- [Quick start](https://svgslid.es/docs/quick-start.md#next)
- [Guide: Recolor SVGs in Google Slides](https://svgslid.es/guides/recolor-svg-in-google-slides)

Source: https://svgslid.es/docs/kb/colours-arrive-black (SVG to Slides Documentation, Knowledge Base). Last reviewed November 20, 2026.
