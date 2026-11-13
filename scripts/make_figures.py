"""Make the working-paper figures from the CSVs in data/csv.

Usage: python scripts/make_figures.py [csv_dir] [out_dir]   (defaults: data/csv, figures)
Writes each figure as PNG (300 dpi), SVG, and PDF. Figures carry only the chart and its
annotations; titles, captions, and source lines are in docs/working-paper.md.
"""
import csv
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

CSV = Path(sys.argv[1] if len(sys.argv) > 1 else "data/csv")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "figures")
OUT.mkdir(parents=True, exist_ok=True)
plt.style.use(Path(__file__).with_name("briefing.mplstyle"))
plt.rcParams["svg.hashsalt"] = "1675"  # fixed salt and no dates, so reruns write identical files
META = {"png": {"Software": None}, "svg": {"Date": None}, "pdf": {"CreationDate": None, "ModDate": None, "Producer": None}}

BLUE, GRAY, PURPLE, DARK = "#5674C4", "#8A8D91", "#6E4F92", "#163353"
rd = lambda n: list(csv.DictReader(open(CSV / n)))
B = 1e9


def save(fig, name):
    for ext in ("png", "svg", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", metadata=META[ext])
    plt.close(fig)
    print("  wrote", name)


def style_h(ax):
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(True); ax.spines["left"].set_color(GRAY)


# Figure 1: benchmark ranges by use case -------------------------------------------------------
bm = {r["use_case"]: r for r in rd("benchmarks.csv")}
cases = [("TUL", "Terrestrial uplink\n(Auction 97 unpaired)"),
         ("SUL", "Satellite uplink\n(SpaceX / EchoStar)"),
         ("SDL", "D2D downlink\n(SpaceX / Grain)")]
fig, ax = plt.subplots(figsize=(6.5, 3.0))
for i, (k, lab) in enumerate(cases):
    lo, ba, hi = (float(bm[k][f"{x}_usd_per_mhz_pop"]) for x in ("low", "base", "high"))
    y = len(cases) - 1 - i
    ax.hlines(y, lo, hi, color=GRAY, lw=6, zorder=2)
    ax.plot(ba, y, "o", ms=9, color=BLUE, zorder=3)
    ax.text(ba, y + 0.27, f"base ${ba:.2f}", ha="center", va="bottom", color=DARK, fontweight="bold", fontsize=8)
    ax.text(lo, y - 0.2, f"${lo:.2f}", ha="center", va="top", color=DARK, fontsize=8)
    ax.text(hi, y - 0.2, f"${hi:.2f}", ha="center", va="top", color=DARK, fontsize=8)
ax.set_yticks(range(len(cases)), [c[1] for c in reversed(cases)])
ax.set_xlabel("Price per megahertz-pop, nominal dollars")
ax.set_xlim(0, 2.0); ax.set_ylim(-0.7, 2.7); style_h(ax)
save(fig, "fig1_benchmarks")

# Figure 2: Auction 97 B1 price versus market population ---------------------------------------
b1 = [r for r in rd("a97_unpaired_licenses.csv") if r["b1_ln_population"]]
x = np.array([float(r["b1_ln_population"]) for r in b1]); y = np.array([float(r["b1_ln_usd_per_mhz_pop"]) for r in b1])
slope, icpt = np.polyfit(x, y, 1)
print(f"  B1 fit: n={len(b1)} slope={slope:.4f}")
fig, ax = plt.subplots(figsize=(6.5, 3.4))
ax.scatter(np.exp(x), np.exp(y), s=14, color=GRAY, alpha=0.7, lw=0, zorder=2)
xs = np.linspace(x.min(), x.max(), 50)
ax.plot(np.exp(xs), np.exp(icpt + slope * xs), color=BLUE, lw=2.2, zorder=3)
ax.annotate(f"Fitted slope {slope:.2f}: price per person\nrises with market size",
            xy=(2.0e6, np.exp(icpt + slope * np.log(2.0e6))), xytext=(2.6e6, 0.035),
            color=BLUE, fontweight="bold", fontsize=9, arrowprops=dict(arrowstyle="-", color=BLUE))
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Market population, 2010 (log scale)"); ax.set_ylabel("Price per megahertz-pop (log scale)")
ax.grid(axis="x")
save(fig, "fig2_market_size")

# Figure 3: license design comparison ---------------------------------------------------------
la = rd("license_area_results.csv")
get = lambda c, d, s="base", v="": next(float(r["gross_revenue_usd"]) for r in la
                                       if r["case"] == c and r["license_design"] == d and r["sensitivity"] == s
                                       and (v == "" or abs(float(r["sensitivity_value"]) - v) < 1e-9))
designs = [("nationwide", "1. Nationwide"), ("pea_only", "2. PEA only"), ("pea_plus_packages", "3. PEA + packages")]
fig, axes = plt.subplots(1, 2, figsize=(6.5, 3.4), sharey=True)
for ax, case in zip(axes, ("UE uplink", "D2D downlink")):
    for i, (d, lab) in enumerate(designs):
        base = get(case, d) / B
        if d == "pea_only":
            low = min(get(case, d, "market_size_slope", 0.0), get(case, d, "exposure_discount", 0.3)) / B
        elif d == "pea_plus_packages":
            low = get(case, d, "market_size_slope", 0.0) / B
        else:
            low = base
        yy = 2 - i
        ax.barh(yy, base, color=BLUE if d == "pea_plus_packages" else GRAY, height=0.55, zorder=2)
        ax.plot([low], [yy], marker="|", ms=22, mew=2.5, color=DARK, zorder=4)
        ax.text(6.5, yy, f"${base:.2f}B", va="center", ha="right", color=DARK, fontweight="bold", fontsize=8.5)
    ax.set_title(case, loc="left", fontsize=10); ax.set_xlim(0, 6.6); style_h(ax)
    ax.set_xlabel("Gross bids, billions of dollars")
axes[0].set_yticks([2, 1, 0], [d[1] for d in designs])
axes[1].plot([], [], marker="|", ms=12, mew=2.5, color=DARK, ls="none", label="Lowest case tested")
axes[1].legend(loc="lower right", fontsize=8, handletextpad=0.2, bbox_to_anchor=(1.0, 0.98))
save(fig, "fig3_license_design")

# Figure 4: scenario revenue ----------------------------------------------------------------------
sc = [r for r in rd("scenarios.csv") if r["in_summary_range"] == "Y"]
sc.sort(key=lambda r: float(r["gross_revenue_usd"]))
fig, ax = plt.subplots(figsize=(6.5, 3.5))
for i, r in enumerate(sc):
    v = float(r["gross_revenue_usd"]) / B
    ax.barh(i, v, height=0.62, color=BLUE if r["scenario"].startswith("S1 ") else GRAY, zorder=2)
    ax.text(v + 0.1, i, f"${v:.2f}B", va="center", color=DARK, fontweight="bold", fontsize=8.5)
ax.set_yticks(range(len(sc)), [r["scenario"] for r in sc])
ax.set_xlim(0, 13); ax.set_xlabel("Gross bids for 20 megahertz, billions of dollars"); style_h(ax)
ax.text(6.3, [r["scenario"] for r in sc].index("S1 Base"), "Central case", color=BLUE, fontweight="bold", va="center", fontsize=9)
save(fig, "fig4_scenarios")

# Figure 5: Monte Carlo distribution -----------------------------------------------------------------
mc = rd("monte_carlo_draws.csv")
rev = np.sort(np.array([float(r["gross_revenue_usd"]) for r in mc])) / B
p = lambda q: rev[int(q * (len(rev) - 1))]
fig, ax = plt.subplots(figsize=(6.5, 3.2))
ax.hist(rev, bins=60, color=GRAY, zorder=2)
for q, lab in ((0.1, "10th"), (0.5, "median"), (0.9, "90th")):
    ax.axvline(p(q), color=BLUE if q == 0.5 else DARK, lw=2 if q == 0.5 else 1.2, ls="-" if q == 0.5 else "--", zorder=3)
    ax.text(p(q), ax.get_ylim()[1] * 1.0, f" {lab}\n ${p(q):.2f}B", ha="left", va="top", color=DARK, fontsize=8.5, fontweight="bold")
share = np.mean([r["price_set_by"] == "D2D" for r in mc])
ax.text(0.98, 0.55, f"A D2D bidder sets the\nprice in {share:.0%} of draws", transform=ax.transAxes,
        ha="right", color=DARK, fontsize=9)
ax.set_xlabel("Gross bids for 20 megahertz, billions of dollars"); ax.set_ylabel("Draws (of 10,000)")
ax.set_xlim(2.0, 6.5)
save(fig, "fig5_monte_carlo")
