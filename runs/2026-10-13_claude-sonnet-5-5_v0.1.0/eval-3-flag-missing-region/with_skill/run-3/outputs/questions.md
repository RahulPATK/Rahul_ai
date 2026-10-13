# Weekly metrics review — blocked, questions before I can write it

## 1. EMEA is in last week's data but not this week's

- `last_week.csv` has EMEA: orders 3,580, revenue 152,900 GBP, active customers 12,870.
- `this_week.csv` has no EMEA row. It has only North America, APAC and LATAM.
- `reported_totals.csv` this-week totals equal the sum of those three regions: orders 7,600, revenue 319,100, active customers 27,200. Last week's totals include EMEA (orders 10,890, revenue 462,300, active customers 39,580).
- Read as-is, the company total would fall about 30% in orders (10,890 to 7,600) and about 31% in revenue (462,300 to 319,100).

**Question:** Was EMEA merged into another region in the reorg, or is this week's EMEA extract missing? That also covers whether the reported totals already leave EMEA out.

- If it was merged, which region(s) absorbed it? I also need last week's figures restated on the new region structure so the week-over-week comparison is like-for-like.
- If the extract is missing, please send the EMEA row for this week. Finance should then confirm whether the reported totals should include EMEA.

I haven't written `review.md` or a company total, and I haven't estimated any EMEA figure.
