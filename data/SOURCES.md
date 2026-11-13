# Data sources

`python scripts/download_raw.py` downloads every file below and checks it against the SHA-256 listed here (`--force` re-downloads). A mismatch means the publisher changed the file after it was downloaded (November 10 or 13, 2026).

All raw files are public federal records (FCC, NTIA, Census Bureau, eCFR), downloaded November 10 or 13, 2026, and committed unedited. The
SHA-256 checksum lets you confirm that a fresh download matches the committed copy.

## FCC Auction 97 (AWS-3, 2015)

| File | What it is | Source | SHA-256 |
|---|---|---|---|
| `raw/fcc_auction97/DA-15-131A1.pdf` | Closing public notice | [DA 15-131](https://docs.fcc.gov/public/attachments/DA-15-131A1.pdf) | `d29fadd0a8a28049b8fafd68d32310c31ab30771e1c7edaa6e5eb891a9d06be2` |
| `raw/fcc_auction97/DA-15-131A2.pdf` | Attachment A: winning bids by license | [DA 15-131 Att. A](https://docs.fcc.gov/public/attachments/DA-15-131A2.pdf) | `7418b6d0e1dfd7cd8955abc8521cb669ea0bc4ce2098a5d327a6181f36a0b759` |
| `raw/fcc_auction97/DA-14-1018A2.pdf` | Attachment A: license inventory with 2010 population and MHz | [DA 14-1018 Att. A](https://docs.fcc.gov/public/attachments/DA-14-1018A2.pdf) | `6a0a3707eff5c16bd4536ca15cef401d88f3a18cfebb7c2360aaf218b3711111` |

## FCC Auction 113 (AWS-3, 2026)

| File | What it is | Source | SHA-256 |
|---|---|---|---|
| `raw/fcc_auction113/DA-26-633A1.pdf` | Closing public notice | [DA 26-633](https://docs.fcc.gov/public/attachments/DA-26-633A1.pdf) | `31102bff23634f6a5ddda751d655a1f37731acc95be2edc0ff6b81fd983ff24f` |
| `raw/fcc_auction113/DA-26-633A2.pdf` | Attachment | [DA 26-633 Att.](https://docs.fcc.gov/public/attachments/DA-26-633A2.pdf) | `e849db807101add8178975352d7b44a6ac31b61cf37e87c1b8609cfc5a41ed57` |
| `raw/fcc_auction113/DA-26-633A3.pdf` | Attachment | [DA 26-633 Att.](https://docs.fcc.gov/public/attachments/DA-26-633A3.pdf) | `d3a16b7f9cd1f67560ff97d147524448ac7b97487b74b3c5999b54d5d23a0648` |
| `raw/fcc_auction113/a113_results_by_license.csv` | Results by license | [FCC PRS download](https://auctiondata.fcc.gov/public/projects/auction113/reports/results_by_license/download) | `e65169fd38b64933d71338874a4befa6f6681fffdc9cc10db84e58e6c299ff3c` |
| `raw/fcc_auction113/a113_market.csv` | Markets with the population the FCC used | [FCC PRS download](https://auctiondata.fcc.gov/public/projects/auction113/reports/market/download) | `bc0ec173c96b9f3c4c3cfdb810cd235a44240a716ef5ac2b40c9f7b84233b7cc` |

## Partial Economic Areas (PEAs)

| File | What it is | Source | SHA-256 |
|---|---|---|---|
| `raw/fcc_pea/a110_market.csv` | 406 contiguous-U.S. PEAs with 2010 population (Auction 110 market file) | [FCC PRS download](https://auctiondata.fcc.gov/public/projects/auction110/reports/market/download) | `87a5079f3b12c88aadda43fc63f6d5ac5433f19b6a3045aefc7c7d3ef57473ec` |

## Added in v0.5 (downloaded November 13, 2026)

| File | What it is | Source | SHA-256 |
|---|---|---|---|
| `raw/fcc_fnprm/FCC-26-70A1.pdf` | Adopted FNPRM, including App. C (the FCC's revenue estimate) | [FCC 26-70](https://docs.fcc.gov/public/attachments/FCC-26-70A1.pdf) | `b700b70af11ff45bd5e353c4e100efdee53e373f45ba0831b40ca7dc63e952b0` |
| `raw/fcc_pea/DA-14-759A1.pdf` | PEA public notice | [DA 14-759](https://docs.fcc.gov/public/attachments/DA-14-759A1.pdf) | `5c95713ad59d1f938a0c2817224cdbb870d4433d5b2a790476081920c5109c9b` |
| `raw/fcc_pea/DA-14-759A2.pdf` | App. A: PEAs with Economic Area numbers | [DA 14-759 App. A](https://docs.fcc.gov/public/attachments/DA-14-759A2.pdf) | `d3303518e88e3798d1beffd5246c03467d6e01244cd35f550e3d961c30f29f2a` |
| `raw/fcc_pea/DA-14-759A3.pdf` | App. B: counties by PEA | [DA 14-759 App. B](https://docs.fcc.gov/public/attachments/DA-14-759A3.pdf) | `3e28df61c669dbff4a71e0e852a5c93d3785de228132bc733afed47472c07bef` |
| `raw/fcc_transactions/FCC-11-188A1.pdf` | Order approving Qualcomm's 700 MHz D and E Block sale to AT&T | [FCC 11-188](https://docs.fcc.gov/public/attachments/FCC-11-188A1.pdf) | `9466a5dd055a0464e0b891b0377359c5c76f31e12d71209bef2bf8398b37f57f` |
| `raw/fcc_transactions/FCC-07-16A1.pdf` | Order on OP LLC (Crown Castle), licensee of 1670–1675 MHz | [FCC 07-16](https://docs.fcc.gov/public/attachments/FCC-07-16A1.pdf) | `bb75c15e85c8da3eb882566aff301b50394473e98b43c5bdaf0fb1ac35e9a403` |
| `raw/ntia/1675-mhz-identification-letter.pdf` | NTIA letter identifying 1675–1680 MHz and the four protected sites | [NTIA](https://www.ntia.gov/sites/default/files/2026-03/1675-mhz-identification-letter.pdf) | `af07659bbe44bd7a9356171cbf0da5bbc90359ebf39fd4adeb31e66cd5f85f18` |
| `raw/ntia/ntia_report_24-01_spres_fo.pdf` | NTIA Report 24-01: site coordinates (Table 3), coordination distances (Table 9), PEA impact (Table 11) | [NTIA](https://www.ntia.gov/sites/default/files/2025-10/ntia_report_24-01_12-2024-1675mhz-rev3-ntia-spres-fo.pdf) | `8230cc382e8753461ef8d0ad979285e40574b406d8bc973c7af5ee17b54dee5d` |
| `raw/census/CenPop2020_Mean_CO.txt` | 2020 county populations and population-weighted centers | [Census Bureau](https://www2.census.gov/geo/docs/reference/cenpop2020/county/CenPop2020_Mean_CO.txt) | `4f754a3bda9714e5820d73bfac44ef1dab2b8c371f6c136305474cda7a752014` |
| `raw/census/cb_2020_us_county_20m.zip` | 2020 county boundaries (map only) | [Census Bureau](https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_county_20m.zip) | `9394913edbd6f72791b06b84509e59ea2d275d10b73ae27ef87df3bdb061890c` |
| `raw/census/cb_2020_us_state_20m.zip` | 2020 state boundaries (map only) | [Census Bureau](https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_state_20m.zip) | `1d872779cbfa2c2bf828850664aa9593a35844205e2e4bed5aeb78affb8da050` |
| `raw/ecfr/title47_section2.106_2026-11-01.xml` | 47 CFR 2.106, including footnote US88 protection zones | [eCFR API](https://www.ecfr.gov/api/versioner/v1/full/2026-11-01/title-47.xml?part=2&section=2.106) | `660ecc8861147243c3fce116b5ab706976ef304f41c1ecc01497c864f6ceb33e` |

`scripts/parse_geo.py` turns these into `data/processed/` tables. Two NTIA tables are typed into
`parse_geo.py` from the report (site coordinates and distances; the Table 11 reference case).

## Other inputs typed into the workbook

These values sit on the workbook's `Inputs` and `Transactions` tabs, each with its source beside it:

- U.S. resident population, 2020 Census (331,449,281), and Alaska and Hawaii populations: U.S. Census Bureau.
- Published Auction 97 averages ($0.52 unpaired, $2.72 paired per MHz-pop): Cramton and Sujarittanonta, "Bidding and Prices in the AWS-3 Auction" (2015). Used only as an independent cross-check.
- SpaceX/EchoStar unpaired AWS-3 price (about $2.6 billion in SpaceX stock): [EchoStar press release, November 6, 2025](https://ir.echostar.com/news-releases/news-release-details/echostar-agrees-sell-full-unpaired-aws-3-spectrum-license).
- SpaceX/Grain 800 MHz price (about $8 billion reported) and the earlier market price (about $3.6 billion): [Fierce Network, October 2026](https://www.fierce-network.com/wireless/spacexs-800-mhz-spectrum-grab-threatens-big-3-mobile-carriers).
- Amazon/Globalstar ($11.57 billion; cross-check only, not used in any benchmark).
- Qualcomm 700 MHz D and E Blocks to AT&T ($1.925 billion): FCC 11-188, paras. 1 and 15 (verified).
- 1670–1675 MHz lease ($13 million a year): [TV Technology, July 27, 2007](https://www.tvtechnology.com/news/crown-castle-leasing-modeo-spectrum-for-13-million-per-year); capitalized at 7% (FNPRM App. C, para. 4).
- FNPRM proposals: FCC 26-70, cited by paragraph on the workbook's `FNPRM` tab.

Except the Qualcomm sale, transaction terms haven't been verified against primary filings; the
workbook's `Checks` tab shows this as PENDING.
