# 1675–1695 MHz auction revenue

**DRAFT//PRE-DECISIONAL.** This repository estimates FCC auction revenue (gross bids) for the two
unpaired 10-megahertz blocks at 1675–1695 MHz proposed in the Further Notice of Proposed Rulemaking
(FNPRM), FCC 26-70, WT Docket No. 26-284. It compares nationwide licenses, Partial Economic Area (PEA)
licenses, and PEA licenses with nationwide package bids, and models the coordination zones around the
four NOAA Data Collection System receive sites, which constrain terrestrial base-station downlink only. The 2020–2025 MHz block in the same proposal is out of
scope.

Start with the working paper, [`docs/working-paper.md`](docs/working-paper.md) (v0.6, 14 figures; also as
[`docs/working-paper.docx`](docs/working-paper.docx)).

## Results (v0.6, November 17, 2026)

Every range is conditional on stated assumptions; none is a confidence interval.

| Measure | Gross bids |
|---|---|
| Central estimate (3 D2D and 4 terrestrial bidders); NOAA zones don't change it | $4.07B |
| Simulated 10th to 90th percentile | $3.33B–$4.50B |
| Two or fewer D2D bidders, or SCS leased instead of bid | $3.46B |
| Terrestrial downlink sets the price (2 D2D): no zones / half / full NTIA distances | $3.19B / $2.99B / $2.38B |
| Central estimate repriced to today's financing (sensitivity) | $3.88B |
| Central estimate with 1 / 2 / 3 years of delay at 7% (sensitivity) | $3.81B / $3.56B / $3.33B |
| Mid-band cross-check (Auction 107 / Auction 110 anchors, repriced) | $4.65B / $3.71B |
| FCC's own estimate for the same 20 MHz (FNPRM App. C method) | $17.0B |

| License design, no zones | Nationwide | PEA only | PEA + packages |
|---|---|---|---|
| UE uplink | $4.07B | $4.65B | $4.65B |
| D2D downlink | $5.14B | $5.21B | $5.21B |

The FCC's estimate is higher mainly because it applies the Auction 113 average price, which is 98%
paired spectrum; unpaired spectrum next door sold for one-fifth as much. PEA licenses with package
bids match or beat the other designs in every case tested, including with zones, if at least three
D2D bidders compete. The zones reduce revenue only when terrestrial downlink bidders set the price.

## Documents

| Document | What it is |
|---|---|
| [`docs/working-paper.md`](docs/working-paper.md) | Evidence, method, results, zones, limitations, numbers ledger, figures |
| [`docs/dataviz-plan.md`](docs/dataviz-plan.md) | Ten ways to show the results, and which are built |
| [`docs/literature-review.md`](docs/literature-review.md) | Related work on valuation, auctions, sharing, and SCS |
| [`docs/next-phase-plan.md`](docs/next-phase-plan.md) | The plan this version carries out, with status |
| [`docs/7ghz-method-lessons-plan.md`](docs/7ghz-method-lessons-plan.md) | Plan to apply lessons from the 7 GHz auction-value report |
| [`docs/license-design-memo.md`](docs/license-design-memo.md) | One-page decision memo (v0.4 copy) |
| [`docs/1675-auction-valuation-plan.md`](docs/1675-auction-valuation-plan.md), [`docs/1675-auction-redteam.md`](docs/1675-auction-redteam.md) | Original plan and red-team review |

## Reproduce the analysis

Requirements: Python 3.10 or later (`pip install -r requirements.txt`: openpyxl, matplotlib, numpy,
pyshp, python-docx), `pdftotext` (poppler-utils), and LibreOffice.

```bash
./reproduce.sh
```

The script:

1. Downloads any missing source file and checks its SHA-256 (`scripts/download_raw.py`).
2. Extracts the FCC tables with `pdftotext` and parses Auctions 97 and 113 (`scripts/parse_auctions.py`)
   and the PEA, county, protection-zone, and NTIA tables (`scripts/parse_geo.py`).
3. Builds the workbook with live formulas (`scripts/build_workbook.py`), recalculates it in
   LibreOffice (`scripts/recalc.py`), and verifies the `Checks` tab and headline numbers
   (`scripts/verify.py`).
4. Exports every dataset to `data/csv/` and ties it to the published FCC totals and the workbook
   (`scripts/export_csvs.py`, `scripts/check_csvs.py`).
5. Runs the independent Python model and the analyses: bidder counts, NOAA zones, AWS-3 zone
   calibration and the zone-free curve, financing and timing sensitivities, structural zone check,
   mid-band cross-check, stage table, backtest, stress tests, tornado, and the FCC comparison
   (`scripts/analysis.py`). It stops if the Python model doesn't reproduce the workbook.
6. Rebuilds all figures from `data/csv/` (`scripts/make_figures.py`); reruns write identical files.
7. Checks the paper's dollar figures against `data/csv/` (`scripts/check_paper.py`) and builds the Word
   version (`scripts/make_docx.py`; needs pandoc and python-docx).

The run prints PASS, with one check PENDING until the remaining transaction terms are verified in
primary filings.

## Repository layout

| Path | Contents |
|---|---|
| `reproduce.sh` | One-command rebuild |
| `scripts/` | Download, parsers, workbook builder, recalculation, verification, export, analyses, figures, paper check, Word build |
| `data/raw/` | Unedited source files (FCC, NTIA, Census Bureau, eCFR) |
| `data/SOURCES.md` | Source URL and SHA-256 for every raw file, plus typed-in inputs |
| `data/processed/` | Parsed tables |
| `data/csv/` | Every dataset used, and every analysis result (see `data/csv/README.md`) |
| `figures/` | Figures as PNG, SVG, and PDF |
| `outputs/` | Current workbook (v0.5); earlier versions in `outputs/archive/` |
| `docs/` | Working paper and supporting documents |

## Status and caveats

- Draft, pre-decisional analysis prepared with AI assistance. It needs review by someone with
  auction experience before any figure is used, and NOAA-related statements need IRAC coordination.
- Zones apply to terrestrial base-station downlink only. Zone sizes use NTIA's coordination distances,
  which NTIA calls conservative, and smaller fractions. The cost of a zone is calibrated on 19 AWS-3 markets.
- Except the Qualcomm 700 MHz sale (FCC 11-188), transaction terms come from releases and press reports.
- Bidders are modeled as counts by class, not named firms.
- Financing, availability delay, and the structural zone factors are sensitivities with assumed inputs;
  `docs/working-paper.md` Appendix A grades every input as observed, calibrated, or assumed.
- The zone, financing, timing, and mid-band analyses run in the Python layer, not the workbook.
- The decision memo is still the v0.4 copy and names bidders; it needs a refresh to match v0.5.
