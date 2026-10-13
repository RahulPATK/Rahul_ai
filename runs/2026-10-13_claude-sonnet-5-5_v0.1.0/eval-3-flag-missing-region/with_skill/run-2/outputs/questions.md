# Weekly metrics review: blocked, questions before I can write it

I have not written `review.md`. One issue needs an answer first.

## EMEA is missing from this week's data

- `last_week.csv` has EMEA: 3,580 orders, 152,900 GBP revenue, 12,870 active customers.
- `this_week.csv` has no EMEA row. It only has North America, APAC and LATAM.
- `reported_totals.csv` for this week equals the sum of those three regions exactly:
  - Orders: 7,600
  - Revenue: 319,100 GBP
  - Active customers: 27,200
- Last week's reported totals (10,890 orders, 462,300 GBP, 39,580 customers) include EMEA.
- So the reported totals reconcile to the regional rows, but the two weeks cover different sets of regions. The reported week-over-week drop (orders 10,890 to 7,600, revenue 462,300 to 319,100 GBP, customers 39,580 to 27,200) is not like-for-like.

**Questions**
1. Was EMEA merged into another region or renamed in the reorg? If so, which region(s), and should last week be restated to the new structure?
2. Or is this week's EMEA extract missing from `this_week.csv`? If so, can you send it?
3. If the extract is missing, was it also left out of the system-of-record totals in `reported_totals.csv`? Those totals may need to be re-issued.

Once I have an answer, I'll rerun the reconciliation and write `review.md`.
