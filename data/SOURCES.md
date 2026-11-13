# Data sources

All raw files are public FCC records, downloaded November 10, 2026, and committed unedited. The
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

## Other inputs typed into the workbook

These values sit on the workbook's `Inputs` and `Transactions` tabs, each with its source beside it:

- U.S. resident population, 2020 Census (331,449,281), and Alaska and Hawaii populations: U.S. Census Bureau.
- Published Auction 97 averages ($0.52 unpaired, $2.72 paired per MHz-pop): Cramton et al., "Bidding and Prices in the AWS-3 Auction" (2015). Used only as an independent cross-check.
- SpaceX/EchoStar unpaired AWS-3 price (about $2.6 billion in SpaceX stock): [EchoStar press release, November 6, 2025](https://ir.echostar.com/news-releases/news-release-details/echostar-agrees-sell-full-unpaired-aws-3-spectrum-license).
- SpaceX/Grain 800 MHz price (about $8 billion reported) and the earlier market price (about $3.6 billion): [Fierce Network, October 2026](https://www.fierce-network.com/wireless/spacexs-800-mhz-spectrum-grab-threatens-big-3-mobile-carriers).
- Amazon/Globalstar ($11.57 billion; cross-check only, not used in any benchmark).
- FNPRM proposals (band plan, license-area options, package bids): FCC 26-70, WT Docket No. 26-284, as summarized by [Covington, October 13, 2026](https://www.insideglobaltech.com/2026/10/13/fcc-proposes-to-auction-spectrum-for-terrestrial-and-space-based-broadband-services/).

Transaction terms haven't been verified against primary filings yet; the workbook's `Checks` tab
shows this as PENDING.
