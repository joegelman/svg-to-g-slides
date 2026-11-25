"""Docs content: Reference and Technical Notes.

The command and shortcut tables are data (COMMANDS, EDITOR_KEYS) taken from the
extension source for 1.3.0: slides-bridge.js SHORTCUT_LABEL and rail-kit.js
commandList(). When a shortcut changes there, change it here.
"""
import html
import re

import site_content as C

A13 = "SVG to Slides Chrome extension, version 1.3.0 and later"
A12 = "SVG to Slides Chrome extension, version 1.2.0 and later"
AALL = "SVG to Slides Chrome extension, versions 1.0.0 through 1.4.0"
AWEB = "SVG to Slides Web Uploader"
AADD = "SVG to Slides Workspace Add-on for Google Slides"

# (id, group, command, Mac keys, what it does, needs, topic, whose key)
# whose: "ext" = handled by the extension; "slides" = Slides' own shortcut, listed for convenience.
COMMANDS = [
    ("toggle-toolbar", "anytime", "Show or hide the toolbar", "Option+\\", "Opens or closes the toolbar.", "Nothing", "toolbar", "ext"),
    ("palette", "anytime", "Command palette", "Command+\\", "Lists every command with its shortcut.", "Nothing", "command-palette", "ext"),
    ("layers", "anytime", "Show or hide Layers", "Option+1", "Opens or closes the Layers panel.", "Nothing", "layers", "ext"),
    ("pen", "anytime", "Pen", "Option+Shift+P", "Draws new shapes, or opens the editor on the selection with the pen active.", "Nothing", "pen", "ext"),
    ("theme-builder", "anytime", "Theme builder, and back", "Option+Shift+M", "Opens Slides' theme builder on the slide's layout, or returns to the slide.", "Nothing", "theme-objects", "ext"),
    ("edit", "anytime", "Edit Shape", "", "Opens the point editor on the selection. Double-click a shape, then click Edit Shape.", "A shape", "edit-shape", "ext"),
    ("direct-select", "anytime", "Select inside a group", "", "Command-click selects the innermost object under the pointer. Shift+Command-click adds.", "Nothing", "layers#direct-select", "ext"),
    ("undo", "anytime", "Undo one of the extension's changes", "Command+Z", "Undoes a multi-step change in one press.", "Right after the change", "undo-redo", "ext"),
    ("redo", "anytime", "Redo it", "Shift+Command+Z", "Redoes it in one press. Command+Y does the same.", "Right after an undo", "undo-redo", "ext"),

    ("align-left", "align", "Align left", "Option+A", "Aligns left edges. One object: to the slide's left edge.", "One object or more", "align-distribute", "ext"),
    ("align-centre", "align", "Align centres horizontally", "Option+H", "Aligns centres on a vertical line. One object: centres it on the page.", "One object or more", "align-distribute", "ext"),
    ("align-right", "align", "Align right", "Option+D", "Aligns right edges. One object: to the slide's right edge.", "One object or more", "align-distribute", "ext"),
    ("align-top", "align", "Align top", "Option+W", "Aligns top edges. One object: to the slide's top edge.", "One object or more", "align-distribute", "ext"),
    ("align-middle", "align", "Align middles vertically", "Option+V", "Aligns middles on a horizontal line. One object: centres it on the page.", "One object or more", "align-distribute", "ext"),
    ("align-bottom", "align", "Align bottom", "Option+S", "Aligns bottom edges. One object: to the slide's bottom edge.", "One object or more", "align-distribute", "ext"),
    ("distribute-h", "align", "Distribute horizontal spacing", "Option+Shift+H", "Evens out the horizontal gaps.", "Three objects or more", "align-distribute", "ext"),
    ("distribute-v", "align", "Distribute vertical spacing", "Option+Shift+V", "Evens out the vertical gaps.", "Three objects or more", "align-distribute", "ext"),

    ("union", "combine", "Union", "Option+Shift+U", "One shape covering everything the selected shapes cover.", "Two shapes or more", "combine-shapes", "ext"),
    ("subtract", "combine", "Subtract", "Option+Shift+S", "The bottom shape with the shapes above it cut out.", "Two shapes or more", "combine-shapes", "ext"),
    ("intersect", "combine", "Intersect", "Option+Shift+I", "Only the area where the shapes overlap.", "Two shapes or more", "combine-shapes", "ext"),
    ("exclude", "combine", "Exclude", "Option+Shift+E", "Everything except the area where the shapes overlap.", "Two shapes or more", "combine-shapes", "ext"),

    ("group", "group", "Group", "Command+Option+G", "Groups the selection.", "Two objects or more", "toolbar", "slides"),
    ("ungroup", "group", "Ungroup", "Shift+Command+Option+G", "Ungroups the selected group.", "A group", "toolbar", "slides"),
    ("mask", "group", "Mask image with shape", "Option+Shift+K", "The shape on top cuts out the picture under it. On a masked picture or its group, opens the picture for moving and resizing under the mask.", "One image and one shape or group, or a masked picture", "mask-image", "ext"),

    ("outline-stroke", "outline", "Outline stroke", "Option+Command+O", "Turns a stroke into a filled shape.", "A shape or line with a stroke", "outline-stroke-text", "ext"),
    ("outline-text", "outline", "Outline text", "Option+Command+T", "Turns text into shapes.", "An object with text", "outline-stroke-text", "ext"),
    ("restore-text", "outline", "Restore outlined text", "Option+Command+T", "Puts outlined text back as live text.", "Text outlined on this computer", "outline-stroke-text#restore", "ext"),

    ("fill", "paint", "Fill colour", "Option+Shift+F", "Opens the colour panel on the fill. With text highlighted, sets the text colour. With nothing selected, opens Replace a colour.", "A shape, highlighted text, or nothing", "fill-stroke", "ext"),
    ("stroke", "paint", "Stroke colour", "Option+Shift+L", "Opens the colour panel on the stroke.", "A shape or line", "fill-stroke", "ext"),
    ("stroke-toggle", "paint", "Stroke on / off", "Option+Shift+/", "Removes the stroke or puts it back.", "A shape or line", "fill-stroke#weight", "ext"),
    ("stroke-thinner", "paint", "Thinner stroke", "Option+Shift+[", "Steps the stroke weight down.", "A shape or line", "fill-stroke#weight", "ext"),
    ("stroke-thicker", "paint", "Thicker stroke", "Option+Shift+]", "Steps the stroke weight up.", "A shape or line", "fill-stroke#weight", "ext"),
    ("stroke-centre", "paint", "Centre stroke", "", "Puts the stroke back on the outline.", "A closed shape with a stroke", "outline-stroke-text#position", "ext"),
    ("stroke-inside", "paint", "Inside stroke", "", "Moves the stroke inside the outline.", "A closed shape with a stroke", "outline-stroke-text#position", "ext"),
    ("stroke-outside", "paint", "Outside stroke", "", "Moves the stroke outside the outline.", "A closed shape with a stroke", "outline-stroke-text#position", "ext"),

    ("front", "arrange", "Bring to front", "Shift+Command+Up Arrow", "Moves the selection to the top of the stack.", "An object", "layers", "slides"),
    ("forward", "arrange", "Bring forward", "Command+Up Arrow", "Moves the selection up one place.", "An object", "layers", "slides"),
    ("backward", "arrange", "Send backward", "Command+Down Arrow", "Moves the selection down one place.", "An object", "layers", "slides"),
    ("back", "arrange", "Send to back", "Shift+Command+Down Arrow", "Moves the selection to the bottom of the stack.", "An object", "layers", "slides"),
    ("rotate-15", "arrange", "Rotate 15° left or right", "Option+Left Arrow", "Rotates the selection. Option+Right Arrow rotates the other way.", "An object", "fill-stroke#transform", "slides"),
    ("rotate-1", "arrange", "Rotate 1° left or right", "Option+Shift+Left Arrow", "Rotates in fine steps. Option+Shift+Right Arrow rotates the other way.", "An object", "fill-stroke#transform", "slides"),
    ("larger", "arrange", "Make larger", "Command+Control+K", "Resizes the selection up.", "An object", "fill-stroke#transform", "slides"),
    ("smaller", "arrange", "Make smaller", "Command+Control+J", "Resizes the selection down.", "An object", "fill-stroke#transform", "slides"),
]
GROUPS = [
    ("anytime", "Tools and panels", "These work whether or not anything is selected."),
    ("align", "Align and distribute", "With objects selected. Not while typing in a text box."),
    ("combine", "Combine", "With two or more shapes selected."),
    ("group", "Group and mask", ""),
    ("outline", "Outline", ""),
    ("paint", "Fill and stroke", ""),
    ("arrange", "Arrange, rotate and resize", "These are Google Slides' own shortcuts. The toolbar and the command palette list them, and Slides carries them out."),
]
# (action, Mac keys or a phrase)
EDITOR_KEYS = [
    ("Select tool", "<<V>>"),
    ("Pen tool", "<<P>>"),
    ("Move a point or handle in 45° steps", "Hold <<Shift>> while dragging"),
    ("Move one curve handle on its own", "Hold <<Option>> while dragging it"),
    ("Switch a point between smooth and corner", "Double-click the point"),
    ("Select all points", "<<Command+A>>"),
    ("Delete selected points. In the pen, remove the last point.", "<<Delete>>"),
    ("Nudge", "Arrow keys. <<Shift>> for ten times the step."),
    ("Undo, redo", "<<Command+Z>>, <<Shift+Command+Z>>"),
    ("Zoom in, zoom out, 100%", "<<Command+Plus>>, <<Command+Minus>>, <<Command+0>>. Or pinch."),
    ("Pan", "Hold <<Spacebar>> and drag, or scroll"),
    ("Show or hide the grid", "<<Command+'>>"),
    ("Ignore snapping for one move", "Hold <<Command>>"),
    ("Change a number by dragging", "Hold <<Option>> and drag across the field. <<Shift>> for steps of ten."),
    ("Round corners in 10 pixel steps", "Hold <<Shift>> while dragging a corner circle"),
    ("Scale in proportion, or from the centre", "<<Shift>>, <<Option>> while dragging the box"),
    ("Skew", "<<Command>> and drag an edge of the box"),
    ("Rotate", "<<Command>> and drag a corner of the box"),
    ("Pen: close the shape", "Click the first point"),
    ("Pen: leave the path open", "<<Enter>> or <<Esc>>"),
    ("Done", "<<Enter>>, or <<Esc>> with nothing selected"),
]


def _keys_html(mac, cx):
    import site_docs as D
    if not mac:
        return ""
    return D.kbd_html(mac)


def shortcuts_html(cx):
    import site_docs as D
    out = []
    for gid, gname, gnote in GROUPS:
        rows = [c for c in COMMANDS if c[1] == gid]
        out.append(f'<h2 id="{gid}">{gname}<a class="hx" href="#{gid}" aria-label="Link to this section">#</a></h2>')
        if gnote:
            out.append(f"<p>{D.inline(gnote, cx)}</p>")
        trs = []
        for cid, _, name, mac, what, needs, topic, whose in rows:
            if not mac:
                mac_c = "Double-click, then <b>Edit Shape</b>" if cid == "edit" else ("<kbd>COMMAND</kbd>-click" if cid == "direct-select" else "")
                win_c = "Double-click, then <b>Edit Shape</b>" if cid == "edit" else ("<kbd>CTRL</kbd>-click" if cid == "direct-select" else "")
                if not mac_c:
                    continue
            else:
                mac_c = f"<kbd>{html.escape(mac.upper())}</kbd>"
                win_c = f"<kbd>{html.escape(D.win_keys(mac).upper())}</kbd>"
            slug, anchor, _l = cx.xref(topic)
            trs.append(f'<tr id="k-{cid}"><td><a class="x" href="{D.url(slug)}{"#" + anchor if anchor else ""}">{html.escape(name)}</a></td><td>{mac_c}</td><td>{win_c}</td></tr>')
        out.append('<div class="tw"><table class="t"><thead><tr><th>Command</th><th>Mac</th><th>Windows</th></tr></thead><tbody>' + "".join(trs) + "</tbody></table></div>")
    out.append('<h2 id="editor">In Edit Shape and the pen<a class="hx" href="#editor" aria-label="Link to this section">#</a></h2>')
    out.append("<p>These apply while the editor is open. On Windows use <kbd>CTRL</kbd> for <kbd>COMMAND</kbd>, <kbd>ALT</kbd> for <kbd>OPTION</kbd> and <kbd>BACKSPACE</kbd> for <kbd>DELETE</kbd>.</p>")
    trs = "".join(f"<tr><td>{D.inline(a, cx)}</td><td>{D.inline(k, cx)}</td></tr>" for a, k in EDITOR_KEYS)
    out.append('<div class="tw"><table class="t"><thead><tr><th>Action</th><th>Keys</th></tr></thead><tbody>' + trs + "</tbody></table></div>")
    return "\n".join(out)


def shortcuts_md(cx):
    import site_docs as D
    out = []
    for gid, gname, gnote in GROUPS:
        out += [f"## {gname}", ""]
        if gnote:
            out += [gnote, ""]
        out += ["| Command | Mac | Windows |", "|---|---|---|"]
        for cid, _, name, mac, *_ in [c for c in COMMANDS if c[1] == gid]:
            if mac:
                out.append(f"| {name} | {mac} | {D.win_keys(mac)} |")
            elif cid == "edit":
                out.append(f"| {name} | Double-click, then Edit Shape | Double-click, then Edit Shape |")
            elif cid == "direct-select":
                out.append(f"| {name} | Command-click | Ctrl-click |")
        out.append("")
    out += ["## In Edit Shape and the pen", "", "On Windows use Ctrl for Command, Alt for Option and Backspace for Delete.", "", "| Action | Keys |", "|---|---|"]
    out += [f"| {D.plain(a, cx)} | {D.plain(k, cx)} |" for a, k in EDITOR_KEYS]
    return "\n".join(out)


def commands_html(cx):
    import site_docs as D
    out = []
    for gid, gname, _ in GROUPS:
        rows = [c for c in COMMANDS if c[1] == gid]
        out.append(f'<h2 id="{gid}">{gname}<a class="hx" href="#{gid}" aria-label="Link to this section">#</a></h2>')
        trs = []
        for cid, _, name, mac, what, needs, topic, whose in rows:
            slug, anchor, label = cx.xref(topic)
            key = f"<kbd>{html.escape(mac.upper())}</kbd>" if mac else ""
            by = "" if whose == "ext" else " <i>Slides' own.</i>"
            trs.append(f'<tr id="c-{cid}"><td><b>{html.escape(name)}</b></td><td>{D.text(what)}{by}</td><td>{html.escape(needs)}</td><td>{key}</td>'
                       f'<td><a class="x" href="{D.url(slug)}{"#" + anchor if anchor else ""}">{html.escape(label)}</a></td></tr>')
        out.append('<div class="tw"><table class="t"><thead><tr><th>Command</th><th>What it does</th><th>Needs selected</th><th>Shortcut (Mac)</th><th>Topic</th></tr></thead><tbody>' + "".join(trs) + "</tbody></table></div>")
    return "\n".join(out)


def commands_md(cx):
    import site_docs as D
    out = []
    for gid, gname, _ in GROUPS:
        out += [f"## {gname}", "", "| Command | What it does | Needs selected | Shortcut (Mac) |", "|---|---|---|---|"]
        out += [f"| {n} | {w} | {nd} | {m} |" for _c, _g, n, m, w, nd, _t, _w in [c for c in COMMANDS if c[1] == gid]]
        out.append("")
    return "\n".join(out)


# ---------------------------------------------------------- compatibility
def _compat():
    import site_specs as S
    plain = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s))
    groups = {S.OK: [], S.PART: [], S.NO: []}
    for stem, what, web, ext in S.COMPAT:
        groups[ext[0]].append((plain(what), plain(ext[1]), web[0], plain(web[1])))
    return S, groups


def compat_html(cx):
    import site_docs as D
    S, g = _compat()
    out = [f"<p>Tested {S.TESTED_ON} on {len(S.COMPAT)} sample files, one feature each. The per-file table, with every sample file to download, is on the <a href=\"/specs#compatibility\">Specs page</a>.</p>"]
    for key, title, hid in ((S.OK, "Converts", "works"), (S.PART, "Converts in part", "partly"), (S.NO, "Does not convert", "not-converted")):
        out.append(f'<h2 id="{hid}">{title}<a class="hx" href="#{hid}" aria-label="Link to this section">#</a></h2>')
        trs = "".join(
            f"<tr><td>{D.text(what)}</td><td>{D.text(note) or 'Converts.'}</td><td>{S.LABEL[w]}{'. ' + D.text(wn) if wn else ''}</td></tr>"
            for what, note, w, wn in g[key])
        out.append('<div class="tw"><table class="t"><thead><tr><th>SVG feature</th><th>Chrome extension and add-on</th><th>Web Uploader</th></tr></thead><tbody>' + trs + "</tbody></table></div>")
    return "\n".join(out)


def compat_md(cx):
    S, g = _compat()
    out = [f"Tested {S.TESTED_ON} on {len(S.COMPAT)} sample files. Per-file table and sample files: {C.SITE}/specs.md", ""]
    for key, title in ((S.OK, "Converts"), (S.PART, "Converts in part"), (S.NO, "Does not convert")):
        out += [f"## {title}", "", "| SVG feature | Chrome extension and add-on | Web Uploader |", "|---|---|---|"]
        out += [f"| {what} | {note or 'Converts.'} | {S.LABEL[w]}{'. ' + wn if wn else ''} |" for what, note, w, wn in g[key]]
        out.append("")
    return "\n".join(out)


# ------------------------------------------------------------------ index
_IX = {}


def index_prepare(topics, order):
    import site_docs as D
    entries = {}
    for s in order:
        t = topics[s]
        if s == "a-z-index":
            continue
        cx = D.Ctx(topics, s)
        label = t.get("nav") or t["title"]
        terms = list(t.get("keys", []))
        for k in terms:
            term, _, anchor = k.partition("#")
            entries.setdefault(term.strip(), [])
            ref = (s, anchor, label)
            if ref not in entries[term.strip()]:
                entries[term.strip()].append(ref)
    _IX.clear()
    _IX.update(entries)


def _ix_sorted():
    key = lambda t: re.sub(r"[^a-z0-9 ]", "", t.lower())
    return sorted(_IX.items(), key=lambda kv: key(kv[0]))


def index_html(cx):
    import site_docs as D
    letters = {}
    for term, refs in _ix_sorted():
        first = re.sub(r"[^A-Za-z0-9]", "", term)[:1].upper() or "#"
        first = "#" if first.isdigit() else first
        letters.setdefault(first, []).append((term, refs))
    az = "".join(f'<a href="#ix-{l.lower() if l != "#" else "num"}">{l}</a>' if l in letters else f"<span>{l}</span>" for l in ["#"] + [chr(c) for c in range(65, 91)])
    out = [f'<nav class="az" aria-label="Letters">{az}</nav>',
           '<input class="ixf" type="search" placeholder="Type to narrow the index" aria-label="Narrow the index" autocomplete="off">',
           '<div class="ix">']
    for l in sorted(letters, key=lambda x: (x != "#", x)):
        hid = "ix-" + (l.lower() if l != "#" else "num")
        out.append(f'<section data-l><h2 id="{hid}">{l}</h2><dl>')
        for term, refs in letters[l]:
            links = ", ".join(f'<a href="{D.url(s)}{"#" + a if a else ""}">{html.escape(lab)}</a>' for s, a, lab in refs)
            out.append(f"<div data-t><dt>{D.text(term)}</dt><dd>{links}</dd></div>")
        out.append("</dl></section>")
    out.append("</div>")
    out.append("<script>(function(){var f=document.querySelector('.ixf');if(!f)return;f.addEventListener('input',function(){var q=f.value.trim().toLowerCase();"
               "document.querySelectorAll('.ix [data-t]').forEach(function(e){e.style.display=!q||e.textContent.toLowerCase().indexOf(q)>-1?'':'none';});"
               "document.querySelectorAll('.ix [data-l]').forEach(function(s){var any=[].some.call(s.querySelectorAll('[data-t]'),function(e){return e.style.display!=='none';});s.style.display=any?'':'none';});});})();</script>")
    return "\n".join(out)


def index_md(cx):
    import site_docs as D
    out = []
    for term, refs in _ix_sorted():
        out.append(f"- {term}: " + ", ".join(f"[{lab}]({C.SITE}{D.url(s)}.md{'#' + a if a else ''})" for s, a, lab in refs))
    return "\n".join(out)


def index_anchors():
    return {"ix-" + c for c in "abcdefghijklmnopqrstuvwxyz"} | {"ix-num"}


INCLUDES = {
    "shortcuts": {"html": shortcuts_html, "md": shortcuts_md, "anchors": {g[0] for g in GROUPS} | {"editor"} | {"k-" + c[0] for c in COMMANDS}},
    "commands": {"html": commands_html, "md": commands_md, "anchors": {g[0] for g in GROUPS} | {"c-" + c[0] for c in COMMANDS}},
    "compat": {"html": compat_html, "md": compat_md, "anchors": {"works", "partly", "not-converted"}},
    "index": {"html": index_html, "md": index_md, "anchors": index_anchors(), "prepare": index_prepare},
}

TOPICS = [
    # ------------------------------------------------------------------ Reference
    dict(
        slug="keyboard-shortcuts", book="reference", kind="Reference", nav="Keyboard shortcuts",
        title="Keyboard shortcuts",
        desc="Every SVG to Slides keyboard shortcut for Google Slides on Mac and Windows: toolbar, Layers, pen, align, distribute, combine, mask, outline, stroke, and the Edit Shape editor.",
        applies=[A13 + ". Editor keys also apply to version 1.2.0 unless they name a 1.3.0 tool."],
        summary="All shortcuts, with the Mac and Windows keys side by side. The extension's own shortcuts work while objects are selected and you are not typing in a text box. Five of them work at any time.",
        keys=["keyboard shortcuts", "shortcuts", "Windows shortcuts", "Mac shortcuts", "editor keys#editor"],
        howto=False,
        body="""
!!! Note: The extension's shortcuts are off while the cursor is in a text box, so that typing <<Option+Shift>> characters still works. Click the slide or an object first.

@@shortcuts

## Where the keys come from {#origin}

Align and distribute use the keys Figma uses. Rotate, resize, arrange, group and ungroup are Google Slides' own shortcuts. The rest are the extension's.
""",
        see=["commands", "command-palette", "toolbar", "conventions#keys"],
    ),
    dict(
        slug="commands", book="reference", kind="Reference", nav="Command reference",
        title="Command reference",
        desc="Reference for every SVG to Slides command in Google Slides: what it does, what must be selected, its shortcut, and the topic that explains it.",
        applies=[A13],
        summary="Every command the toolbar and the command palette offer, by group, with what each one needs selected.",
        keys=["commands, list of", "command reference"],
        howto=False,
        body="""
@@commands

## Messages {#messages}

When a command cannot run, the extension shows a short message under the toolbar that says what to select. Examples: "Select two or more objects to group", "Select three or more objects to distribute", "Nothing selected has text".
""",
        see=["keyboard-shortcuts", "command-palette", "toolbar", "limits"],
    ),
    dict(
        slug="svg-compatibility", book="reference", kind="Reference", nav="SVG feature support",
        title="SVG feature support",
        desc="Which SVG features convert to Google Slides shapes: paths, arcs, transforms, gradients, text, strokes, clip paths, masks, CSS classes, patterns, filters.",
        applies=[AALL, AADD, AWEB],
        summary="Paths, basic shapes, arcs, nested transforms and even-odd cut-outs convert in every product. Gradients convert in the Web Uploader and, since version 1.4.0, in the extension, which also keeps transparency. Text converts only in the Web Uploader. Masks, patterns and filters do not convert.",
        keys=["SVG feature support", "compatibility", "gradients#partly", "clip paths#partly", "masks, SVG#partly", "CSS classes#partly", "currentColor#not-converted", "text, SVG#not-converted", "use and symbol#not-converted", "opacity#partly", "pattern fills#partly", "filters#partly", "hsl colours#partly", "arcs#works", "transforms#works"],
        howto=False,
        body="""
@@compat

## Reading the table {#reading}

The extension column is for version 1.4.0. Version 1.3.1 added outline icon sets, colours from CSS classes, clip paths and use with symbol. Version 1.4.0 added gradients and transparency. The Workspace Add-on runs the earlier converter: it fills a gradient with its first colour and does not keep transparency. See [[how-conversion-works#javascript]].

## Getting a file to convert {#workarounds}

| Problem | What to do |
|---|---|
| A gradient arrives as one colour | Update the extension to version 1.4.0, which keeps gradients, or use the [[web-uploader]]. See [[kb/gradient-becomes-solid-colour]]. |
| Text is missing | Convert the text to outlines in your design tool before exporting, or use the [[web-uploader]]. |
| A line icon inserts nothing | Update the extension to version 1.3.1 or later. See [[kb/line-icon-inserts-nothing]]. |
| Colours arrive black | Export with colours written on each element. See [[kb/colours-arrive-black]]. |
| A masked shape shows in full | Apply the mask in your design tool before exporting, or mask it on the slide with [[mask-image]] and [[combine-shapes]]. |

Have a file that does not convert? Send it to the address on the [Support](/support) page.
""",
        see=["how-conversion-works", "insert-svg", "web-uploader", "limits", ("Specs: tested compatibility table", "/specs#compatibility")],
    ),
    dict(
        slug="permissions-privacy", book="reference", kind="Reference", nav="Permissions and data",
        title="Permissions and data handling",
        desc="What the SVG to Slides Chrome extension, Web Uploader and add-on can access: Chrome permissions by version, what is stored on your computer, and what is sent over the network.",
        applies=[AALL, AWEB, AADD],
        summary="The extension has no access to your Google account and runs only on Google Slides editor pages. Version 1.3.0 holds one Chrome permission, storage, and converts every file inside your browser.",
        keys=["permissions", "privacy", "storage permission#storage", "host permission#by-version", "data handling", "network requests#network", "Google account access"],
        howto=False,
        body="""
## Chrome permissions by version {#by-version}

| Version | Chrome permissions | Where SVG files are converted |
|---|---|---|
| 1.3.0 | storage | In your browser, always. |
| 1.2.0 | storage, and one host permission for the svgslid.es converter | In your browser. The converter on the server was a fallback if in-browser conversion was unavailable. |
| 1.0.1 | One host permission for the svgslid.es converter | As 1.2.0. |

No version requests a Google sign-in or any Google account permission. The extension cannot read your Drive or reach your presentations through Google's API.

## What the extension reads {#reads}

- The .svg files you drop on the slide.
- When you use Edit Shape or a shape command, the objects you selected on the open slide: their outlines, fill and stroke. This is read in your browser.

## What is stored on your computer {#storage}

The storage permission keeps these items in Chrome on the computer you use. None of them is part of the presentation.

| Item | Used by |
|---|---|
| Whether the toolbar is open or closed, and whether Layers is open | [[toolbar]] |
| Snapping settings | [[snapping]] |
| Layer names | [[layers#stored]] |
| Recent colours | [[fill-stroke#panel]] |
| The original text of outlined text | [[outline-stroke-text#restore]] |
| The original outline of shapes whose stroke was moved inside or outside | [[outline-stroke-text#position]] |
| Whether the update note has been shown | [[install#updates]] |

## Network requests in version 1.3.0 {#network}

SVG files are not uploaded. The extension makes one kind of network request: **Outline text** downloads the font it needs from Google Fonts. The request names the font family, weight and style and carries nothing from the presentation. See [[outline-stroke-text#fonts]].

## Web Uploader {#web-uploader}

- The SVG files you upload are sent to the svgslid.es server, held while the request runs, and deleted when it finishes.
- The converted file is stored in Google Drive for 7 days and shared with anyone who has the link.
- If you type a Google account address, it is used once, to share the file to that account.

## Workspace Add-on {#add-on}

- The add-on reads the current presentation's page size, shows its dialog, and calls the svgslid.es converter. It has no Drive access.
- The files you select are sent to the server, held in memory while the request runs, and not kept.
- The result is written to your clipboard. You paste it.

!!! Note: The [Privacy Policy](/privacy) is the governing statement for all three products. This topic summarises it and adds the per-version detail.
""",
        see=["install", "how-shapes-reach-the-slide", "release-notes", ("Privacy Policy", "/privacy"), ("Terms", "/terms")],
    ),
    dict(
        slug="limits", book="reference", kind="Reference", nav="Limits and known issues",
        title="Limits and known issues",
        desc="Known limits of SVG to Slides in one list: files per drop, text, masks, combine and outline limits, colour and gradient limits, rotated masks, undo, 7-day links.",
        applies=[A13, AWEB, AADD],
        summary="The limits stated across this library, gathered in one place. Each one links to the topic that explains it.",
        keys=["limits", "known issues", "maximum files"],
        howto=False,
        body="""
## Inserting {#inserting}

| Limit | Detail |
|---|---|
| Files per drop | 25 in the extension. See [[insert-svg#several]]. |
| Where shapes land | On the slide you have open. The extension and the add-on cannot create slides. |
| Gradients | Kept by the extension since version 1.4.0 and by the Web Uploader. First colour only in the add-on and in earlier versions of the extension. `gradientTransform` is not applied. |
| SVG text | Not converted by the extension or the add-on. Outlined by the Web Uploader. |
| Masks, patterns, filters | Not converted. See [[svg-compatibility]]. |

## Shape tools {#shape-tools}

| Limit | Detail |
|---|---|
| Combine and outline | Gradients, pattern fills, transparency and shadows are not carried into the result. Images, video and charts are refused. |
| Mask | Rotated images are not supported yet. Text must be outlined first. A fill on a whole mask group is refused. See [[mask-image#limits]]. |
| Gradient on text with several styles | The object is replaced, so its animation and link are not kept. See [[fill-stroke#applied]]. |
| Stroke weight | A weight that is not one of Slides' own replaces the object. See [[fill-stroke#weight]]. |
| Gradient stops | One opacity for the whole fill. Slides does not keep an opacity per stop. |
| Replace a colour, all slides | Colours of slides far down a long filmstrip may not be listed until you scroll to them. See [[fill-stroke#replace]]. |
| Pen | Point by point only. No freehand mode. |
| Skew | Available in Edit Shape only. |
| Layers | Only top-level rows can be dragged to restack. |
| Edit Shape | **Done** replaces the object, so animations and links on the original are not kept. See [[edit-shape#done]]. |
| Converting Slides' own shapes | One-way. See [[convert-slides-shapes]]. |

## Kept on one computer {#local}

Layer names, snapping settings, recent colours, the memory that restores outlined text, and the memory of stroke position are kept on the computer you used. They do not travel with the presentation. Hiding an object in Layers affects only your view and ends when the page is reloaded. See [[permissions-privacy#storage]].

## Undo {#undo}

One-press undo applies right after one of the extension's changes. If you change the slide in between, Slides' own undo takes over. See [[undo-redo#slides-undo]].

## Web Uploader and add-on {#other}

| Limit | Detail |
|---|---|
| Web Uploader links | Deleted after 7 days. Make a copy to keep the file. |
| Add-on gradients | First colour only. |
| Add-on insert | Always ends with <<Command+V>>. A web page cannot paste for you. |
""",
        see=["svg-compatibility", "kb", "release-notes/1-4-0#limits", "release-notes/1-3-0#limits"],
    ),
    dict(
        slug="glossary", book="reference", kind="Reference", nav="Glossary",
        title="Glossary",
        desc="Glossary of SVG to Slides terms: custom shape, polyline, corner point, smooth point, handle, mask, theme object, still copy, stroke position.",
        applies=["All SVG to Slides documentation"],
        summary="Terms used in this library, in alphabetical order.",
        keys=["glossary", "terms"],
        howto=False,
        body="""
### Add-on {#add-on}
The SVG to Slides Workspace Add-on. It runs inside Google Slides from the Extensions menu. See [[add-on]].

### Box {#box}
The frame with handles around the selection in Edit Shape. Dragging it scales, stretches, skews or rotates. See [[edit-shape#smart-box]].

### Combine {#combine}
To make one shape from several with Union, Subtract, Intersect or Exclude. See [[combine-shapes]].

### Command palette {#command-palette}
A searchable list of every command, opened with <<Command+\\>>. See [[command-palette]].

### Corner point {#corner-point}
A point where the outline turns sharply. Drawn as a square in Edit Shape. Compare *smooth point*.

### Custom shape {#custom-shape}
A Slides shape defined by its own outline, as opposed to a preset from the shape menu. Every shape SVG to Slides inserts is a custom shape or a polyline.

### Flatten {#flatten}
What Slides does to an SVG placed on a slide without SVG to Slides: it turns the drawing into a picture made of pixels.

### Handle {#handle}
One of the two control points beside a smooth point. Dragging a handle changes the curve on that side of the point.

### Layout {#layout}
A slide design in the theme that slides are based on. Objects on a layout appear on every slide that uses it. See [[theme-objects]].

### Mask {#mask}
A shape used to cut a picture so that the picture shows only inside the shape. See [[mask-image]].

### Master {#master}
The top level of a Slides theme. Objects on the master appear on every layout and slide. See [[theme-objects]].

### Native shape {#native-shape}
A shape that Slides treats as its own: it can be selected, filled, resized, grouped, used in themes and copied to Google Drawings.

### Outline {#outline}
As a verb: to turn a stroke or text into filled shapes. As a noun: the path that defines a shape's edge. See [[outline-stroke-text]].

### Path {#path}
In an SVG file, a sequence of lines and curves. Each path becomes one Slides shape.

### Pill {#pill}
The small dark panel under the selection in Edit Shape that holds width, height, rotation and corner radius.

### Polyline {#polyline}
A Slides shape made of straight segments, on which Slides' own Edit points command works. See [[edit-points-and-polylines]].

### Scrub {#scrub}
To change a number by holding <<Option>> and dragging across its field.

### Smooth point {#smooth-point}
A point where the outline curves through without a corner. Drawn as a circle in Edit Shape. It has two handles.

### Snapping {#snapping}
Pulling a point onto a nearby point, pixel or grid line as you place or drag it. See [[snapping]].

### Still copy {#still-copy}
A picture of the slide that the extension shows while a change takes several steps, so that only the result is seen. See [[undo-and-still-copy]].

### Stroke position {#stroke-position}
Whether a stroke sits inside, on, or outside a shape's outline. See [[outline-stroke-text#position]].

### Theme object {#theme-object}
An object drawn on a slide that belongs to the slide's layout or master. It cannot be changed on the slide. See [[theme-objects]].

### Toolbar {#toolbar}
The strip of buttons the extension adds at the left edge of the slide canvas. See [[toolbar]].

### Web Uploader {#web-uploader}
The page at svgslid.es/convert that converts SVG files to a Drive file. See [[web-uploader]].
""",
        see=["a-z-index", "conventions"],
    ),
    dict(
        slug="a-z-index", book="reference", kind="Reference", nav="Index",
        title="Index",
        desc="Alphabetical index of the SVG to Slides documentation. Find a tool, command, shortcut, message or term and go to the section that covers it.",
        applies=["All SVG to Slides documentation"],
        summary="Every tool, command and term in this library, in alphabetical order. Each entry goes to the section that covers it.",
        keys=[],
        howto=False,
        body="""
@@index
""",
        see=["glossary", "keyboard-shortcuts", "kb"],
    ),

    # ------------------------------------------------------------ Technical Notes
    dict(
        slug="how-conversion-works", book="technical", kind="Technical note", nav="How conversion works",
        title="How conversion works",
        desc="How SVG to Slides converts an SVG into Google Slides shapes: paint, shapes to paths, arcs to curves, stroke outlines, transforms, and the JavaScript converter.",
        applies=[AALL, AWEB, AADD],
        summary="Conversion turns every drawable element of the SVG into a path, and every path into one Slides shape with one fill. The extension and the add-on write the shapes in Slides' own form. The Web Uploader writes a presentation file.",
        keys=["conversion", "converter", "JavaScript converter#javascript", "Pyodide#javascript", "WebAssembly#javascript", "arcs to curves#stages", "strokes to outlines#stages", "DrawingML#outputs"],
        howto=False,
        body="""
## Stages {#stages}

| Stage | What happens |
|---|---|
| 1. Read | The SVG is parsed. Definitions, clip paths and masks are set aside, and so is a rectangle that only fills the canvas as a background. |
| 2. Paint | Fill and stroke are worked out for each element, including values inherited from the groups around it. |
| 3. Shapes to paths | `rect`, `circle`, `ellipse`, `line`, `polyline` and `polygon` become path data. |
| 4. Arcs to curves | Arc commands are converted into cubic Bézier curves. |
| 5. Strokes to outlines | A stroke with a width is expanded into a filled outline, because the shape that lands has one fill. |
| 6. Transforms | `translate`, `rotate` and `scale` on the element and on its groups are applied to the points. |
| 7. Write | Each path becomes one shape with a tight bounding box. Shapes from one file are grouped. |

## Two outputs {#outputs}

| | Extension and add-on | Web Uploader |
|---|---|---|
| Output | Slides' own shape data, handed to the open slide. See [[how-shapes-reach-the-slide]]. | A presentation file with one slide per SVG, each path a custom-geometry shape. |
| Gradients | Extension 1.4.0: written as Slides gradients, with the stops re-timed onto the line Slides draws. Add-on and earlier extension versions: the first colour stop becomes a solid fill. | Kept as gradients. |
| Text and some strokes | Not converted. | Outlined on the server before conversion. |

## The JavaScript converter in version 1.3.0 {#javascript}

Up to version 1.2.0 the extension carried a Python runtime compiled to WebAssembly and ran the same Python converter the server runs. That runtime was most of the installed size.

Version 1.3.0 replaces it with a JavaScript converter that follows the Python one line for line, including its rounding rules and its error cases. The two were compared before release:

| Check | Result |
|---|---|
| All 138 SVG files in the project's repository, and multi-file drops | Output identical, byte for byte. |
| 3,000 randomly generated SVG files | Identical except for 3 files with a perfect half-ellipse arc, where the last bit of a floating-point result decides whether the same shape is written as two curve pieces or three. |

The installed size fell from 14 MB to 1.1 MB. With no runtime to fall back from, the server fallback and its host permission were removed. See [[release-notes/1-3-0#packaging]].

## Why some features do not convert {#why}

A Slides shape has one outline and one fill. SVG features that depend on something else, such as a clip path, a mask, a filter, a pattern or per-element transparency, have no place to go and are dropped or ignored. Colours written as `hsl()` are not parsed and arrive black. The tested results are in [[svg-compatibility]].
""",
        see=["svg-compatibility", "how-shapes-reach-the-slide", "point-precision", "edit-points-and-polylines"],
    ),
    dict(
        slug="how-shapes-reach-the-slide", book="technical", kind="Technical note", nav="How shapes reach the slide",
        title="How shapes reach the slide",
        desc="How SVG to Slides inserts native shapes into Google Slides without the Slides API, Drive access or any Google permission.",
        applies=[AALL, AADD],
        summary="The extension never calls a Google API. It hands shapes to Slides in the form Slides itself uses when you copy and paste a shape, so Slides treats them as its own. That is why the extension needs no Google permission.",
        keys=["clipboard format", "paste, scripted", "Slides API, not used", "Google permissions, none needed", "insertion method"],
        howto=False,
        body="""
## The route {#route}

When you copy a shape in Google Slides, Slides writes it to the clipboard in a form of its own. Paste that data back and Slides rebuilds the shape. SVG to Slides writes the same form from an SVG's paths and gives it to Slides. Slides accepts it as if it had copied the shapes itself.

No request goes to the Slides API or to Drive, and no OAuth scope is involved.

## How the hand-over is made {#hand-over}

| Product and version | Hand-over |
|---|---|
| Extension 1.0.0 and 1.0.1 | The extension placed the data on your clipboard at your click. You pressed <<Command+V>>. |
| Extension 1.2.0 and later | The extension delivers the data to the Slides tab the way a paste does. If Slides does not accept it, the extension falls back to your clipboard and asks for <<Command+V>>. |
| Add-on | You click **Copy**, then press <<Command+V>>. A dialog in a web page cannot paste for you. |

## Reading the selection {#reading}

Edit Shape and the shape commands need to know what is selected. They read it the way a copy does: Slides hands over the same shape data, inside your browser. Nothing is sent anywhere.

## Replacing a shape {#replacing}

An edit, a combine or an outline ends by removing the original objects and handing Slides the result in the same place, then restoring its place in the stack. Slides records that as several steps. See [[undo-and-still-copy]] for how those steps are hidden and undone as one.

## What follows from this route {#consequences}

- Shapes land on the slide you have open. The route cannot create slides.
- The result is a native object. A masked image, for example, is the same kind of object Slides makes when you crop an image to a shape: a shape filled with the picture.
- The form Slides uses is internal to Google and can change. The extension is built so that if a scripted hand-over stops working, it falls back to copy and <<Command+V>>.
""",
        see=["how-conversion-works", "permissions-privacy", "undo-and-still-copy", "kb/press-command-v-prompt"],
    ),
    dict(
        slug="edit-points-and-polylines", book="technical", kind="Technical note", nav="Edit points and polylines",
        title="Slides' Edit points and polylines",
        desc="Why Google Slides' own Edit points works on some inserted SVG shapes and not others: straight-line shapes land as polylines, and curved shapes need SVG to Slides' Edit Shape.",
        applies=[A12, AADD],
        summary="Google Slides has an Edit points command of its own, which works on polylines. Inserted shapes with one outline and only straight segments land as polylines, so that command works on them. Curved shapes land as custom shapes. Use Edit Shape for those.",
        keys=["Edit points, Slides' own", "polyline", "custom shape", "curves, why not polylines#why"],
        howto=False,
        body="""
## The rule {#rule}

A converted shape lands as a polyline when all three are true:

- It has a single outline, with no holes and no separate pieces.
- Every segment is a straight line.
- It has no more than 150 points.

Rectangles, polygons and other straight-edged closed paths meet the rule. Circles, curved icons and shapes with holes land as custom shapes.

## Why curved shapes are not polylines {#why}

Slides' point editor has no model for Bézier curves. These results come from inserting test shapes and dragging a point in each.

| Test | Result |
|---|---|
| A polyline that contains curves | It draws correctly when inserted. On the first point drag, Slides rewrites the whole outline as straight lines, and every curve control point becomes a corner. |
| A polyline with several outlines | Slides merges them into one outline, joining the outer and inner parts with stray diagonal edges. |
| A shape of Slides' curve-tool kind, given curve data | Slides ignores the curve data and draws its own smooth line through every coordinate. A circle made of four curves comes out as a lumpy rounded square. |

So only shapes that Slides' editor can represent exactly are marked for it.

## A difference you can see {#difference}

| Shape | Double-click in Slides |
|---|---|
| Custom shape | Gives a text cursor. The shape can hold text. |
| Polyline | Enters Slides' point editing. |

## Which editor to use {#which}

| To edit | Use |
|---|---|
| A straight-edged shape, corner by corner | Slides' own **Edit points**, or [[edit-shape]]. |
| Any shape with curves or holes | [[edit-shape]]. |
| A shape from Slides' shape menu | [[edit-shape]], which converts it first. See [[convert-slides-shapes]]. |
""",
        see=["edit-shape", "convert-slides-shapes", "how-conversion-works", "kb/edit-points-missing"],
    ),
    dict(
        slug="point-precision", book="technical", kind="Technical note", nav="Point precision",
        title="Point precision: small SVGs keep their detail",
        desc="Why an SVG inserted small into Google Slides can be enlarged without losing its curves: SVG to Slides 1.3.0 stores points at full precision.",
        applies=[A13],
        summary="From version 1.3.0 every inserted shape carries its points at full precision, whatever size it lands at. An icon dropped at 12 pixels can be enlarged later and keeps every curve.",
        keys=["precision", "small SVGs", "enlarging an icon", "detail, keeping"],
        howto=False,
        body="""
## The problem before 1.3.0 {#before}

Slides stores an inserted shape's points as they arrive and resizes the shape by changing its transform. It does not recalculate the points. Earlier versions wrote the points at the size of the drop, so those points were all the detail the shape ever had. An icon that landed 12 pixels wide carried 12 pixels' worth of positions, and enlarging it showed the rounding.

## What 1.3.0 does {#now}

Each shape's points are written in a frame of its own, about 100,000 units across, and the shape's transform scales that frame down to the size on the slide. The points are the same whatever the size.

Slides keeps a transform's scale to four decimal places. A scale of 0.047625 comes back as 0.0476. The converter therefore rounds the scale to four places first and sizes the frame to fit that scale exactly, so nothing shifts when Slides stores the shape.

@fig small-svg-detail | A slide zoomed to 400 percent showing a large palm icon with smooth, clean curves | A small icon after enlarging, viewed at 400% zoom. *Illustration.*

## Checks {#checks}

| Check | Result |
|---|---|
| The 138 SVG files in the project's repository | Every shape lands within 0.01 pixel of where it landed before the change. |
| A 12 pixel, two-shape icon enlarged about 700 times with Slides' own resize | The shape kept its full-precision points. |

!!! Note: The add-on still writes points at the size of the insert.
""",
        see=["insert-svg#size", "how-conversion-works", "release-notes/1-3-0#converter"],
    ),
    dict(
        slug="undo-and-still-copy", book="technical", kind="Technical note", nav="Multi-step changes and undo",
        title="How multi-step changes run and undo",
        desc="How SVG to Slides hides the steps of a combine, outline or mask in Google Slides behind a still copy of the slide and undoes the change in one press.",
        applies=[A13],
        summary="A combine, an outline, a mask or an Edit Shape session reaches Slides as several steps: remove, insert, restack. The extension shows a still copy of the slide while they run, so you see only the result, and it counts the steps so that one <<Command+Z>> undoes them all.",
        keys=["still copy", "freeze", "multi-step changes", "undo, how it works", "helper square#edge", "images, moving#native"],
        howto=False,
        body="""
## The still copy {#still-copy}

While a change runs, the extension lays a still picture of the slide over the canvas, under its own toolbar. Slides' toolbar is held still too. The copy includes the selection box, so the selection does not blink. When the last step has finished, the copy is removed and the finished slide shows.

Objects hidden in the Layers panel stay hidden in the copy.

For Align and Distribute the copy is drawn with the objects already at their destination. The slide changes once, straight to the result.

## Slides' own commands for moving {#native}

Align, Distribute and Center on page are run from Slides' own Arrange menu, which the extension keeps invisible while it uses it. Each is one Slides step. Nothing is deleted or reinserted.

This matters for images. An image that is deleted and reinserted from copied data can lose its picture, so anything that moves an image goes through Slides' own commands.

## One object to a slide edge {#edge}

Slides' Align needs something to align to. To align a single object to an edge of the slide, the extension inserts a 1 pixel square with no fill and no line at the corner it needs, selects it with the object, runs Slides' Align, takes the object out of the selection and deletes the square. The steps run behind the still copy and undo as one. No extra object is left in the presentation.

## One-press undo {#undo}

The extension notes the slide before and after each of its changes and counts the Slides steps the change made. If you press <<Command+Z>> right after, it walks Slides' own undo back that many steps, behind the still copy. Redo walks forward the same way.

Two rules keep this safe:

- It never presses undo more times than the change made steps.
- It applies only while the slide is as the extension left it. If you have changed the slide since, Slides' own undo is used, one step per press.
""",
        see=["undo-redo", "align-distribute", "how-shapes-reach-the-slide", "kb/undo-takes-several-presses"],
    ),
]
