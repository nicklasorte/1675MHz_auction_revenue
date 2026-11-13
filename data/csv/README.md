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
| `transactions.csv` | SpaceX/EchoStar, SpaceX/Grain (two prices), and Amazon/Globalstar (cross-check only); terms are from press reports and are flagged PENDING until verified in primary filings |
| `bidders.csv` | Bidders, class (D2D or carrier), value multiplier, and why each is credible |

## Calculated results (from the recalculated workbook)

| File | Contents |
| --- | --- |
| `evidence.csv` | Reconciliation to published totals and the fitted measures (slope 0.65, premium 1.21, flat-price ratio 0.99) |
| `benchmarks.csv` | Low, base, and high price per megahertz-pop for each use |
| `scenarios.csv` | Scenarios S1–S9: switches, benchmark values, clearing price, and gross revenue |
| `revenue_definitions.csv` | Gross bids, net bids at two credit rates, and net of NOAA costs, by scenario |
| `pea_results.csv` | Each PEA's population, carrier value, price, revenue, and winner class for uplink and downlink |
| `license_area_results.csv` | Nationwide, PEA, and PEA-plus-package revenue, with the exposure-discount and market-size sensitivities |
| `monte_carlo_summary.csv` | Monte Carlo parameters and percentiles |
| `monte_carlo_draws.csv` | All 10,000 draws (seed 1675): each bidder's value, the clearing price, who set it, and gross revenue |
