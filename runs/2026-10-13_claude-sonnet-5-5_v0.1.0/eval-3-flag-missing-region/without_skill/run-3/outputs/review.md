# Weekly Metrics Review (week ending 2026-10-13)

## Headline: the reported ~31% drop is a data gap, not a business decline

**EMEA is missing from `this_week.csv`.** Last week had four regions (North America, EMEA, APAC, LATAM). This week has three. The EMEA row is absent, not zero. The reported "this week" totals equal the sum of the three remaining regions exactly (7,600 orders / £319,100 / 27,200 customers). They therefore leave out EMEA entirely.

EMEA was about a third of the business last week (32.9% of orders, 33.1% of revenue, 32.5% of customers). That accounts almost exactly for the apparent fall.

**Do not circulate the reported totals as a performance result.** Whether EMEA's data feed failed to load or was dropped or re-mapped in the regional reorg is something I can't tell from these files. It needs confirming with the data owner. I have not estimated or filled in EMEA numbers.

## As reported (misleading)

| Metric | Last week | This week | Change |
|---|---|---|---|
| Orders | 10,890 | 7,600 | -30.2% |
| Revenue (GBP) | 462,300 | 319,100 | -31.0% |
| Active customers | 39,580 | 27,200 | -31.3% |

## Like-for-like (excluding EMEA in both weeks)

| Metric | Last week | This week | Change |
|---|---|---|---|
| Orders | 7,310 | 7,600 | +290 (+4.0%) |
| Revenue (GBP) | 309,400 | 319,100 | +9,700 (+3.1%) |
| Active customers | 26,710 | 27,200 | +490 (+1.8%) |

### By region

| Region | Orders | Δ | Revenue (GBP) | Δ | Active customers | Δ |
|---|---|---|---|---|---|---|
| North America | 4,390 | +4.3% | 192,800 | +3.4% | 15,660 | +2.2% |
| APAC | 2,210 | +3.3% | 90,400 | +2.4% | 8,000 | +1.1% |
| LATAM | 1,000 | +4.2% | 35,900 | +3.5% | 3,540 | +1.7% |
| **EMEA** | **missing** | n/a | **missing** | n/a | **missing** | n/a |

(Last week EMEA: 3,580 orders, £152,900 revenue, 12,870 active customers.)

## Takeaways

- The three regions we can see all grew on every metric. Orders were up 3–4%, revenue up 2–4% and customers up 1–2%.
- Revenue grew more slowly than orders in each region (it is also slower than orders in aggregate: +3.1% vs +4.0%). That suggests slightly lower average order value, though the change is small.
- **We have no view of EMEA this week**, so we cannot say whether the company as a whole grew or shrank. If EMEA were flat on last week, the total would be about 11,180 orders and £472,000 revenue (rough illustration only, not a forecast).

## Actions

1. Confirm with the data owner why EMEA is absent from `this_week.csv`. Check the pipeline, and check whether the reorg changed the region name or mapping (for example EMEA split or merged into another region).
2. Once the EMEA data is supplied, re-run the review and issue corrected totals.
3. Make the reported-totals process fail or flag when a region present last week is missing this week.

## Method and checks

- Last week's regional rows sum to the reported last-week totals (10,890 / 462,300 / 39,580).
- This week's regional rows sum to the reported this-week totals (7,600 / 319,100 / 27,200), which confirms the totals were built without EMEA.
- Percentages are rounded to one decimal place.
