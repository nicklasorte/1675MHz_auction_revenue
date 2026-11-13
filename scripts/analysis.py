"""Phase B analyses for the 1675-1695 MHz auction revenue estimate.

Usage: python scripts/analysis.py <processed_dir> <pea_market.csv> <recalculated.xlsx> <out_dir>

This is an independent Python implementation of the workbook's auction model. It first recomputes the
benchmarks from the parsed FCC data and checks that it reproduces every workbook scenario and the
license-area results; then it runs the analyses the workbook doesn't:

  model_validation.csv        Python model vs workbook, every scenario and license design
  bidder_count_grid.csv       revenue for 0-6 D2D x 0-6 terrestrial bidders (deterministic and Monte Carlo)
  ntia_zone_validation.csv    zone model vs NTIA Report 24-01 Table 11 (reference case)
  zone_sweep.csv              revenue with the four NOAA coordination zones, by zone radius and by the value
                              retained inside a zone, for each license design
  zone_pea_impact.csv         encumbered population by PEA at NTIA's coordination distances
  aws3_zone_calibration.csv   do AWS-3 federal protection zones (47 CFR 2.106 US88) lower Auction 97 prices?
  backtest.csv                split-half test of the market-size curve; Auction 113 out-of-sample check
  income_check.csv            annual payment each benchmark implies (FCC RIA method) over a 15-year term
  adjacency_demand_reduction.csv  adjacency premium and second-block value vs whether the lead bids for two
  package_threshold.csv       package bidding when local bidders can't fully coordinate (threshold problem)
  tornado.csv                 one-at-a-time sensitivity of the central estimate
  fcc_ria_comparison.csv      this estimate against the FCC's own estimate (FNPRM App. C)

Every dollar figure is gross bids for 1675-1695 MHz (two 10 MHz blocks).
"""
import csv
import math
import random
import statistics as st
import sys
from pathlib import Path

import numpy as np
from openpyxl import load_workbook

PROC, PEA_FILE, XLSX, OUT = (Path(a) for a in sys.argv[1:5])
OUT.mkdir(parents=True, exist_ok=True)
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig")))
A97, A113 = rd(PROC / "a97_licenses.csv"), rd(PROC / "a113_licenses.csv")
PEAS = rd(PEA_FILE)
WB = load_workbook(XLSX, data_only=True)
written = []


def write(name, header, rows):
    with open(OUT / name, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    written.append((name, len(rows)))


# =============================================================== constants and inputs
POP20, POP10, AKHI = 331449281, 308745538, 2188662
MHZ, BLOCKS = 10, 2
CAPRATE = 0.07           # FNPRM App. C para. 4 (OMB Circular A-4)
TERM = 15                # FNPRM para. 56
f = lambda s: float(s) if s not in ("", None) else 0.0

# =============================================================== benchmarks from the raw data
sold = [x for x in A97 if x["sold"] == "Y"]
mp = lambda rows: sum(int(x["mhz"]) * int(x["population_2010"]) for x in rows)
gs = lambda rows: sum(f(x["gross_bid"]) for x in rows)
unp = [x for x in sold if x["block"] in ("A1", "B1")]
b1 = [x for x in sold if x["block"] == "B1" and int(x["population_2010"]) > 0]
resold = {"AW-" + x["license"] for x in A113}
DISH = ("Northstar Wireless, LLC", "SNR Wireless LicenseCo, LLC")
held = [x for x in unp if x["bidder"] in DISH and x["license"] not in resold]
heldall = held + [x for x in unp if x["bidder"] == "2014 AWS Spectrum Bidco Corporation"
                  and x["license"] not in resold]


def wq(q):
    rows = sorted((f(x["gross_bid"]) / (10 * int(x["population_2010"])), int(x["population_2010"])) for x in b1)
    tot, c = sum(w for _, w in rows), 0
    for v, w in rows:
        c += w
        if c >= q * tot:
            return v


ab = gs(unp) / mp(unp)
b1p = gs(b1) / mp(b1)
q25 = wq(0.25)
share = mp(held) / mp(unp)
shareall = mp(heldall) / mp(unp)
sul = 2.6e9 / (15 * share * POP20)
sul_all = 2.6e9 / (15 * shareall * POP20)
spx113 = [f(x["gross_per_mhz_pop"]) for x in A113 if x["license"] == "BEA049-B1"][0]
grain_prior, grain_spx = 3.6e9 / (14 * POP20), 8e9 / (14 * POP20)
pe = rd(PROC / "pea_ea.csv")
qcE = sum(int(r["population_2010"]) for r in pe if int(r["ea"]) in {10, 3, 12, 160, 163})
qualcomm = 1.925e9 / (6 * POP10 + 6 * qcE)
lease = 13e6 / CAPRATE / (5 * POP10)
BM = {"TUL": {"Low": q25, "Base": ab, "High": b1p},
      "SUL": {"Low": spx113, "Base": sul, "High": b1p},
      "SDL": {"Low": sul, "Base": grain_prior, "High": grain_spx},
      "TDL": {"Low": lease, "Base": (lease + qualcomm) / 2, "High": qualcomm}}
# flat-nominal ratio and national premium
d97 = {x["license"]: x for x in A97}
num97 = den97 = num13 = den13 = 0.0
for x in A113:
    y = d97.get("AW-" + x["license"])
    if y and y["sold"] == "Y" and int(y["population_2010"]) > 0 and int(x["population"]) > 0:
        num97 += f(y["gross_bid"]); den97 += int(y["population_2010"])
        num13 += f(x["gross_bid"]); den13 += int(x["population"])
flat = (num13 / den13) / (num97 / den97)
hold15 = gs(held) / mp(held)
PREM = sul / (hold15 * flat)
# market-size fit
X = np.array([math.log(int(x["population_2010"])) for x in b1])
Y = np.array([math.log(f(x["gross_bid"]) / (10 * int(x["population_2010"]))) for x in b1])
SLOPE, ICPT = np.polyfit(X, Y, 1)

# =============================================================== core model
def clear(vD, vC, nD, nC, lead_prem=0.0, wants_both=False, second_share=1.0, B=BLOCKS, reserve=0.0):
    """Uniform-price clock outcome for B identical blocks. Values are per block. Returns (price, sold, d2d_won,
    lead_bids_two). Mirrors the Scenarios tab, including demand reduction for the lead D2D bidder."""
    lead = vD * (1 + lead_prem) if nD >= 1 else 0.0
    others = [vD] * max(nD - 1, 0) + [vC] * nC
    one = ([lead] if nD >= 1 else []) + others
    two = one + ([lead * second_share] if (nD >= 1 and wants_both) else [])

    def price(bids):
        b = sorted([x for x in bids if x > 0], reverse=True)
        return max(b[B], reserve) if len(b) > B else reserve

    p1, p2 = price(one), price(two)
    above = sum(1 for x in others if x > lead)
    won1 = (0 if above >= B else 1) if lead > 0 else 0
    v2 = lead * second_share
    won2 = 0
    if lead > 0 and wants_both:
        won2 = (1 if above < B else 0) + (1 if (v2 > 0 and sum(1 for x in others if x > v2) <= B - 2) else 0)
    s1 = won1 * (lead - p1)
    s2 = won2 * (v2 - p2) + min(won2, 1) * (lead - v2)
    two_ = wants_both and s2 > s1
    bids = two if two_ else one
    p = p2 if two_ else p1
    nsold = min(B, len([x for x in bids if x > 0]))
    lowest = sorted([x for x in bids if x > 0], reverse=True)[B - 1] if len([x for x in bids if x > 0]) >= B else 0
    d2d = min(nsold, (won2 if two_ else won1) + sum(1 for x in [vD] * max(nD - 1, 0) if x >= lowest and x > 0))
    return p, nsold, d2d, two_


def nat_rev(pD, pC, nD, nC, avail_d=1.0, avail_c=1.0, **kw):
    vD, vC = pD * MHZ * POP20 * avail_d, pC * MHZ * POP20 * avail_c
    p, n, d2d, two = clear(vD, vC, nD, nC, **kw)
    return p * n


# PEA table (as the workbook: 406 contiguous PEAs scaled to 2020, plus combined AK/HI)
C = np.array([int(r["population"]) for r in PEAS] + [0], dtype=float)
scale = (POP20 - AKHI) / C[:-1].sum()
D = C * scale
D[-1] = AKHI
C[-1] = AKHI / scale
CODES = [r["market"] for r in PEAS] + ["AK+HI"]
NAMES = [r["market_name"] for r in PEAS] + ["Alaska and Hawaii"]


def carrier_values(base, slope=SLOPE):
    k = D.sum() / (D * C ** slope).sum()
    return base * k * C ** slope


def pea_price(d, F, nD, nC, B=BLOCKS):
    hi_is_d = d > F
    v_h, v_l = np.where(hi_is_d, d, F), np.where(hi_is_d, F, d)
    n_h = np.where(hi_is_d, nD, nC)
    n_l = np.where(hi_is_d, nC, nD)
    return np.where(n_h >= B + 1, v_h, np.where(n_h + n_l >= B + 1, v_l, 0.0))


def pea_rev(pC_base, pD_nat, nD, nC, avail=None, slope=SLOPE, prem=PREM, exposure=0.0, apply_prem=True):
    A = np.ones_like(D) if avail is None else avail
    F = carrier_values(pC_base, slope)
    d = pD_nat / (prem if apply_prem else 1) * (1 - exposure)
    p = pea_price(np.full_like(F, d), F, nD, nC)
    return float((p * BLOCKS * MHZ * D * A).sum()), p, F, d


def package_rev(pC_base, pD_nat, nD, nC, avail=None, slope=SLOPE, theta=1.0):
    """PEA licenses plus all-or-nothing nationwide packages per block (workbook rows 72-91), with an optional
    threshold-problem factor theta: local bidders jointly mount only theta x the sum of their per-PEA bids."""
    A = np.ones_like(D) if avail is None else avail
    pea_total, _, _, _ = pea_rev(pC_base, pD_nat, nD, nC, avail=A, slope=slope)  # 0% exposure
    per_block_pea = pea_total / BLOCKS
    pkg = pD_nat * MHZ * float((D * A).sum())
    if nD >= BLOCKS + 1:                      # D2D bidders compete for packages
        per_block = max(pkg, per_block_pea)
    elif nD >= 1 and pkg > theta * per_block_pea:  # thin package competition: core price set by local bids
        per_block = theta * per_block_pea
    else:
        per_block = per_block_pea
    return BLOCKS * per_block


# =============================================================== 1. validation against the workbook
ws = WB["Scenarios"]
val = []
for j in range(9):
    c = chr(66 + j)
    name, case, tu, du = ws[f"{c}4"].value, ws[f"{c}6"].value, ws[f"{c}7"].value, ws[f"{c}8"].value
    nD, nC, both = int(ws[f"{c}9"].value), int(ws[f"{c}10"].value), int(ws[f"{c}11"].value) == 1
    py = nat_rev(BM[du][case], BM[tu][case], nD, nC, wants_both=both)
    val.append([name, "nationwide", ws[f"{c}47"].value, py])
la = WB["License_Area"]
for lab, cell, py in [
        ("UE uplink", "C20", pea_rev(ab, sul, 3, 4)[0]), ("D2D downlink", "C21", pea_rev(ab, grain_prior, 3, 4)[0]),
        ("UE uplink", "B78", package_rev(ab, sul, 3, 4)), ("D2D downlink", "C78", package_rev(ab, grain_prior, 3, 4))]:
    val.append([lab, "PEA only" if cell[0] == "C" and cell != "C78" else "PEA + packages", la[cell].value, py])
for r in val:
    r.append(r[3] - r[2])
bad = [r for r in val if abs(r[4]) > 1.0]
write("model_validation.csv", ["case", "license_design", "workbook_usd", "python_usd", "difference_usd"], val)
if bad:
    sys.exit(f"Python model does not reproduce the workbook: {bad}")
BASE = val[0][2]  # S1 central

# =============================================================== 2. bidder-count grid
rng = random.Random(1675)
sigma = 0.237763975890283  # MonteCarlo tab (Auction 97 paired winners over $1B)
sig_check = WB["MonteCarlo"]["B7"].value
assert abs(sig_check - sigma) < 1e-12
grid = []
for nD in range(7):
    for nC in range(7):
        up = nat_rev(sul, ab, nD, nC)
        dn = nat_rev(grain_prior, ab, nD, nC)
        sims = []
        for _ in range(2000):
            car = [ab * math.exp(rng.gauss(0, sigma)) for _ in range(nC)]
            d2 = [rng.uniform(spx113, grain_prior) for _ in range(nD)]
            v = sorted(car + d2, reverse=True)
            sims.append(BLOCKS * (v[BLOCKS] if len(v) > BLOCKS else 0.0) * MHZ * POP20)
        sims.sort()
        q = lambda p: sims[int(p * (len(sims) - 1))]
        grid.append([nD, nC, up, dn, q(0.1), q(0.5), q(0.9)])
write("bidder_count_grid.csv", ["d2d_bidders", "terrestrial_bidders", "uplink_value_usd", "downlink_value_usd",
                                "monte_carlo_p10_usd", "monte_carlo_median_usd", "monte_carlo_p90_usd"], grid)

# =============================================================== 3. coordination zones
cty = {r["fips"]: r for r in rd(PROC / "county_pop_2020.csv")}
pc = rd(PROC / "pea_counties.csv")
fips2pea = {r["fips"]: int(r["pea"]) for r in pc}
for new, old in (("02063", "02261"), ("02066", "02261"), ("02158", "02270"), ("46102", "46113")):
    fips2pea[new] = fips2pea[old]  # 2010-2020 county changes in Alaska and South Dakota
CF = [k for k in cty if k in fips2pea]
clat = np.radians([float(cty[k]["lat"]) for k in CF])
clon = np.radians([float(cty[k]["lon"]) for k in CF])
cpop = np.array([int(cty[k]["population_2020"]) for k in CF], dtype=float)
cpea = np.array([fips2pea[k] for k in CF])


def dist_km(lat, lon):
    la_, lo_ = math.radians(lat), math.radians(lon)
    a = np.sin((clat - la_) / 2) ** 2 + np.cos(clat) * math.cos(la_) * np.sin((clon - lo_) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


sites = rd(PROC / "ntia_sites.csv")
SD = {s["site"]: dist_km(float(s["lat"]), float(s["lon"])) for s in sites}


def encumbered(site_names, scale_=1.0, radii=None):
    m = np.zeros(len(CF), dtype=bool)
    for s in sites:
        if s["site"] in site_names:
            r = (radii or {}).get(s["site"], float(s["ntia_dcs_coordination_km"])) * scale_
            m |= SD[s["site"]] <= r
    return m


def pea_share(mask):
    """Share of each PEA's 2020 population inside a zone, aligned to the workbook PEA rows."""
    out = np.zeros(len(CODES))
    for i, code in enumerate(CODES):
        if code == "AK+HI":
            sel = np.isin(cpea, [p for p in range(1, 417) if False])  # AK/HI PEAs aren't near any site
            continue
        n = int(code[3:])
        sel = cpea == n
        tot = cpop[sel].sum()
        out[i] = cpop[sel & mask].sum() / tot if tot else 0.0
    return out


# 3a. reference case: NTIA Table 11 (ADM scenario includes Hunt Valley)
adm = encumbered([s["site"] for s in sites])
sh = pea_share(adm)
t11 = rd(PROC / "ntia_table11.csv")
rows = []
for r in t11:
    i = int(r["pea"]) - 1
    ntia = float(r["non_overlapping_pct"]) + float(r["overlapping_pct"])
    rows.append([r["pea"], NAMES[i], ntia, round(100 * sh[i], 1), round(100 * sh[i] - ntia, 1)])
mae = st.fmean(abs(r[4]) for r in rows)
agree = sum(1 for r in rows if (r[2] >= 50) == (r[3] >= 50))
write("ntia_zone_validation.csv", ["pea", "name", "ntia_encumbered_pct", "model_encumbered_pct", "difference_pct"],
      rows)

# =============================================================== 4. AWS-3 protection-zone calibration (Auction 97)
z = rd(PROC / "us88_zones.csv")
zm = np.zeros(len(CF), dtype=bool)
for r in z:
    zm |= dist_km(float(r["lat"]), float(r["lon"])) <= float(r["radius_km"])
pea2ea = {int(r["pea"]): int(r["ea"]) for r in pe}
cea = np.array([pea2ea[p] for p in cpea])
ea_share = {}
for e in set(cea.tolist()):
    sel = cea == e
    ea_share[e] = cpop[sel & zm].sum() / cpop[sel].sum()
cal = []
for x in b1:
    e = int(x["market"].replace("BEA", ""))
    if e in ea_share:
        cal.append((x["license"], x["market_name"], int(x["population_2010"]),
                    f(x["gross_bid"]) / (10 * int(x["population_2010"])), ea_share[e]))
Xc = np.column_stack([np.ones(len(cal)), np.log([c_[2] for c_ in cal]), [c_[4] for c_ in cal]])
Yc = np.log([c_[3] for c_ in cal])
beta, res, *_ = np.linalg.lstsq(Xc, Yc, rcond=None)
resid = Yc - Xc @ beta
s2 = resid @ resid / (len(Yc) - 3)
se = np.sqrt(np.diag(s2 * np.linalg.inv(Xc.T @ Xc)))
n_enc = sum(1 for c_ in cal if c_[4] > 0)
retained = math.exp(beta[2])
lo95, hi95 = math.exp(beta[2] - 1.96 * se[2]), math.exp(beta[2] + 1.96 * se[2])
cal_rows = [[c_[0], c_[1], c_[2], c_[3], round(c_[4], 4)] for c_ in cal]


def zone_coef(rows):
    Xr = np.column_stack([np.ones(len(rows)), np.log([c_[2] for c_ in rows]), [c_[4] for c_ in rows]])
    br, *_ = np.linalg.lstsq(Xr, np.log([c_[3] for c_ in rows]), rcond=None)
    return br[2]


robust = {
    "drop_washington_baltimore": zone_coef([c_ for c_ in cal if "Wash.-Balt." not in c_[1]]),
    "drop_largest_encumbered_market": zone_coef(
        [c_ for c_ in cal if c_ is not max((c for c in cal if c[4] > 0), key=lambda c: c[2])]),
    "encumbered_indicator_any_share": None,
}
Xi = np.column_stack([np.ones(len(cal)), np.log([c_[2] for c_ in cal]), [1.0 if c_[4] > 0 else 0.0 for c_ in cal]])
bi, *_ = np.linalg.lstsq(Xi, Yc, rcond=None)
robust["encumbered_indicator_any_share"] = bi[2]
write("aws3_zone_calibration.csv", ["license", "market_name", "population_2010", "usd_per_mhz_pop",
                                    "population_share_in_us88_zones"], cal_rows)

# 3b. FNPRM's four sites: sweep zone radius (share of NTIA's distance) and value retained inside zones
FOUR = [s["site"] for s in sites if s["protected_in_fnprm"] == "Y"]
zone_rows, impact_rows = [], []
for sc in (0.0, 0.1, 0.25, 0.5, 0.75, 1.0):
    m = encumbered(FOUR, sc)
    shr = pea_share(m)
    nat_share = float((shr * D).sum() / D.sum())
    for keep in (0.0, round(retained, 3), 0.5):
        A = 1 - (1 - keep) * shr
        Fv = carrier_values(ab)
        c_eff = float((Fv * D * A).sum() / D.sum())        # terrestrial value tracks where value sits
        d_avail = float((D * A).sum() / D.sum())
        for case, pD in (("UE uplink", sul), ("D2D downlink", grain_prior)):
            nat = nat_rev(pD * d_avail, c_eff, 3, 4)
            peo = pea_rev(ab, pD, 3, 4, avail=A)[0]
            pk = package_rev(ab, pD, 3, 4, avail=A)
            zone_rows.append([sc, round(sc * 100), keep, case, nat_share, nat, peo, pk])
    if sc == 1.0:
        for i in np.argsort(-shr * D)[:25]:
            impact_rows.append([CODES[i], NAMES[i], round(D[i]), round(100 * shr[i], 1), round(D[i] * shr[i])])
# county-level zone membership for the map figure
near = np.full(len(CF), np.inf)
ratio = np.full(len(CF), np.inf)
for s_ in sites:
    if s_["site"] in FOUR:
        dd = SD[s_["site"]]
        near = np.minimum(near, dd)
        ratio = np.minimum(ratio, dd / float(s_["ntia_dcs_coordination_km"]))
write("zone_counties.csv", ["fips", "pea", "population_2020", "km_to_nearest_site", "distance_share_of_ntia",
                            "in_zone_at_ntia_distance", "in_zone_at_half_ntia_distance"],
      [[CF[i], int(cpea[i]), int(cpop[i]), round(float(near[i]), 1), round(float(ratio[i]), 4),
        int(ratio[i] <= 1.0), int(ratio[i] <= 0.5)] for i in range(len(CF))])
write("zone_sweep.csv", ["radius_share_of_ntia", "radius_pct_of_ntia", "value_retained_in_zone", "case",
                         "national_population_share_encumbered", "nationwide_usd", "pea_only_usd",
                         "pea_plus_packages_usd"], zone_rows)
write("zone_pea_impact.csv", ["pea", "name", "population_2020_scaled", "encumbered_pct", "encumbered_population"],
      impact_rows)

# =============================================================== 5. backtest
rb = random.Random(1675)
errs, agg = [], []
idx = list(range(len(b1)))
for _ in range(200):
    rb.shuffle(idx)
    tr, te = idx[: len(idx) // 2], idx[len(idx) // 2:]
    s_, i_ = np.polyfit(X[tr], Y[tr], 1)
    wtr = np.exp(X[tr])
    pbar = (np.exp(Y[tr]) * wtr).sum() / wtr.sum()          # training population-weighted price
    k_ = wtr.sum() / (wtr * wtr ** s_).sum()                  # calibration as in the workbook PEA tab
    pred = pbar * k_ * np.exp(X[te]) ** s_
    act = np.exp(Y[te])
    errs.append(float(np.median(np.abs(pred / act - 1))))
    w = np.exp(X[te])
    agg.append(float((pred * w).sum() / (act * w).sum() - 1))
unp113 = [x for x in A113 if x["block"] in ("A1", "B1")]
oos = []
for x in unp113:
    pop = int(x["population"])
    w_all = np.exp(X)
    k_all = w_all.sum() / (w_all * w_all ** SLOPE).sum()
    pred = b1p * k_all * pop ** SLOPE * flat                 # calibrated B1 curve at 2026 population
    oos.append([x["license"], x["market_name"], x["block"], pop, f(x["gross_per_mhz_pop"]), pred,
                pred / f(x["gross_per_mhz_pop"]) - 1])
flat_err = []
rb2 = random.Random(1675)
idx2 = list(range(len(b1)))
for _ in range(200):
    rb2.shuffle(idx2)
    tr, te = idx2[: len(idx2) // 2], idx2[len(idx2) // 2:]
    wtr, wte = np.exp(X[tr]), np.exp(X[te])
    pbar = (np.exp(Y[tr]) * wtr).sum() / wtr.sum()
    flat_err.append(float(np.median(np.abs(pbar / np.exp(Y[te]) - 1))))
bt = [["split_half_median_abs_error_per_license", st.median(errs), "200 random halves of the 174 B1 licenses; "
       "market-size curve calibrated on the training half"],
      ["split_half_median_abs_error_flat_price", st.median(flat_err), "Same splits, one national price per pop"],
      ["split_half_aggregate_revenue_error_median", st.median(agg), "Population-weighted hold-out revenue"],
      ["split_half_aggregate_revenue_error_p10", sorted(agg)[19], ""],
      ["split_half_aggregate_revenue_error_p90", sorted(agg)[179], ""]]
for o in oos:
    bt.append([f"auction113_{o[0]}_predicted_vs_actual", o[6],
               f"{o[1]} {o[2]}: predicted ${o[5]:.3f} vs actual ${o[4]:.3f} per MHz-pop (2015 curve x flat ratio)"])
write("backtest.csv", ["measure", "value", "note"], bt)

# =============================================================== 6. income check (FCC RIA method)
inc = []
annuity = CAPRATE / (1 - (1 + CAPRATE) ** -TERM)
for use, label in (("TUL", "Terrestrial uplink"), ("TDL", "Terrestrial downlink"), ("SUL", "Satellite uplink"),
                   ("SDL", "D2D downlink")):
    p = BM[use]["Base"]
    value_per_pop = p * MHZ * BLOCKS
    inc.append([label, p, value_per_pop, value_per_pop * CAPRATE, value_per_pop * annuity,
                value_per_pop * POP20 * CAPRATE, value_per_pop * annuity / 12])
write("income_check.csv", ["use", "base_usd_per_mhz_pop", "value_per_person_20mhz_usd",
                           "annual_payment_per_person_perpetuity_usd", "annual_payment_per_person_15yr_usd",
                           "annual_payment_national_perpetuity_usd", "monthly_payment_per_person_15yr_usd"], inc)

# =============================================================== 7. adjacency premium and demand reduction
adr = []
for nD in (2, 3):
    for prem in (0.0, 0.1, 0.21, 0.3, 0.5):
        for second in (0.5, 0.8, 1.0, 1.2):
            vD, vC = grain_prior * MHZ * POP20, ab * MHZ * POP20
            p, n, d2d, two = clear(vD, vC, nD, 4, lead_prem=prem, wants_both=True, second_share=second)
            adr.append([nD, 4, prem, second, int(two), p * n])
write("adjacency_demand_reduction.csv", ["d2d_bidders", "terrestrial_bidders", "lead_adjacency_premium",
                                         "lead_second_block_value_share", "lead_bids_for_two", "gross_revenue_usd"],
      adr)

# =============================================================== 8. package threshold problem
pth = []
for nD in (1, 2, 3):
    for theta in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        for case, pD in (("UE uplink", sul), ("D2D downlink", grain_prior)):
            pth.append([nD, 4, theta, case, package_rev(ab, pD, nD, 4, theta=theta), pea_rev(ab, pD, nD, 4)[0],
                        nat_rev(pD, ab, nD, 4)])
write("package_threshold.csv", ["d2d_bidders", "terrestrial_bidders", "local_coordination_share", "case",
                                "pea_plus_packages_usd", "pea_only_usd", "nationwide_usd"], pth)

# =============================================================== 9. tornado (central estimate, S1 nationwide)
zfull = encumbered(FOUR, 1.0)
shf = pea_share(zfull)


def zone_rev(keep, scale_=1.0):
    shr = pea_share(encumbered(FOUR, scale_))
    A = 1 - (1 - keep) * shr
    c_eff = float((carrier_values(ab) * D * A).sum() / D.sum())
    return nat_rev(sul * float((D * A).sum() / D.sum()), c_eff, 3, 4)


tor = [
    ("D2D bidders (2 / 4; base 3)", nat_rev(sul, ab, 2, 4), nat_rev(sul, ab, 4, 4)),
    ("Terrestrial bidders (2 / 6; base 4)", nat_rev(sul, ab, 3, 2), nat_rev(sul, ab, 3, 6)),
    ("Satellite uplink benchmark (low / high)", nat_rev(BM["SUL"]["Low"], ab, 3, 4),
     nat_rev(BM["SUL"]["High"], ab, 3, 4)),
    ("Terrestrial uplink benchmark (low / high)", nat_rev(sul, BM["TUL"]["Low"], 3, 4),
     nat_rev(sul, BM["TUL"]["High"], 3, 4)),
    ("D2D values the band as downlink (no / yes)", BASE, nat_rev(grain_prior, ab, 3, 4)),
    ("EchoStar holdings include Bidco licenses (yes / no)", nat_rev(sul_all, ab, 3, 4), BASE),
    ("NOAA zones at NTIA distances, calibrated value kept (with / without)", zone_rev(round(retained, 3)), BASE),
    ("NOAA zones at half NTIA distances, calibrated value kept (with / without)",
     zone_rev(round(retained, 3), 0.5), BASE),
]
tor_rows = [[lab, lo, hi, lo - BASE, hi - BASE, max(abs(lo - BASE), abs(hi - BASE))] for lab, lo, hi in tor]
tor_rows.sort(key=lambda r: -r[5])
write("tornado.csv", ["input", "low_case_usd", "high_case_usd", "low_change_usd", "high_change_usd", "swing_usd"],
      [r[:5] for r in tor_rows])

# =============================================================== 10. FCC RIA comparison (FNPRM App. C)
a113_avg = sum(f(x["gross_bid"]) for x in A113) / sum(int(x["mhz"]) * int(x["population"]) for x in A113)
fcc_pmp, fcc_pop = 2.53, 335073176
fc = [
    ["FCC RIA, 25 MHz (App. C para. 4)", fcc_pmp, 25, fcc_pmp * fcc_pop * 25, "Auction 113 average, all blocks"],
    ["FCC RIA method, scaled to 20 MHz", fcc_pmp, 20, fcc_pmp * fcc_pop * 20, "Same price, this paper's band"],
    ["FCC RIA low and high (±50%), 20 MHz", fcc_pmp, 20, f"{0.5 * fcc_pmp * fcc_pop * 20:.0f}-"
     f"{1.5 * fcc_pmp * fcc_pop * 20:.0f}", ""],
    ["Auction 113 average recomputed from FCC data", a113_avg, 20, a113_avg * POP20 * 20,
     "Mostly paired licenses"],
    ["Auction 97 unpaired (A1 + B1) price, 20 MHz", ab, 20, ab * POP20 * 20, "Terrestrial uplink base"],
    ["This paper, central (S1)", BASE / (20 * POP20), 20, BASE, "Third-highest bid, 3 D2D and 4 terrestrial"],
]
write("fcc_ria_comparison.csv", ["estimate", "usd_per_mhz_pop", "mhz", "gross_usd", "basis"], fc)

# =============================================================== summary for the paper
SUMMARY = {
    "python_model_max_abs_diff_usd": max(abs(r[4]) for r in val),
    "ntia_reference_mean_abs_error_pct": mae, "ntia_reference_majority_agreement": f"{agree}/25",
    "zone_ntia_national_share": [r[4] for r in zone_rows if r[0] == 1.0][0],
    "aws3_zone_coef": beta[2], "aws3_zone_se": se[2], "aws3_zone_retained": retained,
    "aws3_zone_retained_95ci": (lo95, hi95), "aws3_n": len(cal), "aws3_n_encumbered": n_enc,
    "aws3_robust_drop_dc": robust["drop_washington_baltimore"],
    "aws3_robust_drop_largest": robust["drop_largest_encumbered_market"],
    "aws3_robust_indicator": robust["encumbered_indicator_any_share"],
    "backtest_flat_median_abs_err": st.median(flat_err),
    "backtest_median_abs_err": st.median(errs), "backtest_agg_err": st.median(agg),
    "qualcomm_pmp": qualcomm, "lease_pmp": lease, "a113_avg": a113_avg,
}
with open(OUT / "analysis_summary.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["measure", "value"])
    for k, v in SUMMARY.items():
        w.writerow([k, v])
written.append(("analysis_summary.csv", len(SUMMARY)))
for name, n in written:
    print(f"  {name}: {n} rows")
for k, v in SUMMARY.items():
    print(f"  {k}: {v}")
