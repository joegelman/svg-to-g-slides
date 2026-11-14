# What's new in SVG to Slides

## 1.2.0 (November 2026)

- Edit as SVG: double-click a shape, then click Edit as SVG. A vector editor opens on the slide at the shape's exact size and position. Drag points and curve handles, add or remove points, multi-select, undo, redo, zoom. Done updates the shape in place.
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
