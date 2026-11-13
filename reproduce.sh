#!/usr/bin/env bash
# Rebuild the 1675-1695 MHz auction valuation workbook from the FCC source files in data/raw.
# Requires: Python 3.10+, openpyxl, poppler-utils (pdftotext), and LibreOffice for recalculation.
set -euo pipefail
cd "$(dirname "$0")"

OUT=outputs/1675-auction-valuation-v0.5.xlsx
INTERIM=data/interim
mkdir -p "$INTERIM" data/processed

echo "0. Check the FCC source files (downloads any that are missing)"
python3 scripts/download_raw.py

echo "1. Extract Auction 97 tables from the FCC public notices"
pdftotext -layout data/raw/fcc_auction97/DA-15-131A2.pdf "$INTERIM/a97_win.txt"
pdftotext -layout data/raw/fcc_auction97/DA-14-1018A2.pdf "$INTERIM/a97_inv.txt"
cp data/raw/fcc_auction113/a113_results_by_license.csv data/raw/fcc_auction113/a113_market.csv "$INTERIM/"

echo "2. Parse per-license results"
python3 scripts/parse_auctions.py "$INTERIM" data/processed
pdftotext -layout data/raw/fcc_pea/DA-14-759A2.pdf "$INTERIM/pea_ea.txt"
pdftotext -layout data/raw/fcc_pea/DA-14-759A3.pdf "$INTERIM/pea_county.txt"
python3 scripts/parse_geo.py "$INTERIM" data/raw data/processed

echo "3. Build the workbook"
python3 scripts/build_workbook.py data/processed "$OUT" data/raw/fcc_pea/a110_market.csv data/csv/monte_carlo_draws.csv

echo "4. Recalculate formulas"
python3 scripts/recalc.py "$OUT"

echo "5. Verify checks and headline numbers"
python3 scripts/verify.py "$OUT"

echo "6. Export every dataset used in the calculation to data/csv"
python3 scripts/export_csvs.py data/processed data/raw/fcc_pea/a110_market.csv "$OUT" data/csv
python3 scripts/check_csvs.py data/csv "$OUT"

echo "7. Run the Phase B analyses (independent Python model, zones, sensitivities) into data/csv"
python3 scripts/analysis.py data/processed data/raw/fcc_pea/a110_market.csv "$OUT" data/csv

echo "8. Rebuild the working-paper figures from data/csv"
python3 scripts/make_figures.py data/csv figures
