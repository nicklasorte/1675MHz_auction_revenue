"""Export every dataset used in the calculation to CSV files.

Usage: python scripts/export_csvs.py <processed_dir> <pea_market.csv> <recalculated.xlsx> <out_dir>

Inputs (FCC data, filtered to what the model uses) come from the parsed per-license CSVs and the
FCC PEA file. Calculated results come from the recalculated workbook, so the CSVs match it exactly.
Run ./reproduce.sh instead of calling this directly. data/csv/README.md describes each file.
"""
import csv
import math
import sys
from pathlib import Path

from openpyxl import load_workbook

PROC, PEA_FILE, XLSX, OUT = (Path(a) for a in sys.argv[1:5])
OUT.mkdir(parents=True, exist_ok=True)

A97 = list(csv.DictReader(open(PROC / "a97_licenses.csv")))
A113 = list(csv.DictReader(open(PROC / "a113_licenses.csv")))
PEAS = list(csv.DictReader(open(PEA_FILE, encoding="utf-8-sig")))
WB = load_workbook(XLSX, data_only=True)

ECHOSTAR_SELLERS = ("Northstar Wireless, LLC", "SNR Wireless LicenseCo, LLC")
NOAA_PEAS = {"PEA005": "Suitland, MD", "PEA147": "Wallops, VA",  # counties checked in FCC DA 14-759 App. B
             "PEA114": "Fairmont, WV", "PEA286": "Sioux Falls, SD"}
written = []


def num(s):
    return float(s) if s not in ("", None) else None


def write(name, header, rows):
    with open(OUT / name, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    written.append((name, len(rows)))


def val(sheet, ref):
    return WB[sheet][ref].value


# Auctions 107 and 110 (mid-band cross-check): every license, as parsed from the FCC downloads.
for aid in (107, 110):
    src_rows = list(csv.reader(open(PROC / f"a{aid}_licenses.csv")))
    write(f"a{aid}_licenses.csv", src_rows[0], src_rows[1:])

# ------------------------------------------------------------------ Inputs: FCC data, filtered
resold = {"AW-" + x["license"] for x in A113}

# Auction 97 unpaired 1695-1710 MHz licenses (A1, B1): terrestrial and satellite uplink benchmarks,
# market-size fit, and EchoStar holdings.
rows = []
for x in A97:
    if x["block"] not in ("A1", "B1"):
        continue
    pop, gross, mhz = int(x["population_2010"]), float(x["gross_bid"]), int(x["mhz"])
    sold = x["sold"] == "Y"
    pmp = gross / (mhz * pop) if sold and pop else None
    rows.append([x["license"], x["market"], x["market_name"], x["block"], x["frequencies"], mhz, pop,
                 x["sold"], x["bidder"], gross, float(x["net_bid"]), pmp,
                 "Y" if x["license"] in resold else "N",
                 "Y" if sold and x["bidder"] in ECHOSTAR_SELLERS and x["license"] not in resold else "N",
                 math.log(pop) if pmp and x["block"] == "B1" else None,
                 math.log(pmp) if pmp and x["block"] == "B1" else None])
write("a97_unpaired_licenses.csv",
      ["license", "market", "market_name", "block", "frequencies", "mhz", "population_2010", "sold",
       "winning_bidder", "gross_bid_usd", "net_bid_usd", "usd_per_mhz_pop", "resold_in_auction113",
       "sold_to_spacex_via_echostar", "b1_ln_population", "b1_ln_usd_per_mhz_pop"], rows)

# Auction 97 paired licenses (G, H, I, J): paired price, unpaired discount, Monte Carlo spread.
rows = [[x["license"], x["market"], x["market_name"], x["block"], x["frequencies"], int(x["mhz"]),
         int(x["population_2010"]), x["sold"], x["bidder"], float(x["gross_bid"]), float(x["net_bid"]),
         num(x["gross_per_mhz_pop"])]
        for x in A97 if x["block"] in ("G", "H", "I", "J")]
write("a97_paired_licenses.csv",
      ["license", "market", "market_name", "block", "frequencies", "mhz", "population_2010", "sold",
       "winning_bidder", "gross_bid_usd", "net_bid_usd", "usd_per_mhz_pop"], rows)

# Paired spending by bidder: the winners that spent over $1B set the Monte Carlo carrier spread.
agg = {}
for x in A97:
    if x["block"] in ("G", "H", "I", "J") and x["sold"] == "Y" and int(x["population_2010"]) > 0:
        d = agg.setdefault(x["bidder"], [0.0, 0, 0])
        d[0] += float(x["gross_bid"])
        d[1] += int(x["mhz"]) * int(x["population_2010"])
        d[2] += 1
avg = sum(v[0] for v in agg.values()) / sum(v[1] for v in agg.values())
rows = [[b, v[2], v[0], v[1], v[0] / v[1], v[0] / v[1] / avg, "Y" if v[0] > 1e9 else "N"]
        for b, v in sorted(agg.items(), key=lambda t: -t[1][0])]
write("a97_paired_by_bidder.csv",
      ["bidder", "licenses_won", "gross_bid_usd", "mhz_pop", "usd_per_mhz_pop", "ratio_to_auction_average",
       "used_for_monte_carlo_spread"], rows)

# Auction 113: totals check, SpaceX's B1 price, matched-pair test.
rows = [[x["license"], x["market"], x["market_name"], x["block"], int(x["mhz"]), int(x["population"]),
         x["bidder"], x["bidding_credit_type"], float(x["gross_bid"]), float(x["net_bid"]),
         num(x["gross_per_mhz_pop"]), "Y" if x["block"] in ("A1", "B1") else "N"] for x in A113]
write("a113_licenses.csv",
      ["license", "market", "market_name", "block", "mhz", "population", "winning_bidder",
       "bidding_credit_type", "gross_bid_usd", "net_bid_usd", "usd_per_mhz_pop", "unpaired"], rows)

# Licenses sold in both auctions: test that nominal $/pop held flat from 2015 to 2026.
d97 = {x["license"]: x for x in A97}
rows = []
for x in A113:
    y = d97.get("AW-" + x["license"])
    if y and y["sold"] == "Y" and int(y["population_2010"]) > 0 and int(x["population"]) > 0:
        g97, p97, g113, p113 = float(y["gross_bid"]), int(y["population_2010"]), float(x["gross_bid"]), int(x["population"])
        rows.append([x["license"], x["market_name"], x["block"], y["bidder"], g97, p97, g97 / p97,
                     x["bidder"], g113, p113, g113 / p113, (g113 / p113) / (g97 / p97)])
write("matched_pairs_a97_a113.csv",
      ["license", "market_name", "block", "a97_winning_bidder", "a97_gross_bid_usd", "a97_population_2010",
       "a97_usd_per_pop", "a113_winning_bidder", "a113_gross_bid_usd", "a113_population", "a113_usd_per_pop",
       "ratio_2026_to_2015"], rows)

# PEA populations (FCC Auction 110 market file) with the 2020 scaling the model applies.
pea_ws = WB["PEA"]
rows = []
for i in range(5, 5 + len(PEAS) + 1):
    code = pea_ws[f"A{i}"].value
    rows.append([code, pea_ws[f"B{i}"].value, pea_ws[f"C{i}"].value, pea_ws[f"D{i}"].value,
                 NOAA_PEAS.get(code, "")])
write("pea_populations.csv",
      ["pea", "name", "population_2010", "population_2020_scaled", "noaa_dcs_site"], rows)

# ------------------------------------------------------------------ Inputs typed into the workbook
ws = WB["Inputs"]
rows = [[ws[f"A{r}"].value, ws[f"B{r}"].value, ws[f"C{r}"].value]
        for r in range(5, ws.max_row + 1) if ws[f"A{r}"].value]
write("inputs.csv", ["input", "value", "source_or_note"], rows)

ws = WB["Transactions"]
rows = [[ws[f"{c}{r}"].value for c in "ABCDEFGH"] for r in range(5, 11)]
write("transactions.csv",
      ["transaction", "price_usd", "mhz", "population_share_covered", "usd_per_mhz_pop", "payment",
       "source_and_caveats", "primary_source_verified"], rows)

ws = WB["Bidders"]
rows = [[ws[f"{c}{r}"].value for c in "ABC"] for r in range(5, 7)]
write("bidder_classes.csv", ["bidder_class", "value_multiplier", "meaning"], rows)

# ------------------------------------------------------------------ Calculated results
ws = WB["Evidence"]
rows = [[ws[f"A{r}"].value, ws[f"B{r}"].value, ws[f"C{r}"].value]
        for r in range(5, ws.max_row + 1) if ws[f"A{r}"].value and ws[f"B{r}"].value is not None]
write("evidence.csv", ["measure", "value", "what_it_shows"], rows)

ws = WB["Benchmarks"]
rows = [[ws[f"{c}{r}"].value for c in "ABCDE"] for r in range(5, 9)]
write("benchmarks.csv", ["use_case", "low_usd_per_mhz_pop", "base_usd_per_mhz_pop", "high_usd_per_mhz_pop",
                         "basis"], rows)

ws = WB["Scenarios"]
fields = [(4, "scenario"), (5, "description"), (6, "benchmark_case"), (7, "terrestrial_use_case"),
          (8, "d2d_use_case"), (9, "d2d_bidders"), (10, "terrestrial_bidders"),
          (11, "lead_d2d_wants_both_blocks"), (12, "in_summary_range"),
          (14, "terrestrial_usd_per_mhz_pop"), (15, "d2d_usd_per_mhz_pop"), (16, "terrestrial_value_per_block_usd"),
          (17, "d2d_value_per_block_usd"), (41, "lead_bids_for_two"), (45, "clearing_price_per_block_usd"),
          (46, "blocks_sold"), (47, "gross_revenue_usd"), (48, "implied_usd_per_mhz_pop"),
          (50, "blocks_won_by_d2d"), (51, "winning_class")]
rows = [[ws[f"{chr(66 + j)}{r}"].value for r, _ in fields] for j in range(9)]
write("scenarios.csv", [f for _, f in fields], rows)


rows = []
for i in range(5, 5 + len(PEAS) + 1):
    rows.append([pea_ws[f"{c}{i}"].value for c in "ABDFGHIJKL"])
write("pea_results.csv",
      ["pea", "name", "population_2020_scaled", "carrier_usd_per_mhz_pop", "uplink_price_usd_per_mhz_pop",
       "uplink_revenue_usd", "uplink_winner", "downlink_price_usd_per_mhz_pop", "downlink_revenue_usd",
       "downlink_winner"], rows)

la = WB["License_Area"]
rows = [
    ["UE uplink", "nationwide", "base", "", la["B20"].value],
    ["UE uplink", "pea_only", "base", "", la["C20"].value],
    ["UE uplink", "pea_plus_packages", "base", "", la["B78"].value],
    ["D2D downlink", "nationwide", "base", "", la["B21"].value],
    ["D2D downlink", "pea_only", "base", "", la["C21"].value],
    ["D2D downlink", "pea_plus_packages", "base", "", la["C78"].value],
]
for r in range(28, 32):
    rows.append(["UE uplink", "pea_only", "exposure_discount", la[f"A{r}"].value, la[f"B{r}"].value])
    rows.append(["D2D downlink", "pea_only", "exposure_discount", la[f"A{r}"].value, la[f"C{r}"].value])
for r in range(35, 38):
    rows.append(["UE uplink", "pea_only", "market_size_slope", la[f"A{r}"].value, la[f"B{r}"].value])
    rows.append(["D2D downlink", "pea_only", "market_size_slope", la[f"A{r}"].value, la[f"C{r}"].value])
for r in range(87, 90):
    rows.append(["UE uplink", "pea_plus_packages", "market_size_slope", la[f"A{r}"].value, la[f"D{r}"].value])
    rows.append(["D2D downlink", "pea_plus_packages", "market_size_slope", la[f"A{r}"].value, la[f"E{r}"].value])
write("license_area_results.csv",
      ["case", "license_design", "sensitivity", "sensitivity_value", "gross_revenue_usd"], rows)

ws = WB["MonteCarlo"]
rows = [[ws[f"A{r}"].value, ws[f"B{r}"].value, ws[f"C{r}"].value] for r in range(6, 16)]
write("monte_carlo_summary.csv", ["item", "value", "note"], rows)

for name, n in written:
    print(f"  {name}: {n} rows")
