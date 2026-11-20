# Motion audit benchmark: 2026-11-20 run

**Result: the skill made no measurable difference here.** The agent without the skill (baseline) already found 95–100% of the required defects. The differences between the two arms come from how the scorer matches findings to defects, not from what the agents noticed.

| | |
| --- | --- |
| Date | 2026-11-20 |
| Agent | Claude Code subagents (Agent tool, `general-purpose` type), one fresh subagent per run |
| Model | Same model and settings for all six runs: each subagent used the model of the session that started it. The model ID is left out of committed files on purpose, per the repository environment's policy. |
| Arms | `baseline` (3 runs), `skill` (3 runs) |
| Fixtures / key | `benchmarks/motion-audit/` at branch `agent/claude/motion-audit-bench`: 19 required defects, 3 optional, `06-faq.html` is the clean control |
| Scorer | `score.py` unchanged; `tests/test_motion_audit_score.py` passed before the runs |

## Method

1. The answer key (`answers/`) was moved out of the repository before any subagent ran, and put back only for scoring.
2. Each run got its own empty directory (`/root/runs/<arm>-<N>/`) holding only `fixtures/`, `prompt.md` and `findings.schema.json`.
3. **Baseline:** the prompt was the full text of `prompt.md`, plus: "Work only inside /root/runs/<arm>-<N>/. Do not read any file outside it. Reply with only the JSON object."
4. **Skill:** the same prompt, with the full text of `skills/web-motion-auditor/SKILL.md` and its one linked reference (`references/motion-quality-rubric.md`) placed before it, introduced as "You have this skill installed:".
5. No subagent was told its arm, that an answer key exists, or how many defects there are. All six ran at the same time.
6. Each reply's JSON was taken word for word from the subagent's final message and saved as `<arm>-<N>.json`. All six were valid JSON. The tool-call logs show that every subagent only read files in its own run directory.
7. Scored with `python3 benchmarks/motion-audit/score.py <arm>-*.json --json`. Output is in `score-baseline.json` and `score-skill.json`.

### Limitations

- **The skill was pasted into the prompt, not installed.** The README's procedure installs it with `npx skills add` into a fresh agent session. Here its text went straight into the subagent's prompt, so this run tests the skill's content, not how it is found and loaded.
- **The baseline may not be fully clean.** Subagents ran inside a Claude Code session that has other plugins and skills available, and possibly the repository's project instructions, which mention motion review. No subagent read anything outside its run directory, but some general context may have reached both arms equally.
- **3 runs per arm.** The differences below are one or two defects per run. They are not statistically significant, and none is claimed.
- **Static review only.** As the README says, no browser, frame-rate or device checks were made.

## Per-run results

| Run | Findings | Recall | Precision | False positives | Control false positives | Required defects missed |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| baseline-1 | 25 | 1.000 | 0.840 | 4 | 0 | none |
| baseline-2 | 24 | 0.947 | 0.833 | 4 | 0 | d04a |
| baseline-3 | 23 | 0.947 | 0.826 | 4 | 0 | d02b |
| skill-1 | 22 | 0.947 | 0.864 | 3 | 0 | d02b |
| skill-2 | 23 | 0.895 | 0.783 | 5 | 0 | d02b, d04a |
| skill-3 | 24 | 0.947 | 0.833 | 4 | 0 | d02b |

## Per-arm summary

| Arm | Mean recall | Recall range | Mean precision | Precision range | Control false positives |
| --- | ---: | --- | ---: | --- | ---: |
| baseline | 0.965 | 0.947–1.000 | 0.833 | 0.826–0.840 | 0 in all runs |
| skill | 0.930 | 0.895–0.947 | 0.827 | 0.783–0.864 | 0 in all runs |

## Most-missed required defects

| Defect | What it is | Baseline misses | Skill misses |
| --- | --- | ---: | ---: |
| d02b | Permanent `will-change` on 24 cards, including layout properties (`02-feature-cards.html` line 10) | 1 / 3 | 3 / 3 |
| d04a | `requestAnimationFrame` loop never cancelled on unmount (`04-stats-panel.html`, anchored at line 30) | 1 / 3 | 1 / 3 |

Every other required defect was found in all six runs.

**Both misses are mostly about how findings were matched, not what was noticed:**

- **d02b** is anchored to the same line as d02a (layout-property transition). Both are performance defects, so a run gets credit for both only if it reports two separate performance findings near line 10. All six replies mention the `will-change` problem in their text. Baseline-1 and baseline-2 reported it as its own finding (lines 10 and 11). The other runs folded it into the d02a finding, which counts once.
- **d04a**: baseline-2 and skill-2 reported the rAF cleanup at line 35, the outer `requestAnimationFrame(tick)` call. That is outside d04a's ±3-line window around line 30. The scorer matches greedily, so that finding was credited to d04b (observer, line 37), and the run's real d04b finding then counted as a false positive.

**False positives** follow the same pattern in every run. None landed on the control page.

- `05-carousel.html` line 10: the slide `transition` has no reduced-motion fallback. This was reported in all six runs. It is a real issue, but it is not in the key, not even as optional.
- `05-carousel.html` line 34: "the autoplay interval is not reset after manual navigation", reported as a second finding next to the autoplay/reduced-motion one. d05d accepts both categories but only one finding can claim it. Reported in all six runs.
- `02-feature-cards.html` line 13: the hover-only "Learn more" link, split into a touch finding and a keyboard finding. d02d is a single defect that accepts either category. Reported in all six runs.
- One-offs: missing focus return as a separate finding (baseline-1), non-passive `touchstart` (baseline-3), Escape as a separate finding (skill-3), and an unbounded counter labelled performance (skill-2).

## Reading

On this benchmark, the web-motion-auditor skill gave no measurable improvement over the same model without it. The baseline averaged 0.965 recall and 0.833 precision; the skill arm averaged 0.930 and 0.827. That gap is one defect per run, and nearly all of it comes from scorer granularity: two defects anchored to the same line, a ±3-line window around a multi-line loop, and greedy matching. None of it reflects defects the skill arm failed to notice. Both arms named the same problems in nearly the same words, kept the clean control page clean, and spent their false positives on the same real-but-unkeyed or split-out issues. The benchmark is close to its ceiling for this model. The skill is a general review workflow (probes, report format, rubric) rather than a list of detection rules, so a static source audit that this model already handles well gives it little room to help. With 3 runs per arm this is not evidence that the skill hurts either. To give a future comparison more power, harder fixtures would help, along with a key that marks the carousel transition as optional, merges or separates same-line defects deliberately, and a scorer that matches findings optimally instead of greedily. Installing the skill through the README's `npx` route, instead of pasting it into the prompt, would also test how it is loaded.
