"""Check the exported CSVs in data/csv against the published FCC totals and the recalculated workbook.

Usage: python scripts/check_csvs.py <csv_dir> <recalculated.xlsx>
Exits non-zero on any failure.
"""
import csv
import statistics
import sys
from pathlib import Path

from openpyxl import load_workbook

D, XLSX = Path(sys.argv[1]), sys.argv[2]
WB = load_workbook(XLSX, data_only=True)
fails = []


def rd(name):
    return list(csv.DictReader(open(D / name)))


def check(label, got, want, tol=0.0):
    ok = abs(got - want) <= tol
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got:,.6g} (expected {want:,.6g})")
    if not ok:
        fails.append(label)


# Auction 113 file reconciles to the published results.
a113 = rd("a113_licenses.csv")
check("A113 license count", len(a113), 200)

# Auction 97: unpaired + paired files together hold every license the model parses.
a97u, a97p = rd("a97_unpaired_licenses.csv"), rd("a97_paired_licenses.csv")
check("A97 license rows (unpaired + paired)", len(a97u) + len(a97p), 1614)
sold = [r for r in a97u + a97p if r["sold"] == "Y"]
check("A97 net bids, all licenses", sum(float(r["net_bid_usd"]) for r in sold), WB["Evidence"]["B7"].value, 1)
check("A97 licenses won", len(sold), 1611)

# PEA table: 406 contiguous PEAs plus the combined AK/HI row; populations tie to the workbook.
pea = rd("pea_populations.csv")
check("PEA rows", len(pea), 407)
check("PEA 2020-scaled population", sum(float(r["population_2020_scaled"]) for r in pea),
      float(WB["Inputs"]["B5"].value), 5)

# PEA results re-add to the License_Area headline cells.
la = WB["License_Area"]
res = rd("pea_results.csv")
check("PEA uplink revenue sums to License_Area C20", sum(float(r["uplink_revenue_usd"]) for r in res),
      la["C20"].value, 1)
check("PEA downlink revenue sums to License_Area C21", sum(float(r["downlink_revenue_usd"]) for r in res),
      la["C21"].value, 1)

# Scenario headlines.
sc = {r["scenario"]: float(r["gross_revenue_usd"]) for r in rd("scenarios.csv")}
check("Scenario S1 gross revenue", sc["S1 Base"], WB["Scenarios"]["B47"].value, 1)
check("Scenario S2 gross revenue", sc["S2 D2D downlink value"], WB["Scenarios"]["C47"].value, 1)

# Monte Carlo draws reproduce the workbook's percentiles and the D2D share.
draws = rd("monte_carlo_draws.csv")
check("Monte Carlo draws", len(draws), 10000)
rev = sorted(float(r["gross_revenue_usd"]) for r in draws)
mc = WB["MonteCarlo"]
pct = lambda p: rev[int(p * (len(rev) - 1))]  # same rule as build_workbook.py
check("Monte Carlo P10", pct(0.10), mc["B11"].value, 1)
check("Monte Carlo median", pct(0.50), mc["B12"].value, 1)
check("Monte Carlo P90", pct(0.90), mc["B13"].value, 1)
check("Monte Carlo mean", statistics.fmean(rev), mc["B14"].value, 1)
check("Monte Carlo D2D share", sum(r["price_set_by"] == "D2D" for r in draws) / len(draws),
      mc["B15"].value, 0.0001)

if fails:
    print(f"\n{len(fails)} CSV check(s) failed: {fails}")
    sys.exit(1)
print("\nAll CSV checks passed.")
