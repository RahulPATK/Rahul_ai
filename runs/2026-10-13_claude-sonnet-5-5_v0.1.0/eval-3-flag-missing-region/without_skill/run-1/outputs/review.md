# Weekly Metrics Review: week of 2026-10-13

## Data issue: EMEA is missing from this week's data

`this_week.csv` has no EMEA row. It covers only North America, APAC and LATAM. `last_week.csv` has all four regions. This is the first review since the regional reorg, so the likely cause is that EMEA was dropped or remapped in the pipeline. I haven't confirmed that.

`reported_totals.csv` is the sum of the rows present in each file, so it carries the same gap. The totals tie out exactly to the regional rows, which means there is no arithmetic error. EMEA is simply absent from this week's figure.

**The headline decline is not a real business decline.**

| Metric | Last week (4 regions) | This week (3 regions) | Reported change |
|---|---|---|---|
| Orders | 10,890 | 7,600 | -30.2% |
| Revenue (GBP) | 462,300 | 319,100 | -31.0% |
| Active customers | 39,580 | 27,200 | -31.3% |

EMEA was about a third of last week's volume: 32.9% of orders, 33.1% of revenue and 32.5% of active customers. That share accounts for almost all of the reported drop. Please do not circulate the -30% figures.

## Like-for-like view (NA + APAC + LATAM only)

This compares the same three regions in both weeks. EMEA is excluded from both.

| Metric | Last week | This week | Change |
|---|---|---|---|
| Orders | 7,310 | 7,600 | **+4.0%** |
| Revenue (GBP) | 309,400 | 319,100 | **+3.1%** |
| Active customers | 26,710 | 27,200 | **+1.8%** |

### By region

| Region | Orders | Revenue (GBP) | Active customers |
|---|---|---|---|
| North America | 4,390 (+4.3%) | 192,800 (+3.4%) | 15,660 (+2.2%) |
| APAC | 2,210 (+3.3%) | 90,400 (+2.4%) | 8,000 (+1.1%) |
| LATAM | 1,000 (+4.2%) | 35,900 (+3.5%) | 3,540 (+1.7%) |
| EMEA | **missing** | **missing** | **missing** |

(Percentages are week-over-week changes against last week's figure for the same region.)

## Takeaways

- The three reporting regions are all growing modestly. Orders are up 3–4%, revenue is up 2–3.5%, and active customers are up 1–2%.
- Revenue is growing more slowly than orders in every region. That suggests flat or slightly lower revenue per order. The gap is small and based on one week of data, so I would only watch it.
- North America is the largest contributor. It added 180 orders and £6.4k of revenue, and it is about 60% of this week's revenue in the reporting regions.
- **EMEA performance this week is unknown.** I can't say whether it grew, shrank or stayed flat.

## Actions before this goes to leadership

1. Ask the data owner whether EMEA was dropped, renamed or remapped in the reorg. Check whether its rows now sit under a new region name or code that isn't in this extract.
2. Re-pull `this_week.csv` with EMEA, then re-run this review. The full four-region totals should replace the reported totals above.
3. Check last week's regional mapping against the new one. If the reorg moved countries between regions, the week-over-week comparison by region may not be like-for-like even after EMEA returns.
4. Until then, share only the like-for-like view above, and label it as excluding EMEA.

## Method

- Checked that the rows in each file sum to `reported_totals.csv`. All six totals match exactly.
- Compared the regions present in both files.
- Computed like-for-like changes on NA, APAC and LATAM only.
