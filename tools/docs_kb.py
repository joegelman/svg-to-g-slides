"""Docs content: Knowledge Base. One symptom per article, in the old form:
Symptoms, Cause, Resolution, Status, More information.

Messages quoted here are the extension's own (shape-tools.js, content.js, 1.3.0).
Compatibility facts come from tools/site_specs.py COMPAT.
"""
import html

A13 = "SVG to Slides Chrome extension, version 1.3.0"
A12 = "SVG to Slides Chrome extension, versions 1.2.0 and 1.3.0"
AALL = "SVG to Slides Chrome extension, versions 1.0.0 through 1.3.0"
AWEB = "SVG to Slides Web Uploader"
AADD = "SVG to Slides Workspace Add-on for Google Slides"


def kb(num, slug, prefix, title, desc, applies, q, a, body, see, keys):
    return dict(slug="kb/" + slug, book="kb", kind="Article", nav=f"{prefix}: {title}",
                title=f"{prefix}: {title}", desc=desc, applies=applies, summary=a,
                kb=dict(id=f"Q{num}", q=q, a=a), body=body, see=see, keys=keys, howto=prefix == "HOWTO",
                head=f"{title} | SVG to Slides")


ARTICLES = [
    kb(100101, "svg-becomes-a-flat-image", "PRB", "An SVG placed in Google Slides becomes a flat image",
       "Why an SVG inserted into Google Slides turns into a blurry, uneditable picture, and how to insert it as native, editable vector shapes instead.",
       ["Google Slides", AALL, AWEB, AADD],
       "Why does my SVG turn into a flat image in Google Slides?",
       "Google Slides has no SVG import, so an SVG placed on a slide is flattened into a picture. To keep it as vectors, insert it with SVG to Slides: drag the file onto the slide with the Chrome extension, or convert it with the Web Uploader.",
       """
## Symptoms {#symptoms}

An SVG placed on a slide without SVG to Slides behaves as one picture:

- It blurs or shows pixels when enlarged.
- Its parts cannot be selected or recoloured.
- Slides offers it picture options only.

## Cause {#cause}

Google Slides does not keep SVG files as vectors. It flattens the drawing into a picture on the way in.

## Resolution {#resolution}

Insert the file as native shapes with one of the three products.

| Product | Do this |
|---|---|
| Chrome extension | Drag the .svg file onto the slide and click where it goes. See [[insert-svg]]. |
| Web Uploader | Upload the file and open the Drive link. See [[web-uploader]]. |
| Workspace Add-on | Choose **Insert SVGs** from the Extensions menu. See [[add-on]]. |

## Status {#status}

This is how Google Slides behaves.

## More information {#more}

There are two manual routes that need no extension: convert the SVG to EMF, open it in Google Drawings and copy the shapes across; or insert it in PowerPoint, convert it to a shape, save, and open the file in Slides. The guide [How to insert an SVG into Google Slides](/guides/insert-svg-into-google-slides) walks through both.
""",
       ["insert-svg", "overview", "svg-compatibility", ("Guide: Does Google Slides support SVG?", "/guides/does-google-slides-support-svg"), ("Guide: SVG vs PNG in Google Slides", "/guides/svg-vs-png-google-slides")],
       ["flat image", "blurry SVG", "pixelated SVG", "PNG, SVG becomes", "EMF route#more", "PowerPoint route#more"]),

    kb(100102, "gradient-becomes-solid-colour", "PRB", "A gradient arrives as one solid colour",
       "SVG gradients inserted into Google Slides with the SVG to Slides extension or add-on arrive as a single solid colour. Cause and the way to keep the gradient.",
       [AALL, AADD],
       "Why did my SVG gradient become a solid colour in Google Slides?",
       "The Chrome extension and the add-on fill each shape with the gradient's first colour. To keep gradients, convert the file with the Web Uploader, which carries them through.",
       """
## Symptoms {#symptoms}

A shape that has a linear or radial gradient in the SVG lands with one flat colour. A radial gradient with a white centre lands white.

## Cause {#cause}

The extension and the add-on write each shape with a single fill. They use the first colour stop of the gradient.

## Resolution {#resolution}

>> To keep the gradient
1. Convert the file with the [[web-uploader]]. It keeps linear and radial gradients.
2. Open the Drive link and make a copy of the file.
3. Copy the shapes from the copy into your presentation.

## Status {#status}

This is a known limit of the extension and the add-on in the versions listed above.
""",
       ["web-uploader", "svg-compatibility#partly", "how-conversion-works#outputs"],
       ["gradient becomes solid", "radial gradient", "linear gradient"]),

    kb(100103, "text-missing-after-insert", "PRB", "Text in an SVG does not appear on the slide",
       "Text inside an SVG is missing after inserting it into Google Slides with the SVG to Slides extension. Cause and two ways to bring the text across.",
       [AALL, AADD],
       "Why is the text from my SVG missing in Google Slides?",
       "The extension and the add-on do not convert SVG text elements. Convert the text to outlines in your design tool before exporting, or use the Web Uploader, which outlines text into shapes.",
       """
## Symptoms {#symptoms}

The shapes of the SVG land on the slide. Words that were text in the SVG are not there.

## Cause {#cause}

The extension and the add-on convert paths and basic shapes. They do not convert `<text>` elements.

## Resolution {#resolution}

Use either method.

- In your design tool, convert the text to outlines, then export the SVG again. The letters are then paths, and paths convert.
- Convert the file with the [[web-uploader]]. It outlines text on the server.

Either way the words arrive as shapes. They look the same but cannot be retyped. To have editable text, add a Slides text box.

## Status {#status}

This is a known limit of the extension and the add-on.
""",
       ["svg-compatibility#not-converted", "web-uploader", "outline-stroke-text"],
       ["text missing", "SVG text", "fonts in SVG"]),

    kb(100104, "line-icon-inserts-nothing", "PRB", "A line icon inserts nothing",
       "Stroke-based SVG icons in the Lucide and Feather style insert nothing into Google Slides with the SVG to Slides extension. Cause and resolution.",
       [AALL, AADD],
       "Why does my line icon SVG insert nothing in Google Slides?",
       "Icons that set their stroke once on the root svg element, or use stroke=\"currentColor\", are not converted by the extension. Convert them with the Web Uploader, or outline the strokes in your design tool before exporting.",
       """
## Symptoms {#symptoms}

You drop a line icon and click to place it. Nothing lands on the slide. Icon sets drawn with strokes, in the style of Lucide and Feather, are the usual case.

## Cause {#cause}

These icons do not put a stroke on each path. They set it once on the root `<svg>` element, often as `stroke="currentColor"`. The extension's converter does not pick up a stroke set there, and it does not resolve `currentColor`, so it finds nothing to draw.

Strokes written on the elements themselves, with a stated colour, do convert. They land as filled outline shapes.

## Resolution {#resolution}

Use either method.

- Convert the icons with the [[web-uploader]]. It converts strokes set on the whole SVG into filled outline shapes. A `currentColor` stroke comes out black, and you can recolour it in Slides.
- In your design tool, outline the strokes, then export again.

## Status {#status}

This is a known limit of the extension and the add-on. Test files 04 and 17 on the [Specs page](/specs#compatibility) cover it.
""",
       ["svg-compatibility", "web-uploader", "how-conversion-works#stages", ("Guide: SVG logos and icons in Slides themes", "/guides/svg-logos-icons-google-slides")],
       ["line icon", "stroke icons", "Lucide", "Feather", "currentColor", "nothing is inserted"]),

    kb(100105, "colours-arrive-black", "PRB", "Shapes arrive black",
       "SVG shapes arrive black in Google Slides when their colours come from CSS classes, hsl() values or pattern fills. Causes and how to export so colours convert.",
       [AALL, AADD, AWEB],
       "Why are my SVG shapes black after inserting them into Google Slides?",
       "Colours set by CSS classes in a style block, colours written as hsl(), and pattern fills are not read by the converter, so those shapes arrive black. Export with colours written on each element, or recolour the shapes in Slides.",
       """
## Symptoms {#symptoms}

The shapes land with the right outlines but filled black.

## Cause {#cause}

| In the SVG | Result |
|---|---|
| Colours set by CSS classes in a `<style>` block, as some Illustrator exports write them | Shapes kept, colours black. |
| Colours written as `hsl()` | Black. `rgb()`, named colours and short hex values are exact. |
| A pattern fill | Shape kept, filled black. |

## Resolution {#resolution}

- In your design tool's SVG export settings, choose the option that writes each colour on its own element instead of in a style sheet. It is often called presentation attributes.
- Or select the shapes in Slides and set their colours with the fill picker. Each path is its own shape.

## Status {#status}

This is a known limit in all three products.
""",
       ["svg-compatibility#partly", "quick-start#next", ("Guide: Recolor SVGs in Google Slides", "/guides/recolor-svg-in-google-slides")],
       ["black shapes", "CSS classes", "Illustrator export", "hsl()", "pattern fill"]),

    kb(100106, "press-command-v-prompt", "INFO", "The extension asks you to press COMMAND+V",
       "Why the SVG to Slides extension sometimes shows a prompt to press Command+V or Ctrl+V in Google Slides, and what to do.",
       [A12],
       "Why does SVG to Slides ask me to press Command+V?",
       "The extension hands shapes to Google Slides the way a paste does. If Slides does not accept them, the extension places the shapes on your clipboard and asks you to press COMMAND+V to finish.",
       """
## Summary {#summary}

Since version 1.2.0 a click inserts the shapes directly. The prompt is the fallback for when that does not go through.

## More information {#more}

| You see | Do this |
|---|---|
| A prompt to press <<Command+V>> after placing an SVG | Press <<Command+V>>. The shapes land. |
| "Press ⌘V to finish" after a shape command | Press <<Command+V>>. |
| "Couldn't replace the shapes. Delete them, then press ⌘V." | Delete the selected originals, then press <<Command+V>>. The result is on your clipboard. |
| "Slides didn't accept the result. Press ⌘Z to undo." | Press <<Command+Z>> and try the command again. |

On Windows the prompts name <<Ctrl>> in place of <<Command>>.

In versions 1.0.0 and 1.0.1 every insert ended with <<Command+V>>. That was the normal flow in those versions.
""",
       ["insert-svg#fallback", "how-shapes-reach-the-slide"],
       ["COMMAND+V prompt", "CTRL+V prompt", "paste prompt"]),

    kb(100107, "more-than-25-files", "PRB", "Nothing is inserted when more than 25 files are dropped",
       "Dropping more than 25 SVG files onto Google Slides with the SVG to Slides extension inserts nothing. The limit, the reason, and how to convert a larger batch.",
       [AALL],
       "How many SVG files can I drop into Google Slides at once?",
       "The extension inserts up to 25 SVG files per drop. A larger drop inserts nothing and shows a message. Drop the files in batches of 25, or use the Web Uploader, which makes one slide per SVG.",
       """
## Symptoms {#symptoms}

You drag more than 25 .svg files onto a slide. A message says there are too many files at once, and nothing lands.

## Cause {#cause}

Files from one drop are laid out in a grid on the current slide. Past 25 files the grid stops being useful, so the extension refuses the drop.

## Resolution {#resolution}

- Drop the files in batches of 25 or fewer.
- Or convert the whole set with the [[web-uploader]]. It makes a file with one slide per SVG.

## Status {#status}

This behaviour is by design.
""",
       ["insert-svg#several", "web-uploader", "limits#inserting"],
       ["too many files", "25 files", "batch"]),

    kb(100108, "edit-points-missing", "INFO", "Slides' own Edit points is offered for some inserted shapes only",
       "Google Slides' Edit points command works on inserted SVG shapes with straight edges and not on curved ones. Why, and how to edit the points of any shape.",
       [A12],
       "Why can't I use Edit points on my inserted SVG shape in Google Slides?",
       "Slides' own Edit points works only on polylines. Inserted shapes with one outline and straight segments land as polylines. Curved shapes and shapes with holes do not, because Slides' point editor would damage them. Use Edit Shape for those.",
       """
## Summary {#summary}

After inserting an SVG, some shapes offer Slides' **Edit points** and enter point editing on a double-click. Others give a text cursor on a double-click and have no **Edit points**.

## More information {#more}

Slides' point editor works with straight segments only. A shape is inserted as a polyline, which that editor accepts, only if it has a single outline, only straight segments, and no more than 150 points.

Every other shape is inserted as a custom shape. To edit its points, double-click it and click **Edit Shape**. See [[edit-shape]].

The tests behind this rule are described in [[edit-points-and-polylines]].
""",
       ["edit-points-and-polylines", "edit-shape"],
       ["Edit points missing", "polyline"]),

    kb(100109, "undo-takes-several-presses", "PRB", "COMMAND+Z undoes only part of a combine or outline",
       "After a combine, outline or mask in Google Slides with SVG to Slides, one press of Command+Z sometimes undoes only part of the change. Cause and resolution.",
       [A13],
       "Why does undo only partly reverse a combine in Google Slides?",
       "A combine, outline or mask is several steps inside Slides. The extension undoes them in one press only while the slide is as it left it. If you changed the slide afterwards, Slides' own undo takes over and goes one step per press. Keep pressing COMMAND+Z until the original returns.",
       """
## Symptoms {#symptoms}

You press <<Command+Z>> after a Union, an Outline or a Mask. Shapes disappear or reappear one at a time and the slide passes through states you did not make.

## Cause {#cause}

The change reached Slides as several steps: remove the originals, insert the result, restore its place in the stack. The extension undoes all of them in one press, but only right after the change. Once you change the slide yourself, the extension stops, because pressing undo for you could remove your own work.

## Resolution {#resolution}

Keep pressing <<Command+Z>> until the slide is back to where you want it. Nothing is lost. The steps are in Slides' own history.

## Status {#status}

This behaviour is by design.

## More information {#more}

In version 1.2.0, which had no one-press undo, undoing an Edit Shape session always took several presses.
""",
       ["undo-redo", "undo-and-still-copy#undo"],
       ["undo partly", "several presses"]),

    kb(100110, "layer-names-missing", "PRB", "Layer names are missing on another computer",
       "Layer names set in the SVG to Slides Layers panel do not appear for other people or on another computer. They are stored on the computer where they were set.",
       [A13],
       "Why don't my layer names show up on another computer?",
       "Layer names are kept in Chrome on the computer where you set them. They are not saved in the presentation, so other people and other computers show the default names.",
       """
## Symptoms {#symptoms}

You renamed objects in the Layers panel. On another computer, or for a colleague who opens the same presentation, the rows show their default names such as "Shape", "Image" or "Group of 3".

## Cause {#cause}

The extension has no way to save a name inside the presentation without changing the objects. It keeps the names in Chrome's storage on the computer you used.

## Resolution {#resolution}

There is none. Rename the layers on the other computer if you need the names there.

## Status {#status}

This behaviour is by design.

## More information {#more}

The same applies to snapping settings, the memory that restores outlined text, and stroke position memory. Objects hidden with the eye are hidden only in your view. See [[permissions-privacy#storage]].
""",
       ["layers#stored", "permissions-privacy#storage", "limits#local"],
       ["layer names missing", "another computer"]),

    kb(100111, "object-greyed-with-m", "INFO", "An object in Layers is greyed and marked M",
       "Objects shown greyed with an M badge in the SVG to Slides Layers panel belong to the slide's layout or master. How to select and edit them in the theme builder.",
       [A13],
       "What does the M badge mean in the SVG to Slides Layers panel?",
       "The M marks a theme object: one that belongs to the slide's layout or master. It cannot be changed on the slide. Click its row twice to open Slides' theme builder on the layout or master that holds it.",
       """
## Summary {#summary}

Some rows in the Layers panel are grey with an **M** badge, and clicking the object on the slide does nothing.

## More information {#more}

Slides draws layout and master objects on every slide that uses them. They can be edited only in the theme builder.

>> To edit the object
1. Click its row in the Layers panel.
2. Click the row again within 5 seconds. The theme builder opens with the object selected.
3. Press <<Option+Shift+M>> to return to the slide.

If the Layers panel says it could not select an object that is not marked **M**, click the object on the slide instead.
""",
       ["theme-objects", "layers"],
       ["M badge", "greyed layer", "cannot select an object"]),

    kb(100112, "cannot-mask-image", "PRB", "Mask image with shape shows a message and does not mask",
       "Messages shown by Mask image with shape in SVG to Slides for Google Slides, what each means, and how to fix the selection, rotated images and text masks.",
       [A13],
       "Why won't Mask image with shape work in Google Slides?",
       "Mask image with shape needs exactly one image and one shape or group selected, an image that is not rotated, and a mask that is a shape and not live text. The message under the toolbar says which condition failed.",
       """
## Symptoms {#symptoms}

You press <<Option+Shift+K>>. The picture is not masked and a message appears under the toolbar.

## Cause and resolution {#resolution}

| Message | Cause | Do this |
|---|---|---|
| Select an image and a shape to mask it with | The selection has no image, or no shape. | Select the picture, then <<Shift>>-click the shape. |
| Select an image and the shape to mask it with (two objects) | More than two objects are selected. | Group the shapes first with <<Command+Option+G>>, then select the image and the group. |
| Straighten the image first: masking a rotated image isn't supported yet | The image is rotated. | Set the image's rotation back to 0, mask it, then rotate the result. |
| That shape is too thin to mask with | The shape has no width or no height, as a straight line has. | Use a shape that has both. |
| That shape has nothing to mask with | The object has no outline the extension can cut with. | Use a different shape. |
| Outline the text first (⌥⌘T), then mask with it | The mask is live text. | Press <<Option+Command+T>> to outline the text, then mask. |
| The mask has to be a shape (the other object is an image too) | Both selected objects are images. | Select one image and one shape. |
| Couldn't get the picture from Slides to mask it | Slides did not hand over the picture. | Try again. If it repeats, copy and paste the image, then mask the pasted copy. |

## Status {#status}

Masking rotated images is not supported in version 1.3.0.
""",
       ["mask-image", "outline-stroke-text#text", "limits#shape-tools"],
       ["mask error", "rotated image", "Straighten the image first"]),

    kb(100113, "outline-text-font", "PRB", "Outline text reports that it could not get the font",
       "Outline text in SVG to Slides needs the font's letter shapes. What to do when it reports that it could not get the font in Google Slides.",
       [A13],
       "Why does Outline text say it couldn't get the font?",
       "Outline text reads letter shapes from the font. It downloads Google fonts from Google Fonts and asks Chrome for access to fonts installed on your computer. If neither works, allow font access when Chrome asks, or set the text in a Google font and outline it again.",
       """
## Symptoms {#symptoms}

You press <<Option+Command+T>>. The text is not outlined, and a message says the extension could not get the font and suggests allowing font access or using a Google font.

## Cause {#cause}

The font is not one that Google Fonts serves, and the extension could not read it from your computer. Either Chrome's font access prompt was declined, or the font is not installed.

## Resolution {#resolution}

Use either method.

- Press <<Option+Command+T>> again and choose **Allow** when Chrome asks for access to your fonts.
- Change the text to a Google font, then outline it.

## More information {#more}

For some system fonts that cannot be downloaded, the extension outlines the text with a font that has the same letter widths, and a note names the font it used. The outline then matches the text's spacing but not every letter shape.
""",
       ["outline-stroke-text#fonts", "permissions-privacy#network"],
       ["font access", "Couldn't get the font", "Google font"]),

    kb(100114, "web-uploader-link-expired", "PRB", "A Web Uploader link stops working after 7 days",
       "Google Drive links from the SVG to Slides Web Uploader are deleted after 7 days. How to keep a converted file.",
       [AWEB],
       "Why did my SVG to Slides Drive link stop working?",
       "Files made by the Web Uploader are deleted after 7 days. To keep one, open the link within that time and choose File, Make a copy in Google Drive. If the link has expired, convert the SVG files again.",
       """
## Symptoms {#symptoms}

A Drive link you received from the Web Uploader no longer opens.

## Cause {#cause}

Converted files are stored for 7 days, then deleted by a daily clean-up.

## Resolution {#resolution}

>> To keep a converted file
1. Open the link within 7 days.
2. Choose **File › Make a copy**. The copy is yours and does not expire.

If the link has already expired, upload the SVG files again at [svgslid.es/convert](/convert).

## Status {#status}

This behaviour is by design.
""",
       ["web-uploader#keep", "permissions-privacy#web-uploader"],
       ["expired link", "7 days", "Drive link"]),

    kb(100115, "shapes-land-away-from-pointer", "FIX", "Inserted shapes landed away from the pointer in versions 1.0.0 and 1.0.1",
       "In SVG to Slides 1.0, inserted shapes could land away from the pointer when Google Slides was zoomed or its layout changed. Fixed in version 1.2.0.",
       ["SVG to Slides Chrome extension, versions 1.0.0 and 1.0.1"],
       "Why did my SVG land in the wrong place on the slide?",
       "Versions 1.0.0 and 1.0.1 estimated the position from the size of the window, which was off when Slides was zoomed or its panels were resized. Version 1.2.0 measures the slide itself and centres the graphic on the point you click.",
       """
## Symptoms {#symptoms}

In version 1.0.0 or 1.0.1 the shapes land some distance from where you clicked. The error grows when Slides is zoomed in, or when the filmstrip or toolbar is not at its default size.

## Cause {#cause}

Those versions did not read the slide's position. They estimated it from the window size, assuming Slides' default layout.

## Resolution {#resolution}

Update to version 1.2.0 or later. See [[install#updates]].

## Status {#status}

Fixed in version 1.2.0. The extension now measures the slide you have open. In testing, an inserted graphic was centred within 2 pixels of the point clicked.

## More information {#more}

Version 1.2.0 also corrects a related fault in which visiting another slide first could throw off both placement and the editor.
""",
       ["release-notes/1-2-0", "insert-svg#size"],
       ["wrong place", "placement error"]),

    kb(100116, "toolbar-does-not-appear", "PRB", "The toolbar does not appear",
       "The SVG to Slides toolbar is missing in Google Slides. Check the version, reload the tab, and see the cases in which the toolbar hides itself.",
       [A13],
       "Why can't I see the SVG to Slides toolbar in Google Slides?",
       "The toolbar is part of version 1.3.0 and shows only on a Google Slides presentation open for editing. Check the installed version, reload the tab, and look for the round button at the left edge of the slide canvas: the toolbar starts closed.",
       """
## Symptoms {#symptoms}

There is no round button and no toolbar at the left of the slide.

## Cause and resolution {#resolution}

| Cause | Do this |
|---|---|
| The installed version is earlier than 1.3.0. | Check the version. See [[install#check-version]]. Chrome updates on its own once the Chrome Web Store has published the new version. |
| The tab was open before the extension was installed or updated. | Reload the tab. |
| The toolbar is closed. | It is one round button when closed. Click it, or press <<Option+\\>>. |
| Edit Shape is open. | The editor's own toolbar takes the same place. Click **Done** or **Cancel**. |
| Slides is in full-screen view. | Leave full screen. |
| The window is very small. | Make the window larger. The toolbar hides when the canvas is too small to hold it. |
| The page is not a presentation open for editing. | The extension runs only in the Slides editor. |
""",
       ["toolbar", "install", "kb/which-version"],
       ["toolbar missing", "no toolbar"]),

    kb(100117, "which-version", "HOWTO", "Find which version of the extension is installed",
       "How to check the installed version of the SVG to Slides Chrome extension, and how to tell versions 1.0, 1.2 and 1.3 apart on the slide.",
       [AALL],
       "How do I check which version of SVG to Slides I have?",
       "Type chrome://extensions in Chrome's address bar and find SVG to Slides. The version number is beside the name. On the slide, version 1.3.0 shows a round toolbar button at the left of the canvas.",
       """
>> To check the version
1. In Chrome's address bar, type `chrome://extensions` and press <<Enter>>.
2. Find **SVG to Slides**. The version number is shown beside the name.

## Telling versions apart on the slide {#apart}

| Version | What you see in Google Slides |
|---|---|
| 1.3.0 | A round button at the left edge of the slide canvas. It opens the toolbar. |
| 1.2.0 | No toolbar. Double-clicking a shape shows an **Edit Shape** button. |
| 1.0.0, 1.0.1 | Neither. Dropping an SVG ends with a prompt to press <<Command+V>>. |

## More information {#more}

Chrome installs new versions on its own, usually within a few hours of their release. See [[install#updates]] and [[release-notes]].
""",
       ["install#check-version", "release-notes"],
       ["version, finding"]),
]


def kblist_html(cx):
    import site_docs as D
    rows = "".join(
        f'<tr id="{a["kb"]["id"].lower()}"><td style="white-space:nowrap">{a["kb"]["id"]}</td>'
        f'<td><a class="x" href="{D.url(a["slug"])}">{html.escape(a["title"])}</a></td></tr>' for a in ARTICLES)
    return f'<div class="tw"><table class="t"><thead><tr><th>Article ID</th><th>Title</th></tr></thead><tbody>{rows}</tbody></table></div>'


def kblist_md(cx):
    import site_content as C
    import site_docs as D
    return "\n".join(f"- {a['kb']['id']}: [{a['title']}]({C.SITE}{D.url(a['slug'])}.md)" for a in ARTICLES)


INCLUDES = {"kblist": {"html": kblist_html, "md": kblist_md, "anchors": {a["kb"]["id"].lower() for a in ARTICLES}}}

TOPICS = [
    dict(
        slug="kb", book="kb", kind="Article list", nav="All articles",
        title="Knowledge Base",
        desc="The SVG to Slides Knowledge Base: numbered articles on known problems inserting and editing SVGs in Google Slides, each with symptoms, cause and resolution.",
        applies=["SVG to Slides Chrome extension", "SVG to Slides Web Uploader", "SVG to Slides Workspace Add-on"],
        summary="Each article covers one symptom: what you see, why it happens, and what to do. Articles are numbered so that they can be cited.",
        keys=["Knowledge Base", "troubleshooting", "problems", "error messages"],
        howto=False,
        body="""
@@kblist

## Kinds of article {#kinds}

| Prefix | Meaning |
|---|---|
| PRB | A problem and its cause. The behaviour may be by design. |
| FIX | A problem that a later version corrects. |
| INFO | Background on how something behaves. |
| HOWTO | A procedure. |

## If your problem is not listed {#not-listed}

Check [[limits]] and [[svg-compatibility]]. If a file does not convert, send the .svg file itself to the address on the [Support](/support) page. Most conversion problems are specific to how one file was exported.
""",
        see=["limits", "svg-compatibility", "conventions#kb", ("Support", "/support")],
    ),
] + ARTICLES
