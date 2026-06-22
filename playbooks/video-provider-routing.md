# Video Provider Routing Playbook

Date: 2026-06-22

## What Codex Can Manage Today

Codex can manage the complete preflight and finishing system:

- media strategy, shot lists, and creative briefs
- imagegen/GPT Image 2 style frames and poster frames
- provider routing and dry-run job specs
- Remotion compositions for exact typography, UI overlays, captions, and variants
- Playwright capture of real site/app motion
- ffmpeg GIF, MP4, WebM, poster, and compression exports
- QA checklists for crop, file size, readability, reduced motion, and provenance

Codex should only submit real third-party video jobs after credentials and access are explicitly available in the environment, user secret store, provider OAuth session, or Vercel project environment.

## Current Local Capability Reading

Local commands were found for Grok and Gemini:

- `grok.exe`
- `gr`
- `gemini.ps1`

No direct command was found for `xai`, `veo`, `runway`, `luma`, or `higgsfield`.

The checked environment did not expose these video provider credentials:

- `XAI_API_KEY`
- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`
- `OPENAI_API_KEY`
- `RUNWAYML_API_SECRET`
- `RUNWAY_API_KEY`
- `LUMA_API_KEY`
- `HIGGSFIELD_API_KEY`
- `HIGGSFIELD_KEY_ID`
- `HIGGSFIELD_KEY_SECRET`
- `FAL_KEY`
- `REPLICATE_API_TOKEN`
- `VERCEL_OIDC_TOKEN`

So the safe default is **dry-run routing**: create excellent prompts, job specs, and finishing plans; submit only when provider auth is confirmed.

## Recommended Provider Order

### 1. Vercel AI Gateway First For Grok/Veo

Use this when the output supports a Vercel site or web product. It keeps generation closer to the existing hosting and deployment stack.

Best for:

- Grok Imagine social loops
- Veo cinematic clips
- quick web-to-media experiments
- unified model access from a Next.js/Vercel app

### 2. Direct Provider APIs For Advanced Control

Use direct APIs when provider-specific features matter:

- OpenAI Sora: OpenAI-first video generation, image-to-video, editing, and management.
- xAI Grok Imagine: fast image/video/social generation and image-to-video.
- Google Veo: high-fidelity cinematic video, native audio, first/last-frame workflows.
- Luma: cinematic exploration and creative-agent motion workflows.
- Runway: existing video transformation and production editing.
- Higgsfield: creator/social/ad video variants.

### 3. Starlight Motion Designer MCP After Adapters

Do not make the MCP call raw vendor APIs first. Build a provider adapter layer first, then expose those adapters as tools:

- `select_media_provider`
- `create_media_job`
- `submit_media_job`
- `poll_media_job`
- `download_media_asset`
- `finish_with_remotion`
- `export_with_ffmpeg`
- `write_asset_provenance`

This keeps the MCP stable even when providers change endpoints, prices, or model names.

## Routing Rules

Use imagegen first when:

- the visual language is not locked
- a poster frame is needed
- a hero image or keyframe must be strong before motion
- exact UI text should be controlled outside the video model

Use Grok Imagine when:

- speed matters
- the asset is social-first
- image-to-video is enough
- audio-synced or stylized variants are desired

Use Veo when:

- the shot needs premium realism
- native audio matters
- first/last-frame control matters
- the asset is a brand hero or cinematic trailer beat

Use Sora when:

- the team wants OpenAI-first provenance
- the project needs Sora's video workflow
- the clip is high-end image-to-video or generated video with synced audio

Use Luma when:

- the brief is exploratory
- cinematic texture and alternative motion takes matter
- the team wants quick concept-to-motion options

Use Runway when:

- editing existing footage is the core task
- a production video workflow is more important than a raw generated clip

Use Higgsfield when:

- the deliverable is creator/social/ad format
- the project needs trend-aware commercial variants

Use Remotion when:

- exact text, layout, UI, captions, and brand lockups matter
- the deliverable needs repeatable variants
- the asset must be regenerated from data

Use Playwright when:

- the clip must prove real product motion
- the source is a Vercel preview, localhost, or live site

Use ffmpeg when:

- the asset is ready for export, compression, GIF conversion, poster extraction, or format variants

## Minimal Job Flow

1. Create `media-job.json` using `schemas/media-job.schema.json`.
2. Route with `configs/provider-routing.default.json`.
3. Generate or select a style frame.
4. Write a provider-specific video prompt.
5. Submit only if credentials and rights are confirmed.
6. Save raw output plus prompt/provenance.
7. Finish in Remotion if text, layout, overlays, or variants matter.
8. Export with ffmpeg.
9. QA final output in target crop and device context.

## Source Links

- OpenAI Sora video generation: https://developers.openai.com/api/docs/guides/video-generation
- xAI Imagine overview: https://docs.x.ai/developers/model-capabilities/imagine
- Google Veo in Gemini API: https://ai.google.dev/gemini-api/docs/video
- Vercel AI Gateway text-to-video: https://vercel.com/docs/ai-gateway/capabilities/video-generation/text-to-video
- Vercel AI Gateway image-to-video: https://vercel.com/docs/ai-gateway/capabilities/video-generation/image-to-video
- Luma API: https://docs.lumalabs.ai/docs/api
- Runway API: https://docs.dev.runwayml.com/
- Higgsfield JS SDK: https://github.com/higgsfield-ai/higgsfield-js
