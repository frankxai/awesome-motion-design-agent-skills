# Skill verification

Author: Codex. Created 2 November 2026. Revision 3.
Review state: package checks run locally; independent review and motion-output benchmarks pending.

These skills provide instructions. They do not include a browser, motion runtime,
renderer, provider account, or a guarantee that an agent follows every instruction.
An installed folder, a successful lint run, and a good rendered result establish
different things.

## Check the shipped payload

Run from the repository root with Python 3.10 or later:

```bash
python scripts/verify-skill-packages.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

The package check validates all five skill entrypoints, verifies four bundled
references against their canonical repo sources, creates each individual ZIP in
memory, extracts it into an isolated temporary folder, and checks its local links.
The temporary files are removed after the check. Nothing is installed into an
agent profile, and the check needs no network access or third-party packages.

The regression cases reject missing references, links outside the skill folder,
encoded traversal, machine-specific links, invalid skill names, and stale bundled
copies. Required reference files are checked even when instructions name them as
inline code instead of Markdown links. External documentation links remain the
existing Link Checker's job.
The check does not execute instructions, grade taste, or prove installer behavior
for every supported harness.

The site spec and rubrics remain canonical under `templates/` and `rubrics/`.
When changing them, copy the exact bytes to the corresponding `references/`
folders identified in `BUNDLED_REFERENCES` in the verifier. CI rejects drift.
Each skill can then be installed or uploaded alone without needing the repo root.

## Check the actual release ZIPs

After packaging the five individual archives and `all-skills.zip` into `dist/`, run:

```bash
python scripts/verify-skill-packages.py --archives dist
```

This compares the actual archive inventory, paths, and file bytes against the
current source. It rejects missing references, changed content, duplicate paths,
traversal, symlinks, and a missing archive. It reads ZIP members without extracting
their paths. Use one individual skill ZIP for a single-skill upload;
`all-skills.zip` contains the collection for distribution.

The release workflow checks source and regression cases before packaging, then
checks the actual ZIPs before creating its artifact. The artifact includes
`SHA256SUMS` and `release-provenance.json`, which bind all six archives and their
payload files to the source commit. A manual run prepares artifacts by default.
Publishing additionally requires `main` and either a main push or an explicit
manual `publish` input. Feature-branch runs cannot publish.

Publication runs separately with write permission and rechecks the archive hashes.
When main has advanced, it compares complete Git trees for the skills, bundled
canonical sources, release workflow, verifier, publication policy and regression
tests. A README-only advance can still publish the unchanged packaged inputs;
the provenance keeps the actual packaged commit. Changed release inputs supersede
the older package, and the matching push filter schedules a replacement run.
Incomplete trees or API failures block publication. Regression cases exercise
README-only commits, changes/removals, file modes and unavailable tree data, and
keep the push filter aligned with the comparison policy.
Runs are serialized per branch and are not canceled during an upload. The rolling
URL is mutable; retain its downloaded provenance and hashes when reproducing an install.

## Verify installation separately

Use an isolated project and the current [skills CLI documentation](https://github.com/vercel-labs/skills).
Record the CLI version, command, source commit, agent target, generated files, and
hashes. Confirm that the installed folder includes its references, and that the
harness actually discovers and reads the entrypoint. Do not infer activation from
a catalog listing. Reload the harness when its discovery mechanism requires it.

Do not bulk-update a live profile to test a release. Preserve local customizations,
inspect the selected skill's source and changes, and test the exact candidate in
an isolated project before updating a shared installation.

## Measure whether the instructions help

Use the same source project, task, tools, model settings, time budget, and allowed
dependencies for a baseline and a skill-assisted attempt. Record the actual model
identifier when exposed; mark it unknown otherwise. Run at least three paired
attempts per scenario, preserve failures, and have a reviewer who did not make the
artifact assess the exact revisions without seeing which condition produced them.

| Scenario | Required behavior | Evidence |
| --- | --- | --- |
| Frequent keyboard command | Immediate focus and input; no delayed entrance | Keyboard recording and focus observations |
| Save-state feedback | Clear pending/success/error states using the existing stack | Working example, touch and keyboard checks |
| Rapid open/close reversal | Latest requested state wins; no orphan overlay or lost focus | Interrupted-transition recording in both directions |
| Scroll explanation | Native reading and useful reduced-motion sequence | Desktop, phone, keyboard, and reduced-motion captures |
| Failed media request | Required content and controls remain available | Reproduced network failure and recovery |
| Remotion export | Deterministic frame timing; valid text, duration, audio, and output | Input props, render command, inspected frames and playback |
| Unavailable generator | Honest handoff; no invented generation or unauthorized paid fallback | Tool result and delivered handoff |
| Screenshot-only audit | Source findings separated from unobserved runtime claims | Report with pending frame-rate/input checks |

Use the repo's [motion rubric](../rubrics/motion-quality-rubric.md) and
[site gate](../rubrics/site-motion-excellence-gate.md) with evidence per category.
Also record time to usable output, repair time, successful exports, tool failures,
and measured cost where available. Missing observations stay missing; do not
replace them with a composite score.

For library-specific implementation, compare the same task using the relevant
official [GSAP skills](https://github.com/greensock/gsap-skills) or
[Remotion skills](https://github.com/remotion-dev/skills). This pack's hypothesis
is that cross-stack direction and evidence improve the result. That advantage
needs measured output before it becomes a public claim.

## Documentation sources

- [Agent Skills specification](https://agentskills.io/specification): portable folders and bundled references.
- [Motion performance](https://motion.dev/docs/performance): rendering costs and acceleration limits.
- [Motion reduced-motion configuration](https://motion.dev/docs/react-motion-config): opt-in user preference behavior.
- [GSAP documentation](https://gsap.com/docs/v3/): current runtime APIs and lifecycle guidance.
- [Remotion documentation](https://www.remotion.dev/docs/): frame-based rendering and export APIs.

Sources inspected on 2 November 2026. Recheck version-dependent advice before
implementation. The GitHub workflows validate structure and links; they do not
enforce an agent's judgment or establish product demand.
