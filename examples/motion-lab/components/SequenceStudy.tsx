"use client";

import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "motion/react";
import gsap from "gsap";
import { sourceFile } from "../lib/brief";

const steps = [
  { name: "Brief", title: "Start with the job.", detail: "Name the audience, message, and one action the viewer should understand." },
  { name: "Choreograph", title: "Give attention a path.", detail: "One primary move, a clear hold, and a useful resting state." },
  { name: "Inspect", title: "Check what actually shipped.", detail: "Review the first frame, transitions, final hold, and reduced-motion alternative." },
];

export function SequenceStudy() {
  const [active, setActive] = useState(0);
  const root = useRef<HTMLDivElement>(null);
  const instant = useRef(false);
  const reduce = useReducedMotion();

  useEffect(() => {
    if (!root.current) return;
    const context = gsap.context(() => gsap.set(".traveller", { xPercent: 0 }), root);
    return () => context.revert();
  }, []);

  useEffect(() => {
    if (!root.current) return;
    const traveller = root.current.querySelector(".traveller");
    const tween = gsap.to(traveller, { xPercent: active * 100, duration: reduce || instant.current ? 0 : 0.55, ease: "power3.out", overwrite: "auto" });
    return () => { tween.kill(); };
  }, [active, reduce]);

  return <section id="sequence" className="sequence-section shell" aria-labelledby="sequence-heading">
    <div className="section-intro"><div><h2 id="sequence-heading">A sequence with a purpose.</h2><p>Move the emphasis. Keep the explanation still.</p></div><span className="runtime">GSAP</span></div>
    <div className="sequence-workbench" ref={root}>
      <div className="sequence-track" aria-hidden="true"><div className="track-line" /><div className="traveller"><span /></div></div>
      <div className="sequence-steps" role="group" aria-label="Sequence stage">
        {steps.map((step, index) => <button key={step.name} type="button" aria-pressed={index === active} onClick={event => {
          instant.current = event.detail === 0; setActive(index);
        }}><span className="step-name">{step.name}</span><span className="step-title">{step.title}</span><span className="step-detail">{step.detail}</span></button>)}
      </div>
      <p className="sequence-status" aria-live="polite">Current emphasis: {steps[active].name}</p>
    </div>
    <div className="study-caption"><p>No scroll pinning. No autoplay. All three steps remain readable.</p><a href={sourceFile("components/SequenceStudy.tsx")}>View source</a></div>
  </section>;
}
