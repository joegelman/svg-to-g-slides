"""Single source of truth for svgslid.es keyword landing pages + agent-facing text.

Every claim here is drawn from existing site copy (index, guide, features, convert,
privacy) or from the code (25-file drop limit, no usage cap). Don't add claims that
aren't backed by one of those.
"""

CWS = "https://chromewebstore.google.com/detail/svg-to-slides/bdhhnakellmdnbgbdokiojipaebdeioi"
SITE = "https://svgslid.es"

FREE_LINE = "Free forever. Every feature, no daily cap, no account, no Pro tier."

# Keyword landing pages. Order = footer/related order.
PAGES = [
    {
        "slug": "insert-svg-into-google-slides",
        "nav": "Insert an SVG into Google Slides",
        "title": "Insert an SVG into Google Slides as Editable Shapes",
        "desc": "Insert an SVG into Google Slides as native, editable shapes: drag the file onto your slide with the free SVG to Slides extension. No account, no daily cap.",
        "h1": "Insert an SVG into Google Slides&trade;",
        "lede": "Drag the file onto your slide. SVG to Slides converts every path into a native Google Slides shape you can select, recolour, and resize.",
        "answer": "Google Slides doesn't accept SVG files as editable graphics. To insert one, install the free SVG to Slides Chrome extension, open your presentation, and drag the .svg file onto a slide. Each path becomes its own native Slides shape.",
        "lottie": "svgslides_drop.json",
        "howto": [
            ("Install the extension.", "Add SVG to Slides from the Chrome Web Store. No account required."),
            ("Open Google Slides.", "Work in any existing or new presentation."),
            ("Drag in your SVG.", "Drop the file onto a slide. Its paths become editable shapes. Up to 25 files per drop."),
        ],
        "sections": [
            ("Other ways in", [
                "<b>Web converter.</b> Upload SVGs at <a href=\"/convert\">svgslid.es/convert</a> and get a Google Drive link to a Slides-ready file, one slide per SVG. No install.",
                "<b>Google Slides add-on.</b> Insert SVGs from a dialog inside Slides, without leaving the tab. <a href=\"/addon\">Get the add-on</a>.",
                "<b>The long way.</b> Without a converter, your options are flattening the SVG to a PNG, or EMF conversion, Google Drawings, and copy-paste.",
            ]),
        ],
        "faq": [
            ("Can I upload an SVG to Google Slides directly?", "Not as an editable graphic. Without a converter, your options are to flatten it into a PNG or take the long way through EMF conversion, Google Drawings, and copy-paste. SVG to Slides converts the file into native Slides shapes instead."),
            ("How many SVGs can I insert at once?", "Up to 25 per drop with the Chrome extension. For larger batches, use the bulk converter at svgslid.es/convert."),
            ("Does it cost anything?", FREE_LINE),
            ("Is my file uploaded anywhere?", "The Chrome extension converts on your device using an embedded WebAssembly engine, so your file usually never leaves the browser. The web converter and add-on send the file to our backend for conversion."),
        ],
        "related": ["does-google-slides-support-svg", "svg-to-google-slides-converter", "recolor-svg-in-google-slides"],
    },
    {
        "slug": "does-google-slides-support-svg",
        "nav": "Does Google Slides support SVG?",
        "title": "Does Google Slides Support SVG? How to Use SVGs Anyway",
        "desc": "Google Slides doesn't keep SVGs as editable vectors. Here's what happens to your file, and how to insert SVGs as native, recolorable shapes instead.",
        "h1": "Does Google Slides&trade; support SVG?",
        "lede": "Not as an editable format. Here's what that costs you, and how to keep your SVGs as real vector shapes.",
        "answer": "No. Google Slides doesn't keep SVG files as editable vectors. Your options are to flatten the SVG into a PNG, or convert it through EMF and Google Drawings. SVG to Slides converts the file into Slides' native shape format, so it stays editable.",
        "lottie": "svgslides_scale.json",
        "compare": [
            ("Blurs or pixelates when resized", "Resizes at any size, always crisp"),
            ("One flattened image, single object", "Every path is its own selectable shape"),
            ("Can't recolour without re-exporting", "Recolour any shape directly in Slides"),
            ("Can't animate individual elements", "Animate each shape independently"),
            ("Can't edit points or paths", "Right-click &rarr; Edit points, like any native shape"),
        ],
        "faq": [
            ("Can you import an SVG into Google Slides?", "Not as editable vector shapes. Install the SVG to Slides Chrome extension and drag the file onto a slide, or upload it at svgslid.es/convert. Both turn every path into a native Slides shape."),
            ("Why does my SVG look blurry in Google Slides?", "It's been flattened into a raster image, so it pixelates when you resize it. Converted with SVG to Slides, it stays a vector and every edge stays sharp."),
            ("What happens to gradients and complex curves?", "Solid fills and strokes convert cleanly. Gradients currently collapse to a solid approximate colour, and arc commands (A/a) in paths are approximated as straight line segments. Re-exporting with more path segments avoids visibly angular curves."),
            ("Do the converted shapes work in Google Drawings?", "Yes. The native shapes also work in Google Drawings."),
        ],
        "related": ["insert-svg-into-google-slides", "svg-to-google-slides-converter", "svg-logos-icons-google-slides"],
    },
    {
        "slug": "svg-to-google-slides-converter",
        "nav": "SVG to Google Slides converter",
        "title": "SVG to Google Slides Converter — Free, Online & Extension",
        "desc": "Convert SVG files into native, editable Google Slides shapes. Free Chrome extension, online converter, and Slides add-on. No account, no daily cap, no Pro tier.",
        "h1": "SVG to Google Slides&trade; converter",
        "lede": "Three ways to turn SVG files into native, editable Slides shapes. All free.",
        "answer": "SVG to Slides converts SVG files into native, editable Google Slides shapes. Use the Chrome extension to drop files straight onto a slide, or the web converter to turn a batch of SVGs into a Slides-ready file in Google Drive. Every surface is free.",
        "lottie": "svgslides_install.json",
        "cards": [
            ("Chrome extension", "Drag an SVG straight onto an open Slides tab and drop it in place. No dialog, no upload step. Converts in your browser.", CWS, "Add to Chrome &mdash; free"),
            ("Online converter", "Upload one or more SVGs and get back a Google Drive link to a Slides-ready file, one slide per SVG. Best for bulk conversion or building an icon library.", "/convert", "Open the converter"),
            ("Google Slides add-on", "Insert SVGs into a presentation you're already editing, from a dialog inside Slides itself.", "/addon", "Get the add-on"),
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
        "title": "Edit and Recolor SVGs in Google Slides — SVG to Slides",
        "desc": "Recolor individual SVG elements, edit points, and animate shapes in Google Slides. SVG to Slides turns every path into a native shape. Free Chrome extension.",
        "h1": "Edit and recolor SVGs in Google Slides&trade;",
        "lede": "Every SVG path becomes its own Slides shape. Select the palm without touching the wordmark, then recolour it with the standard fill picker.",
        "answer": "Once converted with SVG to Slides, every path in your SVG is a separate native Slides shape. Select one element and change its fill with the standard picker, edit its points, or animate it on its own.",
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
            ("What about gradients?", "Gradients currently collapse to a solid approximate colour. Solid fills and strokes convert cleanly."),
        ],
        "related": ["insert-svg-into-google-slides", "svg-logos-icons-google-slides", "does-google-slides-support-svg"],
    },
    {
        "slug": "svg-logos-icons-google-slides",
        "nav": "SVG logos & icons in Slides themes",
        "title": "SVG Logos and Icons in Google Slides Themes — SVG to Slides",
        "desc": "Use SVG logos and icons in Google Slides theme layouts. Convert once, reuse across slides, resize without losing quality. Works in Google Drawings too.",
        "h1": "SVG logos and icons in Google Slides&trade; themes",
        "lede": "Add converted graphics to your theme layouts and reuse them across slides. From a small footer icon to a full-slide graphic, every edge stays sharp.",
        "answer": "Convert your logo or icon set with SVG to Slides, add it to your theme layouts, and reuse it on every slide. The shapes resize without losing quality and also work in Google Drawings.",
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
        "title": "SVG to Slides — Insert Editable SVGs into Google Slides (Free)",
        "desc": "Drag an SVG into Google Slides and get native, editable shapes. Recolor elements, resize without losing quality. Free forever: no daily cap, no account.",
    },
    "guide.html": {
        "path": "/guide",
        "title": "SVG in Google Slides: Keep It an Editable Vector, Not a PNG",
        "desc": "Google Slides flattens SVGs into images. See what you lose, and how to keep every path as a native, editable, recolourable Slides shape instead. Free.",
    },
    "convert.html": {
        "path": "/convert",
        "title": "SVG to Google Slides Converter (Online, Free) — SVG to Slides",
        "desc": "Upload SVG files and get a Google Slides-ready file with real, editable vector shapes. One slide per SVG. Free online converter, no account required.",
    },
    "features.html": {
        "path": "/features",
        "title": "Features — SVG to Slides for Google Slides",
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

## How it works
1. Install the extension from the Chrome Web Store. No account required.
2. Open Google Slides, in any existing or new presentation.
3. Drag in your SVG. Its paths become editable shapes.

## Limits
- Gradients currently collapse to a solid approximate colour.
- Arc commands (A/a) in paths are approximated as straight line segments.
- Up to 25 files per drop in the extension; use the online converter for larger batches.

## Privacy
The Chrome extension converts on your device with an embedded WebAssembly engine; your file usually never leaves the browser. Details: {site}/privacy
"""
