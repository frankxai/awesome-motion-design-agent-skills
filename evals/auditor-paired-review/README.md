# Interrupted preview review, paired pilot

On 19 November 2026 six independent Work sessions reviewed the same [source fragment](case.txt). Each session had one tool read and a 230-word answer budget. The control read an empty guide. The treatment read the complete `web-motion-auditor/SKILL.md` from revision `e7dc6e2e728c918ffcea5edb2d7c94e2a6f7785d`, immediately followed by the same case. The six fresh sessions inherited the same model configuration. An immutable provider model ID, seeds, token counts, latency and price were unavailable. No browser execution or image tool was allowed during these six source reviews.

| Pair | Baseline | Skill supplied |
| --- | --- | --- |
| 1 | amber | flint |
| 2 | ash | opal |
| 3 | jade | elm |

A separate reviewer received the case and six anonymous [responses](responses/) without the condition key. The [assessment](assessment.json) records a judgment per response and dimension. All six found the stale callback, exit-focus defect and reduced-motion defect and supplied checks for all three. All six correctly qualified the checks as unexecuted. Two of three treatment responses identified loss of access without JavaScript. Zero of three control responses identified it. The fragment did not specify a dialog, so one suggestion to handle Escape was optional.

This is one fixture, six text answers and a model judge. Assignment was interleaved, not randomized. The skill was supplied directly. Natural triggering, real repairs and user preference require separate trials. The dimensions were scored after collection, so treat the extra failure mode as a hypothesis for an unseen fixture.

To replay, use fresh sessions with the same model, task, tool count and answer cap. Read the entrypoint from the pinned commit for the treatment and a zero-byte file for the control. Then supply the case verbatim. Keep raw answers before anonymization and obtain the review before joining the condition key. The separate [drawer browser probe](../drawer-probe/README.md) exercises a different source fixture.
