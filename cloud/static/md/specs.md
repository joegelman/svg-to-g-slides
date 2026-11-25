# SVG to Slides: product facts and SVG compatibility

Web uploader tested November 11, 2026. Chrome extension 1.4.0 run November 24, 2026.

## Product facts

- **Product:** SVG to Slides
- **What it does:** Converts SVG files into native, editable Google Slides shapes. Every SVG path becomes its own shape.
- **Ways to use it:** Chrome extension (drag and drop onto a slide, or paste SVG code), web uploader (returns a Google Drive file), Google Slides add-on (dialog inside Slides)
- **Price:** Free. No daily cap, no Pro tier.
- **Account:** None for the extension. The web uploader takes an optional Google account email to share the file to.
- **Google permissions:** Chrome extension: none. Add-on: reads the current presentation's page size, shows a dialog, and calls the converter.
- **Files per drop:** Up to 25 SVGs per drop in the extension. The web uploader takes a batch and makes one slide per SVG.
- **Where conversion runs:** Extension: inside your browser, with a JavaScript converter. Nothing is uploaded. Web uploader and add-on: on the svgslid.es backend.
- **Chrome permissions:** Extension 1.4.0: access to Google Slides pages, where its tools run, and storage, to remember your settings. No access to other sites.
- **Extension size:** Version 1.4.0: 434 KB to download, 1.3 MB installed.
- **File retention:** Web uploader files are deleted after 7 days. Make a copy in Drive to keep one.
- **Gradients:** Kept by the web uploader and, since version 1.4.0, by the extension. The add-on fills the shape with the gradient's first colour.
- **Colour tools:** Extension 1.4.0: a colour panel with opacity, an eyedropper and a gradient builder, text colour for highlighted words, and Replace a colour across one slide or the whole presentation.
- **Text:** Web uploader: converted to outlined shapes, not editable text. Extension and add-on: not converted.
- **Transparency:** Kept by the extension since version 1.4.0. Lost in the web uploader and the add-on.
- **Placement:** The extension fits each SVG to about a fifth of the slide, centred where you click. The add-on fits it to the current slide.
- **Editing:** Chrome extension: double-click any shape and click Edit Shape to move its points and curve handles on the slide, or round its corners by dragging or typing a radius. Works on Slides' own shapes, lines and WordArt by converting them to custom shapes first. SVG shapes made only of straight lines also support Slides' own Edit points. Version 1.3 adds a toolbar on the slide with a pen, snapping, exact strokes, outline stroke and outline text, image masks, union, subtract, intersect and exclude, align and distribute, a Layers panel and a command palette. Each tool has a topic in the documentation.
- **Also works in:** Google Drawings
- **Current versions:** Chrome extension 1.4.0 (what’s new, release notes)
- **Source code:** github.com/joegelman/svg-to-g-slides (source-available, PolyForm Strict 1.0.0)
- **Built by:** Joe Gelman. Contact: joe@glmn.co

## SVG compatibility

| Test file | What it tests | Web uploader | Chrome extension 1.4.0 |
|---|---|---|---|
| 01-single-path-icon.svg | One filled path | Works | Works |
| 02-multi-colour-logo.svg | Circle, rounded rectangle and path in three colours | Works | Works |
| 03-basic-shapes.svg | rect, circle, ellipse, polygon, polyline, line | Works: Lines and polylines become filled outline shapes | Works: Lines and polylines become filled outline shapes |
| 04-stroked-line-icon.svg | Line icon with the stroke set on the root <svg> (Lucide and Feather style) | Works: Strokes become filled outline shapes | Works: Strokes become filled outline shapes |
| 05-arcs.svg | Arc commands (A and a) | Works | Works |
| 06-nested-transforms.svg | translate, rotate and scale on nested groups | Works | Works |
| 07-even-odd-holes.svg | fill-rule="evenodd" cut-outs | Works | Works |
| 08-linear-gradient.svg | Linear gradient fill | Works: Kept as a gradient | Works: Kept as a gradient |
| 09-radial-gradient.svg | Radial gradient fill | Works: Kept as a gradient | Works: Kept as a gradient |
| 10-text.svg | <text> element | Works: Outlined into shapes, not editable text | Not converted: Not converted |
| 11-css-classes-illustrator.svg | Colours set by CSS classes in a <style> block (Illustrator style) | Partly: Shapes kept, colours become black | Works |
| 12-figma-clip-path.svg | Figma-style frame clip and white background | Works: Frame clip and background skipped | Works: Frame clip and background skipped |
| 13-clip-path-crop.svg | clip-path that crops a shape | Partly: Clip ignored; the full shape shows | Works: Cropped to the clip shape |
| 14-mask.svg | mask that cuts a hole | Partly: Mask ignored | Partly: Mask ignored |
| 15-use-symbol-sprite.svg | <use> referencing a <symbol> (icon sprites) | Not converted: Not converted | Works |
| 16-opacity.svg | fill-opacity | Partly: Shapes kept, transparency lost | Works: Transparency kept |
| 17-current-color.svg | stroke="currentColor" | Partly: Converted, but black instead of the inherited colour | Works: Strokes become filled outline shapes |
| 18-pattern-fill.svg | Pattern fill | Partly: Shape kept, filled black | Partly: Shape kept, filled black |
| 19-filter-shadow.svg | Drop-shadow filter | Partly: Shape kept, shadow dropped | Partly: Shape kept, shadow dropped |
| 20-colour-formats.svg | rgb(), named, short hex and hsl() colours | Partly: hsl() becomes black; the rest are exact | Works |

Test files: https://svgslid.es/static/specs/svg-to-slides-test-files.zip
