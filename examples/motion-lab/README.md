# Motion lab

Author: Codex. Created 2 November 2026. Revision 1.
Review state: implementation candidate. Check the exact revision's CI and review
artifacts before treating the gallery as a verified release.

Three examples for the existing [gallery issue](https://github.com/frankxai/awesome-motion-design-agent-skills/issues/2):

- [Motion disclosure](components/InterfaceStudy.tsx): keyboard, touch, and interrupted open/close behavior.
- [GSAP sequence](components/SequenceStudy.tsx): user-directed emphasis with readable static content.
- [Remotion composition](video/LaunchVideo.tsx): editable text, eight seconds, a checked MP4 and poster.

## Run

Use Node.js 24 and npm. From this folder:

```bash
npm ci
npm run dev
```

Open `http://127.0.0.1:3100`. Follow your environment's server and browser admission
rules. This app adds no account, hosted renderer, API key, or payment requirement.

## Make a video

Edit the brief in the app and download `motion-brief.json` into this folder. Install
FFmpeg, including `ffprobe`, then run:

```bash
npm run render -- motion-brief.json
```

For the included example:

```bash
npm run render
```

Remotion may download a compatible browser when one is not supplied. In CI the
renderer reuses the isolated Playwright browser. `output/latest.json` points to
the most recent checked export. Each export has its inputs, source hashes, actual
video metadata, poster, job record, and visual provenance sidecars. Visual review
is still required. Repeating an unchanged successful job can reuse its checked
video; a failed replacement keeps the previous output and latest receipt.

The browser provides editing and playback; MP4 encoding uses the included renderer.
There is no generated footage, speech, or external asset service. Runtime packages
have their own licenses; check [Remotion's current license](https://www.remotion.dev/license)
for your intended use.

## Verify

```bash
npm test
npm run build
npm run typecheck
npm run render
npx playwright install chromium
npm run test:e2e
python scripts/verify-provenance.py
```

The provenance check requires `jsonschema==4.26.0`. CI installs it and stores
desktop/phone captures, playback artifacts, export files, and reports for one day.
The manual **Skills Validate** dispatch accepts `verify_gallery=true`; the dedicated
motion-lab workflow also runs for ready PRs affecting this example. These jobs use
standard public-repository GitHub runners. No scheduled job or deployment is added.

The copied VIS schema and its MIT license live in [`schemas/`](schemas). Source:
`frankxai/visual-intelligence`, revision `9458fab2540eab49d26e42e13d481e00b4486960`,
schema SHA-256 `a198d2c0294c101e11747f92432cb5c9d80e1ff08d8a30fe59dec4352a1d435d`.
The public schema URL returned 404 during implementation, so validation uses this
pinned copy. Captures and exports remain unapproved until their review is recorded.

## Scope

This example supports the existing [Next.js demo-site issue](https://github.com/frankxai/awesome-motion-design-agent-skills/issues/3).
It does not establish a deployed site, completed skill benchmark, market advantage,
paid offer, or native harness activation. The current surface remains `noindex`
while its release is under review. The optional FrankX link goes to the existing
newsletter and carries campaign parameters; no opt-in or conversion is fabricated.
