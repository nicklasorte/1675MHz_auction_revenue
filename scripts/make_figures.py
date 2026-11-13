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
         ("TDL", "Terrestrial downlink\n(1670–1675 lease; 700 MHz SDL)"),
         ("SUL", "Satellite uplink\n(SpaceX / EchoStar)"),
         ("SDL", "D2D downlink\n(SpaceX / Grain)")]
fig, ax = plt.subplots(figsize=(6.5, 3.6))
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
ax.set_xlim(0, 2.0); ax.set_ylim(-0.7, len(cases) - 0.3); style_h(ax)
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


# Figure 6: bridge from the FCC's estimate to this paper's -------------------------------------
fc = {r["estimate"]: r for r in rd("fcc_ria_comparison.csv")}
tor = {r["input"]: r for r in rd("tornado.csv")}
fcc20 = float(fc["FCC RIA method, scaled to 20 MHz"]["gross_usd"]) / B
a113 = float(fc["Auction 113 average recomputed from FCC data"]["usd_per_mhz_pop"])
pop20 = 331449281
fcc20_census = 2.53 * pop20 * 20 / B
unp = float(fc["Auction 97 unpaired (A1 + B1) price, 20 MHz"]["gross_usd"]) / B
central = float(fc["This paper, central (S1)"]["gross_usd"]) / B
zkey = [k for k in tor if k.startswith("NOAA zones at NTIA distances")][0]
zoned = float(tor[zkey]["low_case_usd"]) / B
steps = [("FCC estimate method,\n20 MHz", fcc20, "total"),
         ("2020 Census\npopulation", fcc20_census - fcc20, "step"),
         ("Unpaired, not\npaired, prices", unp - fcc20_census, "step"),
         ("Auction rule:\n3 D2D bidders", central - unp, "step"),
         ("This paper,\nbefore zones", central, "total"),
         ("NOAA zones\n(NTIA distances)", zoned - central, "step"),
         ("This paper,\nwith zones", zoned, "total")]
fig, ax = plt.subplots(figsize=(6.5, 3.4))
run = 0
for i, (lab, v, kind) in enumerate(steps):
    if kind == "total":
        ax.bar(i, v, color=BLUE if i == len(steps) - 1 else GRAY, width=0.62, zorder=2)
        run = v
        ax.text(i, v + 0.3, f"${v:.1f}B", ha="center", color=DARK, fontweight="bold", fontsize=8.5)
    else:
        lo, hi = sorted((run, run + v))
        ax.bar(i, hi - lo, bottom=lo, color="white", edgecolor=DARK, hatch="////" if v < 0 else None,
               linewidth=0.9, width=0.62, zorder=2)
        ax.text(i, hi + 0.3, f"{'+' if v >= 0 else '−'}${abs(v):.1f}B", ha="center", color=DARK, fontsize=8.5)
        run += v
ax.set_xticks(range(len(steps)), [s_[0] for s_ in steps], fontsize=7.5)
ax.set_ylabel("Gross bids, billions of dollars"); ax.set_ylim(0, 19.5)
save(fig, "fig6_fcc_bridge")

# Figure 7: fan chart by number of D2D bidders --------------------------------------------------
g = [r for r in rd("bidder_count_grid.csv") if r["terrestrial_bidders"] == "4"]
xd = np.array([int(r["d2d_bidders"]) for r in g])
p10 = np.array([float(r["monte_carlo_p10_usd"]) for r in g]) / B
p50 = np.array([float(r["monte_carlo_median_usd"]) for r in g]) / B
p90 = np.array([float(r["monte_carlo_p90_usd"]) for r in g]) / B
up = np.array([float(r["uplink_value_usd"]) for r in g]) / B
dn = np.array([float(r["downlink_value_usd"]) for r in g]) / B
fig, ax = plt.subplots(figsize=(6.5, 3.3))
ax.fill_between(xd, p10, p90, color="#E8E9EA", zorder=1, lw=0)
ax.plot(xd, p50, color=BLUE, lw=2.4, marker="o", ms=5, zorder=3)
ax.step(xd, up, where="mid", color=GRAY, lw=1.4, ls="--", zorder=2)
ax.step(xd, dn, where="mid", color=DARK, lw=1.2, ls=":", zorder=2)
ax.text(6.1, p50[-1], f"Simulated median\n${p50[-1]:.1f}B", color=BLUE, fontweight="bold", va="center", fontsize=8.5)
ax.text(4.6, p10[4] - 0.05, "10th–90th percentile of simulated outcomes", color=DARK, va="top", ha="center", fontsize=8)
ax.text(6.1, up[-1] - 0.32, "Point estimate,\nD2D at uplink value", color=GRAY, va="top", fontsize=8)
ax.text(6.1, dn[-1], "Point estimate,\nD2D at downlink value", color=DARK, va="center", fontsize=8)
ax.axvline(3, color=GRAY, lw=0.8, zorder=0)
ax.text(3.05, 1.4, "Base case: 3", color=DARK, fontsize=8)
ax.set_xlim(-0.2, 8.4); ax.set_ylim(0, 6.2); ax.set_xticks(range(7))
ax.set_xlabel("Number of D2D bidders (four terrestrial bidders)"); ax.set_ylabel("Gross bids, billions of dollars")
save(fig, "fig7_bidder_fan")

# Figure 8: tornado -----------------------------------------------------------------------------
tr = rd("tornado.csv")
base = central
fig, ax = plt.subplots(figsize=(6.5, 3.6))
for i, r in enumerate(reversed(tr)):
    lo, hi = float(r["low_case_usd"]) / B, float(r["high_case_usd"]) / B
    ax.barh(i, hi - base, left=base, color=BLUE, height=0.6, zorder=2)
    ax.barh(i, lo - base, left=base, color=GRAY, height=0.6, zorder=2)
    if abs(hi - base) > 0.005:
        ax.text(hi + 0.05, i, f"${hi:.2f}B", va="center", fontsize=7.5, color=DARK)
    if abs(lo - base) > 0.005:
        ax.text(lo - 0.05, i, f"${lo:.2f}B", va="center", ha="right", fontsize=7.5, color=DARK)
ax.axvline(base, color=DARK, lw=1)
for i, r in enumerate(reversed(tr)):
    if abs(float(r["low_case_usd"]) - float(r["high_case_usd"])) < 1:
        ax.text(base + 0.05, i, "no effect", va="center", fontsize=7.5, color=GRAY)
ax.set_yticks(range(len(tr)), [r["input"] for r in reversed(tr)], fontsize=7.5)
ax.set_xlim(2.6, 5.6); ax.set_xlabel("Gross bids, billions of dollars (central case $%.2fB)" % base)
style_h(ax); ax.spines["left"].set_visible(False)
save(fig, "fig8_tornado")

# Figure 9: county map of NOAA coordination zones -------------------------------------------------
import shapefile, zipfile, io
RAWC = Path("data/raw/census")


def albers(lon, lat, lon0=-96.0, lat0=37.5, p1=29.5, p2=45.5):
    lon, lat = np.radians(lon), np.radians(lat)
    lon0, lat0, p1, p2 = map(math.radians, (lon0, lat0, p1, p2))
    n = (math.sin(p1) + math.sin(p2)) / 2
    Cc = math.cos(p1) ** 2 + 2 * n * math.sin(p1)
    rho = np.sqrt(Cc - 2 * n * np.sin(lat)) / n
    rho0 = math.sqrt(Cc - 2 * n * math.sin(lat0)) / n
    th = n * (lon - lon0)
    return rho * np.sin(th), rho0 - rho * np.cos(th)


def shapes(zipname):
    z = zipfile.ZipFile(RAWC / zipname)
    base_ = zipname.replace(".zip", "")
    sf = shapefile.Reader(shp=io.BytesIO(z.read(base_ + ".shp")), dbf=io.BytesIO(z.read(base_ + ".dbf")),
                          shx=io.BytesIO(z.read(base_ + ".shx")))
    return sf


zc = {r["fips"]: r for r in rd("zone_counties.csv")}
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
fig, ax = plt.subplots(figsize=(6.5, 4.0))
sf = shapes("cb_2020_us_county_20m.zip")
cols = {"half": "#3F5FA8", "full": "#B4C2E6", "out": "#F2F2F2"}
patches, colors = [], []
for sr in sf.iterShapeRecords():
    rec = sr.record.as_dict()
    if rec["STATEFP"] in ("02", "15", "72"):
        continue
    z_ = zc.get(rec["GEOID"])
    k = "out" if z_ is None else ("half" if z_["in_zone_at_half_ntia_distance"] == "1" else
                                  ("full" if z_["in_zone_at_ntia_distance"] == "1" else "out"))
    pts, parts = sr.shape.points, list(sr.shape.parts) + [len(sr.shape.points)]
    for a_, b_ in zip(parts[:-1], parts[1:]):
        arr = np.array(pts[a_:b_])
        x_, y_ = albers(arr[:, 0], arr[:, 1])
        patches.append(Polygon(np.column_stack([x_, y_]), closed=True))
        colors.append(cols[k])
ax.add_collection(PatchCollection(patches, facecolor=colors, edgecolor="none", zorder=1))
ss = shapes("cb_2020_us_state_20m.zip")
for sr in ss.iterShapeRecords():
    if sr.record.as_dict()["STATEFP"] in ("02", "15", "72"):
        continue
    pts, parts = sr.shape.points, list(sr.shape.parts) + [len(sr.shape.points)]
    for a_, b_ in zip(parts[:-1], parts[1:]):
        arr = np.array(pts[a_:b_])
        x_, y_ = albers(arr[:, 0], arr[:, 1])
        ax.plot(x_, y_, color="white", lw=0.5, zorder=2)
for site, lat, lon in [("Fairmont", 39.4336, -80.1928), ("Sioux Falls", 43.7351, -96.6255),
                       ("Suitland", 38.8522, -76.9367), ("Wallops", 37.9465, -75.4621)]:
    x_, y_ = albers(np.array([lon]), np.array([lat]))
    ax.plot(x_, y_, marker="o", ms=5, color=PURPLE, mec="white", mew=0.8, zorder=4)
    dx = {"Fairmont": -0.012, "Sioux Falls": 0.008, "Suitland": 0.006, "Wallops": 0.01}[site]
    dy = {"Fairmont": 0.006, "Sioux Falls": 0.008, "Suitland": 0.018, "Wallops": -0.012}[site]
    ax.text(x_[0] + dx, y_[0] + dy, site, fontsize=7.5, color=DARK, fontweight="bold",
            ha="right" if site == "Fairmont" else "left", zorder=5)
shr_full = float([r for r in rd("zone_sweep.csv") if r["radius_pct_of_ntia"] == "100"][0][
    "national_population_share_encumbered"])
shr_half = float([r for r in rd("zone_sweep.csv") if r["radius_pct_of_ntia"] == "50"][0][
    "national_population_share_encumbered"])
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=cols["half"], label=f"Inside zone at half NTIA distance ({shr_half:.0%} of people)"),
                   Patch(color=cols["full"], label=f"Inside zone at NTIA distance ({shr_full:.0%} of people)")],
          loc="lower left", fontsize=7.5, frameon=False)
ax.set_aspect("equal"); ax.axis("off"); ax.grid(False)
ax.autoscale_view()
save(fig, "fig9_zone_map")

# Figure 10: revenue by license design as zones grow ---------------------------------------------
zs = rd("zone_sweep.csv")
keep = sorted({r["value_retained_in_zone"] for r in zs})[1]  # calibrated value retained
fig, axes = plt.subplots(1, 2, figsize=(6.5, 3.2), sharey=True)
for ax, case in zip(axes, ("UE uplink", "D2D downlink")):
    rr = [r for r in zs if r["case"] == case and r["value_retained_in_zone"] == keep]
    xs = [float(r["radius_pct_of_ntia"]) for r in rr]
    ends = []
    series = {}
    for col, lab, color, ls, lw in (("nationwide_usd", "Nationwide", GRAY, "-", 1.6),
                                     ("pea_only_usd", "PEA only", GRAY, "--", 1.4),
                                     ("pea_plus_packages_usd", "PEA + packages", BLUE, "-", 2.4)):
        ys = [float(r[col]) / B for r in rr]
        series[lab] = ys
        ax.plot(xs, ys, color=color, ls=ls, lw=lw, zorder=3 if color == BLUE else 2)
        ends.append([ys[-1], lab, color])
    if all(abs(a - b) < 1e-6 for a, b in zip(series["PEA only"], series["PEA + packages"])):
        ends = [e for e in ends if e[1] != "PEA only"]
        ends = [[e[0], "PEA only = PEA + packages", e[2]] if e[1] == "PEA + packages" else e for e in ends]
    ends.sort()
    for k in range(1, len(ends)):                      # keep labels at least 0.3B apart
        ends[k][0] = max(ends[k][0], ends[k - 1][0] + 0.3)
    for y_, lab, color in ends:
        ax.text(102, y_, lab, fontsize=7.5, color=color if color == BLUE else DARK,
                fontweight="bold" if color == BLUE else "normal", va="center")
    ax.set_title(case, loc="left", fontsize=10)
    ax.set_xlim(0, 150); ax.set_ylim(0, 6); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Zone radius, % of NTIA distance")
axes[0].set_ylabel("Gross bids, billions of dollars")
save(fig, "fig10_zone_designs")

# Figure 11: AWS-3 protection zones and Auction 97 prices -----------------------------------------
cal = rd("aws3_zone_calibration.csv")
lp = np.log([float(r["population_2010"]) for r in cal])
ly = np.log([float(r["usd_per_mhz_pop"]) for r in cal])
sh = np.array([float(r["population_share_in_us88_zones"]) for r in cal])
Xc = np.column_stack([np.ones(len(cal)), lp, sh])
bc, *_ = np.linalg.lstsq(Xc, ly, rcond=None)
partial = ly - bc[0] - bc[1] * lp            # price net of market size
fig, ax = plt.subplots(figsize=(6.5, 3.3))
ax.scatter(sh[sh == 0] + np.random.default_rng(1675).uniform(0, 0.012, (sh == 0).sum()), np.exp(partial[sh == 0]),
           s=10, color=GRAY, alpha=0.6, lw=0, zorder=2)
ax.scatter(sh[sh > 0], np.exp(partial[sh > 0]), s=22, color=DARK, lw=0, zorder=3)
xx = np.linspace(0, 1, 50)
ax.plot(xx, np.exp(bc[2] * xx), color=BLUE, lw=2.4, zorder=4)
ax.set_yscale("log")
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
ax.yaxis.set_major_locator(FixedLocator([0.25, 0.5, 1, 2, 4, 8]))
ax.yaxis.set_minor_locator(NullLocator())
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}×"))
ax.annotate(f"A fully covered market keeps about {math.exp(bc[2]):.0%}\nof its price", xy=(1, math.exp(bc[2])),
            xytext=(0.55, 4.0), color=BLUE, fontweight="bold", fontsize=8.5,
            arrowprops=dict(arrowstyle="-", color=BLUE))
ax.text(0.03, 3.2, "Markets with no protection zone", color=GRAY, fontsize=8)
ax.text(0.78, 0.2, "Markets partly\ninside a zone", color=DARK, fontsize=8, va="center")
ax.set_xlabel("Share of market population inside AWS-3 federal protection zones")
ax.set_ylabel("Price relative to market-size\nexpectation (log scale)")
ax.set_xlim(-0.03, 1.05)
save(fig, "fig11_aws3_calibration")
