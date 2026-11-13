"""Build the 1675-1695 MHz auction valuation workbook, v0.5 (bidder counts instead of a named list; terrestrial
downlink restored with two unpaired-downlink comparables; adopted FNPRM citations; gross revenue only).

Usage: python scripts/build_workbook.py <processed_dir> <out.xlsx> <pea_market.csv> [mc_draws.csv]
processed_dir holds a97_licenses.csv and a113_licenses.csv from parse_auctions.py and pea_ea.csv from parse_geo.py;
pea_market.csv is the FCC Auction 110 market file (data/raw/fcc_pea/a110_market.csv).
Run ./reproduce.sh instead of calling this directly.
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
PEA_FILE = Path(sys.argv[3])  # FCC PRS Auction 110 market download (406 PEAs, 2010 population)
MC_OUT = Path(sys.argv[4]) if len(sys.argv) > 4 else None  # optional CSV of every Monte Carlo draw
PEAS = list(csv.DictReader(open(PEA_FILE, encoding="utf-8-sig")))
A97 = list(csv.DictReader(open(DATA / "a97_licenses.csv")))
A113 = list(csv.DictReader(open(DATA / "a113_licenses.csv")))
PEA_EA = list(csv.DictReader(open(DATA / "pea_ea.csv")))
# Lower 700 MHz E Block EAs Qualcomm sold to AT&T: New York, Boston, Philadelphia, Los Angeles, San Francisco
# (FCC 11-188, para. 15). EA numbers from FCC DA 14-759 Appendix A.
QC_EAS = {10, 3, 12, 160, 163}
QC_E_POP = sum(int(r["population_2010"]) for r in PEA_EA if int(r["ea"]) in QC_EAS)

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
    ("mhz", "Block size (MHz)", 10, INT, None, "FNPRM para. 48: two unpaired 10 MHz blocks (1675-1685 and 1685-1695 MHz)."),
    ("blocks", "Number of blocks", 2, INT, None, "FNPRM para. 48. The 2020-2025 MHz block is out of scope."),
    ("reserve", "Reserve price per block ($)", 0, USD, YELLOW,
     "Not known. Used only when fewer unit bids than blocks plus one."),
    ("avail", "Federal coordination availability", "=Coordination!B5", PCT, None,
     "Deferred; 100% until zones are modeled."),
    ("spx2", "Lead D2D bidder's value of a second block (share of first)", 1.0, PCT, YELLOW,
     "Used only when one D2D bidder wants both blocks. Demand reduction then decides whether it bids for two."),
    ("caprate", "Capitalization rate for the 1670-1675 MHz lease", 0.07, PCT, YELLOW,
     "FNPRM App. C, para. 4 converts auction values to annual payments at 7% (OMB Circular A-4)."),
    ("adj", "Adjacency premium for the lead D2D bidder (share of its value)", 0.0, PCT, YELLOW,
     "A bidder next to the band may value it more (Ausubel et al. 1997). 0 by default; swept in analysis.py."),
    ("pub97net", "Auction 97 net bids, published ($)", 41329673325, USD, None,
     "FCC Public Notice DA 15-131 (Jan 30, 2015), para. 1."),
    ("pub97n", "Auction 97 licenses won, published", 1611, INT, None, "FCC Public Notice DA 15-131."),
    ("pub97gross", "Auction 97 gross bids, published (rounded, $)", 44900000000, USD, None,
     "Widely reported as $44.9 billion gross (for example, Cramton and Sujarittanonta 2015)."),
    ("pub113gross", "Auction 113 gross bids, published ($)", 3572889200, USD, None,
     "FCC Public Notice DA 26-633 (June 26, 2026)."),
    ("pub113net", "Auction 113 net bids, published ($)", 3572347950, USD, None,
     "FCC Public Notice DA 26-633, Attachment A (sum of bidder net payments)."),
    ("pub113n", "Auction 113 licenses won, published", 200, INT, None, "FCC Public Notice DA 26-633."),
    ("cramU", "Published Auction 97 unpaired $/MHz-pop", 0.52, PMP, None,
     "Cramton and Sujarittanonta, 'Bidding and Prices in the AWS-3 Auction' (2015). Independent cross-check."),
    ("cramP", "Published Auction 97 paired $/MHz-pop", 2.72, PMP, None, "Cramton and Sujarittanonta (2015)."),
    ("net2gross", "Net-to-gross ratio (Auction 113)", "=B17/B16", '0.0000%', None, "Formula."),
    ("akhi", "Alaska + Hawaii population, 2020 Census", 2188662, INT, None,
     "U.S. Census Bureau 2020: Alaska 733,391; Hawaii 1,455,271. Not in the Auction 110 PEA file."),
    ("slope", "Market-size slope used for carrier PEA values", "=Evidence!$B$35", RAT, YELLOW,
     "Defaults to the fitted Auction 97 B1 slope (Evidence). Override to test; 0 means flat $/pop."),
    ("exposure", "D2D exposure discount under PEA licensing", 0.0, PCT, YELLOW,
     "Extra cut to D2D per-PEA bids for the risk of not assembling a national footprint. "
     "Judgment; see License_Area sensitivity."),
    ("pop10", "U.S. population, 2010 Census", 308745538, INT, None,
     "U.S. Census Bureau (50 states and DC); equals the sum of PEA populations in FCC DA 14-759 App. A."),
    ("qcE", "Population of the five E Block EAs Qualcomm sold (2010)", QC_E_POP, INT, None,
     "FCC 11-188 para. 15 lists the EAs; populations summed from FCC DA 14-759 App. A."),
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
put(ws, "C5", "The NOAA zones (four DCS sites) constrain terrestrial base-station downlink only, so they don't "
    "change scenarios priced by D2D or uplink bids. The zone analysis for terrestrial downlink (NTIA Report 24-01 "
    "distances and smaller radii) is in scripts/analysis.py; results in data/csv/zone_*.csv.", wrap=True)
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
            "Paired", "Resold in A113", "B1 ln(pop)", "B1 ln($/MHz-pop)"])
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
    ws.cell(row=i, column=18, value=f'=IF(AND(D{i}="B1",H{i}="Y",G{i}>0,N(M{i})>0),LN(G{i}),"")')
    ws.cell(row=i, column=19, value=f'=IF(AND(D{i}="B1",H{i}="Y",G{i}>0,N(M{i})>0),LN(M{i}),"")')
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
    ("h6", "Market size and aggregation (for nationwide vs PEA licensing)", None, None, ""),
    ("slope", "B1 slope of ln($/MHz-pop) on ln(population)", f'=SLOPE({R97("S")},{R97("R")})', RAT,
     "Bigger markets paid more per pop. Drives carrier values by PEA."),
    ("rsq", "R-squared of that fit", f'=RSQ({R97("S")},{R97("R")})', RAT, ""),
    ("hold15", "2015 $/MHz-pop of the licenses EchoStar sold to SpaceX (Northstar + SNR, less resold)",
     f'=(SUMIFS({R97("K")},{R97("I")},"Northstar Wireless, LLC",{R97("D")},"A1",{R97("Q")},0)+'
     f'SUMIFS({R97("K")},{R97("I")},"Northstar Wireless, LLC",{R97("D")},"B1",{R97("Q")},0)+'
     f'SUMIFS({R97("K")},{R97("I")},"SNR Wireless LicenseCo, LLC",{R97("D")},"A1",{R97("Q")},0)+'
     f'SUMIFS({R97("K")},{R97("I")},"SNR Wireless LicenseCo, LLC",{R97("D")},"B1",{R97("Q")},0))/'
     f'(SUMIFS({R97("N")},{R97("I")},"Northstar Wireless, LLC",{R97("D")},"A1",{R97("Q")},0)+'
     f'SUMIFS({R97("N")},{R97("I")},"Northstar Wireless, LLC",{R97("D")},"B1",{R97("Q")},0)+'
     f'SUMIFS({R97("N")},{R97("I")},"SNR Wireless LicenseCo, LLC",{R97("D")},"A1",{R97("Q")},0)+'
     f'SUMIFS({R97("N")},{R97("I")},"SNR Wireless LicenseCo, LLC",{R97("D")},"B1",{R97("Q")},0))', PMP,
     "Sum of the market-by-market 2015 prices for the same licenses."),
    ("prem", "National-portfolio premium: EchoStar price ÷ (2015 price × flat-nominal ratio)",
     "=Transactions!$E$5/(B37*B33)", '0.00"x"',
     "What one buyer paid for a national footprint over the sum of market prices. One deal, paid in stock."),
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
assert EV["flat"].endswith("$33") and EV["slope"].endswith("$35") and EV["hold15"].endswith("$37") and EV["prem"].endswith("$38"), EV

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
    ("Qualcomm 700 MHz D and E Blocks to AT&T (unpaired downlink)", 1925000000, 12,
     f"=({INP['pop10']}+{INP['qcE']})/(2*{INP['pop']})", "Cash",
     "FCC 11-188 (Dec. 22, 2011), paras. 1, 15: $1.925B for six D Block licenses (6 MHz nationwide) and five E Block "
     "EA licenses (6 MHz in NY, Boston, Philadelphia, LA, SF). Coverage column makes MHz-pops = 6 x 2010 U.S. pop + "
     "6 x E Block EA pop. Used for supplemental downlink. 700 MHz low band: likely overstates 1.7 GHz."),
    ("1670-1675 MHz nationwide lease (capitalized)", f"=13000000/{INP['caprate']}", 5,
     f"={INP['pop10']}/{INP['pop']}", "Lease",
     "Crown Castle leased its 1670-1675 MHz license for $13M a year (TV Technology, July 27, 2007); capitalized "
     "as a perpetuity at the Inputs rate; 2010 population. Adjacent to the band. Auction 46 price (2003) not "
     "retrievable from FCC records here."),
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
    put(ws, f"H{i}", "VERIFIED (FCC 11-188)" if i == 9 else "PENDING", BLUE, fill=None if i == 9 else YELLOW)
    ws.row_dimensions[i].height = 62
    TX[i] = f"Transactions!$E${i}"

# ======================================================== Benchmarks
ws = sheet("Benchmarks", "Benchmark by use case (nominal $/MHz-pop)", [10, 13, 13, 13, 90])
hdr(ws, 4, ["Use case", "Low", "Base", "High", "Basis"])
bm = [
    ("TDL", f"={TX[10]}", f"=AVERAGE({TX[9]},{TX[10]})", f"={TX[9]}",
     "Two unpaired-downlink comparables. Low: the 1670-1675 MHz lease, capitalized (same band edge, thin "
     "market). High: Qualcomm 700 MHz D and E Blocks sold to AT&T for supplemental downlink (low band, so a "
     "ceiling). Base: their average."),
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
ws = sheet("Bidders", "Bidder pool: number of bidders by class (no named list)", [22, 14, 80])
hdr(ws, 4, ["Bidder class", "Value multiplier", "What the class means"])
CLASSES = [
    ("D2D", "Satellite direct-to-device operators. Value the band at the satellite uplink (SUL) or D2D downlink "
     "(SDL) benchmark. One of them may hold adjacent spectrum (adjacency premium, Inputs)."),
    ("Carrier", "Terrestrial mobile operators and other terrestrial bidders. Value the band at the terrestrial "
     "uplink (TUL) or terrestrial downlink (TDL) benchmark."),
]
MULT = {}
for i, (cl, why) in enumerate(CLASSES, 5):
    put(ws, f"A{i}", cl, BOLD)
    put(ws, f"B{i}", 1.0, fmt=RAT)
    put(ws, f"C{i}", why, wrap=True)
    ws.row_dimensions[i].height = 45
    MULT[cl] = f"Bidders!$B${i}"
note(ws, "A8", "The workbook uses a number of bidders in each class, set per scenario on the Scenarios tab, not a "
     "named list. The base case assumes three D2D and four terrestrial bidders. scripts/analysis.py sweeps 0-6 "
     "bidders in each class (data/csv/bidder_count_grid.csv).", "C8", 45)

# ======================================================== Scenarios
ws = sheet("Scenarios", "Scenarios and pricing rule", [44] + [15] * 9)
SC = [
    # name, desc, case, carrier use, d2d use, D2D bidders, terrestrial bidders, lead wants both, include
    ("S1 Base", "3 D2D and 4 terrestrial bidders; D2D values the band as uplink (same-frequency evidence)",
     "Base", "TUL", "SUL", 3, 4, 0, "Y"),
    ("S2 D2D downlink value", "As S1; D2D values the band as downlink", "Base", "TUL", "SDL", 3, 4, 0, "Y"),
    ("S3 Two D2D bidders", "As S2 with two D2D bidders", "Base", "TUL", "SDL", 2, 4, 0, "Y"),
    ("S4 One D2D bidder wants 20 MHz", "As S3; the lead D2D bidder may bid for both blocks (demand reduction)",
     "Base", "TUL", "SDL", 2, 4, 1, "Y"),
    ("S5 All downlink", "As S2; terrestrial bidders also value the band as downlink", "Base", "TDL", "SDL",
     3, 4, 0, "Y"),
    ("S6 Low", "As S1 with low benchmarks", "Low", "TUL", "SUL", 3, 4, 0, "Y"),
    ("S7 High", "As S2 with high benchmarks", "High", "TUL", "SDL", 3, 4, 0, "Y"),
    ("S8 Lease-only SCS", "D2D operators lease SCS rights instead of bidding", "Base", "TUL", "SUL", 0, 4, 0, "Y"),
    ("S9 Terrestrial downlink", "As S1; terrestrial bidders value the band as downlink", "Base", "TDL", "SUL",
     3, 4, 0, "Y"),
]
rows = ["Scenario", "Description", "Benchmark case (Low/Base/High)", "Terrestrial use case", "D2D use case",
        "D2D bidders (0-6)", "Terrestrial bidders (0-6)", "Lead D2D bidder wants both blocks",
        "Include in Summary range (Y/N)"]
for k, lab in enumerate(rows, 4):
    put(ws, f"A{k}", lab)
ws["A4"].font, ws["A4"].fill = HDR_FONT, HDR_FILL
calc = {14: "Terrestrial $/MHz-pop", 15: "D2D $/MHz-pop", 16: "Terrestrial value per block ($)",
        17: "D2D value per block ($)", 18: "Lead D2D bidder value per block, with adjacency premium ($)"}
for k in range(6):
    calc[19 + k] = f"Unit bid: D2D bidder {k + 1}" + (" (lead)" if k == 0 else "")
    calc[25 + k] = f"Unit bid: terrestrial bidder {k + 1}"
calc.update({31: "Unit bid: lead D2D bidder, block 2", 32: "Unit bids if the lead bids for one block",
             33: "Unit bids if the lead bids for two", 34: "Price if the lead bids for one ($)",
             35: "Price if the lead bids for two ($)", 36: "Other bids above the lead's value",
             37: "Lead blocks won, bidding for one", 38: "Lead blocks won, bidding for two",
             39: "Lead surplus, bidding for one ($)", 40: "Lead surplus, bidding for two ($)",
             41: "Lead bids for two (demand reduction decides)", 45: "Clearing price per block ($)",
             46: "Blocks sold", 47: "Gross revenue ($)", 48: "Implied $/MHz-pop", 49: "Lowest winning value ($)",
             50: "Blocks won by D2D bidders", 51: "Winning class", 52: "Every winner's value ≥ price",
             53: "Label"})
put(ws, "A13", "Calculation", BOLD)
for r, lab in calc.items():
    put(ws, f"A{r}", lab, BOLD if r in (45, 47) else None)
B, MH, POP, AV, RES = INP["blocks"], INP["mhz"], INP["pop"], INP["avail"], INP["reserve"]
for j, s in enumerate(SC):
    c = get_column_letter(2 + j)
    hdr(ws, 4, [s[0]], col=2 + j)
    for k, v in enumerate(s[1:], 5):
        put(ws, f"{c}{k}", v, BLUE, wrap=(k == 5))
    look = lambda use: f"=INDEX({TABLE},MATCH({use},{UC},0),MATCH({c}6,{CASES},0))"
    put(ws, f"{c}14", look(f"{c}7"), fmt=PMP)
    put(ws, f"{c}15", look(f"{c}8"), fmt=PMP)
    put(ws, f"{c}16", f"={c}14*{MH}*{POP}*{AV}*{MULT['Carrier']}", fmt=USD)
    put(ws, f"{c}17", f"={c}15*{MH}*{POP}*{AV}*{MULT['D2D']}", fmt=USD)
    put(ws, f"{c}18", f"={c}17*(1+{INP['adj']})", fmt=USD)
    for k in range(6):
        put(ws, f"{c}{19 + k}", f"=IF({c}9>={k + 1},{c}{18 if k == 0 else 17},0)", fmt=USD)
        put(ws, f"{c}{25 + k}", f"=IF({c}10>={k + 1},{c}16,0)", fmt=USD)
    put(ws, f"{c}31", f"={c}19*{c}11*{INP['spx2']}", fmt=USD)
    put(ws, f"{c}32", f'=COUNTIF({c}19:{c}30,">0")', fmt=INT)
    put(ws, f"{c}33", f'=COUNTIF({c}19:{c}31,">0")', fmt=INT)
    put(ws, f"{c}34", f"=IF({c}32>{B},MAX(LARGE({c}19:{c}30,{B}+1),{RES}),{RES})", fmt=USD)
    put(ws, f"{c}35", f"=IF({c}33>{B},MAX(LARGE({c}19:{c}31,{B}+1),{RES}),{RES})", fmt=USD)
    put(ws, f"{c}36", f'=COUNTIF({c}20:{c}30,">"&{c}19)', fmt=INT)
    put(ws, f"{c}37", f"=IF({c}19>0,IF({c}36>={B},0,1),0)", fmt=INT)
    put(ws, f"{c}38", f'=IF(AND({c}19>0,{c}11=1),IF({c}36<{B},1,0)+IF(AND({c}31>0,COUNTIF({c}20:{c}30,">"&{c}31)<={B}-2),1,0),0)', fmt=INT)
    put(ws, f"{c}39", f"={c}37*({c}19-{c}34)", fmt=USD)
    put(ws, f"{c}40", f"={c}38*({c}31-{c}35)+MIN({c}38,1)*({c}19-{c}31)", fmt=USD)
    put(ws, f"{c}41", f"=IF(AND({c}11=1,{c}40>{c}39),1,0)", fmt=INT)
    put(ws, f"{c}45", f"=IF({c}41=1,{c}35,{c}34)", BOLD, fmt=USD)
    put(ws, f"{c}46", f"=MIN({B},IF({c}41=1,{c}33,{c}32))", fmt=INT)
    put(ws, f"{c}47", f"={c}45*{c}46", BOLD, fmt=USD)
    put(ws, f"{c}48", f"=IF({c}46>0,{c}47/({c}46*{MH}*{POP}),0)", fmt=PMP)
    put(ws, f"{c}49", f"=IFERROR(IF({c}41=1,LARGE({c}19:{c}31,{B}),LARGE({c}19:{c}30,{B})),0)", fmt=USD)
    put(ws, f"{c}50", f"=MIN({c}46,IF({c}41=1,{c}38,{c}37)+SUMPRODUCT(({c}20:{c}24>={c}49)*({c}20:{c}24>0)))",
        fmt=INT)
    put(ws, f"{c}51", f'=IF({c}46=0,"None",IF({c}50>={c}46,"D2D",IF({c}50=0,"Terrestrial","Split")))')
    put(ws, f"{c}52", f"=OR({c}46=0,{c}49>={c}45)")
    put(ws, f"{c}53", LABEL, MARK, wrap=True)
    ws.column_dimensions[c].width = 16
ws.row_dimensions[5].height = 75
ws.row_dimensions[53].height = 30
for r in (19, 31):
    ws[f"A{r}"].fill = GREY
note(ws, "A55", "Pricing rule: each bidder wants one 10 MHz block; the lead D2D bidder may want two. The uniform "
     "clock price stops at the highest losing unit bid. Demand reduction: the lead bids for two blocks only if that "
     "leaves it more surplus than bidding for one. Unit bid = benchmark $/MHz-pop × 10 MHz × 2020 population × "
     "availability × class multiplier (× 1 + adjacency premium for the lead D2D bidder). Up to six bidders per "
     "class.", "J55", 60)
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
rev, d2d_sets, draws = [], 0, []
for _ in range(N):
    carriers = [tul_base * math.exp(rng.gauss(0, sigma)) for _ in range(4)]  # four terrestrial bidders
    d2d = [rng.uniform(spx113, sdl_base) for _ in range(3)]  # three D2D bidders
    vals = sorted(carriers + d2d, reverse=True)
    price = vals[2]
    if price in d2d:
        d2d_sets += 1
    rev.append(2 * price * 10 * pop20)
    draws.append(carriers + d2d + [price, "D2D" if price in d2d else "Carrier", 2 * price * 10 * pop20])
if MC_OUT:
    MC_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(MC_OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["draw"] + [f"terrestrial_{k}_usd_per_mhz_pop" for k in range(1, 5)]
                   + [f"d2d_{k}_usd_per_mhz_pop" for k in range(1, 4)]
                   + ["clearing_price_usd_per_mhz_pop", "price_set_by", "gross_revenue_usd"])
        for k, d in enumerate(draws, 1):
            w.writerow([k] + d)
rev.sort()
pct = lambda p: rev[int(p * (N - 1))]

ws = sheet("MonteCarlo", "Monte Carlo of the pricing rule (illustrative)", [58, 18, 70])
put(ws, "A3", "Values below come from scripts/build_workbook.py (seed 1675, 10,000 draws; every draw is in data/csv/monte_carlo_draws.csv). They are pasted "
    "values, not live formulas; rerun the script after changing assumptions.", wrap=True)
ws.merge_cells("A3:C3")
ws.row_dimensions[3].height = 30
hdr(ws, 5, ["Item", "Value", "Note"])
mc = [
    ("Terrestrial value: TUL base × lognormal", tul_base, PMP, "Four terrestrial bidders"),
    ("Carrier spread (σ of log price relative to auction average)", sigma, RAT,
     "From Auction 97 paired prices of winners that spent over $1B"),
    ("D2D value: uniform, low end ($/MHz-pop)", spx113, PMP, "Three D2D bidders; low end is SpaceX's Auction 113 B1 price"),
    ("D2D value: uniform, high end ($/MHz-pop)", sdl_base, PMP, "Grain prior market price"),
    ("Draws", N, INT, "Each bidder bids for one block (demand reduction). Bidder-count sweep in analysis.py."),
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

# ======================================================== FNPRM
ws = sheet("FNPRM", "FNPRM proposals used (FCC 26-70, WT Docket No. 26-284)", [46, 46, 26, 20])
hdr(ws, 4, ["Proposal", "Model input it drives", "Source", "Paragraph (adopted text)"])
fn = [("Two unpaired 10 MHz blocks (1675-1685, 1685-1695 MHz); a 5 MHz block at 2020-2025 MHz",
       "Inputs: block size, number of blocks. 2020-2025 MHz out of scope", "48"),
      ("Alternative band plans", "Not modeled", "54-55"),
      ("Unpaired; licensee chooses FDD or TDD, uplink or downlink", "Use cases TUL, TDL, SUL, SDL", "52"),
      ("Co-primary fixed and mobile; secondary MSS for domestic SCS", "D2D bidder class; S8 lease-only", "30-34"),
      ("License area: nationwide, REAG, or PEA, or different sizes by block", "License_Area tab", "43-44, 51"),
      ("Bundling and all-or-nothing nationwide package bids to reduce exposure risk",
       "License_Area rows 72-91", "75-78"),
      ("15-year license term", "Income cross-check in analysis.py", "56"),
      ("Performance requirements", "Not modeled", "57-68"),
      ("Small-business and rural bidding credits", "Not modeled (gross revenue only)", "79-81"),
      ("Coordination zones around four NOAA DCS sites", "Zone analysis in analysis.py", "101-102"),
      ("FCC's own estimate: $21.2B for 25 MHz at the Auction 113 average ($2.53/MHz-pop), ±50%",
       "Compared in the working paper", "App. C, para. 4")]
for i, (pp, m, para) in enumerate(fn, 5):
    put(ws, f"A{i}", pp, wrap=True)
    put(ws, f"B{i}", m, wrap=True)
    put(ws, f"C{i}", "FCC 26-70 (adopted Oct. 29, 2026)", wrap=True)
    put(ws, f"D{i}", para, BLUE)


# ======================================================== PEA
pr0, pr1 = 5, 5 + len(PEAS)  # last row is Alaska + Hawaii
ws = sheet("PEA", "PEA licensing: values by market", [9, 30, 13, 13, 11, 11, 11, 14, 10, 11, 14, 10, 26])
put(ws, "A3", "Source: FCC PRS Auction 110 market file (406 contiguous-U.S. PEAs, 2010 population). 2020 "
    "population scales each PEA to the 2020 contiguous total; Alaska and Hawaii are one combined row.", wrap=True)
ws.merge_cells("A3:M3")
ws.row_dimensions[3].height = 30
hdr(ws, 4, ["PEA", "Name", "Population (2010)", "Population (2020, scaled)", "pop^slope",
            "Carrier $/MHz-pop", "Uplink price $/MHz-pop", "Uplink revenue ($)", "Uplink winner",
            "Downlink price $/MHz-pop", "Downlink revenue ($)", "Downlink winner", "NOAA DCS site (county)"])
SITES = {"PEA005": "Suitland, MD (Prince George's)", "PEA147": "Wallops, VA (Accomack)",
         "PEA114": "Fairmont, WV (Marion)", "PEA286": "Sioux Falls, SD (Minnehaha)"}  # FCC DA 14-759 App. B
LA = lambda r: f"License_Area!$B${r}"
scale = f"(({INP['pop']}-{INP['akhi']})/SUM($C${pr0}:$C${pr1 - 1}))"
for i, r in enumerate(PEAS, pr0):
    put(ws, f"A{i}", r["market"], BLUE)
    put(ws, f"B{i}", r["market_name"], BLUE)
    put(ws, f"C{i}", int(r["population"]), fmt=INT)
    put(ws, f"D{i}", f"=C{i}*{scale}", fmt=INT)
    if r["market"] in SITES:
        put(ws, f"M{i}", SITES[r["market"]], BLUE, fill=YELLOW)
i = pr1
put(ws, f"A{i}", "AK+HI", BLUE)
put(ws, f"B{i}", "Alaska and Hawaii (combined)", BLUE)
put(ws, f"C{i}", f"=D{i}/{scale}", fmt=INT)
put(ws, f"D{i}", f"={INP['akhi']}", fmt=INT)
for i in range(pr0, pr1 + 1):
    put(ws, f"E{i}", f"=C{i}^{INP['slope']}", fmt='0.00')
    put(ws, f"F{i}", f"={LA(6)}*{LA(15)}*E{i}", fmt=PMP)
    for pc, rc, wc, d in (("G", "H", "I", LA(13)), ("J", "K", "L", LA(14))):
        nd, nc, bb = LA(17), LA(16), INP["blocks"]
        put(ws, f"{pc}{i}", f"=IF({d}>F{i},IF({nd}>={bb}+1,{d},IF({nd}+{nc}>={bb}+1,F{i},0)),"
                            f"IF({nc}>={bb}+1,F{i},IF({nc}+{nd}>={bb}+1,{d},0)))", fmt=PMP)
        put(ws, f"{rc}{i}", f"={pc}{i}*{INP['blocks']}*{INP['mhz']}*D{i}*{INP['avail']}", fmt=USD)
        put(ws, f"{wc}{i}", f'=IF({d}>F{i},"D2D","Carrier")')
ws.freeze_panes = "C5"
PR = lambda col: f"PEA!${col}${pr0}:${col}${pr1}"

# ======================================================== License_Area
ws = sheet("License_Area", "Nationwide vs PEA licensing: UE uplink and D2D downlink", [58, 17, 17, 17, 14, 16, 14])
put(ws, "A3", LABEL + ". Bidder counts as in S1 (uplink) and S2 (downlink).", MARK)
hdr(ws, 4, ["Input", "Value", "Note"])
la = [
    (5, "Carrier base $/MHz-pop (TUL)", "=Benchmarks!$C$6", PMP, "National average; PEA values spread around it"),
    (6, "Carrier base used for PEA curve", "=B5", PMP, ""),
    (7, "D2D uplink, national $/MHz-pop (SUL base)", "=Benchmarks!$C$7", PMP, "EchoStar national price"),
    (8, "D2D downlink, national $/MHz-pop (SDL base)", "=Benchmarks!$C$8", PMP, "Grain prior market price"),
    (9, "National-portfolio premium", f"={EV['prem']}", '0.00"x"',
     "Lost under PEA licensing: D2D bids revert to market-by-market value"),
    (10, "Apply premium loss under PEA (1 = yes, 0 = no)", 1, INT, "0 tests PEA with no aggregation loss"),
    (11, "Exposure discount", f"={INP['exposure']}", PCT, "Inputs"),
    (12, "Market-size slope", f"={INP['slope']}", RAT, "Inputs; fitted from Auction 97 B1"),
    (13, "D2D uplink bid per PEA $/MHz-pop", "=B7/IF(B10=1,B9,1)*(1-B11)", PMP, ""),
    (14, "D2D downlink bid per PEA $/MHz-pop", "=B8/IF(B10=1,B9,1)*(1-B11)", PMP, ""),
    (15, "Calibration constant k", f"=SUM({PR('D')})/SUMPRODUCT({PR('D')},{PR('E')})", '0.000000E+0',
     "Keeps the population-weighted average carrier value at the national base"),
    (16, "Terrestrial bidders per PEA", "=Scenarios!$B$10", INT, "As S1"),
    (17, "D2D bidders per PEA", "=Scenarios!$B$9", INT, "As S1"),
]
for r, lab, val, fmt, nt in la:
    put(ws, f"A{r}", lab)
    put(ws, f"B{r}", val, fmt=fmt, fill=YELLOW if r in (10,) else None)
    put(ws, f"C{r}", nt)

hdr(ws, 19, ["Results (before federal coordination, upper bound)", "Nationwide", "PEA", "PEA − nationwide",
             "Change", "Population won by D2D (PEA)", "PEAs won by D2D"])
res = [
    (20, "UE uplink (carriers at TUL, D2D at SUL)", "=Scenarios!$B$47", f"=SUM({PR('H')})", "I"),
    (21, "D2D downlink (carriers at TUL, D2D at SDL)", "=Scenarios!$C$47", f"=SUM({PR('K')})", "L"),
]
for r, lab, nat, pea, wcol in res:
    put(ws, f"A{r}", lab, BOLD)
    put(ws, f"B{r}", nat, fmt=USDB)
    put(ws, f"C{r}", pea, fmt=USDB)
    put(ws, f"D{r}", f"=C{r}-B{r}", fmt=USDB)
    put(ws, f"E{r}", f"=C{r}/B{r}-1", fmt=PCT)
    put(ws, f"F{r}", f'=SUMIFS({PR("D")},{PR(wcol)},"D2D")/SUM({PR("D")})', fmt=PCT)
    put(ws, f"G{r}", f'=COUNTIF({PR(wcol)},"D2D")', fmt=INT)

put(ws, "A23", "What drives the difference", BOLD)
note(ws, "A24", "Under PEA licensing each market goes to whoever values it most. Carriers paid far more per pop in "
     "big markets in Auction 97, so they win the largest PEAs; D2D bidders win most others. That sorting raises "
     "revenue. Against it, D2D bidders lose the national-portfolio premium and face exposure risk, which "
     "lowers their PEA bids. Which effect wins depends on the slope, the premium, and the exposure discount.",
     "G24", 75)

# Sensitivity: exposure
put(ws, "A26", "PEA revenue by exposure discount (premium loss applied)", BOLD)
hdr(ws, 27, ["Exposure discount", "UE uplink, PEA", "D2D downlink, PEA", "Uplink vs nationwide",
             "Downlink vs nationwide"])
def pea_sum(dexpr, slope_expr=None):
    if slope_expr is None:
        cm = PR("F")
    else:
        ks = f"(SUM({PR('D')})/SUMPRODUCT({PR('D')},{PR('C')}^{slope_expr}))"
        cm = f"($B$6*{ks}*{PR('C')}^{slope_expr})"
    return (f"{INP['blocks']}*{INP['mhz']}*{INP['avail']}*SUMPRODUCT({PR('D')},"
            f"(({dexpr})>{cm})*({dexpr})+(({dexpr})<={cm})*{cm})")
for k_, e in enumerate([0, 0.1, 0.2, 0.3]):
    r = 28 + k_
    put(ws, f"A{r}", e, fmt=PCT)
    put(ws, f"B{r}", "=" + pea_sum(f"$B$7/IF($B$10=1,$B$9,1)*(1-A{r})"), fmt=USDB)
    put(ws, f"C{r}", "=" + pea_sum(f"$B$8/IF($B$10=1,$B$9,1)*(1-A{r})"), fmt=USDB)
    put(ws, f"D{r}", f"=B{r}-$B$20", fmt=USDB)
    put(ws, f"E{r}", f"=C{r}-$B$21", fmt=USDB)

# Sensitivity: slope
put(ws, "A33", "PEA revenue by market-size slope (exposure as on Inputs)", BOLD)
hdr(ws, 34, ["Slope", "UE uplink, PEA", "D2D downlink, PEA", "Uplink vs nationwide", "Downlink vs nationwide"])
for k_, (lab, sv) in enumerate([("0 (flat $/pop)", 0), ("Half the fitted slope", "=Evidence!$B$35/2"),
                                ("Fitted (Auction 97 B1)", "=Evidence!$B$35")]):
    r = 35 + k_
    put(ws, f"A{r}", sv, fmt=RAT)
    put(ws, f"F{r}", lab)
    put(ws, f"B{r}", "=" + pea_sum("$B$13", f"A{r}"), fmt=USDB)
    put(ws, f"C{r}", "=" + pea_sum("$B$14", f"A{r}"), fmt=USDB)
    put(ws, f"D{r}", f"=B{r}-$B$20", fmt=USDB)
    put(ws, f"E{r}", f"=C{r}-$B$21", fmt=USDB)

# NOAA PEAs
put(ws, "A39", "PEAs with a NOAA DCS receive site (zones modeled in analysis.py)", BOLD)
hdr(ws, 40, ["PEA", "Site", "Population (2020)", "Uplink revenue, PEA", "Share of uplink PEA revenue",
             "Uplink winner"])
for k_, code in enumerate(["PEA005", "PEA147", "PEA114", "PEA286"]):
    r = 41 + k_
    m = f"MATCH(\"{code}\",{PR('A')},0)"
    put(ws, f"A{r}", f"=INDEX({PR('B')},{m})")
    put(ws, f"B{r}", f"=INDEX({PR('M')},{m})")
    put(ws, f"C{r}", f"=INDEX({PR('D')},{m})", fmt=INT)
    put(ws, f"D{r}", f"=INDEX({PR('H')},{m})", fmt=USDB)
    put(ws, f"E{r}", f"=D{r}/$C$20", fmt=PCT)
    put(ws, f"F{r}", f"=INDEX({PR('I')},{m})")
put(ws, "A45", "Total, four PEAs", BOLD)
put(ws, "C45", "=SUM(C41:C44)", fmt=INT)
put(ws, "D45", "=SUM(D41:D44)", fmt=USDB)
put(ws, "E45", "=SUM(E41:E44)", fmt=PCT)
note(ws, "A46", "Under PEA licensing, coordination limits would mostly hit these markets, and bidders could price "
     "them separately. Under a nationwide license, the same limits are spread across one price. The "
     "Baltimore-Washington PEA alone is a large share of uplink value.", "G46", 45)

ch = BarChart()
ch.type = "col"
ch.grouping = "clustered"
ch.title = "Nationwide vs PEA (before coordination, upper bound)"
ch.y_axis.numFmt = '$#,##0.0,,,"B"'
ch.add_data(Reference(ws, min_col=2, max_col=3, min_row=19, max_row=21), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=20, max_row=21))
ch.height, ch.width = 8, 18
ws.add_chart(ch, "A49")

# ---- Package bidding: PEA licenses plus all-or-nothing nationwide package bids
put(ws, "A72", "PEA licenses plus nationwide package bids (FNPRM option)", BOLD)
note(ws, "A73", "Each block is sold either PEA by PEA or as one nationwide package. A package wins only if it beats "
     "the sum of the per-PEA bids for that block, and it pays at least that sum (core pricing). D2D bidders "
     "bid packages at their national value, so they carry no exposure risk and keep the national premium. "
     "Carriers bid PEA by PEA.", "G73", 60)
hdr(ws, 74, ["Item", "UE uplink", "D2D downlink", "Note"])
pk = [
    (75, "D2D package value per block ($)", f"=$B$7*{INP['mhz']}*{INP['pop']}*{INP['avail']}",
     f"=$B$8*{INP['mhz']}*{INP['pop']}*{INP['avail']}", "National $/MHz-pop, premium kept"),
    (76, "Competing per-PEA bids per block, no exposure ($)", f"=$B$28/{INP['blocks']}",
     f"=$C$28/{INP['blocks']}", "PEA-by-PEA revenue at 0% exposure, per block"),
    (77, "Enough D2D bidders to compete for packages", f"=IF($B$17>={INP['blocks']}+1,1,0)",
     f"=IF($B$17>={INP['blocks']}+1,1,0)", "Needs one more D2D bidder than blocks"),
    (78, "Revenue with package bids ($)", f"={INP['blocks']}*MAX(B75*B77,B76)",
     f"={INP['blocks']}*MAX(C75*C77,C76)", "Before federal coordination, upper bound"),
    (79, "How the blocks sell", '=IF(B75*B77>B76,"Nationwide packages (D2D)","PEA by PEA")',
     '=IF(C75*C77>C76,"Nationwide packages (D2D)","PEA by PEA")', ""),
]
for r, lab, u, d, nt in pk:
    put(ws, f"A{r}", lab, BOLD if r == 78 else None)
    put(ws, f"B{r}", u, fmt=None if r == 79 else (INT if r == 77 else USDB))
    put(ws, f"C{r}", d, fmt=None if r == 79 else (INT if r == 77 else USDB))
    put(ws, f"D{r}", nt)

hdr(ws, 81, ["Comparison (before federal coordination, upper bound)", "Nationwide", "PEA only",
             "PEA + packages", "Packages vs nationwide", "Packages vs PEA only"])
for k_, (lab, nat, peao, pk_) in enumerate([("UE uplink", "$B$20", "$C$20", "$B$78"),
                                            ("D2D downlink", "$B$21", "$C$21", "$C$78")]):
    r = 82 + k_
    put(ws, f"A{r}", lab, BOLD)
    put(ws, f"B{r}", f"={nat}", fmt=USDB)
    put(ws, f"C{r}", f"={peao}", fmt=USDB)
    put(ws, f"D{r}", f"={pk_}", fmt=USDB)
    put(ws, f"E{r}", f"=D{r}-B{r}", fmt=USDB)
    put(ws, f"F{r}", f"=D{r}-C{r}", fmt=USDB)

put(ws, "A85", "Package-bid revenue by market-size slope", BOLD)
hdr(ws, 86, ["Slope", "Uplink PEA at 0% exposure", "Downlink PEA at 0% exposure", "Uplink with packages",
             "Downlink with packages", "Uplink: nationwide", "Downlink: nationwide"])
for k_, sv in enumerate(["=0", "=Evidence!$B$35/2", "=Evidence!$B$35"]):
    r = 87 + k_
    put(ws, f"A{r}", sv, fmt=RAT)
    put(ws, f"B{r}", "=" + pea_sum("$B$7/IF($B$10=1,$B$9,1)", f"A{r}"), fmt=USDB)
    put(ws, f"C{r}", "=" + pea_sum("$B$8/IF($B$10=1,$B$9,1)", f"A{r}"), fmt=USDB)
    put(ws, f"D{r}", f"={INP['blocks']}*MAX($B$75*$B$77,B{r}/{INP['blocks']})", fmt=USDB)
    put(ws, f"E{r}", f"={INP['blocks']}*MAX($C$75*$C$77,C{r}/{INP['blocks']})", fmt=USDB)
    put(ws, f"F{r}", "=$B$20", fmt=USDB)
    put(ws, f"G{r}", "=$B$21", fmt=USDB)
note(ws, "A91", "Packages remove exposure risk, so this table ignores the exposure discount. With at least three "
     "D2D bidders, revenue is the larger of the nationwide and PEA-only results. Caveat: in real package "
     "auctions, many small bidders must jointly outbid a package (the threshold problem), which can let "
     "packages win too cheaply.", "G91", 60)

# ======================================================== Summary
ws = sheet("Summary", "1675–1695 MHz auction revenue, v0.5", [46, 17, 14, 30, 40])
put(ws, "A3", LABEL + ". Not for release.", MARK)
hdr(ws, 5, ["Measure (before federal coordination, upper bound)", "Gross revenue", "$/MHz-pop", "Scenario",
            "Meaning"])
inc = SCR(12)
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
     f"={B}*{MH}*{POP}*{AV}*MAX(Scenarios!B14,Transactions!B5/(Transactions!C5*{EV['dishall']}*{POP}))",
     f"=MAX(Scenarios!B14,Transactions!B5/(Transactions!C5*{EV['dishall']}*{POP}))", "S1 variant",
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
    'terrestrial bidders set it: "&TEXT(B18,"$0.00,,,""B""")&". A third D2D bidder raises it to "&TEXT(B19,"$0.00,,,""B""")'
    '&" at the uplink evidence, or "&TEXT(C19,"$0.00,,,""B""")&" if D2D bidders value the band as downlink."',
    BLACK, wrap=True)
ws.merge_cells("A12:E12")
ws.row_dimensions[12].height = 48
put(ws, "A14", "Revenue by number of independent D2D bidders (before federal coordination, upper bound)", BOLD)
hdr(ws, 15, ["Independent D2D bidders", "D2D at uplink value", "D2D at downlink value"])
for k in range(5):
    r = 16 + k
    put(ws, f"A{r}", k, BLACK, fmt=INT)
    for col, d2dcell in (("B", "Scenarios!$B$17"), ("C", "Scenarios!$C$17")):
        put(ws, f"{col}{r}", f"={B}*IF(AND($A{r}>={B}+1,{d2dcell}>Scenarios!$B$16),{d2dcell},Scenarios!$B$16)",
            fmt=USDB)
put(ws, "A21", "Assumes three or more terrestrial bidders at the terrestrial uplink base value.")
hdr(ws, 23, ["Scenario (before federal coordination, upper bound)", "Gross revenue", "In range",
             "Winning class"])
for j, s in enumerate(SC):
    r, c = 24 + j, get_column_letter(2 + j)
    put(ws, f"A{r}", f"=Scenarios!{c}4")
    put(ws, f"B{r}", f"=Scenarios!{c}47", fmt=USDB)
    put(ws, f"C{r}", f"=Scenarios!{c}12")
    put(ws, f"D{r}", f"=Scenarios!{c}51")
put(ws, "A34", "Checks status:", BOLD)
hdr(ws, 37, ["License area (before federal coordination, upper bound)", "Nationwide", "PEA only",
             "PEA + packages"])
for k_, r_ in enumerate([82, 83]):
    put(ws, f"A{38 + k_}", f"=License_Area!A{r_}")
    put(ws, f"B{38 + k_}", f"=License_Area!B{r_}", fmt=USDB)
    put(ws, f"C{38 + k_}", f"=License_Area!C{r_}", fmt=USDB)
    put(ws, f"D{38 + k_}", f"=License_Area!D{r_}", fmt=USDB)
put(ws, "A35", "Gross bids only. Excluded here: NOAA coordination zones (see analysis.py), REAG licenses, "
    "2020-2025 MHz, bidding credits, timing, buildout.", wrap=True)
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
ws.add_chart(ch, "A42")

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
     P(f"ROUND(Scenarios!I47-{B}*Scenarios!I16,0)=0"), "Second computation path"),
    ("Bidder-count table never decreases as D2D bidders are added",
     P("AND(SUMPRODUCT((Summary!B17:B20<Summary!B16:B19)*1)=0,SUMPRODUCT((Summary!C17:C20<Summary!C16:C19)*1)=0)"),
     ""),
    ("Bidder-count table at 3 and 2 D2D bidders matches S2 and S3",
     P("AND(ROUND(Summary!C19-Scenarios!C47,0)=0,ROUND(Summary!C18-Scenarios!D47,0)=0)"),
     "Two independent computation paths; needs default multipliers"),
    ("Every dollar table on Summary and License_Area carries the upper-bound label",
     P('AND(COUNTIF(Summary!A3:E37,"*upper bound*")>=5,COUNTIF(License_Area!A3:A19,"*upper bound*")>=2)'),
     "Fails if a table header loses the label"),
    ("PEA 2020 population sums to the U.S. 2020 Census total",
     P(f"ROUND(SUM(PEA!D5:D{4 + len(PEAS) + 1})-{INP['pop']},0)=0"), "Fails if scaling or the AK/HI row is wrong"),
    ("Carrier PEA values average to the national carrier base (population-weighted)",
     P(f"ABS(SUMPRODUCT(PEA!D5:D{4 + len(PEAS) + 1},PEA!F5:F{4 + len(PEAS) + 1})/{INP['pop']}/Benchmarks!C6-1)<1E-9"),
     "Fails if calibration is off"),
    ("Fitted market-size slope matches an independent Python fit (0.6498) within 0.005",
     P("ABS(Evidence!B35-0.6498)<=0.005"), "Python fit run before the workbook was built"),
    ("Slope table at the fitted slope reproduces the main PEA results",
     P("AND(ABS(License_Area!B37-License_Area!C20)<1,ABS(License_Area!C37-License_Area!C21)<1)"),
     "Two computation paths; holds when Inputs slope = fitted"),
    ("Exposure table at 0% equals the main PEA results when exposure is 0",
     P(f"OR({INP['exposure']}<>0,AND(ABS(License_Area!B28-License_Area!C20)<1,ABS(License_Area!C28-License_Area!C21)<1))"),
     "Two computation paths"),
    ("PEA revenue is never below every PEA sold at the carrier value",
     P(f"AND(License_Area!C20>=SUMPRODUCT(PEA!D5:D{4 + len(PEAS) + 1},PEA!F5:F{4 + len(PEAS) + 1})*{INP['blocks']}*{INP['mhz']}*{INP['avail']}-1,"
       f"License_Area!C21>=SUMPRODUCT(PEA!D5:D{4 + len(PEAS) + 1},PEA!F5:F{4 + len(PEAS) + 1})*{INP['blocks']}*{INP['mhz']}*{INP['avail']}-1)"),
     "Carriers bid in every PEA"),
    ("Package value per block × blocks equals nationwide revenue (S1 and S2)",
     P(f"AND(ABS({INP['blocks']}*License_Area!B75-Scenarios!B47)<1,ABS({INP['blocks']}*License_Area!C75-Scenarios!C47)<1)"),
     "Two computation paths; needs default multipliers and D2D above carrier value"),
    ("Package revenue is never below the nationwide or PEA-only (0% exposure) result",
     P("AND(License_Area!B78>=License_Area!B20-1,License_Area!B78>=License_Area!B28-1,"
       "License_Area!C78>=License_Area!C21-1,License_Area!C78>=License_Area!C28-1)"), "Needs three or more D2D bidders"),
    ("Slope table for packages at the fitted slope reproduces the main package result",
     P("AND(ABS(License_Area!D89-License_Area!B78)<1,ABS(License_Area!E89-License_Area!C78)<1)"), "Two computation paths"),
    ("Holdings-share net of resold licenses is no larger than gross 2015 share",
     P(f"{EV['dish']}<=Evidence!$B$19+Evidence!$B$20"), "Resold licenses can only reduce holdings"),
    ("Transaction terms verified in primary filings",
     '=IF(COUNTIF(Transactions!H5:H10,"PENDING")=0,"PASS","PENDING")', ""),
    ("FNPRM inputs cited to adopted paragraphs", '=IF(COUNTIF(FNPRM!D5:D15,"PENDING")=0,"PASS","PENDING")', ""),
    ("Downlink benchmarks ordered: 1670-1675 lease ≤ average ≤ Qualcomm 700 MHz",
     P("AND(Benchmarks!B5<=Benchmarks!C5,Benchmarks!C5<=Benchmarks!D5)"), "Two comparables"),
]
for i, (lab, fml, d) in enumerate(checks, 5):
    put(ws, f"A{i}", lab, wrap=True)
    put(ws, f"B{i}", fml, BOLD)
    put(ws, f"C{i}", d, wrap=True)
last = 4 + len(checks)
guards = [
    ("Every winner's value ≥ the price it pays", f'=IF(COUNTIF({SCR(52)},FALSE)=0,"OK","CHECK")',
     "Holds by construction unless a reserve price is set"),
    ("Expected outcome: S4 equals S3 (demand reduction; the lead D2D bidder bids for one block)",
     '=IF(ROUND(Scenarios!E47-Scenarios!D47,0)=0,"OK","CHANGED")',
     "Not a correctness test: shows CHANGED if inputs make two blocks worth bidding for"),
    ("Headline is before coordination (availability 100%)", '=IF(Coordination!B5=1,"OK","CHANGED")',
     "Zone results are in analysis.py"),
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
ws = sheet("README", "1675–1695 MHz auction valuation workbook, v0.5", [120])
lines = [
    ("What changed in v0.5", BOLD),
    ("• Bidders are counts by class (D2D, terrestrial), not a named list. Base case: three D2D, four terrestrial.",
     None),
    ("• Terrestrial downlink restored with two unpaired-downlink comparables: Qualcomm 700 MHz D and E Blocks "
     "(FCC 11-188) and the 1670-1675 MHz lease, capitalized.", None),
    ("• FNPRM tab cites the adopted FNPRM (FCC 26-70) by paragraph. Gross revenue only (Revenue_Defs removed).",
     None),
    ("• Zones, bidder-count grid, backtest, sharing calibration, and sensitivities: scripts/analysis.py.", None),
    ("", None),
    ("What changed in v0.4 and earlier", BOLD),
    ("• v0.4: PEA licenses plus all-or-nothing nationwide package bids. v0.3: nationwide vs PEA licensing. "
     "v0.2: raw per-license FCC data for Auctions 97 and 113.", None),
    ("", None),
    ("Population basis", BOLD),
    ("Benchmarks use each source's own population basis; values apply them to the 2020 Census population. "
     "The matched-pair test (Evidence) found 2026 $/pop within about 1% of 2015 $/pop for the same licenses.",
     None),
    ("", None),
    ("Every dollar figure in this workbook is: " + LABEL + ".", MARK),
    ("", None),
    ("Color key: blue = hardcoded input or raw data; black = formula; green = link to another tab; "
     "yellow = assumption to verify.", None),
    ("Repository: github.com/nicklasorte/1675MHz_auction_revenue. Run ./reproduce.sh to rebuild from FCC data.", None),
]
for i, (t, fnt) in enumerate(lines, 4):
    put(ws, f"A{i}", t, fnt or BLACK, wrap=True)

order_tabs = ["Summary", "README", "Scenarios", "License_Area", "PEA", "Bidders", "Benchmarks", "Evidence",
              "Transactions",
              "MonteCarlo", "Inputs", "FNPRM", "Coordination", "Checks", "Raw_A97", "Raw_A113"]
wb._sheets = [wb[n] for n in order_tabs]
wb.active = 0
wb.calculation.fullCalcOnLoad = True  # Excel and LibreOffice compute every formula on open
wb.save(OUT)
print(MCPY)
