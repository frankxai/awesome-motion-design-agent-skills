# Recommended Installs

This is the install posture for FrankX/Arcanea/Starlight motion design work.

## Keep Enabled In Codex

- Figma plugin/connector
- Canva plugin/connector
- Vercel plugin/connector
- Browser automation
- GitHub CLI/connector
- Image generation

These are already visible or locally available in this environment.

## Add To Motion/Video Projects

```bash
npm i motion gsap
npm i -D @playwright/test
```

For Remotion projects:

```bash
npm create video@latest
npm i @remotion/lottie lottie-web @remotion/rive
```

For 3D or cinematic web scenes:

```bash
npm i three @react-three/fiber @react-three/drei
npm i @theatre/core @theatre/studio
```

For interactive vector animation:

```bash
npm i @rive-app/react-canvas
```

For Lottie in React UI:

```bash
npm i lottie-react
```

## Add Agent Skills

Official Remotion docs currently recommend:

```bash
npx skills add remotion-dev/skills
```

Run this in the agent environment where the video work will happen. Then verify the installed path before relying on it in production.

## Add MCP Carefully

Recommended:

- Figma MCP for design context and write-back.
- Canva MCP for asset/design creation and collateral.
- Remotion MCP for Remotion-specific docs/context.
- Vercel connector for deploy/preview/log workflows.

Security rule: install MCP servers from official vendors or audited source only. Review scopes, command execution behavior, and whether the tool can read secrets or write files.

## Local Machine Status

Checked on 2026-06-18:

- `git` is available.
- `gh` is available.
- `node` is available.
- `npm` is available.
- `ffmpeg` is available.

