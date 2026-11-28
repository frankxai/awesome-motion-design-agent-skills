# Native skill discovery

Measured on 19 November 2026 from commit `e7dc6e2e728c918ffcea5edb2d7c94e2a6f7785d` with the skills CLI 1.9.0. Each run used a temporary project and empty home, a project-local CLI install and removal, and a fresh native process per observation. The matching skill counts were:

| Runtime | Before install | After install | After targeted removal | After isolated cleanup |
| --- | ---: | ---: | ---: | ---: |
| Claude Code 2.1.328 | 0 | 5 | 0 | 0 |
| Codex CLI 0.167.0-alpha.4 | 0 | 5 | 0 | 0 |
| OpenCode 1.19.6 | 0 | 5 | 5 | 0 |

Codex returned enabled repository entries and paths through `skills/list`. Claude Code returned slash-command names through SDK initialization. OpenCode's `debug skill --pure` reported the source location and complete instruction body. The JSON files contain hashes of the installed entrypoints. No user prompt or model turn was sent. These observations establish discovery for the recorded versions and project layout.

OpenCode's scoped removal left the shared `.agents/skills` copies discoverable. The probe records this failure and exits nonzero, even when the CLI returned success. It verifies cleanup by removing one skill name at a time without a target in its disposable single-target project. An unscoped removal in a shared working project can affect other runtimes.

Use Python 3.12+, Git and the indicated locally installed CLIs. This is an opt-in maintainer check.

```sh
python evals/native-discovery/check.py --repo . --commit e7dc6e2e728c918ffcea5edb2d7c94e2a6f7785d --target codex --skills-cli skills --runtime codex --output /tmp/codex-discovery.json
python evals/native-discovery/check.py --repo . --commit e7dc6e2e728c918ffcea5edb2d7c94e2a6f7785d --target claude-code --skills-cli skills --runtime claude --output /tmp/claude-discovery.json
python evals/native-discovery/check.py --repo . --commit e7dc6e2e728c918ffcea5edb2d7c94e2a6f7785d --target opencode --skills-cli skills --runtime opencode --output /tmp/opencode-discovery.json
```

Pass a candidate commit to retest its own payload. The probe only installs the tracked `skills/` tree from that revision. Activation, model behavior and produced work require separate evidence.
