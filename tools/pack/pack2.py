"""Starter pack part 2: workshop -> messaging architecture -> messages, plus the brand style sheet.

Builds two sets of workbooks from the same code: the naked sample (Relay, fictional)
and the filled instance for SVG to Slides. Formulas that Sheets must parse natively
(=AI, FILTER/ARRAYFORMULA exports) are written after upload; see FORMULAS_*.json.
"""
import json
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import FormulaRule

OUT = Path(__file__).parent / "out2"
OUT.mkdir(exist_ok=True)
HEAD = PatternFill("solid", fgColor="F4F5F7")

# ---------------------------------------------------------------- workshop questions
ARCH = ["Caregiver", "Ruler", "Creator", "Lover", "Jester", "Everyman", "Innocent", "Sage", "Explorer", "Maverick", "Magician", "Hero"]
MOTIV = ["Be in control", "Be accepted by the team", "Do excellent work", "Be seen as the expert", "Save effort", "Build something new", "Avoid risk"]
Q = [  # key, section, question, type, choices
    ("name", "1. Company and focus", "What is the company or product called?", "short", ""),
    ("what", "1. Company and focus", "In one plain sentence, what does it do?", "long", ""),
    ("future", "1. Company and focus", "Where should it be in two years?", "long", ""),
    ("category", "2. Market", "What category do customers put you in? (This)", "short", ""),
    ("not_category", "2. Market", "What do people mistake you for that you are not? (Not this)", "long", ""),
    ("category_age", "2. Market", "Is the category existing or new?", "choice", "Existing|New|Existing, with a new angle"),
    ("alternatives", "2. Market", "What are the top three alternatives a buyer considers, including doing nothing?", "long", ""),
    ("champion", "3. Champion", "Who is the champion? Give the job title.", "short", ""),
    ("champion_job", "3. Champion", "What is the champion responsible for?", "long", ""),
    ("goal_explicit", "3. Champion", "Explicit goal: what direct result do they want from a product like this?", "long", ""),
    ("goal_implicit", "3. Champion", "Implicit goal: what is the personal motivation behind the purchase?", "choice", "|".join(MOTIV)),
    ("org_size", "4. Target organizations", "What size of organization? Give a not-smaller-than and a not-larger-than.", "short", ""),
    ("org_verticals", "4. Target organizations", "Which verticals come first?", "long", ""),
    ("org_qualifiers", "4. Target organizations", "What must be true of an organization for it to be a fit?", "long", ""),
    ("scenario_primary", "5. Buying scenarios", "Primary buying scenario: what is happening when they go looking?", "long", ""),
    ("scenario_secondary", "5. Buying scenarios", "Secondary buying scenarios, one per line.", "long", ""),
    ("awareness", "6. Awareness", "How aware is the champion today? 1 = not sure they have the problem, 5 = knows the competition and asks why you are better.", "scale", "1|5"),
    ("need_must", "7. Needs", "Must have: finish the sentence \"I have to...\"", "long", ""),
    ("need_important", "7. Needs", "Important to have: finish the sentence \"I want to...\"", "long", ""),
    ("need_nice", "7. Needs", "Nice to have: finish the sentence \"It would be nice to...\"", "long", ""),
    ("unique", "8. Selling proposition", "Unique: what is different from what competitors offer?", "long", ""),
    ("relevant", "8. Selling proposition", "Relevant: which real need or pain does that difference meet?", "long", ""),
    ("believable", "8. Selling proposition", "Believable: what proof supports it? Numbers, customers, reviews, how it works.", "long", ""),
    ("sweet_spot", "9. Sweet spot", "What do you do for customers that rivals cannot, in this market?", "long", ""),
    ("context", "10. Message raw material", "Context: what changed in the world that makes this matter now?", "long", ""),
    ("problem", "10. Message raw material", "Problem: what is still broken, even with the current options?", "long", ""),
    ("promise", "10. Message raw material", "Promise: what do you make possible?", "long", ""),
    ("how", "10. Message raw material", "How it works, in three steps or pillars. One per line.", "long", ""),
    ("benefits", "10. Message raw material", "Benefits a buyer gets. One per line, most important first.", "long", ""),
    ("secondary", "10. Message raw material", "Secondary points worth saying further down the page. One per line.", "long", ""),
    ("archetype", "11. Personality and tone", "Which archetype is the brand?", "choice", "|".join(ARCH)),
    ("archetype_2", "11. Personality and tone", "Which archetype is the runner-up?", "choice", "|".join(ARCH)),
    ("tone_formal", "11. Personality and tone", "Tone: 1 = formal, 5 = casual.", "scale", "1|5"),
    ("tone_serious", "11. Personality and tone", "Tone: 1 = serious, 5 = funny.", "scale", "1|5"),
    ("tone_respect", "11. Personality and tone", "Tone: 1 = respectful, 5 = irreverent.", "scale", "1|5"),
    ("tone_energy", "11. Personality and tone", "Tone: 1 = matter-of-fact, 5 = enthusiastic.", "scale", "1|5"),
    ("avoid_language", "11. Personality and tone", "Which phrases does the whole category use that you should not lead with?", "long", ""),
    ("words", "11. Personality and tone", "Words you always use, and words you never use.", "long", ""),
]
QROW = {q[0]: i for i, q in enumerate(Q, start=2)}

# ---------------------------------------------------------------- architecture rows
A = [  # level, key, element, workshop keys, budget
    ("Primary", "tagline", "Lead message / tagline", ["what", "sweet_spot", "promise"], 48),
    ("Primary", "positioning", "Positioning statement", ["category", "champion", "unique", "relevant"], 220),
    ("Level 2", "context", "Context", ["context"], 200),
    ("Level 2", "problem", "Problem", ["problem", "alternatives"], 200),
    ("Level 2", "promise", "Promise", ["promise", "sweet_spot"], 200),
    ("Level 3", "how_1", "How it works 1", ["how"], 90),
    ("Level 3", "how_2", "How it works 2", ["how"], 90),
    ("Level 3", "how_3", "How it works 3", ["how"], 90),
    ("Level 4", "benefit_1", "Benefit 1", ["benefits", "need_must"], 110),
    ("Level 4", "benefit_2", "Benefit 2", ["benefits", "need_important"], 110),
    ("Level 4", "benefit_3", "Benefit 3", ["benefits", "need_important"], 110),
    ("Level 4", "benefit_4", "Benefit 4", ["benefits", "need_nice"], 110),
    ("Level 4", "proof", "Proof", ["believable"], 160),
    ("Level 5", "secondary_1", "Secondary 1", ["secondary"], 110),
    ("Level 5", "secondary_2", "Secondary 2", ["secondary"], 110),
    ("Level 5", "secondary_3", "Secondary 3", ["secondary"], 110),
    ("Level 5", "secondary_4", "Secondary 4", ["secondary"], 110),
]
AROW = {a[1]: i for i, a in enumerate(A, start=2)}
A_PROMPT = {
    "Primary": "Write this element of a B2B messaging hierarchy from the workshop notes. One line. Plain, specific, active voice. No superlatives.",
    "Level 2": "Write this element of a B2B messaging hierarchy from the workshop notes. One or two sentences. Plain, specific, active voice.",
    "Level 3": "The notes list how the product works, one step per line. Write step {n} as one short sentence. Plain, specific, active voice.",
    "Level 4": "The notes list benefits, one per line. Write benefit {n} as one sentence that names what the buyer gets. Plain, specific.",
    "Level 5": "The notes list secondary points, one per line. Write point {n} as one sentence. Plain, specific.",
}


def head(ws, widths, wrap=True):
    for c in ws[1]:
        c.font = Font(name="Arial", bold=True); c.fill = HEAD; c.alignment = Alignment(vertical="center")
    ws.freeze_panes = "A2"
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = Font(name="Arial"); c.alignment = Alignment(wrap_text=wrap, vertical="top")


def fits_rules(ws, col, n):
    ws.conditional_formatting.add(f"{col}2:{col}{n}", FormulaRule(formula=[f'LEFT(${col}2,4)="Over"'], fill=PatternFill("solid", bgColor="FBD5D0", fgColor="FBD5D0")))
    ws.conditional_formatting.add(f"{col}2:{col}{n}", FormulaRule(formula=[f'${col}2="Empty"'], fill=PatternFill("solid", bgColor="FFF2CC", fgColor="FFF2CC")))


def _inline(wb, api):
    from openpyxl.utils import range_boundaries
    for rng, rows in api.items():
        tab, a1 = rng.split("!")
        c1, r1, _, _ = range_boundaries(a1 if ":" in a1 else a1 + ":" + a1)
        for i, row in enumerate(rows):
            if row[0]:
                cell = wb[tab].cell(row=r1 + i, column=c1, value=row[0])
                cell.font = Font(name="Arial"); cell.alignment = Alignment(wrap_text=True, vertical="top")


def architecture_book(b):
    """b: brand dict with answers{key: text}, arch{key: approved}, messages[(key, role, source, line, budget, used)]."""
    wb = Workbook()
    api = {}  # range -> formulas written through the Sheets API after upload

    ws = wb.active; ws.title = "Workshop"
    ws.append(["Key", "Section", "Question", "Type", "Choices", "Latest response", "Override", "Final"])
    for i, (k, sec, q, typ, ch) in enumerate(Q, start=2):
        f = (f'=IFERROR(INDEX(INDIRECT("\'Responses\'!A:BZ"),MAX(2,COUNTA(INDIRECT("\'Responses\'!A:A"))),'
             f'MATCH(C{i},INDIRECT("\'Responses\'!1:1"),0))&"","")')
        ws.append([k, sec, q, typ, ch, f, b["answers"].get(k, ""), f'=IF(G{i}<>"",G{i},F{i})'])
    head(ws, {"A": 18, "B": 24, "C": 58, "D": 9, "E": 28, "F": 40, "G": 54, "H": 54})

    ws = wb.create_sheet("Architecture")
    ws.append(["Level", "Key", "Element", "Workshop inputs", "Source notes", "Draft", "Approved line", "Budget", "Length", "Fits"])
    drafts, count = [], {}
    for i, (lvl, k, el, keys, bud) in enumerate(A, start=2):
        refs = ",".join(f"Workshop!H{QROW[x]}" for x in keys)
        ws.append([lvl, k, el, ", ".join(keys), f'=TEXTJOIN(" | ",TRUE,{refs})', "", b["arch"].get(k, ""), bud, f"=LEN(G{i})",
                   f'=IF(G{i}="","Empty",IF(I{i}<=H{i},"OK","Over by "&(I{i}-H{i})))'])
        count[lvl] = count.get(lvl, 0) + 1
        p = A_PROMPT[lvl].replace("{n}", str(count[lvl]))
        drafts.append([f'=AI("{el}. {p}", E{i})'])
    api[f"Architecture!F2:F{len(A)+1}"] = drafts
    head(ws, {"A": 10, "B": 14, "C": 24, "D": 26, "E": 50, "F": 46, "G": 56, "H": 8, "I": 8, "J": 11})
    fits_rules(ws, "J", len(A) + 1)

    ws = wb.create_sheet("Messages")
    ws.append(["Key", "Role", "Source", "Source line", "Draft", "Approved line", "Budget", "Length", "Fits", "Used in"])
    drafts = []
    for i, (k, role, src, line, bud, used) in enumerate(b["messages"], start=2):
        srcline = f'=IFERROR(VLOOKUP(C{i},Architecture!$B:$G,6,FALSE),"")' if src else ""
        ws.append([k, role, src, srcline, "", line, bud, f"=LEN(F{i})", f'=IF(F{i}="","Empty",IF(H{i}<=G{i},"OK","Over by "&(H{i}-G{i})))', used])
        drafts.append([f'=AI("Write {role} copy for a one-page asset from this approved message. At most {bud} characters. Plain, specific, active voice.", D{i})' if src else ""])
    n = len(b["messages"]) + 1
    api[f"Messages!E2:E{n}"] = drafts
    head(ws, {"A": 20, "B": 10, "C": 14, "D": 44, "E": 44, "F": 52, "G": 8, "H": 8, "I": 11, "J": 26})
    fits_rules(ws, "I", n)

    ws = wb.create_sheet("Refinements")
    ws.append(["Date", "Key", "Tab", "Previous line", "New line", "Reason", "Source", "Requested by", "Status"])
    for r in b["refinements"]:
        ws.append(r)
    head(ws, {"A": 12, "B": 18, "C": 14, "D": 44, "E": 44, "F": 34, "G": 22, "H": 16, "I": 12})

    ws = wb.create_sheet("Audiences")
    ws.append(["Key", "Base line", "Audience", "Variant draft", "Approved variant", "Budget", "Length", "Fits"])
    drafts = []
    for i, (k, aud, var) in enumerate(b["audiences"], start=2):
        ws.append([k, f'=IFERROR(VLOOKUP(A{i},Messages!$A:$F,6,FALSE),"")', aud, "", var, f'=IFERROR(VLOOKUP(A{i},Messages!$A:$G,7,FALSE),"")',
                   f"=LEN(E{i})", f'=IF(E{i}="","Empty",IF(G{i}<=F{i},"OK","Over by "&(G{i}-F{i})))'])
        drafts.append([f'=AI("Rewrite this line for the audience named in the second cell. Keep the claim the same. Same length or shorter. Plain, specific.", B{i}:C{i})'])
    api[f"Audiences!D2:D{len(b['audiences'])+1}"] = drafts
    head(ws, {"A": 20, "B": 48, "C": 26, "D": 48, "E": 48, "F": 8, "G": 8, "H": 11})
    fits_rules(ws, "H", len(b["audiences"]) + 1)

    ws = wb.create_sheet("Proof")
    ws.append(["Claim", "Evidence", "Source", "Date checked", "Usable in"])
    for r in b["proof"]:
        ws.append(r)
    head(ws, {"A": 40, "B": 50, "C": 44, "D": 14, "E": 26})

    ws = wb.create_sheet("Assets")
    ws.append(["Asset", "Deck URL", "Sync?", "Last synced", "Slots changed", "Flags", "Kind"])
    for name, url, kind in b["assets"]:
        ws.append([name, url, True, "", "", "", kind])
    ws.append(["Replace each URL with the URL of your own copy. Kind is print or deck and picks the type sizes from the style sheet."])
    head(ws, {"A": 30, "B": 70, "C": 8, "D": 20, "E": 14, "F": 50, "G": 8})

    ws = wb.create_sheet("Approvals")
    ws.append(["Date", "Keys changed", "What changed", "Requested by", "Approver", "Decision", "Assets synced", "Assets locked"])
    ws.append(["2026-11-09", "tagline", "Example row. Replace it.", "Name", "Name", "Approved", "One-pager", "Yes"])
    head(ws, {"A": 12, "B": 26, "C": 44, "D": 16, "E": 16, "F": 12, "G": 28, "H": 14})

    _inline(wb, api)
    p = OUT / f"{b['slug']} - Messaging architecture.xlsx"
    wb.save(p)
    (OUT / f"{b['slug']}-architecture-formulas.json").write_text(json.dumps(api))
    return p


GEMS = [
    ("Message drafter", "Turns a plain fact into a finished line that fits a character budget.", "Messages and Architecture tabs; Gemini side panel in Sheets",
     "You draft product marketing lines. You are given a plain fact, a role (eyebrow, headline, subhead, body, stat, label, cta, legal) and a character budget. Return one line. Stay inside the budget. Keep the claim exactly as the fact states it. Follow the voice rules and word lists in the style block below. Never add a claim, number or customer name that is not in the fact."),
    ("Copy editor", "Checks a draft against the voice rules and says what to change.", "Docs, Slides and Sheets side panels",
     "You edit copy against the style block below. List each line that breaks a voice rule, name the rule, and give a corrected line of the same length or shorter. Do not change claims, numbers or product names. If a line already follows the rules, say so and leave it."),
    ("Image maker", "Generates images in the brand's imagery style.", "Gemini app; Slides image generation",
     "You generate images for collateral. Follow the Imagery rules in the style block below for subject, style, background, colour and what to avoid. Use only the brand colours listed. No text inside the image. No logos of any company. Ask for the asset and the slot size if they are not given, and compose for that aspect ratio."),
    ("Image prep", "Prepares a supplied image for a slot: crop, background, treatment, export size.", "Gemini app, with the image attached",
     "You prepare supplied images for collateral. For each image: crop to the aspect ratio of the named slot, keep the subject inside the safe area, apply the treatment named in the Imagery rules, and remove or replace the background as those rules say. Do not add elements that were not in the original. Report the final pixel size and what you changed."),
    ("Asset checker", "Reviews a finished deck against the style sheet and the messaging sheet.", "Slides side panel, with both sheets referenced",
     "You review an asset. Compare every text box with the Approved line column of the messaging sheet and list any difference. Compare fonts, sizes and colours with the Type and Colors rules in the style block below and list any difference by page. List any text that spills out of its box or overlaps another element. Change nothing. Report only."),
]


def style_book(b):
    wb = Workbook(); api = {}
    ws = wb.active; ws.title = "Colors"
    ws.append(["Token", "Hex", "Role", "Use for", "Text on it"])
    for r in b["colors"]:
        ws.append(r)
    head(ws, {"A": 14, "B": 11, "C": 16, "D": 54, "E": 12})
    for i, r in enumerate(b["colors"], start=2):
        ws.cell(row=i, column=6).fill = PatternFill("solid", fgColor=r[1].lstrip("#"))
    ws["F1"] = "Swatch"; ws["F1"].font = Font(name="Arial", bold=True); ws["F1"].fill = HEAD

    ws = wb.create_sheet("Type")
    ws.append(["Role", "Font", "Weight", "Print pt", "Deck pt", "Line spacing", "Colour token", "Case", "Notes"])
    for r in b["type"]:
        ws.append(r)
    head(ws, {"A": 12, "B": 14, "C": 10, "D": 9, "E": 9, "F": 12, "G": 13, "H": 12, "I": 50})

    ws = wb.create_sheet("Layout")
    ws.append(["Token", "Value", "Unit", "Applies to", "Notes"])
    for r in b["layout"]:
        ws.append(r)
    head(ws, {"A": 20, "B": 10, "C": 8, "D": 22, "E": 60})

    ws = wb.create_sheet("Logo")
    ws.append(["Rule", "Value"])
    for r in b["logo"]:
        ws.append(r)
    head(ws, {"A": 26, "B": 90})

    ws = wb.create_sheet("Imagery")
    ws.append(["Rule", "Value"])
    for r in b["imagery"]:
        ws.append(r)
    head(ws, {"A": 26, "B": 90})

    ws = wb.create_sheet("Voice")
    ws.append(["Rule", "Do", "Do not", "Before", "After"])
    for r in b["voice"]:
        ws.append(r)
    head(ws, {"A": 26, "B": 40, "C": 40, "D": 44, "E": 44})

    ws = wb.create_sheet("Personality")
    ws.append(["Item", "Value", "Notes"])
    for r in b["personality"]:
        ws.append(r)
    head(ws, {"A": 26, "B": 44, "C": 70})

    ws = wb.create_sheet("Gems")
    ws.append(["Gem", "Job", "Where to use it", "Instructions (paste into the Gem, then paste the Export block under it)"])
    for r in GEMS:
        ws.append(list(r))
    head(ws, {"A": 18, "B": 44, "C": 34, "D": 110})

    ws = wb.create_sheet("Export")
    ws.append(["Style block: one cell an agent, a script or a Gem can read. Built by formula from the other tabs."])
    ws.append([""])
    head(ws, {"A": 120})
    api["Export!A2"] = [[(
        '="/* ' + b["name"] + ' style block */"&CHAR(10)&"colors {"&CHAR(10)&TEXTJOIN(CHAR(10),TRUE,ARRAYFORMULA("  --"&FILTER(Colors!A2:A40,Colors!A2:A40<>"")&": "&FILTER(Colors!B2:B40,Colors!A2:A40<>"")&";  /* "&FILTER(Colors!C2:C40,Colors!A2:A40<>"")&" */"))&CHAR(10)&"}"'
        '&CHAR(10)&"type {"&CHAR(10)&TEXTJOIN(CHAR(10),TRUE,ARRAYFORMULA("  "&FILTER(Type!A2:A40,Type!A2:A40<>"")&": "&FILTER(Type!B2:B40,Type!A2:A40<>"")&" "&FILTER(Type!C2:C40,Type!A2:A40<>"")&", print "&FILTER(Type!D2:D40,Type!A2:A40<>"")&"pt, deck "&FILTER(Type!E2:E40,Type!A2:A40<>"")&"pt, color "&FILTER(Type!G2:G40,Type!A2:A40<>"")&";"))&CHAR(10)&"}"'
        '&CHAR(10)&"voice {"&CHAR(10)&TEXTJOIN(CHAR(10),TRUE,ARRAYFORMULA("  "&FILTER(Voice!A2:A40,Voice!A2:A40<>"")&". Do: "&FILTER(Voice!B2:B40,Voice!A2:A40<>"")&" Do not: "&FILTER(Voice!C2:C40,Voice!A2:A40<>"")))&CHAR(10)&"}"'
        '&CHAR(10)&"personality {"&CHAR(10)&TEXTJOIN(CHAR(10),TRUE,ARRAYFORMULA("  "&FILTER(Personality!A2:A40,Personality!A2:A40<>"")&": "&FILTER(Personality!B2:B40,Personality!A2:A40<>"")))&CHAR(10)&"}"'
        '&CHAR(10)&"imagery {"&CHAR(10)&TEXTJOIN(CHAR(10),TRUE,ARRAYFORMULA("  "&FILTER(Imagery!A2:A40,Imagery!A2:A40<>"")&": "&FILTER(Imagery!B2:B40,Imagery!A2:A40<>"")))&CHAR(10)&"}"'
        '&CHAR(10)&"logo {"&CHAR(10)&TEXTJOIN(CHAR(10),TRUE,ARRAYFORMULA("  "&FILTER(Logo!A2:A40,Logo!A2:A40<>"")&": "&FILTER(Logo!B2:B40,Logo!A2:A40<>"")))&CHAR(10)&"}"')]]
    _inline(wb, api)
    p = OUT / f"{b['slug']} - Brand style sheet.xlsx"
    wb.save(p)
    (OUT / f"{b['slug']}-style-formulas.json").write_text(json.dumps(api))
    return p


if __name__ == "__main__":
    from brands import RELAY, SVGS
    for b in (RELAY, SVGS):
        print(architecture_book(b)); print(style_book(b))
