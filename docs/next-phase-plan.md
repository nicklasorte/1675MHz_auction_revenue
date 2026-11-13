**DRAFT//PRE-DECISIONAL**

# 1675–1695 MHz auction revenue: plan for the next phase of analysis and the working paper

November 13, 2026. Prepared with AI assistance. Reviewer: [CONFIRM].

This plan follows workbook v0.4 and the working paper (`docs/working-paper.md`). It lists what to
add, in priority order, with the public data each item needs and the check that shows it worked.
The literature review behind several items is in `docs/literature-review.md`.

## Bottom line

Three findings from the literature and policy search change the scope, so they come first:

1. **NTIA has identified only 1675–1680 MHz so far.** Its February 26, 2026 letter to the FCC
   identifies 5 megahertz under P.L. 119-21 and says NTIA is still studying 1680–1695 MHz.[1] The
   model's 20-megahertz base case is conditional on that study.
2. **NTIA framed the band as terrestrial downlink.** The letter recommends the 1670–1675 MHz
   downlink emission limits and per-base-station coordination using an NTIA software tool.[1] The
   model suspends terrestrial downlink for lack of a comparable. Two candidate unpaired-downlink
   comparables now exist (item 2).
3. **The FNPRM covers 25 megahertz, not 20.** It pairs 1675–1695 MHz with 2020–2025 MHz.[2] The
   current scope excludes 2020–2025 MHz. That's a decision for Nick, because SpaceX holds adjacent
   spectrum next to both bands.

Then come the analysis upgrades. The most valuable is turning the "upper bound" into an estimate by
modeling the four NOAA coordination zones and calibrating the price effect of federal sharing on
Auctions 105 and 110.

## Decisions needed from Nick

| # | Decision | Options | Why it matters |
|---|---|---|---|
| D1 | Base case band | 20 MHz (as proposed in the FNPRM) or 5 MHz (as identified by NTIA) | The 5 MHz case is about one quarter of the revenue and may change the license-design answer |
| D2 | 2020–2025 MHz | Keep out of scope, or model the 25 MHz package | The FNPRM treats them together; adjacency to SpaceX spectrum affects both |
| D3 | Terrestrial downlink benchmark | Accept one or both candidates in item 2, or keep downlink suspended | Restores scenario S9, the use NTIA studied |
| D4 | Bidder list | Sign off the eight bidders, or name a reviewer | One D2D bidder more or less moves the estimate by about $0.6 billion |
| D5 | Outside reviewer | An auction economist who didn't build the model | Required before figures go to appointees |

## Phase A: scope and evidence fixes

**1. Add a 5-megahertz scenario (1675–1680 MHz).**
- Work: one 5 MHz block; with one block the price is the second-highest bid. Use the Auction 97 A1
  (5 MHz) price as the block-size check. Report both cases side by side in every table.
- Data: existing CSVs.
- Check: the 5 MHz and 20 MHz results reconcile through the per-MHz price and the change in the
  pricing rule; `verify.py` gets new expected values.

**2. Restore terrestrial downlink with unpaired-downlink comparables.**
- Candidates:
  - Qualcomm's 700 MHz D and E block licenses, sold to AT&T for $1.925 billion in December 2010 for
    supplemental downlink.[3] With AT&T's coverage figures (12 MHz over 70 million people and 6 MHz
    over 230 million), that's about $0.87 per megahertz-pop in 2010 dollars. Provisional: confirm
    the license list and population in the FCC transfer record.
  - Qualcomm's UK 1452–1492 MHz L-band, sold to Vodafone and Three in 2015 for at least
    £100 million for supplemental downlink.[4] An international cross-check only.
  - Auction 46, the nationwide 1670–1675 MHz license (April 2003), is the closest frequency
    match.[5] Pull the winning bid from the closing public notice (DA 03-1472); it's old and
    thinly contested, so treat it as a floor.
- Check: each comparable goes through the existing benchmark-quality rules (cash equivalent, primary
  source, strategic premium noted). Rerun scenario S9.

**3. Model the 110 percent rule and NOAA transition costs.**
- Work: proceeds must cover 110 percent of federal relocation or sharing costs, or the auction can't
  close.[6] Add the test to `Revenue_Defs` for each scenario. NTIA will notify the FCC of costs and
  timelines at least six months before the auction.[1]
- Data: no public NOAA cost yet; use a placeholder range and say so.
- Check: flag for counsel review; don't state a legal conclusion.

**4. Read the adopted FNPRM.**
- Replace the Covington summary with paragraph citations from FCC 26-70, and confirm the block plan,
  license-area options, package-bidding question, and SCS treatment. Closes the pending check.

## Phase B: analysis upgrades

**5. Model the NOAA coordination zones (turns the upper bound into an estimate).**
- Work: four protected sites (Fairmont, WV; Sioux Falls, SD; Suitland, MD; Wallops, VA).[1] For
  terrestrial downlink, size zones from base-station emissions; for D2D downlink, use this project's
  MATLAB LEO interference engine. Convert each zone to encumbered population by PEA, then to a
  revenue haircut under each license design.
- Data: site coordinates from public filings; 2020 Census block populations; NTIA's coordination
  tool if NTIA releases it.
- Check: reproduce one published propagation reference case before trusting zone sizes; compare
  zone population to the 3 percent of uplink revenue the four PEAs hold now.

**6. Calibrate the price effect of federal sharing on Auctions 105 and 110.**
- Work: no published study isolates how much coordination areas lower auction prices (see the
  literature review). Regress license price per megahertz-pop on the share of population inside
  dynamic protection areas (Auction 105, county licenses, $4.58 billion)[7] and inside cooperative
  planning or periodic use areas (Auction 110, PEA licenses, $22.5 billion gross),[8] controlling
  for market size.
- Data: FCC Public Reporting System results by license; FCC and NTIA published area definitions.
- Check: reconcile each auction to its published total; hold out 20 percent of licenses and report
  prediction error.

**7. Backtest the method.**
- Work: fit the market-size curve on half of the Auction 97 B1 licenses and predict the other half.
  Then predict the two Auction 113 unpaired licenses from 2015 data alone.
- Check: report mean absolute percentage error; put it in the paper as the method's track record.

**8. Add an income-approach cross-check.**
- Work: the literature recommends more than one valuation technique.[9] For carriers, value the
  spectrum as the cost of cell sites avoided. For D2D, value it from subscribers served, revenue per
  user, and margin over the license term.
- Data: public carrier filings, Census, published D2D service pricing.
- Check: the income value should bracket the market value; explain any gap of more than a factor
  of two.

**9. Value adjacency.**
- Work: prices were higher when the highest losing bidder held adjacent licenses in the PCS
  auctions.[10] SpaceX holds 1695–1710 MHz next door. Model an adjacency premium for SpaceX, and the
  guard band cost when 1675–1695 MHz runs in the opposite direction from 1695–1710 MHz.
- Check: sensitivity on the premium from 0 to the 1.21 national premium.

**10. Stress-test package bidding and demand reduction.**
- Work: simulate the threshold problem, where regional bidders fail to jointly outbid a national
  package,[11] and test core pricing against a pay-as-bid package rule.[12] Sweep SpaceX's
  second-block value to find where demand reduction stops binding.[13]
- Check: the v0.4 package result reappears when regional bidders coordinate fully.

**11. Run a global sensitivity analysis.**
- Work: vary every input across its documented range; rank inputs by their effect on revenue
  (tornado chart); optionally compute variance-based indices.
- Check: the top three drivers should match the red team's top risks (D2D bidder count, benchmark
  choice, market-size slope). If they don't, find out why.

## Phase C: the working paper

**12. Literature review.** Done in this update: section 2 of the working paper, with the full
review in `docs/literature-review.md`.

**13. New figures.** Each figure built by `scripts/make_figures.py` from `data/csv`:
- Tornado chart of revenue drivers (item 11).
- Map of coordination zones over PEAs with encumbered population (item 5).
- Backtest: predicted against actual prices (item 7).
- Benchmarks including the downlink comparables (item 2).
- 5 MHz against 20 MHz results (item 1).

**14. Structure.** Add a one-page executive summary up front, move method detail to an appendix, and
version the paper with the workbook (v0.5 with this phase).

**15. Review and clearance.**
- Independent agent review of the paper and workbook by an agent that didn't draft them.
- Outside auction economist (D5).
- IRAC coordination for any NOAA equity statement; counsel review of the 110 percent rule and
  package-bidding questions; clearance before any figure leaves the agency.

**16. Delivery formats.** Keep markdown as the source in the repo. Export to Word or PDF when the
paper circulates.

## Sequence

| Phase | Items | Depends on |
|---|---|---|
| A | 1–4 | D1–D3 |
| B | 5–11 | Phase A; item 5 needs site data and the propagation reference case |
| C | 12–16 | Phases A and B for the new figures; review last |

Each item ends with `./reproduce.sh` passing, updated CSVs in `data/csv`, and updated expected
values in `verify.py` and `check_csvs.py`.

## Sources

1. NTIA, letter to FCC Chairman Brendan Carr identifying 1675–1680 MHz (Feb. 26, 2026)
   ([NTIA](https://www.ntia.gov/sites/default/files/2026-03/1675-mhz-identification-letter.pdf)).
2. FCC, FNPRM, FCC 26-70, WT Docket No. 26-284
   ([FCC](https://docs.fcc.gov/public/attachments/FCC-26-70A1.pdf)); see also
   [Benton, "FCC Aims to Auction 25 Megahertz of Prime, Mid-Band Spectrum"](https://benton.org/node/361497).
3. [TV Technology, "AT&T Takes Qualcomm Spectrum for $1.9 Billion" (Dec. 20, 2010)](https://www.tvtechnology.com/news/atampt-takes-qualcomm-spectrum-for-19-billion).
4. [Fierce Network, "Qualcomm agrees €139m L-band spectrum deal with Vodafone UK and Three UK"](https://www.fierce-network.com/europe/qualcomm-agrees-eu139m-l-band-spectrum-deal-vodafone-uk-and-three-uk).
5. [FCC, Auction 46: 1670–1675 MHz](https://www.fcc.gov/auction/46).
6. CRS, *Spectrum Provisions in P.L. 119-21, the FY2025 Reconciliation Law*, R48862 (Feb. 25, 2026),
   p. 8, citing 47 U.S.C. § 309(j)(16)
   ([EveryCRSReport](https://www.everycrsreport.com/files/2026-02-25_R48862_aa6d6610f436cee1da921cdc06f728c756639fea.pdf)).
7. [Fierce Network, "CBRS 3.5 GHz auction concludes, raising $4.58B"](https://www.fierce-network.com/regulatory/cbrs-3-5-ghz-auction-concludes-raising-4-58b).
8. [IEEE ComSoc Technology Blog, "FCC Auction 110 rakes in $22.5 billion in gross proceeds"](https://techblog.comsoc.org/2022/01/14/fcc-auction-110-rakes-in-22-5-billion-in-gross-proceeds-for-3-45-ghz-service/).
9. Bazelon and McHenry, "Spectrum value," *Telecommunications Policy* 37(9) (2013): 737–747
   ([RePEc](https://econpapers.repec.org/RePEc:eee:telpol:v:37:y:2013:i:9:p:737-747)).
10. Ausubel, Cramton, McAfee, and McMillan, "Synergies in Wireless Telephony," *Journal of Economics
    & Management Strategy* 6(3) (1997): 497–527
    ([RePEc](https://econpapers.repec.org/RePEc:bla:jemstr:v:6:y:1997:i:3:p:497-527)).
11. Goeree and Holt, "Hierarchical package bidding: A paper & pencil combinatorial auction," *Games
    and Economic Behavior* 70(1) (2010): 146–169
    ([RePEc](https://econpapers.repec.org/RePEc:eee:gamebe:v:70:y:2010:i:1:p:146-169)).
12. Day and Milgrom, "Core-selecting package auctions," *International Journal of Game Theory* 36
    (2008): 393–407 ([Springer](https://link.springer.com/doi/10.1007/s00182-007-0100-7)).
13. Ausubel, Cramton, Pycia, Rostek, and Weretka, "Demand Reduction and Inefficiency in Multi-Unit
    Auctions," *Review of Economic Studies* 81(4) (2014): 1366–1400
    ([RePEc](https://econpapers.repec.org/RePEc:oup:restud:v:81:y:2014:i:4:p:1366-1400)).

**DRAFT//PRE-DECISIONAL**
