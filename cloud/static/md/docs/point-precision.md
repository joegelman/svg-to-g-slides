# Point precision: small SVGs keep their detail

Applies to: SVG to Slides Chrome extension, version 1.3.0.

From version 1.3.0 every inserted shape carries its points at full precision, whatever size it lands at. An icon dropped at 12 pixels can be enlarged later and keeps every curve.

## The problem before 1.3.0

Slides stores an inserted shape's points as they arrive and resizes the shape by changing its transform. It does not recalculate the points. Earlier versions wrote the points at the size of the drop, so those points were all the detail the shape ever had. An icon that landed 12 pixels wide carried 12 pixels' worth of positions, and enlarging it showed the rounding.

## What 1.3.0 does

Each shape's points are written in a frame of its own, about 100,000 units across, and the shape's transform scales that frame down to the size on the slide. The points are the same whatever the size.

Slides keeps a transform's scale to four decimal places. A scale of 0.047625 comes back as 0.0476. The converter therefore rounds the scale to four places first and sizes the frame to fit that scale exactly, so nothing shifts when Slides stores the shape.

![A slide zoomed to 400 percent showing a large palm icon with smooth, clean curves](https://svgslid.es/static/docs/img/small-svg-detail.jpg)
Figure 1. A small icon after enlarging, viewed at 400% zoom. *Illustration.*

## Checks

| Check | Result |
|---|---|
| The 138 SVG files in the project's repository | Every shape lands within 0.01 pixel of where it landed before the change. |
| A 12 pixel, two-shape icon enlarged about 700 times with Slides' own resize | The shape kept its full-precision points. |

> **Note:** The add-on still writes points at the size of the insert.

## See also

- [Inserting SVG files](https://svgslid.es/docs/insert-svg.md#size)
- [How conversion works](https://svgslid.es/docs/how-conversion-works.md)
- [Version 1.3.0](https://svgslid.es/docs/release-notes/1-3-0.md#converter)

Source: https://svgslid.es/docs/point-precision (SVG to Slides Documentation, Technical Notes). Last reviewed November 20, 2026.
