"""Docs content: Release Notes. Version history and a technical changelog per release.

Sources: tools/site_pages.py whats_new_page (public release posts), the project's
release notes for 1.2.0 and 1.3.0, and the extension source. Package sizes are the
measured zips and unpacked folders.
"""

import site_docs as D

A13 = "SVG to Slides Chrome extension, version 1.3.0"
A14 = "SVG to Slides Chrome extension, version 1.4.0"

# Wording that depends on whether the Chrome Web Store has published the current version
# (site_docs.STORE). The %...% tokens in the topics below are filled in at the end of this module.
_ADDS = ("adds a colour panel with opacity and an eyedropper, a gradient builder, Replace a colour across a slide or "
         "the whole presentation, live preview, and image masks that keep their shape. SVG gradients and transparency "
         "now come across on import. Each release has a technical changelog below.")
TOKENS = {
    "%SUMMARY%": (f"Version 1.4.0 is the newest version of the Chrome extension. It is not in the Chrome Web Store yet, "
                  f"and the store installs version {D.STORE}. Version 1.4.0 {_ADDS}") if D.PENDING
                 else f"Version 1.4.0 is the current release of the Chrome extension. It {_ADDS}",
    "%DATE140%": "Not in the Chrome Web Store yet" if D.PENDING else "November 24, 2026",
    "%DATE130%": "November 2026",
}

LEGEND = """
| Mark | Meaning |
|---|---|
| NEW | Added in this version. |
| CHG | Behaviour that changed. |
| FIX | A fault corrected. |
| REM | Removed. |
"""

TOPICS = [
    dict(
        slug="release-notes", book="release", kind="Version history", nav="Version history",
        title="Release notes and version history",
        desc="SVG to Slides version history: what each Chrome extension release added, package sizes, permissions by version, and a feature availability table for versions 1.0 to 1.4.",
        applies=["SVG to Slides Chrome extension, versions 1.0.0 through 1.4.0", "SVG to Slides Web Uploader", "SVG to Slides Workspace Add-on"],
        summary="%SUMMARY%",
        keys=["release notes", "version history", "changelog", "what's new", "versions#versions", "feature availability#matrix", "package size#versions"],
        howto=False,
        version="1.4.0",
        body="""
## Chrome extension versions {#versions}

| Version | Date | What it added | Download | Installed | Chrome permissions |
|---|---|---|---|---|---|
| [[release-notes/1-4-0|1.4.0]] | %DATE140% | Colour panel, gradient builder, text colour, Replace a colour, live preview, masks that keep their shape, the picture adjustable under its mask, gradients and transparency on import | 434 KB | 1.3 MB | storage |
| 1.3.1 | November 2026 | Outline icon sets convert (strokes set on the root element), round caps and joins, colours from CSS classes, currentColor, hsl(), clip paths, use and symbol | 399 KB | 1.1 MB | storage |
| [[release-notes/1-3-0|1.3.0]] | %DATE130% | Toolbar, pen, snapping, image masks, combine, one-press undo, instant align, Layers, outline stroke and text, command palette, full-precision points, JavaScript converter | 392 KB | 1.1 MB | storage |
| [[release-notes/1-2-0|1.2.0]] | November 2026 | Edit Shape, round corners, editing Slides' own shapes, click to insert, exact placement | 5.8 MB | 14 MB | storage, one host permission |
| [[release-notes/1-0|1.0.1]] | July 2026 | Removed an unused permission | | | One host permission |
| [[release-notes/1-0|1.0.0]] | July 2026 | First release: drag SVG files onto a slide | | | |

Version 1.1.0 was an internal build and was not released. Its changes shipped in 1.2.0.

!!! Note: A new version reaches installed copies through the Chrome Web Store's automatic update, once the store has published it. To see which version you have, see [[install#check-version]].

## Feature availability by version {#matrix}

| Feature | 1.0 | 1.2 | 1.3 | 1.4 |
|---|---|---|---|---|
| Insert SVG files by drag and drop | Yes | Yes | Yes | Yes |
| Up to 25 files per drop | Yes | Yes | Yes | Yes |
| Converts in the browser | Yes | Yes | Yes | Yes |
| Click places the shapes, with no <<Command+V>> | | Yes | Yes | Yes |
| Placement measured from the slide | | Yes | Yes | Yes |
| [[edit-shape|Edit Shape]] | | Yes | Yes | Yes |
| [[round-corners|Round corners]] | | Yes | Yes | Yes |
| [[convert-slides-shapes|Edit Slides' own shapes]] | | Yes | Yes | Yes |
| Straight-edged shapes work with Slides' Edit points | | Yes | Yes | Yes |
| [[toolbar|Toolbar]] and [[command-palette|command palette]] | | | Yes | Yes |
| [[pen|Pen]] and [[snapping|snapping]] | | | Yes | Yes |
| [[mask-image|Mask image with shape]] | | | Yes | Yes |
| [[combine-shapes|Union, subtract, intersect, exclude]] | | | Yes | Yes |
| [[align-distribute|Align and distribute commands]] | | | Yes | Yes |
| [[layers|Layers panel]] and theme builder shortcut | | | Yes | Yes |
| [[outline-stroke-text|Outline stroke, outline text, stroke position]] | | | Yes | Yes |
| [[undo-redo|One-press undo]] | | | Yes | Yes |
| Paste SVG code | | | Yes | Yes |
| [[point-precision|Full-precision points]] | | | Yes | Yes |
| Server fallback for conversion | Yes | Yes | Removed | Removed |
| Outline icon sets, CSS class colours, clip paths, use and symbol | | | 1.3.1 | Yes |
| [[fill-stroke#panel|Colour panel with opacity and eyedropper]] | | | | Yes |
| [[fill-stroke#gradients|Gradient builder]] | | | | Yes |
| [[fill-stroke#text|Text colour for highlighted words]] | | | | Yes |
| [[fill-stroke#replace|Replace a colour, one slide or all]] | | | | Yes |
| [[fill-stroke#preview|Live preview]] | | | | Yes |
| [[mask-image#result|Mask keeps the shape as an outline]] | | | | Yes |
| [[mask-image#adjust|Move the picture under its mask]] | | | | Yes |
| [[insert-svg#converts|Gradients and transparency on import]] | | | | Yes |

## Web Uploader and Workspace Add-on {#other}

| Product | Available since |
|---|---|
| [[web-uploader|Web Uploader]] | June 2026 |
| [[add-on|Workspace Add-on]] | July 2026, on the Google Workspace Marketplace |

Both are updated in place and carry no version number in these notes.

## How to read a changelog {#legend}
""" + LEGEND + """
## Release posts {#posts}

The illustrated release posts, with animations of each feature, are on the [What's new](/whats-new) page.
""",
        see=["release-notes/1-4-0", "release-notes/1-3-0", "release-notes/1-2-0", "release-notes/1-0", "install#updates", ("What's new: release posts", "/whats-new")],
    ),
    dict(
        slug="release-notes/1-4-0", book="release", kind="Technical changelog", nav="Version 1.4.0",
        title="Version 1.4.0: technical changelog",
        desc="Technical changelog for SVG to Slides 1.4.0: colour panel, gradient builder, Replace a colour, live preview, masks that keep their shape, gradients on import.",
        applies=[A14],
        summary="Version 1.4.0 gives the toolbar its own colour panel, with opacity, an eyedropper and a gradient builder. It replaces a colour across a slide or the whole presentation, shows changes on the slide while you pick, keeps the shape when it masks an image, and brings SVG gradients and transparency across on import. It asks for no new permission.",
        keys=["version 1.4.0", "1.4.0", "colour panel#colour", "Replace a colour#colour", "gradients on import#import"],
        howto=False,
        version="1.4.0",
        body="""
| Item | Detail |
|---|---|
| Version | 1.4.0 |
| Date | %DATE140% |
| Download size | 434 KB (1.3.1: 399 KB) |
| Installed size | 1.3 MB (1.3.1: 1.1 MB) |
| Chrome permissions | storage (unchanged) |

## Colour {#colour}

| Mark | Change | Topic |
|---|---|---|
| NEW | Colour panel for fill and stroke: colour square, hue and opacity bars, eyedropper, hex field, the slide's colours and recent colours. | [[fill-stroke#panel]] |
| CHG | **Fill colour** and **Stroke colour** open the colour panel. In 1.3.0 they opened Slides' own menus. | [[fill-stroke#panel]] |
| NEW | Gradient builder: linear and radial, stops on a bar, an angle dial, a start point for radial gradients. | [[fill-stroke#gradients]] |
| NEW | Text colour. With text highlighted, the panel colours those words only. | [[fill-stroke#text]] |
| NEW | Replace a colour. With nothing selected, one colour is changed wherever it is used: fills, strokes, gradient stops and text, inside groups too. **All slides** runs it across the presentation. | [[fill-stroke#replace]] |
| NEW | Live preview. The slide shows the colour, opacity, gradient, text colour or stroke weight while the panel or the field is in use. | [[fill-stroke#preview]] |
| CHG | **Fill colour** is available with nothing selected. | [[fill-stroke#replace]] |
| NEW | A colour change is made on the object itself, through Slides' own colour dialog or paint format, so the object keeps its animation and link. | [[fill-stroke#applied]] |
| NEW | A change that takes longer than about a fifth of a second shows a labelled progress bar. | [[undo-redo]] |

## Image masks {#masks}

| Mark | Change | Topic |
|---|---|---|
| CHG | **Mask image with shape** keeps the shape. It stays on top of the masked picture with no fill, and the two are grouped. | [[mask-image#result]] |
| NEW | The picture can be moved and resized under its mask: double-click the group, or press <<Option+Shift+K>> again. | [[mask-image#adjust]] |
| NEW | A stroke applied to a mask group goes to the shape only. A fill on the whole group is refused. | [[mask-image#colour]] |

## Inserting SVG files {#import}

| Mark | Change | Topic |
|---|---|---|
| NEW | Linear and radial gradients arrive as Slides gradients. The stops are re-timed onto the line Slides draws. | [[insert-svg#converts]] |
| NEW | `opacity`, `fill-opacity` and `stroke-opacity` are kept. | [[insert-svg#converts]] |
| FIX | A gradient no longer arrives as its first colour. | [[kb/gradient-becomes-solid-colour]] |

## Edit Shape and text {#editor}

| Mark | Change | Topic |
|---|---|---|
| FIX | Edit Shape draws a shape's gradient and opacity while you edit. In 1.3.0 a gradient shape was drawn flat. | [[edit-shape]] |
| CHG | The tick and the cross on the Edit Shape pill keep or cancel everything changed since the pill came up. Neither leaves the editor. | [[edit-shape#exact-values]] |
| FIX | **Outline text** on text set bold with the B button, in a font with no bold face, is drawn as Chrome draws it. | [[outline-stroke-text]] |
| FIX | Text boxes that come from a layout can be grouped with shapes. They become plain text boxes first. | [[layers]] |
| CHG | A name given in Layers follows a copy of the object to another slide or presentation on the same computer. | [[layers#stored]] |

## Undo {#undo}

| Mark | Change | Topic |
|---|---|---|
| NEW | Colour changes, Replace a colour across all slides, and moving the picture under a mask each undo with one press. | [[undo-redo#which]] |
| FIX | One-press undo no longer stops short after a change to opacity, text colour, a gradient, or a picture's position under its mask. | [[undo-redo]] |

## Limits in this version {#limits}

| Limit | Detail |
|---|---|
| Gradient on an object whose text has several styles | The object is replaced, so its animation and link are not kept. |
| Stroke weights that are not Slides' own | The object is replaced. |
| Fill on a whole mask group | Refused. Fill the shape inside the group. |
| Rotated images | Still cannot be masked. |
| Deck colours | Read from the filmstrip. Slides far down a long filmstrip may not be listed until scrolled to. |
| A narrow window | If Slides folds its fill or border button under the More menu, the colour panel cannot apply a colour and says so. Use Slides' own menu, or widen the window. |
| Workspace Add-on and Web Uploader | Unchanged by this release. |

## Release post {#post}

The illustrated post, with a clip of each feature, is on the [What's new](/whats-new#v14) page.
""",
        see=["release-notes", "fill-stroke", "mask-image", "insert-svg", "release-notes/1-3-0"],
    ),
    dict(
        slug="release-notes/1-3-0", book="release", kind="Technical changelog", nav="Version 1.3.0",
        title="Version 1.3.0: technical changelog",
        desc="Technical changelog for SVG to Slides 1.3.0: toolbar, pen, snapping, image masks, combine, one-press undo, Layers, JavaScript converter, 92% smaller.",
        applies=[A13],
        summary="Version 1.3.0 puts a pen, image masks, shape combining, instant align and a Layers panel on the slide, with one toolbar for all of it. The converter now runs as JavaScript inside the extension, which makes the package 92% smaller and removes the server fallback and its permission.",
        keys=["version 1.3.0", "1.3.0", "92% smaller#packaging", "Paper.js#packaging", "fontkit#packaging"],
        howto=False,
        version="1.3.0",
        body="""
| Item | Detail |
|---|---|
| Version | 1.3.0 |
| Date | %DATE130% |
| Download size | 392 KB (1.2.0: 5.8 MB) |
| Installed size | 1.1 MB (1.2.0: 14 MB) |
| Chrome permissions | storage |

## Toolbar and commands {#toolbar}

| Mark | Change | Topic |
|---|---|---|
| NEW | One toolbar at the left edge of the slide canvas, two columns wide. Closed, it is a single round button. <<Option+\\>> opens and closes it. The state is remembered. | [[toolbar]] |
| NEW | Command palette, <<Command+\\>>: every command by name, with its shortcut. | [[command-palette]] |
| NEW | Tooltips with shortcuts on every button, pop-out item and field. | [[toolbar#tooltips]] |
| NEW | Stroke weight field in pixels, stroke on and off, thinner and thicker stroke. | [[fill-stroke]] |
| NEW | On a short canvas the Combine and Outline groups fold into one pop-out button each. | [[toolbar#short]] |

## Drawing and editing {#drawing}

| Mark | Change | Topic |
|---|---|---|
| NEW | Pen. Draws new shapes anywhere on the slide, point by point. <<Option+Shift+P>>. | [[pen]] |
| NEW | Snapping to points, their lines, the slide's edges and centre, whole pixels, or a grid of any size. | [[snapping]] |
| NEW | A box around the selection in Edit Shape scales, stretches, skews and rotates. | [[edit-shape#smart-box]] |
| NEW | Exact values: width, height, rotation and corner radius can be typed. <<Option>>-drag changes any number. | [[edit-shape#exact-values]] |
| CHG | The Edit Shape toolbar has two columns and repeats the main toolbar's command groups. Commands used inside the editor are applied on **Done**. | [[edit-shape#scope]] |
| CHG | A whole Edit Shape or pen session is one undo step on the slide. | [[undo-redo]] |
| NEW | SVG markup copied as text can be pasted onto the slide and placed with a click. | [[insert-svg#paste-code]] |

## Shape operations {#operations}

| Mark | Change | Topic |
|---|---|---|
| NEW | Union, Subtract, Intersect, Exclude, on the slide and inside Edit Shape. | [[combine-shapes]] |
| NEW | Mask image with shape, <<Option+Shift+K>>. Any shape or group cuts the picture under it, and the picture keeps its position and size. The result is the same kind of object Slides makes when an image is cropped to a shape. | [[mask-image]] |
| NEW | Outline stroke and Outline text. Outlined text can be restored on the computer that outlined it. | [[outline-stroke-text]] |
| NEW | Stroke position: inside, centre, outside. | [[outline-stroke-text#position]] |
| NEW | Align and distribute commands with shortcuts. They run Slides' own Align, Distribute and Center on page behind a still copy of the slide, so objects move once and images stay intact. | [[align-distribute]] |
| NEW | One object, an image included, aligns to the slide's edges. A 1 pixel helper is placed, used and removed in one undo step. | [[align-distribute#single]] |
| NEW | One-press undo and redo for the extension's multi-step changes. | [[undo-redo]] |

## Layers and selection {#layers}

| Mark | Change | Topic |
|---|---|---|
| NEW | Layers panel, <<Option+1>>: select, add to the selection, restack, rename, hide, fold groups. | [[layers]] |
| NEW | Theme objects are greyed and marked M. A second click opens the theme builder on the layout or master that holds the object. <<Option+Shift+M>> opens the theme builder and returns. | [[theme-objects]] |
| NEW | <<Command>>-click selects the innermost object inside groups. | [[layers#direct-select]] |
| NEW | Objects under 6 pixels on screen get a zoom-in on the second click. | [[layers#small]] |

## Converter {#converter}

| Mark | Change | Topic |
|---|---|---|
| CHG | The converter is JavaScript inside the extension. It replaces the Python converter that ran in WebAssembly. Output was compared on all 138 SVG files in the project's repository and was identical, byte for byte. | [[how-conversion-works#javascript]] |
| CHG | Every shape's points are written at full precision and scaled by the shape's transform, so a graphic inserted small keeps its detail when enlarged. | [[point-precision]] |

## Packaging and permissions {#packaging}

| Mark | Change |
|---|---|
| CHG | The download is 392 KB, down from 5.8 MB. Installed, the extension is 1.1 MB, down from 14 MB: 92% smaller. |
| REM | The bundled Python runtime and the converter's Python files. |
| REM | The converter fallback on the svgslid.es server, and the host permission that reached it. SVG files are never uploaded. |
| REM | The content security policy entry that allowed WebAssembly to run. |
| CHG | Chrome permissions: storage only. Storage now also holds the toolbar state, snapping settings, layer names, and the memory that restores outlined text and stroke position. See [[permissions-privacy#storage]]. |
| NEW | Bundled open-source libraries, all under the MIT licence: Paper.js 0.12.18 and paperjs-offset 2.2.2 for shape geometry, fontkit 3.0.0 for reading font outlines. |

## Fixes {#fixes}

| Mark | Change |
|---|---|
| FIX | Layer tooltips no longer read "undefined". |
| FIX | Renaming a layer always ends with <<Enter>>, <<Esc>> or a click elsewhere. |
| FIX | Objects are no longer flagged as theme objects, or as too small to see, by mistake. |

## Known limits {#limits}

- Gradients, pattern fills, transparency and shadows are not carried through Combine and Outline. Images, video and charts cannot be combined or outlined.
- Rotated images cannot be masked yet. Text must be outlined before it is used as a mask.
- Layer names, the memory that restores outlined text, and stroke position memory are kept on the computer you used.
- Skew is available in Edit Shape only. Only top-level layers can be dragged to restack.
- One-press undo is lost if you change the slide after the extension's change.
- The pen has no freehand mode.

The full list is in [[limits]].

## Upgrading from 1.2.0 {#upgrading}

Chrome installs 1.3.0 on its own. Version 1.3.0 holds fewer permissions than 1.2.0, so Chrome does not ask you to approve anything. The first time you open Slides after the update, a note names the changes. The toolbar starts closed: look for the round button at the left edge of the slide canvas.
""",
        see=["release-notes", "release-notes/1-2-0", "toolbar", "limits", ("What's new: release post", "/whats-new")],
    ),
    dict(
        slug="release-notes/1-2-0", book="release", kind="Technical changelog", nav="Version 1.2.0",
        title="Version 1.2.0: technical changelog",
        desc="Technical changelog for SVG to Slides 1.2.0: Edit Shape editor, corner rounding, editing Google Slides' own shapes, click to insert, exact placement.",
        applies=["SVG to Slides Chrome extension, version 1.2.0"],
        summary="Version 1.2.0 adds Edit Shape, a vector editor that opens on the slide, and corner rounding. It works on Slides' own shapes as well as inserted ones. Inserting no longer needs a paste: the click places the shapes.",
        keys=["version 1.2.0", "1.2.0", "version 1.1.0#notes"],
        howto=False,
        version="1.2.0",
        body="""
| Item | Detail |
|---|---|
| Version | 1.2.0 |
| Date | November 2026 |
| Download size | 5.8 MB |
| Installed size | 14 MB |
| Chrome permissions | storage, and one host permission for the converter fallback |

## Editor {#editor}

| Mark | Change | Topic |
|---|---|---|
| NEW | Edit Shape. Double-click a shape and click **Edit Shape**. An editor opens on the slide at the shape's exact size and position: drag points and curve handles, add and remove points, select several, undo, redo, zoom and pan. **Done** updates the shape in place. | [[edit-shape]] |
| NEW | Round corners. Drag a circle inside a corner or type a radius in pixels. A whole shape or several shapes round together. | [[round-corners]] |
| NEW | Edit Shape opens on Slides' own shapes, lines, text boxes and WordArt by converting them to custom shapes first. The conversion reads the outlines Slides itself draws. **Cancel** restores the original. | [[convert-slides-shapes]] |
| NEW | Shapes stacked above the one being edited stay visible, and **Done** returns each edited shape to its place in the stack. | [[edit-shape#done]] |

## Inserting {#insert}

| Mark | Change | Topic |
|---|---|---|
| CHG | Click to insert. Drop an SVG and click where it goes. The shapes land with nothing to paste. If Slides does not accept them, the extension asks for <<Command+V>>. | [[insert-svg]] |
| CHG | Placement is measured from the slide. Earlier versions estimated it from the window size. | [[kb/shapes-land-away-from-pointer]] |

## Converter {#converter}

| Mark | Change | Topic |
|---|---|---|
| CHG | Shapes with one outline, straight segments only and no more than 150 points land as Slides polylines, so Slides' own Edit points works on them. | [[edit-points-and-polylines]] |
| FIX | For those shapes, a closing segment that repeated the start point is dropped. It left two points in one place, and dragging one tore the corner. | |

## Fixes {#fixes}

| Mark | Change |
|---|---|
| FIX | Placement and the editor measure the slide you have open. Before, visiting another slide first could throw both off. |
| FIX | The editor measures the visible canvas, so editing while Slides is zoomed in works. |
| FIX | Shapes picked from inside a group are placed correctly when edited. |

## Permissions and updates {#permissions}

| Mark | Change |
|---|---|
| NEW | The storage permission, used to remember that the update note has been shown. |
| NEW | A one-time note in the corner of Slides after the update, naming the changes. New installations do not see it. |

## Notes {#notes}

Version 1.1.0 was an internal build of the editor and was not released. Everything in it shipped in 1.2.0.

Version 1.3.0 changes parts of what is described here: the editor's toolbar, the permissions and the converter. See [[release-notes/1-3-0]].
""",
        see=["release-notes", "release-notes/1-3-0", "release-notes/1-0", "edit-shape", ("What's new: release post", "/whats-new")],
    ),
    dict(
        slug="release-notes/1-0", book="release", kind="Technical changelog", nav="Versions 1.0.0 and 1.0.1",
        title="Versions 1.0.0 and 1.0.1: technical changelog",
        desc="Changelog for the first releases of the SVG to Slides Chrome extension, 1.0.0 and 1.0.1: drag and drop SVG insert into Google Slides with in-browser conversion.",
        applies=["SVG to Slides Chrome extension, versions 1.0.0 and 1.0.1"],
        summary="Version 1.0.0 is the first release: drag SVG files onto a Google Slides tab and they land as native, editable shapes, converted inside the browser. Version 1.0.1 removed an unused permission.",
        keys=["version 1.0.0", "version 1.0.1", "first release"],
        howto=False,
        version="1.0.1",
        body="""
## Version 1.0.1 {#v1-0-1}

July 2026.

| Mark | Change |
|---|---|
| REM | The activeTab permission. The extension did not use it, and Chrome Web Store review flagged it. |

## Version 1.0.0 {#v1-0-0}

July 2026. First release.

| Mark | Change |
|---|---|
| NEW | Drag one or more .svg files onto an open Google Slides tab. A preview follows the pointer. |
| NEW | Place the graphic, then press <<Command+V>> to confirm. The shapes land as native Slides shapes, one per path, grouped per file. |
| NEW | Up to 25 files per drop, laid out in a grid on the current slide. |
| NEW | Conversion runs inside the browser. The converter was the project's Python converter, compiled to WebAssembly. A converter on the svgslid.es server was the fallback. |
| NEW | No Google sign-in and no Google permissions. |

## How 1.0 differs from later versions {#differences}

| In 1.0 | Since |
|---|---|
| Every insert ended with <<Command+V>>. | 1.2.0: the click places the shapes. |
| Position was estimated from the window size. See [[kb/shapes-land-away-from-pointer]]. | 1.2.0: measured from the slide. |
| No editing tools. | 1.2.0: [[edit-shape]]. 1.3.0: [[toolbar]]. |
| The extension carried a Python runtime. | 1.3.0: a JavaScript converter. See [[how-conversion-works#javascript]]. |
""",
        see=["release-notes", "release-notes/1-2-0", "insert-svg", "how-shapes-reach-the-slide"],
    ),
]

INCLUDES = {}

for _t in TOPICS:
    for _k in ("summary", "body"):
        for _tok, _val in TOKENS.items():
            _t[_k] = _t[_k].replace(_tok, _val)
