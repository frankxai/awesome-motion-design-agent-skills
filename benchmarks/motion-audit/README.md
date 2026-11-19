# Motion audit benchmark

Six small HTML pages with known motion problems, an answer key, and a scorer. It measures whether an agent finds the problems, and whether [`web-motion-auditor`](../../skills/web-motion-auditor/SKILL.md) helps it find more of them than the same agent without the skill.

| | |
| --- | --- |
| Fixtures | 6 pages: 5 with problems, 1 clean control (which one is not disclosed to the agent) |
| Required defects | 19, across reduced motion, performance, interruption, cleanup, touch and keyboard |
| Optional defects | 3, real but minor; reporting them neither helps recall nor costs precision |
| Scoring | Same fixture, accepted category, line within 3 of the defect (5 for one wider defect) |

**Status: no agent has been scored yet.** The fixtures, key and scorer are tested offline in CI; the first baseline-versus-skill runs are tracked in [#40](https://github.com/frankxai/awesome-motion-design-agent-skills/issues/40).

## Run it

1. Copy `fixtures/`, `prompt.md` and `findings.schema.json` into an empty working directory. **Do not copy `answers/`.**
2. Baseline: run the agent in that directory with no motion skills installed and the text of `prompt.md` as the task. Save its JSON reply as `baseline-1.json`.
3. Skill: install only the auditor (`npx --yes skills add frankxai/awesome-motion-design-agent-skills --skill web-motion-auditor -a <agent> -y`), start a fresh session, give the same prompt, save `skill-1.json`.
4. Repeat each arm at least three times with the same model, effort setting and tool permissions.
5. Score:

```bash
python3 benchmarks/motion-audit/score.py baseline-*.json
python3 benchmarks/motion-audit/score.py skill-*.json
```

Report recall, precision, false positives on the control page, and the range across runs, together with the agent, model, version and date. A higher finding count is not a better result; precision falls when an agent pads its report.

## What it does not measure

Static review only. Frame rate, real interruption behavior and screen-reader output need a browser and device run, which this benchmark does not perform. Whether the agent's proposed fixes work is also not scored yet.

## Changing the fixtures

Each defect in `answers/expected.json` points at a unique line through `anchor`. `python3 -m unittest tests/test_motion_audit_score.py` fails if an anchor stops matching exactly one line, if a fixture is missing from the key, or if a fixture name or body gives the answer away.
