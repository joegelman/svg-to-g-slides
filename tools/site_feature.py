"""/vector-editor: the editing toolkit on one page.

The homepage sells SVG import. This page is the second way in, for people who
want to draw, reshape, combine, mask or recolour in Google Slides and have never
searched for an SVG converter. Each section is a short description, one clip
already used on /whats-new, the keys, and links to the docs topic and the guide.

Every statement comes from the docs topics it links to (docs_guide.py) or from
/whats-new. Don't add a claim that isn't backed by one of those.
"""
import product as PR
import site_content as C
import site_pages as P

TITLE = "Vector Editor for Google Slides: Points, Pen, Masks | SVG to Slides"
DESC = ("Edit points and curves, draw with a pen, combine shapes, mask images, outline text, manage layers and "
        "replace colours across a deck, all inside Google Slides. Free Chrome extension.")

# (anchor, heading, paragraph, clip, keys [(label, mac keys)], docs slug, guide slug or None)
# clip: ("lot", lottie name, aria label, caption) or ("vid", file stem, aria label, caption)
TOOLS = [
    ("points", "Edit points and curves",
     "Double-click any shape and click <b>Edit Shape</b>. A vector editor opens on the slide at the shape&rsquo;s exact "
     "size and position. Drag points and curve handles, add or remove points, scale, rotate or skew with the box, or type "
     "exact sizes. Click <b>Done</b> and the shape updates in place. Slides&rsquo; own Edit points works only on "
     "polylines, which have straight segments only.",
     ("vid", "edit-points", "Double-clicking a palm tree in Google Slides and dragging its points and curve handles in the editor",
      "Double-click, Edit Shape, drag."),
     [("Add or remove a point", "<kbd>P</kbd>, then click"), ("Smooth or corner point", "Double-click the point"),
      ("Apply", "<kbd>&#8629;</kbd> or Done")],
     "edit-shape", "edit-points-google-slides"),
    ("corners", "Round any corner",
     "In Edit Shape, shapes with corners show a small circle inside each corner. Drag it toward the middle, or type a "
     "radius in pixels. Select several shapes to give them all the same radius.",
     ("vid", "round-corners", "Selecting three cards, dragging a corner handle to round all twelve corners, then typing 25",
      "Three cards, twelve corners, one drag. Then type 25."),
     [("Radius in 10 px steps", "Hold <kbd>&#8679;</kbd> while dragging")],
     "round-corners", None),
    ("pen", "Draw with the pen",
     "The pen draws new shapes point by point, anywhere on the slide. Click for a corner, drag for a curve, and click the "
     "first point to close the shape. With snapping on, points and handles land on a grid.",
     ("lot", "13_pen", "Drawing a curved wave shape with the pen while points and handles snap to a 20 pixel grid",
      "Click for corners, drag for curves. Every point and handle lands on the grid."),
     [("Pen", "<kbd>&#8997;&#8679;P</kbd>"), ("Keep to 45&deg;", "Hold <kbd>&#8679;</kbd>"), ("Leave the path open", "<kbd>&#8629;</kbd> or <kbd>Esc</kbd>")],
     "pen", "pen-tool-google-slides"),
    ("combine", "Union, subtract, intersect, exclude",
     "Select two or more shapes and make one shape from them. Union covers everything, Subtract cuts the shapes above "
     "out of the bottom one, Intersect keeps the overlap, Exclude keeps everything but the overlap. Each is one undo step.",
     ("lot", "13_combine", "Four shapes combined into one cloud with Union, then undone and redone in one press each",
      "Union, then &#8984;Z and &#8679;&#8984;Z."),
     [("Union", "<kbd>&#8997;&#8679;U</kbd>"), ("Subtract", "<kbd>&#8997;&#8679;S</kbd>"),
      ("Intersect", "<kbd>&#8997;&#8679;I</kbd>"), ("Exclude", "<kbd>&#8997;&#8679;E</kbd>")],
     "combine-shapes", "combine-shapes-google-slides"),
    ("mask", "Mask an image with any shape",
     "Put a shape over a picture, select both, and mask. Any shape or group of shapes can be the mask, not just the crop "
     "shapes in Slides&rsquo; menu. The shape stays on top as an outline. Double-click the result to move or resize the "
     "picture under it.",
     ("lot", "14_mask", "Double-clicking a photo masked by an arch, dragging and resizing the whole picture under it, then confirming",
      "Double-click, drag the picture, resize it, confirm."),
     [("Mask image with shape", "<kbd>&#8997;&#8679;K</kbd>"), ("Adjust the picture", "Double-click the group")],
     "mask-image", None),
    ("outline", "Outline strokes and text",
     "<b>Outline stroke</b> turns lines and borders into filled shapes. <b>Outline text</b> turns text into shapes whose "
     "points you can edit, or use as a mask. On the computer that outlined it, the same command puts the text back.",
     ("lot", "13_beach", "Typing BEACH in a heavy condensed font, outlining it, and masking a beach photo with the letters",
      "Type, outline, select both, mask."),
     [("Outline text", "<kbd>&#8997;&#8984;T</kbd>")],
     "outline-stroke-text", None),
    ("colour", "Colour, gradients and Replace a colour",
     "The paint bucket opens a colour panel with opacity, an eyedropper and a gradient builder, for the fill or the stroke. "
     "With words highlighted it sets their colour. With nothing selected it becomes <b>Replace a colour</b>: pick a colour "
     "in use and choose what it becomes, on one slide or every slide. The slide shows each change while you pick.",
     ("lot", "14_replace", "Picking a teal in Replace a colour, choosing indigo, ticking All slides, then every slide in the deck changing in turn",
      "Pick the colour, choose the new one, tick All slides."),
     [("Fill colour, or Replace a colour", "<kbd>&#8997;&#8679;F</kbd>"), ("Stroke colour", "<kbd>&#8997;&#8679;L</kbd>")],
     "fill-stroke", "replace-color-google-slides"),
    ("layers", "Layers",
     "List every object on the slide, front first. Click a row to select it, drag rows to restack, double-click to rename, "
     "and hide an object while you work. Nested groups open in the list.",
     ("lot", "13_layers", "Opening three levels of nested groups in the Layers panel, Command-clicking an icon on the slide, and renaming it",
      "Three levels down, Command-click, rename."),
     [("Layers", "<kbd>&#8997;1</kbd>")],
     "layers", None),
    ("palette", "Command palette",
     "A searchable list of every command with its shortcut. Type a few letters, move with the arrow keys and press Enter.",
     ("lot", "13_palette", "Opening the command palette, scrolling through every command group, and searching for mask",
      "&#8984;\\, type, Enter."),
     [("Command palette", "<kbd>&#8984;\\</kbd>"), ("Open the toolbar", "<kbd>&#8997;\\</kbd>")],
     "command-palette", None),
]

GUIDES = [s for *_x, s in TOOLS if s]


def _clip(c):
    kind, name, label, cap = c
    if kind == "vid":
        media = (f'<video src="/static/whats-new/{name}.mp4" poster="/static/whats-new/{name}.jpg" autoplay muted loop '
                 f'playsinline preload="metadata" aria-label="{label}"></video>')
    else:
        media = f'<div class="lot" data-lottie="/static/lottie/svgslides_{name}.json" style="aspect-ratio:16/9" role="img" aria-label="{label}"></div>'
    return f'<div class="clip">{media}</div><p class="cap">{cap}</p>'


def _guide_nav(slug):
    return next(p["nav"] for p in C.PAGES if p["slug"] == slug)


def vector_editor_page(ctx):
    cws = P.cws
    jump = "".join(f'<li><a href="#{a}">{h}</a></li>' for a, h, *_r in TOOLS)
    secs = []
    for a, h, para, clip, keys, docs, guide in TOOLS:
        krows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in keys)
        more = f'<a href="/docs/{docs}">Full reference</a>'
        if guide:
            more = f'<a href="/guides/{guide}">{_guide_nav(guide)}</a> &middot; ' + more
        secs.append(f'''    <h2 id="{a}">{h}</h2>
    <p>{para}</p>
    {_clip(clip)}
    <table><tbody>{krows}</tbody></table>
    <p class="more">{more}</p>''')
    body = f"""  <div class="wrap"><p class="crumb"><a href="/">SVG to Slides</a> &rsaquo; Vector editor</p></div>
  <section class="wrap phero wnp">
    <h1>A vector editor inside Google Slides&trade;.</h1>
    <p class="lede">SVG to Slides adds the drawing tools Slides leaves out: point editing, a pen, shape combining, image masks, outline text, layers, and a colour panel with gradients. They work on any shape in the deck, including Slides&rsquo; own shapes, not only SVGs you bring in.</p>
    <div class="ctas"><a class="btn btn-primary" href="{cws('vector-editor', 'hero')}" data-cta="hero"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome, free</a><a class="btn btn-ghost" href="/docs/toolbar">Read the docs</a></div>
    <p class="free">{C.FREE_LINE}</p>
  </section>
  <article class="about wn">
    <h2 id="contents">The tools</h2>
    <ul class="jump">{jump}</ul>
{chr(10).join(secs)}
    <h2 id="any-shape">Works on any shape</h2>
    <p>The tools open on shapes from Slides&rsquo; shape menu, arrows, lines, text boxes and WordArt as well as on SVGs. The extension converts the object into custom shapes first and says what that costs before you start, for example &ldquo;text becomes outlines&rdquo;. <a href="/docs/convert-slides-shapes">What each object becomes</a>.</p>
    <p>Combine, mask, colour changes and a whole Edit Shape session each undo with one press of &#8984;Z. On Windows, use Ctrl for &#8984; and Alt for &#8997;.</p>
    <h2 id="where">Where it runs</h2>
    <p>The editing tools are in the Chrome extension, version {PR.VERSION}. It asks Chrome for {PR.PERMISSIONS} Files are converted inside your browser, and nothing is uploaded. The <a href="/convert">web uploader</a> and the <a href="/google-slides-addon">add-on</a> insert SVGs but have no editing tools.</p>
  </article>
  <div class="wrap"><hr class="rule" style="margin-top:56px"></div>
  <section class="wrap close">
    <h2>Draw in Google Slides&trade;.</h2>
    <div class="ctas"><a class="btn btn-primary" href="{cws('vector-editor', 'close')}" data-cta="close"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome, free</a><a class="btn btn-ghost" href="/whats-new">What&rsquo;s new in {PR.minor()}</a></div>
  </section>"""
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": "Vector editor for Google Slides", "url": C.SITE + "/vector-editor",
           "description": DESC, "about": {"@id": C.SITE + "/#app"}},
          ctx["crumbs"]([("Vector editor", "/vector-editor")])]
    css = ".jump{columns:2;column-gap:28px}.wn .more{font-size:15px;margin:-.4em 0 2em}.wn .more a{color:var(--blue-ink,#0b57d0)}@media (max-width:560px){.jump{columns:1}}"
    doc = P.shell(title=TITLE, desc=DESC, path="/vector-editor", body=body, md="/vector-editor.md",
                  extra_css=P.ABOUT_CSS + P.WHATS_NEW_CSS + css, campaign="vector-editor",
                  ld_block=ctx["ld_block"](ld), tail=ctx["lottie_js"], **ctx["common"])
    import re
    strip = lambda s: re.sub(r"<[^>]+>", "", s).replace("&rsquo;", "'").replace("&ldquo;", '"').replace("&rdquo;", '"') \
        .replace("&#8997;", "Option+").replace("&#8679;", "Shift+").replace("&#8984;", "Command+").replace("&#8629;", "Enter") \
        .replace("&deg;", "°").replace("&middot;", "·").replace("&trade;", "™")
    md = [f"# A vector editor inside Google Slides", "",
          "SVG to Slides adds the drawing tools Slides leaves out: point editing, a pen, shape combining, image masks, outline text, "
          "layers, and a colour panel with gradients. They work on any shape in the deck, not only SVGs you bring in.", "",
          f"_{C.FREE_LINE}_ Install: {C.CWS}", ""]
    for a, h, para, clip, keys, docs, guide in TOOLS:
        md += [f"## {h}", strip(para), ""] + [f"- {strip(k)}: {strip(v)}" for k, v in keys]
        md += [f"- Reference: {C.SITE}/docs/{docs}.md"] + ([f"- Guide: {C.SITE}/guides/{guide}.md"] if guide else []) + [""]
    md += ["## Where it runs",
           f"Chrome extension {PR.VERSION}, on Google Slides pages only. Chrome permissions: {PR.PERMISSIONS} "
           "Files are converted inside the browser; nothing is uploaded. The web uploader and the add-on insert SVGs but have no editing tools.", ""]
    return doc, "\n".join(md)
