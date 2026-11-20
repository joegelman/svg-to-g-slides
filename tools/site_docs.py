"""/docs: the SVG to Slides documentation library.

A two-pane library in the manner of 1990s product documentation (contents tree,
"applies to" boxes, numbered procedures, See Also, a Knowledge Base with article
IDs, an A-Z index), set in the site's own type: Overpass headings, Verdana body,
white ground, hairline rules.

Content lives in docs_guide.py, docs_reference.py, docs_kb.py and docs_release.py
as topic dicts written in a small markup (see `blocks()` below). Every topic is
rendered twice from the same source: an HTML page at /docs/<slug> and a markdown
twin at /docs/<slug>.md for agents.

Cross-references are checked at build time: `[[slug]]` or `[[slug#anchor]]` to a
topic or anchor that does not exist stops the build.

Imported by build_site.py, which calls build(ctx, lastmod).
"""
import html
import json
import re
from pathlib import Path

import site_content as C
import site_pages as P

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "cloud" / "static"
OUT = STATIC / "docs"
MD = STATIC / "md"
IMG = OUT / "img"

LIB = "SVG to Slides Documentation"
PUBLISHED = "2026-11-20"
CURRENT = "1.3.0"  # the version this library documents
# The version the Chrome Web Store installs today (checked against the store's update
# service on 2026-11-20). While it differs from CURRENT, every topic about CURRENT
# carries an availability note and the release notes say the version is not in the
# store. The day the store publishes CURRENT: set STORE = CURRENT, check CURRENT_DATE,
# run build_site.py. The notes go away.
STORE = "1.2.0"
CURRENT_DATE = "November 2026"  # month the store published CURRENT; shown once STORE == CURRENT
PENDING = STORE != CURRENT
PENDING_TOPICS = {"overview", "install", "quick-start", "permissions-privacy", "how-conversion-works", "kb/which-version"}  # general topics that describe CURRENT
PENDING_NOTE = (f"Version {CURRENT} is not in the Chrome Web Store yet. The store installs version {STORE}. "
                "See [[release-notes#matrix|what each version has]].")


def pending_for(t):
    """True while CURRENT is unpublished and the topic is about CURRENT."""
    return PENDING and (t["slug"] in PENDING_TOPICS or any(
        re.search(rf"\bversion {re.escape(CURRENT)}", a) for a in t.get("applies", [])))

# Books, in reading order. (id, title, one line for the library home)
BOOKS = [
    ("start", "Getting Started", "What SVG to Slides is, how to install it, and how these documents are written."),
    ("guide", "User's Guide", "Every tool in the Chrome extension, one topic each, with procedures."),
    ("surfaces", "Web Uploader and Add-on", "The two ways in that need no extension."),
    ("reference", "Reference", "Keyboard shortcuts, commands, permissions, limits, glossary and index."),
    ("technical", "Technical Notes", "How conversion, insertion, precision and undo work underneath."),
    ("kb", "Knowledge Base", "Numbered articles: one symptom, its cause, and what to do."),
    ("release", "Release Notes", "Version history and a technical changelog for each release."),
]

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def long_date(iso):
    y, m, d = iso.split("-")
    return f"{MONTHS[int(m) - 1]} {int(d)}, {y}"


# ------------------------------------------------------------------ keys
# Keys are written Mac-first in the source, <<Option+Shift+P>>, and shown the way
# period manuals printed them: small capitals joined with plus signs. The Windows
# equivalent follows the rule the extension itself uses (Ctrl for Command, Alt
# for Option).
WIN = {"command": "Ctrl", "option": "Alt", "control": "Alt"}


def win_keys(combo):
    parts = [WIN.get(p.strip().lower(), p.strip()) for p in combo.split("+")] if combo != "+" else ["+"]
    order = {"Ctrl": 0, "Alt": 1, "Shift": 2}
    mods = sorted([p for p in parts if p in order], key=lambda p: order[p])
    rest = [p for p in parts if p not in order]
    seen, out = set(), []
    for p in mods + rest:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return "+".join(out)


def kbd_html(combo):
    has_mod = any(p.strip().lower() in WIN for p in combo.split("+"))
    title = f' title="Windows: {html.escape(win_keys(combo).upper(), quote=True)}"' if has_mod else ""
    return f"<kbd{title}>{html.escape(combo.upper())}</kbd>"


# ---------------------------------------------------------------- inline
INLINE = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<kbd><<[^>]+>>)"
    r"|(?P<xref>\[\[[^\]]+\]\])"
    r"|(?P<link>\[[^\]]+\]\([^)]+\))"
    r"|(?P<bold>\*\*[^*]+\*\*)"
    r"|(?P<ital>(?<![\w*])\*[^*\s][^*]*\*(?!\w))")


class Ctx:
    """What a topic needs while it renders: the topic table (for xrefs) and its own slug."""

    def __init__(self, topics, slug):
        self.topics, self.slug = topics, slug
        self.fig = 0

    def xref(self, raw):
        target, _, label = raw.partition("|")
        slug, _, anchor = target.partition("#")
        slug = slug or self.slug
        if slug not in self.topics:
            raise SystemExit(f"docs: [[{raw}]] in '{self.slug}' points at a topic that does not exist")
        t = self.topics[slug]
        if anchor and anchor not in t["_anchors"]:
            raise SystemExit(f"docs: [[{raw}]] in '{self.slug}': no anchor #{anchor} in '{slug}'")
        return slug, anchor, label or t.get("nav") or t["title"]


def text(s):
    s = html.escape(s, quote=False)
    return re.sub(r"(?<=\w)'(?=\w)|(?<=\w)'(?=[\s.,;:)]|$)", "&rsquo;", s)


def inline(s, cx):
    out, pos = [], 0
    for m in INLINE.finditer(s):
        out.append(text(s[pos:m.start()]))
        pos = m.end()
        tok = m.group(0)
        if m.lastgroup == "code":
            out.append(f"<code>{html.escape(tok[1:-1], quote=False)}</code>")
        elif m.lastgroup == "kbd":
            out.append(kbd_html(tok[2:-2]))
        elif m.lastgroup == "xref":
            slug, anchor, label = cx.xref(tok[2:-2])
            out.append(f'<a class="x" href="{url(slug)}{"#" + anchor if anchor else ""}">{inline(label, cx)}</a>')
        elif m.lastgroup == "link":
            label, href = re.match(r"\[([^\]]+)\]\(([^)]+)\)", tok).groups()
            ext = ' rel="noopener"' if href.startswith("http") and not href.startswith(C.SITE) else ""
            out.append(f'<a href="{html.escape(href, quote=True)}"{ext}>{inline(label, cx)}</a>')
        elif m.lastgroup == "bold":
            out.append(f"<b>{inline(tok[2:-2], cx)}</b>")
        else:
            out.append(f"<i>{inline(tok[1:-1], cx)}</i>")
    out.append(text(s[pos:]))
    return "".join(out)


def inline_md(s, cx):
    def rep(m):
        tok = m.group(0)
        if m.lastgroup == "kbd":
            return tok[2:-2]
        if m.lastgroup == "xref":
            slug, anchor, label = cx.xref(tok[2:-2])
            return f"[{inline_md(label, cx)}]({C.SITE}{url(slug)}.md{'#' + anchor if anchor else ''})"
        if m.lastgroup == "link":
            label, href = re.match(r"\[([^\]]+)\]\(([^)]+)\)", tok).groups()
            return f"[{label}]({C.SITE + href if href.startswith('/') else href})"
        return tok
    return INLINE.sub(rep, s)


def plain(s, cx=None):
    def rep(m):
        tok = m.group(0)
        if m.lastgroup == "code":
            return tok[1:-1]
        if m.lastgroup == "kbd":
            return tok[2:-2]
        if m.lastgroup == "xref":
            raw = tok[2:-2]
            if "|" in raw:
                return raw.split("|", 1)[1]
            return cx.xref(raw)[2] if cx else raw.split("#")[0]
        if m.lastgroup == "link":
            return re.match(r"\[([^\]]+)\]", tok).group(1)
        return tok.strip("*")
    return INLINE.sub(rep, s)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", plain(s).lower()).strip("-")


def url(slug):
    return "/docs" if slug == "index" else f"/docs/{slug}"


# ---------------------------------------------------------------- blocks
# Markup, one block per paragraph (blank line between blocks):
#   ## Heading {#id}        section; the id is optional (made from the words)
#   ### Heading             subsection
#   >> To do something      a procedure title; the numbered list after it is its steps
#   - item / 1. item        lists
#   | a | b |               table; the first row is the header
#   !!! Note: text          also Tip, Important, Caution
#   @fig name | alt | caption | 1=first callout; 2=second callout
#   @@name                  a generated block (see INCLUDES in the content modules)
# Inline: **bold**, *placeholder*, `code`, <<Option+Shift+P>>, [text](url),
#         [[topic]], [[topic#anchor]], [[topic#anchor|words]]
HEAD = re.compile(r"^(#{2,3})\s+(.*?)(?:\s*\{#([a-z0-9-]+)\})?$")
_BAR = "\x00"


def cells(line):
    """Split on | but not inside [[topic|words]]."""
    safe = re.sub(r"\[\[[^\]]*\]\]", lambda m: m.group(0).replace("|", _BAR), line)
    return [c.strip().replace(_BAR, "|") for c in safe.split("|")]


def blocks(src):
    out = []
    for chunk in re.split(r"\n\s*\n", src.strip()):
        lines = [l.rstrip() for l in chunk.strip("\n").split("\n")]
        first = lines[0]
        m = HEAD.match(first)
        if m and len(lines) == 1:
            out.append(("h", len(m.group(1)), m.group(2), m.group(3) or slugify(m.group(2))))
        elif first.startswith(">> "):
            out.append(("proc", first[3:].strip()))
            if len(lines) > 1:
                out += blocks("\n".join(lines[1:]))
        elif first.startswith("@fig "):
            parts = cells(first[5:])
            legend = []
            if len(parts) > 3 and parts[3]:
                legend = [tuple(x.strip().split("=", 1)) for x in parts[3].split(";") if x.strip()]
            out.append(("fig", parts[0], parts[1], parts[2] if len(parts) > 2 else "", legend))
        elif first.startswith("@@"):
            out.append(("inc", first[2:].strip()))
        elif first.startswith("!!! "):
            kind, _, body = " ".join(lines)[4:].partition(":")
            out.append(("note", kind.strip(), body.strip()))
        elif first.startswith("|"):
            rows = [cells(l.strip().strip("|")) for l in lines if not re.match(r"^\|[\s:|-]+\|$", l.strip())]
            out.append(("table", rows[0], rows[1:]))
        elif re.match(r"^(-|\d+\.)\s", first):
            ordered = first[0].isdigit()
            items = []
            for l in lines:
                mm = re.match(r"^(?:-|\d+\.)\s+(.*)$", l)
                if mm:
                    items.append(mm.group(1))
                elif items:
                    items[-1] += " " + l.strip()
            out.append(("ol" if ordered else "ul", items))
        else:
            out.append(("p", " ".join(l.strip() for l in lines)))
    return out


def anchors_of(t, includes):
    ids = set()
    for b in blocks(t.get("body", "")):
        if b[0] == "h":
            ids.add(b[3])
        elif b[0] == "fig":
            ids.add("fig-" + b[1])
        elif b[0] == "inc":
            ids |= set(includes[b[1]].get("anchors", ()))
    ids |= {"applies-to", "see-also", "availability"}
    return ids


def figure_html(name, alt, cap, legend, cx):
    from PIL import Image
    f = IMG / f"{name}.jpg"
    if not f.exists():
        raise SystemExit(f"docs: missing figure {f}")
    w, h = Image.open(f).size
    cx.fig += 1
    lazy = "" if cx.fig == 1 else ' loading="lazy"'
    leg = ""
    if legend:
        leg = f'<ol class="legend{" one" if len(legend) < 4 else ""}">' + "".join(f'<li><span class="n">{n}</span><span>{inline(tx, cx)}</span></li>' for n, tx in legend) + "</ol>"
    return (f'<figure class="fig" id="fig-{name}"><a href="/static/docs/img/{name}.jpg"><picture>'
            f'<source type="image/webp" srcset="/static/docs/img/{name}.webp">'
            f'<img src="/static/docs/img/{name}.jpg" width="{w}" height="{h}" alt="{html.escape(plain(alt), quote=True)}"{lazy} decoding="async">'
            f'</picture></a><figcaption><b>Figure {cx.fig}.</b> {inline(cap, cx)}</figcaption>{leg}</figure>')


def render_html(src, cx, includes):
    out, toc, steps = [], [], []
    seq = blocks(src)
    for i, b in enumerate(seq):
        k = b[0]
        if k == "h":
            lvl, title, hid = b[1], b[2], b[3]
            if lvl == 2:
                toc.append((hid, title))
            out.append(f'<h{lvl} id="{hid}">{inline(title, cx)}<a class="hx" href="#{hid}" aria-label="Link to this section">#</a></h{lvl}>')
        elif k == "proc":
            out.append(f'<p class="proc">{inline(b[1], cx)}</p>')
            nxt = seq[i + 1] if i + 1 < len(seq) else None
            if nxt and nxt[0] == "ol":
                steps.append((b[1], nxt[1]))
        elif k == "p":
            out.append(f"<p>{inline(b[1], cx)}</p>")
        elif k in ("ul", "ol"):
            prev = seq[i - 1][0] if i else ""
            cls = ' class="psteps"' if k == "ol" and prev == "proc" else ""
            out.append(f"<{k}{cls}>" + "".join(f"<li>{inline(x, cx)}</li>" for x in b[1]) + f"</{k}>")
        elif k == "note":
            out.append(f'<div class="note n-{b[1].lower()}"><b>{b[1]}</b> {inline(b[2], cx)}</div>')
        elif k == "table":
            head = "".join(f"<th>{inline(c, cx)}</th>" for c in b[1])
            mark = lambda c: f'<td class="mk"><span class="mk-{c.lower()}">{c}</span></td>' if c in ("NEW", "CHG", "FIX", "REM") else f"<td>{inline(c, cx)}</td>"
            rows = "".join("<tr>" + "".join(mark(c) for c in r) + "</tr>" for r in b[2])
            out.append(f'<div class="tw"><table class="t"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
        elif k == "fig":
            out.append(figure_html(b[1], b[2], b[3], b[4], cx))
        elif k == "inc":
            out.append(includes[b[1]]["html"](cx))
    return "\n".join(out), toc, steps


def render_md(src, cx, includes):
    out, n = [], 0
    for b in blocks(src):
        k = b[0]
        if k == "h":
            out += ["#" * b[1] + " " + plain(b[2], cx), ""]
        elif k == "proc":
            out += [f"**{plain(b[1], cx)}**", ""]
        elif k == "p":
            out += [inline_md(b[1], cx), ""]
        elif k == "ul":
            out += [f"- {inline_md(x, cx)}" for x in b[1]] + [""]
        elif k == "ol":
            out += [f"{i + 1}. {inline_md(x, cx)}" for i, x in enumerate(b[1])] + [""]
        elif k == "note":
            out += [f"> **{b[1]}:** {inline_md(b[2], cx)}", ""]
        elif k == "table":
            out += ["| " + " | ".join(inline_md(c, cx) for c in b[1]) + " |", "|" + "---|" * len(b[1])]
            out += ["| " + " | ".join(inline_md(c, cx) for c in r) + " |" for r in b[2]] + [""]
        elif k == "fig":
            n += 1
            out += [f"![{plain(b[2], cx)}]({C.SITE}/static/docs/img/{b[1]}.jpg)", f"Figure {n}. {inline_md(b[3], cx)}"]
            out += [f"{a}. {inline_md(tx, cx)}" for a, tx in b[4]] + [""]
        elif k == "inc":
            out += [includes[b[1]]["md"](cx), ""]
    return "\n".join(out).rstrip() + "\n"


# ------------------------------------------------------------------- css
ICON_BOOK = ('<svg class="bi bc" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 2h8.5A1.5 1.5 0 0 1 13 3.5V14H4.5A1.5 1.5 0 0 1 3 12.5Z" fill="#FFC700" stroke="#1c1e22" stroke-width="1"/><path d="M5.5 2v12" stroke="#1c1e22" stroke-width="1"/></svg>'
             '<svg class="bi bo" viewBox="0 0 16 16" aria-hidden="true"><path d="M1.5 4 8 5.5 14.5 4v8.5L8 14l-6.5-1.5Z" fill="#fff" stroke="#1c1e22" stroke-width="1" stroke-linejoin="round"/><path d="M8 5.5V14" stroke="#1c1e22" stroke-width="1"/><path d="M3.5 6.6 6.5 7.3M3.5 8.6 6.5 9.3M9.5 7.3l3-.7M9.5 9.3l3-.7" stroke="#FFC700" stroke-width="1.2"/></svg>')
ICON_PAGE = '<svg class="pi" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 1.5h6l3 3v10h-9Z" fill="#fff" stroke="#6b6f76" stroke-width="1" stroke-linejoin="round"/><path d="M9.5 1.5v3h3" fill="none" stroke="#6b6f76" stroke-width="1"/><path d="M5.5 8h5M5.5 10h5M5.5 12h3.5" stroke="#b9bdc4" stroke-width="1"/></svg>'

DOCS_CSS = """
.dx{max-width:1220px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.dxbar{display:flex;align-items:center;gap:14px;flex-wrap:wrap;border:1px solid var(--rule);border-left:5px solid var(--yellow);padding:9px 12px 9px 14px;font:600 13px/1.2 var(--display);letter-spacing:.07em;text-transform:uppercase;background:#fff}
.dxbar .t{text-decoration:none;color:var(--fg);font-weight:700}
.dxbar .v{color:var(--mute);font-weight:600}
.dxbar nav{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap}
.dxbar nav a{padding:6px 10px 5px;border:1px solid var(--rule);text-decoration:none;color:var(--fg);background:#fff}
.dxbar nav a:hover,.dxbar nav a.on{background:var(--tint);border-color:var(--yellow)}
.dxgrid{display:grid;grid-template-columns:272px minmax(0,1fr);border:1px solid var(--rule);border-top:0;margin-bottom:56px;background:#fff}
.dxtoc{border-right:1px solid var(--rule);padding:14px 10px 22px 10px;font-size:13px;line-height:1.4;position:sticky;top:0;align-self:start;max-height:100vh;overflow:auto}
.dxtoc>details>summary{list-style:none;font:700 12px var(--display);letter-spacing:.12em;text-transform:uppercase;color:var(--mute);margin:2px 0 10px 4px;cursor:default}
.dxtoc summary::-webkit-details-marker{display:none}
.dxtoc .bk{margin:0 0 1px}
.dxtoc .bk>summary{list-style:none;cursor:pointer;display:flex;gap:7px;align-items:center;padding:4px;font:600 14px/1.25 var(--display);color:var(--fg)}
.dxtoc .bk>summary:hover{background:var(--tint)}
.dxtoc .bi{width:16px;height:16px;flex:none}.dxtoc .bo{display:none}.dxtoc .bk[open]>summary .bo{display:block}.dxtoc .bk[open]>summary .bc{display:none}
.dxtoc ul{list-style:none;margin:0 0 7px 11px;padding:1px 0 1px 9px;border-left:1px dotted #b9bdc4}
.dxtoc li a{display:flex;gap:6px;align-items:flex-start;padding:3px 4px;color:var(--fg);text-decoration:none}
.dxtoc li a:hover{text-decoration:underline}
.dxtoc li a.cur{background:var(--tint);box-shadow:inset 3px 0 0 var(--yellow);font-weight:bold}
.dxtoc .pi{width:14px;height:14px;flex:none;margin-top:1px}
.dxart{padding:20px 36px 30px;min-width:0;font-size:15px;line-height:1.65}
.dxart .crumb{padding-top:0;margin-bottom:14px}
.dxart .kick{font-weight:700;font-size:12px;letter-spacing:.12em;color:var(--mute)}
.dxart h1{font-size:clamp(28px,3.6vw,36px);line-height:1.12;margin:6px 0 16px;letter-spacing:-.01em}
.dxart h2{font-size:23px;line-height:1.2;margin:34px 0 10px;padding-top:14px;border-top:1px solid var(--rule);scroll-margin-top:12px}
.dxart h3{font-size:18px;margin:24px 0 8px;scroll-margin-top:12px}
.dxart p{margin:0 0 12px}
.dxart a{color:var(--blue-ink);text-underline-offset:3px;text-decoration-thickness:1px}
.dxart .hx{margin-left:8px;font:600 15px var(--display);color:#b9bdc4;text-decoration:none;visibility:hidden}
.dxart h2:hover .hx,.dxart h3:hover .hx,.dxart .hx:focus{visibility:visible}
.dxart ul,.dxart ol{margin:0 0 14px;padding-left:1.5em}.dxart li{margin:0 0 5px}
.dxart code{font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#f3f4f6;padding:1px 4px}
.dxart kbd{font:700 11px/1 var(--body);letter-spacing:.04em;border:1px solid #c9ccd1;border-bottom-width:2px;border-radius:3px;padding:2px 5px 1px;background:#fff;white-space:nowrap;color:var(--fg)}
.applies{border:1px solid var(--rule);padding:10px 14px 9px;margin:0 0 16px;font-size:13px;line-height:1.5;scroll-margin-top:12px}
.applies b{display:block;font:700 11.5px var(--display);letter-spacing:.1em;text-transform:uppercase;color:var(--mute);margin-bottom:3px}
.applies ul{margin:0;padding-left:1.3em}.applies li{margin:0}
.lead{font-size:16px;line-height:1.6;border-left:4px solid var(--yellow);background:var(--tint);padding:13px 16px;margin:0 0 16px}
.inthis{font-size:13.5px;margin:0 0 6px}.inthis b{font:700 11.5px var(--display);letter-spacing:.1em;text-transform:uppercase;color:var(--mute);display:block;margin-bottom:4px}
.inthis ul{list-style:none;padding:0;margin:0;columns:2;column-gap:28px}.inthis li{margin:0 0 3px;break-inside:avoid}
.proc{font:600 17px/1.3 var(--display);margin:20px 0 8px!important}
.proc::before{content:"";display:inline-block;width:0;height:0;border:5px solid transparent;border-left:8px solid var(--yellow);margin-right:5px}
ol.psteps{list-style:none;counter-reset:s;padding-left:0}
ol.psteps li{counter-increment:s;position:relative;padding:0 0 0 34px;margin:0 0 8px}
ol.psteps li::before{content:counter(s) ".";position:absolute;left:8px;top:0;font-weight:bold}
.note{border-left:4px solid var(--yellow);background:var(--tint);padding:10px 14px;margin:14px 0 16px;font-size:14px}
.note b:first-child{font:700 13px var(--display);letter-spacing:.08em;text-transform:uppercase;margin-right:8px}
.note.n-caution,.note.n-important{border-left-color:var(--fg)}
.tw{overflow-x:auto;margin:0 0 16px}
table.t{border-collapse:collapse;width:100%;font-size:14px}
table.t th,table.t td{text-align:left;vertical-align:top;padding:7px 10px;border:1px solid var(--rule)}
table.t th{font:700 12px var(--display);letter-spacing:.07em;text-transform:uppercase;color:var(--mute);background:#fafbfc;white-space:nowrap}
table.t td.mk{white-space:nowrap;width:1%}
table.t td.mk span{font:700 11px/1 var(--display);letter-spacing:.08em;border:1px solid var(--fg);padding:3px 5px 2px;display:inline-block}
table.t td.mk .mk-new{background:var(--yellow);border-color:var(--yellow)}
table.t td.mk .mk-fix{background:var(--fg);color:#fff}
table.t td.mk .mk-rem{border-style:dashed}
figure.fig{margin:18px 0 20px;scroll-margin-top:12px}
figure.fig img{display:block;width:100%;height:auto;border:1px solid var(--rule)}
figure.fig figcaption{font-size:13px;color:var(--mute);margin-top:7px;line-height:1.5}
figure.fig figcaption b{color:var(--fg)}
ol.legend{list-style:none;padding:0;margin:9px 0 0;font-size:13.5px;line-height:1.45;columns:2;column-gap:26px}
ol.legend.one{columns:1}
ol.legend li{display:flex;gap:8px;margin:0 0 6px;break-inside:avoid}
ol.legend .n{flex:none;width:20px;height:20px;border-radius:50%;background:var(--yellow);color:#1c1e22;font:700 12px/21px var(--display);text-align:center}
.see{margin-top:30px;border:1px solid var(--rule);padding:12px 16px 8px;scroll-margin-top:12px}
.see h2{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--mute);margin:0 0 6px;padding:0;border:0;font-weight:700}
.see ul{list-style:none;padding:0;margin:0;columns:2;column-gap:28px}.see li{margin:0 0 5px;break-inside:avoid}
.see li::before{content:"\\25B8";color:var(--mute);margin-right:6px}
.dxnav{display:flex;justify-content:space-between;gap:12px;margin-top:26px;font:600 14px var(--display)}
.dxnav a{border:1px solid var(--rule);padding:8px 12px;text-decoration:none;color:var(--fg)!important;max-width:48%}
.dxnav a:hover{border-color:var(--yellow);background:var(--tint)}
.dxnav small{display:block;font:700 10.5px var(--display);letter-spacing:.12em;text-transform:uppercase;color:var(--mute)}
.dxmeta{margin-top:14px;font-size:12px;color:var(--mute);display:flex;gap:6px 18px;flex-wrap:wrap}
.dxmeta a{color:var(--mute)}
.kbhead{border:1px solid var(--rule);border-left:5px solid var(--fg);padding:9px 14px;margin:0 0 16px;font-size:13px;display:flex;gap:4px 22px;flex-wrap:wrap}
.kbhead b{font-family:var(--display)}
.books{display:grid;grid-template-columns:1fr 1fr;gap:0;border-top:1px solid var(--rule);border-left:1px solid var(--rule);margin:18px 0 8px}
.books section{border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:14px 16px 12px;scroll-margin-top:12px}
.books h2{font-size:18px;margin:0 0 4px;padding:0;border:0;display:flex;gap:8px;align-items:center}
.books h2 svg{width:18px;height:18px;flex:none}
.books p{font-size:13px;color:var(--mute);margin:0 0 8px}
.books ul{list-style:none;padding:0;margin:0;font-size:14px}.books li{margin:0 0 4px}
.az{display:flex;flex-wrap:wrap;gap:4px;margin:0 0 14px;font:700 13px var(--display)}
.az a,.az span{width:27px;height:27px;display:grid;place-items:center;border:1px solid var(--rule);text-decoration:none}
.az span{color:#c2c5ca}.az a:hover{background:var(--tint);border-color:var(--yellow)}
.ixf{display:block;width:100%;max-width:340px;height:36px;border:1px solid #c9ccd1;padding:0 10px;font:14px var(--body);margin:0 0 14px;box-sizing:border-box}
.ix h2{font-size:20px;margin:22px 0 6px}
.ix dl{margin:0;columns:2;column-gap:30px;font-size:14px}
.ix dt{margin:0 0 1px;break-after:avoid}.ix dd{margin:0 0 7px 14px;font-size:13px;break-inside:avoid}
.gl dt{font:600 16px var(--display);margin:16px 0 3px;scroll-margin-top:12px}.gl dd{margin:0 0 4px}
@media (max-width:920px){
  .dxgrid{grid-template-columns:1fr}
  .dxtoc{position:static;max-height:none;border-right:0;border-bottom:1px solid var(--rule);padding:8px 10px}
  .dxtoc>details>summary{cursor:pointer;margin:4px;color:var(--fg);font-size:13px}
  .dxtoc>details>summary::after{content:" \\25BE"}
  .dxart{padding:18px 16px 26px}
  .inthis ul,.see ul,ol.legend,.ix dl{columns:1}
  .books{grid-template-columns:1fr}
  .dxbar nav{margin-left:0}
  table.t{font-size:13px}table.t th,table.t td{padding:6px 7px}table.t th{white-space:normal}
  .dxart kbd{font-size:10px;padding:2px 3px 1px;letter-spacing:.02em}
}
@media print{.nav,.dxtoc,.dxbar,.sfoot,.dxnav,.hx{display:none!important}.dxgrid{display:block;border:0}.dxart{padding:0}}
"""

TOC_JS = ("<script>(function(){var d=document.querySelector('.dxtoc>details');"
          "if(d&&matchMedia('(max-width:920px)').matches)d.removeAttribute('open');"
          "var c=document.querySelector('.dxtoc a.cur');if(c&&c.scrollIntoView&&!matchMedia('(max-width:920px)').matches)c.scrollIntoView({block:'nearest'});})();</script>")


# ------------------------------------------------------------- page parts
def bar(active=""):
    tabs = [("Contents", "/docs", "index"), ("Index", "/docs/a-z-index", "a-z-index"),
            ("Shortcuts", "/docs/keyboard-shortcuts", "keyboard-shortcuts"),
            ("Knowledge Base", "/docs/kb", "kb"), ("Release Notes", "/docs/release-notes", "release-notes")]
    links = "".join(f'<a href="{h}"{" class=\"on\"" if k == active else ""}>{t}</a>' for t, h, k in tabs)
    return (f'<div class="dxbar"><a class="t" href="/docs">{LIB}</a><span class="v">Version {CURRENT}</span>'
            f'<nav aria-label="Documentation">{links}</nav></div>')


def tree(topics, order, cur):
    by_book = {}
    for s in order:
        by_book.setdefault(topics[s]["book"], []).append(s)
    cur_book = topics[cur]["book"] if cur in topics else ""
    out = []
    for bid, title, _ in BOOKS:
        items = "".join(
            f'<li><a href="{url(s)}"{" class=\"cur\" aria-current=\"page\"" if s == cur else ""}>{ICON_PAGE}<span>{html.escape(topics[s].get("nav") or topics[s]["title"])}</span></a></li>'
            for s in by_book.get(bid, []))
        out.append(f'<details class="bk"{" open" if bid == cur_book else ""}><summary>{ICON_BOOK}<span>{title}</span></summary><ul>{items}</ul></details>')
    return ('<aside class="dxtoc" aria-label="Contents"><details open><summary>Contents</summary>'
            + "".join(out) + "</details></aside>")


def crumbs_html(t):
    book = dict((b[0], b[1]) for b in BOOKS)[t["book"]]
    return (f'<p class="crumb"><a href="/">SVG to Slides</a> &rsaquo; <a href="/docs">Docs</a> &rsaquo; '
            f'<a href="/docs#{t["book"]}">{book}</a> &rsaquo; {html.escape(t.get("nav") or t["title"])}</p>')


def applies_html(t, cx):
    if not t.get("applies"):
        return ""
    lis = "".join(f"<li>{inline(a, cx)}</li>" for a in t["applies"])
    note = f'<div class="note n-important" id="availability"><b>Important</b> {inline(PENDING_NOTE, cx)}</div>' if pending_for(t) else ""
    return f'<div class="applies" id="applies-to"><b>The information in this topic applies to:</b><ul>{lis}</ul></div>{note}'


def see_html(t, cx):
    if not t.get("see"):
        return ""
    lis = []
    for s in t["see"]:
        if isinstance(s, tuple):
            lis.append(f'<li><a href="{s[1]}">{html.escape(s[0])}</a></li>')
        else:
            slug, anchor, label = cx.xref(s)
            lis.append(f'<li><a href="{url(slug)}{"#" + anchor if anchor else ""}">{html.escape(label)}</a></li>')
    return f'<section class="see" id="see-also"><h2>See also</h2><ul>{"".join(lis)}</ul></section>'


def topic_ld(t, cx, ctx, steps, modified, og):
    path = url(t["slug"])
    book = dict((b[0], b[1]) for b in BOOKS)[t["book"]]
    art = {"@context": "https://schema.org", "@type": "TechArticle", "headline": t["title"], "description": plain(t["desc"], cx),
           "url": C.SITE + path, "mainEntityOfPage": C.SITE + path, "datePublished": PUBLISHED, "dateModified": modified,
           "inLanguage": "en", "articleSection": book, "image": og,
           "author": {"@type": "Person", "name": "Joe Gelman"},
           "publisher": {"@type": "Organization", "@id": C.SITE + "/#org", "name": "SVG to Slides", "url": C.SITE + "/"},
           "about": {"@type": "SoftwareApplication", "@id": C.SITE + "/#app", "name": "SVG to Slides"},
           "isPartOf": {"@type": "CollectionPage", "@id": C.SITE + "/docs#library", "name": LIB, "url": C.SITE + "/docs"}}
    if t.get("version"):
        art["softwareVersion"] = t["version"]
    lds = [art, ctx["crumbs"]([("Docs", "/docs"), (book, "/docs#" + t["book"]), (t.get("nav") or t["title"], path)])]
    if steps and t.get("howto", True):
        name, items = steps[0]
        lds.append({"@context": "https://schema.org", "@type": "HowTo", "name": plain(name, cx),
                    "tool": [{"@type": "HowToTool", "name": "SVG to Slides"}],
                    "step": [{"@type": "HowToStep", "position": i + 1, "text": plain(x, cx)} for i, x in enumerate(items)]})
    faq = list(t.get("faq", []))
    if t.get("kb"):
        faq.insert(0, (t["kb"]["q"], t["kb"]["a"]))
    if faq:
        lds.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": plain(q, cx), "acceptedAnswer": {"@type": "Answer", "text": plain(a, cx)}} for q, a in faq]})
    return lds


def page(ctx, *, title, desc, path, art, toc_html, active, ld, md, og):
    body = f"""  <div class="dx">
    {bar(active)}
    <div class="dxgrid">
      {toc_html}
      <article class="dxart">
{art}
      </article>
    </div>
  </div>"""
    doc = P.shell(title=title, desc=desc, path=path, body=body, md=md, extra_css=DOCS_CSS, campaign="docs",
                  ld_block=ctx["ld_block"](ld), og_image=og, og_type="article", tail=TOC_JS, **ctx["common"])
    return doc.replace('<meta name="viewport"', '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">\n  <meta name="viewport"', 1)


def first_fig(t):
    for b in blocks(t.get("body", "")):
        if b[0] == "fig":
            return f"{C.SITE}/static/docs/img/{b[1]}.jpg"
    return f"{C.SITE}/static/og-image.png"


def topic_page(ctx, topics, order, t, includes, lastmod):
    cx = Ctx(topics, t["slug"])
    body, toc, steps = render_html(t["body"], cx, includes)
    i = order.index(t["slug"])
    prev_t = topics[order[i - 1]] if i > 0 else None
    next_t = topics[order[i + 1]] if i + 1 < len(order) else None
    book = dict((b[0], b[1]) for b in BOOKS)[t["book"]]
    modified = lastmod("doc:" + t["slug"], json.dumps({k: v for k, v in t.items() if not k.startswith("_")}, sort_keys=True, default=str), seed=PUBLISHED)
    kb = ""
    if t.get("kb"):
        kb = (f'<div class="kbhead"><span><b>Article ID:</b> {t["kb"]["id"]}</span><span><b>Last reviewed:</b> {long_date(modified)}</span>'
              f'<span><b>Revision:</b> {t["kb"].get("rev", "1.0")}</span></div>')
    inthis = ""
    if len(toc) >= 3:
        inthis = '<nav class="inthis" aria-label="In this topic"><b>In this topic</b><ul>' + "".join(
            f'<li><a href="#{h}">{inline(tt, Ctx(topics, t["slug"]))}</a></li>' for h, tt in toc) + "</ul></nav>"
    nav = '<nav class="dxnav" aria-label="Browse">'
    nav += f'<a rel="prev" href="{url(prev_t["slug"])}"><small>&#9668; Previous</small>{html.escape(prev_t.get("nav") or prev_t["title"])}</a>' if prev_t else "<span></span>"
    nav += f'<a rel="next" href="{url(next_t["slug"])}" style="text-align:right"><small>Next &#9658;</small>{html.escape(next_t.get("nav") or next_t["title"])}</a>' if next_t else "<span></span>"
    nav += "</nav>"
    art = f"""{crumbs_html(t)}
<div class="kick">{book if t["kind"].lower() == book.lower() else book + " &middot; " + t["kind"]}</div>
<h1>{inline(t["title"], cx)}</h1>
{kb}{applies_html(t, cx)}
<p class="lead">{inline(t["summary"], cx)}</p>
{inthis}
{body}
{see_html(t, cx)}
{nav}
<p class="dxmeta"><span>Last reviewed {long_date(modified)}</span><span>Documentation for version {CURRENT}</span><span><a href="{url(t["slug"])}.md">Plain text of this topic</a></span><span><a href="/support">Support</a></span></p>"""
    og = first_fig(t)
    title = t.get("head") or f'{plain(t["title"], cx)} | SVG to Slides Docs'
    doc = page(ctx, title=title, desc=plain(t["desc"], cx), path=url(t["slug"]), art=art, toc_html=tree(topics, order, t["slug"]),
               active=t["slug"] if t["slug"] in ("a-z-index", "keyboard-shortcuts", "kb", "release-notes") else "",
               ld=topic_ld(t, cx, ctx, steps, modified, og), md=url(t["slug"]) + ".md", og=og)
    cxm = Ctx(topics, t["slug"])
    md = [f"# {plain(t['title'], cxm)}", ""]
    if t.get("kb"):
        md += [f"Article ID: {t['kb']['id']}. Last reviewed: {long_date(modified)}.", ""]
    if t.get("applies"):
        md += ["Applies to: " + "; ".join(plain(a, cxm) for a in t["applies"]) + ".", ""]
    if pending_for(t):
        md += ["Availability: " + inline_md(PENDING_NOTE, cxm), ""]
    md += [inline_md(t["summary"], cxm), "", render_md(t["body"], cxm, includes)]
    if t.get("see"):
        md += ["## See also", ""]
        for s in t["see"]:
            if isinstance(s, tuple):
                md.append(f"- [{s[0]}]({C.SITE + s[1] if s[1].startswith('/') else s[1]})")
            else:
                slug, anchor, label = cxm.xref(s)
                md.append(f"- [{label}]({C.SITE}{url(slug)}.md{'#' + anchor if anchor else ''})")
        md.append("")
    md += [f"Source: {C.SITE}{url(t['slug'])} ({LIB}, {book}). Last reviewed {long_date(modified)}.", ""]
    return doc, "\n".join(md), modified


def home_page(ctx, topics, order, lastmod):
    cx = Ctx(topics, "index")
    by_book = {}
    for s in order:
        by_book.setdefault(topics[s]["book"], []).append(s)
    secs = []
    for bid, title, blurb in BOOKS:
        lis = "".join(f'<li><a href="{url(s)}">{html.escape(topics[s].get("nav") or topics[s]["title"])}</a></li>' for s in by_book.get(bid, []))
        secs.append(f'<section id="{bid}"><h2>{ICON_BOOK.split("<svg class=\"bi bo\"")[0]}{title}</h2><p>{blurb}</p><ul>{lis}</ul></section>')
    modified = lastmod("doc:index", json.dumps([[s, topics[s]["title"], topics[s]["desc"]] for s in order]), seed=PUBLISHED)
    quick = [("insert-svg", "Insert an SVG file"), ("edit-shape", "Reshape a shape"), ("pen", "Draw with the pen"),
             ("mask-image", "Mask a picture with a shape"), ("combine-shapes", "Combine shapes"), ("layers", "Use the Layers panel"),
             ("keyboard-shortcuts", "Look up a shortcut"), ("kb", "Fix a problem")]
    ql = "".join(f'<li><a href="{url(s)}">{w}</a></li>' for s, w in quick)
    art = f"""<p class="crumb"><a href="/">SVG to Slides</a> &rsaquo; Docs</p>
<div class="kick">Product documentation</div>
<h1 id="library">{LIB}</h1>
<div class="applies"><b>This library documents:</b><ul><li>SVG to Slides Chrome extension, version {CURRENT} (earlier versions where noted)</li><li>SVG to Slides Web Uploader</li><li>SVG to Slides Workspace Add-on for Google Slides&trade;</li></ul></div>{f'<div class="note n-important" id="availability"><b>Important</b> {inline(PENDING_NOTE, cx)}</div>' if PENDING else ""}
<p class="lead">SVG to Slides puts SVG files into Google Slides&trade; as native shapes, then lets you reshape, draw, mask, combine, align and layer them on the slide. This library has a topic for every tool, a reference for every shortcut, numbered Knowledge Base articles for known problems, and a technical changelog for every release.</p>
<nav class="inthis" aria-label="Common tasks"><b>Common tasks</b><ul>{ql}</ul></nav>
<h2 id="contents">Contents<a class="hx" href="#contents" aria-label="Link to this section">#</a></h2>
<div class="books">{"".join(secs)}</div>
<h2 id="using">Using this library<a class="hx" href="#using" aria-label="Link to this section">#</a></h2>
<ul>
<li>Each topic opens with a box that says which product and version it applies to. See {inline("[[conventions]]", cx)}.</li>
<li>Every heading has its own address. Point at a heading and click the # that appears to get a link to that section.</li>
<li>Each page has a plain-text twin for reading by programs: add <code>.md</code> to its address. The whole library is listed in <a href="/llms.txt">/llms.txt</a>.</li>
<li>Product facts and the tested SVG compatibility table are kept in one place: <a href="/specs">Specs</a>. Step-by-step articles for searchers live in <a href="/guides">Guides</a>.</li>
</ul>
<p class="dxmeta"><span>Last reviewed {long_date(modified)}</span><span>Documentation for version {CURRENT}</span><span><a href="/docs.md">Plain text of this page</a></span><span><a href="/support">Support</a></span></p>"""
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "@id": C.SITE + "/docs#library", "name": LIB, "url": C.SITE + "/docs",
           "description": "Product documentation for SVG to Slides: user's guide, reference, Knowledge Base and release notes.",
           "dateModified": modified, "inLanguage": "en",
           "about": {"@type": "SoftwareApplication", "@id": C.SITE + "/#app", "name": "SVG to Slides"},
           "publisher": {"@type": "Organization", "@id": C.SITE + "/#org", "name": "SVG to Slides", "url": C.SITE + "/"},
           "hasPart": [{"@type": "TechArticle", "headline": topics[s]["title"], "url": C.SITE + url(s)} for s in order]},
          ctx["crumbs"]([("Docs", "/docs")])]
    doc = page(ctx, title="SVG to Slides Documentation: User's Guide, Reference and Release Notes",
               desc="Documentation for SVG to Slides: insert SVGs into Google Slides, edit points, pen, masks, combine, layers, shortcuts, Knowledge Base and release notes.",
               path="/docs", art=art, toc_html=tree(topics, order, "index"), active="index", ld=ld, md="/docs.md",
               og=f"{C.SITE}/static/docs/img/toolbar-open.jpg")
    md = [f"# {LIB}", "", f"Documents the SVG to Slides Chrome extension (version {CURRENT}), the Web Uploader and the Workspace Add-on.", ""]
    if PENDING:
        md += ["Availability: " + inline_md(PENDING_NOTE, cx), ""]
    for bid, title, blurb in BOOKS:
        md += [f"## {title}", blurb, ""]
        md += [f"- [{topics[s]['title']}]({C.SITE}{url(s)}.md): {plain(topics[s]['desc'], cx)}" for s in by_book.get(bid, [])] + [""]
    return doc, "\n".join(md), modified


def load():
    import docs_guide, docs_reference, docs_kb, docs_release
    topics, order, includes = {}, [], {}
    for mod in (docs_guide, docs_reference, docs_kb, docs_release):
        includes.update(getattr(mod, "INCLUDES", {}))
    seq = docs_guide.TOPICS + docs_reference.TOPICS + docs_kb.TOPICS + docs_release.TOPICS
    rank = {b[0]: i for i, b in enumerate(BOOKS)}
    seq = sorted(seq, key=lambda t: rank[t["book"]])  # stable: keeps each module's order inside a book
    for t in seq:
        if t["slug"] in topics:
            raise SystemExit(f"docs: duplicate topic {t['slug']}")
        topics[t["slug"]] = t
        order.append(t["slug"])
    for t in topics.values():
        t["_anchors"] = anchors_of(t, includes)
    return topics, order, includes


def build(ctx, lastmod):
    """Write every docs page and its markdown twin. Returns [(path, title, desc, md_text)] in reading order."""
    topics, order, includes = load()
    for mod_inc in includes.values():
        mod_inc.setdefault("anchors", ())
    for inc in includes.values():
        if "prepare" in inc:
            inc["prepare"](topics, order)
    for t in topics.values():
        t["_anchors"] = anchors_of(t, includes)
    OUT.mkdir(exist_ok=True)
    (MD / "docs").mkdir(parents=True, exist_ok=True)
    keep_html, keep_md, listing = set(), set(), []
    doc, md, _ = home_page(ctx, topics, order, lastmod)
    (OUT / "index.html").write_text(doc)
    (MD / "docs.md").write_text(md)
    keep_html.add(OUT / "index.html")
    listing.append(("/docs", LIB, "Library home: every topic by book.", md))
    for s in order:
        t = topics[s]
        doc, md, _ = topic_page(ctx, topics, order, t, includes, lastmod)
        f, g = OUT / f"{s}.html", MD / "docs" / f"{s}.md"
        f.parent.mkdir(parents=True, exist_ok=True)
        g.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(doc)
        g.write_text(md)
        keep_html.add(f)
        keep_md.add(g)
        listing.append((url(s), plain(t["title"], Ctx(topics, s)), plain(t["desc"], Ctx(topics, s)), md))
    for f in OUT.rglob("*.html"):  # topics that were renamed or removed
        if f not in keep_html:
            f.unlink()
    for g in (MD / "docs").rglob("*.md"):
        if g not in keep_md:
            g.unlink()
    return listing, topics, order
