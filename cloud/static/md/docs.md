# SVG to Slides Documentation

Documents the SVG to Slides Chrome extension (version 1.4.0), the Web Uploader and the Workspace Add-on.

## Getting Started
What SVG to Slides is, how to install it, and how these documents are written.

- [What SVG to Slides does](https://svgslid.es/docs/overview.md): SVG to Slides converts SVG files into native, editable Google Slides shapes. Overview of the Chrome extension, the Web Uploader and the Workspace Add-on.
- [Installing and updating the extension](https://svgslid.es/docs/install.md): Install the SVG to Slides Chrome extension, check which version you have, and see how updates arrive. Requirements and permissions by version.
- [Quick start: your first SVG](https://svgslid.es/docs/quick-start.md): Put an SVG into Google Slides as editable shapes in three steps: drag the file onto the slide, click to place it, then recolour, resize or reshape it.
- [Document conventions](https://svgslid.es/docs/conventions.md): How the SVG to Slides documentation is written: key names for Mac and Windows, typography, version boxes, note types, figures and Knowledge Base article IDs.

## User's Guide
Every tool in the Chrome extension, one topic each, with procedures.

- [Inserting SVG files](https://svgslid.es/docs/insert-svg.md): Insert SVG files into Google Slides with the SVG to Slides extension: drag and drop, click to place, several files at once, pasting SVG code, size and position.
- [The toolbar](https://svgslid.es/docs/toolbar.md): The SVG to Slides toolbar in Google Slides: where it is, how to open it, and what each button does: Layers, Edit Shape, Pen, Align, Combine, Outline.
- [Edit Shape: points and curves](https://svgslid.es/docs/edit-shape.md): Edit the points and curves of any shape in Google Slides with Edit Shape: drag points and handles, add and remove points, scale, rotate, skew, type exact sizes.
- [Rounding corners](https://svgslid.es/docs/round-corners.md): Round the corners of shapes in Google Slides by dragging a corner handle or typing a radius in pixels. Round one corner, a whole shape, or several shapes at once.
- [Drawing with the pen](https://svgslid.es/docs/pen.md): Draw custom shapes in Google Slides with the SVG to Slides pen tool: click for corners, drag for curves, close the path, and place native shapes on the slide.
- [Snapping](https://svgslid.es/docs/snapping.md): Snapping in the SVG to Slides editor: snap pen points and dragged points to other points, slide edges and centre, whole pixels, or a grid of any size in Google Slides.
- [Masking an image with a shape](https://svgslid.es/docs/mask-image.md): Crop a picture to any shape in Google Slides: put a shape over an image, select both, press Option+Shift+K. Then move or resize the picture under its mask.
- [Combining shapes](https://svgslid.es/docs/combine-shapes.md): Combine shapes in Google Slides with union, subtract, intersect and exclude. Merge shapes into one, cut one shape out of another, and undo in one step.
- [Aligning and distributing](https://svgslid.es/docs/align-distribute.md): Align and distribute objects in Google Slides instantly with SVG to Slides, including aligning a single image to the slide's left, right, top or bottom edge.
- [The Layers panel](https://svgslid.es/docs/layers.md): The Layers panel for Google Slides in SVG to Slides: list every object on a slide, select, rename, hide, restack and fold groups. Theme objects are marked.
- [Theme objects and the theme builder](https://svgslid.es/docs/theme-objects.md): Why some objects on a Google Slides slide cannot be selected: they belong to the layout or master. How SVG to Slides marks theme objects and opens the theme builder on them.
- [Outlining strokes and text](https://svgslid.es/docs/outline-stroke-text.md): Outline stroke and Outline text in Google Slides: turn lines, borders and text into shapes you can reshape, restore outlined text, set stroke position.
- [Colour, gradients, stroke and exact values](https://svgslid.es/docs/fill-stroke.md): The SVG to Slides colour panel for Google Slides: fill and stroke colour with opacity, gradients, text colour, replacing a colour across a deck, stroke weight.
- [The command palette](https://svgslid.es/docs/command-palette.md): Open the SVG to Slides command palette in Google Slides with Command+\ to search and run every command by name, with its keyboard shortcut shown.
- [Undo and redo](https://svgslid.es/docs/undo-redo.md): How undo works with SVG to Slides: one press of Command+Z undoes a combine, outline, mask, colour change or a whole Edit Shape session.
- [Editing Slides' own shapes](https://svgslid.es/docs/convert-slides-shapes.md): Edit the points of Google Slides' built-in shapes, arrows, callouts, lines, text boxes and WordArt. What each object becomes when Edit Shape converts it, and what is lost.

## Web Uploader and Add-on
The two ways in that need no extension.

- [Web Uploader](https://svgslid.es/docs/web-uploader.md): Convert SVG files to Google Slides online with the Web Uploader: upload a batch, get a Drive file with one slide per SVG. Gradients kept, 7-day links.
- [Workspace Add-on](https://svgslid.es/docs/add-on.md): Insert SVG files into Google Slides with the SVG to Slides Workspace Add-on: pick files in a dialog inside Slides, copy, and paste them as editable vector shapes.

## Reference
Keyboard shortcuts, commands, permissions, limits, glossary and index.

- [Keyboard shortcuts](https://svgslid.es/docs/keyboard-shortcuts.md): Every SVG to Slides keyboard shortcut for Google Slides on Mac and Windows: toolbar, Layers, pen, align, distribute, combine, mask, outline, stroke, and the Edit Shape editor.
- [Command reference](https://svgslid.es/docs/commands.md): Reference for every SVG to Slides command in Google Slides: what it does, what must be selected, its shortcut, and the topic that explains it.
- [SVG feature support](https://svgslid.es/docs/svg-compatibility.md): Which SVG features convert to Google Slides shapes: paths, arcs, transforms, gradients, text, strokes, clip paths, masks, CSS classes, patterns, filters.
- [Permissions and data handling](https://svgslid.es/docs/permissions-privacy.md): What the SVG to Slides Chrome extension, Web Uploader and add-on can access: Chrome permissions by version, what is stored on your computer, and what is sent over the network.
- [Limits and known issues](https://svgslid.es/docs/limits.md): Known limits of SVG to Slides in one list: files per drop, text, masks, combine and outline limits, colour and gradient limits, rotated masks, undo, 7-day links.
- [Glossary](https://svgslid.es/docs/glossary.md): Glossary of SVG to Slides terms: custom shape, polyline, corner point, smooth point, handle, mask, theme object, still copy, stroke position.
- [Index](https://svgslid.es/docs/a-z-index.md): Alphabetical index of the SVG to Slides documentation. Find a tool, command, shortcut, message or term and go to the section that covers it.

## Technical Notes
How conversion, insertion, precision and undo work underneath.

- [How conversion works](https://svgslid.es/docs/how-conversion-works.md): How SVG to Slides converts an SVG into Google Slides shapes: paint, shapes to paths, arcs to curves, stroke outlines, transforms, and the JavaScript converter.
- [How shapes reach the slide](https://svgslid.es/docs/how-shapes-reach-the-slide.md): How SVG to Slides inserts native shapes into Google Slides without the Slides API, Drive access or any Google permission.
- [Slides' Edit points and polylines](https://svgslid.es/docs/edit-points-and-polylines.md): Why Google Slides' own Edit points works on some inserted SVG shapes and not others: straight-line shapes land as polylines, and curved shapes need SVG to Slides' Edit Shape.
- [Point precision: small SVGs keep their detail](https://svgslid.es/docs/point-precision.md): Why an SVG inserted small into Google Slides can be enlarged without losing its curves: SVG to Slides 1.3.0 stores points at full precision.
- [How multi-step changes run and undo](https://svgslid.es/docs/undo-and-still-copy.md): How SVG to Slides hides the steps of a combine, outline or mask in Google Slides behind a still copy of the slide and undoes the change in one press.

## Knowledge Base
Numbered articles: one symptom, its cause, and what to do.

- [Knowledge Base](https://svgslid.es/docs/kb.md): The SVG to Slides Knowledge Base: numbered articles on known problems inserting and editing SVGs in Google Slides, each with symptoms, cause and resolution.
- [PRB: An SVG placed in Google Slides becomes a flat image](https://svgslid.es/docs/kb/svg-becomes-a-flat-image.md): Why an SVG inserted into Google Slides turns into a blurry, uneditable picture, and how to insert it as native, editable vector shapes instead.
- [FIX: A gradient arrives as one solid colour](https://svgslid.es/docs/kb/gradient-becomes-solid-colour.md): SVG gradients inserted into Google Slides with SVG to Slides versions before 1.4.0, or with the add-on, arrive as a single solid colour. Fixed in extension version 1.4.0.
- [PRB: Text in an SVG does not appear on the slide](https://svgslid.es/docs/kb/text-missing-after-insert.md): Text inside an SVG is missing after inserting it into Google Slides with the SVG to Slides extension. Cause and two ways to bring the text across.
- [PRB: A line icon inserts nothing](https://svgslid.es/docs/kb/line-icon-inserts-nothing.md): Stroke-based SVG icons in the Lucide and Feather style insert nothing into Google Slides with the SVG to Slides extension. Cause and resolution.
- [PRB: Shapes arrive black](https://svgslid.es/docs/kb/colours-arrive-black.md): SVG shapes arrive black in Google Slides when their colours come from CSS classes, hsl() values or pattern fills. Causes and how to export so colours convert.
- [INFO: The extension asks you to press COMMAND+V](https://svgslid.es/docs/kb/press-command-v-prompt.md): Why the SVG to Slides extension sometimes shows a prompt to press Command+V or Ctrl+V in Google Slides, and what to do.
- [PRB: Nothing is inserted when more than 25 files are dropped](https://svgslid.es/docs/kb/more-than-25-files.md): Dropping more than 25 SVG files onto Google Slides with the SVG to Slides extension inserts nothing. The limit, the reason, and how to convert a larger batch.
- [INFO: Slides' own Edit points is offered for some inserted shapes only](https://svgslid.es/docs/kb/edit-points-missing.md): Google Slides' Edit points command works on inserted SVG shapes with straight edges and not on curved ones. Why, and how to edit the points of any shape.
- [PRB: COMMAND+Z undoes only part of a combine or outline](https://svgslid.es/docs/kb/undo-takes-several-presses.md): After a combine, outline or mask in Google Slides with SVG to Slides, one press of Command+Z sometimes undoes only part of the change. Cause and resolution.
- [PRB: Layer names are missing on another computer](https://svgslid.es/docs/kb/layer-names-missing.md): Layer names set in the SVG to Slides Layers panel do not appear for other people or on another computer. They are stored on the computer where they were set.
- [INFO: An object in Layers is greyed and marked M](https://svgslid.es/docs/kb/object-greyed-with-m.md): Objects shown greyed with an M badge in the SVG to Slides Layers panel belong to the slide's layout or master. How to select and edit them in the theme builder.
- [PRB: Mask image with shape shows a message and does not mask](https://svgslid.es/docs/kb/cannot-mask-image.md): Messages shown by Mask image with shape in SVG to Slides for Google Slides, what each means, and how to fix the selection, rotated images and text masks.
- [PRB: Outline text reports that it could not get the font](https://svgslid.es/docs/kb/outline-text-font.md): Outline text in SVG to Slides needs the font's letter shapes. What to do when it reports that it could not get the font in Google Slides.
- [PRB: A Web Uploader link stops working after 7 days](https://svgslid.es/docs/kb/web-uploader-link-expired.md): Google Drive links from the SVG to Slides Web Uploader are deleted after 7 days. How to keep a converted file.
- [FIX: Inserted shapes landed away from the pointer in versions 1.0.0 and 1.0.1](https://svgslid.es/docs/kb/shapes-land-away-from-pointer.md): In SVG to Slides 1.0, inserted shapes could land away from the pointer when Google Slides was zoomed or its layout changed. Fixed in version 1.2.0.
- [PRB: The toolbar does not appear](https://svgslid.es/docs/kb/toolbar-does-not-appear.md): The SVG to Slides toolbar is missing in Google Slides. Check the version, reload the tab, and see the cases in which the toolbar hides itself.
- [HOWTO: Find which version of the extension is installed](https://svgslid.es/docs/kb/which-version.md): How to check the installed version of the SVG to Slides Chrome extension, and how to tell versions 1.0, 1.2, 1.3 and 1.4 apart on the slide.

## Release Notes
Version history and a technical changelog for each release.

- [Release notes and version history](https://svgslid.es/docs/release-notes.md): SVG to Slides version history: what each Chrome extension release added, package sizes, permissions by version, and a feature availability table for versions 1.0 to 1.4.
- [Version 1.4.0: technical changelog](https://svgslid.es/docs/release-notes/1-4-0.md): Technical changelog for SVG to Slides 1.4.0: colour panel, gradient builder, Replace a colour, live preview, masks that keep their shape, gradients on import.
- [Version 1.3.0: technical changelog](https://svgslid.es/docs/release-notes/1-3-0.md): Technical changelog for SVG to Slides 1.3.0: toolbar, pen, snapping, image masks, combine, one-press undo, Layers, JavaScript converter, 92% smaller.
- [Version 1.2.0: technical changelog](https://svgslid.es/docs/release-notes/1-2-0.md): Technical changelog for SVG to Slides 1.2.0: Edit Shape editor, corner rounding, editing Google Slides' own shapes, click to insert, exact placement.
- [Versions 1.0.0 and 1.0.1: technical changelog](https://svgslid.es/docs/release-notes/1-0.md): Changelog for the first releases of the SVG to Slides Chrome extension, 1.0.0 and 1.0.1: drag and drop SVG insert into Google Slides with in-browser conversion.
