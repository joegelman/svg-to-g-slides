# Letter spacing survives the PDF. Kerning does too.

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
- Test PDF: https://svgslid.es/static/blog/files/letter-spacing-pdf-test.pdf

## Results
- Tracking: every step +3.00 pt or −1.50 pt vs. the 0 slide, all fonts, all sizes (±0.06 pt rounding).
- Kerning: Roboto's AV kern (−2.69 pt at 64 pt) is still applied with +3; AV moves by exactly the tracking amount.
- Editor vs. PDF: overlay matches within 1 px; an 11 pt line at +3 wraps after the same word in both.

## Three things that change
1. Unit is points. +3 is 0.047 em at 64 pt and 0.375 em at 8 pt. Set it per text style.
2. Any non-zero spacing turns ligatures (ff, fi) off. At negative values the f's can crowd.
3. Open Sans has no kerning in Slides or the PDF, at any setting: the Google Fonts version ships without kerning data (https://fonts.google.com/specimen/Open+Sans).

## Not tested
PowerPoint export, bold and italic weights, Docs.
