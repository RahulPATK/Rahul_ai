# HANDOFF: skill-eval-lab

Everything decided in the planning conversation (claude.ai), so work can continue in Claude Code without re-pasting. Date: 2026-10-13.

## 1. Why this project exists

I (the user) want a small capstone project that fills a gap at forgd: an evaluation workstream for Claude skills and tasks. I searched forgd's Google Drive (only Drive; Slack, GitHub, Teams not searched) and found:

- No finished eval harness, no multi-model comparison, no trigger-accuracy tester, nothing reusable across customers.
- Closest existing things:
  - Claude Use-Case Playbook: defines a "pass test" (known input, expected output) and a "flag test" (input where Claude should stop and ask), to be rerun on a schedule and before switching models.
    https://docs.google.com/document/d/1ffOGK4cgeWovCK-M90y_NuU86hz1sY96S2ixyMmya6Y/edit
  - Acme demo kit, demo 4: shows /skill-creator running pass/flag tests on a "weekly metrics review" skill. There is an `evals` folder with `pass-test`, `flag-test`, `output` subfolders and an `eval-1-missing-region` folder (flag case: a region vanishes after a reorg, Claude should ask). It demos skill-creator; it is not a forgd-built harness.
    https://drive.google.com/file/d/1agxyLMIxMXcN0qgvi_26AEwo9rq-zKul/view
  - Ocado "Skill Quality Workstream (Op-1)" scoping doc (draft, 7 Oct 2026): PLANS a model-change run (5.1), outcome review (3.5), Otis-in-evals mock plugin (3.6), improvement loop PoC (4.2). Not built. Says evals "have not proven cost-effective" as a promotion gate elsewhere at Ocado.
    https://docs.google.com/document/d/1ud_xJ9FA0pwe0I9Noct_07meEId16_RdRVIKtj6yjxg/edit
  - Skills & Plugins Reference Pack has a "Troubleshooting and evals" section (only the table of contents was seen).
- I confirmed no prototype of this is underway.

## 2. What the ideal eval workstream answers

1. Does the skill fire? (trigger accuracy: should-fire and should-not-fire cases)
2. Is the output right? (pass test)
3. Does it stop when it should? (flag test)
4. What does it cost? (tokens, latency, run-to-run variance)

Layers: Cases -> Runner (with and without the skill, several models, repeats, mocked/replayed tools) -> Graders (deterministic first, LLM rubric second, rubric checked against ~20 human-labelled samples) -> Report (one-page diff vs last run/model) -> Loop (failures become new cases; checks retired when production evidence covers them) -> Ownership.

Design principles (from the Ocado doc):
- Gate test: only require a check if its result changes a decision, production can't measure it more cheaply, and it costs less than the failure it prevents.
- Build only the gap: start from Anthropic's tooling and plain scripts, not a new platform.
- With vs without the skill shows whether a skill still adds value after a model upgrade (retirement signal).

## 3. What skill-creator already does (REUSE, do not rebuild)

Read /mnt/skills/examples/skill-creator/SKILL.md (or wherever it is installed in Claude Code) and its agents/ and references/ folders. Known from SKILL.md:
- Writes test cases (evals.json) and runs each with and without the skill (baseline).
- agents/grader.md grades assertions against outputs; agents/comparator.md does blind A/B; agents/analyzer.md explains why one version beat another.
- benchmark.json with variance; eval-viewer/generate_review.py for human review (use `--static <path>` when no display).
- references/schemas.md defines JSON structures for evals.json, grading.json, etc.
- Trigger optimizer: `python -m scripts.run_loop --eval-set <trigger-eval.json> --skill-path <skill> --model <model-id> --max-iterations 5 --verbose`. Runs each query 3 times, 60/40 train/held-out split, proposes better descriptions, picks best by held-out score. Uses `claude -p`, so it only works in Claude Code.
- Trigger queries must be substantive; trivial one-step queries won't trigger skills regardless of description.
- It writes tests inside the skill's own folder and saves results next to it. So ALWAYS run it on a copy inside this project, never on a shared original.
- Not covered / limits: single skill, single model per run; no catalogue-level view; no cross-model regression diff; no over-time report; no tool mocking.

## 4. The gap this project fills

1. Cross-model runs: same cases and same skill across 2-3 models, with regressions/improvements diffed.
2. Catalogue-level view: many skills in one report, including trigger confusion between overlapping skills.
3. Over-time comparison: "what changed since last run or last model change" as one page.
4. Customer-agnostic packaging: a cases-file convention plus runner anyone can point at a skill folder.
5. Tool mocking: replayed tool answers so MCP-dependent skills can be tested (Ocado's Otis problem). Likely a later stage.

## 5. MVP scope

- Subject: a SYNTHETIC "weekly-metrics-review" skill modelled on the playbook example (metrics tables and focus areas ready Monday; boundary: never guesses a number, flags mismatches instead). Do not copy real Acme or customer files. Fabricated data only.
- Cases in subjects/weekly-metrics-review/evals.json:
  - 2 pass cases (e.g. clean week's data where every number must match its source)
  - 2 flag cases (e.g. a region vanishes after a reorg; a metric total doesn't reconcile) where the correct behaviour is to stop and ask
  - 6 trigger queries: 3 should-fire, 3 should-not-fire (substantive, realistic phrasing; include near-miss negatives)
- Runner: takes a skill folder + evals.json + a list of model IDs; runs cases per model with and without the skill; saves each run's benchmark.json under runs/<date>_<model>/.
- Demo output (LATER stage, not now): model x case table with pass, flag, trigger rate, tokens, latency, regressions highlighted.
- Stretch (LAST stage): a second deliberately overlapping skill to show trigger confusion.

## 6. Build order (stop and ask between stages)

1. Scaffold folders, synthetic skill, evals.json, runner skeleton. No model calls yet.
2. Review the plan and files with me.
3. Run ONE model end to end. Confirm benchmark.json lands in runs/<date>_<model>/. Inspect by hand: do pass cases pass, do flag cases stop, are trigger rates plausible?
4. Add a second model and the merged comparison page.
5. Overlapping-skill trigger test.

## 7. Constraints and risks

- Isolation: work only inside this project folder (a plain local folder; git init locally is optional and recommended for undo/diffs, no remote). Do not touch Drive or any forgd/Acme/Ocado folders.
- Environment: Claude Code. `claude -p` is required for trigger tests. Confirm which model IDs my account can call before designing the matrix. Verify current Claude Code install and CLI flags in the official docs rather than from memory.
- Grader trust: deterministic checks (numbers match source) before LLM-graded rubrics. Any LLM grader should later be checked against ~20 human-labelled samples.
- Cost: tell me models and approximate call counts before any run that calls models.
- Do not invent schema details; read skill-creator's references/schemas.md.

## 8. Open questions for me (ask me, don't assume)

- Which model IDs should be in the comparison matrix?
- Is skill-creator already installed and listed in this Claude Code setup?
- Should the final report be a static HTML file or something else?

## 9. First prompt to run in Claude Code

> Read HANDOFF.md and CLAUDE.md. Then read the skill-creator skill, including its agents/ and references/schemas.md. Propose a short plan for Stage 1 (scaffold only: synthetic weekly-metrics-review skill, evals.json with 2 pass cases, 2 flag cases and 6 trigger queries, and a runner skeleton that accepts a model list and writes benchmark.json under runs/). Do not call any models and do not build the report page. Show me the plan and wait for approval before writing files.
