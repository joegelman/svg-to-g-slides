"""/specs: product facts and tested SVG compatibility, in one maintained place.

Compatibility results come from running the converter code on the 20 files in
cloud/static/specs/samples/ (extension results pasted into Google Slides with
the extension's clipboard format; web results read from the generated .pptx).
Re-run and update TESTED_ON and COMPAT whenever svg_to_slides.py or
slides_clip.py changes.
"""
import html

import site_content as C
import site_pages as P

TESTED_ON = "November 11, 2026"
TESTED_ON_ISO = "2026-11-11"

# (label, value) — plain facts, each one stated somewhere else on the site or in the code.
FACTS = [
    ("Product", "SVG to Slides"),
    ("What it does", "Converts SVG files into native, editable Google Slides shapes. Every SVG path becomes its own shape."),
    ("Ways to use it", f'<a href="{C.CWS}">Chrome extension</a> (drag and drop onto a slide), <a href="/convert">web uploader</a> (returns a Google Drive file), <a href="/google-slides-addon">Google Slides add-on</a> (dialog inside Slides)'),
    ("Price", "Free. No daily cap, no Pro tier."),
    ("Account", "None for the extension. The web uploader takes an optional Google account email to share the file to."),
    ("Google permissions", "Chrome extension: none. Add-on: reads the current presentation's page size, shows a dialog, and calls the converter."),
    ("Files per drop", "Up to 25 SVGs per drop in the extension. The web uploader takes a batch and makes one slide per SVG."),
    ("Where conversion runs", "Extension: in your browser, with a WebAssembly engine. Web uploader and add-on: on the svgslid.es backend."),
    ("File retention", "Web uploader files are deleted after 7 days. Make a copy in Drive to keep one."),
    ("Gradients", "Kept by the web uploader. The extension and add-on fill the shape with the gradient's first colour."),
    ("Text", "Web uploader: converted to outlined shapes, not editable text. Extension and add-on: not converted."),
    ("Placement", "The extension fits each SVG to about a fifth of the slide, centred where you click. The add-on fits it to the current slide."),
    ("Editing", "Chrome extension: double-click any shape and click Edit Shape to move its points and curve handles on the slide. Works on Slides' own shapes, lines and WordArt by converting them to custom shapes first. SVG shapes made only of straight lines also support Slides' own Edit points."),
    ("Also works in", "Google Drawings"),
    ("Current versions", 'Chrome extension 1.2.0 (<a href="/whats-new">what&rsquo;s new</a>)'),
    ("Source code", f'<a href="{C.GITHUB}">github.com/joegelman/svg-to-g-slides</a> (MIT)'),
    ("Built by", 'Joe Gelman. Contact: <a href="mailto:joe@glmn.co">joe@glmn.co</a>'),
]

OK, PART, NO = "ok", "part", "no"
# (file stem, what it tests, (web status, web note), (extension status, extension note))
COMPAT = [
    ("01-single-path-icon", "One filled path", (OK, ""), (OK, "")),
    ("02-multi-colour-logo", "Circle, rounded rectangle and path in three colours", (OK, ""), (OK, "")),
    ("03-basic-shapes", "rect, circle, ellipse, polygon, polyline, line", (OK, "Lines and polylines become filled outline shapes"), (OK, "Lines and polylines become filled outline shapes")),
    ("04-stroked-line-icon", "Line icon with the stroke set on the root &lt;svg&gt; (Lucide and Feather style)", (OK, "Strokes become filled outline shapes"), (NO, "Nothing pastes")),
    ("05-arcs", "Arc commands (A and a)", (OK, ""), (OK, "")),
    ("06-nested-transforms", "translate, rotate and scale on nested groups", (OK, ""), (OK, "")),
    ("07-even-odd-holes", "fill-rule=&quot;evenodd&quot; cut-outs", (OK, ""), (OK, "")),
    ("08-linear-gradient", "Linear gradient fill", (OK, "Kept as a gradient"), (PART, "Solid fill in the first colour")),
    ("09-radial-gradient", "Radial gradient fill", (OK, "Kept as a gradient"), (PART, "Solid fill in the first colour; a white-centred gradient pastes white")),
    ("10-text", "&lt;text&gt; element", (OK, "Outlined into shapes, not editable text"), (NO, "Not converted")),
    ("11-css-classes-illustrator", "Colours set by CSS classes in a &lt;style&gt; block (Illustrator style)", (PART, "Shapes kept, colours become black"), (PART, "Shapes kept, colours become black")),
    ("12-figma-clip-path", "Figma-style frame clip and white background", (OK, "Frame clip and background skipped"), (OK, "Frame clip and background skipped")),
    ("13-clip-path-crop", "clip-path that crops a shape", (PART, "Clip ignored; the full shape shows"), (PART, "Clip ignored; the full shape shows")),
    ("14-mask", "mask that cuts a hole", (PART, "Mask ignored"), (PART, "Mask ignored")),
    ("15-use-symbol-sprite", "&lt;use&gt; referencing a &lt;symbol&gt; (icon sprites)", (NO, "Not converted"), (NO, "Not converted")),
    ("16-opacity", "fill-opacity", (PART, "Shapes kept, transparency lost"), (PART, "Shapes kept, transparency lost")),
    ("17-current-color", "stroke=&quot;currentColor&quot;", (PART, "Converted, but black instead of the inherited colour"), (NO, "Not converted")),
    ("18-pattern-fill", "Pattern fill", (PART, "Shape kept, filled black"), (PART, "Shape kept, filled black")),
    ("19-filter-shadow", "Drop-shadow filter", (PART, "Shape kept, shadow dropped"), (PART, "Shape kept, shadow dropped")),
    ("20-colour-formats", "rgb(), named, short hex and hsl() colours", (PART, "hsl() becomes black; the rest are exact"), (PART, "hsl() becomes black; the rest are exact")),
]

LABEL = {OK: "Works", PART: "Partly", NO: "Not converted"}

SPECS_CSS = """
.spec{max-width:56em;margin:0 auto;padding:0 20px}
.spec h2{font-size:clamp(22px,3vw,28px);margin:2.2em 0 .5em}
.spec p{color:var(--mute);line-height:1.6}
.spec a{color:var(--blue-ink,#0b57d0);text-underline-offset:3px}
.facts-t,.compat-t{width:100%;border-collapse:collapse;font-size:15px}
.facts-t th,.facts-t td,.compat-t th,.compat-t td{border-bottom:1px solid var(--rule);padding:10px 8px;text-align:left;vertical-align:top}
.facts-t th{width:12em;font-family:var(--display);font-weight:700}
.compat-t thead th{font-family:var(--display);font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:var(--mute)}
.compat-t td small{display:block;color:var(--mute);font-size:13px;margin-top:2px}
.compat-t code{font-size:12px}
.st{display:inline-block;font:700 12px/1 var(--display);padding:5px 9px;border-radius:999px;white-space:nowrap}
.st.ok{background:#e6f4ea;color:#137333}.st.part{background:#fef7e0;color:#8a5a00}.st.no{background:#fce8e6;color:#a50e0e}
.figs{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:18px 0}
.figs figure{margin:0}.figs img{width:100%;height:auto;border:1px solid var(--rule);border-radius:12px;background:#fff}
.figs figcaption{font-size:13px;color:var(--mute);margin-top:6px}
.dl{display:inline-block;margin-top:8px}
@media (max-width:720px){.figs{grid-template-columns:1fr}.compat-t{font-size:14px}.facts-t th{width:auto}}
"""


def _status(s, note):
    n = f"<small>{note}</small>" if note else ""
    return f'<span class="st {s}">{LABEL[s]}</span>{n}'


def specs_page(ctx):
    facts = "".join(f"<tr><th scope=\"row\">{k}</th><td>{v}</td></tr>" for k, v in FACTS)
    rows = "".join(
        f'<tr><td><a href="/static/specs/samples/{stem}.svg"><code>{stem}.svg</code></a><small>{what}</small></td>'
        f"<td>{_status(*web)}</td><td>{_status(*ext)}</td></tr>"
        for stem, what, web, ext in COMPAT)
    n_ok_web = sum(1 for r in COMPAT if r[2][0] == OK)
    n_ok_ext = sum(1 for r in COMPAT if r[3][0] == OK)
    body = f"""  <div class="wrap"><p class="crumb"><a href="/">SVG to Slides</a> &rsaquo; Specs</p></div>
  <section class="wrap phero">
    <div class="kick">Specs</div>
    <h1>SVG to Slides: product facts and SVG compatibility</h1>
    <p class="lede">What SVG to Slides is, what it costs, and which SVG features come through, tested on {len(COMPAT)} sample files.</p>
  </section>
  <div class="spec">
    <h2 id="facts">Product facts</h2>
    <table class="facts-t"><tbody>{facts}</tbody></table>

    <h2 id="compatibility">SVG compatibility</h2>
    <p>Tested {TESTED_ON} on {len(COMPAT)} small SVGs, one feature each. Fully supported: {n_ok_web} of {len(COMPAT)} on the web uploader, {n_ok_ext} of {len(COMPAT)} in the Chrome extension and add-on, which share one converter. Each file name links to the file.</p>
    <table class="compat-t"><thead><tr><th>Test file</th><th>Web uploader</th><th>Extension and add-on</th></tr></thead><tbody>{rows}</tbody></table>
    <a class="btn btn-ghost dl" href="/static/specs/svg-to-slides-test-files.zip" download>Download all {len(COMPAT)} test files (.zip)</a>

    <h2 id="evidence">What the extension pasted into Google Slides</h2>
    <div class="figs">
      <figure><picture><source type="image/webp" srcset="/static/specs/reference-renders.webp"><img src="/static/specs/reference-renders.png" width="580" height="464" alt="Reference renders of the 20 SVG test files in a five by four grid" loading="lazy"></picture><figcaption>The 20 test files as a browser renders them, in order.</figcaption></figure>
      <figure><picture><source type="image/webp" srcset="/static/specs/extension-paste-google-slides.webp"><img src="/static/specs/extension-paste-google-slides.png" width="580" height="335" alt="The same 20 SVG files pasted into a Google Slides slide by the SVG to Slides extension, showing gaps where files did not convert" loading="lazy"></picture><figcaption>The same files pasted into Google Slides with the extension's clipboard format. Gaps are files that didn't convert.</figcaption></figure>
    </div>

    <h2 id="method">How these were tested</h2>
    <p>Each file was converted with the code the extension and web uploader run. Extension output was pasted into a Google Slides deck. Web uploader output was read from the generated .pptx file. Several files mimic Illustrator, Figma and icon-library exports; they were written for this test, not exported from those apps.</p>
    <p>Have an SVG that doesn't convert? Send it to <a href="mailto:joe@glmn.co">joe@glmn.co</a>.</p>
  </div>
  <div class="wrap"><hr class="rule" style="margin-top:56px"></div>
  <section class="wrap close">
    <h2>Bring your SVGs into Google Slides&trade;.</h2>
    <div class="ctas"><a class="btn btn-primary" href="{P.cws('specs', 'close')}" data-cta="close"><img src="/static/chrome-glyph.svg" alt="">Add to Chrome, free</a><a class="btn btn-ghost" href="/convert">Use the web uploader</a></div>
  </section>"""
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": "SVG to Slides: product facts and SVG compatibility",
           "url": C.SITE + "/specs", "dateModified": TESTED_ON_ISO, "author": {"@type": "Person", "name": "Joe Gelman"},
           "publisher": {"@type": "Organization", "@id": C.SITE + "/#org", "name": "SVG to Slides", "url": C.SITE + "/"},
           "about": {"@type": "SoftwareApplication", "@id": C.SITE + "/#app", "name": "SVG to Slides"},
           "image": C.SITE + "/static/specs/extension-paste-google-slides.png"},
          ctx["crumbs"]([("Specs", "/specs")])]
    doc = P.shell(title="SVG to Slides Specs: Product Facts and SVG Compatibility",
                  desc=f"What SVG to Slides converts into Google Slides shapes, tested on {len(COMPAT)} SVG files: gradients, text, strokes, clip paths, masks, Illustrator and Figma exports.",
                  path="/specs", body=body, md="/specs.md", extra_css=SPECS_CSS, campaign="specs",
                  ld_block=ctx["ld_block"](ld), **ctx["common"])
    md = [f"# SVG to Slides: product facts and SVG compatibility", "", f"Tested {TESTED_ON}.", "", "## Product facts", ""]
    md += [f"- **{_plain(k)}:** {_plain(v)}" for k, v in FACTS]
    md += ["", "## SVG compatibility", "", "| Test file | What it tests | Web uploader | Extension and add-on |", "|---|---|---|---|"]
    md += [f"| {s}.svg | {_plain(w)} | {LABEL[a[0]]}{(': ' + _plain(a[1])) if a[1] else ''} | {LABEL[b[0]]}{(': ' + _plain(b[1])) if b[1] else ''} |"
           for s, w, a, b in COMPAT]
    md += ["", f"Test files: {C.SITE}/static/specs/svg-to-slides-test-files.zip", ""]
    return doc, "\n".join(md)


def _plain(s):
    import re
    return html.unescape(re.sub(r"<[^>]+>", "", s))
