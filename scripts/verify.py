"""Verify a recalculated workbook: every test on the Checks tab passes and the headline numbers hold.

Usage: python scripts/verify.py <recalculated.xlsx>

Exit code 0 means every check passed (PENDING items are reported, not failed).
"""
import sys

from openpyxl import load_workbook

# Headline results as delivered on November 10, 2026 (gross bids, $, before federal coordination).
EXPECTED = {
    ("Scenarios", "B47"): 4073638216,   # S1 central (nationwide)
    ("Scenarios", "C47"): 5142857143,   # S2 D2D downlink value
    ("Scenarios", "I47"): 3460286484,   # S8 lease-only SCS
    ("License_Area", "C20"): 4649631172,  # UE uplink, PEA only
    ("License_Area", "C21"): 5212968610,  # D2D downlink, PEA only
    ("License_Area", "B78"): 4649631172,  # UE uplink, PEA + packages
    ("License_Area", "C78"): 5212968610,  # D2D downlink, PEA + packages
    ("Evidence", "B7"): 41329673325,    # Auction 97 net bids (published)
    ("Evidence", "B25"): 3572889200,    # Auction 113 gross bids (published)
}
TOL = 1.0  # dollars


def main():
    wb = load_workbook(sys.argv[1], data_only=True)
    ok = True
    if wb["Scenarios"]["B47"].value is None:
        sys.exit("No cached values. Run scripts/recalc.py on the workbook first.")
    ws = wb["Checks"]
    print("Checks tab")
    for r in range(5, ws.max_row + 1):
        label, status = ws[f"A{r}"].value, ws[f"B{r}"].value
        if not label or status in (None, "Status"):
            continue
        if label.startswith("Logic guards"):
            print("  -- logic guards (informational) --")
            continue
        print(f"  {status:8} {label}")
        if status == "FAIL":
            ok = False
    print("Headline numbers")
    for (sheet, cell), want in EXPECTED.items():
        got = wb[sheet][cell].value
        good = isinstance(got, (int, float)) and abs(got - want) <= TOL
        ok &= good
        print(f"  {'OK ' if good else 'BAD'} {sheet}!{cell}: {got:,.0f} (expected {want:,.0f})")
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
