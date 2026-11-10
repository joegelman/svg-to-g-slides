from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.chart import BarChart, Reference
from messages import ROWS

wb = Workbook()
HEAD = PatternFill("solid", fgColor="F4F5F7")
def head(ws, widths):
    for c in ws[1]:
        c.font = Font(name="Arial", bold=True); c.fill = HEAD
        c.alignment = Alignment(vertical="center")
    ws.freeze_panes = "A2"
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = Font(name="Arial"); c.alignment = Alignment(wrap_text=True, vertical="top")

ws = wb.active; ws.title = "Messages"
ws.append(["Key", "Fact", "Draft", "Approved line", "Budget", "Length", "Fits", "Used in"])
for i, (k, f, l, b, u) in enumerate(ROWS, start=2):
    ws.append([k, f,
        f'=IFERROR(AI("Write one line of product marketing copy from this fact. At most "&E{i}&" characters. "&Voice!$B$2, B{i}),"")',
        l, b, f"=LEN(D{i})", f'=IF(D{i}="","Empty",IF(F{i}<=E{i},"OK","Over by "&(F{i}-E{i})))', u])
head(ws, {"A": 20, "B": 46, "C": 46, "D": 52, "E": 9, "F": 9, "G": 12, "H": 30})
n = len(ROWS) + 1
ws.conditional_formatting.add(f"G2:G{n}", FormulaRule(formula=['LEFT($G2,4)="Over"'], fill=PatternFill("solid", bgColor="FBD5D0", fgColor="FBD5D0")))
ws.conditional_formatting.add(f"G2:G{n}", FormulaRule(formula=['$G2="Empty"'], fill=PatternFill("solid", bgColor="FFF2CC", fgColor="FFF2CC")))

ws = wb.create_sheet("Voice")
ws.append(["Setting", "Value", "Notes"])
ws.append(["Voice rules", "Plain and specific. Active voice. Say what the product does. No superlatives, no exclamation marks, no questions.", "Every Draft formula on the Messages tab reads this cell."])
ws.append(["Audience", "IT and security leads at mid-size companies.", "Edit to match your buyer."])
ws.append(["Product", "Relay, a secure file transfer service (fictional sample).", "Replace with your product."])
ws.append(["How to use", "Write the plain fact in Fact. Read the Draft. Paste the line you approve into Approved line as plain text. Only Approved line reaches an asset.", "The Draft column needs a Google plan that includes Gemini. Without it the column stays blank and you write Approved line by hand."])
head(ws, {"A": 16, "B": 70, "C": 60})

ws = wb.create_sheet("Assets")
ws.append(["Asset", "Deck URL", "Sync?", "Last synced", "Slots changed", "Flags"])
D = "https://docs.google.com/presentation/d/"
for name, i in [("One-pager (Letter)", "1feiCP4d4Gi_crzSQFDib4JgMrdq8pxt6BdLs9JHTucU"),
                ("One-pager, print with bleed", "11p2Rb2uAxAQ0Kw4kKt4Rs84bWL3ccV8miyxrEyRlj8A"),
                ("Solution brief", "1E4RW38YNuj7lZER7ZM88fDFJtJCFT7kdL01XRPXK5vc"),
                ("Whitepaper", "1-2caooSTgUQduoKtqya8wmM-9mIW8ncb3NlDu6B6NFQ"),
                ("Battlecard", "14sTC645cIijFziQDjfOjiobxQWDKRHECai6jj8d8LW4")]:
    ws.append([name, D + i + "/edit", True, "", "", ""])
ws.append(["Replace each URL with the URL of your own copy. The script only touches rows where Sync? is TRUE."])
head(ws, {"A": 30, "B": 70, "C": 8, "D": 20, "E": 14, "F": 50})

ws = wb.create_sheet("Data")
ws.append(["Capability", "Starter", "Team", "Enterprise"])
for r in [("Transfer size limit", "2 GB", "10 GB", "10 GB"), ("Single sign-on", "Included", "Included", "Included"),
          ("Link expiry and download limits", "Included", "Included", "Included"),
          ("Audit log export", "Not included", "Included", "Included"),
          ("Custom retention rules", "Not included", "Not included", "Included")]:
    ws.append(r)
ws.append([]); ws.append(["Sample data for a linked chart. Copy A1:D6 or the chart, paste into Slides, choose Link to spreadsheet."])
ws.append(["Quarter", "Transfers sent (sample)"])
for r in [("Q1", 1200), ("Q2", 1850), ("Q3", 2400), ("Q4", 3100)]:
    ws.append(r)
head(ws, {"A": 34, "B": 22, "C": 16, "D": 16})
for c in ws[9]:
    c.font = Font(name="Arial", bold=True); c.fill = HEAD
ch = BarChart(); ch.type = "col"; ch.legend = None; ch.title = None
ch.add_data(Reference(ws, min_col=2, min_row=9, max_row=13), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=10, max_row=13))
ch.width, ch.height = 14, 7
ws.add_chart(ch, "F2")

ws = wb.create_sheet("Sizes")
ws.append(["Asset", "Width", "Height", "Unit", "Pages", "Page setup entry", "Notes"])
for r in [("One-pager, US Letter", 8.5, 11, "in", 1, "Custom: 8.5 x 11 in", "Portrait."),
          ("One-pager, A4", 21, 29.7, "cm", 1, "Custom: 21 x 29.7 cm", "Portrait."),
          ("One-pager, US Letter with bleed", 8.75, 11.25, "in", 1, "Custom: 8.75 x 11.25 in", "Adds 0.125 in per side. Keep text 0.25 in inside the trim."),
          ("One-pager, A4 with bleed", 21.6, 30.3, "cm", 1, "Custom: 21.6 x 30.3 cm", "Adds 3 mm per side. Keep text 6 mm inside the trim."),
          ("Solution brief", 8.5, 11, "in", 2, "Custom: 8.5 x 11 in", "Front and back."),
          ("Whitepaper", 8.5, 11, "in", "4+", "Custom: 8.5 x 11 in", "One page per slide. Cover, inside pages, back."),
          ("Battlecard", 11, 8.5, "in", 1, "Custom: 11 x 8.5 in", "Landscape. Read on screen."),
          ("Sales deck", 10, 5.625, "in", "Any", "Widescreen 16:9", "The Slides default."),
          ("Poster 18 x 24 with bleed", 18.25, 24.25, "in", 1, "Custom: 18.25 x 24.25 in", "Ask the printer for their bleed. 0.125 in is common."),
          ("Web banner", 1200, 628, "px", 1, "Custom: 1200 x 628 px", "Check the current spec of the platform before you build.")]:
    ws.append(r)
head(ws, {"A": 34, "B": 9, "C": 9, "D": 7, "E": 8, "F": 26, "G": 60})

ws = wb.create_sheet("Approvals")
ws.append(["Date", "Keys changed", "What changed", "Requested by", "Approver", "Decision", "Assets synced", "Assets locked"])
ws.append(["2026-11-09", "benefit_1_title, win_1", "Example row: SSO moved to every plan.", "Name", "Name", "Approved", "One-pager, Battlecard", "Yes"])
head(ws, {"A": 12, "B": 26, "C": 44, "D": 16, "E": 16, "F": 12, "G": 28, "H": 14})
wb.save("out/Messaging sheet.xlsx")
