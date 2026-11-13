"""Recalculate every formula in an .xlsx with headless LibreOffice and report formula errors.

Usage: python scripts/recalc.py <in.xlsx> [<out.xlsx>]

openpyxl writes formulas without cached values. scripts/build_workbook.py sets the workbook to
calculate fully on open, so a headless LibreOffice round trip computes and stores every value.
pandas, openpyxl (data_only=True), and scripts/verify.py can then read the results. With no
<out.xlsx>, the input file is overwritten. Opening the file in Excel and saving it works too.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from openpyxl import load_workbook

ERRORS = ("#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NUM!", "#NULL!", "Err:502", "Err:504")


def soffice():
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    sys.exit("LibreOffice (soffice) not found. Install it, or open the workbook in Excel and save.")


def main():
    src = Path(sys.argv[1]).resolve()
    dst = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src
    with tempfile.TemporaryDirectory() as profile, tempfile.TemporaryDirectory() as outdir:
        subprocess.run([soffice(), f"-env:UserInstallation=file://{profile}", "--headless", "--norestore",
                        "--convert-to", "xlsx:Calc MS Excel 2007 XML", "--outdir", outdir, str(src)],
                       check=True, timeout=600, capture_output=True)
        shutil.move(str(Path(outdir) / src.name), dst)
    values = load_workbook(dst, data_only=True)
    formulas = load_workbook(dst)
    n_formulas, empty, bad = 0, 0, []
    for ws in formulas.worksheets:
        vs = values[ws.title]
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    n_formulas += 1
                    v = vs[c.coordinate].value
                    if v is None:
                        empty += 1
                    elif isinstance(v, str) and v in ERRORS:
                        bad.append(f"{ws.title}!{c.coordinate} {v}")
    print(f"{dst.name}: {n_formulas} formulas, {len(bad)} errors, {empty} blank (formulas that return an empty string)")
    for b in bad[:50]:
        print("  ", b)
    if n_formulas and empty == n_formulas:
        sys.exit("Nothing was calculated. Check the LibreOffice installation.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
