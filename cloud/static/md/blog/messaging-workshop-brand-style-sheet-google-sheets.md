# Run a messaging workshop in Google Forms and build a brand style sheet in Google Sheets

*Nov 9, 2026 · svgslid.es blog · Part 2 of the collateral series (part 1: https://svgslid.es/blog/google-slides-collateral-messaging-sheet-gemini)*

## TL;DR
- A messaging workshop runs as a Google Form: 38 questions in 11 sections, built by script from a Workshop tab.
- Answers feed a five-level messaging architecture (primary; context, problem, promise; how; benefits and proof; secondary). Drafts come from =AI(); a person types the approved line.
- The Messages tab gains Role, Source and Source line. Adjunct tabs: Refinements, Audiences, Proof.
- A brand style sheet holds Colors, Type, Layout, Logo, Imagery, Voice, Personality and Gems, and exports itself as one text cell for scripts, agents and Gems.
- Worked example for SVG to Slides: https://drive.google.com/drive/folders/1EOSAfzAkwnhXBWwTkqBSMdMxF-BH9t50
- Starter pack: https://drive.google.com/drive/folders/12DEX6TnEHQ8goCO29j9ubwYfHP5K72-q

## Workshop sections
Company and focus; market; champion; target organizations; buying scenarios; awareness (1 to 5); needs (must, important, nice); selling proposition (unique, relevant, believable); sweet spot; message raw material; personality and tone (twelve archetypes, four tone scales).

Workshop tab columns: Latest response (newest form row, matched by question text), Override, Final. Everything downstream reads Final.

## Architecture
17 rows on five levels. Each row joins its workshop inputs into Source notes and drafts with the AI function (https://support.google.com/docs/answer/15877199):

    =AI("Promise. Write this element of a B2B messaging hierarchy from the workshop notes. One or two sentences. Plain, specific, active voice.", E6)

Example from our test: Gemini drafted "Convert SVG files into editable vector shapes directly inside Google Slides." The approved lead message is "Editable SVGs in Google Slides."

## Style sheet
Type is set by role (eyebrow, headline, subhead, title, body, stat, label, cta, legal). The Messages tab gives each slot a role; `apply_style.gs` sets font, size and colour on tagged text boxes. The Export tab joins all tabs into one cell of text.

## Gems
Message drafter, copy editor, image maker, image prep, asset checker. Paste the instructions into a Gem, then the export block. Availability depends on your Google plan.

## Test results
- AI formulas written by import or API show as text until you click Generate and fill. One click covers a selected range.
- Our test account hit the monthly AI function limit after five cells.
- The Slides Gemini side panel was not available on that account, so the whole-deck edit is still untested by us.
- Sheet formulas and the export block compute. workshop_form.gs built the example form on its first run, on a Workspace account; another account refused the permission request ("This app is blocked"). apply_style.gs and sync_copy.gs have not been run yet.

The screens in the post are mockups. Google Slides, Google Sheets, Google Forms, Google Drive and Gemini are trademarks of Google LLC.
