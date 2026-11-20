# Combining shapes

Applies to: SVG to Slides Chrome extension, version 1.3.0.

Union, Subtract, Intersect and Exclude make one shape from two or more. They work on the slide and inside Edit Shape, and each is one undo step.

## The four commands

| Command | Result | Shortcut |
|---|---|---|
| **Union** | One shape covering everything the selected shapes cover. | Option+Shift+U |
| **Subtract** | The bottom shape with the shapes above it cut out. | Option+Shift+S |
| **Intersect** | Only the area where the shapes overlap. | Option+Shift+I |
| **Exclude** | Everything except the area where the shapes overlap. | Option+Shift+E |

**To combine shapes**

1. Select two or more shapes.
2. Click the command in the Combine section of the toolbar, or press its shortcut.

![Two views of a slide. On the left, three overlapping circles and a rounded bar. On the right, a single cloud shape.](https://svgslid.es/static/docs/img/combine-before-after.jpg)
Figure 1. Before and after Union. Four shapes become one cloud. *Illustration.*

Press Command+Z once to split them again. See [Undo and redo](https://svgslid.es/docs/undo-redo.md).

## Inside Edit Shape

The same four buttons are on the editor's toolbar. There they act on the shapes that have selected points, or on every shape in the editor, and the result is applied when you click **Done**.

## Limits

- Gradients, pattern fills, transparency and shadows are not carried into the result.
- Images, video and charts cannot be combined.
- The shapes need a fill or an outline.
- Intersect needs shapes that overlap. If a command would leave nothing, the extension says so and changes nothing.

## See also

- [Masking an image](https://svgslid.es/docs/mask-image.md)
- [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md)
- [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md)
- [Undo and redo](https://svgslid.es/docs/undo-redo.md)
- [Limits and known issues](https://svgslid.es/docs/limits.md)

Source: https://svgslid.es/docs/combine-shapes (SVG to Slides Documentation, User's Guide). Last reviewed November 20, 2026.
