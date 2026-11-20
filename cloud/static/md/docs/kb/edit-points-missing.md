# INFO: Slides' own Edit points is offered for some inserted shapes only

Article ID: Q100108. Last reviewed: November 20, 2026.

Applies to: SVG to Slides Chrome extension, versions 1.2.0 and 1.3.0.

Slides' own Edit points works only on polylines. Inserted shapes with one outline and straight segments land as polylines. Curved shapes and shapes with holes do not, because Slides' point editor would damage them. Use Edit Shape for those.

## Summary

After inserting an SVG, some shapes offer Slides' **Edit points** and enter point editing on a double-click. Others give a text cursor on a double-click and have no **Edit points**.

## More information

Slides' point editor works with straight segments only. A shape is inserted as a polyline, which that editor accepts, only if it has a single outline, only straight segments, and no more than 150 points.

Every other shape is inserted as a custom shape. To edit its points, double-click it and click **Edit Shape**. See [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md).

The tests behind this rule are described in [Edit points and polylines](https://svgslid.es/docs/edit-points-and-polylines.md).

## See also

- [Edit points and polylines](https://svgslid.es/docs/edit-points-and-polylines.md)
- [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md)

Source: https://svgslid.es/docs/kb/edit-points-missing (SVG to Slides Documentation, Knowledge Base). Last reviewed November 20, 2026.
