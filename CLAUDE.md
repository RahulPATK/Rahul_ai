# skill-eval-lab

Goal: compare how a skill performs across Claude models (pass, flag, trigger accuracy, cost) and produce a repeatable, customer-agnostic report. Read HANDOFF.md for full context before doing anything.

## Rules
- Only read and write inside this project folder. Never touch anything outside it.
- Reuse skill-creator's grader, comparator, analyzer, benchmark.json and eval-viewer. Do not write custom grading or custom review HTML for single-skill results.
- Run deterministic checks before any LLM-graded check.
- Every run records model ID, date and skill version in its output folder name.
- Build in stages. Get one model working end to end first. Ask before adding each next stage (second model, report page, overlap test).
- Use only synthetic data. No customer data, no real forgd/Acme files.
- Before running anything that calls models, tell me which models and roughly how many calls, and wait for approval.
- If a fact about skill-creator, flags or schemas is uncertain, read the skill's own files (SKILL.md, references/schemas.md, agents/*.md) instead of guessing.

## Layout
```
subjects/<skill>/        skill folder + evals.json (pass, flag, trigger cases)
runner/                  loops models, calls skill-creator steps
runs/<date>_<model>/     raw benchmark.json per run
reports/                 merged comparison page (later stage)
vendor/skill-creator/    pinned copy of skill-creator (Apache-2.0); never edit, reuse as-is
HANDOFF.md               full context
```

## Commands
- Plan and call counts, no model calls: `python3 -B runner/run.py --subject subjects/weekly-metrics-review --models <id> [<id>...] --dry-run`
- Pipeline self-test with canned outputs, no model calls: add `--offline` (writes to runs/_offline/, gitignored)
- Real run (only after approval): drop `--dry-run`; `--runs`, `--cases`, `--configs`, `--skip-triggers` narrow it
- All model calls go through `runner/bin/claude`, which adds `--no-session-persistence`, `--setting-sources project,local` and excludes this repo's CLAUDE.md files from runs
