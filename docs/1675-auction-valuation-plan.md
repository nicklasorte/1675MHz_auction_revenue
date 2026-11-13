# 1675–1695 MHz auction valuation plan

DRAFT//PRE-DECISIONAL

**Version:** 6 (November 10, 2026). Adds nationwide package-bid results from workbook v0.4.
**Builds on:**

- FCC, *Auctioning the 1675–1695 MHz and 2020–2025 MHz Bands*, Further Notice of Proposed
  Rulemaking (FNPRM), FCC 26-70, WT Docket No. 26-284 (October 29, 2026)
- Corner Alliance, *Proposed Valuation Methodology for the 1675–1695 MHz Band* (November 4, 2026)

**Deliverable:** Excel workbook that estimates auction value for 20 MHz at 1675–1695 MHz, using the
license structure the FNPRM proposes

## Bottom line

The FNPRM changes the valuation question. It proposes flexible-use licenses: each licensee chooses
uplink, downlink, or TDD, and the band carries a secondary allocation for supplemental coverage
from space (SCS). So the four use cases aren't four revenue streams. They're four kinds of bidders
competing for the same licenses.

The model therefore treats the use cases as competing bidders, and sets the price from the
highest losing bid, not from the winner's value. The red team's main finding follows from this:
if only one strong D2D bidder shows up, D2D value doesn't set the price. Terrestrial value does.
The number of credible bidders in each class is the most important input in the model.

Federal coordination zones are deferred. Every output is labeled **before federal coordination,
upper bound**, with a placeholder for zones later.

Build in three layers, following the Corner Alliance staging:

1. **Market value:** what observed transactions say the spectrum is worth, per use case.
2. **License structure:** how the FNPRM band plan, license area, and package-bidding options turn
   those values into auction revenue.
3. **Operating adjustments:** buildout, bidding credits, timing, and ODS, applied only where
   evidence supports them.

## What the FNPRM sets, and what it means for the model

| FNPRM proposal | Model implication |
|---|---|
| Two unpaired 10 MHz blocks: 1675–1685 MHz and 1685–1695 MHz | Base case values two licenses per area |
| Alternative: unpaired 5 MHz blocks | Sensitivity case: four 5 MHz blocks in 1675–1695 MHz |
| Alternative: pair 1685–1695 MHz with 2020–2025 MHz | Out of scope (1675–1695 MHz only); noted, not modeled |
| Uplink, downlink, or TDD at licensee's choice | Value each license at its highest-value use case |
| Secondary MSS allocation for SCS | SCS can add value on top of a terrestrial license; how SCS rights are obtained is an open question |
| License area not set: nationwide, regional, or PEA | Model all three |
| Possible license bundling and all-or-nothing nationwide package bids | Test whether a nationwide package is worth more than the sum of PEAs |
| 15-year term, open eligibility, no pre-auction spectrum cap | No eligibility adjustment |
| Terrestrial buildout: 45% interim, 80% final population per license area; automatic termination | Possible discount for terrestrial bidders in hard-to-build areas; not applied to D2D |
| Small-business and rural bidding credits | Report gross and net revenue |
| Coordination with NTIA near four NOAA DCS sites; other sites move to an alternative distribution system | Deferred; placeholder availability of 100% |

## Scope

- **Spectrum:** 20 MHz, 1675–1695 MHz only.
- **Use cases (bidder types):**

| Code | Use case | Transmitter | Receiver | Likely bidder |
|---|---|---|---|---|
| TDL | Terrestrial downlink | Base station | UE | Mobile carrier |
| TUL | Terrestrial uplink | UE | Base station | Mobile carrier |
| SUL | Satellite uplink | UE | LEO satellite | D2D operator |
| SDL | D2D downlink | LEO satellite | UE | D2D operator |

- **Deferred:** federal coordination zones, OSM mitigation dataset, UE geofencing.
- **Sources:** public and cleared material only.

## Layer 1: market value by use case

### Benchmarks

| Use case | Primary benchmark | Cross-check | Gap |
|---|---|---|---|
| TDL | None adjacent | AWS-3 paired licenses (2155–2180 MHz downlink half), Auctions 97 and 113 | No unpaired downlink comparable near 1.7 GHz. Paired values include the uplink half. |
| TUL | Auction 97 A1 and B1 (1695–1710 MHz) | Auction 113 A1 and B1 | Closest match: unpaired uplink, adjacent, with federal protection zones |
| SUL | SpaceX/EchoStar AWS-3 transaction ($2.617 billion, up to 15 MHz) | Auction 97 A1 and B1 for the same licenses | Transaction price can include strategic premium |
| SDL | SpaceX/Grain 800 MHz transaction (about $8 billion) | SpaceX/EchoStar | Large frequency gap |

Note on A1 and B1: their prices already include the effect of AWS-3 federal protection zones.
Because 1675–1695 MHz zones are deferred, document this. It means the TUL benchmark is an
encumbered price applied to an unencumbered base. Flag it on `Summary`; don't adjust it yet.

### Steps

1. Load the Auction 97 and Auction 113 per-license results from the FCC Public Reporting System CSV.
2. Reproduce each auction's published gross total before using any per-license price. Auction 113
   must reconcile to $3,572,889,200 gross.
3. Compute gross value and $/MHz-pop for A1 (1695–1700 MHz) and B1 (1700–1710 MHz) in each auction,
   per license and nationally.
4. Match the SpaceX/EchoStar licenses back to Auction 97. Compute the share of Auction 97 A1 and B1
   value they represent and the implied current value of the full A1 and B1 universe.
5. Compute transaction-level $/MHz-pop for SpaceX/EchoStar and SpaceX/Grain from the actual
   holdings.
6. Put all benchmarks on one basis: nominal $/MHz-pop, no inflation adjustment.
7. Report the spread between benchmarks as a finding, not a problem to smooth over.

### Assumptions to test

| Claim | Test | If it fails |
|---|---|---|
| Nominal $/MHz-pop is flat over time | Matched licenses, Auction 97 vs. Auction 113 | Add an explicit time adjustment or report both vintages |
| Auction 113 reflects current value | Check for a biased license subset (defaulted markets); rerun without any single dominant bidder | Use Auction 113 as cross-check only |
| The EchoStar price reflects spectrum value | Compare implied $/MHz-pop with Auction 113 prices for the same blocks | Show the excess as a strategic premium |
| Unpaired sells at a discount to paired | Ratio of A1 and B1 to paired $/MHz-pop | Use as empirical unpaired discount for TDL |
| Auction 113 prices weren't pushed up by a bidder with a reason to overbid | Identify any bidder with a financial stake in re-auction prices (for example, default shortfall liability); compare prices on licenses it bid on with those it didn't | Use prices from licenses that bidder didn't contest, or use Auction 113 as a ceiling only |
| Transaction prices are cash-equivalent | Read the primary deal documents (SEC filings, FCC applications) for the form of payment, other assets in the deal, and seller distress | Restate at cash-equivalent value, or widen the range and say why |
| $/MHz-pop is the right unit for D2D | Compute D2D benchmarks per MHz-pop and per MHz-km²; see which is more stable across the two transactions | Value D2D as a nationwide lump sum, not by PEA population |

### Benchmark quality rules

- **Primary sources only.** Take every transaction figure (the $2.617 billion EchoStar price, the
  approximately $8 billion Grain price, MHz, and license lists) from the deal's own filings, not
  from the Corner Alliance memo or the press. Record the document and page on `Transactions`.
- **Ranges, not points.** Four benchmarks can't support a single number. Carry low, base, and high
  for each benchmark, and show per-license spread (median and interquartile range) for the auction
  data.
- **Add an unpaired downlink comparable for TDL.** The paired AWS-3 price can't be split into
  uplink and downlink halves without an assumption. Look for a real unpaired downlink sale, such
  as the 2011 AT&T purchase of Qualcomm's Lower 700 MHz D and E block licenses (verify price and
  holdings from the FCC order). It's older and lower in frequency, so use it as a cross-check.

## Layer 2: license structure

### Pricing rule

Version 3 priced each license at the second-highest use-case value. The red team found two errors
in that rule, so version 4 replaces it.

- **Bidders are firms, not use cases.** Three carriers can all want uplink. Then carriers set the
  price against each other, and the price is near the top terrestrial value.
- **Benchmarks are prices, not valuations.** Auction 97 and 113 results are already clearing
  prices, set by losing bidders. Discounting them again to a "second price" double counts.

The rule now works on bidder classes with a bidder count:

1. For each license, list each bidder class's benchmark price and its count of credible bidders
   (an input on `Bidders`, with a public source for each named firm).
2. With two blocks per area, the price is set by the highest bid that doesn't win a block (the
   third-highest bid when each bidder wants one block).
3. If the top class has enough bidders to fill both blocks and leave a loser, the price is the top
   class's benchmark. If not, the price falls to the next class's benchmark.
4. Report three numbers per scenario:
   - **Floor:** the lower of the terrestrial benchmarks (thin competition, price set by carriers).
   - **Estimate:** the pricing rule above, at the base-case bidder counts.
   - **Ceiling:** the highest benchmark (competitive D2D bidding).
5. Report the winning class per license, so the map shows where carriers win and where D2D
   operators win.

Report the sum-of-use-cases only as a labeled error case. Summing would double count, because one
license can only go to one winner.

### Exposure risk for D2D bidders under PEA licensing

A D2D operator needs rights across a whole service area. Under PEA licensing, it must win every
PEA for a block, and one holdout winner can block the service. That risk lowers what a D2D bidder
will pay per PEA. So the license-area choice isn't neutral: PEA licensing favors carriers, and
nationwide licensing or package bidding favors D2D operators. Model this as a D2D exposure
discount on the PEA option, default off, with the FCC's supplemental-coverage lease rules (current
and as proposed in the companion D2D NPRM) cited as the basis. Confirm the rule before turning it
on.

### SCS on top of terrestrial

The FNPRM pairs co-primary terrestrial use with secondary SCS. If a terrestrial winner can also
earn SCS value (directly or by lease), its bid rises. Model SCS as an optional adder to TDL and TUL
bids, off by default, until the SCS rights mechanism is clear.

### License-area options

| Option | Units | How value is computed | Status |
|---|---|---|---|
| Nationwide | 2 licenses | National population × benchmark | Built (v0.2) |
| PEA | 407 rows (406 contiguous PEAs + Alaska/Hawaii) × 2 blocks | Market-by-market highest losing bid | Built (v0.3) |
| Regional | Regions × 2 blocks (definition TBD) | Sum of member PEAs | Not built |

### Nationwide vs PEA results (workbook v0.3)

All figures are before federal coordination, upper bound.

| Case | Nationwide | PEA | Change |
|---|---|---|---|
| UE uplink (carriers at TUL, D2D at SUL) | $4.07B | $4.65B | +$0.58B (+14%) |
| D2D downlink (carriers at TUL, D2D at SDL) | $5.14B | $5.21B | +$0.07B (+1%) |

Two measured effects pull in opposite directions:

- **Market sorting raises PEA revenue.** In Auction 97, price per pop rose with market size
  (B1 slope 0.65 on log population, R² 0.59). Under PEA licensing, carriers win the largest PEAs,
  where they value spectrum most, and D2D bidders win most of the rest. In the uplink case,
  carriers win the 13 largest markets and D2D bidders win the other 394, including Alaska and
  Hawaii (61% of population).
- **Lost aggregation lowers D2D bids.** SpaceX paid 1.21 times the 2015 market-by-market price
  for the same EchoStar licenses, after the flat-nominal adjustment. That national-portfolio
  premium is lost under PEA licensing, so D2D per-PEA bids fall from $0.61 to $0.51 (uplink) and
  from $0.78 to $0.64 (downlink).

The result depends on two inputs:

| Sensitivity | UE uplink, PEA vs nationwide | D2D downlink, PEA vs nationwide |
|---|---|---|
| Flat $/pop (slope 0) | −$0.61B | −$0.91B |
| Half the fitted slope | +$0.02B | −$0.51B |
| Fitted slope, 10% D2D exposure discount | +$0.38B | −$0.21B |
| Fitted slope, 30% D2D exposure discount | +$0.01B | −$0.72B |

**Reading:** PEA licensing helps the uplink case only if the strong market-size effect from 2015
holds and D2D bidders don't discount heavily for exposure. For D2D downlink, PEA licensing is at
best a wash and loses revenue under any exposure discount. Package bidding for a nationwide
footprint would remove most of the exposure risk.

**Caveats:**

- The slope comes from 2015 B1 prices, which Dish-affiliated bidders largely set. It may not
  describe today's carriers.
- The premium comes from one deal, paid in stock, by one strategic buyer.
- The exposure discount is a judgment, not evidence.
- PEA populations are 2010 values scaled to the 2020 national total.

### PEA licenses plus nationwide package bids (workbook v0.4)

The FNPRM also asks about all-or-nothing nationwide package bids. In the model, each block sells
either PEA by PEA or as one nationwide package. A package wins only if it beats the sum of the
per-PEA bids for that block, and pays at least that sum. D2D bidders bid packages at their
national value, so they keep the national premium and carry no exposure risk.

| Case | Nationwide | PEA only | PEA + packages |
|---|---|---|---|
| UE uplink | $4.07B | $4.65B | $4.65B |
| D2D downlink | $5.14B | $5.21B | $5.21B |

With at least three D2D bidders, package bidding returns the larger of the nationwide and
PEA-only results. It never does worse than either:

| Case | PEA only | PEA + packages | Protection |
|---|---|---|---|
| Downlink, flat $/pop | $4.24B | $5.14B | +$0.91B |
| Uplink, flat $/pop | $3.46B | $4.07B | +$0.61B |
| Downlink, fitted slope, 30% exposure | $4.42B | $5.21B | +$0.79B |

**Reading:** at the fitted market-size slope, PEA-by-PEA sales beat the packages, so packages add
nothing in the base case. Their value is insurance: they recover up to about $0.9B when the
market-size effect is weak or D2D bidders discount heavily for exposure. That makes "PEA licenses
with nationwide package bids" the license design with the highest floor.

**Caveats:**

- In real package auctions, many small bidders must jointly outbid a package (the threshold
  problem), so packages can win too cheaply.
- The result needs three or more independent D2D bidders. With two, packages win at the per-PEA
  price and revenue equals PEA only.

**Coordination tie-in:** under PEA licensing, the four PEAs with a NOAA DCS site hold about 3%
of uplink revenue. Baltimore–Washington (Suitland) is most of that, at about $0.13B. Bidders could
price those markets separately. Under a nationwide license, the same limits spread across one
price. The PEA-to-site mapping still needs verification.

### Band plan sensitivity

Run the base case (two 10 MHz blocks) and the alternative (four 5 MHz blocks). Smaller blocks can
draw more bidders but lose value if a use case needs 10 MHz. State the channel-width needs per use
case as an input, sourced from the technical team.

## Layer 3: operating adjustments

Keep each in its own column. Show value before and after.

| Adjustment | Applies to | Method | Default |
|---|---|---|---|
| Buildout (45% and 80%) | TDL, TUL | Flag PEAs where 80% population coverage needs disproportionate sites | Off; flag only |
| Bidding credits | All | Gross minus estimated credits, using Auction 113 gross-to-net ratio | On; report both |
| Timing | Later-access use cases | Present value at a stated discount rate | Sensitivity only |
| ODS | SDL | Fraction of capacity lost under ODS | Off until ODS rules are quantified |
| Federal coordination | All | Availability factor per PEA | **Deferred; 100%** |
| Usable spectrum | All | Usable MHz per use case after any guard band (adjacent 1695–1710 MHz uplink, 1670–1675 MHz, and between the two blocks if they run opposite directions) | 20 MHz; flag as unconfirmed |
| Device and standards readiness | All | Years until handsets and networks support the band; present-value discount | Off; needs technical team input |
| Competing auctions | TDL, TUL | Carrier budget left after the Upper C-band auction | Sensitivity only |

### Mixed-direction risk

The FNPRM lets each licensee pick uplink, downlink, or TDD. If neighbors pick opposite directions
(in the adjacent block or the adjacent area), base stations and UEs interfere with each other, and
someone gives up spectrum as a guard band. The model assumes all 20 MHz is usable. That holds only
if both blocks run the same direction, or the rules force alignment. State this assumption on
`Summary`, and ask the technical team for the guard band needed in each direction pairing.

## Revenue definitions

"Auction revenue" has at least four meanings. The workbook reports each on its own line, and
`Summary` states which one the headline uses.

| Measure | Definition |
|---|---|
| Gross bids | Sum of winning bids |
| Net bids | Gross bids minus bidding credits |
| Net of federal costs | Net bids minus NOAA relocation and sharing costs paid from proceeds |
| Budget score | What CBO or OMB would score; outside this model, noted only |

If the band is covered by the Commercial Spectrum Enhancement Act, auction proceeds must reach
110 percent of estimated federal relocation or sharing costs for the auction to close. Confirm
with counsel whether this applies, and if so, add the NOAA cost estimate as a reserve-price check.

## Workbook layout

| Tab | Contents |
|---|---|
| `README` | Purpose, sources, marking, version, change log, deferred items |
| `FNPRM` | Each FNPRM proposal used, with paragraph citation and the model input it drives |
| `Inputs` | Named-range assumptions; selectors for band plan, license area, SCS adder |
| `Raw_A97`, `Raw_A113` | Per-license CSVs as downloaded, unedited |
| `Transactions` | EchoStar and Grain holdings, prices, and citations |
| `Benchmarks` | All comparables on a common $/MHz-pop basis, plus the assumption tests |
| `PEA_Pop` | 416 PEAs with 2020 Census population and region mapping |
| `Bidders` | Credible bidders per class, each with a public source; base, low, and high counts |
| `Bids` | Benchmark price per license for each bidder class |
| `Auction` | Pricing rule: floor, estimate, ceiling, and winning class per license |
| `Revenue_Defs` | Gross, net of credits, and net of federal costs |
| `Coordination` | Placeholder availability (all 100%) for the deferred zone analysis |
| `Scenarios` | Band plan × license area × benchmark (low, base, high) × SCS on or off |
| `Summary` | One range, one chart, and a list of what's excluded |
| `Checks` | Reconciliations that must all read PASS |

## Checks

- Auction 97 and Auction 113 CSV totals reconcile to the FCC public notices.
- PEA populations sum to the 2020 Census U.S. total; regions sum to the nation.
- Each license has exactly one winner; floor ≤ estimate ≤ ceiling for every license.
- Setting every class to one bidder drops the estimate to the floor (or the reserve). Setting
  every class to three or more raises it to the ceiling.
- `Coordination` is all 100%. Every chart, table, and `Summary` cell that shows dollars carries the
  label "before federal coordination, upper bound" in the cell or title itself, so the label
  survives a copy and paste.
- Every transaction figure traces to a primary filing, not to the memo or the press.
- Every number on `Summary` traces to an `Auction` cell; every FNPRM input traces to a paragraph.
- A separate agent that didn't build the workbook tries to break it before it goes to appointees.
- Policy judgment and anything leaving NTIA gets human review.

## Red-team findings

The red team took three roles: an auction economist, an opposing filer, and a budget examiner.
Findings are ranked by how much they could move the headline number.

| # | Finding | Risk | Change in version 4 |
|---|---|---|---|
| 1 | Thin D2D competition. If one D2D operator dominates, it wins at the carriers' price, and the D2D benchmarks never show up in revenue. | High | Bidder counts per class on `Bidders`; floor, estimate, and ceiling |
| 2 | The version 3 pricing rule double discounted. Benchmarks are already clearing prices, and bidders are firms, not use cases. | High | Pricing rule rewritten |
| 3 | The headline is an upper bound that looks like an estimate. Zones are deferred, and two of the four sites sit near the dense Northeast corridor. | High | Label on every dollar output; check added |
| 4 | Transaction benchmarks aren't auction prices. They can include non-cash payment, other assets, strategic premium, or a pressured seller. | High | Cash-equivalent test; primary sources only |
| 5 | Auction 113 prices may be biased upward by a bidder with a stake in the outcome, and the licenses are a non-random subset. | Medium | New assumption test; Auction 113 as ceiling if it fails |
| 6 | All 20 MHz may not be usable. Opposite-direction neighbors and adjacent bands can force guard bands. | Medium | Usable-MHz input; mixed-direction section |
| 7 | PEA licensing exposes D2D bidders to holdouts, so license area changes who wins and what they pay. | Medium | Exposure discount on the PEA option |
| 8 | "Revenue" was undefined. Gross bids, net bids, net of NOAA costs, and budget score differ. | Medium | `Revenue_Defs` tab; 110 percent check flagged for counsel |
| 9 | $/MHz-pop fits carriers, not satellites. D2D value follows area and unserved territory. | Medium | Per-km² test; nationwide lump-sum option |
| 10 | Four benchmarks, no error bars. | Medium | Ranges and per-license spread |
| 11 | No real unpaired downlink comparable for TDL. | Medium | Added a candidate transaction as cross-check |
| 12 | No allowance for device and standards readiness, or for carrier budgets after Upper C-band. | Low | Added to Layer 3, default off |
| 13 | The TUL benchmark already includes AWS-3 protection-zone effects, so it's inconsistent with a "before coordination" base. | Low | Already flagged; kept on `Summary` |
| 14 | Independence. Reusing Corner Alliance's gathered data makes this a replication, not an independent check. | Low | Workbook pulls its own raw data; see open question 5 |

### What the red team couldn't close

- Whether the adopted FNPRM differs from the October 8 draft on band plan, license area, or SCS
  rights. The adopted text wasn't readable from here.
- The guard band needed for each direction pairing. This needs the technical team.
- The credible-bidder list. This is a judgment call that should be sourced and reviewed, not set
  by the model builder alone.

This red team was done by the plan's author. Before the workbook goes to appointees, have a
reviewer who didn't write the plan repeat it.

## Open questions

1. The adopted FNPRM (FCC 26-70) couldn't be read directly here; this plan uses the October 8 draft
   as summarized by Covington. Can you attach the adopted text so the `FNPRM` tab cites final
   paragraphs?
2. How does a D2D operator get SCS rights in this band: by winning the license, or by lease from a
   terrestrial licensee? This decides whether SCS is a separate bidder or an adder.
3. For the regional option, which regions: REAGs, EAs, or something else?
4. For TDL, which downlink benchmark do you accept?
5. Should the workbook reconcile with Corner Alliance's results, or serve as an independent check?
6. Which revenue measure does the headline use: gross bids, net bids, or net of NOAA costs?
7. Who are the credible bidders in each class, and who signs off on that list?
8. Is there a public NOAA cost estimate for the transition to an alternative distribution system?

## Next step

Confirm this plan and answer the open questions. The build then starts with Layer 1: downloading
the Auction 97 and 113 CSVs and reconciling the totals.

## Possible extensions

- **Zones back in:** add the four NOAA coordination zones to `Coordination` and show revenue lost
  per site and per dB of mitigation.
- **Comment input:** turn the license-area and band-plan results into the revenue argument for
  NTIA's FNPRM comments (which license area and block size maximize value).
