"""Download every FCC source file used in the analysis and check it against the recorded SHA-256.

Usage: python scripts/download_raw.py [--dest data/raw] [--force]

Without --force, files already present are only checked, not downloaded again. A checksum mismatch
means the FCC changed the file after November 10, 2026; the script reports it and exits non-zero.
"""
import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

FILES = [
    ("fcc_auction97/DA-15-131A1.pdf", "https://docs.fcc.gov/public/attachments/DA-15-131A1.pdf",
     "d29fadd0a8a28049b8fafd68d32310c31ab30771e1c7edaa6e5eb891a9d06be2"),
    ("fcc_auction97/DA-15-131A2.pdf", "https://docs.fcc.gov/public/attachments/DA-15-131A2.pdf",
     "7418b6d0e1dfd7cd8955abc8521cb669ea0bc4ce2098a5d327a6181f36a0b759"),
    ("fcc_auction97/DA-14-1018A2.pdf", "https://docs.fcc.gov/public/attachments/DA-14-1018A2.pdf",
     "6a0a3707eff5c16bd4536ca15cef401d88f3a18cfebb7c2360aaf218b3711111"),
    ("fcc_auction113/DA-26-633A1.pdf", "https://docs.fcc.gov/public/attachments/DA-26-633A1.pdf",
     "31102bff23634f6a5ddda751d655a1f37731acc95be2edc0ff6b81fd983ff24f"),
    ("fcc_auction113/DA-26-633A2.pdf", "https://docs.fcc.gov/public/attachments/DA-26-633A2.pdf",
     "e849db807101add8178975352d7b44a6ac31b61cf37e87c1b8609cfc5a41ed57"),
    ("fcc_auction113/DA-26-633A3.pdf", "https://docs.fcc.gov/public/attachments/DA-26-633A3.pdf",
     "d3a16b7f9cd1f67560ff97d147524448ac7b97487b74b3c5999b54d5d23a0648"),
    ("fcc_auction113/a113_results_by_license.csv",
     "https://auctiondata.fcc.gov/public/projects/auction113/reports/results_by_license/download",
     "e65169fd38b64933d71338874a4befa6f6681fffdc9cc10db84e58e6c299ff3c"),
    ("fcc_auction113/a113_market.csv",
     "https://auctiondata.fcc.gov/public/projects/auction113/reports/market/download",
     "bc0ec173c96b9f3c4c3cfdb810cd235a44240a716ef5ac2b40c9f7b84233b7cc"),
    ("fcc_pea/a110_market.csv",
     "https://auctiondata.fcc.gov/public/projects/auction110/reports/market/download",
     "87a5079f3b12c88aadda43fc63f6d5ac5433f19b6a3045aefc7c7d3ef57473ec"),
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default="data/raw")
    ap.add_argument("--force", action="store_true", help="download even if the file exists")
    args = ap.parse_args()
    ok = True
    for rel, url, want in FILES:
        path = Path(args.dest) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        action = "kept"
        if args.force or not path.exists():
            req = urllib.request.Request(url, headers={"User-Agent": "1675MHz_auction_revenue reproduction"})
            with urllib.request.urlopen(req, timeout=120) as r:
                path.write_bytes(r.read())
            action = "downloaded"
        got = sha256(path)
        match = got == want
        ok &= match
        print(f"{'OK      ' if match else 'MISMATCH'} {action:10} {rel}")
        if not match:
            print(f"         expected {want}\n         got      {got}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
