# Starter pack generators

Scripts that built the Drive starter pack for the collateral blog series. Kept for reference;
paths inside them point at the session workspace they were written in and need adjusting to rerun.

- `messages.py`, `make_templates.py`, `make_sheet.py`: part 1 sample templates and messaging sheet (python-pptx, openpyxl).
- `pack2.py`, `brands.py`: messaging architecture and brand style sheet workbooks, for the Relay sample and for SVG to Slides.
- `make_brand.py`, `vec.py`: SVG to Slides one-pager and deck. `vec.py` places SVGs as native shapes with `svg_to_slides.py` and turns `<text>` into text boxes.
- `gemini-ui.svg`: the UI mockup SVG that Gemini wrote in the Slides side panel on Nov 10, 2026.
- `*.gs`: the Apps Script files shipped in the pack.
- Icons: Phosphor Icons 2.1.1 (`@phosphor-icons/core`, MIT), fill weight.
