#!/usr/bin/env python3
"""Score motion-audit findings against the answer key.

    python3 benchmarks/motion-audit/score.py run1.json [run2.json ...] [--json] [--fixtures 01,02]

A finding can match a defect when the fixture is the same, the category is one
the defect accepts, and the reported line is within the defect's window
(default 3 lines) of one of its anchors. Findings and defects are paired by
maximum matching, required defects first, so the order of a report never
changes its score. Each defect matches at most one finding.

A finding that could have matched a defect already claimed by another finding
is a duplicate: the same problem reported twice. Duplicates are counted apart
from false positives and left out of precision.
"""

import argparse
import json
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent


def load_key(here=HERE, fixtures=None):
    key = json.loads((here / "answers" / "expected.json").read_text(encoding="utf-8"))
    if fixtures:
        key["defects"] = [d for d in key["defects"] if any(d["fixture"].startswith(p) for p in fixtures)]
    for d in key["defects"]:
        lines = (here / "fixtures" / d["fixture"]).read_text(encoding="utf-8").split("\n")
        anchors = d["anchor"] if isinstance(d["anchor"], list) else [d["anchor"]]
        d["lines"] = []
        for anchor in anchors:
            hits = [i + 1 for i, line in enumerate(lines) if anchor in line]
            if len(hits) != 1:
                raise ValueError(f"{d['id']}: anchor {anchor!r} must match exactly one line in {d['fixture']}, matched {len(hits)}")
            d["lines"].append(hits[0])
        d["line"] = d["lines"][0]
    return key


def can_match(f, d):
    return (f.get("fixture") == d["fixture"] and f.get("category") in d["accept"]
            and isinstance(f.get("line"), int)
            and any(abs(f["line"] - line) <= d.get("window", 3) for line in d["lines"]))


def max_matching(findings, defects, taken):
    """Kuhn's augmenting paths over findings not yet in `taken` (finding index -> defect id)."""
    owner = {}
    # Closest anchor first, so when one finding fits two defects it is credited to the one it points at.
    edges = {i: [d["id"] for d in sorted(defects, key=lambda d: min(abs(f["line"] - x) for x in d["lines"]))
                 if can_match(f, d)]
             for i, f in enumerate(findings) if i not in taken and isinstance(f.get("line"), int)}

    def augment(i, seen):
        for did in edges[i]:
            if did in seen:
                continue
            seen.add(did)
            if did not in owner or augment(owner[did], seen):
                owner[did] = i
                return True
        return False

    for i in edges:
        augment(i, set())
    for did, i in owner.items():
        taken[i] = did


def score(findings, key):
    defects = key["defects"]
    required = [d for d in defects if d["level"] == "required"]
    taken = {}
    max_matching(findings, required, taken)
    max_matching(findings, [d for d in defects if d["level"] != "required"], taken)
    claimed = set(taken.values())
    duplicates = {i for i, f in enumerate(findings)
                  if i not in taken and any(d["id"] in claimed and can_match(f, d) for d in defects)}
    false_pos = [i for i in range(len(findings)) if i not in taken and i not in duplicates]
    required_ids = [d["id"] for d in required]
    control = {d["fixture"] for d in defects} - {d["fixture"] for d in required}
    judged = len(taken) + len(false_pos)
    return {
        "recall": round(sum(i in claimed for i in required_ids) / len(required_ids), 3) if required_ids else None,
        "precision": round(len(taken) / judged, 3) if judged else None,
        "found": sorted(i for i in required_ids if i in claimed),
        "missed": [i for i in required_ids if i not in claimed],
        "falsePositives": len(false_pos),
        "duplicates": len(duplicates),
        "controlFalsePositives": sum(1 for i in false_pos if findings[i].get("fixture") in control),
        "findings": len(findings),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="+")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fixtures", help="comma-separated fixture name prefixes to score, e.g. 01,02,03")
    args = parser.parse_args()
    key = load_key(fixtures=args.fixtures.split(",") if args.fixtures else None)
    results = {}
    for run in args.runs:
        data = json.loads(Path(run).read_text(encoding="utf-8"))
        results[run] = score(data.get("findings", []), key)
    recalls = [r["recall"] for r in results.values()]
    summary = {"runs": len(recalls), "recallMean": round(statistics.mean(recalls), 3),
               "recallMin": min(recalls), "recallMax": max(recalls)}
    if args.json:
        print(json.dumps({"summary": summary, "runs": results}, indent=2))
        return
    for run, r in results.items():
        print(f"{run}: recall {r['recall']}  precision {r['precision']}  false+ {r['falsePositives']}"
              f"  dup {r['duplicates']}  missed {','.join(r['missed']) or '-'}")
    print(f"mean recall {summary['recallMean']} over {summary['runs']} run(s), range {summary['recallMin']}-{summary['recallMax']}")


if __name__ == "__main__":
    sys.exit(main())
