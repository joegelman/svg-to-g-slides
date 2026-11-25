# Colour, gradients, stroke and exact values

Applies to: SVG to Slides Chrome extension, version 1.3.0 and later. The colour panel, gradients, text colour, Replace a colour and live preview: version 1.4.0..

The Paint section of the toolbar opens a colour panel for the fill or the stroke of the selection, with opacity, an eyedropper and a gradient builder. With text highlighted it sets the colour of those words. With nothing selected it replaces one colour across the slide or the whole presentation. The slide shows each change while you pick.

## The colour panel

| Command | Shortcut | What happens |
|---|---|---|
| **Fill colour** | Option+Shift+F | Opens the colour panel on the fill of the selection. |
| **Stroke colour** | Option+Shift+L | Opens the colour panel on the stroke of the selection. |

The bar under each button shows the current colour of the selection.

| Part of the panel | What it does |
|---|---|
| **Solid**, **Linear**, **Radial**, **None** | The kind of fill or stroke. **None** removes it. |
| The square | Sets how strong and how bright the colour is. Drag in it. |
| The rainbow bar | Sets the hue. |
| The second bar, and the **%** field | Set the opacity. |
| The eyedropper | Picks a colour from anywhere on the screen. |
| **Hex** | Takes a colour typed as 3, 6 or 8 hex digits. Eight digits include the opacity. |
| **On this slide** | The colours the open slide already uses. Click one to take it. |
| **Recent** | The colours you used last. They are kept on this computer. |
| The cross and the tick | The cross puts the slide back as it was. The tick keeps the change. Enter is the tick and Esc is the cross. |

![The colour panel open beside the toolbar on a slide. It has a title, Solid, Linear, Radial and None tabs, a colour square, hue and opacity bars, Hex and percent fields, swatches of the slide's colours, and a cross and a tick. The selected card on the slide shows the colour being picked.](https://svgslid.es/static/docs/img/colour-panel.jpg)
Figure 1. The colour panel on a fill. The card on the slide already shows the colour in the panel. *Illustration.*

The panel places itself beside the toolbar and stays inside the window.

> **Note:** In version 1.3.0 the two buttons open Slides' own fill and border colour menus. Those menus are still there in Slides' toolbar and can be used at any time.

## Gradients

**To fill a shape with a gradient**

1. Select the shape and press Option+Shift+F.
2. Click **Linear** or **Radial**. The shape takes a gradient that starts from its current colour.
3. Click a stop on the bar to select it, then set its colour in the square or the **Hex** field. Click an empty part of the bar to add a stop. Drag a stop along the bar to move it. **Remove stop** deletes the selected stop, and **Reverse** swaps the order.
4. For a linear gradient, turn the dial or type an angle. For a radial gradient, choose where it starts: the middle or a corner.
5. Click the tick.

![The colour panel in Linear mode. Under the tabs is a gradient bar with three stops, a Stop percent field, Remove stop and Reverse buttons, an angle dial with a degrees field, and buttons for 0, 45, 90 and 180 degrees. The card on the slide is filled with the gradient.](https://svgslid.es/static/docs/img/gradient-builder.jpg)
Figure 2. The gradient builder with three stops. *Illustration.*

The result is a gradient of Slides' own kind. It can be edited later in this panel or in Slides' own fill menu.

> **Note:** Slides does not keep a separate opacity for each stop. The opacity applies to the whole fill.

## Text colour

With a stretch of text highlighted in a text box, **Fill colour** opens the panel as **Text colour**. The colour applies to the highlighted words only, and the highlight stays. Text takes a solid colour, with no opacity.

## Replacing a colour

**To change one colour everywhere it is used**

1. Click an empty part of the slide so that nothing is selected.
2. Press Option+Shift+F. The panel opens as **Replace a colour**.
3. Click the colour to change in the list, or pick it from the slide with the eyedropper.
4. Set the new colour. The slide shows it in every place the old colour is used.
5. To change it on every slide, tick **All slides**. The list then shows the colours of the whole presentation.
6. Click the tick.

Fills, strokes, gradient stops and text are changed, inside groups too. A run across all slides shows a progress bar and is undone with one press of Command+Z.

![The panel titled Replace a colour, with the old colour and the new colour as two chips joined by an arrow, an All slides box, and the slide's colours listed. The card on the slide shows the new colour.](https://svgslid.es/static/docs/img/replace-colour.jpg)
Figure 3. Replace a colour. The old and the new colour are at the top of the panel. *Illustration.*

> **Note:** The colours of other slides are read from the filmstrip. In a long presentation, slides far down the filmstrip may not be listed until you scroll to them.

## Live preview

While the panel is open, the slide shows the colour, opacity, gradient or text colour in hand, and the stroke weight as you type or drag it. Nothing is changed in the presentation until you click the tick. The cross puts the slide back.

## How a colour change is applied

| Change | How it is made | What is kept |
|---|---|---|
| Solid colour, fill opacity, text colour | Through Slides' own custom colour dialog. | The object, with its animation and link. |
| None | Through Slides' own **Transparent**. | The object, with its animation and link. |
| Gradient, or a stroke with opacity | Through Slides' paint format, from a temporary copy that is removed again. | The object, with its animation and link. |
| Gradient on an object whose text has more than one style | The object is replaced. | The text styles. Animations and links on the object are not kept, and the extension says so. |

Each of these is one undo step. See [Undo and redo](https://svgslid.es/docs/undo-redo.md).

## Stroke weight

| Control | Shortcut | What it does |
|---|---|---|
| Weight field |  | Type a weight in pixels and press Enter. 0 removes the stroke. The slide shows the weight as you type. A weight that is not one of Slides' own (1, 2, 3, 4, 8, 12, 16, 24) replaces the object. |
| Thinner stroke | Option+Shift+[ | Steps down through Slides' weights: 24, 16, 12, 8, 4, 3, 2, 1 pixels. |
| Thicker stroke | Option+Shift+] | Steps up through the same weights. |
| **Stroke on / off** | Option+Shift+/ | Removes the stroke or puts it back. |
| **Stroke position** |  | Inside, centre or outside. See [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md#position). |

## Changing a number by dragging

Hold Option and drag left or right across a number field to change the value. Add Shift for steps of ten. This works on the weight field and on every field in the Edit Shape pill.

## Rotate and resize

The toolbar has no rotate or resize buttons. Outside Edit Shape, use Slides' own shortcuts. Inside Edit Shape, use [the box](https://svgslid.es/docs/edit-shape.md#smart-box).

| Command | Shortcut |
|---|---|
| Rotate 15° left or right | Option+Left Arrow, Option+Right Arrow |
| Rotate 1° left or right | Option+Shift+Left Arrow, Option+Shift+Right Arrow |
| Make larger | Command+Control+K |
| Make smaller | Command+Control+J |

## See also

- [The toolbar](https://svgslid.es/docs/toolbar.md)
- [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md)
- [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md#exact-values)
- [Keyboard shortcuts](https://svgslid.es/docs/keyboard-shortcuts.md#paint)

Source: https://svgslid.es/docs/fill-stroke (SVG to Slides Documentation, User's Guide). Last reviewed November 24, 2026.
