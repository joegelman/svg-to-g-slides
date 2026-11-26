"""Single source of truth for svgslid.es keyword landing pages + agent-facing text.

Every claim here is drawn from existing site copy (index, guide, features, convert,
privacy) or from the code (25-file drop limit, no usage cap). Don't add claims that
aren't backed by one of those.
"""

CWS = "https://chromewebstore.google.com/detail/svg-to-slides/bdhhnakellmdnbgbdokiojipaebdeioi"
SITE = "https://svgslid.es"
MARKETPLACE = "https://workspace.google.com/marketplace/app/svg_%E2%9E%94_slides/477942279738"
GITHUB = "https://github.com/joegelman/svg-to-g-slides"

FREE_LINE = "Free forever. Every feature, no daily cap, no account, no Pro tier."

# Keyword landing pages. Order = footer/related order.
PAGES = [
    {
        "slug": "svg-vs-png-google-slides",
        "nav": "SVG vs PNG in Google Slides",
        "title": "SVG vs PNG in Google Slides: Keep It an Editable Vector",
        "desc": "Google Slides flattens SVGs into images. See what you lose, and how to keep every path as a native, editable, recolourable Slides shape instead. Free.",
        "h1": "SVG vs PNG in Google Slides&trade;",
        "lede": "Drop an SVG onto a Slides canvas the normal way and Google flattens it into a raster image. Here's what that costs you, and how to avoid it.",
        "answer": "When Google Slides flattens an SVG it becomes a single image that blurs when resized and can't be recoloured or edited. SVG to Slides converts every path into Slides' own native shape format instead, so the result behaves like a shape you drew yourself.",
        "img_alt": "SVG vs PNG in Google Slides: a flattened PNG that blurs when resized next to an SVG converted into sharp, editable vector shapes",
        "lottie": "svgslides_recolor.json",
        "compare": [
            ("Blurs or pixelates when resized", "Resizes at any size, always crisp"),
            ("One flattened image, single object", "Every path is its own selectable shape"),
            ("Can't recolour without re-exporting", "Recolour any shape directly in Slides"),
            ("Can't animate individual elements", "Animate each shape independently"),
            ("Can't edit points or paths", "Double-click &rarr; Edit Shape to move points and curves on the slide"),
        ],
        "sections": [
            ("How it stays a vector", [
                "Every <code>&lt;path&gt;</code> in your SVG is converted directly into Google Slides' own native shape format. It isn't re-rendered as an image and it isn't a third-party embed.",
                "The result behaves exactly like a shape you drew in Slides yourself: resizable, recolourable, editable.",
            ]),
        ],
        "cards": [
            ("Chrome extension", "Drag an SVG file straight onto an open Slides tab and drop it in place. No dialog, no upload step.", CWS, "Add to Chrome &mdash; free"),
            ("Web Uploader", "Upload one or more SVGs and get back a Google Drive link to a ready-made Slides file, one slide per SVG.", "/convert", "Open the converter"),
            ("Google Slides add-on", "Insert SVGs into a presentation you're already editing, from a dialog inside Slides itself.", "/addon", "Get the add-on"),
        ],
        "faq": [
            ("Does Google Slides support SVG natively?", "Not as an editable format. Slides rasterizes an inserted SVG into a flattened image, so you lose the ability to edit individual paths or recolour parts of it. SVG to Slides converts it into Slides' native shape format instead, so it stays fully editable."),
            ("What happens to gradients and complex curves?", "Solid fills and strokes convert cleanly. Arc commands are converted into smooth curves. Gradients come through in the online converter and, since version 1.4.0, in the Chrome extension. In the add-on they collapse to a single solid colour. Tested results are on the <a href=\"/specs#compatibility\">specs page</a>."),
            ("Is my file uploaded anywhere?", "Depends on the surface. The Chrome extension converts every file inside your browser, and nothing is uploaded. The online converter and add-on send the file to our backend for conversion. See the <a href=\"/privacy\">privacy policy</a> for specifics."),
            ("Is it free?", "Yes. " + FREE_LINE),
        ],
        "related": ["does-google-slides-support-svg", "insert-svg-into-google-slides", "recolor-svg-in-google-slides"],
    },
    {
        "slug": "insert-svg-into-google-slides",
        "nav": "Insert an SVG into Google Slides",
        "title": "How to Insert an SVG into Google Slides, Step by Step",
        "desc": "Insert or import an SVG into Google Slides as editable vector shapes. Drag it in with a free Chrome extension, or use the PowerPoint or Google Drawings route.",
        "h1": "How to insert an SVG into Google Slides&trade;",
        "lede": "Drag the SVG file onto your slide. SVG to Slides converts every path into a native Google Slides shape you can select, recolour, and resize. Below: the extension, the online uploader, and the two manual workarounds.",
        "answer": "Google Slides doesn't support SVG files, so you can't upload one as an editable graphic. To insert an SVG into Google Slides, install the free SVG to Slides Chrome extension, open your presentation, and drag the .svg file onto a slide. Each path becomes its own native Slides shape.",
        "img_alt": "Inserting an SVG into Google Slides: an SVG file dragged onto a slide with the SVG to Slides Chrome extension, placed, clicked into place",
        "lottie": "svgslides_drop.json",
        "howto": [
            ("Install the free Chrome extension.", "Add SVG to Slides from the Chrome Web Store. No account required."),
            ("Open your presentation in Google Slides.", "Any existing or new deck."),
            ("Drag the SVG file onto a slide.", "Click where it goes. It lands there and its paths become editable shapes. Up to 25 SVG files per drop."),
        ],
        "sections": [
            ("Reshape it after you insert it", [
                "Double-click any shape and click <b>Edit Shape</b>. A vector editor opens on the slide at the shape&rsquo;s exact size, so you can drag its points and curve handles, add or remove points, round corners, and undo as you go. Click <b>Done</b> and the shape updates in place.",
                "It works on Slides&rsquo; own shapes, lines and WordArt too. <a href=\"/vector-editor\">Every editing tool</a>.",
            ]),
            ("Import an SVG without installing anything", [
                "<b>Web uploader.</b> Upload one or more SVG files at <a href=\"/convert\">svgslid.es/convert</a> and get a Google Drive link to a Slides-ready file, one slide per SVG. Good for bulk conversion.",
                "<b>Google Slides add-on.</b> Insert SVGs from a dialog inside Slides, without leaving the tab. <a href=\"/addon\">Get the add-on</a>.",
            ]),
            ("Insert SVG icons into Google Slides", [
                "Download icons as SVG files from any icon library and drag them onto your slide, up to 25 per drop.",
                "Each icon arrives as native shapes with no background box, so you can recolour it with the fill picker to match your theme.",
                "For a whole icon set, upload it at <a href=\"/convert\">svgslid.es/convert</a> and get one slide per icon, ready to copy from.",
            ]),
            ("The manual workaround: EMF and Google Drawings", [
                "Convert the SVG to an EMF or WMF file with a desktop or online converter.",
                "Upload the EMF or WMF file to Google Drive.",
                "Open it with Google Drawings.",
                "Copy the shapes and paste them into your Google Slides presentation.",
            ], "ol", "It works, but it's four steps for every file."),
            ("The Microsoft PowerPoint route", [
                "In PowerPoint, choose Insert &rarr; Pictures and pick the SVG file.",
                "Right-click the graphic and choose Convert to Shape.",
                "Save the presentation as .pptx and upload it to Google Drive.",
                "Open it with Google Slides and copy the shapes into your deck.",
            ], "ol", "It needs a PowerPoint licence and a round trip through Drive for every graphic."),
        ],
        "faq": [
            ("How do I import an SVG into Google Slides?", "Install the free SVG to Slides Chrome extension and drag the SVG file onto a slide, or upload it at svgslid.es/convert. Both turn every path into a native, editable Slides shape."),
            ("Can I upload an SVG to Google Slides directly?", "Not as an editable graphic. Without a converter, your options are to flatten it into a PNG or take the long way through EMF conversion, Google Drawings, and copy-paste. SVG to Slides converts the file into native Slides shapes instead."),
            ("Can I insert SVG icons into Google Slides?", "Yes. Drag up to 25 SVG icons onto a slide at once. Each one becomes editable shapes you can recolour and resize without losing quality."),
            ("How many SVGs can I insert at once?", "Up to 25 per drop with the Chrome extension. For larger batches, use the bulk converter at svgslid.es/convert."),
            ("Does it cost anything?", FREE_LINE),
            ("Is my file uploaded anywhere?", "The Chrome extension converts every file inside your browser, and nothing is uploaded. The web converter and add-on send the file to our backend for conversion."),
        ],
        "related": ["does-google-slides-support-svg", "svg-to-google-slides-converter", "recolor-svg-in-google-slides"],
    },
    {
        "slug": "does-google-slides-support-svg",
        "nav": "Does Google Slides support SVG?",
        "title": "Does Google Slides Support SVG? What Happens to Your File",
        "desc": "Google Slides doesn't keep SVGs as editable vectors. Here's what happens to your file, and how to insert SVGs as native, recolorable shapes instead.",
        "h1": "Does Google Slides&trade; support SVG?",
        "lede": "Not as an editable format. Here's why, what happens to your file, and which SVG features survive conversion.",
        "answer": "No. Google Slides doesn't keep SVG files as editable vectors. Your options are to flatten the SVG into a PNG, or convert it through EMF and Google Drawings. SVG to Slides converts the file into Slides' native shape format, so it stays editable.",
        "img_alt": "Does Google Slides support SVG? An SVG file shown as editable vector shapes in a Google Slides presentation",
        "lottie": "svgslides_scale.json",
        "compare": [
            ("Blurs or pixelates when resized", "Resizes at any size, always crisp"),
            ("One flattened image, single object", "Every path is its own selectable shape"),
            ("Can't recolour without re-exporting", "Recolour any shape directly in Slides"),
            ("Can't animate individual elements", "Animate each shape independently"),
            ("Can't edit points or paths", "Double-click &rarr; Edit Shape to move points and curves on the slide"),
        ],
        "sections": [
            ("Why Google Slides can't keep an SVG", [
                "Slides builds everything from its own shapes, text boxes and images. It has no SVG import, so an SVG can only arrive as an image.",
                "An image is one object. You can't select its parts, recolour them, or edit their points.",
                "Resizing an image resizes its pixels, so edges blur.",
                "To stay editable, the SVG's paths have to become Slides' own shape format. That's the conversion SVG to Slides does.",
            ]),
            ("Which SVG features survive conversion", [
                "Paths, basic shapes, arcs, transforms and even-odd cut-outs convert everywhere.",
                "Gradients and text convert on the web uploader, not in the extension or add-on.",
                "Clip paths, masks, patterns, filters and transparency are dropped. <a href=\"/specs#compatibility\">Full results for 20 tested SVG features</a>.",
            ]),
        ],
        "faq": [
            ("Can you import an SVG into Google Slides?", "Not as editable vector shapes. Install the SVG to Slides Chrome extension and drag the file onto a slide, or upload it at svgslid.es/convert. Both turn every path into a native Slides shape."),
            ("Why does my SVG look blurry in Google Slides?", "It's been flattened into a raster image, so it pixelates when you resize it. Converted with SVG to Slides, it stays a vector and every edge stays sharp."),
            ("What happens to gradients and complex curves?", "Solid fills and strokes convert cleanly. Arc commands are converted into smooth curves. Gradients come through in the online converter and, since version 1.4.0, in the Chrome extension. In the add-on they collapse to a single solid colour. Tested results are on the <a href=\"/specs#compatibility\">specs page</a>."),
            ("Do the converted shapes work in Google Drawings?", "Yes. The native shapes also work in Google Drawings."),
        ],
        "related": ["insert-svg-into-google-slides", "svg-to-google-slides-converter", "svg-logos-icons-google-slides"],
    },
    {
        "slug": "svg-to-google-slides-converter",
        "nav": "SVG to Google Slides converter",
        "title": "SVG to Google Slides Converter: Free Online Tool and Extension",
        "desc": "Convert SVG files into native, editable Google Slides shapes. Free Chrome extension, online converter, and Slides add-on. No account, no daily cap, no Pro tier.",
        "h1": "SVG to Google Slides&trade; converter",
        "lede": "Three ways to turn SVG files into native, editable Slides shapes, and how to pick the right one. All free.",
        "answer": "SVG to Slides converts SVG files into native, editable Google Slides shapes. Use the Chrome extension to drop files straight onto a slide, or the web converter to turn a batch of SVGs into a Slides-ready file in Google Drive. Every surface is free.",
        "img_alt": "SVG to Google Slides converter: SVG files converted into native, editable Google Slides shapes",
        "lottie": "svgslides_install.json",
        "cards": [
            ("Chrome extension", "Drag an SVG straight onto an open Slides tab and drop it in place. No dialog, no upload step. Converts in your browser.", CWS, "Add to Chrome &mdash; free"),
            ("Web Uploader", "Upload one or more SVGs and get back a Google Drive link to a Slides-ready file, one slide per SVG. Best for bulk conversion or building an icon library.", "/convert", "Open the converter"),
            ("Google Slides add-on", "Insert SVGs into a presentation you're already editing, from a dialog inside Slides itself.", "/addon", "Get the add-on"),
        ],
        "tables": [
            ("Which converter to use", ["You want to", "Use", "Why"], [
                ("Drop an SVG into the deck you're editing", "Chrome extension", "Converts in your browser and pastes in place. No Google permissions."),
                ("Turn text into shapes", "Web uploader", "Only the web uploader outlines text."),
                ("Convert a whole icon set at once", "Web uploader", "One slide per SVG, in one Google Drive file."),
                ("Stay inside Slides without the Chrome extension", "Google Slides add-on", "Runs from a dialog in the Slides Extensions menu."),
            ]),
            ("Every way to get an SVG into Google Slides", ["Method", "Result in Slides", "What it takes"], [
            ("SVG to Slides Chrome extension", "Editable shapes, one per path", "Drag and drop onto the slide"),
            ("SVG to Slides web uploader", "Editable shapes, one slide per SVG", "Upload in the browser, open the Google Drive link"),
            ("SVG to Slides add-on", "Editable shapes", "Extensions menu inside Google Slides"),
            ("Convert to PNG, then Insert &rarr; Image", "One flattened image that blurs when resized", "Any image converter"),
            ("EMF or WMF via Google Drawings", "Shapes, after several manual steps", "A converter, Google Drive, Google Drawings"),
            ("Microsoft PowerPoint, then import", "Shapes, after a round trip through Drive", "A PowerPoint licence"),
            ]),
        ],
        "sections": [
            ("What each converter keeps", [
                "Every surface converts paths, basic shapes, arcs, transforms and even-odd cut-outs into native shapes.",
                "Gradients and text come through on the web uploader only.",
                "Clip paths, masks, patterns, filters and transparency don't come through on any surface. <a href=\"/specs#compatibility\">See the tested results for 20 SVG features</a>.",
            ]),
        ],
        "faq": [
            ("Is there an online SVG to Google Slides converter?", "Yes. Upload SVGs at svgslid.es/convert. No install needed. You get a Google Drive link to a file with one slide per SVG."),
            ("Do I need an account?", "No account is required for the extension. The web converter takes an optional Google account email if you want the file shared directly to you."),
            ("How long does the web converter keep my file?", "The link stays active for 7 days. To keep a file, open it in Drive and choose File &rarr; Make a copy. The copy is fully yours, with no expiry."),
            ("Is it really free?", FREE_LINE),
        ],
        "related": ["insert-svg-into-google-slides", "does-google-slides-support-svg", "svg-logos-icons-google-slides"],
    },
    {
        "slug": "recolor-svg-in-google-slides",
        "nav": "Edit & recolor SVGs in Google Slides",
        "title": "Edit and Recolor SVGs in Google Slides | SVG to Slides",
        "desc": "Recolor individual SVG elements, edit points, and animate shapes in Google Slides. SVG to Slides turns every path into a native shape. Free Chrome extension.",
        "h1": "Edit and recolor SVGs in Google Slides&trade;",
        "lede": "Every SVG path becomes its own Slides shape. Select the palm without touching the wordmark, then recolour it with the standard fill picker.",
        "answer": "Once converted with SVG to Slides, every path in your SVG is a separate native Slides shape. Select one element and change its fill with the standard picker, edit its points, or animate it on its own.",
        "img_alt": "Recolor an SVG in Google Slides: one element of a converted SVG selected and recoloured with the fill picker",
        "lottie": "svgslides_recolor.json",
        "points": [
            ("Select individual elements.", "Every path is its own selectable shape, not one flattened image."),
            ("Recolour with the fill picker.", "Change any shape's colour directly in Slides. No re-exporting."),
            ("Edit points.", "Double-click a shape and click Edit Shape to drag its points and curve handles on the slide. <a href=\"/docs/edit-shape\">How Edit Shape works</a>."),
            ("Animate each shape.", "Build transitions element by element instead of animating one image."),
        ],
        "faq": [
            ("Can I change the color of an SVG in Google Slides?", "Yes, once it's converted. SVG to Slides turns each path into a native shape, so you can recolour any element with the standard fill picker."),
            ("Can I edit the points of an SVG shape?", "Yes, with the Chrome extension. Double-click a converted shape and click Edit Shape to move its points and curve handles in place. Slides&rsquo; own Edit points works only on shapes with straight segments."),
            ("What about gradients?", "Solid fills and strokes convert cleanly. Gradients come through in the online converter and, since version 1.4.0, in the Chrome extension. In the add-on they collapse to a single solid colour."),
        ],
        "related": ["edit-points-google-slides", "replace-color-google-slides", "svg-logos-icons-google-slides"],
    },
    {
        "slug": "svg-logos-icons-google-slides",
        "nav": "SVG logos & icons in Slides themes",
        "title": "SVG Logos and Icons in Google Slides Themes | SVG to Slides",
        "desc": "Use SVG logos and icons in Google Slides theme layouts. Convert once, reuse across slides, resize without losing quality. Works in Google Drawings too.",
        "h1": "SVG logos and icons in Google Slides&trade; themes",
        "lede": "Add converted graphics to your theme layouts and reuse them across slides. From a small footer icon to a full-slide graphic, every edge stays sharp.",
        "answer": "Convert your logo or icon set with SVG to Slides, add it to your theme layouts, and reuse it on every slide. The shapes resize without losing quality and also work in Google Drawings.",
        "img_alt": "SVG logos and icons in a Google Slides theme, reused across slides as sharp vector shapes",
        "lottie": "svgslides_reuse.json",
        "points": [
            ("Use SVGs in your themes.", "Put converted logos and icons in theme layouts so they appear on every slide that uses them."),
            ("Resize without losing quality.", "From a small footer icon to a full-slide graphic, every edge stays sharp."),
            ("Build an icon library.", "Upload a batch at svgslid.es/convert and get one slide per icon, ready to copy from."),
            ("Works in Google Drawings.", "The native shapes also work in Google Drawings."),
        ],
        "faq": [
            ("Can I put an SVG logo in a Google Slides theme?", "Yes. Convert it with SVG to Slides, then add it to your theme layouts. It stays a native, resizable shape."),
            ("How do I convert a whole icon set?", "Upload the files at svgslid.es/convert. You get a Google Drive link to a file with one slide per SVG."),
            ("Will my logo stay sharp when I scale it?", "Yes. Converted shapes are vectors, so they resize at any size and stay crisp."),
        ],
        "related": ["recolor-svg-in-google-slides", "svg-to-google-slides-converter", "insert-svg-into-google-slides"],
    },
]

# Editing-tool guides (Nov 25, 2026). One search task each; the facts come from the
# docs topics each one links to (docs_guide.py). "alt" and "close" replace the
# converter CTA and the SVG closing line, which don't fit an editing task.
_EDIT_ALT = ("/vector-editor", "See every editing tool")
_EDIT_CLOSE = "Draw in Google Slides&trade;."
PAGES += [
    {
        "slug": "edit-points-google-slides",
        "nav": "Edit points in Google Slides",
        "title": "How to Edit Points in Google Slides, on Any Shape | SVG to Slides",
        "desc": "Edit the points and curves of any shape in Google Slides: SVGs, Slides' own shapes, arrows, text boxes and WordArt. Drag points and handles, add or remove points. Free Chrome extension.",
        "h1": "How to edit points in Google Slides&trade;",
        "lede": "Slides&rsquo; own Edit points works only on polylines, which have straight segments. SVG to Slides opens a vector editor on any shape, curves included, at its exact size and position on the slide.",
        "answer": "Install SVG to Slides, double-click the shape and click <b>Edit Shape</b>. Drag a point to move it, click a point to show its curve handles, then click <b>Done</b>. The shape updates in place and keeps its place in the stack.",
        "img_alt": "Double-clicking a palm tree in Google Slides and dragging its points and curve handles in the Edit Shape editor",
        "video": "edit-points",
        "lottie": "",
        "alt": _EDIT_ALT,
        "close": _EDIT_CLOSE,
        "howto": [
            ("Open Edit Shape.", "Double-click the shape, then click <b>Edit Shape</b>. You can also select it and click Edit Shape on the extension&rsquo;s toolbar."),
            ("Move points and curves.", "Drag a point to move it. Click a point to see its curve handles, and drag a handle to change the curve."),
            ("Add or remove points.", "Press P, then click the outline to add a point, or click a point to remove it."),
            ("Click Done.", "Or press Enter. The edited shape takes the original&rsquo;s place, and the whole session is one undo step."),
        ],
        "sections": [
            ("Point and curve keys", [
                "<b>Smooth or corner point:</b> double-click the point.",
                "<b>Move one handle only:</b> hold Option (Alt on Windows) while dragging it.",
                "<b>Keep to 45&deg; steps:</b> hold Shift while dragging.",
                "<b>Select several points:</b> Shift-click each one, or drag a box around them.",
                "<b>Nudge:</b> arrow keys. Hold Shift for ten times the step.",
                "<b>Undo and redo, point by point:</b> Command+Z and Shift+Command+Z (Ctrl on Windows).",
            ], "ul", 'Every key is in the <a href="/docs/edit-shape#points">Edit Shape reference</a>.'),
            ("Slides&rsquo; own shapes, lines and WordArt", [
                "Edit Shape also opens on shapes from Slides&rsquo; shape menu, arrows, callouts, lines, text boxes and WordArt. It converts the object into custom shapes first.",
                "Beside the Edit Shape button, a grey note says what the conversion costs, for example &ldquo;text becomes outlines&rdquo;. Cancel puts the original back.",
                "A preset shape loses its adjustment handles. Text inside a shape stays editable. WordArt becomes letter outlines you can reshape but not retype.",
            ], "ul", '<a href="/docs/convert-slides-shapes">What each object becomes</a>.'),
            ("More than points", [
                "<b>The box.</b> Drag a corner to scale, an edge to stretch, Command and an edge to skew, Command and a corner to rotate. The points stay editable.",
                "<b>Exact values.</b> The pill under the shape holds width, height and rotate-by. Type a value and press Enter.",
                "<b>Round corners.</b> Drag the small circle inside a corner, or type a radius. <a href=\"/docs/round-corners\">Rounding corners</a>.",
            ]),
        ],
        "faq": [
            ("Can you edit points in Google Slides without an extension?", "Only on polylines: shapes with straight segments only. Curved shapes and shapes with holes need Edit Shape. <a href=\"/docs/kb/edit-points-missing\">Why</a>."),
            ("Can I edit the points of an SVG?", "Yes. Insert the SVG with SVG to Slides, so every path arrives as its own shape, then double-click a shape and click Edit Shape."),
            ("Are animations kept after I edit a shape?", "No. Done puts a new object in place of the original, so animations and links attached to it do not carry over."),
            ("What can't be edited as a shape?", "Images, video and charts."),
            ("Is it free?", "Yes. " + FREE_LINE),
        ],
        "related": ["pen-tool-google-slides", "combine-shapes-google-slides", "recolor-svg-in-google-slides"],
    },
    {
        "slug": "pen-tool-google-slides",
        "nav": "Pen tool for Google Slides",
        "title": "Pen Tool for Google Slides: Draw Custom Shapes and Curves | SVG to Slides",
        "desc": "Draw custom shapes in Google Slides with a pen tool: click for corners, drag for curves, snap points to a grid, and place native shapes on the slide. Free Chrome extension.",
        "h1": "A pen tool for Google Slides&trade;",
        "lede": "Draw the shapes the shape menu doesn&rsquo;t have. Click for corners, drag for curves, and let points and handles snap to a grid.",
        "answer": "Install SVG to Slides. With nothing selected, press Option+Shift+P (Alt+Shift+P on Windows) or click <b>Pen</b> on the toolbar. Click to place corners, drag for curves, click the first point to close the shape, then click <b>Done</b>. Each path becomes a native Slides shape.",
        "img_alt": "Drawing a curved wave shape with the pen in Google Slides while points and handles snap to a grid",
        "lottie": "svgslides_13_pen.json",
        "alt": _EDIT_ALT,
        "close": _EDIT_CLOSE,
        "howto": [
            ("Open the pen.", "With nothing selected, press Option+Shift+P or click <b>Pen</b> on the toolbar. An empty editor opens over the slide."),
            ("Place points.", "Click for a corner point. To make a curve, press, drag and release."),
            ("Close the shape.", "Click the first point. A ring appears on it when the pointer is over it. To leave the path open, press Enter or Esc."),
            ("Click Done.", "The new shapes are placed on the slide, on top, in one undo step."),
        ],
        "sections": [
            ("Pen keys", [
                "<b>Sharp turn after a curve:</b> hold Option while dragging to break the handles.",
                "<b>Keep to 45&deg; steps:</b> hold Shift.",
                "<b>Remove the last point:</b> Delete.",
                "<b>Carry on an open path:</b> click its end point.",
                "<b>Add a point to a path:</b> click a segment. Click a point to remove it.",
                "<b>Switch to the Select tool:</b> V.",
            ], "ul", '<a href="/docs/pen#keys">All pen keys</a> &middot; <a href="/docs/snapping">Snapping</a>'),
            ("What you get", [
                "Each path becomes a new shape. The first shape you draw has a 2 pixel dark stroke and no fill. Each later shape starts with the paint of the last one drawn.",
                "Set a fill or stroke from the editor&rsquo;s toolbar before you click Done, or afterwards on the slide.",
                "With shapes selected when you open the pen, the editor opens on those shapes, and the pen can edit them and draw new ones beside them.",
            ]),
        ],
        "faq": [
            ("Is there a freehand mode?", "No. The pen draws point by point."),
            ("Can I reshape a drawn shape later?", "Yes. Double-click it and click Edit Shape to move its points and curves. <a href=\"/guides/edit-points-google-slides\">How to edit points</a>."),
            ("Can I leave a path open, like a line?", "Yes. Press Enter or Esc instead of clicking the first point."),
            ("Is it free?", "Yes. " + FREE_LINE),
        ],
        "related": ["edit-points-google-slides", "combine-shapes-google-slides", "replace-color-google-slides"],
    },
    {
        "slug": "combine-shapes-google-slides",
        "nav": "Combine shapes in Google Slides",
        "title": "How to Combine, Merge or Subtract Shapes in Google Slides | SVG to Slides",
        "desc": "Combine shapes in Google Slides with union, subtract, intersect and exclude. Merge shapes into one, cut one shape out of another, and undo in one step. Free Chrome extension.",
        "h1": "How to combine shapes in Google Slides&trade;",
        "lede": "Union, Subtract, Intersect and Exclude make one shape from two or more. They work on the slide and inside Edit Shape, and each is one undo step.",
        "answer": "Install SVG to Slides, select two or more shapes, and press Option+Shift+U for Union or Option+Shift+S for Subtract (Alt+Shift on Windows). Intersect and Exclude are Option+Shift+I and Option+Shift+E. The same four commands are in the Combine section of the toolbar.",
        "img_alt": "Four overlapping shapes combined into one cloud shape with Union in Google Slides",
        "lottie": "svgslides_13_combine.json",
        "alt": _EDIT_ALT,
        "close": _EDIT_CLOSE,
        "howto": [
            ("Select the shapes.", "Select two or more shapes on the slide. For Subtract, the bottom shape is the one that keeps its outline."),
            ("Run the command.", "Click it in the Combine section of the toolbar, or press its shortcut."),
            ("Undo if you need to.", "One Command+Z (Ctrl+Z on Windows) splits them again."),
        ],
        "tables": [
            ("The four commands", ["Command", "Result", "Shortcut (Mac)"], [
                ["<b>Union</b>", "One shape covering everything the selected shapes cover.", "Option+Shift+U"],
                ["<b>Subtract</b>", "The bottom shape with the shapes above it cut out.", "Option+Shift+S"],
                ["<b>Intersect</b>", "Only the area where the shapes overlap.", "Option+Shift+I"],
                ["<b>Exclude</b>", "Everything except the area where the shapes overlap.", "Option+Shift+E"],
            ]),
        ],
        "sections": [
            ("Limits", [
                "Gradients, pattern fills, transparency and shadows are not carried into the result.",
                "Images, video and charts cannot be combined. To cut a picture to a shape, use <a href=\"/docs/mask-image\">Mask image with shape</a>.",
                "The shapes need a fill or an outline.",
                "Intersect needs shapes that overlap. If a command would leave nothing, the extension says so and changes nothing.",
            ], "ul", 'Inside Edit Shape the same buttons act on the shapes with selected points. <a href="/docs/combine-shapes">Combining shapes reference</a>.'),
        ],
        "faq": [
            ("How do I merge shapes in Google Slides?", "Select them and use Union (Option+Shift+U). You get one shape covering everything the selected shapes covered."),
            ("How do I cut one shape out of another?", "Put the shape to cut on top, select both, and use Subtract (Option+Shift+S). The bottom shape keeps its outline, minus the shapes above it."),
            ("Can I undo a combine?", "Yes. One Command+Z splits the shapes again."),
            ("Is it free?", "Yes. " + FREE_LINE),
        ],
        "related": ["pen-tool-google-slides", "edit-points-google-slides", "svg-logos-icons-google-slides"],
    },
    {
        "slug": "replace-color-google-slides",
        "nav": "Replace a colour across Google Slides",
        "title": "How to Replace a Color Throughout Google Slides | SVG to Slides",
        "desc": "Replace one colour everywhere it is used in Google Slides, on one slide or every slide: fills, strokes, gradient stops and text, inside groups too. Undo in one step. Free Chrome extension.",
        "h1": "How to replace a colour throughout Google Slides&trade;",
        "lede": "Change one colour everywhere it is used, on one slide or every slide in the deck. Fills, strokes, gradient stops and text change, inside groups too.",
        "answer": "Install SVG to Slides. Click an empty part of the slide and press Option+Shift+F (Alt+Shift+F on Windows). Pick the colour to change, set the new one, tick <b>All slides</b> for the whole deck, and click the tick. One Command+Z undoes the whole run.",
        "img_alt": "Replacing a teal with indigo across every slide of a Google Slides deck with Replace a colour",
        "lottie": "svgslides_14_replace.json",
        "alt": _EDIT_ALT,
        "close": _EDIT_CLOSE,
        "howto": [
            ("Clear the selection.", "Click an empty part of the slide so that nothing is selected."),
            ("Open Replace a colour.", "Press Option+Shift+F, or click the paint bucket on the toolbar."),
            ("Pick the old colour.", "Click it in the list, or pick it from the slide with the eyedropper."),
            ("Set the new colour.", "The slide shows it in every place the old colour is used."),
            ("Choose the scope and apply.", "Tick <b>All slides</b> to change it on every slide; the list then shows the colours of the whole presentation. Click the tick."),
        ],
        "sections": [
            ("What changes, and what is kept", [
                "Fills, strokes, gradient stops and text are changed, inside groups too.",
                "A run across all slides shows a progress bar and is undone with one press of Command+Z.",
                "Most changes are made on the object itself, so its animation and link stay. <a href=\"/docs/fill-stroke#applied\">When an object is replaced instead</a>.",
            ]),
            ("Long presentations", [
                "The colours of other slides are read from the filmstrip. Slides far down the filmstrip may not be listed until you scroll to them.",
            ], "ul", '<a href="/docs/fill-stroke#replace">Replace a colour reference</a> &middot; <a href="/docs/fill-stroke#panel">The colour panel</a>'),
        ],
        "faq": [
            ("Does it change text colour too?", "Yes. Fills, strokes, gradient stops and text all change."),
            ("Does it reach shapes inside groups?", "Yes."),
            ("Can I see the result before I apply it?", "Yes. While the panel is open, the slide shows the new colour in every place the old one is used. The cross puts the slide back."),
            ("Can I undo it?", "Yes. One Command+Z undoes the whole run, even across every slide."),
            ("Is it free?", "Yes. " + FREE_LINE),
        ],
        "related": ["recolor-svg-in-google-slides", "combine-shapes-google-slides", "pen-tool-google-slides"],
    },
]


# Existing pages: SEO fixes applied in place by build_site.py.
EXISTING = {
    "index.html": {
        "path": "/",
        "title": "Editable SVGs in Google Slides: Free Chrome Extension | SVG to Slides",
        "desc": "Insert SVG files into Google Slides as native, editable shapes. Drag them in with a free Chrome extension, recolor any element, resize without losing quality.",
    },
    "convert.html": {
        "path": "/convert",
        "title": "SVG to Google Slides Converter (Online, Free) | SVG to Slides",
        "desc": "Upload SVG files and get a Google Slides-ready file with real, editable vector shapes. One slide per SVG. Free online converter, no account required.",
    },
    "features.html": {
        "path": "/features",
        "title": "Features | SVG to Slides for Google Slides",
        "desc": None,
    },
    "support.html": {"path": "/support", "title": None, "desc": None},
    "privacy.html": {"path": "/privacy", "title": None, "desc": None},
    "terms.html": {"path": "/terms", "title": None, "desc": None},
    "chrome.html": {"path": "/chrome", "title": None, "desc": None, "noindex": True},
    "addon.html": {"path": "/addon", "title": None, "desc": None, "noindex": True},
}

HOME_MD = """# SVG to Slides — editable SVGs in Google Slides

SVG to Slides is a free Chrome extension that inserts SVG files into Google Slides as native, editable shapes.

Free forever. Every feature, no daily cap, no account, no Pro tier.

- Install: {cws}
- Online converter (no install): {site}/convert
- Google Slides add-on: {site}/addon

## The problem
Google Slides doesn't support SVG files. Your options are to flatten them into PNGs or take the long way through EMF conversion, Google Drawings, and copy-paste.

## What it does
- **Edit individual elements.** Every SVG path becomes its own Slides shape. Recolour any element with the standard fill picker.
- **Resize without losing quality.** From a small footer icon to a full-slide graphic, every edge stays sharp.
- **Use SVGs in your themes.** Add converted graphics to theme layouts and reuse them across slides.
- **Edit any shape as SVG.** Double-click a shape and move its points and curve handles right on the slide. Works on Slides' own shapes, lines and WordArt too.
- **Draw and colour inside Slides.** A pen with grid snapping, union and subtract, image masks, outline text, a Layers panel, a colour panel with gradients, and Replace a colour across the deck. ({site}/vector-editor)

## How it works
1. Install the extension from the Chrome Web Store. No account required.
2. Drag in your SVG and click where it goes. Its paths become editable shapes.
3. Double-click any shape to edit its points as SVG.

## Limits
- Gradients come through in the online converter and, since version 1.4.0, in the extension, which also keeps opacity. The add-on fills a gradient with its first colour.
- Arc commands (A/a) are converted into smooth curves.
- Up to 25 files per drop in the extension; use the online converter for larger batches.

## Questions
{faq}

## Privacy
The Chrome extension converts every file inside your browser; nothing is uploaded. Details: {site}/privacy
"""


# Homepage FAQ: covers the entities Google Images groups with "svg google slides"
# (upload/import/insert SVG file, PowerPoint, icons, vector graphics, themes).
HOME_FAQ_H2 = "SVG in Google Slides: common questions"
HOME_FAQ = [
    ("Can you upload or import an SVG file into Google Slides?", "Not as an editable graphic. Google Slides doesn't support SVG files. Install SVG to Slides and drag the file onto a slide, or convert it online at <a href=\"/convert\">svgslid.es/convert</a>. Every path arrives as a native Slides shape."),
    ("How is this different from Microsoft PowerPoint?", "PowerPoint can insert an SVG file and convert it to shapes. Google Slides can't. SVG to Slides gives Slides the same result: vector graphics you can select, recolour, and resize."),
    ("Can you edit the points of a shape in Google Slides?", "Only for lines and polylines you draw yourself. With SVG to Slides, double-click any shape, including Slides&rsquo; own shapes and WordArt, and click Edit Shape to move its points and curves in place. <a href=\"/vector-editor\">See the editing tools</a>."),
    ("Can I add SVG icons to Google Slides?", "Yes. Drag up to 25 SVG icons onto a slide at once. Each one becomes editable shapes with no background box, so you can recolour it to match your theme."),
    ("Do the shapes stay sharp when I resize them?", "Yes. They're vector graphics, so a small footer icon and a full-slide graphic both keep crisp edges."),
    ("Can I use SVG logos in my Google Slides theme?", "Yes. Add converted logos and icons to your theme layouts and reuse them across slides. The shapes also work in Google Drawings."),
    ("Is it free?", "Yes. " + FREE_LINE),
]
HOME_GUIDE_LINKS = [
    ("insert-svg-into-google-slides", "How to insert an SVG into Google Slides"),
    ("does-google-slides-support-svg", "Does Google Slides support SVG?"),
    ("svg-to-google-slides-converter", "SVG to Google Slides converter"),
    ("recolor-svg-in-google-slides", "Recolor SVGs in Google Slides"),
    ("svg-logos-icons-google-slides", "SVG logos and icons in Slides themes"),
    ("svg-vs-png-google-slides", "SVG vs PNG in Google Slides"),
    ("edit-points-google-slides", "Edit points in Google Slides"),
    ("combine-shapes-google-slides", "Combine shapes in Google Slides"),
    ("pen-tool-google-slides", "Pen tool for Google Slides"),
    ("replace-color-google-slides", "Replace a colour across Google Slides"),
]


# Guides lobby: groups (display order) and per-guide card metadata.
GUIDE_GROUPS = [
    ("start", "Start here", "What Slides does with SVGs, and how to get them in."),
    ("workflow", "Design workflows", "Recolouring, logos, icon sets and themes."),
    ("editing", "Editing tools", "Reshape, draw, combine and recolour any shape in Slides."),
]
GUIDE_META = {
    "does-google-slides-support-svg": ("start", "🤔", 3),
    "insert-svg-into-google-slides": ("start", "📥", 2),
    "svg-vs-png-google-slides": ("start", "⚖️", 3),
    "svg-to-google-slides-converter": ("workflow", "🔁", 2),
    "recolor-svg-in-google-slides": ("workflow", "🎨", 2),
    "svg-logos-icons-google-slides": ("workflow", "🧩", 2),
    "edit-points-google-slides": ("editing", "✏️", 2),
    "pen-tool-google-slides": ("editing", "🖋️", 2),
    "combine-shapes-google-slides": ("editing", "🔗", 2),
    "replace-color-google-slides": ("editing", "🪣", 2),
}
DEFAULT_FEATURED = "does-google-slides-support-svg"

# Old URL -> new URL (301s in cloud/main.py are generated from this).
LEGACY = {"/guide": "/guides/insert-svg-into-google-slides"}
LEGACY.update({f"/{p['slug']}": f"/guides/{p['slug']}" for p in PAGES })
