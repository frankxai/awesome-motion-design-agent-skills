"use client";

import dynamic from "next/dynamic";
import { Component, useEffect, useRef, useState, type ReactNode } from "react";
import { useReducedMotion } from "motion/react";
import { DEFAULT_BRIEF, VIDEO, parseBrief, type LaunchBrief } from "../lib/brief";
import { sourceFile } from "../lib/source";
import { LaunchFrame } from "../video/LaunchVideo";

const Preview = dynamic(() => import("./VideoPreview"), { ssr: false, loading: () => <div className="preview-loading" role="status">Loading the video controls…</div> });
const STORAGE_KEY = "motion-skills-launch-brief-v1";

class PreviewBoundary extends Component<{ children: ReactNode; fallback: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? this.props.fallback : this.props.children; }
}

function Poster({ brief }: { brief: LaunchBrief }) {
  const root = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(640);
  useEffect(() => {
    if (!root.current) return;
    const observer = new ResizeObserver(entries => setWidth(entries[0].contentRect.width));
    observer.observe(root.current);
    return () => observer.disconnect();
  }, []);
  return <div className="video-poster" ref={root} role="img" aria-label={`${brief.product}. ${brief.headline.replaceAll("\n", " ")}. ${brief.detail}`}>
    <div aria-hidden="true" style={{ transform: `scale(${width / VIDEO.width})`, transformOrigin: "top left" }}><LaunchFrame frame={200} brief={brief} /></div>
  </div>;
}

export function VideoStudy() {
  const [brief, setBrief] = useState<LaunchBrief>(DEFAULT_BRIEF);
  const [loaded, setLoaded] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [storageError, setStorageError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState("");
  const reduce = useReducedMotion();

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const saved = JSON.parse(stored);
        if (saved.version !== 1) throw new Error("The saved brief uses a different version.");
        setBrief(parseBrief(saved.brief));
      } else {
        setBrief({ ...DEFAULT_BRIEF, reducedMotion: matchMedia("(prefers-reduced-motion: reduce)").matches });
      }
    } catch {
      setStorageError("The saved brief could not be loaded. The example is shown; your saved data has been kept.");
    }
    setLoaded(true);
  }, []);

  useEffect(() => {
    if (!loaded || storageError) return;
    let valid: LaunchBrief;
    try {
      valid = parseBrief(brief);
    } catch {
      // Incomplete typing must not replace the last valid saved brief.
      return;
    }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ version: 1, brief: valid }));
    } catch {
      setStorageError("This browser could not save the brief. You can keep editing and download the JSON file.");
    }
  }, [brief, loaded, storageError]);

  function update<K extends keyof LaunchBrief>(key: K, value: LaunchBrief[K]) {
    setBrief(current => ({ ...current, [key]: value }));
    setFormError(null); setNotice("");
  }

  function download() {
    try {
      const valid = parseBrief(brief);
      const url = URL.createObjectURL(new Blob([JSON.stringify(valid, null, 2) + "\n"], { type: "application/json" }));
      const link = document.createElement("a");
      link.href = url; link.download = "motion-brief.json"; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setNotice("Downloaded motion-brief.json. Save it in the example folder to render your clip.");
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Check the brief before downloading.");
    }
  }

  function resetSaved() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ version: 1, brief: DEFAULT_BRIEF }));
      setBrief(DEFAULT_BRIEF); setStorageError(null); setNotice("The saved brief has been reset to the example.");
    } catch {
      setStorageError("This browser cannot save the brief. You can still edit it and download the JSON file.");
    }
  }

  const previewBrief = { ...brief, reducedMotion: brief.reducedMotion || Boolean(reduce) };
  return <section id="video" className="video-section shell" aria-labelledby="video-heading">
    <div className="section-intro"><div><h2 id="video-heading">Your words. The same eight seconds.</h2><p>Edit a real composition, then take its inputs and source.</p></div><span className="runtime">Remotion</span></div>
    <div className="video-workbench">
      <div className="video-output">
        {showPreview ? <PreviewBoundary fallback={<><Poster brief={previewBrief} /><p className="form-message" role="alert">The video preview could not load. Your brief is intact; return to the still frame or use the included renderer.</p></>}><Preview brief={previewBrief} /></PreviewBoundary> : <Poster brief={previewBrief} />}
        <div className="video-controls"><span>1920 × 1080 · 30 fps · 8 seconds</span><button type="button" className="quiet-button" onClick={() => setShowPreview(current => !current)}>{showPreview ? "Show still frame" : "Load video preview"}</button></div>
        {reduce && <p className="preference-note">Reduced motion is on. The preview uses a gentle fade and keeps positions still.</p>}
        <details className="render-instructions"><summary>Render the MP4 on your machine</summary><p>Save the downloaded brief in this example’s folder, install its dependencies, then run:</p><pre><code>npm run render -- motion-brief.json</code></pre><p>The renderer checks the export before replacing the latest receipt. Previous exports remain available.</p></details>
      </div>
      <form className="brief-editor" onSubmit={event => { event.preventDefault(); download(); }}>
        <h3>Edit the brief</h3>
        <label htmlFor="product">Product name</label><input id="product" value={brief.product} maxLength={48} onChange={event => update("product", event.target.value)} autoComplete="off" />
        <label htmlFor="headline">Headline</label><textarea id="headline" value={brief.headline} maxLength={80} rows={3} aria-describedby="headline-help" onChange={event => update("headline", event.target.value)} /><p id="headline-help" className="field-help">Up to three lines and 80 characters.</p>
        <label htmlFor="detail">Supporting line</label><textarea id="detail" value={brief.detail} maxLength={100} rows={2} onChange={event => update("detail", event.target.value)} />
        <label htmlFor="accent">Accent color</label><div className="color-control"><input id="accent" type="color" value={brief.accent} onChange={event => update("accent", event.target.value)} /><span>{brief.accent}</span></div>
        <label className="checkbox-label"><input type="checkbox" checked={brief.reducedMotion} onChange={event => update("reducedMotion", event.target.checked)} />Export the reduced-motion version</label>
        {storageError && <div className="form-message" role="alert"><p>{storageError}</p><button type="button" className="quiet-button" onClick={resetSaved}>Reset saved brief</button></div>}
        {formError && <p className="form-message" role="alert">{formError}</p>}
        <button className="primary-button" type="submit">Download render inputs</button>
        <p className="save-note" role="status">{notice || (storageError ? "Editing and download remain available." : "Valid edits are saved in this browser.")}</p>
      </form>
    </div>
    <div className="study-caption"><p>Frame-driven timing. Editable text. No generated footage or audio.</p><a href={sourceFile("video/LaunchVideo.tsx")}>View composition source</a></div>
  </section>;
}
