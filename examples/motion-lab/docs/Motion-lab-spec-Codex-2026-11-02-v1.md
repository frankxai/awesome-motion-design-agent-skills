# Motion lab surface specification

Author: Codex. Created 2 November 2026. Revision 1.
Review state: code-led candidate; build, captures, and independent review pending.
Scope: the example app only. The public README and product identity stay intact.

## Outcome and alternatives

The visitor tries a small motion behavior, understands why it moves, finds the
source, and edits a composition that produces an actual video. A static catalog
keeps discovery intact but cannot demonstrate that behavior. A cinematic showcase
could add atmosphere, but would leave the adoption and export questions unanswered.
The selected approach is an interactive example workbench in the existing world.
Frank's autonomous execution request delegates routine implementation choices;
audience and commercial hypotheses remain assumptions, not customer acceptance.

## Direction contract

THESIS: Give visitors inspectable motion behavior and editable output. The examples
lead; setup and source remain close to the work.

OWN-WORLD: Inherit the banner's graphite, off-white, and coral. A pale interface
canvas separates the first study from the dark page. Borders organize content;
glow, ambient particles, and autoplay have no job here.

STORY: Try a reversal, change the emphasis in a readable sequence, edit a video,
download its inputs, and render it with the included code.

FIRST VIEWPORT: A short headline and explanation occupy the left side. A full
interface study occupies the right. On a phone they stack, with the controls
remaining visible and at least 44 pixels high.

FORM: Operate, with gallery exploration. The existing world is preserved and the
three requested example jobs determine the structure. Code-led execution follows
the explicit autonomous brief; no image comp or human visual approval is claimed.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish
review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

## Motion and recovery

- Motion disclosure: 220 ms ease-out; keyboard actions and reduced motion resolve immediately. Repeated actions must reach the latest state.
- GSAP emphasis: 550 ms `power3.out`; preserve current progress on interruption and dispose the scoped owner on unmount. Every step remains readable.
- Remotion clip: 240 frames at 30 fps, 1920×1080. Frame-derived positions and opacity; no wall-clock animation. Reduced motion removes movement.
- Valid brief edits persist locally. Corrupt data remains intact until an explicit reset. Incomplete typing does not overwrite the last valid brief.
- Render input is validated before work starts. Export to a new candidate, inspect metadata and poster, then update the latest receipt. Keep previous exports and failed-run evidence.

## Acceptance

Require a production build, typecheck, meaningful input/metadata tests, keyboard
and pointer reversal, phone touch, reduced motion, saved-input recovery, JSON
download, real video/poster export, schema-valid sidecars, and visual inspection
of the exact revision. Source instructions and passing structural checks cannot
stand in for those observations. Physical-device testing remains distinct from
emulated touch. Deployment and any paid offer require the applicable release gate.
