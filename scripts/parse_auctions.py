"""Parse FCC Auction 97 and 113 public data into clean CSVs.

Inputs (in the download dir passed as argv[1]):
  a97_win.txt  - pdftotext -layout of DA-15-131A2 (Auction 97 winning bids by license)
  a97_inv.txt  - pdftotext -layout of DA-14-1018A2 (Auction 97 license inventory with population)
  a113_results_by_license.csv, a113_market.csv - FCC PRS downloads
  a107_results_by_license.csv, a107_market.csv, a110_results_by_license.csv, a110_market.csv - FCC PRS downloads
Outputs (to argv[2]): a97_licenses.csv, a113_licenses.csv, a107_licenses.csv, a110_licenses.csv
"""
import csv
import re
import sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])

inv = {}
inv_re = re.compile(r"^(\S+)\s+(.+?)\s{2,}(AW-\S+)\s+(\S+)\s+([A-Z]\d?)\s+([\d,]+|-)\s+(\d+)\s")
for line in (src / "a97_inv.txt").read_text().splitlines():
    m = inv_re.match(line.strip())
    if m:
        market, name, lic, freq, block, pop, mhz = m.groups()
        inv[lic] = dict(market=market, market_name=name.strip(), block=block,
                        frequencies=freq, population_2010=0 if pop == "-" else int(pop.replace(",", "")), mhz=int(mhz))

win = {}
win_re = re.compile(r"^(AW-\S+)\s+(.+?)\s+(\d{1,3})\s{2,}(.+?)\s+(\d{10})\s+\$\s*([\d,\.]+)\s+\$\s*([\d,\.]+)")
for line in (src / "a97_win.txt").read_text().splitlines():
    m = win_re.match(line.strip())
    if m:
        lic, desc, rnd, bidder, frn, gross, net = m.groups()
        win[lic] = dict(round=int(rnd), bidder=bidder.strip(), frn=frn,
                        gross=float(gross.replace(",", "")), net=float(net.replace(",", "")))

with open(out / "a97_licenses.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["license", "market", "market_name", "block", "frequencies", "mhz", "population_2010",
                "sold", "bidder", "frn", "gross_bid", "net_bid", "gross_per_mhz_pop"])
    for lic, d in inv.items():
        x = win.get(lic)
        g = x["gross"] if x else 0.0
        w.writerow([lic, d["market"], d["market_name"], d["block"], d["frequencies"], d["mhz"],
                    d["population_2010"], "Y" if x else "N", x["bidder"] if x else "", x["frn"] if x else "",
                    g, x["net"] if x else 0.0, g / (d["mhz"] * d["population_2010"]) if x and d["population_2010"] else ""])

pops = {}
with open(src / "a113_market.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        pops[r["market"].strip()] = int(r["population"])
mhz113 = {"A1": 5, "B1": 10, "G": 10, "H": 10, "I": 10, "J": 20}
with open(src / "a113_results_by_license.csv", encoding="utf-8-sig") as f, \
        open(out / "a113_licenses.csv", "w", newline="") as g:
    w = csv.writer(g)
    w.writerow(["license", "market", "market_name", "block", "mhz", "population", "bidder",
                "bidding_credit_type", "gross_bid", "net_bid", "gross_per_mhz_pop"])
    for r in csv.DictReader(f):
        mk, b = r["market"].strip(), r["channel_block"].strip()
        p, gross = pops[mk], float(r["gross_license_price"])
        w.writerow([r["license"], mk, r["market_name"].strip(), b, mhz113[b], p, r["bidder"].strip(),
                    r["bidding_credit_type"].strip(), gross, float(r["net_license_price"]),
                    gross / (mhz113[b] * p) if p else ""])

# Auctions 107 (3.7 GHz, 14 blocks of 20 MHz) and 110 (3.45 GHz, 10 blocks of 10 MHz): mid-band cross-check
for aid, mhz, res_name, mkt_name, mcol, pcol in (
        (107, 20, "a107_results_by_license.csv", "a107_market.csv", "market_number", "market_population"),
        (110, 10, "a110_results_by_license.csv", "a110_market.csv", "market", "population")):
    pops_ = {}
    with open(src / mkt_name, encoding="utf-8-sig") as f_:
        for r in csv.DictReader(f_):
            pops_[r[mcol].strip()] = int(r[pcol])
    with open(src / res_name, encoding="utf-8-sig") as f_, open(out / f"a{aid}_licenses.csv", "w", newline="") as g_:
        w_ = csv.writer(g_)
        w_.writerow(["license", "market", "market_name", "block", "mhz", "population_2010", "bidder",
                     "gross_bid", "net_bid", "gross_per_mhz_pop"])
        for r in csv.DictReader(f_):
            mk = (r["market_number"] if aid == 107 else r["market"]).strip()
            blk = (r["block_final"] if aid == 107 else r["block"]).strip()
            gross = float(r["gross_license_price"])
            w_.writerow([r["license"], mk, r["market_name"].strip(), blk, mhz, pops_[mk], r["bidder"].strip(), gross,
                         float(r["net_license_price"]), gross / (mhz * pops_[mk])])

print(f"A97 inventory {len(inv)}, winners parsed {len(win)}, unmatched winners "
      f"{len(set(win) - set(inv))}")
