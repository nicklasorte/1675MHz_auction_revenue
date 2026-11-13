# 1675–1695 MHz auction revenue

This repository estimates FCC auction revenue for 20 megahertz at 1675–1695 MHz under the
Further Notice of Proposed Rulemaking (FNPRM) in WT Docket No. 26-284. It compares nationwide
licenses, Partial Economic Area (PEA) licenses, and PEA licenses with nationwide package bids, for
terrestrial UE uplink and direct-to-device (D2D) use.

Every revenue figure here is **before federal coordination and an upper bound**: coordination
zones around the four NOAA Data Collection System receive sites aren't modeled yet.

## Results (workbook v0.4, November 10, 2026)

Gross bids for two unpaired 10-megahertz blocks, with SpaceX, Amazon Leo, and AST SpaceMobile as
D2D bidders and AT&T, Verizon, T-Mobile, and Ligado as terrestrial bidders.

| Case | Nationwide | PEA only | PEA + packages |
|---|---|---|---|
| UE uplink | $4.07B | $4.65B | $4.65B |
| D2D downlink | $5.14B | $5.21B | $5.21B |

With two or fewer independent D2D bidders, or if D2D operators lease supplemental coverage from
space (SCS) rights instead of bidding, revenue is about $3.46B. See
[`docs/license-design-memo.md`](docs/license-design-memo.md) for the decision memo and
[`docs/1675-auction-valuation-plan.md`](docs/1675-auction-valuation-plan.md) for the full method
and sensitivities.

## Reproduce the analysis

Requirements: Python 3.10 or later, `openpyxl` (`pip install -r requirements.txt`), `pdftotext`
(poppler-utils), and LibreOffice for recalculation.

```bash
./reproduce.sh
```

The script runs five steps:

1. Extracts the Auction 97 tables from the FCC public notices with `pdftotext`.
2. Parses per-license results for Auctions 97 and 113 (`scripts/parse_auctions.py`).
3. Builds the workbook with live formulas (`scripts/build_workbook.py`).
4. Recalculates every formula in headless LibreOffice (`scripts/recalc.py`).
5. Verifies the `Checks` tab and the headline numbers (`scripts/verify.py`).

A clean run reproduces `outputs/1675-auction-valuation-v0.4.xlsx` exactly: all 35,402 non-empty
cells match, and the parsed CSVs are byte-identical to the originals. The run prints PASS, with two
checks PENDING until the transaction terms and FNPRM paragraph citations are verified.

## Repository layout

| Path | Contents |
|---|---|
| `reproduce.sh` | One-command rebuild |
| `scripts/` | Parser, workbook builder, recalculation, and verification |
| `data/raw/` | Unedited FCC source files (public notices and FCC Public Reporting System downloads) |
| `data/SOURCES.md` | Source URL and SHA-256 checksum for every raw file, plus the typed-in inputs |
| `data/processed/` | Per-license CSVs produced by `parse_auctions.py` |
| `outputs/` | Current workbook (v0.4); earlier versions in `outputs/archive/` |
| `docs/` | Valuation plan, red-team review, and the decision memo |

## How the model works

- **Benchmarks** come from the raw per-license data: Auction 97 unpaired 1695–1710 MHz prices for
  terrestrial uplink, the SpaceX/EchoStar purchase of those licenses for satellite uplink, and the
  Grain 800 MHz prices for D2D downlink.
- **Pricing:** with two blocks, the uniform clock price stops at the highest losing bid. SpaceX
  can bid for both blocks only if that leaves it more surplus (demand reduction).
- **PEA licensing:** carrier values by PEA follow a market-size curve fitted to Auction 97 B1
  prices (slope 0.65 on log population). D2D bidders lose the 1.21 national-portfolio premium
  measured from the EchoStar sale.
- **Package bids:** a nationwide package wins only if it beats the sum of the per-PEA bids for its
  block, and pays at least that sum.
- **Monte Carlo:** an illustrative simulation with a fixed seed (1675), computed in the build
  script and pasted into the workbook as values.

## Status and caveats

- Draft, pre-decisional analysis prepared with AI assistance. It needs human review by someone with
  auction experience before any figure is used.
- Federal coordination zones, the 5-megahertz band plan, and regional licenses aren't modeled.
- Transaction terms come from press releases and reports, not primary filings.
- FNPRM details come from Covington's summary of the October 8 draft, not the adopted text.
- The bidder list hasn't been signed off. Adding or dropping one D2D bidder moves the central
  estimate by about $0.6B.

`docs/1675-auction-redteam.md` records the red-team review of v0.1. Version 0.2 fixed its
main findings; the plan's red-team section lists what's still open.
