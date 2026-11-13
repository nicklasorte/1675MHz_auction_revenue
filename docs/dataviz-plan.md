**DRAFT//PRE-DECISIONAL**

# Data visualization plan: 1675–1695 MHz auction revenue

November 13, 2026. Prepared with AI assistance. Reviewer: [CONFIRM].

## Audience and job

The readers are senior leaders and appointees who will decide what NTIA says about license design and
expected proceeds. They are smart and busy and aren't auction economists. Each visual must do one
job: make a cause-and-effect claim believable at a glance, then hold up under questioning from staff
who will check the numbers.

Every figure follows `slide-design` and `dataviz`: the takeaway as the title, gray for context and
NTIA light blue for the one thing to look at, direct labels instead of legends, bars from zero, no
dual axes, Times New Roman in report figures, and alt text. Every figure is built by
`scripts/make_figures.py` from `data/csv`, so the numbers on the page are the numbers in the data.

## Ghost deck: the story in six headlines

1. The FCC's own estimate is about four times ours because it prices this unpaired band like paired
   spectrum (option 2).
2. Our central estimate is about $4.1 billion; most outcomes fall between $3.3 and $4.5 billion
   (options 1 and 3).
3. The number of D2D bidders matters more than anything else we can't observe (options 4 and 9).
4. NTIA's coordination distances would put about 30% of the population inside a NOAA zone for terrestrial
   base-station downlink (option 6).
5. The zones bind only when terrestrial downlink sets the price: then they cost $0.2 to $0.8 billion;
   package bids hold the floor (option 8).
6. The zone cost is calibrated on the adjacent band's own auction (option 10).

## Ten options, and where each comes from

| # | Visual | What it shows here | Borrowed from | Best use | Status |
|---|---|---|---|---|---|
| 1 | **Valuation "football field"**: horizontal range bars, one per method, with the central value marked | Every estimate on one scale: benchmarks, scenarios, Monte Carlo, zone cases, and the FCC's $17B | Investment-banking fairness opinions and M&A valuation summaries | The one-slide answer to "how much?" | Option |
| 2 | **Bridge (waterfall) chart** from the FCC's estimate to ours | $17.0B → paired-to-unpaired price → auction rule → $4.1B | Corporate finance variance bridges | Explaining a disagreement with another agency's number | Built (Figure 6) |
| 3 | **Quantile dotplot**: 50 dots, each a 2% chance | The Monte Carlo spread as countable outcomes ("8 of 50 dots fall below $3.5B") | Kay, Kola, Hullman, and Munson (CHI 2016), tested on bus-arrival predictions[1] | Non-technical readers; outperforms density plots for decisions[2] | Option |
| 4 | **Fan chart** by number of D2D bidders | Median and 10th–90th percentile band as D2D bidders go from 0 to 6 | Bank of England inflation fan charts (since 1996)[3] | Showing that one input moves the whole distribution | Built (Figure 7) |
| 5 | **Tornado diagram** | Which inputs move the central estimate most, ranked | Decision analysis in oil and gas (P10/P50/P90 reserves) and project finance[4] | Backup slide; tells staff where to spend verification effort | Built (Figure 8) |
| 6 | **County map with coordination zones** | Counties inside NOAA zones at NTIA's distances and at half those distances, with the four sites | NTIA Report 24-01 PEA impact maps (Figures 16–17)[5] | Making the zone footprint concrete | Built (Figure 9) |
| 7 | **Exceedance curve** | Probability that revenue exceeds any given amount, with and without zones | Catastrophe-model exceedance-probability curves in insurance[6] | Budget scorers who think in "chance of at least $X" | Option |
| 8 | **Small multiples by license design** | Revenue against zone radius for nationwide, PEA, and PEA-plus-package licensing, uplink and downlink side by side | Tufte's small multiples; CBO's scenario panels[7] | The license-design decision under zone uncertainty | Built (Figure 10) |
| 9 | **Heat map of bidder counts** | Revenue for every combination of 0–6 D2D and 0–6 terrestrial bidders | Sensitivity grids in pricing and valuation models | Showing that terrestrial bidder count barely matters | Option |
| 10 | **Partial-residual calibration plot** | Auction 97 prices, net of market size, against the share of each market inside AWS-3 protection zones | Applied econometrics (hedonic price studies) | Defending the 36% value-retained assumption to economists | Built (Figure 11) |

## Recommendations

- **For a leadership slide:** option 1 or option 2 as the hero, with option 4 as the second slide.
  Option 2 answers the question leaders will ask first ("why is ours lower than the FCC's?").
- **For the working paper:** options 2, 4, 5, 6, 8, and 10 are built. Option 3 could replace the
  Monte Carlo histogram (Figure 5) if the paper goes to non-technical readers.
- **For a budget audience:** add option 7.
- **Avoid:** pie charts of revenue by scenario (scenarios aren't parts of a whole), dual-axis
  charts of price and revenue, and rainbow maps.

## Sources

1. Matthew Kay, Tara Kola, Jessica Hullman, and Sean Munson, "When (ish) is My Bus? User-centered
   Visualizations of Uncertainty in Everyday, Mobile Predictive Systems," CHI 2016
   ([UW Interactive Data Lab](https://idl.uw.edu/papers/when-ish-is-my-bus)).
2. Michael Fernandes et al., "Uncertainty Displays Using Quantile Dotplots or CDFs Improve Transit
   Decision-Making," CHI 2018 ([UW Interactive Data Lab](https://idl.uw.edu/papers/uncertainty-bus)).
3. Bank of England, "The Inflation Report projections: understanding the fan chart," *Quarterly
   Bulletin* 1998 Q1 ([Bank of England](https://www.bankofengland.co.uk/quarterly-bulletin/1998/q1/the-inflation-report-projections-understanding-the-fan-chart)).
4. Oracle Crystal Ball documentation, "Tornado Charts and Sensitivity Analysis"
   ([Oracle](https://docs.oracle.com/cd/E36352_01/epm.1112/cb_user/apgs06.html)); Edward Tufte,
   "Tornado plots" ([edwardtufte.com](https://www.edwardtufte.com/notebook/tornado-plots/)).
5. NTIA Report 24-01 (SPRES-FO), December 2024, Figures 16–17
   ([NTIA](https://www.ntia.gov/sites/default/files/2025-10/ntia_report_24-01_12-2024-1675mhz-rev3-ntia-spres-fo.pdf)).
6. Verisk, "Modeling fundamentals: combining loss metrics"
   ([Verisk](https://www.verisk.com/insurance/visualize/modeling-fundamentals-combining-loss-metrics/)).
7. CBO, *How Changes in Economic Conditions Might Affect the Federal Budget: 2024 to 2034*
   ([CBO](https://cbo.gov/publication/60072)).

**DRAFT//PRE-DECISIONAL**
