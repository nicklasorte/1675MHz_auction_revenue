# Red team: 1675–1695 MHz auction valuation, approach and workbook v0.1

DRAFT//PRE-DECISIONAL

**Date:** November 10, 2026
**Reviewed:** `1675-auction-valuation-plan.md` (version 4) and `1675-auction-valuation.xlsx` (v0.1)
**Reviewers:**

- The model that built the workbook (self-review)
- A separate agent that had not seen the drafting and was asked to break it (independent review)

Human review is still required before any of these numbers leave the team.

Every dollar figure here is **before federal coordination, upper bound**.

## Bottom line

The v0.1 range of $0.73B to $11.43B can't go to anyone. Here's how each part of it holds up:

- **The base estimate holds.** $3.45B for 20 MHz, with a price set by the carriers, is supported by two independent sources. Correcting the population basis gives a range of $3.21B–$3.45B.
- **The ceiling fails.** The $11.43B case assumes SpaceX bids for both blocks. In a uniform-price clock auction, a rational SpaceX bids for one block instead, keeps $2.9B, and the price falls to the carriers' level.
- **The floor fails.** It uses the price of a 5 MHz block that was discounted for federal protection zones.
- **The D2D upside is real but conditional, and smaller than it looked.** The only same-frequency D2D evidence, the SpaceX/EchoStar purchase of 1695–1710 MHz, is priced at the carriers' level ($0.52/MHz-pop). D2D raises revenue only if three independent D2D bidders each value this band like a downlink portfolio. No same-frequency evidence shows that yet.
- **The downlink scenario is unusable as built.** It has a unit error. Fixing it moves the scenario from $9.0B to $18.0B. A swing that large from one cell shows the benchmark has no evidence behind it.

**What should go forward for now:** a central range of **$3.2B–$3.5B**. Pair it with one conditional upside line: about $9.3B, only if three independent D2D bidders compete at the downlink value, and only if D2D winners can use the band as modeled.

## How the two reviews compare

Both reviews found the demand-reduction flaw, the Globalstar enterprise-value problem, the protection-zone floor, the population-basis mix, and the weak Checks tab.

**Found only by the independent agent:**

- The unit error in the downlink (TDL) base.
- Checks that always pass, cell by cell.
- The buildout-termination question for D2D winners.

**Found only by self-review:**

- The same-frequency D2D evidence that erases the D2D premium.
- The "SpaceX values this band as uplink" adjacency argument.
- Block-specific values, which break the uniform price.
- Grain as one buyer's strategic price.
- The thin Auction 113 unpaired sample.
- Carrier heterogeneity.

**One agent claim rejected:** it said the Summary tab has no chart. It does (a bar chart at A25). openpyxl charts don't show up when a script reads cell values, which is likely why the agent missed it.

## Findings, ranked by effect on the headline

| # | Finding | Severity | Effect on revenue | Found by |
|---|---|---|---|---|
| 1 | Demand reduction: S3 and S7 aren't equilibria | High | Ceiling $11.43B → $4.77B; S3 $9.26B → $3.45B | Both |
| 2 | Unit error in TDL base | High | S5 $9.02B → $18.03B; shows the benchmark is unusable | Independent |
| 3 | Same-frequency D2D evidence prices at the carrier level | High | D2D scenarios S3 and S4 → $3.47B | Self |
| 4 | Estimate rests on a bidder count nobody has signed off on | High | One more independent D2D bidder: $3.45B → $9.26B | Both |
| 5 | D2D bidder class may not exist as modeled (SCS secondary, lease option, buildout) | High | If D2D can lease SCS rights, D2D bidders have no reason to pay a premium at auction; revenue = carrier price | Both |
| 6 | D2D benchmarks are one buyer's strategic prices or enterprise values | Medium | SDL base and high both overstated by an unknown amount | Both |
| 7 | Checks tab tests almost nothing | Medium | No direct effect; false confidence | Both |
| 8 | Floor uses a protection-zone, 5 MHz block price | Medium | Floor $0.73B is not credible against a "before coordination" base | Both |
| 9 | Blocks aren't identical, so the uniform-price assumption may fail | Medium | Direction unclear; likely raises the price of 1685–1695 MHz | Self |
| 10 | Within-class values are identical, which forces a step function | Medium | S1 likely understated; top carrier's value exceeds the class clearing price | Self |
| 11 | Auction 113 has very few unpaired licenses | Medium | The "recent evidence" for uplink may not exist | Self |
| 12 | Population basis mixed (2010 vs. 2020) | Low | S1 $3.45B → $3.21B–$3.24B | Both |
| 13 | Hardcoded benchmarks don't match their own computed values | Low | ±2% | Independent |
| 14 | Missing bidders: AST SpaceMobile, Ligado, EchoStar | Low to high | Depends on finding 4 | Both |
| 15 | Same model planned, built, and red-teamed the work | Process | Unknown | Self |

## Findings in detail

### 1. Demand reduction breaks the ceiling (High)

**Problem:** In S3, SpaceX bids for both blocks at its full value of $4.628B each. It wins both at a price equal to its value, so it keeps nothing (`Scenarios!E22`, `E23`, `E31`). If it bids for one block, the third-highest bid becomes a carrier at $1.724B, and SpaceX keeps $2.90B on the block it wins.

Uniform-price clock auctions reward this demand reduction, and bidders in past FCC auctions have used it. So S3 and S7 aren't outcomes a rational SpaceX would choose.

**Effect:**

- S3 falls from $9.26B to $3.45B.
- S7, the Summary ceiling, falls from $11.43B to $4.77B: two blocks at the high carrier price of $0.72/MHz-pop.

**Fix:**

- Delete S3 and S7, or model a bidder that wants two blocks as reducing demand when that leaves it more surplus.
- Add a check that no winner would gain by bidding for fewer blocks.
- The only legitimate route to a D2D-set price is three independent D2D bidders (S4).

### 2. Unit error in the TDL base (High)

**Problem:** `Benchmarks!C18` is `=D8*Inputs!B13` = $2.72 × 0.5 = $1.36/MHz-pop. But $2.72 is already a price per MHz across all 50 MHz of paired AWS-3 spectrum (25 MHz uplink and 25 MHz downlink). If the downlink half carries 50% of the value, its price per downlink MHz is 0.5 × $2.72 × 50 ÷ 25 = $2.72, not $1.36.

**Effect:** Corrected, carriers value a downlink block above D2D. Carriers win, and S5 rises from $9.02B to $18.03B. The high case ($2.72) then equals the corrected base.

**What this really shows:** The formula is fixable. The benchmark isn't. Treating unpaired downlink as worth as much as paired spectrum goes against the main pattern in Auction 97, where paired spectrum sold for about five times the unpaired price.

**Fix:**

- Correct the formula to `=2*Inputs!B13*D8`.
- Take S5 off the Summary until a real unpaired-downlink comparable is in the workbook, such as AT&T's purchase of Qualcomm's Lower 700 MHz D and E block licenses. Verify that deal's price and holdings in the FCC order.

### 3. The same-frequency D2D evidence erases the D2D premium (High)

**Problem:** The D2D bidders are valued at the SDL (downlink) benchmark: Globalstar at $1.40, Grain at $1.72. But the only D2D transaction in this frequency range is SpaceX's purchase of EchoStar's 1695–1710 MHz licenses for satellite uplink. That works out to $0.523/MHz-pop, the same as the carrier uplink price of $0.52.

Two things point the same way:

- The band touches SpaceX's 1695–1710 MHz uplink holdings. The most natural use for SpaceX is extending that uplink band (Band 70), not adding downlink right next to its own uplink with no frequency gap between them.
- Downlink at 1675–1695 MHz would also face operational data-sharing requirements and protection of the NOAA receivers that the uplink case avoids.

**Effect:** Valuing D2D bidders at SUL instead of SDL puts S3 and S4 at $3.47B. The D2D premium disappears.

**Fix:**

- Make SUL the base D2D use case, and SDL the upside.
- Ask the technical team whether SDL in 1675–1695 MHz is feasible next to 1695–1710 MHz uplink, and what guard band it would need.

### 4. The estimate rests on an unconfirmed bidder count (High)

**Problem:** With two blocks, the price is the third-highest bid. In S1, that's a carrier. Add one more independent D2D bidder and revenue goes from $3.45B to $9.26B, a 2.7x jump from a single assumption. The bidder list isn't signed off (`Bidders!A12`).

**Fix:** Make the number of independent D2D bidders the main sensitivity on the Summary tab, shown as a step chart with 0, 1, 2, and 3 or more bidders.

### 5. The D2D bidder class may not exist as modeled (High)

The FNPRM makes terrestrial use co-primary and SCS secondary. Three things follow.

- **The lease option.** If a D2D operator can get SCS rights by leasing from whoever wins the terrestrial license, it doesn't need to win the auction. Its bid is then capped by what the lease would cost, not by what D2D service is worth to it.
- **Buildout.** The Covington summary describes terrestrial buildout of 45% and 80% with automatic termination, and says it doesn't apply to D2D. It's unclear whether a winner that uses the license only for satellite service is exempt. If it isn't, a satellite-only winner loses the license.
- **Protection.** D2D downlink can't protect the NOAA DCS receivers with terrestrial-style zones. So "100% availability" overstates D2D value more than carrier value.

**Fix:**

- Add a scenario where D2D firms get SCS rights only by lease. That leaves only carriers bidding, so revenue equals S1.
- State on the Summary that every scenario priced by D2D bidders depends on plan open question 2.
- Get the adopted FNPRM text to settle the buildout question.

### 6. The D2D benchmarks aren't market prices (Medium)

- **Globalstar ($11.57B)** is the value of the whole company: satellites, ground network, the Apple agreement, and worldwide MSS rights. Dividing it by U.S. population alone overstates $/MHz-pop.
- **Grain ($8B, press report)** is one buyer's strategic price. The same spectrum was reportedly on the market for about $3.6B (about $0.78/MHz-pop) before SpaceX bought it. Using SpaceX's own price as the value for a second, competing bidder is circular.
- **EchoStar** was paid in SpaceX stock valued as of September 2025, by a seller under FCC pressure to sell. The workbook uses $2.6B; the plan cites $2.617B.

**Fix:**

- Demote Globalstar to a cross-check.
- Show Grain both ways: the reported prior market price and the SpaceX price.
- Pull all three deals' terms from SEC filings and FCC applications.

### 7. The Checks tab is mostly theater (Medium)

| Cell | Problem |
|---|---|
| `Checks!B10` | Compares MIN and MAX of a row with a value from the same row, so it always passes |
| `Checks!B8` | Can't fail, because `Scenarios` row 32 already caps blocks sold with MIN |
| `Checks!B9` | Tests price against the sum of two bid values, which no price can exceed |
| `Checks!B11` | Only confirms the placeholder equals 1; doesn't check labels |
| `Checks!B6` | New Street's $1.73 likely comes from the same $8B ÷ 14 MHz; circular |

**Fix:** Replace these with tests that can fail:

- **Demand reduction:** no winner gains by bidding for fewer blocks.
- **Bidder count:** with one bidder per class, the estimate drops to the floor or the reserve.
- **Recomputed benchmarks:** each hardcoded benchmark matches the value recomputed from its dollars and population, within 2%.
- **Labels:** every dollar cell on the Summary carries the upper-bound label.

### 8. The floor is a protection-zone price (Medium)

**Problem:** The floor (S6, $0.73B) prices uplink at $0.11/MHz-pop, the A1 block alone. A1 was a 5 MHz block that was discounted by AWS-3 federal protection zones. That's an encumbered price applied to a base the workbook labels "before coordination."

**Fix:** Once the Auction 97 per-license CSV is attached, set the floor from the 25th percentile of A1 and B1 $/MHz-pop, with each license weighted by population.

### 9. The two blocks aren't identical (Medium)

**Problem:** 1685–1695 MHz sits next to SpaceX's 1695–1710 MHz. 1675–1685 MHz sits next to Ligado's 1670–1675 MHz. Each block has a natural buyer, so the FCC may not auction them as interchangeable blocks at one price. If they sell separately, each block gets its own price.

**Effect:** Likely a higher price on 1685–1695 MHz and a new natural buyer, Ligado or a partner, for 1675–1685 MHz.

**Fix:** Add a block-specific option, and check how the FNPRM proposes to auction the blocks.

### 10. Identical values within a class force a step function (Medium)

**Problem:** All three carriers bid exactly $0.52/MHz-pop. But that's a clearing price, which reflects the marginal bidder, not the strongest one. In S1, the third-highest bid is really the top carrier's own value, which is probably above $0.52. In Auction 97, AT&T and Verizon paid about $2.9/MHz-pop on paired spectrum while T-Mobile paid $1.63, so carriers clearly value spectrum differently.

**Effect:** S1 is probably understated.

**Fix:** Give each bidder its own value multiplier, drawn from what it actually paid in Auctions 97 and 113, and run the pricing rule as a Monte Carlo. Report the spread, not a single point.

### 11. Auction 113 may hold almost no unpaired evidence (Medium)

**Problem:** The Federal Register's summary of Auction 113 appears to list one A1 license and one B1 license. Both the Corner Alliance memo and the plan count on Auction 113 as recent uplink evidence.

**Fix:** Confirm the license count from the per-license CSV. If it's only two licenses, report Auction 113 as anecdotal for unpaired spectrum.

### 12. Mixed population basis (Low)

**Problem:** Auction 97 $/MHz-pop is computed on 2010 population, but the workbook applies it to 2020 population.

**Effect:** Scaling the actual A1+B1 dollars instead gives $3.21B–$3.24B for S1, not $3.45B.

**Fix:** Pick one basis, apply it everywhere, and state it.

### 13. Hardcoded benchmarks drift from their own inputs (Low)

**Problem:** B1 recomputes to $0.732/MHz-pop but is hardcoded at $0.72. The unpaired average is hardcoded at $0.52; the computed value is $0.5247.

**Fix:** Link benchmark cells to formulas.

### 14. Missing bidders (Low to High)

| Bidder | Why it might bid | Verify |
|---|---|---|
| AST SpaceMobile | D2D operator with carrier backing; reported L-band arrangement with Ligado | Yes |
| Ligado | Holds the adjacent 1670–1675 MHz; could combine for 25 MHz | Yes |
| EchoStar | Has cash from its 2025–2026 spectrum sales | Yes |

Whether any of these matters depends on finding 4.

**Capital constraint:** SpaceX committed about $28B to spectrum in roughly 13 months: $17B for AWS-4 and H-block, $2.6B for unpaired AWS-3, and about $8B for 800 MHz. Model a budget cap as a sensitivity.

### 15. Process (Process)

The same model wrote the plan, built the workbook, and ran the self-review. The independent agent pass helps, but it's still a model. A human reviewer with auction experience should look at findings 1–5 before any number goes to appointees.

## Federal coordination: the deferred risk cuts both ways

Deferring zones overstates value now:

- Suitland, Maryland, sits inside the Washington metro area.
- Wallops and Suitland together touch the Northeast corridor.

But the protection need may shrink later. Earlier work showed most weather broadcast use of the band ending after GOES-R retires around 2033. Over a 15-year license, encumbrance may be front-loaded. When zones come back, model them as declining over time, not as a permanent discount.

## Revised numbers

All figures are before federal coordination, upper bound.

| Measure | v0.1 | After red team | Status |
|---|---|---|---|
| Central range | $3.45B | **$3.2B–$3.5B** | Usable, with label |
| Upside | $11.43B (S7) | **About $9.3B**, only with three independent D2D bidders at downlink value, and only if D2D winners can use the band as modeled | Conditional; show with its conditions |
| D2D at same-frequency evidence | Not shown | $3.47B | Add as a scenario |
| Downlink (S5) | $9.02B | $18.03B corrected; suspended | Needs a real comparable |
| Floor | $0.73B | Not credible; rebuild from per-license data | Pending CSV |
| S3, S7 | $9.26B, $11.43B | Remove (not equilibria) | Delete |

## v0.2 fix list, in order

1. Remove S3 and S7, or add demand reduction. Add the demand-reduction check.
2. Make SUL the base D2D use case. Add the lease-only scenario.
3. Fix the TDL formula and suspend S5 until there's a downlink comparable.
4. Put independent D2D bidder count on the Summary as the main sensitivity.
5. Replace the checks that can't fail.
6. Put everything on one population basis, and link the hardcoded benchmarks to formulas.
7. Load the Auction 97 and 113 per-license CSVs. Rebuild the floor from them and confirm the Auction 113 unpaired license count.
8. Add per-bidder value multipliers and a Monte Carlo of the pricing rule.
9. Add a block-specific option and the extra candidate bidders.
10. Verify deal terms in primary filings.

## Questions for Nick

1. Can you attach the adopted FNPRM? It settles the buildout and lease questions behind finding 5.
2. Can you download the Auction 97 and 113 "Results by License" CSVs? Findings 8 and 11 depend on them.
3. Is SDL in 1675–1695 MHz technically realistic next to SpaceX's 1695–1710 MHz uplink, or should D2D be modeled as uplink only?
4. Who reviews the bidder list, and should AST SpaceMobile and Ligado be on it?
