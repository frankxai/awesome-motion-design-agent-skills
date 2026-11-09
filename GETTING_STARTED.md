# Getting Started with Motion Design Agent Skills

This repository ships **five installable agent skills** under [`skills/`](./skills) and **read-only reference playbooks and rubrics** under [`rubrics/`](./rubrics), [`playbooks/`](./playbooks), [`capabilities/`](./capabilities), and [`rankings/`](./rankings).

## 1. Discover the available skills

Use the [`vercel-labs/skills`](https://github.com/vercel-labs/skills) CLI to list the skills exposed by this repository:

```bash
npx --yes skills add frankxai/awesome-motion-design-agent-skills --list
```

This returns five first-party skills:

- `motion-director`
- `site-motion-excellence-director`
- `web-motion-auditor`
- `remotion-video-agent`
- `generative-media-director`

## 2. Read the skill before installing it

Open the matching `SKILL.md` first so you only install what your workflow needs:

- [`skills/motion-director/SKILL.md`](./skills/motion-director/SKILL.md)
- [`skills/site-motion-excellence-director/SKILL.md`](./skills/site-motion-excellence-director/SKILL.md)
- [`skills/web-motion-auditor/SKILL.md`](./skills/web-motion-auditor/SKILL.md)
- [`skills/remotion-video-agent/SKILL.md`](./skills/remotion-video-agent/SKILL.md)
- [`skills/generative-media-director/SKILL.md`](./skills/generative-media-director/SKILL.md)

## 3. Install for Claude Code or Codex (verified on a fresh checkout)

### Claude Code (project-local → `./.claude/skills/<skill>/SKILL.md`)

```bash
# Install all 5 skills into ./.claude/skills/
npx --yes skills add frankxai/awesome-motion-design-agent-skills -a claude-code -y

# Or install a single skill
npx --yes skills add frankxai/awesome-motion-design-agent-skills --skill motion-director -a claude-code -y
```

### Codex (project-local → `./.agents/skills/<skill>/SKILL.md`)

```bash
# Install all 5 skills into ./.agents/skills/
npx --yes skills add frankxai/awesome-motion-design-agent-skills -a codex -y

# Or install a single skill
npx --yes skills add frankxai/awesome-motion-design-agent-skills --skill web-motion-auditor -a codex -y
```

Other supported `-a` agent targets include `github-copilot`, `cursor`, `gemini-cli`, and `opencode`. Add `-g` (`--global`) when you want a user-wide install instead of a project-local install.

## 4. Verify what is installed

```bash
npx --yes skills list
ls -1 .claude/skills .agents/skills
```

## 5. If you only want the reference guides

- [`README.md`](./README.md)
- [`rubrics/motion-quality-rubric.md`](./rubrics/motion-quality-rubric.md)
- [`rubrics/site-motion-excellence-gate.md`](./rubrics/site-motion-excellence-gate.md)
- [`rankings/best-motion-design-stack.md`](./rankings/best-motion-design-stack.md)

## 6. Safety for third-party installs

For third-party skill packs, prefer official upstream repositories and scan them before installation with [`NVIDIA/SkillSpector`](https://github.com/NVIDIA/SkillSpector).
