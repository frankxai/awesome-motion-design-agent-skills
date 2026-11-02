# Motion lab product context

<!-- impeccable:product-schema 1 -->

Author: Codex. Created 2 November 2026. Revision 1.
Sources: repository issues 2 and 3, BUSINESS_CASE.md, and Frank's instruction to execute the repo improvements autonomously.
Review state: implementation candidate; output and release acceptance remain open.

## Platform

web

## Stack

Next.js, as specified in issue 3. Motion, GSAP, and Remotion demonstrate the three
examples requested in issue 2. Versions are pinned from primary package records
inspected on 2 November 2026. This is an example inside the existing repository.

## Users

Developers and creators evaluating the repository's motion workflows. The working
assumption is that they want to try a small example, inspect its source, and adapt
it in their own project. This audience is inferred from the repository purpose;
there is no completed buyer study.

## Product purpose

Provide three usable motion studies with editable source and a real, checked
video export. Keep the existing repository name, README discovery path, install
names, and catalog. No new brand, account, payment, or service is required.

## Capabilities and constraints

Interface reversal, a user-controlled sequence, editable video inputs, local
recovery, JSON download, deterministic rendering, and metadata/provenance checks
are implementation targets. Video encoding runs locally or in bounded CI, not
inside the browser. A failed replacement must preserve the previous usable export.

## Brand commitments

Preserve the current graphite, off-white, and coral identity visible in the repo's
banner. This adds a demonstration surface and does not replace the README artwork.
Use sentence case and factual descriptions; no invented rankings or customer proof.

## Evidence on hand

The base skills candidate has passing package CI and an isolated Codex CLI install.
Those checks do not prove this app's behavior, visual quality, or a paid product's
value. Independent review and actual output inspection remain release requirements.

## Accessibility and inclusion

Keyboard focus, touch access, reduced motion, readable static explanations,
interrupted transitions, saved-input failure, mobile layout, and media playback
need observed verification. No essential action depends on hover or autoplay.
