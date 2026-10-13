#!/usr/bin/env python3
"""Build the cross-model comparison page from runs/*/benchmark.json.

Reads the latest run per model (plus the one before it, for "since last run"),
and writes one static HTML file. No model calls.

Usage:
    python3 -B reports/build_report.py --subject subjects/weekly-metrics-review \
        [--models claude-opus-5-5 claude-sonnet-5-5 claude-haiku-5-5] [--out reports/index.html]

Models with no run yet are shown as "Not run yet" so the matrix shape stays visible.
"""

import argparse
import html
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "runs"
DEFAULT_MODELS = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]
LABELS = {"claude-opus-5-5": "Opus 5.5", "claude-sonnet-5-5": "Sonnet 5.5", "claude-haiku-5-5": "Haiku 5.5"}


def esc(x) -> str:
    return html.escape(str(x))


def pct(x) -> str:
    return "—" if x is None else f"{x * 100:.0f}%"


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


# ---------------------------------------------------------------- load

def runs_for(model: str) -> list[Path]:
    """Run folders for a model, oldest first. Folder names start with the date."""
    return sorted(p for p in RUNS.glob(f"*_{model}_v*") if (p / "benchmark.json").exists())


def load_run(run_dir: Path, kinds: dict[str, str]) -> dict:
    bench = json.loads((run_dir / "benchmark.json").read_text())
    cfg = json.loads((run_dir / "run_config.json").read_text())
    by_case = defaultdict(lambda: defaultdict(list))
    failures = defaultdict(lambda: defaultdict(int))
    for r in bench["runs"]:
        by_case[r["eval_name"]][r["configuration"]].append(r["result"]["pass_rate"])
        for e in r.get("expectations", []):
            if not e["passed"]:
                failures[(r["eval_name"], r["configuration"])][e["text"]] += 1

    cost = defaultdict(list)
    for t in run_dir.glob("eval-*/*/run-*/timing.json"):
        cost[t.parent.parent.name].append(json.loads(t.read_text()).get("cost_usd"))
    grader_cost = 0.0
    for g in run_dir.glob("eval-*/*/run-*/grader_transcript.jsonl"):
        for line in g.read_text().splitlines():
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("type") == "result":
                grader_cost += e.get("total_cost_usd") or 0

    def strict(kind, config):
        cases = [c for c, k in kinds.items() if k == kind and c in by_case]
        rates = [x for c in cases for x in by_case[c].get(config, [])]
        return sum(1 for x in rates if x == 1.0), len(rates)

    rs = bench["run_summary"]
    return {
        "dir": run_dir,
        "date": run_dir.name.split("_")[0],
        "version": cfg.get("skill_version"),
        "runs": cfg.get("runs"),
        "grader": cfg.get("grader_model"),
        "summary": rs,
        "by_case": by_case,
        "failures": failures,
        "pass_strict": {c: strict("pass", c) for c in ("with_skill", "without_skill")},
        "flag_strict": {c: strict("flag", c) for c in ("with_skill", "without_skill")},
        "trigger": bench.get("trigger_eval"),
        "cost": {k: mean(v) for k, v in cost.items()},
        "grader_cost": grader_cost,
    }


# ---------------------------------------------------------------- render pieces

def state(rate) -> str:
    if rate is None:
        return "na"
    return "good" if rate >= 0.999 else "warn" if rate >= 0.6 else "bad"


def tile(label, value, sub, cls=""):
    return (f'<div class="tile {cls}"><div class="tile-label">{esc(label)}</div>'
            f'<div class="tile-value">{value}</div><div class="tile-sub">{sub}</div></div>')


def model_card(model, run):
    name = LABELS.get(model, model)
    if run is None:
        return (f'<section class="model empty"><header><h3>{esc(name)}</h3><code>{esc(model)}</code></header>'
                f'<p class="empty-note">Not run yet. Run it with<br><code>python3 -B runner/run.py --subject … '
                f'--models {esc(model)}</code></p></section>')
    s = run["summary"]
    w, wo = s.get("with_skill", {}), s.get("without_skill", {})
    lift = (w.get("pass_rate", {}).get("mean", 0) - wo.get("pass_rate", {}).get("mean", 0)) if wo else None
    ps, fs = run["pass_strict"]["with_skill"], run["flag_strict"]["with_skill"]
    psb, fsb = run["pass_strict"]["without_skill"], run["flag_strict"]["without_skill"]
    trig = run["trigger"] or {}
    tsum = trig.get("summary", {})
    tiles = [
        tile("Pass cases", f"{ps[0]}/{ps[1]}", f"fully correct · without skill {psb[0]}/{psb[1]}",
             state(ps[0] / ps[1] if ps[1] else None)),
        tile("Flag cases", f"{fs[0]}/{fs[1]}", f"stopped and asked · without skill {fsb[0]}/{fsb[1]}",
             state(fs[0] / fs[1] if fs[1] else None)),
        tile("Trigger accuracy", f"{tsum.get('passed', '—')}/{tsum.get('total', '—')}",
             f"fires {pct(trig.get('should_trigger_rate'))} when it should, "
             f"{pct(trig.get('should_not_trigger_rate'))} when it shouldn't",
             state(tsum['passed'] / tsum['total'] if tsum.get('total') else None)),
        tile("Skill lift", f"{lift:+.0%}" if lift is not None else "—",
             f"assertion pass rate {pct(w.get('pass_rate', {}).get('mean'))} vs {pct(wo.get('pass_rate', {}).get('mean'))}"),
        tile("Cost per run", f"${run['cost'].get('with_skill') or 0:.3f}",
             f"without skill ${run['cost'].get('without_skill') or 0:.3f} · grading ${run['grader_cost']:.2f} total"),
        tile("Time per run", f"{w.get('time_seconds', {}).get('mean', 0):.1f}s",
             f"± {w.get('time_seconds', {}).get('stddev', 0):.1f}s · without skill {wo.get('time_seconds', {}).get('mean', 0):.1f}s"),
    ]
    return (f'<section class="model"><header><h3>{esc(name)}</h3><code>{esc(model)}</code>'
            f'<span class="meta">{esc(run["date"])} · skill v{esc(run["version"])} · {run["runs"]} repeats</span></header>'
            f'<div class="tiles">{"".join(tiles)}</div></section>')


def case_matrix(cases, models, latest):
    head = "".join(f'<th colspan="2">{esc(LABELS.get(m, m))}</th>' for m in models)
    sub = "".join('<th class="sub">with skill</th><th class="sub">without</th>' for _ in models)
    rows = []
    for c in cases:
        cells = []
        for m in models:
            run = latest.get(m)
            if run is None:
                cells.append('<td class="na" colspan="2">Not run</td>')
                continue
            for config in ("with_skill", "without_skill"):
                rates = run["by_case"].get(c["name"], {}).get(config, [])
                full = sum(1 for x in rates if x == 1.0)
                avg = mean(rates)
                cells.append(f'<td class="cell {state(avg)}"><span class="big">{full}/{len(rates)}</span>'
                             f'<span class="small">{pct(avg)} of checks</span></td>' if rates else '<td class="na">—</td>')
        rows.append(f'<tr><th class="case"><span class="kind {c["kind"]}">{c["kind"]}</span>{esc(c["name"])}'
                    f'<span class="desc">{esc(c["expected_output"])}</span></th>{"".join(cells)}</tr>')
    return (f'<div class="scroll"><table class="matrix"><thead><tr><th class="case">Case</th>{head}</tr>'
            f'<tr><th></th>{sub}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
            f'<p class="note">Big number: runs where every check passed. Small: share of individual checks passed.</p>')


def trigger_table(queries, models, latest):
    head = "".join(f"<th>{esc(LABELS.get(m, m))}</th>" for m in models)
    rows = []
    for q in queries:
        cells = []
        for m in models:
            run = latest.get(m)
            res = {r["query"]: r for r in ((run or {}).get("trigger") or {}).get("results", [])}
            r = res.get(q["query"])
            if r is None:
                cells.append('<td class="na">Not run</td>')
                continue
            cls = "good" if r["pass"] else "bad"
            cells.append(f'<td class="cell {cls}"><span class="big">{r["triggers"]}/{r["runs"]}</span>'
                         f'<span class="small">{"correct" if r["pass"] else "wrong"}</span></td>')
        expect = "should fire" if q["should_trigger"] else "should not fire"
        rows.append(f'<tr><th class="case"><span class="kind {"pass" if q["should_trigger"] else "neg"}">{expect}</span>'
                    f'<span class="query">{esc(q["query"])}</span></th>{"".join(cells)}</tr>')
    return (f'<div class="scroll"><table class="matrix"><thead><tr><th class="case">Query</th>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>'
            f'<p class="note">Times the skill was invoked out of the runs for that query.</p>')


def failures_list(models, latest):
    items = []
    for m in models:
        run = latest.get(m)
        if not run:
            continue
        for (case, config), fails in sorted(run["failures"].items()):
            n = len(run["by_case"][case][config])
            for text, count in sorted(fails.items(), key=lambda kv: -kv[1]):
                items.append(f'<li><span class="who">{esc(LABELS.get(m, m))} · {esc(case)} · '
                             f'{config.replace("_", " ")}</span><span class="what">{esc(text)}</span>'
                             f'<span class="count">{count}/{n}</span></li>')
    return f'<ul class="fails">{"".join(items)}</ul>' if items else '<p class="note">No failed checks.</p>'


def changes(models, history):
    items = []
    for m in models:
        runs = history.get(m, [])
        if len(runs) < 2:
            if runs:
                items.append(f"<li>{esc(LABELS.get(m, m))}: first run ({esc(runs[-1]['date'])}), nothing to compare yet.</li>")
            continue
        prev, cur = runs[-2], runs[-1]
        for case in cur["by_case"]:
            a = mean(prev["by_case"].get(case, {}).get("with_skill", []))
            b = mean(cur["by_case"][case].get("with_skill", []))
            if a is not None and b is not None and abs(b - a) >= 0.01:
                cls = "good" if b > a else "bad"
                items.append(f'<li class="{cls}">{esc(LABELS.get(m, m))} · {esc(case)}: {pct(a)} → {pct(b)} '
                             f'(v{esc(prev["version"])} {esc(prev["date"])} → v{esc(cur["version"])} {esc(cur["date"])})</li>')
    return f'<ul class="changes">{"".join(items)}</ul>'


# ---------------------------------------------------------------- page

CSS = """
/* Layout: one column; summary per model, then case x model matrix, triggers, failures, notes. */
:root {
  --bg: #f6f7f9; --surface: #ffffff; --ink: #18202b; --muted: #5b6676; --line: #dde2e9;
  --accent: #1f5e8c; --good: #1d7a4c; --good-bg: #e6f4ec; --warn: #9a6400; --warn-bg: #fbf1dc;
  --bad: #b3322a; --bad-bg: #fbe9e7; --na-bg: #eef0f3;
  --display: "Schibsted Grotesk", "Helvetica Neue", Arial, sans-serif;
  --body: "Source Sans 3", "Segoe UI", Arial, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #11161d; --surface: #18202a; --ink: #e6ebf1; --muted: #9aa6b5; --line: #2a3542;
  --accent: #7fb6e0; --good: #6fd19c; --good-bg: #16302a; --warn: #e8b85c; --warn-bg: #33291a;
  --bad: #f08a80; --bad-bg: #3a1f1d; --na-bg: #1e2732; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #11161d; --surface: #18202a; --ink: #e6ebf1; --muted: #9aa6b5; --line: #2a3542;
  --accent: #7fb6e0; --good: #6fd19c; --good-bg: #16302a; --warn: #e8b85c; --warn-bg: #33291a;
  --bad: #f08a80; --bad-bg: #3a1f1d; --na-bg: #1e2732; color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.5 var(--body); }
.wrap { max-width: 1120px; margin: 0 auto; padding-inline: 20px; padding-block: 32px 56px; display: grid; gap: 40px; }
.wrap > * { min-width: 0; }
h1, h2, h3 { font-family: var(--display); text-wrap: balance; margin: 0; }
h1 { font-size: 2rem; letter-spacing: -0.01em; }
h2 { font-size: 1.3rem; margin-bottom: 4px; }
h3 { font-size: 1.1rem; }
.lede { color: var(--muted); max-width: 68ch; margin: 8px 0 0; }
.facts { display: flex; flex-wrap: wrap; gap: 8px 20px; margin-top: 14px; font: 13px var(--mono); color: var(--muted); }
.section-intro { color: var(--muted); margin: 0 0 14px; max-width: 70ch; }
.models { display: grid; gap: 16px; }
.model { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 18px; min-width: 0; }
.model header { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 14px; margin-bottom: 14px; }
.model header code { font: 13px var(--mono); color: var(--muted); }
.model .meta { margin-left: auto; font: 13px var(--mono); color: var(--muted); }
.model.empty { background: transparent; border-style: dashed; }
.empty-note { color: var(--muted); margin: 0; }
.empty-note code { font: 13px var(--mono); overflow-wrap: anywhere; }
.tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; }
.tile { border-top: 3px solid var(--line); padding: 10px 2px 2px; min-width: 0; }
.tile.good { border-top-color: var(--good); } .tile.warn { border-top-color: var(--warn); } .tile.bad { border-top-color: var(--bad); }
.tile-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }
.tile-value { font: 600 1.6rem var(--display); font-variant-numeric: tabular-nums; margin: 2px 0; }
.tile-sub { font-size: 13px; color: var(--muted); }
.scroll { overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); }
table.matrix { border-collapse: collapse; width: 100%; min-width: 640px; }
.matrix th, .matrix td { padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: center; vertical-align: top; }
.matrix thead th { font: 600 13px var(--display); background: var(--surface); }
.matrix th.sub { font: 12px var(--body); color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
.matrix th.case { text-align: left; font: 600 14px var(--body); width: 40%; }
.matrix tbody tr:last-child th, .matrix tbody tr:last-child td { border-bottom: 0; }
.desc, .query { display: block; font-weight: 400; color: var(--muted); font-size: 13px; margin-top: 4px; }
.query { color: var(--ink); font-size: 14px; }
.kind { display: inline-block; font: 600 11px var(--mono); text-transform: uppercase; letter-spacing: 0.05em;
  padding: 1px 6px; border-radius: 4px; margin-right: 8px; border: 1px solid currentColor; }
.kind.pass { color: var(--good); } .kind.flag { color: var(--warn); } .kind.neg { color: var(--muted); }
.cell .big { display: block; font: 600 1.05rem var(--mono); font-variant-numeric: tabular-nums; }
.cell .small { display: block; font-size: 12px; color: var(--muted); }
td.good { background: var(--good-bg); } td.good .big { color: var(--good); }
td.warn { background: var(--warn-bg); } td.warn .big { color: var(--warn); }
td.bad { background: var(--bad-bg); } td.bad .big { color: var(--bad); }
td.na { background: var(--na-bg); color: var(--muted); font-size: 13px; }
.note { font-size: 13px; color: var(--muted); margin: 8px 0 0; }
.fails { list-style: none; padding: 0; margin: 0; display: grid; gap: 1px; background: var(--line);
  border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
.fails li { background: var(--surface); display: grid; grid-template-columns: 1fr auto; gap: 2px 16px; padding: 10px 14px; }
.fails .who { font: 12px var(--mono); color: var(--muted); grid-column: 1; }
.fails .what { grid-column: 1; }
.fails .count { grid-column: 2; grid-row: 1 / span 2; align-self: center; font: 600 14px var(--mono); color: var(--bad); }
.changes { margin: 0; padding-left: 20px; } .changes li.good { color: var(--good); } .changes li.bad { color: var(--bad); }
.caveats { margin: 0; padding-left: 20px; max-width: 75ch; } .caveats li + li { margin-top: 6px; }
a { color: var(--accent); }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
@media (max-width: 560px) { h1 { font-size: 1.6rem; } .model .meta { margin-left: 0; } }
"""


def build(subject: Path, models: list[str], out: Path, caveats: list[str]) -> None:
    evals = json.loads((subject / "evals.json").read_text())
    cases = evals["evals"]
    kinds = {c["name"]: c.get("kind", "pass") for c in cases}
    history = {m: [load_run(p, kinds) for p in runs_for(m)] for m in models}
    latest = {m: (h[-1] if h else None) for m, h in history.items()}
    done = [m for m in models if latest[m]]

    total_calls = sum(1 for m in done for _ in latest[m]["dir"].glob("eval-*/*/run-*"))
    facts = [f"skill: {evals['skill_name']}",
             f"models run: {len(done)} of {len(models)}",
             f"cases: {sum(k == 'pass' for k in kinds.values())} pass · {sum(k == 'flag' for k in kinds.values())} flag · "
             f"{len(evals.get('trigger_queries', []))} trigger queries",
             f"executor runs: {total_calls}",
             f"grader: {latest[done[0]]['grader'] if done else '—'}",
             f"built {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC"]

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Skill Eval Lab</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Schibsted+Grotesk:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap">
<style>{CSS}</style></head>
<body><main class="wrap">
<header>
  <h1>{esc(evals['skill_name'])} across models</h1>
  <p class="lede">Does the skill fire when it should, produce numbers that match the source, stop and ask when
  the data doesn't add up, and what does that cost? Each model runs every case with and without the skill.
  Deterministic checks run first; skill-creator's grader judges the rest.</p>
  <div class="facts">{"".join(f"<span>{esc(f)}</span>" for f in facts)}</div>
</header>

<section><h2>Summary by model</h2>
<p class="section-intro">Pass and flag counts are runs where every check passed. Tiles are coloured by that strict result.</p>
<div class="models">{"".join(model_card(m, latest[m]) for m in models)}</div></section>

<section><h2>Cases</h2>
<p class="section-intro">Each case × model, with and without the skill.</p>
{case_matrix(cases, models, latest)}</section>

<section><h2>Trigger accuracy</h2>
<p class="section-intro">Does the skill get picked up from the description alone? Measured with skill-creator's run_eval.</p>
{trigger_table(evals.get("trigger_queries", []), models, latest)}</section>

<section><h2>What failed</h2>
<p class="section-intro">Every check that failed at least once, with how many runs it failed in.</p>
{failures_list(models, latest)}</section>

<section><h2>Since last run</h2>
{changes(models, history)}</section>

<section><h2>Read with care</h2><ul class="caveats">{"".join(f"<li>{c}</li>" for c in caveats)}</ul></section>
</main></body></html>
"""
    out.write_text(page)
    print(f"wrote {out.relative_to(REPO)}  ({len(done)} of {len(models)} models have runs)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subject", required=True, type=Path)
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--out", type=Path, default=REPO / "reports" / "index.html")
    ap.add_argument("--caveats", type=Path, help="JSON list of HTML strings shown under 'Read with care'")
    args = ap.parse_args()
    caveats_file = args.caveats or (args.subject / "report_caveats.json")
    caveats = json.loads(caveats_file.read_text()) if caveats_file.exists() else []
    build(args.subject.resolve(), args.models, args.out.resolve(), caveats)


if __name__ == "__main__":
    main()
