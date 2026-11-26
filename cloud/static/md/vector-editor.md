# A vector editor inside Google Slides

SVG to Slides adds the drawing tools Slides leaves out: point editing, a pen, shape combining, image masks, outline text, layers, and a colour panel with gradients. They work on any shape in the deck, not only SVGs you bring in.

_Free forever. Every feature, no daily cap, no account, no Pro tier._ Install: https://chromewebstore.google.com/detail/svg-to-slides/bdhhnakellmdnbgbdokiojipaebdeioi

## Edit points and curves
Double-click any shape and click Edit Shape. A vector editor opens on the slide at the shape's exact size and position. Drag points and curve handles, add or remove points, scale, rotate or skew with the box, or type exact sizes. Click Done and the shape updates in place. Slides' own Edit points works only on polylines, which have straight segments only.

- Add or remove a point: P, then click
- Smooth or corner point: Double-click the point
- Apply: Enter or Done
- Reference: https://svgslid.es/docs/edit-shape.md
- Guide: https://svgslid.es/guides/edit-points-google-slides.md

## Round any corner
In Edit Shape, shapes with corners show a small circle inside each corner. Drag it toward the middle, or type a radius in pixels. Select several shapes to give them all the same radius.

- Radius in 10 px steps: Hold Shift+ while dragging
- Reference: https://svgslid.es/docs/round-corners.md

## Draw with the pen
The pen draws new shapes point by point, anywhere on the slide. Click for a corner, drag for a curve, and click the first point to close the shape. With snapping on, points and handles land on a grid.

- Pen: Option+Shift+P
- Keep to 45°: Hold Shift+
- Leave the path open: Enter or Esc
- Reference: https://svgslid.es/docs/pen.md
- Guide: https://svgslid.es/guides/pen-tool-google-slides.md

## Union, subtract, intersect, exclude
Select two or more shapes and make one shape from them. Union covers everything, Subtract cuts the shapes above out of the bottom one, Intersect keeps the overlap, Exclude keeps everything but the overlap. Each is one undo step.

- Union: Option+Shift+U
- Subtract: Option+Shift+S
- Intersect: Option+Shift+I
- Exclude: Option+Shift+E
- Reference: https://svgslid.es/docs/combine-shapes.md
- Guide: https://svgslid.es/guides/combine-shapes-google-slides.md

## Mask an image with any shape
Put a shape over a picture, select both, and mask. Any shape or group of shapes can be the mask, not just the crop shapes in Slides' menu. The shape stays on top as an outline. Double-click the result to move or resize the picture under it.

- Mask image with shape: Option+Shift+K
- Adjust the picture: Double-click the group
- Reference: https://svgslid.es/docs/mask-image.md

## Outline strokes and text
Outline stroke turns lines and borders into filled shapes. Outline text turns text into shapes whose points you can edit, or use as a mask. On the computer that outlined it, the same command puts the text back.

- Outline text: Option+Command+T
- Reference: https://svgslid.es/docs/outline-stroke-text.md

## Colour, gradients and Replace a colour
The paint bucket opens a colour panel with opacity, an eyedropper and a gradient builder, for the fill or the stroke. With words highlighted it sets their colour. With nothing selected it becomes Replace a colour: pick a colour in use and choose what it becomes, on one slide or every slide. The slide shows each change while you pick.

- Fill colour, or Replace a colour: Option+Shift+F
- Stroke colour: Option+Shift+L
- Reference: https://svgslid.es/docs/fill-stroke.md
- Guide: https://svgslid.es/guides/replace-color-google-slides.md

## Layers
List every object on the slide, front first. Click a row to select it, drag rows to restack, double-click to rename, and hide an object while you work. Nested groups open in the list.

- Layers: Option+1
- Reference: https://svgslid.es/docs/layers.md

## Command palette
A searchable list of every command with its shortcut. Type a few letters, move with the arrow keys and press Enter.

- Command palette: Command+\
- Open the toolbar: Option+\
- Reference: https://svgslid.es/docs/command-palette.md

## Where it runs
Chrome extension 1.4.0, on Google Slides pages only. Chrome permissions: access to Google Slides pages, where its tools run, and storage, to remember your settings. No access to other sites. Files are converted inside the browser; nothing is uploaded. The web uploader and the add-on insert SVGs but have no editing tools.
