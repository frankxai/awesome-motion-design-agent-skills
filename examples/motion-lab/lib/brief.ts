export type LaunchBrief = {
  product: string;
  headline: string;
  detail: string;
  accent: string;
  reducedMotion: boolean;
};

export const DEFAULT_BRIEF: LaunchBrief = {
  product: "Motion design agent skills",
  headline: "Make the next\nstep clear.",
  detail: "Open examples for Motion, GSAP, and Remotion.",
  accent: "#ef765c",
  reducedMotion: false,
};

export const VIDEO = { width: 1920, height: 1080, fps: 30, durationInFrames: 240 } as const;

export function parseBrief(value: unknown): LaunchBrief {
  if (!value || typeof value !== "object") throw new Error("The saved brief is not an object.");
  const input = value as Record<string, unknown>;
  for (const [key, maximum] of [["product", 48], ["headline", 80], ["detail", 100]] as const) {
    if (typeof input[key] !== "string" || !input[key].trim() || input[key].length > maximum) {
      throw new Error(`The ${key} must contain 1-${maximum} characters.`);
    }
  }
  const headline = (input.headline as string).replace(/\r\n?/g, "\n").trim();
  if (headline.split("\n").length > 3) throw new Error("Keep the headline to three lines or fewer.");
  if (/[\r\n]/.test(input.product as string) || /[\r\n]/.test(input.detail as string)) {
    throw new Error("Keep the product name and supporting line to one paragraph each.");
  }
  if (typeof input.accent !== "string" || !/^#[a-fA-F0-9]{6}$/.test(input.accent)) {
    throw new Error("Choose a six-digit accent color.");
  }
  if (typeof input.reducedMotion !== "boolean") throw new Error("The motion preference is missing.");
  return {
    product: (input.product as string).trim(),
    headline,
    detail: (input.detail as string).trim(),
    accent: input.accent,
    reducedMotion: input.reducedMotion,
  };
}

export const SOURCE_ROOT = "https://github.com/frankxai/awesome-motion-design-agent-skills";
export const SOURCE_REF = typeof process !== "undefined" ? process.env.NEXT_PUBLIC_SOURCE_REVISION || "main" : "main";
export function sourceFile(file: string) {
  return `${SOURCE_ROOT}/blob/${SOURCE_REF}/examples/motion-lab/${file}`;
}
