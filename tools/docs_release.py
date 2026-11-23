"""Docs content: Release Notes. Version history and a technical changelog per release.

Sources: tools/site_pages.py whats_new_page (public release posts), the project's
release notes for 1.2.0 and 1.3.0, and the extension source. Package sizes are the
measured zips and unpacked folders.
"""

import site_docs as D

A13 = "SVG to Slides Chrome extension, version 1.3.0"

# Wording that depends on whether the Chrome Web Store has published the current version
# (site_docs.STORE). The %...% tokens in the topics below are filled in at the end of this module.
_ADDS = ("adds a toolbar with a pen, image masks, shape combining, a Layers panel and one-press undo, "
         "and it is 92% smaller than 1.2.0. Each release has a technical changelog below.")
TOKENS = {
    "%SUMMARY%": (f"Version 1.3.0 is the newest version of the Chrome extension. It is not in the Chrome Web Store yet, "
                  f"and the store installs version {D.STORE}. Version 1.3.0 {_ADDS}") if D.PENDING
                 else f"Version 1.3.0 is the current release of the Chrome extension. It {_ADDS}",
    "%DATE130%": "Not in the Chrome Web Store yet" if D.PENDING else D.CURRENT_DATE,
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
        desc="SVG to Slides version history: what each Chrome extension release added, package sizes, permissions by version, and a feature availability table for versions 1.0 to 1.3.",
        applies=["SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0", "SVG to Slides Web Uploader", "SVG to Slides Workspace Add-on"],
        summary="%SUMMARY%",
        keys=["release notes", "version history", "changelog", "what's new", "versions#versions", "feature availability#matrix", "package size#versions"],
        howto=False,
        version="1.3.0",
        body="""
## Chrome extension versions {#versions}

| Version | Date | What it added | Download | Installed | Chrome permissions |
|---|---|---|---|---|---|
| [[release-notes/1-3-0|1.3.0]] | %DATE130% | Toolbar, pen, snapping, image masks, combine, one-press undo, instant align, Layers, outline stroke and text, command palette, full-precision points, JavaScript converter | 392 KB | 1.1 MB | storage |
| [[release-notes/1-2-0|1.2.0]] | November 2026 | Edit Shape, round corners, editing Slides' own shapes, click to insert, exact placement | 5.8 MB | 14 MB | storage, one host permission |
| [[release-notes/1-0|1.0.1]] | July 2026 | Removed an unused permission | | | One host permission |
| [[release-notes/1-0|1.0.0]] | July 2026 | First release: drag SVG files onto a slide | | | |

Version 1.1.0 was an internal build and was not released. Its changes shipped in 1.2.0.

!!! Note: A new version reaches installed copies through the Chrome Web Store's automatic update, once the store has published it. To see which version you have, see [[install#check-version]].

## Feature availability by version {#matrix}

| Feature | 1.0 | 1.2 | 1.3 |
|---|---|---|---|
| Insert SVG files by drag and drop | Yes | Yes | Yes |
| Up to 25 files per drop | Yes | Yes | Yes |
| Converts in the browser | Yes | Yes | Yes |
| Click places the shapes, with no <<Command+V>> | | Yes | Yes |
| Placement measured from the slide | | Yes | Yes |
| [[edit-shape|Edit Shape]] | | Yes | Yes |
| [[round-corners|Round corners]] | | Yes | Yes |
| [[convert-slides-shapes|Edit Slides' own shapes]] | | Yes | Yes |
| Straight-edged shapes work with Slides' Edit points | | Yes | Yes |
| [[toolbar|Toolbar]] and [[command-palette|command palette]] | | | Yes |
| [[pen|Pen]] and [[snapping|snapping]] | | | Yes |
| [[mask-image|Mask image with shape]] | | | Yes |
| [[combine-shapes|Union, subtract, intersect, exclude]] | | | Yes |
| [[align-distribute|Align and distribute commands]] | | | Yes |
| [[layers|Layers panel]] and theme builder shortcut | | | Yes |
| [[outline-stroke-text|Outline stroke, outline text, stroke position]] | | | Yes |
| [[undo-redo|One-press undo]] | | | Yes |
| Paste SVG code | | | Yes |
| [[point-precision|Full-precision points]] | | | Yes |
| Server fallback for conversion | Yes | Yes | Removed |

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
        see=["release-notes/1-3-0", "release-notes/1-2-0", "release-notes/1-0", "install#updates", ("What's new: release posts", "/whats-new")],
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
