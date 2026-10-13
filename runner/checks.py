"""Deterministic checks, run before any LLM-graded expectation.

Each check in evals.json names the expectation it decides plus a `type`:

  file_exists          {"path"}                    file is in outputs/
  file_absent          {"path"}                    file is not in outputs/
  text_mentions        {"paths", "terms"?, "numbers"?}
                       the existing files among `paths`, read together, contain
                       every term (case-insensitive) and every number
  section_mentions     {"path", "section", "terms"}
                       the markdown section whose heading starts with `section`
                       contains every term
  table_rows_match_csv {"path", "csv", "key"}
                       for every row of the input CSV, the markdown table rows whose
                       first cell equals the row's `key` value (across all tables)
                       contain each of the row's numeric values exactly
  total_row_matches    {"path", "csv", "column", "row_label"}
                       the table row labelled `row_label` contains every value in
                       `column` of the input CSV (metric, value per row)

Paths are relative to the run's outputs/ dir; `csv` is an input file name.
Each check returns (passed, evidence).
"""

import csv
import re
from pathlib import Path

NUMBER_RE = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)


def numbers_in(text: str) -> set[float]:
    out = set()
    for raw in NUMBER_RE.findall(text):
        try:
            out.add(float(raw.replace(",", "")))
        except ValueError:
            pass
    return out


def to_number(value: str) -> float | None:
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return None


def table_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and not re.fullmatch(r"\|[\s:\-|]+\|?", line):
            rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


def label(cell: str) -> str:
    return re.sub(r"[*_`]", "", cell).strip().lower()


def row_numbers(cells: list[str]) -> set[float]:
    # Percent cells are week-over-week changes, not source values.
    return numbers_in(" ".join(c for c in cells[1:] if "%" not in c))


def section(text: str, title: str) -> str | None:
    headings = list(HEADING_RE.finditer(text))
    for i, h in enumerate(headings):
        if h.group(1).strip().lower().startswith(title.lower()):
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            return text[h.end():end]
    return None


def fmt(x: float) -> str:
    return f"{x:,.0f}" if float(x).is_integer() else f"{x:,}"


def run_check(check: dict, outputs: Path, inputs: Path) -> tuple[bool, str]:
    kind = check["type"]

    def read(rel):
        p = outputs / rel
        return p.read_text(errors="replace") if p.is_file() else None

    if kind == "file_exists":
        ok = (outputs / check["path"]).is_file()
        return ok, f"{check['path']} {'found' if ok else 'not found'} in outputs"

    if kind == "file_absent":
        ok = not (outputs / check["path"]).exists()
        return ok, f"{check['path']} {'absent' if ok else 'was written'}"

    if kind == "text_mentions":
        found = [p for p in check["paths"] if read(p) is not None]
        if not found:
            return False, f"None of {check['paths']} exist in outputs"
        text = "\n".join(read(p) for p in found)
        missing = [t for t in check.get("terms", []) if t.lower() not in text.lower()]
        nums = numbers_in(text)
        missing += [fmt(n) for n in check.get("numbers", []) if float(n) not in nums]
        if missing:
            return False, f"Not mentioned in {found}: {missing}"
        return True, f"All of {check.get('terms', []) + [fmt(n) for n in check.get('numbers', [])]} found in {found}"

    review = read(check["path"])
    if review is None:
        return False, f"Cannot check: {check['path']} not in outputs"

    if kind == "section_mentions":
        body = section(review, check["section"])
        if body is None:
            return False, f"No section headed '{check['section']}'"
        missing = [t for t in check["terms"] if t.lower() not in body.lower()]
        return not missing, (f"Missing from '{check['section']}': {missing}" if missing
                             else f"'{check['section']}' mentions {check['terms']}")

    rows = table_rows(review)
    if not rows:
        return False, f"No markdown table in {check['path']}"
    # A label can appear in several tables (e.g. one table per metric): pool its numbers.
    by_label: dict[str, set[float]] = {}
    for r in rows:
        if r:
            by_label.setdefault(label(r[0]), set()).update(row_numbers(r))

    with open(inputs / check["csv"], newline="") as f:
        source = list(csv.DictReader(f))

    if kind == "table_rows_match_csv":
        problems = []
        for src in source:
            key = src[check["key"]].strip()
            have = by_label.get(key.lower())
            if have is None:
                problems.append(f"no table row for {key}")
                continue
            for col, val in src.items():
                n = to_number(val) if col != check["key"] else None
                if n is not None and n not in have:
                    problems.append(f"{key} {col}: expected {fmt(n)}")
        if problems:
            return False, "; ".join(problems)
        return True, f"All {len(source)} rows of {check['csv']} match the table exactly"

    if kind == "total_row_matches":
        have = by_label.get(check["row_label"].lower())
        if have is None:
            return False, f"No table row labelled '{check['row_label']}'"
        want = {r["metric"]: to_number(r[check["column"]]) for r in source}
        wrong = [f"{m}: expected {fmt(v)}" for m, v in want.items() if v is not None and v not in have]
        if wrong:
            return False, f"{check['row_label']} row mismatches: {'; '.join(wrong)}"
        return True, f"{check['row_label']} row matches {check['csv']} ({check['column']})"

    return False, f"Unknown check type {kind!r}"
