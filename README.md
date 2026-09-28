# Awesome Motion Design Agent Skills

> Installable agent skills and curated references for product UI motion, cinematic web interaction, interactive vector/3D assets, deterministic video, generative media, and motion QA.

This repo has **two different kinds of value**:

- **Installable skills** in [`/skills`](./skills) — agent instructions packaged as `SKILL.md` folders.
- **Read-only references** in [`/rubrics`](./rubrics), [`/playbooks`](./playbooks), [`/rankings`](./rankings), [`/templates`](./templates), and [`/mcp`](./mcp) — useful even if you never install anything.

If you only remember one thing: **install skills with the `skills` CLI; do not assume clicking a GitHub link installs anything.**

## Choose your workflow

| Job | Start with | Why this path | Read without installing |
| --- | --- | --- | --- |
| Product UI motion | [`motion-director`](./skills/motion-director/SKILL.md) | Choose between Motion, GSAP, Rive, Lottie, Remotion, or Three.js and define timing, easing, reduced motion, and QA. | [`rubrics/motion-quality-rubric.md`](./rubrics/motion-quality-rubric.md) |
| Cinematic / creative web interaction | [`site-motion-excellence-director`](./skills/site-motion-excellence-director/SKILL.md) | Plans premium site choreography, runtime choice, reduced motion, and proof requirements before implementation. | [`templates/site-motion/SITE_MOTION_SPEC.md`](./templates/site-motion/SITE_MOTION_SPEC.md) · [`rubrics/site-motion-excellence-gate.md`](./rubrics/site-motion-excellence-gate.md) |
| Interactive vector / 3D assets | [`motion-director`](./skills/motion-director/SKILL.md) | Best starting point when the asset could become Rive, Lottie, Three.js, GIF, or embedded UI motion. | [`rankings/best-motion-design-stack.md`](./rankings/best-motion-design-stack.md) |
| Deterministic video / Remotion | [`remotion-video-agent`](./skills/remotion-video-agent/SKILL.md) | Breaks work into scenes, frame ranges, React components, render defaults, and delivery QA. | [`playbooks/gif-video-pipeline.md`](./playbooks/gif-video-pipeline.md) |
| Generative media | [`generative-media-director`](./skills/generative-media-director/SKILL.md) | Routes still-image, image-to-video, finishing, captions, exports, and provenance across providers. | [`playbooks/image-video-gif-production-workflow.md`](./playbooks/image-video-gif-production-workflow.md) · [`playbooks/video-provider-routing.md`](./playbooks/video-provider-routing.md) |
| Review / capture / QA | [`web-motion-auditor`](./skills/web-motion-auditor/SKILL.md) | Reviews animated states, reduced motion, performance, screenshots/video capture, and concrete fixes. | [`rubrics/motion-quality-rubric.md`](./rubrics/motion-quality-rubric.md) · [`playbooks/site-motion-rollout.md`](./playbooks/site-motion-rollout.md) |

## Safely discover and install skills

Verified on **2026-09-28** against the official [`vercel-labs/skills`](https://github.com/vercel-labs/skills) CLI and this repository itself.

### 1) Discover the skills in this repo

```bash
npx skills add frankxai/awesome-motion-design-agent-skills --list
```

This currently lists **five** first-party skills from this repo.

### 2) Install project-local by default

```bash
npx skills add frankxai/awesome-motion-design-agent-skills --skill motion-director -a claude-code
```

- Project-local is the default scope.
- Add `-g` if you intentionally want a global install.
- Replace `claude-code` with another supported agent id such as `github-copilot`, `codex`, `cursor`, `gemini-cli`, or `opencode`.

### 3) Verify what is installed

```bash
npx skills list
npx skills list -g
```

### 4) Use upstream scanning before installing third-party skills

Before installing third-party skill packs, scan them with [`NVIDIA/SkillSpector`](https://github.com/NVIDIA/SkillSpector).

```bash
skillspector scan https://github.com/user/repo
```

## First-party installable skills

### Motion Director

**[View skill →](./skills/motion-director/SKILL.md)**

Use when you need a motion concept, stack choice, choreography, timing/easing tokens, reduced-motion behavior, and implementation notes for web UI, video, GIF, Rive, Lottie, GSAP, Motion, Remotion, or Three.js.

```bash
npx skills add frankxai/awesome-motion-design-agent-skills --skill motion-director -a claude-code
```

### Site Motion Excellence Director

**[View skill →](./skills/site-motion-excellence-director/SKILL.md)**

Use when a site or app needs serious motion direction: still-frame gate, beat sequencing, runtime rules, mobile choreography, reduced-motion planning, and implementation-ready specs.

```bash
npx skills add frankxai/awesome-motion-design-agent-skills --skill site-motion-excellence-director -a claude-code
```

### Web Motion Auditor

**[View skill →](./skills/web-motion-auditor/SKILL.md)**

Use when you want a review pass across load, hover, focus, click, route transitions, scroll, reduced motion, performance, screenshots/video capture, and concrete file-level fixes.

```bash
npx skills add frankxai/awesome-motion-design-agent-skills --skill web-motion-auditor -a claude-code
```

### Remotion Video Agent

**[View skill →](./skills/remotion-video-agent/SKILL.md)**

Use when the output is deterministic video or GIF built in React: scene planning, frame ranges, composition defaults, rendering, and delivery QA.

```bash
npx skills add frankxai/awesome-motion-design-agent-skills --skill remotion-video-agent -a claude-code
```

### Generative Media Director

**[View skill →](./skills/generative-media-director/SKILL.md)**

Use when you need provider routing and finishing for AI-generated images, image-to-video clips, social ads, cinematic brand assets, captions, variants, exports, and provenance.

```bash
npx skills add frankxai/awesome-motion-design-agent-skills --skill generative-media-director -a claude-code
```

## Read without installing

If you just want the playbooks, rubrics, rankings, or MCP notes, start here:

- [`GETTING_STARTED.md`](./GETTING_STARTED.md)
- [`rubrics/motion-quality-rubric.md`](./rubrics/motion-quality-rubric.md)
- [`rubrics/site-motion-excellence-gate.md`](./rubrics/site-motion-excellence-gate.md)
- [`playbooks/site-motion-rollout.md`](./playbooks/site-motion-rollout.md)
- [`rankings/best-motion-design-stack.md`](./rankings/best-motion-design-stack.md)
- [`mcp/motion-designer-mcp.md`](./mcp/motion-designer-mcp.md)

## Skills vs libraries vs MCP vs optional third-party references

### Installable third-party skill packs

| Project | Job | Why it matters | Agent fit | Risk / license note | Official link |
| --- | --- | --- | --- | --- | --- |
| Remotion Agent Skills | Remotion-specific docs and workflows | Official Remotion skill pack with targeted sub-skills like docs lookup, render, studio, captions, and upgrade guidance. | Best when an agent is editing a real Remotion codebase. | Review upstream repo/package licenses before pinning into your own workflow. | [github.com/remotion-dev/skills](https://github.com/remotion-dev/skills) |

### Libraries and runtimes

| Tool | Job | Why it matters | Agent fit | Risk / license note | Official link |
| --- | --- | --- | --- | --- | --- |
| Motion | Product UI motion and layout transitions | Official React/JS/Vue animation library; the upstream README also documents Motion's AI skill/MCP entry points. | Strong default for product UI motion and React choreography. | MIT for the library; some Motion+ extras are paid. | [github.com/motiondivision/motion](https://github.com/motiondivision/motion) |
| GSAP | High-control timelines, SVG, scroll, text, motion paths | Still the standard for authored timelines and ScrollTrigger-heavy creative web work. | Best for cinematic landing pages and complex choreography. | GreenSock standard no-charge license; review terms for your product/business context. | [github.com/greensock/GSAP](https://github.com/greensock/GSAP) |
| Remotion | Deterministic React-authored video | Gives agents exact frame timing, reusable compositions, and dependable MP4/GIF rendering. | Best for explainers, social cutdowns, previews, and video systems. | Review the upstream packages you adopt in your project before shipping. | [github.com/remotion-dev/remotion](https://github.com/remotion-dev/remotion) |

### MCP and install-safety tooling

| Tool | Job | Why it matters | Agent fit | Risk / license note | Official link |
| --- | --- | --- | --- | --- | --- |
| Motion AI / MCP | Current Motion docs context for agents | The Motion project documents `npx motion-ai` plus its MCP/doc surfaces for supported agents. | Useful when building Motion-based UI with an agent that needs fresh API context. | Motion library is MIT; confirm any optional paid services before team rollout. | [github.com/motiondivision/motion](https://github.com/motiondivision/motion) |
| NVIDIA SkillSpector | Scan skills before installation | Adds a practical install gate for third-party skills and publishes explicit scan guidance. | Useful for any agent workflow that installs skills from outside your own repo. | Apache-2.0. Scan results are advisory; still review source and licenses yourself. | [github.com/NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) |
| Agent Skills standard | Understand the `SKILL.md` format | Defines the open format used by this repo and many agent clients. | Useful when authoring or reviewing skills directly. | Apache-2.0 for code and CC-BY-4.0 for docs. | [github.com/agentskills/agentskills](https://github.com/agentskills/agentskills) |

## Maintenance notes

- Internal links in this README were checked against the current repo structure on **2026-09-28**.
- External links and install syntax cited here were spot-checked on **2026-09-28**; treat them as verified references, not a promise that every upstream project will remain unchanged.
- `skills-lock.json` is for pinned third-party installs, not these first-party repo-local skills.

## Contributing

Open a PR with a primary source URL, distinct value, current maintenance evidence, relevant risk/license notes, and any install or safety caveats.

## License

[CC0 1.0](LICENSE) — dedicated to the public domain.
