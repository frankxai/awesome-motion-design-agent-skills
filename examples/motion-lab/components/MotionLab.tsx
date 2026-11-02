"use client";

import { MotionConfig } from "motion/react";
import { InterfaceStudy } from "./InterfaceStudy";
import { SequenceStudy } from "./SequenceStudy";
import { VideoStudy } from "./VideoStudy";
import { SOURCE_ROOT } from "../lib/source";

export function MotionLab() {
  return <MotionConfig reducedMotion="user">
    <a className="skip-link" href="#interface">Skip to the examples</a>
    <header className="site-header shell">
      <a className="brand" href={SOURCE_ROOT}><span className="brand-mark" aria-hidden="true" />Motion design agent skills</a>
      <nav aria-label="Examples">
        <a href="#interface">Interface</a><a href="#sequence">Sequence</a><a href="#video">Video</a>
      </nav>
      <a className="header-source" href={SOURCE_ROOT}>GitHub</a>
    </header>
    <main>
      <noscript><p className="shell">JavaScript is needed for interactive previews and downloads. The explanations, source links, and render instructions remain available.</p></noscript>
      <section className="hero shell" aria-labelledby="page-title">
        <div className="hero-copy">
          <h1 id="page-title">Try the motion.<br /><span>Keep the source.</span></h1>
          <p>Three small studies in making an interface clearer. Interrupt a transition, direct a sequence, then edit a video you can render yourself.</p>
          <a className="text-link" href="#video">Make your own clip</a>
        </div>
        <InterfaceStudy />
      </section>
      <SequenceStudy />
      <VideoStudy />
      <section className="closing shell" aria-labelledby="next-step">
        <div><h2 id="next-step">Take one useful piece.</h2><p>Install a skill for the job in front of you, or adapt an example in your own project.</p></div>
        <div className="closing-links"><a href={`${SOURCE_ROOT}#install`}>Install a skill</a><a href="https://www.frankx.ai/newsletter?utm_source=github&utm_medium=referral&utm_campaign=motion-skills&utm_content=motion-lab">FrankX field notes</a></div>
      </section>
    </main>
    <footer className="site-footer shell"><p>Open examples from the FrankX motion skills repository.</p><a href={`${SOURCE_ROOT}/blob/main/LICENSE`}>Source and license</a></footer>
  </MotionConfig>;
}
