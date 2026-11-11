# Run a messaging workshop in Google Forms and build a brand style sheet in Google Sheets

*Nov 9, 2026 · svgslid.es blog · Part 2 of the collateral series (part 1: https://svgslid.es/blog/google-slides-collateral-messaging-sheet-gemini)*

## TL;DR
- A messaging workshop runs as a Google Form: 38 questions in 11 sections, built by script from a Workshop tab.
- Answers feed a five-level messaging architecture (primary; context, problem, promise; how; benefits and proof; secondary). Drafts come from =AI(); a person sets each of the 17 lines.
- The Messages tab takes each brief from the architecture and has Gemini write the line under a recipe per role and a character limit. No approval column. Adjunct tabs: Refinements, Audiences, Proof.
- Icons and UI mockups live in two master library decks of native shapes; asset decks pull from them by tag.
- Page recipes: twelve block formulas from seven live solution and product pages, filled in as two decks.
- A brand style sheet holds Colors, Type, Layout, Logo, Imagery, Voice, Personality and Gems, and exports itself as one text cell for scripts, agents and Gems.
- Worked example for SVG to Slides: https://drive.google.com/drive/folders/1EOSAfzAkwnhXBWwTkqBSMdMxF-BH9t50
- Starter pack: https://drive.google.com/drive/folders/12DEX6TnEHQ8goCO29j9ubwYfHP5K72-q

## Workshop sections
Company and focus; market; champion; target organizations; buying scenarios; awareness (1 to 5); needs (must, important, nice); selling proposition (unique, relevant, believable); sweet spot; message raw material; personality and tone (twelve archetypes, four tone scales).

Workshop tab columns: Latest response (newest form row, matched by question text), Override, Final. Everything downstream reads Final.

## Architecture
17 rows on five levels. Each row joins its workshop inputs into Source notes and drafts with the AI function (https://support.google.com/docs/answer/15877199):

    =AI("Promise. Write this element of a B2B messaging hierarchy from the workshop notes. One or two sentences. Plain, specific, active voice.", E6)

Example from our test: Gemini drafted "Convert SVG files into editable vector shapes directly inside Google Slides." The line we kept is "Editable SVGs in Google Slides."

## Style sheet
Type is set by role (eyebrow, headline, subhead, title, body, stat, label, cta, legal). The Messages tab gives each slot a role; the Apply style menu item sets font, size and colour on tagged text boxes. The Export tab joins all tabs into one cell of text.

## Gems
Message drafter, copy editor, image maker, image prep, asset checker. Paste the instructions into a Gem, then the export block. Availability depends on your Google plan.

## Libraries and page recipes
- Icon library (https://docs.google.com/presentation/d/1aiPHjI3cdyQO8QnRu5GYpR2mLv0aFSCbSKramv4vOc0/edit): 85 Phosphor icons (MIT), one per slide, native shapes tagged lib:<name>, with a small white keyword label for Ctrl+F. UI library (https://docs.google.com/presentation/d/1YiYVc8NgGR9VfWS5ySz5-0LwCbhVUtaRYRRBHdKrTpE/edit): 13 mockups.
- Asset slots are tagged icon:<key> and ui:<name>. Place icons and UIs swaps them for library shapes and keeps the deck's file ID. Add to library appends converted slides from svgslid.es/convert. The Icons tab has a searchable dropdown of library names.
- Page recipes (https://docs.google.com/spreadsheets/d/1ehY-jZ3Tq1q7070H8WEEniZr_yqYNPwik_4nHf-OCQE/edit): hero, proof bar, problem, pillar trio, feature row, benefit list, feature grid, how it works, FAQ, closing CTA, fact columns, testimonial. Solution pages keep feature names out of headlines until a grid; product pages name the feature first and explain the mechanism. Filled in as a solution page deck (https://docs.google.com/presentation/d/11x2sGv4ZbPbD1BBlyp9bVaXt2fYli2Ki6l2XpgXgY08/edit) and a product page deck (https://docs.google.com/presentation/d/1cG0kRn9CByAw4vw6dv9H9lJBDx8SfAqwn8-bsuzlybA/edit).

## Test results (Nov 10, 2026)
- AI formulas written by script, import or API show as text until you click Generate and fill. One click covers a selected range. The 82 Line formulas had not been generated when this was written.
- Our first test account hit the monthly AI function limit after five cells.
- Gemini in Slides, on a Workspace account: a single-slide prompt applied three lines word for word and kept fonts, sizes and slot tags. The whole-deck prompt was refused; the rollout had not reached the account.
- Gemini in the Slides side panel wrote a 16-element SVG UI mockup to a palette-and-elements brief; it converted to native shapes plus two text boxes without edits.
- Dry run opened four decks and reported zero to three slots to change in each. Place icons and UIs worked after two fixes to mockup text (box width, type scaled from box height).
- Scripts ran on a sheet owned by the Workspace account that runs them. A personal account refused ("This app is blocked"); a sheet owned by another account showed an unverified-app warning. Link chips on the Assets tab break the script.
- Not yet run end to end: Sync all with generated lines, Add to library.

The screens in the post are mockups. Google Slides, Google Sheets, Google Forms, Google Drive and Gemini are trademarks of Google LLC.
