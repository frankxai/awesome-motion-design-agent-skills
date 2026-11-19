#!/usr/bin/env python3
"""Score motion-audit findings against the answer key.

    python3 benchmarks/motion-audit/score.py run1.json [run2.json ...] [--json]

A finding matches a defect when the fixture is the same, the category is one
the defect accepts, and the reported line is within the defect's window
(default 3 lines) of its anchor. Each defect matches at most one finding.
"""

import argparse
import json
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent
CATEGORIES = {"reduced-motion", "performance", "interruption", "cleanup", "touch", "keyboard"}


def load_key(here=HERE):
    key = json.loads((here / "answers" / "expected.json").read_text(encoding="utf-8"))
    for d in key["defects"]:
        lines = (here / "fixtures" / d["fixture"]).read_text(encoding="utf-8").split("\n")
        hits = [i + 1 for i, line in enumerate(lines) if d["anchor"] in line]
        if len(hits) != 1:
            raise ValueError(f"{d['id']}: anchor must match exactly one line in {d['fixture']}, matched {len(hits)}")
        d["line"] = hits[0]
    return key


def score(findings, key):
    defects = key["defects"]
    claimed, matched_required, unmatched = set(), set(), []
    for f in findings:
        if f.get("category") not in CATEGORIES or not isinstance(f.get("line"), int):
            unmatched.append(f)
            continue
        hit = next((d for d in defects if d["id"] not in claimed and d["fixture"] == f.get("fixture")
                    and f["category"] in d["accept"] and abs(f["line"] - d["line"]) <= d.get("window", 3)), None)
        if hit is None:
            unmatched.append(f)
            continue
        claimed.add(hit["id"])
        if hit["level"] == "required":
            matched_required.add(hit["id"])
    required = [d["id"] for d in defects if d["level"] == "required"]
    control = {d["fixture"] for d in defects} - {d["fixture"] for d in defects if d["level"] == "required"}
    counted = len(findings)
    return {
        "recall": round(len(matched_required) / len(required), 3),
        "precision": round((counted - len(unmatched)) / counted, 3) if counted else None,
        "found": sorted(matched_required),
        "missed": [i for i in required if i not in matched_required],
        "falsePositives": len(unmatched),
        "controlFalsePositives": sum(1 for f in unmatched if f.get("fixture") in control),
        "findings": counted,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    key = load_key()
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
        print(f"{run}: recall {r['recall']}  precision {r['precision']}  false+ {r['falsePositives']}  missed {','.join(r['missed']) or '-'}")
    print(f"mean recall {summary['recallMean']} over {summary['runs']} run(s), range {summary['recallMin']}-{summary['recallMax']}")


if __name__ == "__main__":
    sys.exit(main())
