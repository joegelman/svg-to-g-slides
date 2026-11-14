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
            ("Can't edit points or paths", "Right-click &rarr; Edit points, like any native shape"),
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
            ("What happens to gradients and complex curves?", "Solid fills and strokes convert cleanly. Arc commands are converted into smooth curves. Gradients come through in the online converter; in the Chrome extension and add-on they currently collapse to a single solid colour. Tested results are on the <a href=\"/specs#compatibility\">specs page</a>."),
            ("Is my file uploaded anywhere?", "Depends on the surface. The Chrome extension converts entirely on your device using an embedded WebAssembly engine, so your file usually never leaves the browser. The online converter and add-on send the file to our backend for conversion. See the <a href=\"/privacy\">privacy policy</a> for specifics."),
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
                "Double-click any shape and click <b>Edit Shape</b>. A vector editor opens on the slide at the shape&rsquo;s exact size, so you can drag its points and curve handles, add or remove points, and undo as you go. Click <b>Done</b> and the shape updates in place.",
                "It works on Slides&rsquo; own shapes, lines and WordArt too. <a href=\"/whats-new\">What&rsquo;s new in 1.2</a>.",
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
            ("Is my file uploaded anywhere?", "The Chrome extension converts on your device using an embedded WebAssembly engine, so your file usually never leaves the browser. The web converter and add-on send the file to our backend for conversion."),
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
            ("Can't edit points or paths", "Right-click &rarr; Edit points, like any native shape"),
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
            ("What happens to gradients and complex curves?", "Solid fills and strokes convert cleanly. Arc commands are converted into smooth curves. Gradients come through in the online converter; in the Chrome extension and add-on they currently collapse to a single solid colour. Tested results are on the <a href=\"/specs#compatibility\">specs page</a>."),
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
                ("Keep gradients, or turn text into shapes", "Web uploader", "Only the web uploader keeps gradients and outlines text."),
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
            ("Edit points.", "Right-click &rarr; Edit points, like any shape you drew yourself."),
            ("Animate each shape.", "Build transitions element by element instead of animating one image."),
        ],
        "faq": [
            ("Can I change the color of an SVG in Google Slides?", "Yes, once it's converted. SVG to Slides turns each path into a native shape, so you can recolour any element with the standard fill picker."),
            ("Can I edit the points of an SVG shape?", "Yes. Right-click a converted shape and choose Edit points, like any native shape."),
            ("What about gradients?", "Solid fills and strokes convert cleanly. Gradients come through in the online converter; in the Chrome extension and add-on they currently collapse to a single solid colour."),
        ],
        "related": ["insert-svg-into-google-slides", "svg-logos-icons-google-slides", "does-google-slides-support-svg"],
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
- **Edit any shape as SVG.** Double-click a shape and move its points and curve handles right on the slide. Works on Slides' own shapes, lines and WordArt too. ({site}/whats-new)

## How it works
1. Install the extension from the Chrome Web Store. No account required.
2. Drag in your SVG and click where it goes. Its paths become editable shapes.
3. Double-click any shape to edit its points as SVG.

## Limits
- Gradients come through in the online converter; in the extension and add-on they currently collapse to a single solid colour.
- Arc commands (A/a) are converted into smooth curves.
- Up to 25 files per drop in the extension; use the online converter for larger batches.

## Questions
{faq}

## Privacy
The Chrome extension converts on your device with an embedded WebAssembly engine; your file usually never leaves the browser. Details: {site}/privacy
"""


# Homepage FAQ: covers the entities Google Images groups with "svg google slides"
# (upload/import/insert SVG file, PowerPoint, icons, vector graphics, themes).
HOME_FAQ_H2 = "SVG in Google Slides: common questions"
HOME_FAQ = [
    ("Can you upload or import an SVG file into Google Slides?", "Not as an editable graphic. Google Slides doesn't support SVG files. Install SVG to Slides and drag the file onto a slide, or convert it online at <a href=\"/convert\">svgslid.es/convert</a>. Every path arrives as a native Slides shape."),
    ("How is this different from Microsoft PowerPoint?", "PowerPoint can insert an SVG file and convert it to shapes. Google Slides can't. SVG to Slides gives Slides the same result: vector graphics you can select, recolour, and resize."),
    ("Can you edit the points of a shape in Google Slides?", "Only for lines and polylines you draw yourself. With SVG to Slides, double-click any shape, including Slides&rsquo; own shapes and WordArt, and click Edit Shape to move its points and curves in place. <a href=\"/whats-new\">See how</a>."),
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
]


# Guides lobby: groups (display order) and per-guide card metadata.
GUIDE_GROUPS = [
    ("start", "Start here", "What Slides does with SVGs, and how to get them in."),
    ("workflow", "Design workflows", "Recolouring, logos, icon sets and themes."),
]
GUIDE_META = {
    "does-google-slides-support-svg": ("start", "🤔", 3),
    "insert-svg-into-google-slides": ("start", "📥", 2),
    "svg-vs-png-google-slides": ("start", "⚖️", 3),
    "svg-to-google-slides-converter": ("workflow", "🔁", 2),
    "recolor-svg-in-google-slides": ("workflow", "🎨", 2),
    "svg-logos-icons-google-slides": ("workflow", "🧩", 2),
}
DEFAULT_FEATURED = "does-google-slides-support-svg"

# Old URL -> new URL (301s in cloud/main.py are generated from this).
LEGACY = {"/guide": "/guides/insert-svg-into-google-slides"}
LEGACY.update({f"/{p['slug']}": f"/guides/{p['slug']}" for p in PAGES })
