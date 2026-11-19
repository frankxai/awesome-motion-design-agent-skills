#!/usr/bin/env python3
"""Check the trigger eval cases in evals/triggers/ are complete and consistent.

This validates the test cases themselves; it does not call a model. Each skill
needs its own file with at least six prompts that should fire it and six that
should not, and no prompt may be claimed as a positive by two skills.
"""

import json
from pathlib import Path
import sys

MIN_CASES = 6


def verify(root):
    errors = []
    skills = {p.name for p in (root / "skills").iterdir() if p.is_dir()}
    eval_dir = root / "evals" / "triggers"
    files = {p.stem: p for p in eval_dir.glob("*.json")} if eval_dir.exists() else {}
    for missing in sorted(skills - files.keys()):
        errors.append(f"{missing}: no evals/triggers/{missing}.json")
    for extra in sorted(files.keys() - skills):
        errors.append(f"evals/triggers/{extra}.json: no matching skill folder")

    positives = {}
    for name in sorted(skills & files.keys()):
        try:
            data = json.loads(files[name].read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"{name}: invalid JSON ({error})")
            continue
        if data.get("skill") != name:
            errors.append(f"{name}: 'skill' field must be '{name}'")
        for key in ("should_trigger", "should_not_trigger"):
            cases = data.get(key, [])
            if not isinstance(cases, list) or not all(isinstance(c, str) and c.strip() for c in cases):
                errors.append(f"{name}: '{key}' must be a list of non-empty strings")
                continue
            if len(cases) < MIN_CASES:
                errors.append(f"{name}: '{key}' needs at least {MIN_CASES} cases, has {len(cases)}")
            if len({c.strip().lower() for c in cases}) != len(cases):
                errors.append(f"{name}: duplicate case in '{key}'")
        overlap = {c.strip().lower() for c in data.get("should_trigger", [])} & {
            c.strip().lower() for c in data.get("should_not_trigger", [])}
        if overlap:
            errors.append(f"{name}: prompt is both positive and negative: {sorted(overlap)[0]}")
        for case in data.get("should_trigger", []):
            key = case.strip().lower()
            if key in positives:
                errors.append(f"{name}: positive also claimed by {positives[key]}: {case}")
            positives[key] = name
    return errors


if __name__ == "__main__":
    problems = verify(Path(__file__).resolve().parent.parent)
    print("\n".join(problems) or "OK: trigger eval cases")
    sys.exit(1 if problems else 0)
