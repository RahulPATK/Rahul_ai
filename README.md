# skill-eval-lab

Compare how a Claude skill performs across models: does it fire when it should (trigger
accuracy), is its output right (pass cases), does it stop and ask when the data is wrong
(flag cases), and what it costs (tokens, time, variance). Built on Anthropic's
skill-creator, which is vendored unmodified in `vendor/skill-creator/`.

Context and decisions: [HANDOFF.md](HANDOFF.md). Working rules: [CLAUDE.md](CLAUDE.md).

## Requirements

- Python 3.10+ (standard library only)
- Claude Code CLI (`claude`) installed and logged in. Trigger tests use `claude -p`.

## 1. Test the pipeline without calling any models

```bash
# What would run, and how many model calls it would make
python3 -B runner/run.py --subject subjects/weekly-metrics-review \
  --models claude-opus-5-5 claude-sonnet-5-5 claude-haiku-5-5 --dry-run

# Whole pipeline with canned outputs (no model calls) -> runs/_offline/ (gitignored)
python3 -B runner/run.py --subject subjects/weekly-metrics-review \
  --models claude-sonnet-5-5 --runs 1 --offline
```

Offline, the skill-shaped fixture should pass every deterministic check, and the naive
"without skill" fixture should fail both flag cases. LLM-graded expectations show as
"not graded", because offline mode skips the grader.

## 2. Run for real

Before you run anything that calls models, check the call count with `--dry-run`.

```bash
# Smoke test: one case, with the skill, one repeat (2 calls)
python3 -B runner/run.py --subject subjects/weekly-metrics-review \
  --models claude-sonnet-5-5 --cases pass-clean-week --configs with_skill --runs 1 --skip-triggers

# Full run for one model (66 calls: 24 executor + 24 grader + 18 trigger)
python3 -B runner/run.py --subject subjects/weekly-metrics-review --models claude-sonnet-5-5
```

Useful flags:

| Flag | Default | Meaning |
|---|---|---|
| `--models` | (required) | One or more model IDs. Each gets its own run folder. |
| `--runs` | 3 | Repeats per case and configuration, for variance. |
| `--cases` | all | Only these eval names or ids. |
| `--configs` | both | `with_skill`, `without_skill`, or both (without = baseline). |
| `--grader-model` | `claude-opus-5-5` | Fixed grader, so grading doesn't vary with the model under test. |
| `--trigger-runs` | 3 | Runs per trigger query. |
| `--skip-triggers` | off | Skip the trigger-accuracy test. |
| `--workers` | 3 | Parallel executor runs. |
| `--regrade <run folder>` | | Re-run deterministic checks on an existing run and rebuild benchmark.json. No model calls; keeps the LLM grader's verdicts. |

## 3. Look at the results

Each run writes `runs/<date>_<model>_v<skill-version>/`:

```
benchmark.json / benchmark.md      skill-creator's aggregate, plus trigger_eval
eval-<id>-<name>/<config>/run-<k>/
  outputs/          what Claude produced (review.md or questions.md), final_response.md, metrics.json
  transcript.md     readable transcript of the run
  grading.json      every expectation with passed + evidence
  timing.json       tokens, seconds, cost
  run_info.json     model and the skills visible to the run
triggers/trigger_results.json      trigger rate per query
skill-snapshot/                    the exact skill version tested
```

To open skill-creator's review viewer for a run, as one static HTML file:

```bash
R=runs/<run-folder>
python3 -B vendor/skill-creator/eval-viewer/generate_review.py $R \
  --skill-name weekly-metrics-review --benchmark $R/benchmark.json --static $R/review.html
```

## How grading works

1. **Deterministic checks first** (`runner/checks.py`). The code checks: figures in the
   review table equal the source CSV exactly; the Total row equals the reported totals;
   for flag cases, no `review.md` was written and the questions name the problem.
2. **skill-creator's grader** (`vendor/skill-creator/agents/grader.md`, run with
   `--grader-model`) decides only the judgment calls, such as "no invented causes".
3. skill-creator's `aggregate_benchmark` builds `benchmark.json`.

## Containment

Every model call goes through `runner/bin/claude`. It adds `--no-session-persistence`
(no session logs under `~/.claude`) and `--setting-sources project,local` (your user
settings and hooks don't leak in), and it keeps this repo's `CLAUDE.md` files out of the
runs. Each case runs in its own folder under `runs/`.

## Adding another skill

Create `subjects/<skill>/` with `skill/SKILL.md` (put the version in `metadata.version`),
input files, and an `evals.json` following `subjects/weekly-metrics-review/evals.json`:
`evals[]` with `expectations` plus optional `deterministic_checks`, and `trigger_queries[]`.
