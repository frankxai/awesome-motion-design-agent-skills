# Motion audit benchmark

Eight small HTML pages with known motion problems, an answer key, and a scorer. It measures whether an agent finds the problems, and whether [`web-motion-auditor`](../../skills/web-motion-auditor/SKILL.md) helps it find more of them than the same agent without the skill.

| | |
| --- | --- |
| Fixtures | 8 pages: 7 with problems, 1 clean control (which one is not disclosed to the agent) |
| Required defects | 27, across reduced motion, performance, interruption, cleanup, touch and keyboard |
| Optional defects | 7, real but minor; reporting them neither helps recall nor costs precision |
| Scoring | Same fixture, accepted category, line within 3 of an anchor (5 for two wider defects); best-fit matching, so report order never changes the score |

**Status:** one baseline-versus-skill run so far (2026-11-20, three runs per arm, fixtures 01 to 06 only), tracked in [#40](https://github.com/frankxai/awesome-motion-design-agent-skills/issues/40). Both arms found 95 to 100% of the required defects on those six pages, so they cannot separate a skill from no skill. Fixtures 07 and 08 were added afterwards to raise the ceiling: their problems sit behind code that looks handled at a glance (a reduced-motion query that misses transitions, a throttled passive scroll handler next to a listener that is never removed). No agent has been scored on them yet.

To compare with that first run, score only the pages it saw: `--fixtures 01,02,03,04,05,06`.

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

The scorer lists three kinds of extra finding apart. A **false positive** fits no defect and lowers precision. A **duplicate** fits a defect another finding already claimed (for example, the same hover-only link reported once as a touch problem and once as a keyboard problem); it is counted but does not lower precision. A finding on an **optional** defect neither helps nor hurts. Two distinct problems reported as one finding earn credit for one, because the prompt asks for each problem separately.

## What it does not measure

Static review only. Frame rate, real interruption behavior and screen-reader output need a browser and device run, which this benchmark does not perform. Whether the agent's proposed fixes work is also not scored yet.

## Changing the fixtures

Each defect in `answers/expected.json` points at a unique line through `anchor`. `python3 -m unittest tests/test_motion_audit_score.py` fails if an anchor stops matching exactly one line, if a fixture is missing from the key, or if a fixture name or body gives the answer away.
