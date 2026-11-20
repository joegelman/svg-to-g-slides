"""Docs content: Getting Started, User's Guide, Web Uploader and Add-on.

Every statement here comes from the extension source (version 1.3.0), the site's
existing copy (specs, what's new, privacy, convert, add-on) or the project's
release notes. Don't add a claim that isn't backed by one of those.
Markup: see site_docs.blocks().
"""

A13 = "SVG to Slides Chrome extension, version 1.3.0"
A12 = "SVG to Slides Chrome extension, versions 1.2.0 and 1.3.0"
AALL = "SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0"
AWEB = "SVG to Slides Web Uploader"
AADD = "SVG to Slides Workspace Add-on for Google Slides"

TOPICS = [
    # ------------------------------------------------------------ Getting Started
    dict(
        slug="overview", book="start", kind="Overview", nav="What SVG to Slides does",
        title="What SVG to Slides does",
        desc="SVG to Slides converts SVG files into native, editable Google Slides shapes. Overview of the Chrome extension, the Web Uploader and the Workspace Add-on.",
        applies=[AALL, AWEB, AADD],
        summary="Google Slides has no SVG import. An SVG placed on a slide is flattened into a picture. SVG to Slides converts each path of the SVG into a native Slides shape, so the result can be selected, recoloured, resized and reshaped like a shape drawn in Slides.",
        keys=["SVG to Slides, overview", "products, the three", "Chrome extension, overview", "price", "Google Drawings", "native shapes"],
        body="""
## The three products {#products}

| Product | How you use it | Where conversion runs | What you get |
|---|---|---|---|
| **Chrome extension** | Drag .svg files onto an open Slides tab and click where they go. | In your browser. | Native shapes on the slide you have open. See [[insert-svg]]. |
| **Web Uploader** | Upload files on a web page. No install. | On the svgslid.es server. | A Google Drive link to a file with one slide per SVG. See [[web-uploader]]. |
| **Workspace Add-on** | Pick files in a dialog inside Slides, copy, paste. | On the svgslid.es server. | Native shapes on the current slide. See [[add-on]]. |

The shapes are ordinary Slides objects. They take the standard fill picker, resize without loss of quality, work in themes, and work in Google Drawings.

## What the extension adds on the slide {#tools}

From version 1.2.0 the extension edits shapes as well as importing them. Version 1.3.0 adds a toolbar and the tools below.

| Tool | What it is for | Topic |
|---|---|---|
| Edit Shape | Move the points and curves of any shape. | [[edit-shape]] |
| Round corners | Drag or type a corner radius. | [[round-corners]] |
| Pen | Draw new shapes point by point. | [[pen]] |
| Snapping | Snap points to other points, pixels or a grid. | [[snapping]] |
| Mask | Cut a picture to any shape. | [[mask-image]] |
| Combine | Union, subtract, intersect, exclude. | [[combine-shapes]] |
| Align and distribute | Instant, images included. | [[align-distribute]] |
| Layers | List, rename, hide and restack objects. | [[layers]] |
| Outline | Turn strokes and text into shapes. | [[outline-stroke-text]] |
| Command palette | Every command and its shortcut. | [[command-palette]] |

## Price and account {#price}

SVG to Slides is free. There is no account, no daily cap and no paid tier. The extension asks for no access to your Google account. See [[permissions-privacy]].

## What does not convert {#not-converted}

Some SVG features have no Slides equivalent or are not handled yet. Clip paths, masks, pattern fills, filters and transparency are examples. The tested list is in [[svg-compatibility]].
""",
        see=["install", "quick-start", "how-conversion-works", ("Specs: product facts", "/specs#facts"), ("Guide: Does Google Slides support SVG?", "/guides/does-google-slides-support-svg")],
    ),
    dict(
        slug="install", book="start", kind="How to", nav="Installing and updating",
        title="Installing and updating the extension",
        desc="Install the SVG to Slides Chrome extension, check which version you have, and see how updates arrive. Requirements and permissions by version.",
        applies=[AALL],
        summary="The extension installs from the Chrome Web Store and needs no account. It runs only on Google Slides editor pages. Chrome updates it automatically.",
        keys=["installing", "updating", "version, checking#check-version", "chrome://extensions#check-version", "requirements, extension#requirements", "update note#updates"],
        body="""
## Requirements {#requirements}

| Item | Requirement |
|---|---|
| Browser | Google Chrome on a desktop computer. |
| Page | A Google Slides presentation open for editing. The extension does not run on other pages. |
| Account | None. |
| Chrome permissions | Version 1.3.0: storage. Earlier versions: see [[permissions-privacy#by-version]]. |

>> To install the extension
1. Open [svgslid.es/chrome](/chrome). It leads to the SVG to Slides page in the Chrome Web Store.
2. Click **Add to Chrome**.
3. Open a Google Slides presentation. If one was already open, reload its tab.

In version 1.3.0 a round button appears at the left edge of the slide canvas. That button is the toolbar, closed. See [[toolbar]].

## Checking your version {#check-version}

>> To see which version is installed
1. In Chrome's address bar, type `chrome://extensions` and press <<Enter>>.
2. Find **SVG to Slides**. The version number is shown beside the name.

Each topic in this library states the versions it applies to. If a tool described here is missing, compare your version with the topic's box.

## How updates arrive {#updates}

Chrome updates extensions on its own, usually within a few hours of a new version being published in the Chrome Web Store. You do not need to do anything.

The first time you open Slides after an update, a short note in the corner of the page names what changed and links to the release post. It appears once. New installations do not see it.

!!! Note: An update can change the permissions the extension holds. Version 1.3.0 removes one. See [[release-notes/1-3-0#packaging]].
""",
        see=["quick-start", "toolbar", "release-notes", "kb/which-version", "permissions-privacy"],
    ),
    dict(
        slug="quick-start", book="start", kind="How to", nav="Quick start",
        title="Quick start: your first SVG",
        desc="Put an SVG into Google Slides as editable shapes in three steps: drag the file onto the slide, click to place it, then recolour, resize or reshape it.",
        applies=[A12],
        summary="Drag an .svg file onto a slide, click where it goes, and it lands as native shapes. This topic walks through the first insert and the three things most people do next.",
        keys=["quick start", "first SVG", "recolouring a shape#next", "resizing#next"],
        body="""
>> To put an SVG on a slide
1. Open your presentation in Google Chrome with the extension installed.
2. Drag an .svg file from a folder on your computer onto the slide. A faint preview follows the pointer with the label **Click to Place**.
3. Click where the graphic should go. It lands there as shapes, selected.

@fig insert-click-to-place | A Google Slides slide with a faint palm icon under the pointer and a pill reading Click to Place | The file has been dropped. The preview follows the pointer until you click.

## What to do next {#next}

| To do this | Do this |
|---|---|
| Change a colour | Select a shape and use Slides' fill picker. Each path of the SVG is its own shape, so parts recolour separately. |
| Resize | Drag a selection handle. The shapes are vectors, so edges stay sharp at any size. |
| Work on one part | Shapes from one file arrive grouped. Double-click to reach a shape inside the group. In version 1.3.0 you can also hold <<Command>> and click it. See [[layers#direct-select]]. |
| Change the outline | Double-click a shape and click **Edit Shape**. See [[edit-shape]]. |
| Open the tools | In version 1.3.0, click the round button at the left of the slide, or press <<Option+\\>>. See [[toolbar]]. |

!!! Tip: To bring in many files, select up to 25 and drag them together. See [[insert-svg#several]].
""",
        see=["insert-svg", "toolbar", "edit-shape", "svg-compatibility", ("Guide: Recolor SVGs in Google Slides", "/guides/recolor-svg-in-google-slides")],
    ),
    dict(
        slug="conventions", book="start", kind="Reference", nav="Document conventions",
        title="Document conventions",
        desc="How the SVG to Slides documentation is written: key names for Mac and Windows, typography, version boxes, note types, figures and Knowledge Base article IDs.",
        applies=["All SVG to Slides documentation"],
        summary="This library uses a small set of conventions for keys, interface names, versions and notes. Keys are given for Mac. The Windows key follows a fixed rule.",
        keys=["conventions", "key names#keys", "Windows keys#keys", "Mac keys#keys", "applies-to box#versions", "figures#figures", "notes, kinds of#notes", "article IDs#kb"],
        howto=False,
        body="""
## Keys {#keys}

Keys are printed in capitals and joined with a plus sign. <<Option+Shift+P>> means hold OPTION and SHIFT and press P. A phrase such as "<<Command>>-click" means hold the key and click.

Key combinations are given for Mac. On Windows, use the key in the second column. Point at any key combination in a topic to see the Windows form.

| Mac | Windows |
|---|---|
| <<Command>> | <<Ctrl>> |
| <<Option>> | <<Alt>> |
| <<Shift>> | <<Shift>> |
| <<Delete>> | <<Backspace>> |
| <<Command+Control+K>> | <<Ctrl+Alt+K>> |

The full list, with both columns, is in [[keyboard-shortcuts]].

## Typography {#typography}

| Convention | Used for |
|---|---|
| **Bold** | Names you see on screen: buttons, menus, panel titles. |
| *Italic* | A value you supply. |
| `Monospace` | File names, addresses, SVG code and text you type. |
| CAPITALS in a box | Keys. |

Spelling follows the product: colour, centre.

## Versions {#versions}

Each topic opens with a box headed "The information in this topic applies to". If the box names version 1.3.0 only, the tool is not present in earlier versions. To find your version, see [[install#check-version]].

## Procedures {#procedures}

A procedure starts with a line that begins "To", followed by numbered steps. Do the steps in order. A step that has a result says what you should see.

## Notes {#notes}

| Label | Meaning |
|---|---|
| Note | Information that qualifies the text around it. |
| Tip | A faster or easier way. |
| Important | Something that affects the result if you miss it. |
| Caution | A step that loses work or cannot be reversed. |

## Figures {#figures}

Screen pictures show the extension's own interface running over a sample deck, the Vacay.com pitch deck. Numbered yellow markers on a figure match the numbered list under it.

Figures labelled *Illustration* are frames from the release animations. They show the result on the slide and draw the toolbar in simplified form.

## Knowledge Base articles {#kb}

Knowledge Base articles are numbered Q100101 and up. The first word of the title gives the kind of article.

| Prefix | Kind of article |
|---|---|
| PRB | A problem and its cause. The behaviour may be by design. |
| FIX | A problem that a later version corrects. |
| INFO | Background on how something behaves. |
| HOWTO | A procedure. |
""",
        see=["keyboard-shortcuts", "kb", "glossary", "a-z-index"],
    ),

    # --------------------------------------------------------------- User's Guide
    dict(
        slug="insert-svg", book="guide", kind="How to", nav="Inserting SVG files",
        title="Inserting SVG files",
        desc="Insert SVG files into Google Slides with the SVG to Slides extension: drag and drop, click to place, several files at once, pasting SVG code, size and position.",
        applies=[AALL + ". Click to place: version 1.2.0 and later. Pasting SVG code: version 1.3.0."],
        summary="Drag one or more .svg files from your computer onto an open Google Slides tab, then click where they go. Every path lands as its own native shape. Paths from one file arrive as a group.",
        keys=["inserting SVG files", "drag and drop", "Click to Place", "placement#size", "several files#several", "25 files#several", "pasting SVG code#paste-code", "SVG code, pasting#paste-code", "cancelling an insert#cancel", "size of inserted shapes#size"],
        body="""
>> To insert an SVG file
1. Open the presentation in Google Chrome.
2. Drag the .svg file from a folder or the desktop onto the slide. A faint preview of the file follows the pointer, with a green plus badge and the label **Click to Place**.
3. Click the point where the graphic should be centred.

The shapes appear at that point, selected. Nothing needs pasting.

@fig insert-click-to-place | A slide with a faint palm icon under the pointer, a green plus badge and a grey pill reading Click to Place | After the drop. The preview follows the pointer until you click.

## Size and position {#size}

The graphic is fitted to about a fifth of the slide and centred on the point you click. Resize it afterwards with Slides' selection handles.

From version 1.3.0 a graphic keeps all of its detail however small it lands, so it can be enlarged later without loss. See [[point-precision]].

## Several files at once {#several}

Select up to 25 .svg files and drag them together. They land on the current slide in a grid, each file as its own group.

If the drop holds more than 25 .svg files, nothing is inserted and a message says so. Use the [[web-uploader]] for larger batches. See [[kb/more-than-25-files]].

## Pasting SVG code {#paste-code}

In version 1.3.0, SVG markup copied as text can be pasted onto the slide. Copy the code, click the slide and press <<Command+V>>. The same preview appears, and you click to place it.

## Cancelling {#cancel}

Press <<Esc>> before you click. The preview disappears and nothing is inserted.

## Files that are not SVG {#other-files}

A drop that holds no .svg file is left to Slides, which handles it as it always does.

## If the extension asks you to press COMMAND+V {#fallback}

The extension hands the shapes to Slides the way a paste does. If Slides does not accept them, the extension shows a prompt to press <<Command+V>>. Press it and the shapes land. See [[kb/press-command-v-prompt]].

!!! Note: In versions 1.0.0 and 1.0.1 every insert ended with <<Command+V>>. The click has inserted directly since version 1.2.0.

## What converts {#converts}

Paths, basic shapes, arcs, transforms and cut-outs convert. A gradient arrives as its first colour. Text, clip paths, masks, patterns and filters do not convert in the extension. The full table is in [[svg-compatibility]].
""",
        see=["quick-start", "svg-compatibility", "web-uploader", "how-shapes-reach-the-slide", "kb/svg-becomes-a-flat-image", ("Guide: How to insert an SVG into Google Slides", "/guides/insert-svg-into-google-slides")],
    ),
    dict(
        slug="toolbar", book="guide", kind="Reference", nav="The toolbar",
        title="The toolbar",
        desc="The SVG to Slides toolbar in Google Slides: where it is, how to open it, and what each button does: Layers, Edit Shape, Pen, Align, Combine, Outline.",
        applies=[A13],
        summary="The toolbar sits at the left edge of the slide canvas. Closed, it is one round button. Click the button or press <<Option+\\>> to open it. It holds every tool the extension adds to Slides.",
        keys=["toolbar", "svgslid.es button#closed", "opening the toolbar#closed", "hiding the toolbar#closed", "tooltips#tooltips", "dimmed buttons#dimmed", "pop-out menus#pop-outs", "stroke weight field#parts", "short screens#short"],
        howto=False,
        body="""
## The toolbar, closed {#closed}

@fig toolbar-closed | The left edge of a Google Slides canvas with one round yellow SVG button beside the slide | The toolbar when closed. | 1=The svgslid.es button. Click it, or press <<Option+\\>>, to open the toolbar.

The toolbar starts closed. Once you open or close it, the extension remembers the state on this computer.

## The toolbar, open {#parts}

@fig toolbar-open | The open toolbar: a two-column strip of icon buttons at the left of the slide, with numbered markers | The toolbar when open, with the logo selected. Buttons that do not apply to the selection are dimmed. | 1=svgslid.es button. Closes the toolbar.; 2=**Layers**. Opens the [[layers|Layers panel]].; 3=**Edit Shape**. Opens the [[edit-shape|point editor]] on the selection.; 4=**Pen**. [[pen|Draws a new shape]].; 5=**Commands**. Opens the [[command-palette|command palette]].; 6=**Arrange**. Bring forward, send backward, front, back.; 7=**Align and distribute**. See [[align-distribute]].; 8=**Combine**. Union, subtract, intersect, exclude. See [[combine-shapes]].; 9=**Group**, **Ungroup** and **Mask image with shape**. See [[mask-image]].; 10=**Outline stroke** and **Outline text**. See [[outline-stroke-text]].; 11=**Fill colour** and **Stroke colour**.; 12=Stroke weight in pixels. Type a value. 0 means no stroke.; 13=**Stroke position** and **Stroke on / off**. See [[fill-stroke]].

| Section | Buttons | Shortcuts |
|---|---|---|
| Top | svgslid.es button, Layers, Edit Shape, Pen, Commands | <<Option+\\>>, <<Option+1>>, double-click, <<Option+Shift+P>>, <<Command+\\>> |
| Place | Arrange, Align and distribute | See [[keyboard-shortcuts#arrange]] |
| Combine | Union, Subtract, Intersect, Exclude | <<Option+Shift+U>>, <<Option+Shift+S>>, <<Option+Shift+I>>, <<Option+Shift+E>> |
| Group | Group, Ungroup, Mask image with shape | <<Command+Option+G>>, <<Shift+Command+Option+G>>, <<Option+Shift+K>> |
| Outline | Outline stroke, Outline text | <<Option+Command+O>>, <<Option+Command+T>> |
| Paint | Fill colour, Stroke colour, weight, Stroke position, Stroke on / off | <<Option+Shift+F>>, <<Option+Shift+L>>, <<Option+Shift+[>> and <<Option+Shift+]>>, <<Option+Shift+/>> |

## Tooltips {#tooltips}

Point at any button, pop-out item or field to see its name and shortcut.

@fig toolbar-tooltip | The pointer over the Pen button with a dark tooltip reading Pen: draw a shape anywhere, Option Shift P | A tooltip. Every control has one.

## Pop-out menus {#pop-outs}

Buttons with a small mark in the corner open a row of commands beside the toolbar. Arrange, Align and distribute, and Stroke position work this way.

@fig align-flyout | The Align and distribute button open, showing eight align and distribute buttons in a row, with a tooltip on Align centres horizontally | The Align and distribute pop-out, with three objects selected.

## Dimmed buttons {#dimmed}

A button is dimmed when its command does not apply to what is selected. Outline text, for example, is dimmed unless the selection has text. Clicking a dimmed command shows a short message that says what to select.

## Short screens {#short}

When the canvas is too short for the whole toolbar, the Combine buttons fold into one pop-out button, then the Outline buttons do the same.

## While a command runs {#busy}

While the extension carries out a command the toolbar ignores clicks and the pointer shows the progress cursor. This lasts a moment.

## When the toolbar is hidden {#hidden}

The toolbar is hidden while Edit Shape is open, because the editor has its own toolbar in the same place. It is also hidden in full-screen view.
""",
        see=["keyboard-shortcuts", "commands", "command-palette", "layers", "edit-shape"],
    ),
    dict(
        slug="edit-shape", book="guide", kind="How to", nav="Edit Shape: points and curves",
        title="Edit Shape: points and curves",
        desc="Edit the points and curves of any shape in Google Slides with Edit Shape: drag points and handles, add and remove points, scale, rotate, skew, type exact sizes.",
        applies=[A12 + ". The box, exact values and the two-column editor toolbar: version 1.3.0."],
        summary="Edit Shape opens a vector editor on the slide at the shape's exact size and position. Drag points and curve handles, add or remove points, then click **Done**. The shape updates in place and returns to its place in the stack.",
        keys=["Edit Shape", "points, editing", "curve handles#points", "handles#points", "corner point#points", "smooth point#points", "adding a point#points", "removing a point#points", "smart box#smart-box", "skew#smart-box", "rotating in Edit Shape#smart-box", "scaling in Edit Shape#smart-box", "exact values#exact-values", "Done#done", "Cancel#done", "zoom in Edit Shape#points"],
        body="""
>> To edit a shape's points
1. Double-click the shape, then click **Edit Shape**. In version 1.3.0 you can also select the shape and click **Edit Shape** on the toolbar.
2. Drag a point to move it. Click a point to see its curve handles, and drag a handle to change the curve.
3. Click **Done**, or press <<Enter>>.

@fig edit-shape | The Edit Shape editor open on a palm tree icon. Every point of the outline is marked, a box with handles surrounds the shape, and the editor toolbar is at the left. | Edit Shape open on a palm icon, version 1.3.0. Round marks are smooth points and square marks are corner points. | 1=**Select** tool. <<V>>; 2=**Pen** tool. Adds and removes points, and draws. <<P>>; 3=**Snapping**. See [[snapping]].; 4=The same command groups as the main toolbar: Arrange, Align, Combine, Group, Outline, fill and stroke.; 5=Undo and redo, point by point.; 6=Zoom. Click to return to 100%.; 7=**Cancel**. Discards the edit.; 8=**Done**. Applies the edit.; 9=Size pill: width, height and rotate-by. On shapes with corners it also shows the corner radius.; 10=The hint line names the keys for the current tool.

## Points and handles {#points}

| To do this | Do this |
|---|---|
| Move a point | Drag it. Hold <<Shift>> to keep to 45° steps. |
| Change a curve | Click the point, then drag one of its handles. |
| Move one handle only | Hold <<Option>> while dragging the handle. |
| Switch a point between smooth and corner | Double-click the point. |
| Add a point | Press <<P>>, then click the outline where the point should be. |
| Remove a point | Press <<P>>, then click the point. |
| Select several points | <<Shift>>-click each one, or drag a box around them. |
| Select every point of a shape | Click the shape. |
| Select all points | <<Command+A>> |
| Nudge | Arrow keys. Hold <<Shift>> for ten times the step. |
| Delete the selected points | <<Delete>> |
| Undo, redo | <<Command+Z>>, <<Shift+Command+Z>> |
| Zoom | Pinch, or <<Command+Plus>> and <<Command+Minus>>. <<Command+0>> returns to 100%. |
| Pan | Hold <<Spacebar>> and drag, or scroll. |

@fig edit-points-1-2 | A palm tree outline with one point selected and its two curve handles extended, the pointer on a handle | A selected point and its two handles. Recorded in Google Slides with version 1.2.0, whose editor toolbar had one column.

## The box {#smart-box}

In version 1.3.0 a box surrounds the selection inside the editor. Dragging it transforms the shape while its points stay editable.

| Drag | Result |
|---|---|
| A corner | Scale. <<Shift>> keeps the proportions. <<Option>> scales from the centre. |
| An edge | Stretch in one direction. <<Option>> stretches from the centre. |
| <<Command>> + an edge | Skew. <<Shift>> snaps to 15°. |
| <<Command>> + a corner, or just outside a corner | Rotate. <<Shift>> snaps to 15°. |

## Typing exact values {#exact-values}

The pill under the shape holds the width and height in pixels, a rotate-by field and, on shapes with corners, the corner radius. Type a value and press <<Enter>>. Hold <<Option>> and drag across any number to change it by dragging. Add <<Shift>> for steps of ten.

## Commands inside the editor {#scope}

The editor's toolbar repeats the command groups of the main toolbar. Inside the editor a command acts on the shapes that have selected points, or on every shape in the editor when no point is selected. Combine, group, ungroup, outline, fill and stroke are held in the editor and applied when you click **Done**.

## Done and Cancel {#done}

**Done** replaces the shape on the slide with the edited one, in the same place in the stack. Shapes above it stay visible while you edit, so you can line points up against them. In version 1.3.0 the whole session is one undo step. See [[undo-redo]].

**Cancel** discards the edit. <<Esc>> clears the selection first. With nothing selected, <<Esc>> applies the edit the same as **Done**.

!!! Important: **Done** puts a new object in place of the original. Animations and links attached to the original do not carry over. A shape edited from inside a group comes back just above that group.

## What can be edited {#what}

Edit Shape opens directly on shapes inserted by SVG to Slides. On Slides' own shapes, lines, text boxes and WordArt it converts the object first. See [[convert-slides-shapes]]. Images, video and charts cannot be edited as shapes.
""",
        see=["round-corners", "pen", "snapping", "convert-slides-shapes", "undo-redo", "keyboard-shortcuts#editor", "edit-points-and-polylines"],
    ),
    dict(
        slug="round-corners", book="guide", kind="How to", nav="Rounding corners",
        title="Rounding corners",
        desc="Round the corners of shapes in Google Slides by dragging a corner handle or typing a radius in pixels. Round one corner, a whole shape, or several shapes at once.",
        applies=[A12],
        summary="In Edit Shape, shapes with corners show a small circle just inside each corner. Drag a circle toward the middle of the shape to round the corner, or type a radius in pixels.",
        keys=["rounding corners", "corner radius", "radius pill", "several shapes, rounding#several"],
        body="""
>> To round the corners of a shape
1. Open the shape in Edit Shape. See [[edit-shape]].
2. Drag one of the small circles inside a corner toward the middle of the shape. A pill under the shape shows the radius in pixels.
3. To set an exact radius, type a value in the pill and press <<Enter>>.
4. Click **Done**.

@fig round-corners-1-2 | Three cards on a slide in Edit Shape, each with rounded corners and a circle inside every corner. A pill under them reads 25 px, All corners. | Three cards, twelve corners, one radius. Recorded in Google Slides with version 1.2.0.

## Which corners change {#which}

| Selection in the editor | Corners that round |
|---|---|
| The whole shape, or nothing | Every corner of the shape. |
| Several shapes | Every corner of every shape, together. |
| One point or a few points | Those corners only. |

Hold <<Shift>> while dragging to change the radius in steps of 10 pixels.

## Several shapes at once {#several}

>> To give several shapes the same radius
1. Select the shapes on the slide.
2. Open Edit Shape.
3. Type the radius in the pill and press <<Enter>>.
4. Click **Done**.
""",
        see=["edit-shape", "edit-shape#exact-values", "convert-slides-shapes"],
    ),
    dict(
        slug="pen", book="guide", kind="How to", nav="Drawing with the pen",
        title="Drawing with the pen",
        desc="Draw custom shapes in Google Slides with the SVG to Slides pen tool: click for corners, drag for curves, close the path, and place native shapes on the slide.",
        applies=[A13],
        summary="The pen draws new shapes point by point, anywhere on the slide. Press <<Option+Shift+P>> or click **Pen** on the toolbar. Click for a corner, drag for a curve, and click the first point to close the shape.",
        keys=["pen", "drawing shapes", "closing a path#keys", "open path#keys", "freehand#limits", "pencil#limits", "new shapes, paint of#result"],
        body="""
>> To draw a shape
1. With nothing selected, press <<Option+Shift+P>> or click **Pen** on the toolbar. An empty editor opens over the slide.
2. Click to place a corner point. To make a curve, press, drag and release.
3. Click the first point to close the shape. A ring appears on the first point when the pointer is over it. To leave the path open, press <<Enter>> or <<Esc>>.
4. Click **Done**. The new shapes are placed on the slide, on top.

@fig pen-drawing | The pen editor over a slide with a grid showing. A speech-bubble outline is half drawn, with a dashed line from the last point to the pointer and a pink mark where it will snap. | Seven points placed with the grid on. The dashed segment follows the pointer and the pink mark shows where the next point will snap.

## Pen keys {#keys}

| To do this | Do this |
|---|---|
| Place a corner point | Click. |
| Place a smooth point | Press, drag, release. |
| Make a sharp turn after a curve | Hold <<Option>> while dragging to break the handles. |
| Keep to 45° steps | Hold <<Shift>>. |
| Close the shape | Click the first point. |
| Leave the path open | <<Enter>> or <<Esc>> |
| Remove the last point | <<Delete>> |
| Undo one point | <<Command+Z>> |
| Carry on an open path | Click its end point. |
| Add a point to a path | Click a segment. |
| Remove a point from a path | Click the point. |
| Switch to the Select tool | <<V>> |

## What you get {#result}

Each path becomes a new shape. The first shape you draw has a 2 pixel dark stroke and no fill. Each later shape starts with the paint of the last one drawn. Set a fill or stroke from the editor's toolbar before you click **Done**, or afterwards on the slide.

**Done** places all the new shapes in one undo step.

## Pen with shapes selected {#with-selection}

If shapes are selected when you press <<Option+Shift+P>>, the editor opens on those shapes and the pen can both edit them and draw new ones beside them.

## Limits {#limits}

The pen draws point by point. There is no freehand mode.
""",
        see=["snapping", "edit-shape", "fill-stroke", "combine-shapes", "keyboard-shortcuts#editor"],
    ),
    dict(
        slug="snapping", book="guide", kind="Reference", nav="Snapping",
        title="Snapping",
        desc="Snapping in the SVG to Slides editor: snap pen points and dragged points to other points, slide edges and centre, whole pixels, or a grid of any size in Google Slides.",
        applies=[A13],
        summary="Snapping pulls pen points and dragged points onto other points, the slide's edges and centre, whole pixels, or a grid. The magnet button in the editor's toolbar sets it. Points and pixels are on to start.",
        keys=["snapping", "grid#grid", "grid size#grid", "magnet button", "guides, pink#points", "pixels, snapping to#pixels", "snapping, turning off for one move#override"],
        howto=False,
        body="""
@fig snapping-menu | The Snapping pop-out beside the editor toolbar with three toggle buttons and a grid size field reading 10 px | The Snapping pop-out. | 1=**Snap to points**, the lines through them, and the slide's edges and centre.; 2=**Snap to whole pixels**.; 3=**Snap to the grid**. Turning it on shows the grid.; 4=Grid size in pixels.

## Snap to points {#points}

A point being placed or dragged snaps to other points, to the horizontal and vertical lines through them, and to the slide's edges and centre. Pink guides and a pink cross show what caught it. A point wins over the grid and pixels when it is within 6 screen pixels.

## Snap to whole pixels {#pixels}

Positions are rounded to whole pixels.

## Snap to the grid {#grid}

The grid starts at the slide's top-left corner. The size is 10 pixels to start. Type a size in the field to change it, which also turns the grid on. Press <<Command+'>> to show or hide the grid. The grid is not drawn when its lines would be less than 6 pixels apart on screen.

## What snaps {#what}

- Pen points and their handles, and the dashed preview segment.
- Dragged points. The point you grab snaps and the rest of the selection follows.
- Dragged handles.

## Turning snapping off for one move {#override}

Hold <<Command>> while placing or dragging to ignore snapping. <<Shift>> still keeps a move to 45° steps.

## Where the settings are kept {#stored}

Snapping settings are kept on this computer. They are not part of the presentation.
""",
        see=["pen", "edit-shape", "keyboard-shortcuts#editor", "permissions-privacy#storage"],
    ),
    dict(
        slug="mask-image", book="guide", kind="How to", nav="Masking an image",
        title="Masking an image with a shape",
        desc="Crop a picture to any shape in Google Slides with Mask image with shape: put a shape over an image, select both, press Option+Shift+K. The picture keeps its position.",
        applies=[A13],
        summary="Put a shape over a picture, select both, and press <<Option+Shift+K>>. The shape cuts out the picture under it. Any shape or group of shapes can be the mask, and the picture stays exactly where it was.",
        keys=["masking an image", "Mask image with shape", "crop to shape", "image, masking", "rotated image#limits", "mask, editing#editing"],
        body="""
>> To mask an image with a shape
1. Place the shape over the picture, where the picture should show through.
2. Select the picture and the shape. Click one, then <<Shift>>-click the other.
3. Press <<Option+Shift+K>>, or click **Mask image with shape** in the Group section of the toolbar.

The picture is cut to the shape. It is neither stretched nor re-cropped, and the result takes the picture's place in the stack. The change is one undo step.

@fig mask-before-after | Two views of a slide. On the left a yellow arch sits over a beach photograph. On the right the photograph shows only inside the arch. | Before and after. An arch over a photograph, then the photograph cut to the arch. *Illustration.*

## Editing the mask afterwards {#editing}

Open the masked picture in [[edit-shape]] and move its points. The picture holds still while the outline changes. The editor draws the shape grey while you edit, and the picture returns when you click **Done**.

## Requirements and limits {#limits}

| Condition | Result |
|---|---|
| The mask is a group of shapes | Works. The group counts as one mask. |
| The mask is text | Outline the text first with <<Option+Command+T>>. See [[outline-stroke-text]]. |
| The image is rotated | Not supported yet. Straighten the image first. |
| The shape is very thin | The extension reports that the shape is too thin to mask with. |
| More or fewer than two objects are selected | Select one image and one shape, or one image and one group. |

See [[kb/cannot-mask-image]] for the messages and what each one means.
""",
        see=["edit-shape", "outline-stroke-text", "combine-shapes", "undo-redo", "kb/cannot-mask-image"],
    ),
    dict(
        slug="combine-shapes", book="guide", kind="How to", nav="Combining shapes",
        title="Combining shapes",
        desc="Combine shapes in Google Slides with union, subtract, intersect and exclude. Merge shapes into one, cut one shape out of another, and undo in one step.",
        applies=[A13],
        summary="Union, Subtract, Intersect and Exclude make one shape from two or more. They work on the slide and inside Edit Shape, and each is one undo step.",
        keys=["combining shapes", "union#commands", "subtract#commands", "intersect#commands", "exclude#commands", "boolean operations", "merging shapes"],
        body="""
## The four commands {#commands}

| Command | Result | Shortcut |
|---|---|---|
| **Union** | One shape covering everything the selected shapes cover. | <<Option+Shift+U>> |
| **Subtract** | The bottom shape with the shapes above it cut out. | <<Option+Shift+S>> |
| **Intersect** | Only the area where the shapes overlap. | <<Option+Shift+I>> |
| **Exclude** | Everything except the area where the shapes overlap. | <<Option+Shift+E>> |

>> To combine shapes
1. Select two or more shapes.
2. Click the command in the Combine section of the toolbar, or press its shortcut.

@fig combine-before-after | Two views of a slide. On the left, three overlapping circles and a rounded bar. On the right, a single cloud shape. | Before and after Union. Four shapes become one cloud. *Illustration.*

Press <<Command+Z>> once to split them again. See [[undo-redo]].

## Inside Edit Shape {#in-editor}

The same four buttons are on the editor's toolbar. There they act on the shapes that have selected points, or on every shape in the editor, and the result is applied when you click **Done**.

## Limits {#limits}

- Gradients, pattern fills, transparency and shadows are not carried into the result.
- Images, video and charts cannot be combined.
- The shapes need a fill or an outline.
- Intersect needs shapes that overlap. If a command would leave nothing, the extension says so and changes nothing.
""",
        see=["mask-image", "outline-stroke-text", "edit-shape", "undo-redo", "limits"],
    ),
    dict(
        slug="align-distribute", book="guide", kind="How to", nav="Aligning and distributing",
        title="Aligning and distributing",
        desc="Align and distribute objects in Google Slides instantly with SVG to Slides, including aligning a single image to the slide's left, right, top or bottom edge.",
        applies=[A13],
        summary="The align and distribute commands move objects in one step, straight to the result, and leave images intact. One object on its own, an image included, aligns to the slide's edges.",
        keys=["aligning", "distributing", "align to slide edge#single", "single object, aligning#single", "image, aligning#single", "centre on page#single"],
        body="""
## Commands {#commands}

| Command | Shortcut | Needs |
|---|---|---|
| Align left | <<Option+A>> | One object or more |
| Align centres horizontally | <<Option+H>> | One object or more |
| Align right | <<Option+D>> | One object or more |
| Align top | <<Option+W>> | One object or more |
| Align middles vertically | <<Option+V>> | One object or more |
| Align bottom | <<Option+S>> | One object or more |
| Distribute horizontal spacing | <<Option+Shift+H>> | Three objects or more |
| Distribute vertical spacing | <<Option+Shift+V>> | Three objects or more |

>> To align objects
1. Select the objects.
2. Click **Align and distribute** on the toolbar and choose a command, or press its shortcut.

@fig align-flyout | The Align and distribute pop-out with eight buttons and a tooltip reading Align centres horizontally, Option H | The pop-out, with a title, a date and a logo selected.

With two or more objects selected, the objects align to each other.

## One object aligns to the slide {#single}

With one object selected, the align commands use the slide. Left, right, top and bottom move the object to that edge of the slide. Centre and middle centre it on the page.

This works for images. The extension places a 1 pixel helper at the corner of the slide it needs, runs Slides' own Align, and removes the helper, all in one undo step. Nothing extra is left in the presentation.

@fig align-edge-before-after | Two views of the left half of a slide. A small photograph sits in the middle on the left view and in the bottom-left corner on the right view. | A single photograph before and after Align left and Align bottom. *Illustration.*

## How the commands run {#how}

The extension runs Slides' own Align, Distribute and Center on page commands behind a still copy of the slide. You see the objects move once. Because the objects are moved by Slides and not deleted and pasted, images stay intact. See [[undo-and-still-copy]].
""",
        see=["toolbar#pop-outs", "layers", "undo-redo", "undo-and-still-copy", "keyboard-shortcuts#align"],
    ),
    dict(
        slug="layers", book="guide", kind="Reference", nav="The Layers panel",
        title="The Layers panel",
        desc="The Layers panel for Google Slides in SVG to Slides: list every object on a slide, select, rename, hide, restack and fold groups. Theme objects are marked.",
        applies=[A13],
        summary="Press <<Option+1>> to list every object on the current slide, front first. Click a row to select the object. Drag rows to restack, double-click to rename, and use the eye to hide an object while you work.",
        keys=["Layers panel", "layers", "renaming a layer#actions", "hiding an object#hide", "eye#hide", "restacking#actions", "groups in Layers#actions", "small objects#small", "direct select#direct-select", "COMMAND-click#direct-select", "selecting inside a group#direct-select"],
        howto=False,
        body="""
@fig layers-panel | The Layers panel docked at the left of Google Slides, listing two text layers, a group named Vacay logo with two shapes inside, an image named Beach photo, and two greyed theme objects marked M | The Layers panel on the cover slide of the sample deck. | 1=Close. Slides' filmstrip returns.; 2=A text layer. It is named by its words until you rename it.; 3=A group. The arrow folds it open and closed.; 4=The objects inside the group.; 5=The eye hides an object in your view.; 6=A theme object, greyed and marked **M**. See [[theme-objects]].; 7=The **Layers** button on the toolbar.; 8=A reminder of the rules.

The panel docks over Slides' filmstrip and shows the slide you have open. Close the panel to get the filmstrip back.

## Working with rows {#actions}

| To do this | Do this |
|---|---|
| Select an object | Click its row. This works for objects inside groups too. |
| Add to the selection | <<Shift>>-click a row. |
| Restack | Drag a row up or down. Only top-level rows can be dragged. |
| Rename | Double-click the name and type. <<Enter>> keeps the name. <<Esc>> cancels. Clicking elsewhere keeps it. |
| Open or close a group | Click the arrow beside it. Selecting an object inside a group opens the groups around it. |
| Hide or show | Click the eye. |

## Hiding {#hide}

The eye hides an object in your view of the editor so that you can reach what is behind it. The object stays in the presentation. Other people still see it, and it still appears in the slideshow and in exports. Hiding lasts until you click the eye again or reload the page.

## Small objects {#small}

An object smaller than 6 pixels on screen is hard to click. The first click on its row says so. A second click within 5 seconds zooms in on the object and selects it.

## Selecting on the slide inside groups {#direct-select}

Hold <<Command>> and click an object on the slide to select the innermost object under the pointer, however deep it is in groups. <<Shift+Command>>-click adds to the selection. While <<Command>> is held, an outline shows what a click would pick.

## What is kept on this computer {#stored}

Layer names are kept on the computer you used. They are not saved in the presentation and do not appear for other people or on another computer. Hiding is not kept at all: it applies to the page you have open. See [[kb/layer-names-missing]].
""",
        see=["theme-objects", "toolbar", "align-distribute", "kb/layer-names-missing", "kb/object-greyed-with-m"],
    ),
    dict(
        slug="theme-objects", book="guide", kind="Reference", nav="Theme objects",
        title="Theme objects and the theme builder",
        desc="Why some objects on a Google Slides slide cannot be selected: they belong to the layout or master. How SVG to Slides marks theme objects and opens the theme builder on them.",
        applies=[A13],
        summary="Objects that come from the slide's layout or master are drawn on the slide but cannot be changed there. The Layers panel greys them and marks them **M**. A second click opens Slides' theme builder on the layout or master that holds the object.",
        keys=["theme objects", "theme builder", "master", "layout", "M badge", "objects that cannot be selected"],
        body="""
## What a theme object is {#what}

A logo in the corner of every slide, a footer line, a background shape: these usually live on a layout or on the master, and Slides draws them on each slide that uses that layout. On the slide they look like any other object, but a click does not select them.

## How they are marked {#marked}

In the [[layers|Layers panel]], theme objects are listed at the bottom, greyed, with an **M** badge. With <<Command>> held over the slide, a theme object gets a dashed amber outline in place of the blue one.

>> To edit a theme object
1. Click its row in the Layers panel. A message explains that the object belongs to the theme, and the row turns amber.
2. Click the row again within 5 seconds. Slides' theme builder opens on the layout or master that holds the object, with the object selected.
3. Make the change.
4. Press <<Option+Shift+M>> to go back to the slide.

A <<Command>>-click on a theme object on the slide follows the same two steps.

## The theme builder shortcut {#shortcut}

<<Option+Shift+M>> opens the theme builder from any slide and returns from it. It is the same view that Slides opens from **View › Theme builder**.

!!! Note: A change made in the theme builder affects every slide that uses that layout or master.
""",
        see=["layers", "kb/object-greyed-with-m", "keyboard-shortcuts#anytime"],
    ),
    dict(
        slug="outline-stroke-text", book="guide", kind="How to", nav="Outlining strokes and text",
        title="Outlining strokes and text",
        desc="Outline stroke and Outline text in Google Slides: turn lines, borders and text into shapes you can reshape, restore outlined text, set stroke position.",
        applies=[A13],
        summary="**Outline stroke** turns lines and borders into filled shapes. **Outline text** turns text into shapes whose points you can edit. On the computer that outlined it, the same command puts the text back.",
        keys=["outlining a stroke#stroke", "outlining text#text", "text to shapes#text", "restoring text#restore", "fonts#fonts", "Google Fonts#fonts", "stroke position#position", "inside stroke#position", "outside stroke#position"],
        body="""
## Outline stroke {#stroke}

>> To turn a stroke into a shape
1. Select a shape or line that has a stroke.
2. Press <<Option+Command+O>>, or click **Outline stroke** on the toolbar.

The stroke becomes a filled shape in the stroke's colour, as wide as the stroke was. A shape that had both a fill and a stroke becomes two shapes: the fill, and the outline that was its stroke. Use it when a border has to be reshaped, combined or used as a mask like any other shape.

## Outline text {#text}

>> To turn text into shapes
1. Select the text box or the shape that holds the text.
2. Press <<Option+Command+T>>, or click **Outline text** on the toolbar.

The text becomes filled shapes in the form of its letters. A shape that held the text stays as it was, without the text. The letter shapes can then be reshaped in [[edit-shape]], combined, or used as a mask.

## Restoring text {#restore}

Select the outlined text and press <<Option+Command+T>> again, or choose **Restore outlined text** from the [[command-palette]]. The original text returns as live text, at the place and size the outlines have now.

!!! Important: Text can be restored only on the computer that outlined it. The extension keeps the original text on that computer. The presentation does not hold it.

## Fonts {#fonts}

To outline text the extension needs the font's letter shapes.

| Font | Where the letter shapes come from |
|---|---|
| A Google font | The extension downloads the font from Google Fonts. The request names the font family, weight and style. It carries nothing from your presentation. |
| A font installed on your computer | Chrome asks for permission to read your fonts. Allow it to continue. |
| A system font that cannot be downloaded | The extension uses a font with the same letter widths and shows a note naming it. |

If no source works, the extension reports that it could not get the font. See [[kb/outline-text-font]].

## Stroke position {#position}

**Stroke position** on the toolbar sets whether a closed shape's stroke sits inside the outline, centred on it, or outside it. Slides always centres a stroke, so the extension moves the outline by half the stroke weight to get the other two.

The extension remembers the original outline on this computer, so **Centre stroke** returns to it.

## Limits {#limits}

- Gradients, pattern fills, transparency and shadows are not carried into outlined shapes.
- Images, video and charts cannot be outlined.
- Outlined-text memory and stroke-position memory are kept on the computer you used.
""",
        see=["fill-stroke", "combine-shapes", "mask-image", "kb/outline-text-font", "permissions-privacy#network"],
    ),
    dict(
        slug="fill-stroke", book="guide", kind="Reference", nav="Fill, stroke and exact values",
        title="Fill, stroke and exact values",
        desc="Fill colour, stroke colour, stroke weight in pixels, stroke on and off, and the rotate and resize shortcuts in the SVG to Slides toolbar for Google Slides.",
        applies=[A13],
        summary="The Paint section of the toolbar sets fill colour, stroke colour, stroke weight in pixels and stroke position. Numbers can be typed or changed by dragging.",
        keys=["fill colour", "stroke colour", "stroke weight#weight", "stroke on / off#weight", "scrubbing a number#scrub", "rotate shortcuts#transform", "resize shortcuts#transform"],
        howto=False,
        body="""
## Colours {#colours}

| Command | Shortcut | What happens |
|---|---|---|
| **Fill colour** | <<Option+Shift+F>> | Opens Slides' own fill colour menu for the selection. |
| **Stroke colour** | <<Option+Shift+L>> | Opens Slides' own border colour menu for the selection. |

The bar under each button shows the current colour of the selection.

## Stroke weight {#weight}

| Control | Shortcut | What it does |
|---|---|---|
| Weight field | | Type a weight in pixels and press <<Enter>>. 0 removes the stroke. |
| Thinner stroke | <<Option+Shift+[>> | Steps down through Slides' weights: 24, 16, 12, 8, 4, 3, 2, 1 pixels. |
| Thicker stroke | <<Option+Shift+]>> | Steps up through the same weights. |
| **Stroke on / off** | <<Option+Shift+/>> | Removes the stroke or puts it back. |
| **Stroke position** | | Inside, centre or outside. See [[outline-stroke-text#position]]. |

## Changing a number by dragging {#scrub}

Hold <<Option>> and drag left or right across a number field to change the value. Add <<Shift>> for steps of ten. This works on the weight field and on every field in the Edit Shape pill.

## Rotate and resize {#transform}

The toolbar has no rotate or resize buttons. Outside Edit Shape, use Slides' own shortcuts. Inside Edit Shape, use [[edit-shape#smart-box|the box]].

| Command | Shortcut |
|---|---|
| Rotate 15° left or right | <<Option+Left Arrow>>, <<Option+Right Arrow>> |
| Rotate 1° left or right | <<Option+Shift+Left Arrow>>, <<Option+Shift+Right Arrow>> |
| Make larger | <<Command+Control+K>> |
| Make smaller | <<Command+Control+J>> |
""",
        see=["toolbar", "outline-stroke-text", "edit-shape#exact-values", "keyboard-shortcuts#paint"],
    ),
    dict(
        slug="command-palette", book="guide", kind="How to", nav="The command palette",
        title="The command palette",
        desc="Open the SVG to Slides command palette in Google Slides with Command+\\ to search and run every command by name, with its keyboard shortcut shown.",
        applies=[A13],
        summary="Press <<Command+\\>> to open a searchable list of every command with its shortcut. Type a few letters, move with the arrow keys and press <<Enter>> to run the command.",
        keys=["command palette", "Commands button", "searching commands"],
        body="""
>> To run a command by name
1. Press <<Command+\\>>, or click **Commands** on the toolbar.
2. Type part of the command's name. The list narrows as you type.
3. Press <<Up Arrow>> or <<Down Arrow>> to move, and <<Enter>> to run the command.

Press <<Esc>>, or <<Command+\\>> again, to close the palette without running anything.

@fig command-palette | The command palette open over a slide: a search field reading Type a command and a list grouped under Shape tools, Outline, Arrange, and Align and distribute, each command with its shortcut at the right | The command palette. Shortcuts are listed at the right of each command.

## What the palette lists {#lists}

Commands are grouped: Shape tools, Outline, Arrange, Align and distribute, Combine, Group, Fill and stroke, Transform and stroke. The full list with descriptions is in [[commands]].

Commands that need a selection are dimmed while nothing is selected. The Pen, the Layers panel, the toolbar and the theme builder can be opened at any time.
""",
        see=["commands", "keyboard-shortcuts", "toolbar"],
    ),
    dict(
        slug="undo-redo", book="guide", kind="Reference", nav="Undo and redo",
        title="Undo and redo",
        desc="How undo works with SVG to Slides in Google Slides: one press of Command+Z undoes a combine, outline, mask or a whole Edit Shape session, and when Slides' own undo takes over.",
        applies=[A13],
        summary="One press of <<Command+Z>> undoes a whole change made by the extension, even when the change took several steps inside Slides. <<Shift+Command+Z>> or <<Command+Y>> redoes it in one press.",
        keys=["undo", "redo", "one-step undo", "COMMAND+Z"],
        howto=False,
        body="""
## Changes that undo in one press {#which}

- Union, Subtract, Intersect and Exclude.
- Mask image with shape.
- Outline stroke, Outline text and Restore outlined text.
- Stroke position, a typed stroke weight, Thinner stroke and Thicker stroke.
- Restacking in the Layers panel.
- Aligning one object to a slide edge.
- A whole Edit Shape or pen session, from opening the editor to **Done**.

Align and distribute with several objects are a single Slides step to begin with.

## How to undo and redo {#how}

| To do this | Press |
|---|---|
| Undo the extension's last change | <<Command+Z>> |
| Redo it | <<Shift+Command+Z>> or <<Command+Y>> |

Slides' own **Undo** and **Redo** buttons do the same. You can undo and redo back and forth through a chain of the extension's changes, one press each.

## When Slides' own undo takes over {#slides-undo}

The one-press undo applies while the slide is as the extension left it. If you change the slide yourself after one of the extension's changes, Slides' own undo takes over from there, and a change that took several steps then takes several presses to undo. See [[kb/undo-takes-several-presses]].

While you are typing in a text box, <<Command+Z>> is always Slides' own.

## Inside Edit Shape {#in-editor}

Inside the editor, <<Command+Z>> undoes one edit at a time: one moved point, one pen point. After **Done**, the whole session is one step on the slide.
""",
        see=["undo-and-still-copy", "edit-shape#done", "kb/undo-takes-several-presses"],
    ),
    dict(
        slug="convert-slides-shapes", book="guide", kind="Reference", nav="Editing Slides' own shapes",
        title="Editing Slides' own shapes",
        desc="Edit the points of Google Slides' built-in shapes, arrows, callouts, lines, text boxes and WordArt. What each object becomes when Edit Shape converts it, and what is lost.",
        applies=[A12],
        summary="Edit Shape also opens on objects you did not bring in as SVG: shapes from Slides' shape menu, arrows, callouts, lines, text boxes and WordArt. It converts the object into custom shapes first, and tells you what that costs before you start.",
        keys=["Slides' own shapes, editing", "WordArt#table", "arrows#table", "callouts#table", "lines and connectors#table", "text box#table", "adjustment handles#table", "converting a shape"],
        howto=False,
        body="""
## How it works {#how}

Double-click the object. Slides does what it always does: it starts text editing or steps into the group. The **Edit Shape** button also appears, with a note of the cost in grey beside it, for example "text becomes outlines". Click the button to convert the object and open the editor.

The result looks the same as the original. It is a drawing made of custom shapes and is no longer the original preset, line or WordArt.

## What each object becomes {#table}

| Object | After conversion | What is lost |
|---|---|---|
| A shape-menu shape with one outline: arrow, callout, star, rounded rectangle | One shape | Adjustment handles, the small yellow diamonds. |
| A shaded shape: cube, can | A group. A cube becomes 4 shapes, a can 3. | Automatic shading. The shades are kept as flat colours. |
| A line or connector with ends | A group: the stroke and each arrowhead | Connection points. Arrowheads become separate shapes. |
| A shape with text in it | One shape, text kept | |
| A text box | One shape with no fill and no stroke, text kept | |
| WordArt | A group of letter outlines | The text. The letters can be reshaped but not retyped. |

Text inside a shape stays editable after conversion.

## Cancel and Done {#cancel}

**Cancel** puts the original object back. **Done** keeps the converted shapes.

!!! Caution: After **Done** the conversion is one-way. To get the original back, undo.

## Not handled {#limits}

- Gradient and pattern fills, fill transparency, dash styles and shadows are not carried over.
- Images, video and charts cannot be converted.
""",
        see=["edit-shape", "round-corners", "outline-stroke-text", "edit-points-and-polylines"],
    ),

    # ------------------------------------------------------ Web Uploader and Add-on
    dict(
        slug="web-uploader", book="surfaces", kind="How to", nav="Web Uploader",
        title="Web Uploader",
        desc="Convert SVG files to Google Slides online with the Web Uploader: upload a batch, get a Drive file with one slide per SVG. Gradients kept, 7-day links.",
        applies=[AWEB],
        summary="The Web Uploader converts SVG files on a web page, with nothing to install. Upload one file or a batch and get a Google Drive link to a file with one slide per SVG, every path a native shape.",
        keys=["Web Uploader", "online converter", "batch conversion", "Google Drive link", "7-day links#keep", "Make a copy#keep", "gradients, keeping#differences"],
        body="""
>> To convert SVG files online
1. Open [svgslid.es/convert](/convert).
2. Drop your .svg files on the upload area, or click it to browse. Each file becomes one slide.
3. Optional: type a Google account address. The file is then shared straight to that account.
4. Click **Convert**. A link to the file in Google Drive appears.

@fig web-uploader | The Web Uploader page with a dashed upload area reading Drop SVG files here or click to browse, an optional Google account field and a Convert button | The Web Uploader.

## Keeping the file {#keep}

Links stay active for 7 days. After that the file is deleted.

>> To keep a converted file
1. Open the link.
2. In Google Drive, choose **File › Make a copy**.

The copy belongs to your account and does not expire.

## How it differs from the extension {#differences}

| | Web Uploader | Chrome extension |
|---|---|---|
| Where the result goes | A new file, one slide per SVG | The slide you have open |
| Gradients | Kept as gradients | First colour only |
| SVG text | Outlined into shapes. Not editable as text. | Not converted |
| Line icons that set the stroke on the whole SVG | Converted. Strokes become filled outline shapes. | Not converted |
| Where conversion runs | On the svgslid.es server | In your browser |
| Batch size | A batch | Up to 25 files per drop |

Clip paths, masks, patterns, filters and transparency do not come through on either. See [[svg-compatibility]].

## What happens to your files {#data}

Uploaded SVG files are held only while the request runs and are deleted when it finishes. The converted file is stored in Google Drive for 7 days and shared by link. See [[permissions-privacy#web-uploader]].
""",
        see=["add-on", "svg-compatibility", "permissions-privacy", "kb/web-uploader-link-expired", ("Guide: SVG to Google Slides converter", "/guides/svg-to-google-slides-converter")],
    ),
    dict(
        slug="add-on", book="surfaces", kind="How to", nav="Workspace Add-on",
        title="Workspace Add-on",
        desc="Insert SVG files into Google Slides with the SVG to Slides Workspace Add-on: pick files in a dialog inside Slides, copy, and paste them as editable vector shapes.",
        applies=[AADD],
        summary="The add-on inserts SVG files from a dialog inside Google Slides. Pick your files, copy, and paste. Every path lands as a native shape on the slide you have open.",
        keys=["Workspace Add-on", "add-on", "Google Workspace Marketplace", "Insert SVGs dialog"],
        body="""
>> To insert SVG files with the add-on
1. In Google Slides, choose **Insert SVGs** from the **Extensions** menu, or click the add-on's icon in the side panel.
2. Pick your .svg files. They convert as you select them.
3. Click **Copy**, or press <<Enter>>.
4. Press <<Command+V>>. The shapes land on the slide you have open.

@fig add-on-dialog | The add-on dialog titled Insert SVGs with four shape thumbnails, the line Ready, click below or press Enter to copy, and a Copy button | The add-on dialog. *Illustration.*

## Good to know {#notes}

- Select more than one file and they land side by side on the current slide.
- A gradient comes through as its first colour. For full gradients use the [[web-uploader]].
- The add-on is installed from the Google Workspace Marketplace: [svgslid.es/addon](/addon).

## What the add-on can access {#access}

| Access | Used for |
|---|---|
| The current presentation's page size | Sizing the inserted shapes to fit the slide. |
| Showing a dialog | The **Insert SVGs** dialog. |
| Calling the svgslid.es converter | Converting the files you select. |

The add-on has no access to Google Drive and does not read or change the content of your presentation through Google's API. The shapes are written to your clipboard and you paste them. See [[permissions-privacy#add-on]].
""",
        see=["web-uploader", "insert-svg", "how-shapes-reach-the-slide", "permissions-privacy"],
    ),
]

INCLUDES = {}
