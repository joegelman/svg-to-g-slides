"""Post: does Google Slides letter spacing survive a PDF export? Figures: tools/blog_pdf_images.py."""

OPEN_SANS = "https://fonts.google.com/specimen/Open+Sans"
HELP = "https://support.google.com/docs/answer/1663349"
PDF = "/static/blog/files/letter-spacing-pdf-test.pdf"

POST = {
    "slug": "letter-spacing-google-slides-pdf-export",
    "date": "2026-11-14",
    "date_h": "Nov 14, 2026",
    "read": "3 min read",
    "kicker": "Tested",
    "title": "Does Google Slides Letter Spacing Survive PDF Export? We Tested 10 Fonts",
    "h1": "Letter spacing survives the PDF. Kerning does too.",
    "dek": "We set tracking on 10 Google Fonts at six sizes, exported to PDF and measured every letter.",
    "desc": "We tested Google Slides letter spacing in PDF export across 10 Google Fonts and six sizes. Tracking and kerning both carry over exactly. Three things do change.",
    "hero": ("hero-pdf-spacing", "The same Roboto slide with letter spacing +3, shown in the Slides editor and in the exported PDF"),
    "og": "og-pdf-spacing.png",
    "related": ["letter-spacing-google-slides", "on-brand-charts-google-slides", "native-ui-mockups-google-slides"],
    "tldr": [
        "Letter spacing carries into the PDF exactly: +3 is +3.00 pt per letter, &minus;1.5 is &minus;1.50, in every font and size we tried.",
        "Kerning is kept. Tight pairs like <b>AV</b> and <b>To</b> move by the same amount as every other pair.",
        "The editor and the PDF line up within a pixel, line breaks included.",
        "Watch three things: the unit is points (not relative to size), any spacing turns ligatures off, and Open Sans has no kerning at all.",
    ],
    "body": """
<p>The first question after <a href="/blog/letter-spacing-google-slides">our letter spacing post</a> was the right one: does it hold up when you export to PDF, or does kerning go strange on some fonts? We ran the test.</p>

<h2 id="answer">Short answer: it survives</h2>
<p>Left is the Slides editor. Right is the PDF from the same deck. Same spacing, same line breaks, same letters in the same places.</p>
{fig:pdf-editor-side-by-side|The Roboto +3 test slide in the Slides editor and in the exported PDF, side by side|Roboto, letter spacing +3. Editor left, PDF right.}

<h2 id="test">How we tested</h2>
<ul>
<li><b>10 fonts</b> that Slides offers from Google Fonts. Sans: Roboto, Inter, Open Sans, Montserrat, Lato. Serif: Playfair Display, Merriweather, Lora, EB Garamond, Libre Baskerville.</li>
<li><b>6 sizes</b> on every slide: 64, 36, 24, 14, 11 and 8 pt, from headline to footnote.</li>
<li><b>The hard pairs:</b> AV, WA, LT, LY, Te, To, Tw, Yo, P., F, and friends, plus ff and fi.</li>
<li><b>Three versions</b> of each slide: letter spacing 0, +3 and &minus;1.5.</li>
</ul>
<p>Then we exported the deck to PDF and read the position of every letter out of the file. The 0 slide is the baseline. Anything that moved, we can see.</p>
{fig:pdf-ten-fonts|WAVY AVATAR set in ten Google Fonts at letter spacing +3, as rendered in the PDF|All ten fonts at +3, cropped from the PDF.}
<p>The test PDF is <a href="/static/blog/files/letter-spacing-pdf-test.pdf">here</a> if you want to check our numbers.</p>

<h2 id="tracking">Tracking: exact</h2>
<p>Every letter in the +3 slides sits 3 pt further along than the one before it, compared with the 0 slide. Every letter at &minus;1.5 sits 1.5 pt closer. That held for all ten fonts and all six sizes.</p>
{fig:pdf-tracking-measured|Dot chart of the measured extra space per letter: all +3 dots on the 3 pt line and all -1.5 dots on the -1.5 pt line, across ten fonts and six sizes|Measured in the PDF. The spread is &plusmn;0.06 pt, which is rounding.}

<h2 id="kerning">Kerning: kept</h2>
<p>This was the real worry. Some renderers drop kerning once letters get extra space. Slides doesn&rsquo;t. Roboto pulls A and V 2.69 pt closer at 64 pt. With +3 applied, that pair moves by the same 3 pt as every other pair, so the kern is still there underneath.</p>
{fig:pdf-kerning-kept|AV in Roboto at letter spacing 0 and +3, with the distance from A to V marked|The A-to-V distance grows by the tracking amount and nothing else.}
<p>If kerning had been lost, AV would have jumped by more than 3 pt. It didn&rsquo;t, in any font.</p>

<h2 id="match">Editor and PDF match</h2>
<p>We laid a screenshot of the editor over a render of the PDF. Grey means both put ink in the same place.</p>
{fig:pdf-editor-overlay|Screenshot of the Slides editor in red overlaid on the PDF render in cyan; nearly all text is grey where they coincide|Editor in red, PDF in cyan. Almost all grey.}
<p>Line breaks match too. At +3, the 11 pt line got too long for its box and wrapped. It wrapped after the same word in both.</p>

<h2 id="watch">Three things that do change</h2>
<p><b>1. The unit is points, not a share of the font size.</b> The dialog shows no unit. It&rsquo;s points. So +3 is barely visible on a 64 pt headline and very loose on 8 pt type. Pick the value per text style, not once for the whole deck.</p>
{fig:pdf-points-not-em|+3 letter spacing shown on 64 pt WAVY and on 8 pt text scaled to the same height, with a bar chart of 3 pt as a share of each font size|Same setting, very different results.}
<p><b>2. Any spacing turns ligatures off.</b> At 0, fonts like Libre Baskerville join ff and fi into single glyphs. At +3 or &minus;1.5 they come apart. Opened up, that reads fine. Pulled in, the f&rsquo;s can crowd each other.</p>
{fig:pdf-ligatures|ff fi in Libre Baskerville at 0, +3 and -1.5, enlarged from the PDF|0 keeps the ligatures. +3 and &minus;1.5 drop them.}
<p><b>3. If a font looks badly kerned, it might be Open Sans.</b> Open Sans showed zero kerning everywhere, at every setting, in the editor and the PDF. That&rsquo;s the font, not Slides: <a href="{OPEN_SANS}">Open Sans</a> as served by Google Fonts has no kerning data. AV and To look loose in it no matter what you set.</p>
{fig:pdf-open-sans-kerning|AVATAR at 64 pt in Roboto with a negative AV kern, and in Open Sans with no kern|Roboto kerns AV. Open Sans doesn&rsquo;t.}

<h2 id="use">What to do with it</h2>
<ul>
<li>Use letter spacing in decks you send as PDFs. It holds.</li>
<li>Set it per text style: small positive values for all-caps labels, small negative values for big headlines, 0 for body.</li>
<li>Check line breaks after you add positive spacing. They move in the editor, and the PDF follows.</li>
<li>For headlines with lots of A, V, W and T, choose a font that kerns. Swap Open Sans for Inter or Roboto.</li>
</ul>
<p>Not tested yet: PowerPoint export, bold and italic weights, and Docs, which doesn&rsquo;t have the control yet.</p>
""".replace("{OPEN_SANS}", OPEN_SANS),
    "sources": [
        ("Test deck exported to PDF (30 slides, 10 fonts × 0 / +3 / −1.5)", "https://svgslid.es" + PDF),
        ("Open Sans on Google Fonts", OPEN_SANS),
        ("Change how paragraphs & fonts look (Google Docs Editors Help)", HELP),
    ],
    "md": f"""# Letter spacing survives the PDF. Kerning does too.

*Nov 14, 2026 · svgslid.es blog*

We set tracking on 10 Google Fonts at six sizes, exported Google Slides to PDF and measured every letter.

## TL;DR
- Letter spacing carries into the PDF exactly: +3 is +3.00 pt per letter, −1.5 is −1.50, in every font and size tested.
- Kerning is kept. Pairs like AV and To move by the same amount as every other pair.
- The editor and the PDF line up within a pixel, line breaks included.
- Watch three things: the unit is points (not relative to size), any spacing turns ligatures off, and Open Sans has no kerning at all.

## Test
- Fonts: Roboto, Inter, Open Sans, Montserrat, Lato; Playfair Display, Merriweather, Lora, EB Garamond, Libre Baskerville.
- Sizes: 64, 36, 24, 14, 11, 8 pt. Pairs: AV WA LT LY Te To Tw Yo P. F, plus ff and fi.
- Each slide at letter spacing 0, +3 and −1.5. Exported to PDF; every letter position read from the file and compared with the 0 slide.
- Test PDF: https://svgslid.es{PDF}

## Results
- Tracking: every step +3.00 pt or −1.50 pt vs. the 0 slide, all fonts, all sizes (±0.06 pt rounding).
- Kerning: Roboto's AV kern (−2.69 pt at 64 pt) is still applied with +3; AV moves by exactly the tracking amount.
- Editor vs. PDF: overlay matches within 1 px; an 11 pt line at +3 wraps after the same word in both.

## Three things that change
1. Unit is points. +3 is 0.047 em at 64 pt and 0.375 em at 8 pt. Set it per text style.
2. Any non-zero spacing turns ligatures (ff, fi) off. At negative values the f's can crowd.
3. Open Sans has no kerning in Slides or the PDF, at any setting: the Google Fonts version ships without kerning data ({OPEN_SANS}).

## Not tested
PowerPoint export, bold and italic weights, Docs.
""",
}
