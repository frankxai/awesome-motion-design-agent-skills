import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { DEFAULT_BRIEF, VIDEO, type LaunchBrief } from "../lib/brief";

export function LaunchFrame({ frame, brief }: { frame: number; brief: LaunchBrief }) {
  const appear = interpolate(frame, [0, 22], [0.72, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.23, 1, 0.32, 1) });
  const progress = interpolate(frame, [42, 178], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const settle = interpolate(frame, [150, 190], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.23, 1, 0.32, 1) });
  const movement = brief.reducedMotion ? 0 : (1 - appear) * 28;
  const headlineSize = brief.headline.length > 60 ? 84 : brief.headline.length > 40 ? 98 : 112;
  return <div className="launch-frame" style={{ width: VIDEO.width, height: VIDEO.height, background: "#101211", color: "#f6f3ed", fontFamily: "Arial, Helvetica, sans-serif", position: "relative", overflow: "hidden", padding: 100, boxSizing: "border-box" }}>
    <div style={{ display: "flex", alignItems: "center", gap: 18, fontSize: 29, opacity: appear }}><span style={{ width: 14, height: 14, background: brief.accent, borderRadius: 3 }} />{brief.product}</div>
    <div style={{ marginTop: 100, maxWidth: 1580, fontSize: headlineSize, fontWeight: 600, lineHeight: 1.05, letterSpacing: -3, whiteSpace: "pre-line", overflowWrap: "anywhere", opacity: appear, transform: `translateY(${movement}px)` }}>{brief.headline}</div>
    <div style={{ position: "absolute", left: 100, right: 100, bottom: 204, height: 2, background: "#434740" }}>
      <div style={{ width: "100%", height: 2, background: brief.accent, transformOrigin: "left", transform: `scaleX(${brief.reducedMotion ? 1 : progress})` }} />
    </div>
    <div style={{ position: "absolute", bottom: 115, left: 100, right: 100, display: "flex", justifyContent: "space-between", alignItems: "end", gap: 60 }}>
      <span style={{ fontSize: 30, lineHeight: 1.3, maxWidth: 1300, overflowWrap: "anywhere", opacity: 0.5 + settle * 0.5 }}>{brief.detail}</span>
      <span style={{ fontSize: 24, color: "#b9c0b4", whiteSpace: "nowrap" }}>Source included</span>
    </div>
  </div>;
}

export function LaunchVideo({ brief = DEFAULT_BRIEF }: { brief?: LaunchBrief }) {
  const frame = useCurrentFrame();
  return <AbsoluteFill><LaunchFrame frame={frame} brief={brief} /></AbsoluteFill>;
}
