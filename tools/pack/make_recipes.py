from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
import make_pages as mp, ui_kit
wb = Workbook()
def tab(name, head, rows, widths):
    ws = wb.create_sheet(name); ws.append(head)
    for r in rows: ws.append(list(r))
    for c in ws[1]: c.font = Font(bold=True); c.fill = PatternFill("solid", fgColor="F4F5F7")
    for i, w in enumerate(widths): ws.column_dimensions[chr(65 + i)].width = w
    for row in ws.iter_rows(): 
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"; return ws
wb.remove(wb.active)
R = [
 ("R1", "Hero", "Solution: [outcome the reader wants] (in/with [place they work]) or [category] for [persona]. Product: [feature or category name] for/designed for [context].", "[What you do, as 2 or 3 verbs or parts] + [what you get]. One or two sentences.", "eyebrow, headline, subhead, CTA, reassurance line, product UI", "Headline 5 to 8 words. Subhead 15 to 30 words.", "Whole-product UI in its real setting", "All seven pages"),
 ("R2", "Proof bar", "[Number] [who] [verb] [product], or one plain status line", "None. Numbers and labels carry it.", "stat or logo row, optional one-line claim", "Stat label under 5 words", "None, or logos", "Ramp industry, Gong, Riskified, Close, Pitch product"),
 ("R3", "Problem / consolidation", "[The status quo, stated flat] or [one thing, in place of several]", "[The workarounds people use today], named", "title, body, optional two sub-points", "Title 5 to 6 words. Body 13 to 25 words.", "Before and after, side by side", "Ramp industry (blocks 3, 4)"),
 ("R4", "Pillar trio", "Section: [the shift]. Each pillar: [verb + what improves], 3 to 5 words", "One sentence per pillar: mechanism, then result", "section title, 3 x (icon, title, body)", "Pillar body 17 to 20 words", "Icons only", "Gong, Riskified, Pitch product"),
 ("R5", "Feature row", "Pick one lead. Feature: [name]. Capability: [verb] + [object] + [where]. Benefit: [outcome] without [cost].", "[How it works, concretely] + [what that gives you]", "eyebrow (group name), title, body, optional link, UI crop", "Title 3 to 7 words. Body 17 to 28 words.", "A crop of the UI that shows the mechanism named in the body", "All seven pages. The core repeating block."),
 ("R6", "Benefit list", "No section headline needed, or a 3-word label", "4 x [bold lead of 2 to 4 words] + one clause", "4 bullets with icons", "About 45 words total", "Icons", "Ramp product (block 3)"),
 ("R7", "Feature grid", "Card title is the feature's name, 2 to 3 words", "One sentence: what the feature lets you do", "3 to 6 cards: thumbnail, title, body, optional link", "Card body 11 to 17 words", "Small UI thumbnail per card", "Pitch solution, Ramp product (use-case grid), Gong (persona grid)"),
 ("R8", "How it works / tabbed detail", "Section: capability across all cases. Each step or tab: a noun or one verb", "One sentence per step, or benefit title + body + 3 bullets per tab", "section title, 3 to 5 x (label, UI, body)", "Step body under 12 words", "One UI state per step", "Close (channel tabs), Riskified (abuse types), Fletch product-page rule"),
 ("R9", "FAQ", "Question in the reader's words, capability first", "Answer in the first sentence, then the limit or condition", "4 to 6 Q and A pairs", "Web: 40 to 50 words per answer. Print or slide: under 20.", "None", "Ramp x2, Gong, Close"),
 ("R10", "Closing CTA", "Imperative, 4 to 5 words, outcome or first action", "Optional: 3 things you get, or one reassurance line", "headline, CTA, reassurance", "Headline 4 to 5 words", "None, or one device shot", "All seven pages"),
 ("R11", "Fact columns", "Column title is a 3 to 4 word benefit or a product name", "3 or 4 flat facts per column, no sentences", "3 x (rule, title, bullets)", "Bullet under 8 words", "None", "Ramp product (blocks 16 to 18)"),
 ("R12", "Testimonial", "None, or a section title naming the persona", "Quote under 25 words with one concrete result. Name, title, company.", "quote, attribution, logo; often attached to a feature row", "Quote 15 to 25 words", "Headshot or logo", "Pitch x2, Ramp x2, Gong (one per feature row)"),
]
tab("Block recipes", ["ID", "Block", "Headline formula", "Body formula", "Elements", "Length", "Visual", "Seen on"], R, [6, 20, 50, 46, 34, 26, 30, 34])
P = [
 ("Solution page (persona, industry or team)", "Capability and use case for one named reader", "R1 hero (persona or outcome-led) > R2 proof bar > R3 problem or R4 pillar trio > 3 or 4 x R5 feature rows (benefit or capability-led, each with UI, R12 quote attached where you have one) > R7 feature grid (feature names appear here for the first time) > R12 testimonials > R9 FAQ > R10 CTA", "Feature names stay out of headlines until the grid. Headlines talk about the reader's result. On the three solution pages, most feature-row headlines lead with an outcome."),
 ("Product page (feature or product)", "How it works, with the best features", "R1 hero (feature or category-led) > R6 benefit list > R8 how it works > grouped R5 feature rows under short dividers (feature or capability-led, each with UI) > R12 testimonial > R11 fact columns > R7 grid linking to neighbours > R9 FAQ > R10 CTA", "The product or feature is named in the hero. Rows explain the mechanism first, then the gain. Flat fact lists carry terms, limits and coverage."),
 ("Feature section, three leads (Fletch)", "Same facts, different first line", "Feature-led: title is the name, body is capability + benefit. Capability-led: title is what you can do, body names the feature + benefit. Benefit-led: title is the outcome, body is the cost avoided + feature.", "Choose by page: product page uses feature or capability lead; solution, persona and home pages use capability or benefit lead."),
]
tab("Page recipes", ["Page type", "Lead with", "Block order", "Rule"], P, [30, 34, 90, 70])
B = [
 ("Pitch, sales team page", "Solution", 9, "Hero outcome-led; 4 feature rows, all outcome-led, 3 to 5 word titles, 21 to 28 word bodies, one UI each; one quote mid-page; 4-card feature grid with feature-name titles; templates; CTA with 3 bullets", "No stats or logo bar. Feature names appear only in the grid."),
 ("Ramp, consulting industry page", "Solution", 11, "Hero persona-led (category for persona) with form; stat + logos; consolidation block with two sub-points; audit block, text only; 4 feature rows, 3 to 5 word titles, about 20 word bodies, each linking to its product page; 8 quotes with metrics; FAQ; 2 CTAs", "Every feature row is rewritten in the industry's vocabulary and links down to a product page."),
 ("Gong, revenue enablement page", "Solution", 16, "Announcement bar; hero outcome-led with eyebrow naming the persona; logos; pillar trio; 4 feature rows, each with its own customer quote and logo; persona grid of 4; security; integrations; reviews; form; resources; FAQ", "Proof is attached to each claim, one quote per row, and then a second pass by persona."),
 ("Ramp, corporate cards page", "Product", 22, "Hero feature-led; 4-item benefit list; feature rows grouped under short benefit dividers; logos; persona-led and problem-led rows; quote; stat-led rows; 3 fact columns; integrations; use-case grid; FAQ; CTA", "Dividers do the benefit work so the rows under them can be concrete."),
 ("Pitch, product page", "Product", 8, "Hero positioning-led with video; overview with 3 sub-features; three groups (Create, Collaborate, Deliver), each an eyebrow + benefit title + 3 capability-led sub-features of 20 to 30 words + UI; testimonial carousel with stat; template CTA", "Eyebrows name the job stage. Sub-feature titles are mostly capabilities."),
 ("Riskified, Policy Intelligence page", "Product", 7, "Hero benefit-led with a three-verb subhead; 3 capability pillars with image; logo bar with a trust line; tabbed use cases with body and two result stats; industry tabs, each problem then capability; partner CTA", "Read from the rendered page in the browser; the fetch tool was refused. Lower sections may be incomplete."),
 ("Close, communication page", "Product", 7, "Hero outcome-led with eyebrow naming the feature area and dark UI; feature row with 4 bullets, feature-led; tabbed channels (5 tabs), panel is benefit title + body + 3 bullets + UI; CTA band; FAQ; final CTA with review rating", "One big UI per block. Tabs keep five features in one block."),
]
tab("Pages observed", ["Page", "Type", "Content blocks", "Block sequence", "What stands out"], B, [30, 12, 12, 90, 60])
ws = tab("Messages (pages)", ["Key", "Role", "Source", "Recipe", "Draft", "Approved line", "Budget", "Length", "Fits", "Used in"],
    [(m[0], m[1], m[3], m[2], "", m[4], m[5], f"=LEN(F{i+2})", f'=IF(H{i+2}<=G{i+2},"OK","Over by "&(H{i+2}-G{i+2}))', m[6]) for i, m in enumerate(mp.M)], [24, 10, 18, 28, 10, 70, 8, 8, 10, 18])
U = [("ui-editor-mock", "Editor mockup from Gemini's SVG", "Deck slide 3 (earlier deck)")] + [(f"ui-{n}", w, "") for n, (_, w, _) in ui_kit.UIS.items()]
use = {"slides-editor": "Solution hero; Product how it works, step 2", "drag-ghost": "Product hero; how it works, step 1; grid card", "paste-pill": "How it works, step 3", "fill-picker": "Feature row: Edit", "png-vs-shapes": "Problem block", "reuse": "Feature row: Reuse", "letterhead": "Feature row: Build", "addon-dialog": "Grid card: add-on", "web-converter": "Grid card: web converter", "permissions": "Feature row: Permissions", "batch-grid": "Grid card: batch drop", "shape-list": "Feature row: Shapes"}
U = [(a, b, use.get(a[3:], c)) for a, b, c in U]
tab("UI components", ["Library name", "What it shows", "Used in"], U, [22, 70, 50])
tab("Read me", ["Topic", "Note"], [
 ("What this is", "Block and page recipes taken from seven solution and product pages, then filled with SVG to Slides copy."),
 ("Copy", "Every line on Messages (pages) comes from the messaging architecture or the project context. The Source column says which. Nothing is approved by Joe yet."),
 ("To sync", "Paste the Messages (pages) rows (columns A to C, F, G, J) under the existing rows on the Messages tab of the working copy, add the two decks to Assets, then run Dry run."),
 ("Left empty on purpose", "R12 testimonial and logo rows. There are no customer quotes or logos on file."),
 ("UI mockups", "Drawn as plain SVG and converted to native shapes. Pill wording follows the extension; the layout is a simplified stand-in for Google Slides."),
], [22, 110])
wb.move_sheet("Read me", -5)
wb.save("pages/SVG to Slides - Page recipes.xlsx")
