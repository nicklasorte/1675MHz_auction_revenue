"""Download every FCC source file used in the analysis and check it against the recorded SHA-256.

Usage: python scripts/download_raw.py [--dest data/raw] [--force]

Without --force, files already present are only checked, not downloaded again. A checksum mismatch
means the FCC changed the file after November 10, 2026; the script reports it and exits non-zero.
"""
import argparse
import gzip
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
    # v0.5 additions
    ("fcc_fnprm/FCC-26-70A1.pdf", "https://docs.fcc.gov/public/attachments/FCC-26-70A1.pdf",
     "b700b70af11ff45bd5e353c4e100efdee53e373f45ba0831b40ca7dc63e952b0"),
    ("fcc_pea/DA-14-759A1.pdf", "https://docs.fcc.gov/public/attachments/DA-14-759A1.pdf",
     "5c95713ad59d1f938a0c2817224cdbb870d4433d5b2a790476081920c5109c9b"),
    ("fcc_pea/DA-14-759A2.pdf", "https://docs.fcc.gov/public/attachments/DA-14-759A2.pdf",
     "d3303518e88e3798d1beffd5246c03467d6e01244cd35f550e3d961c30f29f2a"),
    ("fcc_pea/DA-14-759A3.pdf", "https://docs.fcc.gov/public/attachments/DA-14-759A3.pdf",
     "3e28df61c669dbff4a71e0e852a5c93d3785de228132bc733afed47472c07bef"),
    ("fcc_transactions/FCC-11-188A1.pdf", "https://docs.fcc.gov/public/attachments/FCC-11-188A1.pdf",
     "9466a5dd055a0464e0b891b0377359c5c76f31e12d71209bef2bf8398b37f57f"),
    ("fcc_transactions/FCC-07-16A1.pdf", "https://docs.fcc.gov/public/attachments/FCC-07-16A1.pdf",
     "bb75c15e85c8da3eb882566aff301b50394473e98b43c5bdaf0fb1ac35e9a403"),
    ("ntia/1675-mhz-identification-letter.pdf",
     "https://www.ntia.gov/sites/default/files/2026-03/1675-mhz-identification-letter.pdf",
     "af07659bbe44bd7a9356171cbf0da5bbc90359ebf39fd4adeb31e66cd5f85f18"),
    ("ntia/ntia_report_24-01_spres_fo.pdf",
     "https://www.ntia.gov/sites/default/files/2025-10/ntia_report_24-01_12-2024-1675mhz-rev3-ntia-spres-fo.pdf",
     "8230cc382e8753461ef8d0ad979285e40574b406d8bc973c7af5ee17b54dee5d"),
    ("census/CenPop2020_Mean_CO.txt",
     "https://www2.census.gov/geo/docs/reference/cenpop2020/county/CenPop2020_Mean_CO.txt",
     "4f754a3bda9714e5820d73bfac44ef1dab2b8c371f6c136305474cda7a752014"),
    ("census/cb_2020_us_county_20m.zip", "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_county_20m.zip",
     "9394913edbd6f72791b06b84509e59ea2d275d10b73ae27ef87df3bdb061890c"),
    ("census/cb_2020_us_state_20m.zip", "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_state_20m.zip",
     "1d872779cbfa2c2bf828850664aa9593a35844205e2e4bed5aeb78affb8da050"),
    ("ecfr/title47_section2.106_2026-11-01.xml",
     "https://www.ecfr.gov/api/versioner/v1/full/2026-11-01/title-47.xml?part=2&section=2.106",
     "660ecc8861147243c3fce116b5ab706976ef304f41c1ecc01497c864f6ceb33e"),
    # v0.6 additions: mid-band cross-check (Auctions 107 and 110) and financing conditions (FRED).
    # FRED files are snapshots taken November 13, 2026; FRED can revise a series, so the snapshot in the
    # repository is the record and a fresh download may legitimately differ.
    ("fcc_auction107/a107_results_by_license.csv",
     "https://auctiondata.fcc.gov/public/projects/auction107/reports/results_by_license/download",
     "83cc9c3da93fcd43246fa2d7aacb37a53a78be50e7e7b10e34f725bf73599777"),
    ("fcc_auction107/a107_market.csv",
     "https://auctiondata.fcc.gov/public/projects/auction107/reports/market/download",
     "a045fb0816dde3ac17ef050cb0d4452c8a49efe75ebe8b49ef816b91a6487767"),
    ("fcc_auction110/a110_results_by_license.csv",
     "https://auctiondata.fcc.gov/public/projects/auction110/reports/results_by_license/download",
     "66f873c5244b0cd781d94b8ea056ebe07b3138119d7cb441c15084a4b0986ad8"),
    ("fred/DGS10.csv", "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10",
     "b9212adabc0b51a0e942c38a91dd4e61014d20c1ea83a26723e31024751b792d"),
    ("fred/DBAA.csv", "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DBAA",
     "f113063758c2139191f39307f8b8fc75a6fcec1ca16603eef855cd1c64dcdefc"),
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
            req = urllib.request.Request(url, headers={"User-Agent": "1675MHz_auction_revenue reproduction",
                                                       "Accept-Encoding": "gzip"})  # eCFR requires compression
            with urllib.request.urlopen(req, timeout=180) as r:
                body = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                path.write_bytes(body)
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
