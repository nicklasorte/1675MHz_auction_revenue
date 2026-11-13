**DRAFT//PRE-DECISIONAL**

# Literature review: valuing 1675–1695 MHz

November 13, 2026. Prepared with AI assistance. Reviewer: [CONFIRM]. Every source below was checked
against its publisher or index record on November 13, 2026; transaction figures are as reported in
the press and are not verified in primary filings.

This review covers what earlier work says about the five choices the model makes: how to value
spectrum, what AWS-3 prices show, how license area changes value, how the auction rules set price,
and how federal sharing and satellite use change value. Each section ends with what it means for the
model.

## 1. How to value spectrum

Bazelon and McHenry review spectrum valuation methods and conclude that market sales are a starting
point that usually needs substantial adjustment, best done with discounted cash flow or econometric
evidence. They warn that relying on one technique leaves information unused.[1] Regulators use
benchmarks the same way: Ofcom set annual licence fees for 900 MHz and 1800 MHz spectrum from
adjusted international auction prices.[2]

Budget scorekeepers use a coarser version. For the spectrum provisions of P.L. 119-21, the
Congressional Budget Office (CBO) estimated $85.0 billion in proceeds over 2026–2034 by reviewing
band characteristics, likely values from bidding history, auction capacity, and industry ability to
pay, not band by band; it gave no numeric range.[3] For the 2016 incentive auction, CBO gave a range
of $10 billion to $40 billion with an expected value of $25 billion.[4] Arner and Furchtgott-Roth
estimated receipts by applying price-per-megahertz-pop benchmarks and then discounting them 50 to 80
percent for limiting factors, including federal protection and sharing.[5]

**For the model:** the workbook uses market comparables from raw FCC data and adds an explicit
auction rule, which is more than CBO or Hudson publish. It still uses one technique. The plan adds an
income-approach cross-check (`docs/next-phase-plan.md`, item 8).

## 2. What AWS-3 prices show

Cramton and Sujarittanonta report that Auction 97 paired spectrum sold for $2.72 per megahertz-pop,
more than five times the $0.52 for unpaired spectrum. They find that prices rose with market size:
the 26 largest licenses brought 38 percent of revenue. They also discuss the Dish-affiliated
designated entities' bidding credits, which they put at about $3.6 billion.[6]

**For the model:** the workbook reproduces both prices from the FCC's per-license data ($2.71 and
$0.52) and fits the market-size effect directly (slope 0.65). The designated-entity dominance of the
unpaired licenses is the reason the market-size slope is a stated risk.

## 3. License area and synergies

Ausubel, Cramton, McAfee, and McMillan found that PCS license prices were higher when the highest
losing bidder held adjacent licenses, evidence of geographic synergies.[7] Fox and Bajari estimated
bidder values in the C block auction and found that four large regional licenses would have raised
allocative efficiency by 48 percent.[8] Comparing 28 mobile markets, Hazlett and Muñoz estimate that the
gains from allocating more bandwidth and supporting competitive market structures generally outweigh
license revenue, so policies meant to raise auction receipts should be judged against those gains.[9]

**For the model:** these support the national-portfolio premium (1.21 from the EchoStar sale) and
the D2D exposure discount under PEA licensing. Hazlett and Muñoz are a reason to present revenue as
one input to the license-design decision, not the decision rule. The plan adds an adjacency premium
for SpaceX (item 9).

## 4. Auction rules and price

Ausubel, Cramton, Pycia, Rostek, and Weretka show that in multi-unit auctions, a bidder's bids on
extra units affect what it pays on the units it wins, so bidders shade demand ("demand reduction").
In uniform-price auctions this generally makes the outcome inefficient.[10] Goeree and Holt designed
hierarchical package bidding, used in the FCC's Auction 73, to let bidders bid for packages while
avoiding the threshold problem, where small bidders fail to jointly outbid a package.[11] Day and
Milgrom show that core-selecting package auctions give the seller competitive revenue and reduce
incentives for shill bidding.[12]

**For the model:** the two-block uniform-price rule, SpaceX's demand reduction, and the core pricing
of nationwide packages follow from these papers. The model doesn't yet simulate the threshold
problem (item 10).

## 5. Federal sharing and coordination zones

Recent FCC auctions sold spectrum shared with federal users: Auction 105 (county Priority Access
Licenses with dynamic protection areas) raised $4.58 billion,[13] and Auction 110 (3.45 GHz, with
sharing with Department of Defense operations) raised $22.5 billion gross.[14] The Congressional
Research Service notes that auction proceeds must cover 110 percent of federal relocation or sharing
costs, and that the 1.78–1.85 GHz transition cost over $4.5 billion and took about 10 years.[15] For
this band, NTIA identified 1675–1680 MHz under P.L. 119-21 and recommended coordination to protect
four NOAA downlink sites, with per-base-station review using an NTIA software tool.[16]

**For the model:** this search found no published study that isolates how much coordination or
protection areas lower auction prices. Hudson's 50–80 percent discount is a judgment covering ten
factors at once.[5] The plan fills the gap with a regression on Auctions 105 and 110 (item 6) and
with zone modeling for the four NOAA sites (item 5).

## 6. Satellite and direct-to-device use

The FCC's 2024 supplemental coverage from space (SCS) order lets a satellite operator offer SCS only
where terrestrial licensees holding all licenses on a channel across a geographically independent
area agree, and it made specific low-band and PCS bands eligible.[17] There is little published
economic work on what D2D operators will pay for spectrum. The evidence is transactions, such as the
SpaceX purchases from EchoStar and Grain, whose terms come from press releases and reports.

**For the model:** the D2D benchmarks rest on transactions, not auctions, and are the weakest link.
Whether D2D operators bid or lease decides between the $3.46 billion and $4.07 billion cases.

## What this paper adds

- Per-license reconstruction of Auctions 97 and 113 from FCC data, reconciled exactly to published
  totals and released as CSV.
- An explicit two-block clearing rule with named bidders, instead of a single price times
  megahertz-pops.
- A side-by-side test of nationwide, PEA, and PEA-plus-package licensing for terrestrial and D2D
  bidders.
- Planned: the first public estimate of the price effect of federal protection areas, calibrated on
  Auctions 105 and 110.

## Sources

1. Coleman Bazelon and Giulia McHenry, "Spectrum value," *Telecommunications Policy* 37(9) (2013):
   737–747 ([RePEc](https://econpapers.repec.org/RePEc:eee:telpol:v:37:y:2013:i:9:p:737-747)).
2. Ofcom, *Annual licence fees for 900 MHz and 1800 MHz spectrum*
   ([Ofcom](https://www.ofcom.org.uk/spectrum/radio-equipment/900-1800-mhz-fees)).
3. CBO, supplemental cost estimate for P.L. 119-21, Sec. 40002, Spectrum Auctions (Oct. 28, 2025)
   ([CBO](https://www.cbo.gov/system/files/2025-10/PL%20119-21-Spectrum.pdf)).
4. CBO, *Proceeds From Auctions Held by the Federal Communications Commission* (Apr. 21, 2015)
   ([CBO](https://www.cbo.gov/publication/50128)).
5. Kirk R. Arner and Harold Furchtgott-Roth, "Estimated Value of Potential Spectrum Auction Receipts
   in the Next Five-Year Window," Hudson Institute (July 18, 2024)
   ([Hudson](https://hudson.org/technology/estimated-value-potential-spectrum-auction-receipts-next-five-year-window-kirk-arner-harold-furchtgott-roth)).
6. Peter Cramton and Pacharasut Sujarittanonta, "Bidding and Prices in the AWS-3 Auction" (May 2015)
   ([copy filed with MinTIC](https://www.mintic.gov.co/portal/historico/articles-103102_avantel_anexo_d_3_cramtonaws3auctionprices.pdf)).
7. Lawrence M. Ausubel, Peter Cramton, R. Preston McAfee, and John McMillan, "Synergies in Wireless
   Telephony: Evidence from the Broadband PCS Auctions," *Journal of Economics & Management
   Strategy* 6(3) (1997): 497–527
   ([RePEc](https://econpapers.repec.org/RePEc:bla:jemstr:v:6:y:1997:i:3:p:497-527)).
8. Jeremy T. Fox and Patrick Bajari, "Measuring the Efficiency of an FCC Spectrum Auction,"
   *American Economic Journal: Microeconomics* 5(1) (2013): 100–146
   ([RePEc](https://econpapers.repec.org/RePEc:aea:aejmic:v:5:y:2013:i:1:p:100-146)).
9. Thomas W. Hazlett and Roberto E. Muñoz, "A welfare analysis of spectrum allocation policies,"
   *RAND Journal of Economics* 40(3) (2009): 424–454
   ([RePEc](https://econpapers.repec.org/RePEc:bla:randje:v:40:y:2009:i:3:p:424-454)).
10. Lawrence M. Ausubel, Peter Cramton, Marek Pycia, Marzena Rostek, and Marek Weretka, "Demand
    Reduction and Inefficiency in Multi-Unit Auctions," *Review of Economic Studies* 81(4) (2014):
    1366–1400 ([RePEc](https://econpapers.repec.org/RePEc:oup:restud:v:81:y:2014:i:4:p:1366-1400)).
11. Jacob K. Goeree and Charles A. Holt, "Hierarchical package bidding: A paper & pencil
    combinatorial auction," *Games and Economic Behavior* 70(1) (2010): 146–169
    ([RePEc](https://econpapers.repec.org/RePEc:eee:gamebe:v:70:y:2010:i:1:p:146-169)).
12. Robert Day and Paul Milgrom, "Core-selecting package auctions," *International Journal of Game
    Theory* 36 (2008): 393–407 ([Springer](https://link.springer.com/doi/10.1007/s00182-007-0100-7)).
13. [Fierce Network, "CBRS 3.5 GHz auction concludes, raising $4.58B"](https://www.fierce-network.com/regulatory/cbrs-3-5-ghz-auction-concludes-raising-4-58b).
14. [IEEE ComSoc Technology Blog, "FCC Auction 110 rakes in $22.5 billion in gross proceeds"](https://techblog.comsoc.org/2022/01/14/fcc-auction-110-rakes-in-22-5-billion-in-gross-proceeds-for-3-45-ghz-service/).
15. Jill C. Gallagher, *Spectrum Provisions in P.L. 119-21, the FY2025 Reconciliation Law*, CRS
    R48862 (Feb. 25, 2026), pp. 8, 22
    ([EveryCRSReport](https://www.everycrsreport.com/files/2026-02-25_R48862_aa6d6610f436cee1da921cdc06f728c756639fea.pdf)).
16. NTIA, letter to FCC Chairman Brendan Carr identifying 1675–1680 MHz (Feb. 26, 2026)
    ([NTIA](https://www.ntia.gov/sites/default/files/2026-03/1675-mhz-identification-letter.pdf)).
17. FCC, *Single Network Future: Supplemental Coverage from Space; Space Innovation*, Report and
    Order and Further Notice of Proposed Rulemaking, FCC 24-28, GN Docket No. 23-65 and IB Docket
    No. 22-271 (adopted Mar. 14, 2024) ([FCC](https://docs.fcc.gov/public/attachments/FCC-24-28A1.pdf)).

**DRAFT//PRE-DECISIONAL**
