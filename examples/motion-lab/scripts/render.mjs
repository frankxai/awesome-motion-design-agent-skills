import { createHash } from "node:crypto";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { readFile, writeFile, mkdir, rename, stat } from "node:fs/promises";
import { dirname, resolve, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { parseBrief, VIDEO } from "../lib/brief.ts";
import { makeProvenance } from "../lib/provenance.ts";

const run = promisify(execFile);
const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sha256 = value => createHash("sha256").update(value).digest("hex");

export function verifyMetadata(metadata) {
  const stream = metadata.streams?.find(item => item.codec_type === "video");
  if (!stream || stream.width !== VIDEO.width || stream.height !== VIDEO.height || stream.codec_name !== "h264") {
    throw new Error("Export validation failed: expected a 1920×1080 H.264 video.");
  }
  const [numerator, denominator = 1] = stream.avg_frame_rate.split("/").map(Number);
  const fps = numerator / denominator;
  const duration = Number(metadata.format?.duration);
  if (!Number.isFinite(fps) || Math.abs(fps - VIDEO.fps) > 0.01 || !Number.isFinite(duration) || Math.abs(duration - VIDEO.durationInFrames / VIDEO.fps) > 0.08) {
    throw new Error("Export validation failed: frame rate or duration differs from the composition.");
  }
  return { width: stream.width, height: stream.height, codec: stream.codec_name, fps, duration };
}

async function atomicJSON(path, value) {
  const temporary = `${path}.tmp-${process.pid}`;
  await writeFile(temporary, JSON.stringify(value, null, 2) + "\n");
  await rename(temporary, path);
}

async function inspect(path) {
  const { stdout } = await run("ffprobe", ["-v", "error", "-show_streams", "-show_format", "-of", "json", path], { timeout: 30000 });
  return verifyMetadata(JSON.parse(stdout));
}

async function fileHash(path) { return sha256(await readFile(path)); }

export async function reusableExport(receipt, outputRoot, inspectVideo = inspect) {
  if (receipt?.state !== "passed" || !receipt.output || !receipt.poster) return null;
  try {
    for (const [name, hash] of [[receipt.output, receipt.outputSha256], [receipt.poster, receipt.posterSha256]]) {
      const path = resolve(outputRoot, basename(name));
      if (await fileHash(path) !== hash) return null;
      const sidecar = JSON.parse(await readFile(`${path}.vis.provenance.json`, "utf8"));
      if (sidecar.asset?.sha256 !== hash || !sidecar.generation?.prompt) return null;
    }
    const videoPath = resolve(outputRoot, basename(receipt.output));
    await inspectVideo(videoPath);
    return videoPath;
  } catch { return null; }
}

async function render() {
  const inputPath = resolve(process.cwd(), process.argv[2] || "fixtures/launch.json");
  if ((await stat(inputPath)).size > 16384) throw new Error("The brief is too large; expected a JSON file below 16 KiB.");
  const brief = parseBrief(JSON.parse(await readFile(inputPath, "utf8")));
  try { await run("ffprobe", ["-version"], { timeout: 10000 }); }
  catch { throw new Error("FFprobe is required to check the export. Install FFmpeg and retry; previous exports have been kept."); }

  const sourceFiles = ["video/LaunchVideo.tsx", "video/index.tsx", "lib/brief.ts", "lib/provenance.ts", "scripts/render.mjs", "package-lock.json"];
  const sourceHashes = Object.fromEntries(await Promise.all(sourceFiles.map(async name => [name, await fileHash(resolve(root, name))])));
  const sourceHash = sha256(JSON.stringify(sourceHashes));
  let sourceRevision = null;
  try { sourceRevision = (await run("git", ["rev-parse", "HEAD"], { cwd: root, timeout: 10000 })).stdout.trim(); } catch { /* Source archives still carry content hashes. */ }
  const briefHash = sha256(JSON.stringify(brief));
  const jobId = sha256(`${sourceHash}:${briefHash}`).slice(0, 16);
  const outputRoot = resolve(root, "output");
  await mkdir(outputRoot, { recursive: true });
  const jobPath = resolve(outputRoot, `job-${jobId}.json`);
  let previous;
  try { previous = JSON.parse(await readFile(jobPath, "utf8")); } catch { previous = null; }
  const reusable = await reusableExport(previous, outputRoot);
  if (reusable) {
    console.log(`Reused checked export: ${reusable}`);
    return;
  }

  const runId = Date.now();
  const staged = resolve(outputRoot, `candidate-${jobId}-${runId}.mp4`);
  const final = resolve(outputRoot, `launch-${jobId}-${runId}.mp4`);
  const poster = resolve(outputRoot, `launch-${jobId}-${runId}.png`);
  const receipt = { author: "Codex", revision: 1, state: "rendering", jobId, startedAt: new Date().toISOString(), sourceRevision, sourceHash, sourceHashes, briefHash, brief, video: VIDEO, previousExport: previous?.output || null };
  await atomicJSON(jobPath, receipt);
  const prompt = `Render the LaunchDemo composition from the exact brief and source hashes in job ${jobId}. Export H.264 at 1920x1080, 30 fps, 240 frames, plus a 1280x720 poster at frame 200. Preserve prior exports and validate the result.`;
  const provenance = (path, hash, reviewState) => makeProvenance({ file: path, hash, prompt, provider: "Remotion", tool: "@remotion/renderer", toolVersion: "4.0.540", mediaType: path.endsWith(".mp4") ? "video" : "image", sourceRevision, settings: { sourceHash, sourceHashes, brief, briefHash, jobId }, reviewState });
  let serveUrl;
  try {
    const { bundle } = await import("@remotion/bundler");
    const { selectComposition, renderMedia, renderStill } = await import("@remotion/renderer");
    serveUrl = await bundle({ entryPoint: resolve(root, "video/index.tsx") });
    const browserExecutable = process.env.REMOTION_BROWSER_EXECUTABLE || undefined;
    const inputProps = { brief };
    const composition = await selectComposition({ serveUrl, id: "LaunchDemo", inputProps, browserExecutable });
    await atomicJSON(`${staged}.vis.provenance.json`, provenance(staged, null, "render pending"));
    await renderMedia({ composition, serveUrl, inputProps, outputLocation: staged, codec: "h264", pixelFormat: "yuv420p", concurrency: 1, browserExecutable });
    const metadata = await inspect(staged);
    if ((await stat(staged)).size === 0) throw new Error("The renderer returned an empty export.");
    await atomicJSON(`${staged}.vis.provenance.json`, provenance(staged, await fileHash(staged), "metadata checked; visual inspection pending"));
    await atomicJSON(`${poster}.vis.provenance.json`, provenance(poster, null, "render pending"));
    await renderStill({ composition, serveUrl, inputProps, output: poster, frame: 200, imageFormat: "png", scale: 2 / 3, browserExecutable });
    const posterBytes = await readFile(poster);
    if (posterBytes.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a" || posterBytes.readUInt32BE(16) !== 1280 || posterBytes.readUInt32BE(20) !== 720) {
      throw new Error("Poster validation failed: expected a 1280×720 PNG.");
    }
    await rename(staged, final);
    await rename(`${staged}.vis.provenance.json`, `${final}.vis.provenance.json`);
    const finalReceipt = { ...receipt, state: "passed", completedAt: new Date().toISOString(), output: basename(final), outputSha256: await fileHash(final), poster: basename(poster), posterSha256: await fileHash(poster), metadata, reviewState: "render and metadata checked; visual review pending" };
    for (const [path, hash] of [[final, finalReceipt.outputSha256], [poster, finalReceipt.posterSha256]]) {
      await atomicJSON(`${path}.vis.provenance.json`, provenance(path, hash, "render and metadata checked; visual inspection pending"));
    }
    await atomicJSON(jobPath, finalReceipt);
    await atomicJSON(resolve(outputRoot, "latest.json"), finalReceipt);
    console.log(`Checked video: ${final}\nPoster: ${poster}\nReceipt: ${jobPath}`);
  } catch (error) {
    for (const path of [staged, poster]) {
      try { await atomicJSON(`${path}.vis.provenance.json`, provenance(path, await fileHash(path), "render failed; artifact incomplete")); } catch { /* A failure before file creation leaves no generated artifact. */ }
    }
    await atomicJSON(jobPath, { ...receipt, state: "failed", failedAt: new Date().toISOString(), error: error instanceof Error ? error.message : String(error), partialOutput: basename(staged), previousExport: previous?.output || null });
    throw error;
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  render().catch(error => { console.error(error.message); process.exitCode = 1; });
}
