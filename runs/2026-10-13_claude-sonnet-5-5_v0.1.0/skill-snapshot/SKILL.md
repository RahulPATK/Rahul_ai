---
name: weekly-metrics-review
description: Prepares the Monday weekly metrics review — regional tables (this week vs last week, week-over-week %) reconciled to the reported company totals, plus 2-3 focus areas for leadership. Use this whenever someone asks for the weekly metrics review, the Monday KPI pack, regional week-over-week numbers, or wants this week's metrics checked against finance totals and written up, even if they just say "prep the numbers for the leadership sync". It never guesses a number — when a region is missing or totals don't reconcile it stops and asks. Not for narrative status updates from notes, charts or dashboards, or writing SQL.
metadata:
  version: 0.1.0
---

# Weekly metrics review

Leadership reads this review on Monday and acts on it. A wrong number in it does far
more damage than a late review, so the rule for this skill is: **every number must come
straight from the source files, and if the source files don't agree with each other,
stop and ask instead of writing the review.** Never estimate, back-fill, carry forward,
or "adjust" a figure to make things add up.

## Inputs

In the working folder (or wherever the user points):

- `this_week.csv`, `last_week.csv` — one row per region: `region, <metric>, <metric>, ...`
- `reported_totals.csv` — company totals from the system of record: `metric, last_week, this_week`

## Step 1 — Reconcile first

Run the bundled checker before writing anything:

```bash
python <skill-dir>/scripts/reconcile.py this_week.csv last_week.csv reported_totals.csv
```

It returns JSON with `status` (`ok` or `stop`), a list of `issues`, per-region values
with week-over-week %, and regional sums vs reported totals. Use its numbers rather than
doing arithmetic by hand.

## Step 2a — If status is `stop`: ask, don't write the review

Do **not** create `review.md`, and do not produce a partial review or a company total.
Instead write `questions.md` and end your reply with the same questions. For each issue:

- say exactly what doesn't line up, with the numbers from the files
  (e.g. "Regional revenue sums to 412,300 but reported_totals.csv says 418,900 — a gap of 6,600");
- ask the specific question that would resolve it
  (e.g. "EMEA is in last week's data but not this week's. Was it merged into another
  region in the reorg, or is this week's EMEA extract missing?");
- don't propose a "best guess" figure — offering one invites people to use it.

## Step 2b — If status is `ok`: write `review.md`

Use this structure:

```markdown
# Weekly metrics review — <week label if known>

## Metrics
| Region | Orders | Orders WoW | Revenue (GBP) | Revenue WoW | Active customers | Customers WoW |
|---|---|---|---|---|---|---|
| North America | 4,355 | +3.4% | 191,200 | +2.6% | 15,610 | +1.9% |
| ... one row per region, in source order ... |
| **Total** | <reported total> | ... | ... | ... | ... | ... |

## Focus areas
- 2–3 bullets on the largest week-over-week movers, quoting the figures.

## Data checks
- One line confirming regions match last week and totals reconcile to reported_totals.csv.
```

Adapt the columns to the metrics actually present. Copy values exactly as they appear in
the source (thousands separators are fine; no rounding, no unit changes).

For focus areas, describe *what* moved and by how much. Don't explain *why* unless the
user gave you the reason — an invented cause ("likely due to the promo") reads as fact
to the people acting on it. A large move that reconciles is real data: report it
plainly rather than treating it as an error.
