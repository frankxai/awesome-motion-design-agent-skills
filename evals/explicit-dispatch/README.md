# Explicit slash-command dispatch in Claude Code

On 19 November 2026, Claude Code 2.1.328 expanded all five installed slash commands into their complete corresponding instruction bodies. The same plain prompt, with all five skills installed, carried zero complete bodies. Each of the six fresh CLI processes issued one Messages request to the loopback fixture, which returned the same canned text.

The measurement covers explicit dispatch up to the model request boundary. It does not measure natural-language skill selection, model execution of instructions, or output quality. No provider model generated these responses. The receipt retains the source revision, tool versions, body digests and matched skill names. It omits the full request, runtime context and headers.

Run manually from this repository with Python 3.12+, Git, the skills CLI and Claude Code in PATH:

```sh
python evals/explicit-dispatch/check.py --repo . --commit e7dc6e2e728c918ffcea5edb2d7c94e2a6f7785d --output /tmp/dispatch.json
```

Pass `--skills-cli` or `--claude` for alternative binary paths. An empty temporary home and repository isolate local configuration. The fixture binds only to loopback, receives the source tracked at the requested revision via the installed skill, and supplies an inert streaming response. Tool execution is disabled and the child receives no inherited provider credentials. [Recorded observations](claude-code.json)
