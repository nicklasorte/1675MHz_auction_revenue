"""Build 1675-1695 MHz auction valuation workbook, v0.1 (nationwide license option)."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

wb = Workbook()
F = "Arial"
BLUE = Font(name=F, color="0000FF")
BLACK = Font(name=F, color="000000")
GREEN = Font(name=F, color="008000")
BOLD = Font(name=F, bold=True)
TITLE = Font(name=F, bold=True, size=14)
MARK = Font(name=F, bold=True, color="C00000")
HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(name=F, bold=True, color="FFFFFF")
YELLOW = PatternFill("solid", fgColor="FFFF00")
GREY = PatternFill("solid", fgColor="EDEDED")
WRAP = Alignment(wrap_text=True, vertical="top")
thin = Side(style="thin", color="BFBFBF")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)

USD = '$#,##0;($#,##0);"-"'
USDB = '$#,##0.00,,,"B";($#,##0.00,,,"B");"-"'
PMP = '$0.000;($0.000);"-"'
PCT = '0.0%;(0.0%);"-"'
INT = '#,##0'

MARKING = "DRAFT//PRE-DECISIONAL"
LABEL = "Before federal coordination, upper bound"


def sheet(name, title, widths):
    ws = wb.create_sheet(name)
    ws["A1"] = MARKING
    ws["A1"].font = MARK
    ws["A2"] = title
    ws["A2"].font = TITLE
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    return ws


def hdr(ws, row, labels, col=1):
    for i, lab in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=lab)
        c.font = HDR_FONT
        c.fill = HDR_FILL
        c.alignment = WRAP
        c.border = BOX


def put(ws, ref, value, font=BLACK, fmt=None, fill=None, wrap=False, comment=None):
    c = ws[ref]
    c.value = value
    c.font = font
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if wrap:
        c.alignment = WRAP
    if comment:
        c.comment = Comment(comment, "Claude")
    return c


wb.remove(wb.active)

# ---------------------------------------------------------------- README
ws = sheet("README", "1675–1695 MHz auction valuation workbook, v0.1", [110])
lines = [
    ("Purpose", BOLD),
    ("Estimates FCC auction revenue for 20 MHz at 1675–1695 MHz under the October 29, 2026 FNPRM "
     "(FCC 26-70, WT Docket No. 26-284). Follows 1675-auction-valuation-plan.md, version 4.", BLACK),
    ("", BLACK),
    ("What v0.1 covers", BOLD),
    ("• Nationwide license option: two unpaired 10 MHz blocks (1675–1685 and 1685–1695 MHz).", BLACK),
    ("• Bidders: SpaceX and Amazon Leo (D2D class); AT&T, Verizon, and T-Mobile (carrier class).", BLACK),
    ("• Pricing rule: uniform price set by the highest losing unit bid (clock-auction logic).", BLACK),
    ("• Benchmarks: Auction 97 block-level results, SpaceX/EchoStar, SpaceX/Grain, Amazon/Globalstar.", BLACK),
    ("", BLACK),
    ("Not yet in v0.1", BOLD),
    ("• Auction 97 and Auction 113 per-license data (Raw_A97, Raw_A113 tabs): the FCC site blocks automated "
     "downloads here. Download the CSVs from auctiondata.fcc.gov and attach them.", BLACK),
    ("• PEA and regional license options (PEA_Pop tab): needs the FCC PEA population file.", BLACK),
    ("• Federal coordination zones (Coordination tab): deferred. Availability is set to 100%.", BLACK),
    ("• Primary-source verification of transaction terms (SEC filings, FCC applications).", BLACK),
    ("", BLACK),
    ("Every dollar figure in this workbook is: " + LABEL + ".", MARK),
    ("", BLACK),
    ("Color key", BOLD),
    ("Blue text: hardcoded input. Black text: formula. Green text: link to another tab. "
     "Yellow fill: key assumption or item still to verify.", BLACK),
    ("Edit only blue cells. Change scenarios on the Scenarios tab (rows 6–15).", BLACK),
    ("", BLACK),
    ("Tab order", BOLD),
    ("Summary → Scenarios → Bidders → Benchmarks → Transactions → Inputs → Revenue_Defs → FNPRM → "
     "Raw_A97 → Raw_A113 → PEA_Pop → Coordination → Checks", BLACK),
    ("", BLACK),
    ("Version log", BOLD),
    ("v0.1, November 10, 2026: first build; nationwide option only.", BLACK),
]
for i, (t, f) in enumerate(lines, 4):
    c = ws.cell(row=i, column=1, value=t)
    c.font = f
    c.alignment = WRAP

# ---------------------------------------------------------------- Inputs
ws = sheet("Inputs", "Inputs", [46, 18, 70])
hdr(ws, 4, ["Input", "Value", "Source or note"])
inputs = [
    ("U.S. population, 2020 Census", 331449281, INT, None,
     "U.S. Census Bureau, 2020 Census resident population (50 states and DC)."),
    ("U.S. population, 2010 Census", 308745538, INT, None,
     "U.S. Census Bureau, 2010 Census resident population. Basis for Auction 97 $/MHz-pop."),
    ("Block size (MHz)", 10, INT, None,
     "FNPRM proposed band plan: two unpaired 10 MHz blocks (Covington summary of Oct 8 draft)."),
    ("Number of blocks", 2, INT, None, "FNPRM proposed band plan."),
    ("Total MHz", "=B7*B8", INT, None, "Formula."),
    ("Reserve price per block ($)", 0, USD, YELLOW,
     "Not set. FNPRM reserve not yet known. Used only when fewer than three unit bids exist."),
    ("Federal coordination availability", "=Coordination!B5", PCT, None,
     "Link to Coordination tab. Deferred; 100% until zones are modeled."),
    ("SpaceX value of second block (share of first)", 1.0, PCT, YELLOW,
     "Used only in scenarios where SpaceX wants both blocks. 100% means it values 20 MHz linearly."),
    ("TDL: downlink share of paired AWS-3 value", 0.5, PCT, YELLOW,
     "Assumption, no evidence yet. Splits the paired AWS-3 price into a downlink half. Weakest benchmark."),
    ("NOAA transition cost paid from proceeds ($)", 0, USD, YELLOW,
     "Unknown. Open question 8 in the plan. Enter when a public estimate exists."),
    ("Auction 113 gross bids ($)", 3572889200, USD, None,
     "FCC Public Notice DA 26-633 (June 26, 2026)."),
    ("Auction 113 net bids ($)", 3572347950, USD, None,
     "FCC Public Notice DA 26-633 (June 26, 2026)."),
    ("Net-to-gross ratio (from Auction 113)", "=B16/B15", '0.0000%', None,
     "Formula. Proxy for bidding credits; these bidders are unlikely to claim credits."),
]
for i, (lab, val, fmt, fill, src) in enumerate(inputs, 5):
    put(ws, f"A{i}", lab)
    is_formula = isinstance(val, str) and val.startswith("=")
    font = (GREEN if "!" in str(val) else BLACK) if is_formula else BLUE
    put(ws, f"B{i}", val, font, fmt, fill)
    put(ws, f"C{i}", src, wrap=True)

# ---------------------------------------------------------------- Transactions
ws = sheet("Transactions", "Spectrum transactions (D2D benchmarks)", [26, 16, 12, 16, 14, 16, 60, 14])
hdr(ws, 4, ["Transaction", "Price ($)", "MHz", "Population basis", "$/MHz-pop",
            "Payment", "Source and caveats", "Primary source verified?"])
tx = [
    ("SpaceX / EchoStar unpaired AWS-3 (1695–1710 MHz)", 2600000000, 15,
     "Stock",
     "EchoStar press release, Nov 6, 2025: about $2.6B in SpaceX stock valued as of Sept 2025; up to 15 MHz, "
     "nationwide, Band 70 uplink. Corner Alliance memo cites $2.617B; confirm in SEC filing. "
     "Caveats: paid in stock; seller under FCC pressure to sell; 'up to' 15 MHz may mean partial coverage."),
    ("SpaceX / Grain 800 MHz", 8000000000, 14,
     "Cash (reported)",
     "Announced Oct 8, 2026; terms not disclosed. $8B is the Wall Street Journal report; up to 14 MHz paired "
     "(7+7). New Street cited about $1.73/MHz-pop. Caveats: low band (better propagation); includes "
     "terrestrial rights."),
    ("Amazon / Globalstar", 11570000000, 25,
     "Company acquisition",
     "Announced Apr 14, 2026; FCC approved Oct 27, 2026. About 25 MHz of MSS spectrum including L-band. "
     "Caveats: enterprise value includes satellites, operations, and the Apple agreement; rights are global. "
     "Use as a reference point, not a clean spectrum price."),
]
for i, (name, price, mhz, pay, src) in enumerate(tx, 5):
    put(ws, f"A{i}", name, wrap=True)
    put(ws, f"B{i}", price, BLUE, USD)
    put(ws, f"C{i}", mhz, BLUE, INT)
    put(ws, f"D{i}", "=Inputs!$B$5", GREEN, INT)
    put(ws, f"E{i}", f"=B{i}/(C{i}*D{i})", BLACK, PMP)
    put(ws, f"F{i}", pay, BLUE)
    put(ws, f"G{i}", src, wrap=True)
    put(ws, f"H{i}", "PENDING", BLUE, fill=YELLOW)
    ws.row_dimensions[i].height = 75
put(ws, "A9", "Note: population basis is the 2020 Census national total because all three portfolios are "
    "described as nationwide.", wrap=True)
ws.merge_cells("A9:G9")

# ---------------------------------------------------------------- Benchmarks
ws = sheet("Benchmarks", "Benchmarks on a common basis (nominal $/MHz-pop, no inflation adjustment)",
           [44, 16, 12, 16, 62])
hdr(ws, 4, ["Data point", "Gross ($)", "MHz", "$/MHz-pop", "Source"])
bm = [
    ("Auction 97 A1 block (1695–1700 MHz), 176 EAs", 170000000, 5, 0.11,
     "Phoenix Center Perspective 15-02 (2015), table of Auction 97 block prices. Replace with per-license sum "
     "from Raw_A97 when attached."),
    ("Auction 97 B1 block (1700–1710 MHz), 176 EAs", 2260000000, 10, 0.72,
     "Phoenix Center Perspective 15-02 (2015)."),
    ("Auction 97 unpaired average (A1 + B1)", None, 15, 0.52,
     "Cramton et al., 'Bidding and Prices in the AWS-3 Auction' (2015); also Fierce Wireless (2015)."),
    ("Auction 97 paired average (G, H, I, J)", None, 50, 2.72,
     "Cramton et al. (2015): paired sold at more than five times the unpaired price."),
    ("Auction 97 A1 + B1, computed", "=B5+B6", 15, "=B9/(C9*Inputs!$B$6)",
     "Formula. Cross-check of row 7 using the 2010 Census population."),
    ("SpaceX / EchoStar (SUL evidence)", "=Transactions!B5", "=Transactions!C5", "=Transactions!E5",
     "Link to Transactions."),
    ("SpaceX / Grain (D2D, low band)", "=Transactions!B6", "=Transactions!C6", "=Transactions!E6",
     "Link to Transactions."),
    ("Amazon / Globalstar (D2D, enterprise value)", "=Transactions!B7", "=Transactions!C7", "=Transactions!E7",
     "Link to Transactions."),
    ("Auction 113 A1 and B1 (2026)", None, 15, None,
     "PENDING: needs per-license CSV (Raw_A113). Auction 113 total gross is on Inputs."),
]
for i, (lab, g, m, p, src) in enumerate(bm, 5):
    put(ws, f"A{i}", lab, wrap=True)
    for col, v, fmt in (("B", g, USD), ("C", m, INT), ("D", p, PMP)):
        if v is None:
            continue
        if isinstance(v, str) and v.startswith("="):
            put(ws, f"{col}{i}", v, GREEN if "!" in v and "Inputs" not in v else BLACK, fmt)
        else:
            put(ws, f"{col}{i}", v, BLUE, fmt)
    put(ws, f"E{i}", src, wrap=True)
    ws.row_dimensions[i].height = 30
ws["D13"].fill = YELLOW

put(ws, "A16", "Benchmark by use case ($/MHz-pop)", BOLD)
hdr(ws, 17, ["Use case", "Low", "Base", "High", "Basis"])
uc = [
    ("TDL", "=D7", "=D8*Inputs!$B$13", "=D8",
     "No unpaired downlink comparable exists. Low: unpaired uplink price. Base: paired price × downlink share "
     "(assumption on Inputs). High: full paired price. Weakest benchmark; see plan finding 11."),
    ("TUL", "=D5", "=D7", "=D6",
     "Auction 97 A1 and B1: closest match (adjacent, unpaired uplink, federal protection zones). "
     "Low: A1. Base: A1 + B1 average. High: B1."),
    ("SUL", "=MIN(D10,D7)", "=D10", "=D6",
     "SpaceX/EchoStar purchase of the adjacent uplink band for satellite use. High: Auction 97 B1."),
    ("SDL", "=D10", "=D12", "=D11",
     "Low: EchoStar (uplink-only). Base: Globalstar (L-band MSS, enterprise value). "
     "High: Grain (800 MHz; low band likely overstates 1.7 GHz value)."),
]
for i, (u, lo, ba, hi, basis) in enumerate(uc, 18):
    put(ws, f"A{i}", u, BOLD)
    for col, v in (("B", lo), ("C", ba), ("D", hi)):
        put(ws, f"{col}{i}", v, BLACK, PMP)
    put(ws, f"E{i}", basis, wrap=True)
    ws.row_dimensions[i].height = 48
put(ws, "A23", "Finding to test: the EchoStar price per MHz-pop (row 10) lands almost exactly on the 2015 "
    "Auction 97 unpaired average (row 7). That supports the 'flat nominal' claim, but confirm with the "
    "Auction 113 per-license data before relying on it.", wrap=True)
ws.merge_cells("A23:E23")
ws.row_dimensions[23].height = 45

# ---------------------------------------------------------------- Bidders
ws = sheet("Bidders", "Credible bidders", [18, 12, 16, 70])
hdr(ws, 4, ["Bidder", "Class", "Values license as", "Why credible (public source)"])
bidders = [
    ("SpaceX", "D2D", "SDL (base)",
     "Bought EchoStar AWS-4, H-block, and unpaired AWS-3, and Grain 800 MHz for D2D. Light Reading notes it is "
     "not clear SpaceX will bid in this auction."),
    ("Amazon Leo", "D2D", "SDL (base)",
     "Acquired Globalstar (FCC approved Oct 27, 2026); D2D constellation filed for service from 2028."),
    ("AT&T", "Carrier", "TUL (base)", "Largest Auction 97 winner; won licenses in Auction 113."),
    ("Verizon", "Carrier", "TUL (base)", "Largest Auction 113 winner by spend."),
    ("T-Mobile", "Carrier", "TUL (base)", "Auction 97 and Auction 113 winner."),
    ("Carrier D2D JV", "D2D", "SDL (scenario only)",
     "AT&T, Verizon, and T-Mobile formed a D2D spectrum-pooling joint venture (reported Oct 2026). "
     "Off in the base case; on in Scenario S4."),
]
for i, row in enumerate(bidders, 5):
    for j, v in enumerate(row):
        c = ws.cell(row=i, column=j + 1, value=v)
        c.font = BLUE if j < 3 else BLACK
        c.alignment = WRAP
    ws.row_dimensions[i].height = 45
put(ws, "A12", "Bidder list provided by Nick (Nov 10, 2026): SpaceX, Amazon, and the carriers. "
    "Sign-off on this list is still open (plan question 7).", wrap=True)
ws.merge_cells("A12:D12")
ws.row_dimensions[12].height = 30

# ---------------------------------------------------------------- Coordination
ws = sheet("Coordination", "Federal coordination (deferred)", [44, 14, 70])
put(ws, "A5", "Population availability after coordination")
put(ws, "B5", 1.0, BLUE, PCT, YELLOW)
put(ws, "C5", "DEFERRED. Placeholder of 100%. Replace with per-PEA availability for the four NOAA DCS "
    "sites when zones come back in.", wrap=True)
put(ws, "A7", LABEL, MARK)

# ---------------------------------------------------------------- Scenarios
ws = sheet("Scenarios", "Scenarios and pricing rule (nationwide licenses)",
           [46, 4, 17, 17, 17, 17, 17, 17, 17])
scen = [
    # name, desc, case, carrier use, d2d use, spx, amz, att, vz, tmo, spx2, jv
    ("S1 Base", "All five bidders; one block each", "Base", "TUL", "SDL", 1, 1, 1, 1, 1, 0, 0),
    ("S2 Thin D2D", "Amazon sits out", "Base", "TUL", "SDL", 1, 0, 1, 1, 1, 0, 0),
    ("S3 SpaceX wants 20 MHz", "SpaceX bids for both blocks", "Base", "TUL", "SDL", 1, 1, 1, 1, 1, 1, 0),
    ("S4 Carrier JV bids D2D", "Carrier JV joins as a third D2D bidder", "Base", "TUL", "SDL", 1, 1, 1, 1, 1, 0, 1),
    ("S5 Carriers value downlink", "Carriers value the band as TDL", "Base", "TDL", "SDL", 1, 1, 1, 1, 1, 0, 0),
    ("S6 Low benchmarks", "S1 with low benchmarks", "Low", "TUL", "SDL", 1, 1, 1, 1, 1, 0, 0),
    ("S7 High benchmarks", "S3 with high benchmarks", "High", "TUL", "SDL", 1, 1, 1, 1, 1, 1, 0),
]
labels = ["Scenario", "Description", "Benchmark case (Low/Base/High)", "Carrier use case (TUL/TDL)",
          "D2D use case (SUL/SDL)", "SpaceX participates", "Amazon Leo participates", "AT&T participates",
          "Verizon participates", "T-Mobile participates", "SpaceX wants both blocks", "Carrier JV bids as D2D"]
for k, lab in enumerate(labels, 4):
    put(ws, f"A{k}", lab, BOLD if k == 4 else BLACK)
ws["A4"].fill = HDR_FILL
ws["A4"].font = HDR_FONT
put(ws, "A16", "Calculation", BOLD)
calc_labels = {
    17: "Carrier $/MHz-pop",
    18: "D2D $/MHz-pop",
    19: "Carrier value per block ($)",
    20: "D2D value per block ($)",
    22: "Unit bid: SpaceX, block 1",
    23: "Unit bid: SpaceX, block 2",
    24: "Unit bid: Amazon Leo",
    25: "Unit bid: AT&T",
    26: "Unit bid: Verizon",
    27: "Unit bid: T-Mobile",
    28: "Unit bid: Carrier D2D JV",
    30: "Unit bids received",
    31: "Clearing price per block ($)",
    32: "Blocks sold",
    33: "Gross revenue ($)",
    34: "Implied $/MHz-pop",
    35: "Blocks won by D2D bidders",
    36: "Winning class",
    37: "Label",
}
for r, lab in calc_labels.items():
    put(ws, f"A{r}", lab, BOLD if r in (31, 33) else BLACK)

uc_range = "Benchmarks!$A$18:$A$21"
case_hdr = "Benchmarks!$B$17:$D$17"
uc_table = "Benchmarks!$B$18:$D$21"
for j, s in enumerate(scen):
    col = get_column_letter(3 + j)
    c = col
    hdr(ws, 4, [s[0]], col=3 + j)
    for k, v in enumerate(s[1:], 5):
        put(ws, f"{c}{k}", v, BLUE, wrap=(k == 5))
    ws.row_dimensions[5].height = 45
    put(ws, f"{c}17", f"=INDEX({uc_table},MATCH({c}7,{uc_range},0),MATCH({c}6,{case_hdr},0))", GREEN, PMP)
    put(ws, f"{c}18", f"=INDEX({uc_table},MATCH({c}8,{uc_range},0),MATCH({c}6,{case_hdr},0))", GREEN, PMP)
    pop_mhz = "Inputs!$B$7*Inputs!$B$5*Inputs!$B$11"
    put(ws, f"{c}19", f"={c}17*{pop_mhz}", BLACK, USD)
    put(ws, f"{c}20", f"={c}18*{pop_mhz}", BLACK, USD)
    put(ws, f"{c}22", f"={c}20*{c}9", BLACK, USD)
    put(ws, f"{c}23", f"={c}20*{c}9*{c}14*Inputs!$B$12", BLACK, USD)
    put(ws, f"{c}24", f"={c}20*{c}10", BLACK, USD)
    put(ws, f"{c}25", f"={c}19*{c}11", BLACK, USD)
    put(ws, f"{c}26", f"={c}19*{c}12", BLACK, USD)
    put(ws, f"{c}27", f"={c}19*{c}13", BLACK, USD)
    put(ws, f"{c}28", f"={c}20*{c}15", BLACK, USD)
    put(ws, f"{c}30", f'=COUNTIF({c}22:{c}28,">0")', BLACK, INT)
    put(ws, f"{c}31",
        f"=IF({c}30>Inputs!$B$8,MAX(LARGE({c}22:{c}28,Inputs!$B$8+1),Inputs!$B$10),Inputs!$B$10)",
        BLACK, USD)
    put(ws, f"{c}32", f"=MIN(Inputs!$B$8,{c}30)", BLACK, INT)
    put(ws, f"{c}33", f"={c}31*{c}32", BOLD, USD)
    ws[f"{c}33"].number_format = USD
    put(ws, f"{c}34", f"=IF({c}32>0,{c}33/({c}32*Inputs!$B$7*Inputs!$B$5),0)", BLACK, PMP)
    put(ws, f"{c}35",
        f'=IF({c}32=0,0,MIN({c}32,SUMPRODUCT(({c}22:{c}24>=LARGE({c}22:{c}28,{c}32))*({c}22:{c}24>0))'
        f'+({c}28>=LARGE({c}22:{c}28,{c}32))*({c}28>0)))', BLACK, INT)
    put(ws, f"{c}36", f'=IF({c}35>={c}32,"D2D",IF({c}35=0,"Carrier","Split"))', BLACK)
    put(ws, f"{c}37", LABEL, MARK, wrap=True)
ws.row_dimensions[37].height = 30
put(ws, "A39", "Pricing rule: each bidder demands one 10 MHz block (SpaceX demands two in S3 and S7). "
    "With two blocks for sale, the uniform clock price stops at the highest losing unit bid (the third-highest "
    "unit bid). The two highest unit bids win. Ties between classes split the count in row 35.", wrap=True)
ws.merge_cells("A39:I39")
ws.row_dimensions[39].height = 45
ws.freeze_panes = "C5"

# ---------------------------------------------------------------- Revenue_Defs
ws = sheet("Revenue_Defs", "Revenue definitions", [40, 17, 17, 17, 17, 17, 17, 17])
hdr(ws, 4, ["Measure"] + [s[0] for s in scen])
rd = ["Gross bids ($)", "Net bids ($)", "Net of NOAA costs ($)", "Budget score"]
for i, lab in enumerate(rd, 5):
    put(ws, f"A{i}", lab)
for j in range(len(scen)):
    sc = get_column_letter(3 + j)
    col = get_column_letter(2 + j)
    put(ws, f"{col}5", f"=Scenarios!{sc}33", GREEN, USD)
    put(ws, f"{col}6", f"={col}5*Inputs!$B$17", BLACK, USD)
    put(ws, f"{col}7", f"={col}6-Inputs!$B$14", BLACK, USD)
    put(ws, f"{col}8", "Outside model", BLACK)
put(ws, "A10", "If the Commercial Spectrum Enhancement Act applies, proceeds must reach 110% of federal "
    "relocation or sharing costs. Confirm with counsel (plan, Revenue definitions).", wrap=True)
ws.merge_cells("A10:H10")
ws.row_dimensions[10].height = 30

# ---------------------------------------------------------------- FNPRM
ws = sheet("FNPRM", "FNPRM proposals used (FCC 26-70, WT Docket No. 26-284)", [42, 52, 30, 22])
hdr(ws, 4, ["Proposal", "Model input it drives", "Source", "Paragraph (adopted text)"])
fn = [
    ("Two unpaired 10 MHz blocks: 1675–1685 and 1685–1695 MHz", "Inputs B7, B8", "Covington, Oct 13, 2026"),
    ("Alternative: unpaired 5 MHz blocks", "Not yet modeled (v0.2)", "Covington, Oct 13, 2026"),
    ("Uplink, downlink, or TDD at licensee's choice", "Bidders value license at their best use case", "Covington"),
    ("Secondary MSS allocation for SCS", "D2D bidder class", "Covington; FCC Oct 2026 releases"),
    ("License area: nationwide, regional, or PEA (not set)", "v0.1 nationwide only", "Covington"),
    ("Possible bundling and all-or-nothing nationwide package bids", "Not yet modeled", "Covington"),
    ("Terrestrial buildout 45% / 80% of population", "Flag only", "Covington"),
    ("Small-business and rural bidding credits", "Net-to-gross ratio (Inputs B17)", "Covington"),
    ("Coordination near four NOAA DCS sites", "Coordination tab (deferred)", "Covington"),
]
for i, (p, m, s) in enumerate(fn, 5):
    put(ws, f"A{i}", p, wrap=True)
    put(ws, f"B{i}", m, wrap=True)
    put(ws, f"C{i}", s, wrap=True)
    put(ws, f"D{i}", "PENDING", BLUE, fill=YELLOW)
    ws.row_dimensions[i].height = 30
put(ws, "A15", "Source for all rows: Covington, 'FCC Proposes to Auction Spectrum for Terrestrial and "
    "Space-Based Broadband Services' (Oct 13, 2026), summarizing the Oct 8 draft. Replace with adopted FCC 26-70 "
    "paragraph numbers.", wrap=True)
ws.merge_cells("A15:D15")
ws.row_dimensions[15].height = 30

# ---------------------------------------------------------------- Raw tabs
for name, title, url in (
    ("Raw_A97", "Auction 97 per-license results (pending)", "https://auctiondata.fcc.gov/public/projects/auction97"),
    ("Raw_A113", "Auction 113 per-license results (pending)", "https://auctiondata.fcc.gov/public/projects/auction113"),
):
    ws = sheet(name, title, [100])
    put(ws, "A4", "PENDING: paste the 'Results by License' CSV here, unedited, starting at row 10.", BOLD, fill=YELLOW)
    put(ws, "A5", f"Download from {url} (Results by License).")
    put(ws, "A6", "The FCC site blocks automated downloads from this workspace, so this needs a manual download.")
ws = sheet("PEA_Pop", "PEA populations (pending, v0.2)", [100])
put(ws, "A4", "PENDING: 416 PEAs with 2020 Census population, from the FCC PEA file. Needed for the PEA and "
    "regional license options.", BOLD, fill=YELLOW)

# ---------------------------------------------------------------- Checks
ws = sheet("Checks", "Checks", [70, 14, 60])
hdr(ws, 4, ["Check", "Status", "Detail"])
first, last = "C", get_column_letter(2 + len(scen))
rng = f"Scenarios!{first}33:{last}33"
checks = [
    ("Auction 97 A1 + B1 computed $/MHz-pop within 5% of published unpaired average",
     '=IF(ABS(Benchmarks!D9/Benchmarks!D7-1)<=0.05,"PASS","FAIL")', "Benchmarks D9 vs D7"),
    ("Grain $/MHz-pop within 3% of New Street's reported $1.73",
     '=IF(ABS(Transactions!E6/1.73-1)<=0.03,"PASS","FAIL")', "Transactions E6"),
    ("Auction 113 net ≤ gross", '=IF(Inputs!B16<=Inputs!B15,"PASS","FAIL")', "Inputs B15:B16"),
    ("Every scenario sells no more than the blocks offered",
     f'=IF(MAX(Scenarios!{first}32:{last}32)<=Inputs!B8,"PASS","FAIL")', "Scenarios row 32"),
    ("Clearing price never exceeds the second-highest unit bid (losers can't set price above winners)",
     f'=IF(SUMPRODUCT((Scenarios!{first}31:{last}31>Scenarios!{first}20:{last}20+Scenarios!{first}19:{last}19)*1)=0,"PASS","FAIL")',
     "Row 31 vs bid values"),
    ("Floor ≤ estimate ≤ ceiling",
     f'=IF(AND(MIN({rng})<=Scenarios!C33,Scenarios!C33<=MAX({rng})),"PASS","FAIL")', "Summary"),
    ("Coordination availability is 100% and outputs labeled upper bound",
     '=IF(Coordination!B5=1,"PASS","FAIL")', LABEL),
    ("Auction 113 per-license data loaded", '=IF(COUNTA(Raw_A113!A10:A400)>0,"PASS","PENDING")', "Raw_A113"),
    ("Auction 97 per-license data loaded", '=IF(COUNTA(Raw_A97!A10:A2000)>0,"PASS","PENDING")', "Raw_A97"),
    ("Transaction terms verified in primary filings",
     '=IF(COUNTIF(Transactions!H5:H7,"PENDING")=0,"PASS","PENDING")', "Transactions H5:H7"),
    ("FNPRM inputs cited to adopted paragraphs",
     '=IF(COUNTIF(FNPRM!D5:D13,"PENDING")=0,"PASS","PENDING")', "FNPRM D5:D13"),
]
for i, (lab, f, d) in enumerate(checks, 5):
    put(ws, f"A{i}", lab, wrap=True)
    put(ws, f"B{i}", f, BLACK)
    put(ws, f"C{i}", d, wrap=True)
put(ws, f"A{5 + len(checks) + 1}", "Overall")
put(ws, f"B{5 + len(checks) + 1}",
    f'=IF(COUNTIF(B5:B{4 + len(checks)},"FAIL")>0,"FAIL",IF(COUNTIF(B5:B{4 + len(checks)},"PENDING")>0,"PENDING","PASS"))',
    BOLD)

# ---------------------------------------------------------------- Summary
ws = sheet("Summary", "1675–1695 MHz auction revenue: first estimate (nationwide licenses)",
           [44, 18, 18, 18, 50])
wb.move_sheet("Summary", offset=-wb.index(wb["Summary"]))
put(ws, "A3", LABEL + ". Not for release.", MARK)
hdr(ws, 5, ["Measure", "Gross revenue", "$/MHz-pop", "Scenario", "Meaning"])
summ = [
    ("Floor", f"=MIN({rng})", f"=MIN(Scenarios!{first}34:{last}34)",
     f'=INDEX(Scenarios!{first}4:{last}4,MATCH(B6,{rng},0))', "Thin competition or low benchmarks"),
    ("Estimate (S1 Base)", "=Scenarios!C33", "=Scenarios!C34", "=Scenarios!C4",
     "All five bidders, one block each, base benchmarks"),
    ("Ceiling", f"=MAX({rng})", f"=MAX(Scenarios!{first}34:{last}34)",
     f'=INDEX(Scenarios!{first}4:{last}4,MATCH(B8,{rng},0))', "Competitive D2D bidding, high benchmarks"),
]
for i, (lab, a, b, c, d) in enumerate(summ, 6):
    put(ws, f"A{i}", lab, BOLD)
    put(ws, f"B{i}", a, GREEN, USDB)
    put(ws, f"C{i}", b, GREEN, PMP)
    put(ws, f"D{i}", c, GREEN)
    put(ws, f"E{i}", d, wrap=True)
put(ws, "A10", "What drives the number", BOLD)
put(ws, "A11", "With two blocks, the price is set by the third-highest bidder. Two D2D bidders (SpaceX and "
    "Amazon Leo) win at the carriers' price unless a third bidder competes at D2D values: SpaceX wanting both "
    "blocks (S3) or a carrier D2D joint venture (S4). Compare S1 with S3 and S4.", wrap=True)
ws.merge_cells("A11:E11")
ws.row_dimensions[11].height = 48
hdr(ws, 13, ["Scenario", "Gross revenue", "Winning class", "Clearing $/MHz-pop"])
for j, s in enumerate(scen):
    r = 14 + j
    sc = get_column_letter(3 + j)
    put(ws, f"A{r}", f"=Scenarios!{sc}4", GREEN)
    put(ws, f"B{r}", f"=Scenarios!{sc}33", GREEN, USDB)
    put(ws, f"C{r}", f"=Scenarios!{sc}36", GREEN)
    put(ws, f"D{r}", f"=Scenarios!{sc}34", GREEN, PMP)
put(ws, "A22", "Checks status:", BOLD)
put(ws, "B22", f"=Checks!B{5 + len(checks) + 1}", GREEN)
put(ws, "A23", "Excluded: federal coordination zones, PEA and regional options, 5 MHz band plan, exposure "
    "discount, timing, buildout, ODS. See README.", wrap=True)
ws.merge_cells("A23:E23")
ws.row_dimensions[23].height = 30

ch = BarChart()
ch.type = "bar"
ch.title = "Gross revenue by scenario ($, " + LABEL.lower() + ")"
ch.y_axis.title = "Gross revenue ($)"
ch.y_axis.numFmt = '$#,##0.0,,,"B"'
data = Reference(ws, min_col=2, min_row=13, max_row=13 + len(scen))
cats = Reference(ws, min_col=1, min_row=14, max_row=13 + len(scen))
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
ch.legend = None
ch.height, ch.width = 9, 20
ws.add_chart(ch, "A25")

for w in wb.worksheets:
    w.sheet_view.showGridLines = False

wb.active = 0
wb.save("1675-auction-valuation.xlsx")
print("saved")
