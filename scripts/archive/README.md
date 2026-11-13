# Archived build scripts

These scripts built the earlier workbooks in `outputs/archive/`. Use `scripts/build_workbook.py` (v0.4) for current work.

| Script | Builds | Usage |
|---|---|---|
| `build_workbook_v01.py` | v0.1: nationwide only, press-report benchmarks, no raw data | `python3 build_workbook_v01.py` (writes to the current directory) |
| `build_workbook_v02.py` | v0.2: raw Auction 97 and 113 data, demand reduction, Monte Carlo | `python3 build_workbook_v02.py data/processed out.xlsx` |
| `build_workbook_v03.py` | v0.3: adds nationwide vs PEA licensing | `python3 build_workbook_v03.py data/processed out.xlsx data/raw/fcc_pea/a110_market.csv` |
