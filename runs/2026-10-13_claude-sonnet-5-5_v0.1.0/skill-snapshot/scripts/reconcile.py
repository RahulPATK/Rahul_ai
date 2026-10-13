#!/usr/bin/env python3
"""Reconcile a week's regional metrics before anything is written up.

Inputs (CSV):
  this_week.csv / last_week.csv   columns: region, <metric>, <metric>, ...
  reported_totals.csv             columns: metric, last_week, this_week
                                  (company totals from the system of record)

Prints JSON:
  status          "ok" or "stop"
  issues          list of {type, ...} explaining every reason to stop
  regions         per-region values and week-over-week % for each metric
  totals          per-metric regional sum vs reported total, both weeks

Stop reasons:
  missing_region  a region in last week's data is absent this week
  new_region      a region appears this week that was not there last week
  total_mismatch  regional values do not sum to the reported total
  bad_value       a blank or non-numeric value

Usage:
    python reconcile.py this_week.csv last_week.csv reported_totals.csv
"""

import csv
import json
import sys


def read_regions(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        metrics = [c for c in reader.fieldnames if c != "region"]
        rows = {r["region"].strip(): r for r in reader}
    return metrics, rows


def number(value):
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return None


def clean(x):
    return int(x) if x is not None and float(x).is_integer() else x


def main():
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    this_path, last_path, totals_path = sys.argv[1:]

    metrics, this_rows = read_regions(this_path)
    _, last_rows = read_regions(last_path)
    with open(totals_path, newline="") as f:
        reported = {r["metric"].strip(): r for r in csv.DictReader(f)}

    issues = []
    for region in last_rows:
        if region not in this_rows:
            issues.append({"type": "missing_region", "region": region})
    for region in this_rows:
        if region not in last_rows:
            issues.append({"type": "new_region", "region": region})

    regions = []
    for region, row in this_rows.items():
        entry = {"region": region}
        for m in metrics:
            tw = number(row.get(m))
            lw = number(last_rows[region].get(m)) if region in last_rows else None
            if tw is None:
                issues.append({"type": "bad_value", "region": region, "metric": m, "week": "this_week"})
            wow = round((tw - lw) / lw * 100, 1) if tw is not None and lw else None
            entry[m] = {"last_week": clean(lw), "this_week": clean(tw), "wow_pct": wow}
        regions.append(entry)

    totals = {}
    for m in metrics:
        totals[m] = {}
        for week, rows in (("this_week", this_rows), ("last_week", last_rows)):
            values = [number(r.get(m)) for r in rows.values()]
            regional_sum = sum(v for v in values if v is not None)
            rep = number(reported.get(m, {}).get(week))
            ok = rep is not None and abs(regional_sum - rep) < 0.5
            totals[m][week] = {"regional_sum": clean(regional_sum), "reported": clean(rep), "reconciles": ok}
            if not ok:
                issues.append({
                    "type": "total_mismatch", "metric": m, "week": week,
                    "regional_sum": clean(regional_sum), "reported": clean(rep),
                    "difference": clean(rep - regional_sum) if rep is not None else None,
                })

    print(json.dumps({
        "status": "stop" if issues else "ok",
        "issues": issues,
        "metrics": metrics,
        "regions": regions,
        "totals": totals,
    }, indent=2))


if __name__ == "__main__":
    main()
