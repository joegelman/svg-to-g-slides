"""The product facts every page states, in one place.

Change this file at each release, then rebuild. Pages that state the current
version, the package size, the permissions or the one-paragraph summary read
them from here: /specs, /docs (site_docs.CURRENT and STORE), the what's-new
band, llms.txt and the homepage "New in" card check.

`check()` runs at the end of build_site.py. It stops the build when a page
that is hand-maintained or tested on a fixed date has fallen behind VERSION:
the homepage card, the /specs compatibility column and the store version.

Statements tied to a past release ("since version 1.4.0", "versions before
1.3.0") are history and stay where they are written.
"""

# Newest Chrome extension version the site documents.
VERSION = "1.4.0"
# The version the Chrome Web Store installs. Set below VERSION to document a
# release before the store has published it (the docs then add availability notes).
STORE = "1.4.0"
RELEASED = "November 2026"  # month the store published VERSION
RELEASED_ISO = "2026-11-24"

DOWNLOAD_SIZE = "434 KB"
INSTALLED_SIZE = "1.3 MB"

# Chrome permissions of VERSION, in the launch-kit wording. Never "no host
# permission" or "basic Google permissions".
PERMISSIONS = ("access to Google Slides pages, where its tools run, and storage, to remember your settings. "
               "No access to other sites.")

# What each minor release added, one clause each, as the release posts word it.
ADDED = {
    "1.2": "edits any shape's points and curves as SVG, directly on the slide",
    "1.3": ("adds drawing tools that work on any shape in the deck: a pen with grid snapping, exact stroke weights, "
            "outline text, image masks, union and subtract, a layers panel and a command palette"),
    "1.4": ("adds a colour panel with opacity, an eyedropper and a gradient builder, text colour for highlighted words, "
            "Replace a colour across one slide or the whole presentation, live preview, and image masks that keep "
            "their shape and let you move the picture under them. SVG gradients and opacity now come across on import"),
}


def minor(v=VERSION):
    return ".".join(v.split(".")[:2])


def summary():
    """The paragraph agents read first (llms.txt). Built from ADDED, so a release adds one line above."""
    parts = [f"Since version {k} the extension {v}." if i == 0 else f"Version {k} {v}."
             for i, (k, v) in enumerate(ADDED.items())]
    return ("Google Slides doesn't keep SVG files as editable vectors. SVG to Slides converts every SVG path into its "
            "own native Slides shape, so users can recolor individual elements, edit points, animate shapes, and resize "
            "without losing quality. The shapes also work in Google Drawings. " + " ".join(parts) +
            f" The current version is {VERSION}. The extension converts every file inside the browser, and nothing is uploaded.")


def check(static_dir, ext_tested_version):
    """Stop the build when a page has fallen behind VERSION. Returns nothing; raises SystemExit."""
    import re
    problems = []
    if minor() not in ADDED:
        problems.append(f"product.ADDED has no line for {minor()}")
    home = (static_dir / "index.html").read_text()
    m = re.search(r"<!-- editsvg:start -->.*?New in ([0-9.]+)<", home, re.S)
    if not m or m.group(1) != minor():
        problems.append(f"homepage card says 'New in {m.group(1) if m else '?'}', product.VERSION is {VERSION} "
                        "(edit cloud/static/index.html between the editsvg markers)")
    if ext_tested_version != VERSION:
        problems.append(f"/specs extension column was tested on {ext_tested_version}, product.VERSION is {VERSION} "
                        "(re-run the samples, then update EXT_VERSION and COMPAT in site_specs.py)")
    if problems:
        raise SystemExit("product facts out of step:\n  - " + "\n  - ".join(problems))
