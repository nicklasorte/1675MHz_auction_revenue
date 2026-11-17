**DRAFT//PRE-DECISIONAL**

# Applying lessons from the 7 GHz auction-value report: plan for the 1675-1695 MHz working paper

November 17, 2026. Prepared with AI assistance. Reviewer: [CONFIRM].

This plan compares our method with the structure of a recent auction-value report for the 7125-7400 MHz
band (report dated November 12, 2026) and lists what to adopt, what to test, and what not to copy. It
names no author and quotes none of that report's results, because this repository is public and the
report's release status isn't confirmed. Comparison values can be added after clearance.

## Status (November 17, 2026, v0.6)

All ten items are done. Financing is a sensitivity only, as decided. Where results differ from the first-pass
estimates in this plan, the paper and `data/csv/` hold the final numbers: the zone-free benchmark is about 10%
higher (as estimated), the zone-free curve changes zone results by 1% or less, and the financing test can't
separate the adjustment from none (interval 0.82 to 1.72 around an observed 0.99).

| Item | Where it landed |
|---|---|
| 1. Zone double count | `zone_free_curve.csv`, `zone_free_designs.csv`, `zone_sweep.csv` (`size_curve` column); paper sections 4 and 6.2 |
| 2. Stage table, bridge | `stage_table.csv`; paper section 5.7; Figure 12 |
| 3. Financing test | `financing_wacc.csv`, `financing_test.csv`, `financing_sensitivity.csv`; paper section 7.1; tornado |
| 4. Timing | `timing_sensitivity.csv`; paper section 7.2; Figure 13 |
| 5. Structural zone check | `zone_structural.csv`; paper section 6.4 |
| 6. Conditional wording | Paper opening, executive summary, Figures 4 and 5 |
| 7. Outside the model | Paper section 8 |
| 8. Mid-band cross-check | `midband_reconciliation.csv`, `midband_crosscheck.csv`; paper section 7.3; Figure 14 |
| 9. Gross-revenue scope | Paper opening and limitations |
| 10. Assumptions register | Paper Appendix A; `assumptions_register.csv` |

Decision 1 (financing as sensitivity) is settled. Decisions 2 to 4 below were resolved as follows: delays of 0
to 3 years; the report is cited generically; the mid-band cross-check ran after items 1 to 7.

## Bottom line

- **Adopt:** a stage table that shows the price after each adjustment, an explicit financing-cost and
  timing sensitivity, an assumptions register, and wording that treats scenarios as conditional.
- **Fix:** our terrestrial benchmark already contains a zone effect from the adjacent band's auction, so
  applying the 1675-1695 MHz zones on top counts part of the effect twice. This is the only item that
  changes headline-adjacent numbers, and it does so by about 10% on the terrestrial benchmark.
- **Don't copy:** scaling value by coverage area, which doesn't transfer to a lower band, and a zone
  discount built from assumptions alone.

## How the 7 GHz report is built

The report starts from one observed auction price per megahertz-pop and applies multiplicative
adjustments in a fixed order: a technical factor, a coordination factor computed market by market, a
clearing-delay factor by market tier, a cost-of-money factor, and a market-perception factor taken from
a later auction. It presents three conditional scenarios, says plainly they aren't a range or equally
likely, and adds a one-year-earlier and one-year-later timing sensitivity. I reproduced its stage
arithmetic from its stated factors; each stage and the final totals tie within rounding.

## Side-by-side

| Step in the 7 GHz report | Our counterpart today | Gap | Item |
|---|---|---|---|
| One anchor auction, nominal price | Several benchmarks by use; nominal-flat test (ratio 0.99) | None; our test supports the premise | - |
| Price shown after each stage | Final numbers and one FCC bridge (Figure 6) | No stage-by-stage table for our own estimate | 2 |
| Coordination by market and population share | County model reproducing NTIA Table 11 | Our benchmark already includes a zone effect | 1 |
| Zone discount from assumed factors | Zone discount calibrated on Auction 97 (35.7% retained; 22%-57%) | Assumption-based cross-check missing | 5 |
| Clearing delay by tier | None; availability assumed at license grant | No timing sensitivity | 4 |
| Cost-of-money factor | None; relies on observed 2026 prices | Not tested explicitly | 3 |
| Market-perception factor | Auction 97 to 113 matched-pair ratio | Different test; keep ours | 8 |
| Conditional scenarios, "not a range" | Monte Carlo P10-P90 called "outcomes" | Wording implies a confidence interval | 6 |
| Qualitative auction-outcome section | Bidder-count sweep only | No discussion of factors outside the model | 7 |
| Gross revenue before transition costs | Gross only, not stated up front | One-line statement needed | 9 |
| Assumptions in a footnote, "on request" | All inputs in the repository | No evidence grade per assumption | 10 |

## Items, in priority order

### 1. Remove the double count of federal protection zones (changes numbers)

- **Problem:** Auction 97 B1 prices, our terrestrial benchmark, already reflect the 27 US88 protection
  zones in 19 of 172 markets. Applying the 1675-1695 MHz zone discount to that price counts the overlap
  twice.
- **Size:** With our calibrated coefficient (-1.03), the revenue-weighted B1 price is about 95% of its
  zone-free level, so the zone-free terrestrial benchmark is about 10% higher ($0.52 becomes about $0.57).
  This is a first-pass calculation from `aws3_zone_calibration.csv`; the workbook must reproduce it.
- **Do:** build a zone-free benchmark, apply the 1675-1695 MHz zones to it, and avoid applying both zones
  to the same population where they overlap (Baltimore-Washington).
- **Where:** workbook `Benchmarks` and `Coordination`; `scripts/analysis.py` zone functions; paper
  sections 4 and 6.
- **Check:** zone-free benchmark times retained share reproduces the Auction 97 average; central case
  stays $4.07B (D2D sets the price); the two-D2D-bidder zone sweep changes and is reported.

### 2. Add a stage table and a second bridge

- **Do:** one table of price per megahertz-pop after each stage (benchmark, bidder class, national
  premium, auction rule, zones, timing, financing) with the dollar effect of each. Add a bridge figure
  for our central case beside Figure 6.
- **Check:** the product of stage factors equals the final price; stage dollars sum to the final total
  within $1; the order of stages is stated, with a reordered run to show how much the order matters.

### 3. Test financing conditions; don't assume them away

- **Do:** compute the present-value ratio of a level benefit stream at a 2015 and a 2026 cost of capital
  over the 15-year license term (FNPRM para. 56). Use public Treasury and Baa yields and stated CAPM
  inputs. Apply it to the 2015-vintage anchor only, as a sensitivity.
- **Why a test:** our 2026 observations (Auction 113, the EchoStar sale, the Grain sale) are already at
  current rates, and the 196-license ratio is 0.99. If those observations land above the adjusted anchor,
  the data don't support a separate adjustment and the paper says so.
- **Check:** the annuity-ratio formula reproduces a hand calculation; the result sits in the tornado
  chart, not in the central case.

### 4. Add an availability-timing sensitivity

- **Do:** a delay parameter d, in years, that shifts the start of the benefit stream; the value factor is
  (1 + r)^-d. Show 0 to 3 years, nationwide and zone areas only. At 7%, each year of nationwide delay
  costs about 6.5%, or roughly $0.26B on the central case; confirm in code.
- **Data limit:** a clearing schedule for federal systems, if one exists, isn't public in the sources
  used here. The paper states the parameter as a sensitivity and names the schedule as the data that
  would replace it.
- **Check:** d = 0 reproduces the current results exactly.

### 5. Cross-check the zone discount with a structural build-up

- **Do:** write a factor table for value kept inside a zone (usable bandwidth, site approval, technical
  performance, coordination timing, rule certainty, reuse of existing sites), fill each factor from
  public precedent, and compare the product with the calibrated 35.7% and its 22%-57% interval.
- **Check:** the structural estimate falls inside the interval, or the paper explains the difference.
  Report both; keep the calibrated value as the central input.

### 6. Reword ranges as conditional

- **Do:** state that the simulated 10th to 90th percentile depends on the assumed bidder-value
  distributions, isn't a confidence interval, and that scenarios aren't equally likely. Name scenarios by
  what they assume, not by S-number.
- **Where:** executive summary, section 5.1, Figures 4 and 5 captions.
- **Check:** every use of "outcomes" or "range" in the paper matches the new wording.

### 7. Add a section on auction-outcome uncertainty

- **Do:** a short section on what the model doesn't capture: bidder participation, financing capacity,
  timing relative to other spectrum offerings, final rules, and the upside from new entrants. Point to
  the bidder-count sweep as the quantitative handle.
- **Research:** a dated list of other FCC offerings in the same window, from public FCC and NTIA notices.
- **Check:** every date and item traces to a retrieved public source.

### 8. Run a mid-band-anchored cross-check

- **Do:** parse Auctions 107 and 110 from public FCC data, reconcile them to published totals as we did
  for Auctions 97 and 113, and run the same stages from a mid-band anchor. This gives a third point
  beside the FCC method and ours.
- **Don't port:** scaling value by coverage area. At 1.7 GHz that logic would raise value several times
  over, which the low-band evidence contradicts.
- **Check:** published totals tie exactly; the result is labeled a cross-check, not an estimate.

### 9. State the gross-revenue scope up front

- **Do:** add one sentence to the executive summary and limitations: estimates are gross bids, before any
  transition or sharing cost, so they can't be compared with net figures.

### 10. Add an assumptions register

- **Do:** an appendix table with each input, value, source or basis, and evidence grade: observed,
  calibrated, or assumed. Link each row to its CSV.
- **Check:** every number in the register matches `data/csv/inputs.csv` and the workbook.

## Sequence

| Phase | Items | Why this order |
|---|---|---|
| 1 | 1, 2 | Changes numbers; everything later builds on them |
| 2 | 3, 4, 5 | Sensitivities on the corrected base |
| 3 | 6, 7, 9, 10 | Text changes after the numbers settle |
| 4 | 8 | Independent cross-check |

After each phase: rerun `reproduce.sh`, match every paper figure to the CSVs, update the numbers
ledger, and rebuild the Word version. After phase 4, have a separate reviewer try to break the revised
paper before it goes to anyone outside.

## Decisions for Nick

1. Show financing conditions as a sensitivity only (recommended), or in the central case?
2. Which delay values to show by default (0 to 3 years proposed)?
3. Is the 7 GHz report cleared to cite, and to name, in this public repository?
4. Run item 8 now, or after items 1-7?

## Limits of this plan

- The 7 GHz report is a different band with different physics; only its structure transfers.
- Item 1's size estimate is a first pass and may move when the workbook reproduces it.
- Timing and financing inputs come from public series; nonpublic federal schedules aren't used.

**DRAFT//PRE-DECISIONAL**
