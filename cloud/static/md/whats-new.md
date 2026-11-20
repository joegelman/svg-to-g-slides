# What's new in SVG to Slides

## 1.3.0 (November 2026)

- One toolbar at the left of the slide canvas (Option+Backslash): Layers, Edit Shape, Pen, command palette, Arrange, Align, Combine, Group, Outline, fill and stroke. Tooltips show shortcuts.
- Pen (Option+Shift+P): click for corners, drag for curves (Option breaks handles, Shift constrains to 45 degrees), click the first point to close, Enter or Esc to leave open, Delete removes the last point. New paths start as a 2 px dark stroke with no fill. Done adds them in one undo step.
- Snapping in the editor: points, the lines through them, slide edges and centre (pink guides), whole pixels, and a grid of any size (Cmd+' toggles). Hold Cmd to ignore.
- Exact strokes: weight field in px with Option-drag scrubbing (Shift x10), stroke inside/centre/outside, typed width, height, rotation and corner radius in Edit Shape; Edit Shape's box scales, stretches, rotates and skews.
- Outline text (Option+Cmd+T, restores on the same computer) and outline stroke (Option+Cmd+O).
- Mask image with shape (Option+Shift+K): any shape, group or outlined text over a picture. The picture keeps its exact position and size. Rotated images not yet supported.
- Combine: union, subtract, intersect, exclude, on the slide or in Edit Shape. One-press undo/redo for multi-step changes.
- Align and distribute are instant and keep images intact; a single object, image included, aligns to the slide edges.
- Layers (Option+1): nested groups fold open, Cmd-click selects inside groups, rename, hide, restack, zoom to tiny objects. Theme objects are greyed with an M; a second click opens the theme builder on them (Option+Shift+M), where one change updates every slide using that layout or master.
- Command palette (Cmd+Backslash): every command and shortcut, searchable.
- Paste SVG code: SVG markup on the clipboard pastes as native shapes.
- Small SVGs keep full detail when enlarged later.
- 92% smaller (installed 14 MB to 1.1 MB): the converter is JavaScript now. No server, and the permission for its address is gone; files never leave the browser. Permissions left: access to Google Slides pages, where the tools run, and storage.
- Fixes: layer tooltips, layer rename, false theme and too-small flags, align preview measurement.

## 1.2.0 (November 2026)

- Edit Shape: double-click a shape, then click Edit Shape. A vector editor opens on the slide at the shape's exact size and position. Drag points and curve handles, add or remove points, multi-select, undo, redo, zoom. Done updates the shape in place.
- Round corners: on shapes with corners, drag a circle inside a corner or type a pixel radius. The whole shape or several shapes round every corner together; selected points round only those corners.
- Layers stay put: shapes above the one you're editing stay visible, and Done returns each shape to its place in the stack.
- Works on Slides' own shapes, lines, text boxes and WordArt by converting them to custom shapes first. Adjustment handles, connection points, automatic 3D shading and editable WordArt text don't carry over. Text inside a shape stays editable. Cancel restores the original.
- Click to insert: drop an SVG and click where it goes. It lands as native shapes with nothing to paste. Falls back to Cmd/Ctrl+V if Slides refuses the insert.
- Straight-line SVG shapes land as Slides polylines, so Slides' own Edit points works on them.
- Placement and the editor measure the slide you have open.
- Adds the Chrome "storage" permission, used only to show the update note once. Still no access to your Google account.

## 1.0.1 (July 2026)
Removed an unused permission flagged in Chrome Web Store review.

## 1.0.0 (July 2026)
First release: drag SVG files onto a Google Slides tab and they land as native, editable shapes.

Get it: https://chromewebstore.google.com/detail/svg-to-slides/bdhhnakellmdnbgbdokiojipaebdeioi
