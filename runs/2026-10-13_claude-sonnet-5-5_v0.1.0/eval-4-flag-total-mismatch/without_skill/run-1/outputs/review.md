# Weekly Metrics Review — week of 2026-10-13

## ⚠️ Data issue: this week's revenue does not reconcile

Finance's `reported_totals.csv` shows **£418,900** revenue for this week. The sum of the four regional exports is **£412,300**. The gap is **£6,600 (1.6%)**, with the regional exports lower.

All other figures reconcile exactly, for both weeks:

| Metric | Regional sum (this week) | Finance reported | Match |
|---|---|---|---|
| Orders | 10,520 | 10,520 | ✅ |
| Revenue (GBP) | 412,300 | 418,900 | ❌ (−6,600) |
| Active customers | 39,240 | 39,240 | ✅ |

Last week reconciles on all three metrics (10,890 / £462,300 / 39,580).

I haven't established the cause. Possible causes include a region's export being incomplete or stale, revenue that finance books outside these regions, or a typo in one figure. The regional numbers are used below, since they are the only ones that can be broken down by region. **Finance and the regional owners should confirm which figure is correct before this goes out as final.** If finance's figure is right, the week-on-week revenue drop is −9.4% instead of −10.8%.

## Headline (week on week)

| Metric | Last week | This week | Change | % |
|---|---|---|---|---|
| Orders | 10,890 | 10,520 | −370 | −3.4% |
| Revenue (GBP), regional sum | 462,300 | 412,300 | −50,000 | −10.8% |
| Revenue (GBP), finance reported | 462,300 | 418,900 | −43,400 | −9.4% |
| Active customers | 39,580 | 39,240 | −340 | −0.9% |
| Revenue per order (regional sum) | £42.45 | £39.19 | −£3.26 | −7.7% |

All three headline metrics declined. Revenue fell much faster than orders, so the fall is mostly lower revenue per order and not only fewer orders.

## By region

**Orders**

| Region | Last week | This week | Change | % |
|---|---|---|---|---|
| North America | 4,210 | 4,160 | −50 | −1.2% |
| EMEA | 3,580 | 3,420 | −160 | −4.5% |
| APAC | 2,140 | 2,050 | −90 | −4.2% |
| LATAM | 960 | 890 | −70 | −7.3% |

**Revenue (GBP)**

| Region | Last week | This week | Change | % |
|---|---|---|---|---|
| North America | 186,400 | 168,900 | −17,500 | −9.4% |
| EMEA | 152,900 | 134,600 | −18,300 | −12.0% |
| APAC | 88,300 | 79,200 | −9,100 | −10.3% |
| LATAM | 34,700 | 29,600 | −5,100 | −14.7% |

**Active customers**

| Region | Last week | This week | Change | % |
|---|---|---|---|---|
| North America | 15,320 | 15,280 | −40 | −0.3% |
| EMEA | 12,870 | 12,690 | −180 | −1.4% |
| APAC | 7,910 | 7,850 | −60 | −0.8% |
| LATAM | 3,480 | 3,420 | −60 | −1.7% |

## Observations

- **Every region declined on every metric.** The drop is broad, not isolated to one market.
- **EMEA made the largest absolute revenue drop (−£18.3k)**, just ahead of North America (−£17.5k). Together they account for about 72% of the regional revenue decline.
- **LATAM has the steepest percentage declines**: orders −7.3% and revenue −14.7%. It is the smallest region, so the effect on the total is limited.
- **North America's orders were nearly flat (−1.2%) but revenue fell 9.4%.** That points to lower order value, such as discounting, mix shift or smaller baskets, and not to lost demand. This is worth checking, and the data here doesn't confirm it.
- **Customer counts are comparatively stable (−0.9% overall)**, so the base is largely intact. Spend per order and order frequency are what moved.

## Suggested follow-ups

1. Reconcile the £6,600 revenue gap between the regional exports and finance's total before distribution.
2. Investigate the drop in revenue per order, starting with North America and EMEA (pricing, promotions, product mix).
3. Check whether LATAM's decline reflects a one-week dip or a trend.

*Source: `this_week.csv`, `last_week.csv`, `reported_totals.csv`. Percentages are rounded to one decimal place.*
