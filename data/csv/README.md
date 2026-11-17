# Datasets used in the calculation

**DRAFT//PRE-DECISIONAL.** Every file here is written by `scripts/export_csvs.py` (and
`monte_carlo_draws.csv` by `scripts/build_workbook.py`) when you run `./reproduce.sh`. Don't edit
them by hand. `scripts/check_csvs.py` ties them to the published FCC totals and to the recalculated
workbook on every run. Dollar figures are gross bids before federal coordination unless the column says
otherwise.

## FCC data, filtered to what the model uses

| File | Rows | Contents |
| --- | --- | --- |
| `a97_unpaired_licenses.csv` | 352 | Auction 97 unpaired 1695–1710 MHz licenses (blocks A1 and B1): population, winner, bids, price per megahertz-pop, whether resold in Auction 113, whether sold to SpaceX through EchoStar, and the log values behind the market-size fit |
| `a97_paired_licenses.csv` | 1,262 | Auction 97 paired licenses (blocks G, H, I, J) |
| `a97_paired_by_bidder.csv` | 29 | Paired spending by winner; the winners that spent over $1 billion set the Monte Carlo carrier spread |
| `a113_licenses.csv` | 200 | Every Auction 113 license won, with price per megahertz-pop |
| `matched_pairs_a97_a113.csv` | 196 | Licenses sold in both auctions, used to test whether price per person stayed flat in nominal dollars |
| `pea_populations.csv` | 407 | 406 PEAs (Auction 110 market file) plus combined Alaska and Hawaii, with 2010 population and the 2020 scaling; flags the four PEAs that contain NOAA receive sites (site-to-PEA mapping still to be verified) |

## Inputs typed into the workbook

| File | Contents |
| --- | --- |
| `inputs.csv` | Model parameters with sources, including published totals used as checks |
| `transactions.csv` | SpaceX/EchoStar, SpaceX/Grain (two prices), Amazon/Globalstar (cross-check only), Qualcomm 700 MHz D and E Blocks (FCC 11-188, verified), and the 1670–1675 MHz lease (capitalized) |
| `bidder_classes.csv` | Bidder classes (D2D, terrestrial) and value multipliers; scenarios set the number in each class |

## Calculated results (from the recalculated workbook)

| File | Contents |
| --- | --- |
| `evidence.csv` | Reconciliation to published totals and the fitted measures (slope 0.65, premium 1.21, flat-price ratio 0.99) |
| `benchmarks.csv` | Low, base, and high price per megahertz-pop for each use |
| `scenarios.csv` | Scenarios S1–S9: switches, benchmark values, clearing price, and gross revenue |
| `pea_results.csv` | Each PEA's population, carrier value, price, revenue, and winner class for uplink and downlink |
| `license_area_results.csv` | Nationwide, PEA, and PEA-plus-package revenue, with the exposure-discount and market-size sensitivities |
| `monte_carlo_summary.csv` | Monte Carlo parameters and percentiles |
| `monte_carlo_draws.csv` | All 10,000 draws (seed 1675): each bidder's value, the clearing price, who set it, and gross revenue |

## Mid-band data (from `scripts/export_csvs.py`)

| File | Contents |
| --- | --- |
| `a107_licenses.csv` | Every Auction 107 (3.7 GHz) license: market, block, bidder, gross and net bid, price per megahertz-pop |
| `a110_licenses.csv` | Every Auction 110 (3.45 GHz) license, same columns |

## Phase B analyses (from `scripts/analysis.py`)

| File | Contents |
| --- | --- |
| `model_validation.csv` | Independent Python model against the workbook for every scenario and license design |
| `bidder_count_grid.csv` | Revenue for 0–6 D2D by 0–6 terrestrial bidders, point estimates and simulated percentiles |
| `ntia_zone_validation.csv` | Zone model against NTIA Report 24-01 Table 11 (reference case) |
| `zone_counties.csv` | Each county's distance to the nearest NOAA site and zone membership |
| `zone_sweep.csv` | Revenue by zone radius, value kept inside zones, case, license design, and market-size curve (zone-free or observed) |
| `zone_pea_impact.csv` | The 25 PEAs with the most population inside zones at NTIA's distances |
| `aws3_zone_calibration.csv` | Auction 97 B1 prices with the share of each market inside US88 protection zones |
| `backtest.csv` | Split-half test of the market-size curve; Auction 113 out-of-sample checks |
| `income_check.csv` | Annual payment each benchmark implies at 7% (FCC method) and over a 15-year term |
| `adjacency_demand_reduction.csv` | When an adjacency premium or second-block value makes the lead D2D bidder bid for two |
| `package_threshold.csv` | Package-bid revenue when local bidders mount only part of their combined value |
| `tornado.csv` | One-at-a-time sensitivity of the central estimate |
| `fcc_ria_comparison.csv` | This estimate against the FCC's (FNPRM App. C) |
| `analysis_summary.csv` | Headline statistics quoted in the working paper |
| `zone_free_curve.csv` | Market-size elasticity and Auction 97 benchmark with the AWS-3 zone effect held out |
| `zone_free_designs.csv` | License designs on the observed and zone-free curves (sensitivity) |
| `stage_table.csv` | Price and revenue after each stage: central case in two stage orders, and the stressed case |
| `financing_wacc.csv` | Cost of capital at each benchmark's date and today, from FRED yields and stated CAPM inputs |
| `financing_test.csv` | Observed 2026-to-2015 price ratio, its bootstrap interval, and the ratio the financing adjustment predicts |
| `financing_sensitivity.csv` | Scenario revenue with every benchmark repriced to today's financing |
| `timing_sensitivity.csv` | Revenue if availability is delayed 0 to 3 years, by discount rate and scope |
| `zone_structural.csv` | Value kept inside a zone: six assumed factors against the calibrated value |
| `midband_reconciliation.csv` | Auctions 107 and 110 parsed and tied to published totals |
| `midband_crosscheck.csv` | Mid-band-anchored cross-check, by stage |
| `assumptions_register.csv` | Every input, value, basis, and evidence grade (paper Appendix A) |
