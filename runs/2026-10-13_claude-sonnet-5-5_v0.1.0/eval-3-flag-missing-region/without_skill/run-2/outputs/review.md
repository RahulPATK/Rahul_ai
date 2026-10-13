# Weekly Metrics Review — week ending 2026-10-13

## ⚠️ Read this first: EMEA is missing from this week's data

`this_week.csv` contains only North America, APAC and LATAM. **EMEA has no row.** Last week EMEA was ~33% of orders, ~33% of revenue and ~33% of active customers.

The reported totals (`reported_totals.csv`) reconcile exactly to the three regions present, so EMEA is simply absent from them rather than being reported as zero or tracked separately. The headline drop below is therefore **a data-coverage gap, not a business decline**. I can't tell from the files whether EMEA is a late/failed feed, a reorg mapping issue (e.g. EMEA split or renamed in the new regional structure), or a real outage. This needs confirming with the data owner before the numbers go to leadership.

## Headline as reported (not like-for-like)

| Metric | Last week | This week | Change |
|---|---|---|---|
| Orders | 10,890 | 7,600 | −30.2% |
| Revenue (GBP) | 462,300 | 319,100 | −31.0% |
| Active customers | 39,580 | 27,200 | −31.3% |

**Do not present these as a performance decline.** They compare four regions against three.

## Like-for-like (excluding EMEA from both weeks)

| Metric | Last week (ex-EMEA) | This week | Change |
|---|---|---|---|
| Orders | 7,310 | 7,600 | +4.0% |
| Revenue (GBP) | 309,400 | 319,100 | +3.1% |
| Active customers | 26,710 | 27,200 | +1.8% |

## By region

| Region | Orders | WoW | Revenue (GBP) | WoW | Active customers | WoW |
|---|---|---|---|---|---|---|
| North America | 4,390 | +4.3% | 192,800 | +3.4% | 15,660 | +2.2% |
| APAC | 2,210 | +3.3% | 90,400 | +2.4% | 8,000 | +1.1% |
| LATAM | 1,000 | +4.2% | 35,900 | +3.5% | 3,540 | +1.7% |
| **EMEA** | **missing** | n/a | **missing** | n/a | **missing** | n/a |

(Last week EMEA: 3,580 orders, £152,900 revenue, 12,870 active customers.)

## Takeaways

- The three reporting regions are all modestly up on every metric: orders +3–4%, revenue +2–3.5%, customers +1–2%. Nothing stands out as unusual.
- **EMEA performance this week is unknown.** No conclusion can be drawn on it or on company-wide totals.
- Revenue is growing a bit slower than orders in every region, so average order value is slipping slightly (e.g. North America £44.3 → £43.9). It is small, but worth watching.

## Actions

1. Confirm with the data/reporting owner why EMEA is absent (feed failure, late load, or region mapping after the reorg).
2. Re-run the review with EMEA included before circulating company-wide totals.
3. If the reorg changed region definitions, check that last week's and this week's files use the same mapping, and add a check that flags any region present in one week but not the other.

## Method

Totals were recomputed from the regional rows and match `reported_totals.csv` in both weeks. Percentages are week-over-week changes, rounded to one decimal place.
