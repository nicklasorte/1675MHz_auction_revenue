"""Build 1675-1695 MHz auction valuation workbook, v0.2.

Usage: python build_1675_workbook_v02.py <data_dir> <out.xlsx>
data_dir holds a97_licenses.csv and a113_licenses.csv from parse_auctions.py.
"""
import csv
import math
import random
import statistics as st
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

DATA, OUT = Path(sys.argv[1]), sys.argv[2]
A97 = list(csv.DictReader(open(DATA / "a97_licenses.csv")))
A113 = list(csv.DictReader(open(DATA / "a113_licenses.csv")))

F = "Arial"
BLUE, BLACK, GREEN = Font(name=F, color="0000FF"), Font(name=F), Font(name=F, color="008000")
BOLD, TITLE = Font(name=F, bold=True), Font(name=F, bold=True, size=14)
MARK = Font(name=F, bold=True, color="C00000")
HDR_FILL, HDR_FONT = PatternFill("solid", fgColor="1F3864"), Font(name=F, bold=True, color="FFFFFF")
YELLOW = PatternFill("solid", fgColor="FFFF00")
GREY = PatternFill("solid", fgColor="E7E6E6")
WRAP = Alignment(wrap_text=True, vertical="top")
thin = Side(style="thin", color="BFBFBF")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
USD = '$#,##0;($#,##0);"-"'
USDB = '$#,##0.00,,,"B";($#,##0.00,,,"B");"-"'
PMP = '$0.000;($0.000);"-"'
PCT = '0.0%;(0.0%);"-"'
INT = '#,##0'
RAT = '0.000'
MARKING = "DRAFT//PRE-DECISIONAL"
LABEL = "Before federal coordination, upper bound"

wb = Workbook()
wb.remove(wb.active)


def sheet(name, title, widths):
    ws = wb.create_sheet(name)
    ws["A1"], ws["A1"].font = MARKING, MARK
    ws["A2"], ws["A2"].font = title, TITLE
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.sheet_view.showGridLines = False
    return ws


def hdr(ws, row, labels, col=1):
    for i, lab in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=lab)
        c.font, c.fill, c.alignment, c.border = HDR_FONT, HDR_FILL, WRAP, BOX


def put(ws, ref, value, font=None, fmt=None, fill=None, wrap=False):
    c = ws[ref]
    c.value = value
    if font is None:
        if isinstance(value, str) and value.startswith("="):
            font = GREEN if "!" in value else BLACK
        elif isinstance(value, (int, float)):
            font = BLUE
        else:
            font = BLACK
    c.font = font
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if wrap:
        c.alignment = WRAP
    return c


def note(ws, ref, text, span, height=30):
    put(ws, ref, text, BLACK, wrap=True)
    ws.merge_cells(f"{ref}:{span}")
    ws.row_dimensions[ws[ref].row].height = height


# ======================================================== Inputs
ws = sheet("Inputs", "Inputs", [52, 20, 80])
hdr(ws, 4, ["Input", "Value", "Source or note"])
INP = {}
inputs = [
    ("pop", "U.S. population, 2020 Census", 331449281, INT, None,
     "U.S. Census Bureau, 2020 Census resident population (50 states and DC)."),
    ("mhz", "Block size (MHz)", 10, INT, None, "FNPRM proposal: two unpaired 10 MHz blocks (Covington summary)."),
    ("blocks", "Number of blocks", 2, INT, None, "FNPRM proposal."),
    ("reserve", "Reserve price per block ($)", 0, USD, YELLOW,
     "Not known. Used only when fewer unit bids than blocks plus one."),
    ("avail", "Federal coordination availability", "=Coordination!B5", PCT, None,
     "Deferred; 100% until zones are modeled."),
    ("spx2", "SpaceX value of a second block (share of first)", 1.0, PCT, YELLOW,
     "Used only when SpaceX wants both blocks. Demand reduction then decides whether it bids for two."),
    ("dlshare", "TDL: downlink share of paired AWS-3 value", 0.5, PCT, YELLOW,
     "Assumption with no evidence. Feeds the TDL high case only. TDL scenarios are suspended."),
    ("noaa", "NOAA transition cost paid from proceeds ($)", 0, USD, YELLOW, "Unknown. Enter when public."),
    ("pub97net", "Auction 97 net bids, published ($)", 41329673325, USD, None,
     "FCC Public Notice DA 15-131 (Jan 30, 2015), para. 1."),
    ("pub97n", "Auction 97 licenses won, published", 1611, INT, None, "FCC Public Notice DA 15-131."),
    ("pub97gross", "Auction 97 gross bids, published (rounded, $)", 44900000000, USD, None,
     "Widely reported as $44.9 billion gross (for example, Cramton et al. 2015)."),
    ("pub113gross", "Auction 113 gross bids, published ($)", 3572889200, USD, None,
     "FCC Public Notice DA 26-633 (June 26, 2026)."),
    ("pub113net", "Auction 113 net bids, published ($)", 3572347950, USD, None,
     "FCC Public Notice DA 26-633, Attachment A (sum of bidder net payments)."),
    ("pub113n", "Auction 113 licenses won, published", 200, INT, None, "FCC Public Notice DA 26-633."),
    ("cramU", "Published Auction 97 unpaired $/MHz-pop", 0.52, PMP, None,
     "Cramton et al., 'Bidding and Prices in the AWS-3 Auction' (2015). Independent cross-check."),
    ("cramP", "Published Auction 97 paired $/MHz-pop", 2.72, PMP, None, "Cramton et al. (2015)."),
    ("net2gross", "Net-to-gross ratio (Auction 113)", "=B17/B16", '0.0000%', None, "Formula."),
]
for i, (key, lab, val, fmt, fill, src) in enumerate(inputs, 5):
    put(ws, f"A{i}", lab)
    put(ws, f"B{i}", val, fmt=fmt, fill=fill)
    put(ws, f"C{i}", src, wrap=True)
    INP[key] = f"Inputs!$B${i}"

# ======================================================== Coordination
ws = sheet("Coordination", "Federal coordination (deferred)", [44, 14, 80])
put(ws, "A5", "Population availability after coordination")
put(ws, "B5", 1.0, fmt=PCT, fill=YELLOW)
put(ws, "C5", "DEFERRED. Placeholder of 100%. When zones return, model them as declining over time "
    "(weather broadcast use is expected to fall after GOES-R retires, around 2033).", wrap=True)
put(ws, "A7", LABEL, MARK)

# ======================================================== Raw_A97
n97 = len(A97)
r0, r1 = 5, 5 + n97 - 1
ws = sheet("Raw_A97", "Auction 97 per-license results (FCC DA 15-131 Attachment A; DA 14-1018 Attachment A)",
           [16, 9, 30, 6, 18, 6, 13, 6, 34, 12, 16, 16, 11, 15, 11, 10])
put(ws, "A3", "Source: winning bids from FCC Public Notice DA 15-131 Attachment A; 2010 population and MHz from "
    "DA 14-1018 Attachment A. Parsed with parse_auctions.py. Blue = raw data; black = formula.")
hdr(ws, 4, ["License", "Market", "Market name", "Block", "Frequencies", "MHz", "Population (2010)", "Sold",
            "Winning bidder", "FRN", "Gross bid ($)", "Net bid ($)", "$/MHz-pop", "MHz-pop", "B1 cum. pop share",
            "Paired", "Resold in A113"])
for i, x in enumerate(A97, r0):
    vals = [x["license"], x["market"], x["market_name"], x["block"], x["frequencies"], int(x["mhz"]),
            int(x["population_2010"]), x["sold"], x["bidder"], x["frn"], float(x["gross_bid"]),
            float(x["net_bid"])]
    for j, v in enumerate(vals, 1):
        c = ws.cell(row=i, column=j, value=v)
        c.font = BLUE
    ws.cell(row=i, column=11).number_format = USD
    ws.cell(row=i, column=12).number_format = USD
    ws.cell(row=i, column=13, value=f'=IF(AND(H{i}="Y",G{i}>0),K{i}/(F{i}*G{i}),"")').number_format = PMP
    ws.cell(row=i, column=14, value=f"=F{i}*G{i}").number_format = INT
    ws.cell(row=i, column=15, value=(
        f'=IF(AND(D{i}="B1",H{i}="Y",G{i}>0),SUMIFS($G${r0}:$G${r1},$D${r0}:$D${r1},"B1",$H${r0}:$H${r1},"Y",'
        f'$M${r0}:$M${r1},"<="&M{i})/SUMIFS($G${r0}:$G${r1},$D${r0}:$D${r1},"B1",$H${r0}:$H${r1},"Y"),"")'
    )).number_format = '0.0000'
    ws.cell(row=i, column=16, value=f'=IF(OR(D{i}="G",D{i}="H",D{i}="I",D{i}="J"),1,0)')
    ws.cell(row=i, column=17, value=f'=IF(ISNUMBER(MATCH(SUBSTITUTE(A{i},"AW-",""),Raw_A113!$A$5:$A$204,0)),1,0)')
ws.freeze_panes = "B5"
R97 = lambda col: f"Raw_A97!${col}${r0}:${col}${r1}"

# ======================================================== Raw_A113
n113 = len(A113)
s0, s1 = 5, 5 + n113 - 1
ws = sheet("Raw_A113", "Auction 113 per-license results (FCC Public Reporting System)",
           [12, 9, 30, 6, 6, 13, 32, 14, 15, 15, 11, 15, 8, 13, 8])
put(ws, "A3", "Source: FCC PRS, auctiondata.fcc.gov, Auction 113 'Results by License' and 'Markets' downloads "
    "(Nov 10, 2026). Population basis is the one the FCC used for Auction 113.")
hdr(ws, 4, ["License", "Market", "Market name", "Block", "MHz", "Population", "Winning bidder",
            "Bidding credit", "Gross bid ($)", "Net bid ($)", "$/MHz-pop", "Auction 97 gross ($)",
            "A97 sold", "A97 population", "Matched pair"])
for i, x in enumerate(A113, s0):
    vals = [x["license"], x["market"], x["market_name"], x["block"], int(x["mhz"]), int(x["population"]),
            x["bidder"], x["bidding_credit_type"], float(x["gross_bid"]), float(x["net_bid"])]
    for j, v in enumerate(vals, 1):
        ws.cell(row=i, column=j, value=v).font = BLUE
    ws.cell(row=i, column=9).number_format = USD
    ws.cell(row=i, column=10).number_format = USD
    ws.cell(row=i, column=11, value=f'=IF(F{i}>0,I{i}/(E{i}*F{i}),"")').number_format = PMP
    m = f'MATCH("AW-"&A{i},{R97("A")},0)'
    c = ws.cell(row=i, column=12, value=f'=IFERROR(INDEX({R97("K")},{m}),0)')
    c.number_format, c.font = USD, GREEN
    ws.cell(row=i, column=13, value=f'=IFERROR(INDEX({R97("H")},{m}),"N")').font = GREEN
    c = ws.cell(row=i, column=14, value=f'=IFERROR(INDEX({R97("G")},{m}),0)')
    c.number_format, c.font = INT, GREEN
    ws.cell(row=i, column=15, value=f'=IF(AND(M{i}="Y",N{i}>0,F{i}>0),1,0)')
ws.freeze_panes = "B5"
R113 = lambda col: f"Raw_A113!${col}${s0}:${col}${s1}"

# ======================================================== Evidence
ws = sheet("Evidence", "Evidence computed from the raw auction data", [62, 18, 70])
hdr(ws, 4, ["Measure", "Value", "What it shows"])
EV = {}
blk_sum = lambda b: f'SUMIFS({R97("K")},{R97("D")},"{b}",{R97("H")},"Y")'
blk_mp = lambda b: f'SUMIFS({R97("N")},{R97("D")},"{b}",{R97("H")},"Y")'
unp_mp = f"({blk_mp('A1')}+{blk_mp('B1')})"
holder = lambda name: (f'(SUMIFS({R97("N")},{R97("I")},"{name}",{R97("D")},"A1")+'
                       f'SUMIFS({R97("N")},{R97("I")},"{name}",{R97("D")},"B1"))/{unp_mp}')
held = lambda name: (f'(SUMIFS({R97("N")},{R97("I")},"{name}",{R97("D")},"A1",{R97("Q")},0)+'
                     f'SUMIFS({R97("N")},{R97("I")},"{name}",{R97("D")},"B1",{R97("Q")},0))/{unp_mp}')
ev = [
    ("h1", "Auction 97 totals", None, None, ""),
    ("g97", "Gross bids, all licenses ($)", f'=SUM({R97("K")})', USD, "Reconciles to the published $44.9B."),
    ("n97", "Net bids, all licenses ($)", f'=SUM({R97("L")})', USD, "Must equal the published net exactly."),
    ("c97", "Licenses won", f'=COUNTIF({R97("H")},"Y")', INT, "Must equal 1,611."),
    ("h2", "Auction 97 unpaired 1695–1710 MHz (2010 population)", None, None, ""),
    ("a1", "A1 (5 MHz) $/MHz-pop", f"={blk_sum('A1')}/{blk_mp('A1')}", PMP, "5 MHz block; heavily discounted."),
    ("b1", "B1 (10 MHz) $/MHz-pop", f"={blk_sum('B1')}/{blk_mp('B1')}", PMP,
     "Same block size as the FNPRM proposal."),
    ("ab", "A1 + B1 $/MHz-pop", f"=({blk_sum('A1')}+{blk_sum('B1')})/{unp_mp}", PMP,
     "Published figure is $0.52 (Cramton)."),
    ("pr", "Paired G, H, I, J $/MHz-pop",
     f"=({blk_sum('G')}+{blk_sum('H')}+{blk_sum('I')}+{blk_sum('J')})/"
     f"({blk_mp('G')}+{blk_mp('H')}+{blk_mp('I')}+{blk_mp('J')})", PMP, "Published figure is $2.72."),
    ("ratio", "Paired price ÷ unpaired price", "=B13/B12", '0.0"x"', "The unpaired discount."),
    ("q25", "B1 population-weighted 25th percentile $/MHz-pop",
     f'=_xlfn.MINIFS({R97("M")},{R97("O")},">=0.25")', PMP, "Low case for terrestrial uplink."),
    ("q50", "B1 population-weighted median $/MHz-pop", f'=_xlfn.MINIFS({R97("M")},{R97("O")},">=0.5")', PMP, ""),
    ("q75", "B1 population-weighted 75th percentile $/MHz-pop",
     f'=_xlfn.MINIFS({R97("M")},{R97("O")},">=0.75")', PMP, "Wide spread: one national price hides a lot."),
    ("h3", "Who won the unpaired spectrum in 2015 (share of A1 + B1 MHz-pops)", None, None, ""),
    ("ns", "Northstar Wireless (Dish-affiliated designated entity)", "=" + holder("Northstar Wireless, LLC"), PCT, ""),
    ("snr", "SNR Wireless LicenseCo (Dish-affiliated designated entity)",
     "=" + holder("SNR Wireless LicenseCo, LLC"), PCT, ""),
    ("bid", "2014 AWS Spectrum Bidco Corporation", "=" + holder("2014 AWS Spectrum Bidco Corporation"), PCT,
     "Ownership not verified. If EchoStar holds these too, its share is near 100%."),
    ("dish", "Northstar + SNR, less licenses resold in Auction 113",
     "=" + held("Northstar Wireless, LLC") + "+" + held("SNR Wireless LicenseCo, LLC"), PCT,
     "Default EchoStar holdings share (Transactions)."),
    ("dishall", "Northstar + SNR + Bidco, less resold", "=B22+" + held("2014 AWS Spectrum Bidco Corporation"),
     PCT, "Upper bound on EchoStar holdings; gives the low EchoStar price."),
    ("h4", "Auction 113 (2026)", None, None, ""),
    ("g113", "Gross bids, all licenses ($)", f'=SUM({R113("I")})', USD, "Must equal $3,572,889,200."),
    ("n113", "Net bids, all licenses ($)", f'=SUM({R113("J")})', USD, "Must equal $3,572,347,950."),
    ("c113", "Licenses in the results file", f'=COUNTA({R113("A")})', INT,
     "Parse-completeness test: must equal the 200 licenses won."),
    ("u113", "Unpaired (A1 or B1) licenses in Auction 113",
     f'=COUNTIF({R113("D")},"A1")+COUNTIF({R113("D")},"B1")', INT,
     "Only two: Auction 113 is anecdotal evidence for unpaired spectrum."),
    ("spx113", "SpaceX's Auction 113 B1 win (Cincinnati, BEA049) $/MHz-pop",
     f'=INDEX({R113("K")},MATCH("BEA049-B1",{R113("A")},0))', PMP,
     "SpaceX's own competitive price for this use in 2026. Low case for satellite uplink."),
    ("spxn", "Licenses SpaceX won in Auction 113", f'=COUNTIF({R113("G")},"Space Exploration*")', INT, ""),
    ("h5", "Test: are nominal $/MHz-pop flat over time? (licenses sold in both auctions)", None, None, ""),
    ("np", "Matched licenses", f'=SUM({R113("O")})', INT, "Defaulted 2015 licenses resold in 2026."),
    ("flat", "2026 $/pop ÷ 2015 $/pop, aggregate",
     f'=(SUMPRODUCT({R113("I")},{R113("O")})/SUMPRODUCT({R113("F")},{R113("O")}))/'
     f'(SUMPRODUCT({R113("L")},{R113("O")})/SUMPRODUCT({R113("N")},{R113("O")}))', RAT,
     "Near 1.0 supports the FCC's 'flat nominal' view, and supports applying $/MHz-pop to current "
     "population. Mostly paired licenses."),
]
for i, (key, lab, val, fmt, why) in enumerate(ev, 5):
    if val is None:
        put(ws, f"A{i}", lab, BOLD)
        ws[f"A{i}"].fill = GREY
        continue
    put(ws, f"A{i}", lab)
    put(ws, f"B{i}", val, fmt=fmt)
    put(ws, f"C{i}", why, wrap=True)
    EV[key] = f"Evidence!$B${i}"
assert EV["ratio"].endswith("$14") and EV["ns"].endswith("$19") and EV["dish"].endswith("$22") and EV["dishall"].endswith("$23"), EV

# ======================================================== Transactions
ws = sheet("Transactions", "Spectrum transactions", [34, 16, 9, 14, 15, 14, 72, 13])
hdr(ws, 4, ["Transaction", "Price ($)", "MHz", "Population covered (share of U.S.)", "$/MHz-pop",
            "Payment", "Source and caveats", "Primary source verified?"])
tx = [
    ("SpaceX / EchoStar unpaired AWS-3 (1695–1710 MHz)", 2600000000, 15, f"={EV['dish']}", "SpaceX stock",
     "EchoStar press release, Nov 6, 2025: about $2.6B in SpaceX stock valued as of Sept 2025, up to 15 MHz, "
     "Band 70 uplink. Coverage defaults to the Northstar + SNR share of 2015 unpaired MHz-pops (Evidence). "
     "If EchoStar also holds the Bidco licenses, coverage is near 100% and the price drops to about $0.52."),
    ("SpaceX / Grain 800 MHz (SpaceX price)", 8000000000, 14, 1, "Cash (reported)",
     "Announced Oct 8, 2026; terms not disclosed; $8B per the Wall Street Journal. Up to 14 MHz paired. "
     "One buyer's strategic price for low band with terrestrial rights."),
    ("SpaceX / Grain 800 MHz (prior market)", 3600000000, 14, 1, "Reported",
     "Fierce Network (Oct 2026): the same spectrum was once on the market for about $3.6B. "
     "A market price without SpaceX's strategic premium."),
    ("Amazon / Globalstar (cross-check only)", 11570000000, 25, 1, "Company",
     "Announced Apr 14, 2026; FCC approved Oct 27, 2026. Enterprise value with satellites, the Apple "
     "agreement, and global MSS rights. Not used in any benchmark."),
]
TX = {}
for i, (name, price, mhz, cov, pay, src) in enumerate(tx, 5):
    put(ws, f"A{i}", name, wrap=True)
    put(ws, f"B{i}", price, fmt=USD)
    put(ws, f"C{i}", mhz, fmt=INT)
    put(ws, f"D{i}", cov, fmt=PCT, fill=YELLOW if i == 5 else None)
    put(ws, f"E{i}", f"=B{i}/(C{i}*D{i}*{INP['pop']})", fmt=PMP)
    put(ws, f"F{i}", pay)
    put(ws, f"G{i}", src, wrap=True)
    put(ws, f"H{i}", "PENDING", BLUE, fill=YELLOW)
    ws.row_dimensions[i].height = 62
    TX[i] = f"Transactions!$E${i}"

# ======================================================== Benchmarks
ws = sheet("Benchmarks", "Benchmark by use case (nominal $/MHz-pop)", [10, 13, 13, 13, 90])
hdr(ws, 4, ["Use case", "Low", "Base", "High", "Basis"])
bm = [
    ("TDL", f"={EV['ab']}", f"={EV['ab']}", f"=2*{INP['dlshare']}*{EV['pr']}",
     "SUSPENDED. No unpaired downlink comparable. Low and base: unpaired price. High: paired price × downlink "
     "share × 2, because the paired $/MHz-pop is spread over both halves. Needs a real comparable."),
    ("TUL", f"={EV['q25']}", f"={EV['ab']}", f"={EV['b1']}",
     "Auction 97 unpaired 1695–1710 MHz. Low: B1 population-weighted 25th percentile. Base: A1 + B1. "
     "High: B1 (same 10 MHz block size)."),
    ("SUL", f"={EV['spx113']}", f"={TX[5]}", f"={EV['b1']}",
     "Low: SpaceX's own 2026 Auction 113 B1 price. Base: SpaceX/EchoStar on matched holdings. High: B1."),
    ("SDL", f"={TX[5]}", f"={TX[7]}", f"={TX[6]}",
     "Low: SUL base (no downlink premium). Base: Grain prior market price. High: SpaceX's Grain price "
     "(800 MHz low band; likely overstates 1.7 GHz)."),
]
for i, (u, lo, ba, hi, basis) in enumerate(bm, 5):
    put(ws, f"A{i}", u, BOLD)
    for col, v in (("B", lo), ("C", ba), ("D", hi)):
        put(ws, f"{col}{i}", v, fmt=PMP)
    put(ws, f"E{i}", basis, wrap=True)
    ws.row_dimensions[i].height = 45
UC, CASES, TABLE = "Benchmarks!$A$5:$A$8", "Benchmarks!$B$4:$D$4", "Benchmarks!$B$5:$D$8"

# ======================================================== Bidders
ws = sheet("Bidders", "Credible bidders", [20, 13, 11, 70])
hdr(ws, 4, ["Bidder", "Class", "Value multiplier", "Why credible, and doubts (public sources)"])
BIDDERS = [
    ("SpaceX", "D2D", "Bought EchoStar AWS-4, H-block, and unpaired AWS-3 (~$19.6B) and Grain 800 MHz (~$8B). "
     "Won B1 Cincinnati and one other license in Auction 113. Owns the adjacent 1695–1710 MHz."),
    ("Amazon Leo", "D2D", "Acquired Globalstar (FCC approved Oct 27, 2026); D2D service planned from 2028."),
    ("AST SpaceMobile", "D2D", "D2D operator backed by AT&T and Verizon; L-band arrangement with Ligado. "
     "Doubt: capital (about $1.5B cash mid-2025; later raises reported but not verified here)."),
    ("Carrier D2D JV", "D2D", "AT&T, Verizon, T-Mobile D2D spectrum-pooling JV (reported Oct 2026). Off by default."),
    ("AT&T", "Carrier", "Largest Auction 97 winner; won 10 licenses in Auction 113."),
    ("Verizon", "Carrier", "Won 82 licenses for $3.16B in Auction 113."),
    ("T-Mobile", "Carrier", "Won 102 licenses in Auction 113."),
    ("Ligado", "Adjacent", "Holds 1670–1675 MHz next to the lower block. Doubt: in Chapter 11 restructuring "
     "(plan approved Sept 2025; claims still being settled in July 2026). Valued at the carrier benchmark."),
]
MULT = {}
for i, (n, cl, why) in enumerate(BIDDERS, 5):
    put(ws, f"A{i}", n, BOLD)
    put(ws, f"B{i}", cl)
    put(ws, f"C{i}", 1.0, fmt=RAT)
    put(ws, f"D{i}", why, wrap=True)
    ws.row_dimensions[i].height = 45
    MULT[n] = f"Bidders!$C${i}"
note(ws, "A14", "Bidder list: SpaceX, Amazon, the carriers (Nick, Nov 10, 2026); AST SpaceMobile and Ligado "
     "added at Nick's request. Sign-off still open.", "D14")

# ======================================================== Scenarios
ws = sheet("Scenarios", "Scenarios and pricing rule", [44] + [15] * 9)
SC = [
    # name, desc, case, carrier, d2d, SpX, Amz, AST, JV, ATT, VZ, TMO, Lig, spx2, include
    ("S1 Base", "All bidders; D2D values the band as uplink (same-frequency evidence)", "Base", "TUL", "SUL",
     1, 1, 1, 0, 1, 1, 1, 1, 0, "Y"),
    ("S2 D2D downlink value", "All bidders; D2D values the band as downlink", "Base", "TUL", "SDL",
     1, 1, 1, 0, 1, 1, 1, 1, 0, "Y"),
    ("S3 Downlink, two D2D", "As S2 without AST and Ligado", "Base", "TUL", "SDL",
     1, 1, 0, 0, 1, 1, 1, 0, 0, "Y"),
    ("S4 SpaceX wants 20 MHz", "As S3; SpaceX may bid for both blocks (demand reduction applies)", "Base",
     "TUL", "SDL", 1, 1, 0, 0, 1, 1, 1, 0, 1, "Y"),
    ("S5 Carrier JV joins", "As S3 plus carrier D2D JV", "Base", "TUL", "SDL", 1, 1, 0, 1, 1, 1, 1, 0, 0, "Y"),
    ("S6 Low", "All bidders; low benchmarks", "Low", "TUL", "SUL", 1, 1, 1, 0, 1, 1, 1, 1, 0, "Y"),
    ("S7 High", "All bidders; high benchmarks, D2D downlink", "High", "TUL", "SDL",
     1, 1, 1, 0, 1, 1, 1, 1, 0, "Y"),
    ("S8 Lease-only SCS", "D2D firms lease SCS rights instead of bidding", "Base", "TUL", "SUL",
     0, 0, 0, 0, 1, 1, 1, 1, 0, "Y"),
    ("S9 Carriers downlink", "SUSPENDED: no downlink comparable", "Base", "TDL", "SUL",
     1, 1, 1, 0, 1, 1, 1, 1, 0, "N"),
]
rows = ["Scenario", "Description", "Benchmark case (Low/Base/High)", "Carrier use case", "D2D use case",
        "SpaceX participates", "Amazon Leo participates", "AST SpaceMobile participates",
        "Carrier D2D JV participates", "AT&T participates", "Verizon participates", "T-Mobile participates",
        "Ligado participates", "SpaceX wants both blocks", "Include in Summary range (Y/N)"]
for k, lab in enumerate(rows, 4):
    put(ws, f"A{k}", lab)
ws["A4"].font, ws["A4"].fill = HDR_FONT, HDR_FILL
calc = {20: "Carrier $/MHz-pop", 21: "D2D $/MHz-pop", 22: "Carrier value per block ($)",
        23: "D2D value per block ($)", 25: "Unit bid: SpaceX, block 1", 26: "Unit bid: Amazon Leo",
        27: "Unit bid: AST SpaceMobile", 28: "Unit bid: Carrier D2D JV", 29: "Unit bid: AT&T",
        30: "Unit bid: Verizon", 31: "Unit bid: T-Mobile", 32: "Unit bid: Ligado",
        33: "Unit bid: SpaceX, block 2", 35: "Unit bids if SpaceX bids for one block",
        36: "Unit bids if SpaceX bids for two", 37: "Price if SpaceX bids for one ($)",
        38: "Price if SpaceX bids for two ($)", 39: "Other bids above SpaceX's value",
        40: "SpaceX blocks won, bidding for one", 41: "SpaceX blocks won, bidding for two",
        42: "SpaceX surplus, bidding for one ($)", 43: "SpaceX surplus, bidding for two ($)",
        44: "SpaceX bids for two (demand reduction decides)", 45: "Clearing price per block ($)",
        46: "Blocks sold", 47: "Gross revenue ($)", 48: "Implied $/MHz-pop", 49: "Lowest winning value ($)",
        50: "Blocks won by D2D bidders", 51: "Winning class", 52: "Every winner's value ≥ price",
        53: "Label"}
put(ws, "A19", "Calculation", BOLD)
for r, lab in calc.items():
    put(ws, f"A{r}", lab, BOLD if r in (45, 47) else None)
B, MH, POP, AV, RES = INP["blocks"], INP["mhz"], INP["pop"], INP["avail"], INP["reserve"]
order = ["SpaceX", "Amazon Leo", "AST SpaceMobile", "Carrier D2D JV", "AT&T", "Verizon", "T-Mobile", "Ligado"]
for j, s in enumerate(SC):
    c = get_column_letter(2 + j)
    hdr(ws, 4, [s[0]], col=2 + j)
    for k, v in enumerate(s[1:], 5):
        put(ws, f"{c}{k}", v, BLUE, wrap=(k == 5))
    look = lambda use: f"=INDEX({TABLE},MATCH({use},{UC},0),MATCH({c}6,{CASES},0))"
    put(ws, f"{c}20", look(f"{c}7"), fmt=PMP)
    put(ws, f"{c}21", look(f"{c}8"), fmt=PMP)
    put(ws, f"{c}22", f"={c}20*{MH}*{POP}*{AV}", fmt=USD)
    put(ws, f"{c}23", f"={c}21*{MH}*{POP}*{AV}", fmt=USD)
    for k, name in enumerate(order):
        r = 25 + k
        part = f"{c}{9 + k}"
        base = f"{c}23" if k < 4 else f"{c}22"
        put(ws, f"{c}{r}", f"={base}*{MULT[name]}*{part}", fmt=USD)
    put(ws, f"{c}33", f"={c}25*{c}17*{INP['spx2']}", fmt=USD)
    put(ws, f"{c}35", f'=COUNTIF({c}25:{c}32,">0")', fmt=INT)
    put(ws, f"{c}36", f'=COUNTIF({c}25:{c}33,">0")', fmt=INT)
    put(ws, f"{c}37", f"=IF({c}35>{B},MAX(LARGE({c}25:{c}32,{B}+1),{RES}),{RES})", fmt=USD)
    put(ws, f"{c}38", f"=IF({c}36>{B},MAX(LARGE({c}25:{c}33,{B}+1),{RES}),{RES})", fmt=USD)
    put(ws, f"{c}39", f'=COUNTIF({c}26:{c}32,">"&{c}25)', fmt=INT)
    put(ws, f"{c}40", f"=IF({c}25>0,IF({c}39>={B},0,1),0)", fmt=INT)
    put(ws, f"{c}41", f'=IF(AND({c}25>0,{c}17=1),IF({c}39<{B},1,0)+IF(AND({c}33>0,COUNTIF({c}26:{c}32,">"&{c}33)<={B}-2),1,0),0)', fmt=INT)
    put(ws, f"{c}42", f"={c}40*({c}25-{c}37)", fmt=USD)
    put(ws, f"{c}43", f"={c}41*({c}33-{c}38)+MIN({c}41,1)*({c}25-{c}33)", fmt=USD)
    put(ws, f"{c}44", f"=IF(AND({c}17=1,{c}43>{c}42),1,0)", fmt=INT)
    put(ws, f"{c}45", f"=IF({c}44=1,{c}38,{c}37)", BOLD, fmt=USD)
    put(ws, f"{c}46", f"=MIN({B},IF({c}44=1,{c}36,{c}35))", fmt=INT)
    put(ws, f"{c}47", f"={c}45*{c}46", BOLD, fmt=USD)
    put(ws, f"{c}48", f"=IF({c}46>0,{c}47/({c}46*{MH}*{POP}),0)", fmt=PMP)
    put(ws, f"{c}49", f"=IFERROR(IF({c}44=1,LARGE({c}25:{c}33,{B}),LARGE({c}25:{c}32,{B})),0)", fmt=USD)
    put(ws, f"{c}50", f"=MIN({c}46,IF({c}44=1,{c}41,{c}40)+SUMPRODUCT(({c}26:{c}28>={c}49)*({c}26:{c}28>0)))",
        fmt=INT)
    put(ws, f"{c}51", f'=IF({c}46=0,"None",IF({c}50>={c}46,"D2D",IF({c}50=0,"Carrier/adjacent","Split")))')
    put(ws, f"{c}52", f"=OR({c}46=0,{c}49>={c}45)")
    put(ws, f"{c}53", LABEL, MARK, wrap=True)
    ws.column_dimensions[c].width = 16
ws.row_dimensions[5].height = 75
ws.row_dimensions[53].height = 30
for r in (25, 33):
    ws[f"A{r}"].fill = GREY
note(ws, "A55", "Pricing rule: each bidder wants one 10 MHz block; SpaceX may want two. The uniform clock price "
     "stops at the highest losing unit bid. Demand reduction: SpaceX bids for two blocks only if that leaves it "
     "more surplus than bidding for one. Unit bid = benchmark $/MHz-pop × 10 MHz × 2020 population × "
     "availability × bidder multiplier. Ligado is valued at the carrier benchmark.", "J55", 60)
ws.freeze_panes = "B5"
LASTC = get_column_letter(1 + len(SC))
SCR = lambda r: f"Scenarios!$B${r}:${LASTC}${r}"

# ======================================================== Monte Carlo (Python, fixed seed)
# Recompute the benchmarks from raw data to drive the simulation.
f = lambda s: float(s) if s not in ("", None) else 0.0
sold = [x for x in A97 if x["sold"] == "Y"]
mp = lambda rows: sum(int(x["mhz"]) * int(x["population_2010"]) for x in rows)
gs = lambda rows: sum(f(x["gross_bid"]) for x in rows)
unp = [x for x in sold if x["block"] in ("A1", "B1")]
tul_base = gs(unp) / mp(unp)
b1rows = sorted([(f(x["gross_bid"]) / (10 * int(x["population_2010"])), int(x["population_2010"]))
                 for x in sold if x["block"] == "B1" and int(x["population_2010"]) > 0])
tot = sum(w for _, w in b1rows)


def wq(q):
    c = 0
    for v, w in b1rows:
        c += w
        if c >= q * tot:
            return v


resold = {"AW-" + x["license"] for x in A113}
share = (mp([x for x in unp if x["bidder"] in ("Northstar Wireless, LLC", "SNR Wireless LicenseCo, LLC")
             and x["license"] not in resold]) / mp(unp))
pop20 = 331449281
sul_base = 2.6e9 / (15 * share * pop20)
spx113 = [f(x["gross_per_mhz_pop"]) for x in A113 if x["license"] == "BEA049-B1"][0]
sdl_base = 3.6e9 / (14 * pop20)
paired_winners = {}
for x in sold:
    if x["block"] in ("G", "H", "I", "J") and int(x["population_2010"]) > 0:
        d = paired_winners.setdefault(x["bidder"], [0.0, 0])
        d[0] += f(x["gross_bid"])
        d[1] += int(x["mhz"]) * int(x["population_2010"])
paired_all = sum(v[0] for v in paired_winners.values()) / sum(v[1] for v in paired_winners.values())
big = [v[0] / v[1] / paired_all for k, v in paired_winners.items() if v[0] > 1e9]
sigma = st.pstdev([math.log(r) for r in big])
rng = random.Random(1675)
N = 10000
rev, d2d_sets = [], 0
for _ in range(N):
    carriers = [tul_base * math.exp(rng.gauss(0, sigma)) for _ in range(4)]  # AT&T, VZ, TMO, Ligado
    d2d = [rng.uniform(spx113, sdl_base) for _ in range(3)]  # SpaceX, Amazon, AST
    vals = sorted(carriers + d2d, reverse=True)
    price = vals[2]
    if price in d2d:
        d2d_sets += 1
    rev.append(2 * price * 10 * pop20)
rev.sort()
pct = lambda p: rev[int(p * (N - 1))]

ws = sheet("MonteCarlo", "Monte Carlo of the pricing rule (illustrative)", [58, 18, 70])
put(ws, "A3", "Values below come from build_1675_workbook_v02.py (seed 1675, 10,000 draws). They are pasted "
    "values, not live formulas; rerun the script after changing assumptions.", wrap=True)
ws.merge_cells("A3:C3")
ws.row_dimensions[3].height = 30
hdr(ws, 5, ["Item", "Value", "Note"])
mc = [
    ("Carrier value: TUL base × lognormal", tul_base, PMP, "AT&T, Verizon, T-Mobile, Ligado"),
    ("Carrier spread (σ of log price relative to auction average)", sigma, RAT,
     "From Auction 97 paired prices of winners that spent over $1B"),
    ("D2D value: uniform, low end ($/MHz-pop)", spx113, PMP, "SpaceX's Auction 113 B1 price"),
    ("D2D value: uniform, high end ($/MHz-pop)", sdl_base, PMP, "Grain prior market price"),
    ("Draws", N, INT, "SpaceX bids for one block (demand reduction)."),
    ("Gross revenue, 10th percentile ($)", pct(0.10), USDB, LABEL),
    ("Gross revenue, median ($)", pct(0.50), USDB, LABEL),
    ("Gross revenue, 90th percentile ($)", pct(0.90), USDB, LABEL),
    ("Gross revenue, mean ($)", sum(rev) / N, USDB, LABEL),
    ("Share of draws where a D2D bidder sets the price", d2d_sets / N, PCT,
     "Needs three D2D values above the top carrier"),
]
MC = {}
for i, (lab, v, fmt, nt) in enumerate(mc, 6):
    put(ws, f"A{i}", lab)
    put(ws, f"B{i}", v, BLUE, fmt=fmt)
    put(ws, f"C{i}", nt, wrap=True)
    MC[i] = f"MonteCarlo!$B${i}"
note(ws, "A17", "Illustrative only. The D2D value range is a judgment, not evidence. Use the median and "
     "spread to show that the outcome depends on whether three D2D bidders value the band above the "
     "strongest carrier.", "C17", 45)
MCPY = dict(tul_base=tul_base, sul_base=sul_base, spx113=spx113, sdl_base=sdl_base, share=share,
            p10=pct(.1), p50=pct(.5), p90=pct(.9), d2d=d2d_sets / N, sigma=sigma)

# ======================================================== Revenue_Defs
ws = sheet("Revenue_Defs", "Revenue definitions", [34] + [15] * 9)
hdr(ws, 4, ["Measure"] + [s[0] for s in SC])
put(ws, "A3", LABEL + ".", MARK)
for i, lab in enumerate(["Gross bids ($)", "Net bids at Auction 113 credit rate ($)", "Net of NOAA costs ($)",
                         "Budget score", "Net bids at Auction 97 credit rate ($)"], 5):
    put(ws, f"A{i}", lab)
for j in range(len(SC)):
    c = get_column_letter(2 + j)
    put(ws, f"{c}5", f"=Scenarios!{c}47", fmt=USD)
    put(ws, f"{c}6", f"={c}5*{INP['net2gross']}", fmt=USD)
    put(ws, f"{c}7", f"={c}6-{INP['noaa']}", fmt=USD)
    put(ws, f"{c}8", "Outside model")
    put(ws, f"{c}9", f"={c}5*{EV['n97']}/{EV['g97']}", fmt=USD)
note(ws, "A11", "Headline uses gross bids. Auction 97's credit rate was about 8%; Auction 113's was near zero. If the Commercial Spectrum Enhancement Act applies, proceeds must "
     "reach 110% of federal relocation or sharing costs. Confirm with counsel.", "J11")

# ======================================================== FNPRM
ws = sheet("FNPRM", "FNPRM proposals used (FCC 26-70, WT Docket No. 26-284)", [46, 46, 26, 20])
hdr(ws, 4, ["Proposal", "Model input it drives", "Source", "Paragraph (adopted text)"])
fn = [("Two unpaired 10 MHz blocks", "Inputs: block size, number of blocks"),
      ("Alternative: unpaired 5 MHz blocks", "Not yet modeled"),
      ("Uplink, downlink, or TDD at licensee's choice", "Bidders value the license at their use case"),
      ("Secondary MSS allocation for SCS", "D2D bidder class; S8 lease-only"),
      ("License area: nationwide, regional, or PEA", "Nationwide only in v0.2"),
      ("Bundling and all-or-nothing nationwide package bids", "Not yet modeled"),
      ("Terrestrial buildout 45% and 80%", "Open question for D2D winners"),
      ("Small-business and rural bidding credits", "Net-to-gross ratio"),
      ("Coordination near four NOAA DCS sites", "Coordination tab (deferred)")]
for i, (p, m) in enumerate(fn, 5):
    put(ws, f"A{i}", p, wrap=True)
    put(ws, f"B{i}", m, wrap=True)
    put(ws, f"C{i}", "Covington, Oct 13, 2026 (draft)", wrap=True)
    put(ws, f"D{i}", "PENDING", BLUE, fill=YELLOW)

# ======================================================== Summary
ws = sheet("Summary", "1675–1695 MHz auction revenue (nationwide licenses), v0.2", [46, 17, 14, 30, 40])
put(ws, "A3", LABEL + ". Not for release.", MARK)
hdr(ws, 5, ["Measure (before federal coordination, upper bound)", "Gross revenue", "$/MHz-pop", "Scenario",
            "Meaning"])
inc = SCR(18)
summ = [
    ("Central estimate", "=Scenarios!B47", "=Scenarios!B48", "=Scenarios!B4",
     "Same-frequency evidence: D2D bidders value the band like uplink"),
    ("Floor", f'=_xlfn.MINIFS({SCR(47)},{inc},"Y")', f'=_xlfn.MINIFS({SCR(48)},{inc},"Y")',
     f'=INDEX(Scenarios!$B$4:${LASTC}$4,SUMPRODUCT(MAX(({SCR(47)}=B7)*({inc}="Y")*(COLUMN({SCR(47)})-1))))',
     "Low benchmarks"),
    ("Ceiling", f'=_xlfn.MAXIFS({SCR(47)},{inc},"Y")', f'=_xlfn.MAXIFS({SCR(48)},{inc},"Y")',
     f'=INDEX(Scenarios!$B$4:${LASTC}$4,SUMPRODUCT(MAX(({SCR(47)}=B8)*({inc}="Y")*(COLUMN({SCR(47)})-1))))',
     "Needs three D2D bidders at downlink value, high benchmarks"),
    ("Central, if EchoStar also holds the Bidco licenses",
     f"={B}*{MH}*{POP}*{AV}*MAX(Scenarios!B20,Transactions!B5/(Transactions!C5*{EV['dishall']}*{POP}))",
     f"=MAX(Scenarios!B20,Transactions!B5/(Transactions!C5*{EV['dishall']}*{POP}))", "S1 variant",
     "Lower EchoStar price per MHz-pop; three D2D bidders"),
    ("Monte Carlo median (illustrative)", f"={MC[12]}", "", "MonteCarlo",
     "Pasted values from the build script; does not update with inputs"),
]
for i, (lab, a, b, c, d) in enumerate(summ, 6):
    put(ws, f"A{i}", lab, BOLD)
    put(ws, f"B{i}", a, fmt=USDB)
    put(ws, f"C{i}", b, fmt=PMP)
    put(ws, f"D{i}", c)
    put(ws, f"E{i}", d, wrap=True)
    ws.row_dimensions[i].height = 30
put(ws, "A11", "What drives the number", BOLD)  # rows 6-10 used above
put(ws, "A12", '="With two blocks, the third-highest bidder sets the price. With two or fewer D2D bidders, '
    'carriers set it: "&TEXT(B18,"$0.00,,,""B""")&". A third D2D bidder raises it to "&TEXT(B19,"$0.00,,,""B""")'
    '&" at the uplink evidence, or "&TEXT(C19,"$0.00,,,""B""")&" if D2D bidders value the band as downlink."',
    BLACK, wrap=True)
ws.merge_cells("A12:E12")
ws.row_dimensions[12].height = 48
put(ws, "A14", "Revenue by number of independent D2D bidders (before federal coordination, upper bound)", BOLD)
hdr(ws, 15, ["Independent D2D bidders", "D2D at uplink value", "D2D at downlink value"])
for k in range(5):
    r = 16 + k
    put(ws, f"A{r}", k, BLACK, fmt=INT)
    for col, d2dcell in (("B", "Scenarios!$B$23"), ("C", "Scenarios!$C$23")):
        put(ws, f"{col}{r}", f"={B}*IF(AND($A{r}>={B}+1,{d2dcell}>Scenarios!$B$22),{d2dcell},Scenarios!$B$22)",
            fmt=USDB)
put(ws, "A21", "Assumes four carrier or adjacent bidders at the carrier base value.")
hdr(ws, 23, ["Scenario (before federal coordination, upper bound)", "Gross revenue", "In range",
             "Winning class"])
for j, s in enumerate(SC):
    r, c = 24 + j, get_column_letter(2 + j)
    put(ws, f"A{r}", f"=Scenarios!{c}4")
    put(ws, f"B{r}", f"=Scenarios!{c}47", fmt=USDB)
    put(ws, f"C{r}", f"=Scenarios!{c}18")
    put(ws, f"D{r}", f"=Scenarios!{c}51")
put(ws, "A34", "Checks status:", BOLD)
put(ws, "A35", "Excluded: federal coordination, PEA and regional licenses, 5 MHz blocks, D2D exposure, timing, "
    "buildout, ODS. S9 is suspended.", wrap=True)
ws.merge_cells("A35:E35")
ws.row_dimensions[35].height = 30
ch = BarChart()
ch.type = "bar"
ch.title = "Gross revenue by scenario (before coordination, upper bound)"
ch.x_axis.title = None
ch.y_axis.numFmt = '$#,##0.0,,,"B"'
ch.add_data(Reference(ws, min_col=2, min_row=23, max_row=23 + len(SC)), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=24, max_row=23 + len(SC)))
ch.legend = None
ch.height, ch.width = 9, 22
ws.add_chart(ch, "A37")

# ======================================================== Checks
ws = sheet("Checks", "Checks (each can fail)", [74, 12, 60])
hdr(ws, 4, ["Check", "Status", "Detail"])
P = lambda cond: f'=IF({cond},"PASS","FAIL")'
checks = [
    ("Auction 97 net bids from raw data equal the published total", P(f"ROUND({EV['n97']}-{INP['pub97net']},0)=0"),
     "DA 15-131"),
    ("Auction 97 licenses won equal 1,611", P(f"{EV['c97']}={INP['pub97n']}"), "DA 15-131"),
    ("Auction 97 gross within 0.1% of the published $44.9B", P(f"ABS({EV['g97']}/{INP['pub97gross']}-1)<=0.001"),
     ""),
    ("Auction 113 gross and net from raw data equal the published totals",
     P(f"AND(ROUND({EV['g113']}-{INP['pub113gross']},0)=0,ROUND({EV['n113']}-{INP['pub113net']},0)=0)"),
     "DA 26-633"),
    ("Auction 113 licenses won equal 200", P(f"{EV['c113']}={INP['pub113n']}"), ""),
    ("Unpaired $/MHz-pop recomputed from raw data within 2% of Cramton's $0.52",
     P(f"ABS({EV['ab']}/{INP['cramU']}-1)<=0.02"), "Independent publication"),
    ("Paired $/MHz-pop recomputed from raw data within 2% of Cramton's $2.72",
     P(f"ABS({EV['pr']}/{INP['cramP']}-1)<=0.02"), "Independent publication"),
    ("Flat-nominal test: matched-pair price ratio between 0.8 and 1.25",
     P(f"AND({EV['flat']}>=0.8,{EV['flat']}<=1.25)"), "Fails if prices moved materially"),
    ("Benchmarks ordered low ≤ base ≤ high for every use case",
     P("SUMPRODUCT((Benchmarks!B5:B8>Benchmarks!C5:C8)+(Benchmarks!C5:C8>Benchmarks!D5:D8))=0"), ""),
    ("Lease-only revenue equals two blocks at the carrier base value",
     P(f"ROUND(Scenarios!I47-{B}*Scenarios!I22,0)=0"), "Second computation path"),
    ("Bidder-count table never decreases as D2D bidders are added",
     P("AND(SUMPRODUCT((Summary!B17:B20<Summary!B16:B19)*1)=0,SUMPRODUCT((Summary!C17:C20<Summary!C16:C19)*1)=0)"),
     ""),
    ("Bidder-count table at 3 and 2 D2D bidders matches S2 and S3",
     P("AND(ROUND(Summary!C19-Scenarios!C47,0)=0,ROUND(Summary!C18-Scenarios!D47,0)=0)"),
     "Two independent computation paths; needs default multipliers"),
    ("Every dollar table on Summary and Revenue_Defs carries the upper-bound label",
     P('AND(COUNTIF(Summary!A3:E23,"*upper bound*")>=4,COUNTIF(Revenue_Defs!A3,"*upper bound*")=1)'),
     "Fails if a table header loses the label"),
    ("Holdings-share net of resold licenses is no larger than gross 2015 share",
     P(f"{EV['dish']}<=Evidence!$B$19+Evidence!$B$20"), "Resold licenses can only reduce holdings"),
    ("Transaction terms verified in primary filings",
     '=IF(COUNTIF(Transactions!H5:H8,"PENDING")=0,"PASS","PENDING")', ""),
    ("FNPRM inputs cited to adopted paragraphs", '=IF(COUNTIF(FNPRM!D5:D13,"PENDING")=0,"PASS","PENDING")', ""),
]
for i, (lab, fml, d) in enumerate(checks, 5):
    put(ws, f"A{i}", lab, wrap=True)
    put(ws, f"B{i}", fml, BOLD)
    put(ws, f"C{i}", d, wrap=True)
last = 4 + len(checks)
guards = [
    ("Every winner's value ≥ the price it pays", f'=IF(COUNTIF({SCR(52)},FALSE)=0,"OK","CHECK")',
     "Holds by construction unless a reserve price is set"),
    ("Expected outcome: S4 equals S3 (demand reduction; SpaceX bids for one block)",
     '=IF(ROUND(Scenarios!E47-Scenarios!D47,0)=0,"OK","CHANGED")',
     "Not a correctness test: shows CHANGED if inputs make two blocks worth bidding for"),
    ("Coordination placeholder is 100% (deferred)", '=IF(Coordination!B5=1,"OK","CHANGED")',
     "Shows CHANGED once zones are added"),
]
hdr(ws, last + 4, ["Logic guards and expected outcomes (not tests)", "Status", "Note"])
for k, (lab, fml, d) in enumerate(guards, last + 5):
    put(ws, f"A{k}", lab, wrap=True)
    put(ws, f"B{k}", fml, BOLD)
    put(ws, f"C{k}", d, wrap=True)
put(ws, f"A{last + 2}", "Overall", BOLD)
put(ws, f"B{last + 2}", f'=IF(COUNTIF(B5:B{last},"FAIL")>0,"FAIL",IF(COUNTIF(B5:B{last},"PENDING")>0,'
    f'"PENDING","PASS"))', BOLD)
wb["Summary"]["B34"] = f"=Checks!B{last + 2}"
wb["Summary"]["B34"].font = GREEN

# ======================================================== README
ws = sheet("README", "1675–1695 MHz auction valuation workbook, v0.2", [120])
lines = [
    ("What changed from v0.1", BOLD),
    ("• Raw per-license data for Auction 97 (1,614 licenses) and Auction 113 (200 licenses); every benchmark is "
     "now a formula on that data.", None),
    ("• Bidders: added AST SpaceMobile and Ligado. Demand reduction for SpaceX. Lease-only SCS scenario.", None),
    ("• D2D base use case is uplink (same-frequency evidence); downlink is the upside.", None),
    ("• TDL formula corrected; carriers-downlink scenario suspended.", None),
    ("• Checks rebuilt so each can fail. Monte Carlo added (illustrative).", None),
    ("", None),
    ("Population basis", BOLD),
    ("Benchmarks use each auction's own population basis; values apply them to the 2020 Census population. "
     "The matched-pair test (Evidence) found 2026 $/pop within about 1% of 2015 $/pop for the same licenses, "
     "which supports this.", None),
    ("", None),
    ("Still not in v0.2", BOLD),
    ("• Federal coordination zones (deferred, 100%). • PEA and regional licenses. • 5 MHz band plan. "
     "• Primary filings for transaction terms. • Adopted FNPRM paragraph numbers.", None),
    ("", None),
    ("Every dollar figure in this workbook is: " + LABEL + ".", MARK),
    ("", None),
    ("Color key: blue = hardcoded input or raw data; black = formula; green = link to another tab; "
     "yellow = assumption to verify.", None),
    ("Scripts: parse_auctions.py (raw data), build_1675_workbook_v02.py (this workbook and the Monte Carlo).", None),
]
for i, (t, fnt) in enumerate(lines, 4):
    put(ws, f"A{i}", t, fnt or BLACK, wrap=True)

order_tabs = ["Summary", "README", "Scenarios", "Bidders", "Benchmarks", "Evidence", "Transactions",
              "MonteCarlo", "Inputs", "Revenue_Defs", "FNPRM", "Coordination", "Checks", "Raw_A97", "Raw_A113"]
wb._sheets = [wb[n] for n in order_tabs]
wb.active = 0
wb.save(OUT)
print(MCPY)
