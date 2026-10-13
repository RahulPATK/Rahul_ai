# Weekly metrics review: blocked, questions before I can write it

I have not written `review.md`. The inputs don't line up, and a review built on them would mislead leadership.

## EMEA is missing from this week's data

- `last_week.csv` has EMEA: orders 3,580, revenue 152,900 GBP, active customers 12,870.
- `this_week.csv` has no EMEA row. It has only North America, APAC and LATAM.
- `reported_totals.csv` this week is orders 7,600, revenue 319,100 and active customers 27,200. These equal the sum of the three regions present, so the reported totals also appear to exclude EMEA.
- Last week's reported totals (10,890 / 462,300 / 39,580) do include EMEA.

This leaves two questions:

1. Was EMEA merged into another region in the reorg, or is this week's EMEA extract missing?
2. If the extract is missing, are the this-week totals in `reported_totals.csv` also incomplete? Total orders would otherwise show -30.2% week over week, revenue -31.0% and active customers -31.3%, which is the loss of a whole region rather than a real movement.

If EMEA was merged into another region, I also need the last-week figures restated on the new region structure. Otherwise the week-over-week % for the receiving region will be wrong.

I haven't estimated or carried forward any EMEA figure. Once you send the corrected files or confirm the reorg mapping, I'll re-run the reconciliation and write the review.
