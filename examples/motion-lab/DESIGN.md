---
name: Motion lab
description: Open motion studies with editable source and checked exports
colors:
  accent: "#ef765c"
  ground: "#101211"
  surface: "#191d1a"
  ink: "#f6f3ed"
  secondary: "#bcc2b9"
  line: "#3d443d"
  paper: "#f0ece4"
  paper-ink: "#202820"
  paper-muted: "#545e52"
typography:
  display:
    fontFamily: '"Onest Variable", sans-serif'
    fontSize: "clamp(48px, 5.6vw, 80px)"
    fontWeight: 500
    lineHeight: 1.04
    letterSpacing: "-0.035em"
  headline:
    fontFamily: '"Onest Variable", sans-serif'
    fontSize: "clamp(28px, 3.1vw, 44px)"
    fontWeight: 500
    lineHeight: 1.1
    letterSpacing: "-0.03em"
rounded:
  control: "6px"
  sheet: "8px"
  canvas: "12px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.ground}"
    rounded: "{rounded.control}"
    padding: "14px 20px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "12px 14px"
---

# Motion lab design system

Author: Codex. Created: 2 November 2026. Revision: 1.
Review state: implementation record; independent design review pending.
Sources: `app/globals.css`, `components/`, `video/LaunchVideo.tsx`;
desktop and phone captures from Actions runs `41469458231` and `41472533513`.

## Overview

The examples use a dark workspace, a paper interface study, and coral controls.
The existing repository banner supplies the visual context. This record describes
the example app and does not replace the repository's identity.

The lead inspected desktop and phone captures. Those captures establish layout
evidence; they do not establish an independent quality verdict or customer demand.

## Colors

Coral marks actions, focus, and sequence emphasis. Off-white carries primary text;
the lighter green neutral carries supporting text. The pale paper study uses its
own dark text and muted green labels.

## Typography

Onest Variable is self-hosted through Fontsource. The display and section headings
use medium weight and balanced wrapping. Body and form text remain sentence case.
Phone input text is at least 16px. Code uses the platform monospace stack.

The portable video composition currently uses Arial/Helvetica independently of
the app font. This is an implementation limitation, not a new display-font rule.

## Layout

The shell is capped at 1280px. The desktop hero pairs the title with the interface
study. At 700px the hero and video editor become single columns. The intermediate
layout changes at 1000px. Examples stay in document flow and preserve source links.

## Elevation & Depth

Most separation comes from surface tone and fine rules. Only the paper sheet uses
a diffuse offset shadow. The sidecar records its exact value.

## Shapes

Controls, sheets, and example canvases use the rounded values in the frontmatter.
The sequence marker is circular. The small brand mark is a rounded square.

## Components

The disclosure reveals details in 220ms; keyboard input and reduced motion settle
immediately. Reversal follows the latest action. The sequence uses a 550ms move,
with immediate keyboard and reduced-motion selection. All steps stay readable.

Controls have visible focus outlines and touch targets. Video controls load on
request. A failed preview preserves the still frame and edited brief. Invalid
typing preserves the last valid saved brief; corrupt saved data requires an
explicit reset. The still frame scales through an SVG viewBox without JavaScript.

## Do's and Don'ts

- Do preserve readable content before motion begins.
- Do keep source links beside each example.
- Do preserve focus, touch, interruption, and reduced-motion behavior when editing.
- Don't treat a screenshot or a source scan as an independent release approval.
- Don't extend the video font exception into the app's visual identity.
