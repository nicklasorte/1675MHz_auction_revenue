"""Check that the key dollar figures in docs/working-paper.md match data/csv.

Usage: python scripts/check_paper.py [csv_dir] [paper.md]
Each check computes a value from the CSVs, rounds it the way the paper does, and looks for that text in the paper.
Exits non-zero on any miss.
"""
import csv
import sys
from pathlib import Path

D = Path(sys.argv[1] if len(sys.argv) > 1 else "data/csv")
PAPER = Path(sys.argv[2] if len(sys.argv) > 2 else "docs/working-paper.md").read_text(encoding="utf-8")
rd = lambda n: list(csv.DictReader(open(D / n)))
B = 1e9
fails = []


def need(label, text):
    ok = text in PAPER
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {text}")
    if not ok:
        fails.append(label)


sc = {r["scenario"]: float(r["gross_revenue_usd"]) for r in rd("scenarios.csv")}
need("central", f"${sc['S1 Base'] / B:.2f} billion")
need("D2D downlink", f"${sc['S2 D2D downlink value'] / B:.2f} billion")
need("two D2D bidders", f"${sc['S3 Two D2D bidders'] / B:.2f} billion")
zs = [r for r in rd("zone_sweep.csv") if r["size_curve"] == "zone-free" and abs(float(r["value_retained_in_zone"]) - 0.357) < 1e-3]
z = lambda case, pct, col: float([r for r in zs if r["case"].endswith(case) and r["radius_pct_of_ntia"] == str(pct)][0][col]) / B
for pct in (0, 50, 100):
    need(f"2 D2D, zones {pct}%", f"{z('2 D2D bidders', pct, 'nationwide_usd'):.2f}")
    need(f"3 D2D PEA only, zones {pct}%", f"{z('3 D2D bidders', pct, 'pea_only_usd'):.2f}")
st = {r["stage"]: float(r["gross_usd_after"]) / B for r in rd("stage_table.csv") if r["case"] == "Stressed"}
need("stressed final", f"${list(st.values())[-1]:.2f} billion")
fs = rd("financing_sensitivity.csv")[0]
need("financing repriced central", f"${float(fs['repriced_to_today_usd']) / B:.2f} billion")
need("financing change", f"${-float(fs['change_usd']) / B:.2f} billion")
tm = [r for r in rd("timing_sensitivity.csv") if r["discount_rate"] == "0.07" and r["scope"] == "nationwide"]
for r in tm[1:]:
    need(f"delay {r['delay_years']} years", f"${float(r['central_3_d2d_usd']) / B:.2f}")
mb = [float(r["gross_20mhz_usd"]) / B for r in rd("midband_crosscheck.csv") if not r["stage"].startswith("Anchor")]
need("mid-band high", f"${max(mb):.2f} billion")
need("mid-band low", f"${min(mb):.2f} billion")
w = {r["anchor"]: float(r["wacc"]) for r in rd("financing_wacc.csv")}
need("WACC today", f"{100 * w['Today (last 20 observations)']:.2f} percent")
need("WACC Auction 97", f"{100 * w['Auction 97 (AWS-3)']:.2f} percent")
fc = {r["estimate"]: float(r["gross_usd"]) / B for r in rd("fcc_ria_comparison.csv") if "-" not in r["gross_usd"]}
need("FCC 20 MHz", f"${fc['FCC RIA method, scaled to 20 MHz']:.1f} billion")
mc = sorted(float(r["gross_revenue_usd"]) for r in rd("monte_carlo_draws.csv"))
for q in (0.1, 0.5, 0.9):
    need(f"Monte Carlo {q}", f"{mc[int(q * (len(mc) - 1))] / B:.2f}")
rec = rd("midband_reconciliation.csv")
need("A107 per MHz-pop", f"${float(rec[0]['usd_per_mhz_pop_2020_census']):.2f}")
need("A110 per MHz-pop", f"${float(rec[1]['usd_per_mhz_pop_2020_census']):.2f}")
if fails:
    print(f"\n{len(fails)} paper check(s) failed: {fails}")
    sys.exit(1)
print("\nAll paper checks passed.")
