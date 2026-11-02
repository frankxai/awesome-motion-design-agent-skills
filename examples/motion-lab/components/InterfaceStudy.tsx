"use client";

import { useRef, useState } from "react";
import { motion, useReducedMotion } from "motion/react";
import { sourceFile } from "../lib/brief";

export function InterfaceStudy() {
  const [expanded, setExpanded] = useState(false);
  const [instant, setInstant] = useState(false);
  const reduce = useReducedMotion();
  const trigger = useRef<HTMLButtonElement>(null);

  return <section id="interface" className="interface-study" aria-labelledby="interface-heading" onKeyDown={event => {
    if (event.key === "Escape" && expanded) {
      setInstant(true); setExpanded(false); trigger.current?.focus();
    }
  }}>
    <div className="study-heading"><h2 id="interface-heading">State, without the jump</h2><span className="runtime">Motion</span></div>
    <div className="interface-canvas">
      <div className="delivery-sheet">
        <div className="sheet-top"><span>Launch preview</span><span className="state-label">{expanded ? "Details open" : "Ready to review"}</span></div>
        <div className="mini-art" aria-hidden="true"><div className="art-rule" /><div className="art-square" /><div className="art-dot" /></div>
        <h3>Make the next step clear.</h3>
        <p>A small reveal keeps context in place.</p>
        <button className="disclosure" ref={trigger} aria-expanded={expanded} aria-controls="delivery-details" onClick={event => {
          setInstant(event.detail === 0); setExpanded(value => !value);
        }}>
          <span>{expanded ? "Hide delivery details" : "Show delivery details"}</span>
          <svg viewBox="0 0 20 20" width="20" height="20" fill="none" aria-hidden="true" style={{ transform: expanded ? "rotate(180deg)" : "none" }}><path d="m5 8 5 5 5-5" stroke="currentColor" strokeWidth="1.5" /></svg>
        </button>
        <motion.div id="delivery-details" aria-hidden={!expanded} initial={false} animate={{ height: expanded ? "auto" : 0, opacity: expanded ? 1 : 0 }} transition={{ duration: reduce || instant ? 0 : 0.22, ease: [0.23, 1, 0.32, 1] }} className="delivery-details">
          <dl><div><dt>Video</dt><dd>1920 × 1080</dd></div><div><dt>Timing</dt><dd>30 frames / second</dd></div><div><dt>Alternative</dt><dd>A useful still frame</dd></div></dl>
        </motion.div>
      </div>
    </div>
    <div className="study-caption"><p>Open it. Close it halfway. Your latest action wins.</p><a href={sourceFile("components/InterfaceStudy.tsx")}>View source</a></div>
  </section>;
}
