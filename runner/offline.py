"""Canned executor outputs for --offline, so the pipeline can be tested without model calls.

with_skill    behaves the way the skill asks: reconcile, then either review.md or questions.md
without_skill a naive baseline that always writes review.md, totalling the regions itself

These say nothing about real model behaviour; they only prove that the runner,
deterministic checks and skill-creator's aggregation fit together.
"""

import csv
import json
import subprocess
import sys
from pathlib import Path


def _rows(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _n(x) -> str:
    return f"{float(x):,.0f}"


def _review(this_rows, last_rows, totals) -> str:
    metrics = [k for k in this_rows[0] if k != "region"]
    last = {r["region"]: r for r in last_rows}
    head = "| Region | " + " | ".join(f"{m} | {m} WoW" for m in metrics) + " |"
    lines = ["# Weekly metrics review", "", "## Metrics", head, "|" + "---|" * (1 + 2 * len(metrics))]
    for r in this_rows:
        cells = []
        for m in metrics:
            lw = float(last.get(r["region"], {}).get(m) or 0)
            wow = f"{(float(r[m]) - lw) / lw * 100:+.1f}%" if lw else "n/a"
            cells += [_n(r[m]), wow]
        lines.append(f"| {r['region']} | " + " | ".join(cells) + " |")
    total_cells = [c for m in metrics for c in (_n(totals[m]), "")]
    lines.append("| **Total** | " + " | ".join(total_cells) + " |")
    lines += ["", "## Focus areas", "- " + ", ".join(r["region"] for r in this_rows) + " reported this week.",
              "", "## Data checks", "- Regions and totals checked."]
    return "\n".join(lines) + "\n"


def write_fixture(case: dict, config: str, work: Path) -> None:
    this_rows, last_rows = _rows(work / "this_week.csv"), _rows(work / "last_week.csv")
    reported = {r["metric"]: r["this_week"] for r in _rows(work / "reported_totals.csv")}

    if config == "without_skill":
        sums = {m: sum(float(r[m]) for r in this_rows) for m in this_rows[0] if m != "region"}
        (work / "review.md").write_text(_review(this_rows, last_rows, sums))
        (work / "_reply.md").write_text("Done — review.md is ready.")
        return

    script = work / ".claude" / "skills" / "weekly-metrics-review" / "scripts" / "reconcile.py"
    out = subprocess.run([sys.executable, str(script), "this_week.csv", "last_week.csv", "reported_totals.csv"],
                         cwd=work, capture_output=True, text=True, check=True)
    result = json.loads(out.stdout)
    if result["status"] == "ok":
        (work / "review.md").write_text(_review(this_rows, last_rows, reported))
        (work / "_reply.md").write_text("review.md is ready; regions and totals reconcile.")
        return

    qs = []
    for i in result["issues"]:
        if i["type"] == "missing_region":
            qs.append(f"- {i['region']} is in last week's data but missing this week. Was it merged into "
                      f"another region in the reorg, or is the extract incomplete?")
        elif i["type"] == "total_mismatch":
            qs.append(f"- {i['metric']} ({i['week']}): regions sum to {_n(i['regional_sum'])} but "
                      f"reported_totals.csv says {_n(i['reported'])}. Which figure is correct?")
        else:
            qs.append(f"- {json.dumps(i)}")
    text = "# Questions before the review\n\n" + "\n".join(qs) + "\n"
    (work / "questions.md").write_text(text)
    (work / "_reply.md").write_text("I stopped before writing the review:\n\n" + text)
