#!/usr/bin/env python3
"""Run a subject skill's evals across one or more Claude models.

For each model this produces runs/<date>_<model>_v<skill-version>/ laid out the way
skill-creator expects, so its aggregate_benchmark script and eval-viewer work on it:

    <run>/
      skill-snapshot/                     exact skill tested
      run_config.json                     models, flags, environment notes
      eval-<id>-<name>/
        eval_metadata.json
        <configuration>/run-<k>/          configuration = with_skill | without_skill
          outputs/                        files the run produced + final_response.md, metrics.json
          transcript.jsonl / transcript.md
          timing.json                     tokens and duration
          grading.json                    deterministic checks first, then skill-creator's grader
      triggers/                           skill-creator run_eval results for trigger queries
      benchmark.json / benchmark.md       skill-creator aggregate_benchmark (+ trigger_eval)

Usage:
    python runner/run.py --subject subjects/weekly-metrics-review \
        --models claude-sonnet-5-5 [more models...] [--runs 3] [--dry-run]

    --dry-run   print the plan and call counts; no model calls
    --offline   exercise the whole pipeline with canned outputs; no model calls
    --regrade <run folder>   re-run deterministic checks on an existing run; no model calls
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import checks
import offline

REPO = Path(__file__).resolve().parent.parent
RUNNER = REPO / "runner"
SKILL_CREATOR = REPO / "vendor" / "skill-creator"
RUNS = REPO / "runs"

CONFIGS = ("with_skill", "without_skill")
DEFAULT_GRADER_MODEL = "claude-opus-5-5"
# Executor tools: enough to read the CSVs, run the skill's script and write outputs.
# Bash is limited to read/python commands so a run can't touch git or delete files.
EXECUTOR_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Skill",
                  "Bash(python3:*)", "Bash(python:*)", "Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)"]
GRADER_TOOLS = ["Read", "Glob", "Grep", "Write"]


# ---------------------------------------------------------------- setup

def parse_frontmatter(skill_md: Path) -> tuple[str, str]:
    """Return (name, metadata.version) from SKILL.md frontmatter."""
    name, version, in_meta = "", "0.0.0", False
    lines = skill_md.read_text().splitlines()
    for line in lines[1:lines[1:].index("---") + 1]:
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip()
        in_meta = line.startswith("metadata:") or (in_meta and line.startswith(" "))
        if in_meta and line.strip().startswith("version:"):
            version = line.split(":", 1)[1].strip().strip("'\"")
    return name, version


def find_real_claude() -> str:
    shim_dir = str(RUNNER / "bin")
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if d.rstrip("/") == shim_dir:
            continue
        cand = Path(d) / "claude"
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    sys.exit("claude CLI not found on PATH")


def model_env() -> dict:
    """Environment for every subprocess that may call `claude`."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    env["REAL_CLAUDE"] = find_real_claude()
    env["PATH"] = f"{RUNNER / 'bin'}{os.pathsep}{env.get('PATH', '')}"
    env["EVAL_CLAUDE_SETTINGS"] = json.dumps({"claudeMdExcludes": [
        str(REPO / "CLAUDE.md"), f"{REPO}/**/CLAUDE.md", str(Path.home() / ".claude" / "CLAUDE.md"),
    ]})
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def new_run_dir(model: str, version: str) -> Path:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base = RUNS / f"{date}_{model}_v{version}"
    path, n = base, 2
    while path.exists():
        path, n = Path(f"{base}_{n}"), n + 1
    return path


# ---------------------------------------------------------------- executor

def run_claude(prompt: str, model: str, cwd: Path, tools: list[str], timeout: int, env: dict) -> list[dict]:
    cmd = ["claude", "-p", prompt, "--model", model, "--output-format", "stream-json",
           "--verbose", "--allowedTools", *tools]
    proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                          timeout=timeout, stdin=subprocess.DEVNULL)
    events = []
    for line in proc.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    if proc.returncode != 0 and not any(e.get("type") == "result" for e in events):
        events.append({"type": "result", "is_error": True, "result": proc.stderr[-2000:]})
    return events


def summarize(events: list[dict]) -> dict:
    """Pull tool usage, tokens, timing and the final reply out of a stream-json run."""
    tool_calls, skills_invoked, init = {}, [], {}
    for e in events:
        if e.get("type") == "system" and e.get("subtype") == "init":
            init = {k: e.get(k) for k in ("model", "skills", "slash_commands", "tools")}
        if e.get("type") == "assistant":
            for block in e.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    tool_calls[block["name"]] = tool_calls.get(block["name"], 0) + 1
                    if block["name"] == "Skill":
                        skills_invoked.append(block.get("input", {}).get("skill", ""))
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    usage = result.get("usage", {}) or {}
    tokens = sum(usage.get(k, 0) or 0 for k in
                 ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return {
        "init": init,
        "tool_calls": tool_calls,
        "skills_invoked": skills_invoked,
        "final_response": result.get("result", "") or "",
        "is_error": bool(result.get("is_error")),
        "num_turns": result.get("num_turns"),
        "duration_ms": result.get("duration_ms", 0) or 0,
        "cost_usd": result.get("total_cost_usd"),
        "usage": usage,
        "total_tokens": tokens,
    }


def transcript_md(prompt: str, events: list[dict]) -> str:
    out = [f"# Transcript\n\n## Prompt\n\n{prompt}\n"]
    for e in events:
        if e.get("type") == "assistant":
            for b in e.get("message", {}).get("content", []):
                if b.get("type") == "text" and b.get("text", "").strip():
                    out.append(f"## Assistant\n\n{b['text']}\n")
                elif b.get("type") == "tool_use":
                    out.append(f"## Tool call: {b['name']}\n\n```json\n{json.dumps(b.get('input'), indent=2)[:4000]}\n```\n")
        elif e.get("type") == "user":
            content = e.get("message", {}).get("content", [])
            for b in content if isinstance(content, list) else []:
                if b.get("type") == "tool_result":
                    c = b.get("content")
                    text = c if isinstance(c, str) else json.dumps(c)
                    out.append(f"### Tool result\n\n```\n{text[:4000]}\n```\n")
        elif e.get("type") == "result":
            out.append(f"## Final result\n\n{e.get('result', '')}\n")
    return "\n".join(out)


def collect_outputs(work: Path, outputs: Path) -> list[str]:
    """Copy what the run produced (new or changed files, outside .claude/) into outputs/."""
    outputs.mkdir(parents=True, exist_ok=True)
    created = []
    for p in sorted(work.rglob("*")):
        rel = p.relative_to(work)
        if not p.is_file() or rel.parts[0] in (".claude", ".inputs"):
            continue
        pristine = work / ".inputs" / rel
        if pristine.is_file() and pristine.read_bytes() == p.read_bytes():
            continue
        dest = outputs / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        created.append(str(rel))
    return created


def prepare_work(run_dir: Path, subject: Path, case: dict, skill_snapshot: Path,
                 skill_name: str, config: str) -> Path:
    work = run_dir / "work"
    (work / ".inputs").mkdir(parents=True, exist_ok=True)
    for rel in case.get("files", []):
        src = subject / rel
        shutil.copy2(src, work / src.name)
        shutil.copy2(src, work / ".inputs" / src.name)  # pristine copy to detect edits
    if config == "with_skill":
        shutil.copytree(skill_snapshot, work / ".claude" / "skills" / skill_name)
    else:
        (work / ".claude").mkdir(exist_ok=True)  # keeps project root here, with no skill
    return work


# ---------------------------------------------------------------- grading

def deterministic(case: dict, outputs: Path, inputs: Path) -> dict[str, dict]:
    results = {}
    for chk in case.get("deterministic_checks", []):
        passed, evidence = checks.run_check(chk, outputs, inputs)
        results[chk["expectation"]] = {"text": chk["expectation"], "passed": passed,
                                       "evidence": f"[deterministic:{chk['type']}] {evidence}"}
    return results


def llm_grade(pending: list[str], decided: dict, rd: Path, model: str, timeout: int, env: dict) -> dict:
    """Grade the remaining expectations with skill-creator's agents/grader.md."""
    instructions = (SKILL_CREATOR / "agents" / "grader.md").read_text()
    out_path = rd / "grading_llm.json"
    prompt = (
        f"{instructions}\n\n---\n\n## Your inputs\n\n"
        f"- expectations: {json.dumps(pending, indent=2)}\n"
        f"- transcript_path: {rd / 'transcript.md'}\n"
        f"- outputs_dir: {rd / 'outputs'}\n"
        f"- input files given to the executor: {rd / 'work' / '.inputs'}\n\n"
        f"These expectations were already decided by deterministic checks; don't re-grade them, "
        f"but use them as context:\n{json.dumps(list(decided.values()), indent=2)}\n\n"
        f"Grade only the expectations listed under `expectations`. Write your JSON to {out_path} "
        f"(not the default grading.json path)."
    )
    events = run_claude(prompt, model, rd, GRADER_TOOLS, timeout, env)
    (rd / "grader_transcript.jsonl").write_text("\n".join(json.dumps(e) for e in events))
    if out_path.exists():
        try:
            return json.loads(out_path.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def merge_grading(case: dict, decided: dict, llm: dict, metrics: dict) -> dict:
    llm_by_text = {e.get("text"): e for e in llm.get("expectations", [])}
    expectations = []
    for text in case["expectations"]:
        if text in decided:
            expectations.append(decided[text])
        elif text in llm_by_text:
            e = llm_by_text[text]
            expectations.append({"text": text, "passed": bool(e.get("passed")),
                                 "evidence": f"[llm-grader] {e.get('evidence', '')}"})
        else:
            expectations.append({"text": text, "passed": False,
                                 "evidence": "[llm-grader] not graded (no grader result)"})
    n = sum(e["passed"] for e in expectations)
    grading = {
        "expectations": expectations,
        "summary": {"passed": n, "failed": len(expectations) - n, "total": len(expectations),
                    "pass_rate": round(n / len(expectations), 4) if expectations else 0.0},
        "execution_metrics": metrics,
    }
    for key in ("claims", "user_notes_summary", "eval_feedback"):
        if key in llm:
            grading[key] = llm[key]
    return grading


# ---------------------------------------------------------------- one run

def execute_one(job: dict, args, env: dict) -> str:
    case, config, k, rd = job["case"], job["config"], job["k"], job["dir"]
    work = prepare_work(rd, args.subject, case, job["skill_snapshot"], job["skill_name"], config)
    started = time.time()

    if args.offline:
        offline.write_fixture(case, config, work)
        summary = {"init": {}, "tool_calls": {}, "skills_invoked": [], "final_response": (work / "_reply.md").read_text(),
                   "is_error": False, "num_turns": 0, "duration_ms": 0, "cost_usd": 0, "usage": {}, "total_tokens": 0}
        (work / "_reply.md").unlink()
        events = []
    else:
        events = run_claude(case["prompt"], job["model"], work, EXECUTOR_TOOLS, args.timeout, env)
        summary = summarize(events)

    (rd / "transcript.jsonl").write_text("\n".join(json.dumps(e) for e in events))
    (rd / "transcript.md").write_text(transcript_md(case["prompt"], events))
    outputs = rd / "outputs"
    created = collect_outputs(work, outputs)
    (outputs / "final_response.md").write_text(summary["final_response"])

    metrics = {
        "tool_calls": summary["tool_calls"],
        "total_tool_calls": sum(summary["tool_calls"].values()),
        "total_steps": summary["num_turns"] or 0,
        "files_created": created,
        "errors_encountered": int(summary["is_error"]),
        "output_chars": sum((outputs / f).stat().st_size for f in created),
        "transcript_chars": len((rd / "transcript.md").read_text()),
        "skills_invoked": summary["skills_invoked"],
        "skill_used": any(job["skill_name"] in s for s in summary["skills_invoked"]),
    }
    (outputs / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (rd / "timing.json").write_text(json.dumps({
        "total_tokens": summary["total_tokens"],
        "duration_ms": summary["duration_ms"],
        "total_duration_seconds": round(summary["duration_ms"] / 1000 or (time.time() - started), 1),
        "cost_usd": summary["cost_usd"],
        "usage": summary["usage"],
    }, indent=2))
    (rd / "run_info.json").write_text(json.dumps({"model": job["model"], "configuration": config,
                                                  "run_number": k, "init": summary["init"]}, indent=2))

    # Deterministic checks first; only what they can't decide goes to the LLM grader.
    decided = deterministic(case, outputs, work / ".inputs")
    pending = [t for t in case["expectations"] if t not in decided]
    llm = {}
    if pending and not args.offline:
        llm = llm_grade(pending, decided, rd, args.grader_model, args.timeout, env)
    grading = merge_grading(case, decided, llm, metrics)
    (rd / "grading.json").write_text(json.dumps(grading, indent=2))
    s = grading["summary"]
    return f"{case['name']:<22} {config:<14} run-{k}  {s['passed']}/{s['total']}"


# ---------------------------------------------------------------- triggers & aggregate

def run_triggers(run_dir: Path, evals: dict, skill_snapshot: Path, model: str, args, env: dict) -> dict:
    tdir = run_dir / "triggers"
    (tdir / ".claude").mkdir(parents=True, exist_ok=True)  # project root for run_eval's temp command files
    eval_set = tdir / "trigger_eval_set.json"
    eval_set.write_text(json.dumps(evals["trigger_queries"], indent=2))
    cmd = [sys.executable, "-m", "scripts.run_eval", "--eval-set", str(eval_set),
           "--skill-path", str(skill_snapshot), "--model", model,
           "--runs-per-query", str(args.trigger_runs), "--num-workers", str(args.workers * 2),
           "--timeout", str(args.trigger_timeout), "--verbose"]
    tenv = dict(env, PYTHONPATH=str(SKILL_CREATOR))
    proc = subprocess.run(cmd, cwd=tdir, env=tenv, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    (tdir / "run_eval.log").write_text(proc.stderr)
    try:
        results = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"error": f"run_eval failed (exit {proc.returncode}); see triggers/run_eval.log"}
    (tdir / "trigger_results.json").write_text(json.dumps(results, indent=2))
    return results


def aggregate(run_dir: Path, skill_name: str, skill_snapshot: Path, model: str,
              version: str, cases: list[dict], triggers: dict | None, args, env: dict) -> Path:
    subprocess.run([sys.executable, "-m", "scripts.aggregate_benchmark", str(run_dir),
                    "--skill-name", skill_name, "--skill-path", str(skill_snapshot)],
                   cwd=SKILL_CREATOR, env=env, check=True, capture_output=True)
    path = run_dir / "benchmark.json"
    bench = json.loads(path.read_text())
    names = {c["id"]: c["name"] for c in cases}
    for r in bench["runs"]:
        r["eval_name"] = names.get(r["eval_id"], str(r["eval_id"]))
    bench["metadata"].update({
        "executor_model": model,
        "analyzer_model": None if args.offline else args.grader_model,
        "grader_model": None if args.offline else args.grader_model,
        "skill_version": version,
        "runs_per_configuration": args.runs,
        "offline": args.offline,
    })
    if triggers is not None:
        res = triggers.get("results", [])
        bench["trigger_eval"] = {
            "runs_per_query": args.trigger_runs,
            "summary": triggers.get("summary", {}),
            "should_trigger_rate": _mean([r["trigger_rate"] for r in res if r["should_trigger"]]),
            "should_not_trigger_rate": _mean([r["trigger_rate"] for r in res if not r["should_trigger"]]),
            "results": res,
            "error": triggers.get("error"),
        }
    path.write_text(json.dumps(bench, indent=2))
    sys.path.insert(0, str(SKILL_CREATOR))
    from scripts.aggregate_benchmark import generate_markdown  # skill-creator's own formatter
    (run_dir / "benchmark.md").write_text(generate_markdown(bench))
    return path


def regrade(run_dir: Path, args, env: dict) -> None:
    """Re-run deterministic checks on an existing run and re-aggregate. No model calls:
    LLM-graded verdicts are kept from the existing grading.json."""
    cfg = json.loads((run_dir / "run_config.json").read_text())
    evals = json.loads((args.subject / "evals.json").read_text())
    cases = {c["id"]: c for c in evals["evals"]}
    for meta in sorted(run_dir.glob("eval-*/eval_metadata.json")):
        case = cases[json.loads(meta.read_text())["eval_id"]]
        for rd in sorted(meta.parent.glob("*/run-*")):
            old = json.loads((rd / "grading.json").read_text())
            llm = {"expectations": [e for e in old["expectations"] if e["evidence"].startswith("[llm-grader]")]}
            for e in llm["expectations"]:
                e["evidence"] = e["evidence"].removeprefix("[llm-grader] ")
            for key in ("claims", "user_notes_summary", "eval_feedback"):
                if key in old:
                    llm[key] = old[key]
            decided = deterministic(case, rd / "outputs", rd / "work" / ".inputs")
            grading = merge_grading(case, decided, llm, old.get("execution_metrics", {}))
            (rd / "grading.json").write_text(json.dumps(grading, indent=2))
            s = grading["summary"]
            print(f"  {case['name']:<22} {rd.parent.name:<14} {rd.name}  {s['passed']}/{s['total']}")
    trig = run_dir / "triggers" / "trigger_results.json"
    triggers = json.loads(trig.read_text()) if trig.exists() else None
    args.runs, args.trigger_runs = cfg["runs"], cfg.get("trigger_runs") or args.trigger_runs
    args.grader_model, args.offline = cfg["grader_model"], cfg.get("offline", False)
    bench = aggregate(run_dir, cfg["skill"], run_dir / "skill-snapshot", cfg["model"], cfg["skill_version"],
                      list(cases.values()), triggers, args, env)
    print(f"  benchmark: {bench.relative_to(REPO)}")


def _mean(xs):
    return round(sum(xs) / len(xs), 4) if xs else None


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subject", required=True, type=Path, help="subjects/<skill> folder with evals.json")
    ap.add_argument("--models", nargs="+", help="model IDs to test")
    ap.add_argument("--regrade", type=Path, help="re-run deterministic checks on this run folder; no model calls")
    ap.add_argument("--runs", type=int, default=3, help="repeats per case and configuration")
    ap.add_argument("--configs", nargs="+", default=list(CONFIGS), choices=CONFIGS)
    ap.add_argument("--cases", nargs="+", help="only these eval names or ids")
    ap.add_argument("--grader-model", default=DEFAULT_GRADER_MODEL)
    ap.add_argument("--trigger-runs", type=int, default=3, help="runs per trigger query")
    ap.add_argument("--skip-triggers", action="store_true")
    ap.add_argument("--workers", type=int, default=3, help="parallel executor runs")
    ap.add_argument("--timeout", type=int, default=900, help="seconds per executor/grader call")
    ap.add_argument("--trigger-timeout", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true", help="print the plan and call counts only")
    ap.add_argument("--offline", action="store_true", help="canned outputs, no model calls")
    args = ap.parse_args()

    args.subject = args.subject.resolve()
    if args.regrade:
        regrade(args.regrade.resolve(), args, {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        return
    if not args.models:
        ap.error("--models is required unless --regrade is given")
    evals = json.loads((args.subject / "evals.json").read_text())
    skill_dir = args.subject / evals.get("skill_path", "skill")
    skill_name, version = parse_frontmatter(skill_dir / "SKILL.md")
    cases = [c for c in evals["evals"]
             if not args.cases or c["name"] in args.cases or str(c["id"]) in args.cases]
    if args.offline:
        args.skip_triggers = True

    per_model_exec = len(cases) * len(args.configs) * args.runs
    per_model_grade = sum(len(args.configs) * args.runs for c in cases
                          if set(c["expectations"]) - {d["expectation"] for d in c.get("deterministic_checks", [])})
    per_model_trig = 0 if args.skip_triggers else len(evals.get("trigger_queries", [])) * args.trigger_runs
    per_model = per_model_exec + per_model_grade + per_model_trig

    print(f"Skill: {skill_name} v{version}   cases: {[c['name'] for c in cases]}")
    print(f"Configs: {args.configs}   runs: {args.runs}   grader: {args.grader_model}")
    for m in args.models:
        print(f"  {m}: {per_model_exec} executor + {per_model_grade} grader ({args.grader_model}) "
              f"+ {per_model_trig} trigger = {per_model} claude -p calls -> runs/<date>_{m}_v{version}/")
    print(f"Total: {per_model * len(args.models)} claude -p calls"
          + ("  (offline: none will be made)" if args.offline else ""))
    if args.dry_run:
        return

    env = model_env()
    for model in args.models:
        run_dir = (RUNS / "_offline" / f"{model}_v{version}") if args.offline else new_run_dir(model, version)
        if args.offline and run_dir.exists():
            shutil.rmtree(run_dir)
        run_dir.mkdir(parents=True)
        snapshot = run_dir / "skill-snapshot"
        shutil.copytree(skill_dir, snapshot, ignore=shutil.ignore_patterns("__pycache__"))
        (run_dir / "run_config.json").write_text(json.dumps({
            "model": model, "grader_model": args.grader_model, "skill": skill_name, "skill_version": version,
            "configs": args.configs, "runs": args.runs, "cases": [c["name"] for c in cases],
            "trigger_runs": 0 if args.skip_triggers else args.trigger_runs, "offline": args.offline,
            "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }, indent=2))
        print(f"\n== {model} -> {run_dir.relative_to(REPO)}")

        jobs = []
        for c in cases:
            edir = run_dir / f"eval-{c['id']}-{c['name']}"
            edir.mkdir()
            (edir / "eval_metadata.json").write_text(json.dumps({
                "eval_id": c["id"], "eval_name": c["name"], "prompt": c["prompt"],
                "assertions": c["expectations"]}, indent=2))
            for config in args.configs:
                for k in range(1, args.runs + 1):
                    rd = edir / config / f"run-{k}"
                    rd.mkdir(parents=True)
                    jobs.append({"case": c, "config": config, "k": k, "dir": rd, "model": model,
                                 "skill_snapshot": snapshot, "skill_name": skill_name})
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(execute_one, j, args, env) for j in jobs]
            for f in as_completed(futures):
                try:
                    print("  " + f.result())
                except Exception as e:  # keep going; the missing grading.json shows up in the benchmark
                    print(f"  run failed: {e!r}")

        triggers = None
        if not args.skip_triggers:
            print("  trigger queries...")
            triggers = run_triggers(run_dir, evals, snapshot, model, args, env)
        bench = aggregate(run_dir, skill_name, snapshot, model, version, cases, triggers, args, env)
        print(f"  benchmark: {bench.relative_to(REPO)}")


if __name__ == "__main__":
    main()
