import test from "node:test";
import assert from "node:assert/strict";
import { parseBrief, DEFAULT_BRIEF } from "../lib/brief.ts";
import { verifyMetadata, reusableExport } from "./render.mjs";
import { mkdtemp, readFile, writeFile, unlink, rmdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";

const validMetadata = { streams: [{ codec_type: "video", width: 1920, height: 1080, codec_name: "h264", avg_frame_rate: "30/1" }], format: { duration: "8.000" } };

test("accepts a valid brief and drops unrelated fields", () => {
  assert.deepEqual(parseBrief({ ...DEFAULT_BRIEF, unrelatedCommand: "ignored" }), DEFAULT_BRIEF);
});
test("rejects empty and oversized text before a render starts", () => {
  assert.throws(() => parseBrief({ ...DEFAULT_BRIEF, headline: " " }), /headline/);
  assert.throws(() => parseBrief({ ...DEFAULT_BRIEF, headline: "a".repeat(81) }), /headline/);
});
test("rejects line counts that cannot fit the composition", () => {
  assert.throws(() => parseBrief({ ...DEFAULT_BRIEF, headline: "one\ntwo\nthree\nfour" }), /three lines/);
  assert.throws(() => parseBrief({ ...DEFAULT_BRIEF, product: "one\ntwo" }), /one paragraph/);
});
test("rejects non-color CSS and missing motion preference", () => {
  assert.throws(() => parseBrief({ ...DEFAULT_BRIEF, accent: "url(example)" }), /accent/);
  assert.throws(() => parseBrief({ ...DEFAULT_BRIEF, reducedMotion: undefined }), /preference/);
});
test("checks a real output's format, dimensions, rate, and duration", () => {
  assert.deepEqual(verifyMetadata(validMetadata), { width: 1920, height: 1080, codec: "h264", fps: 30, duration: 8 });
  assert.throws(() => verifyMetadata({ ...validMetadata, format: { duration: "7" } }), /duration/);
  assert.throws(() => verifyMetadata({ ...validMetadata, streams: [] }), /1920/);
  assert.throws(() => verifyMetadata({ ...validMetadata, streams: [{ ...validMetadata.streams[0], avg_frame_rate: "60/1" }] }), /frame rate/);
});

test("a missing poster or changed output prevents cache reuse", async () => {
  const folder = await mkdtemp(join(tmpdir(), "motion-cache-test-"));
  const output = join(folder, "video.mp4");
  const poster = join(folder, "poster.png");
  const digest = value => createHash("sha256").update(value).digest("hex");
  try {
    await writeFile(output, "video bytes");
    const receipt = { state: "passed", output: "video.mp4", poster: "poster.png", outputSha256: digest("video bytes"), posterSha256: digest("poster bytes") };
    await writeFile(`${output}.vis.provenance.json`, JSON.stringify({ asset: { sha256: receipt.outputSha256 }, generation: { prompt: "render" } }));
    assert.equal(await reusableExport(receipt, folder, async () => {}), null);
    await writeFile(poster, "poster bytes");
    await writeFile(`${poster}.vis.provenance.json`, JSON.stringify({ asset: { sha256: receipt.posterSha256 }, generation: { prompt: "render" } }));
    assert.equal(await reusableExport(receipt, folder, async () => {}), output);
    await writeFile(output, "changed bytes");
    assert.equal(await reusableExport(receipt, folder, async () => {}), null);
  } finally {
    for (const path of [output, poster, `${output}.vis.provenance.json`, `${poster}.vis.provenance.json`]) { try { await unlink(path); } catch {} }
    await rmdir(folder);
  }
});

test("an invalid CLI input fails before replacing a previous receipt", async () => {
  const folder = await mkdtemp(join(tmpdir(), "motion-invalid-input-"));
  const input = join(folder, "invalid.json");
  const latest = resolve("output/latest.json");
  let before = null;
  try { before = await readFile(latest, "utf8"); } catch {}
  try {
    await writeFile(input, JSON.stringify({ ...DEFAULT_BRIEF, headline: "" }));
    const result = spawnSync(process.execPath, [resolve("scripts/render.mjs"), input], { encoding: "utf8", timeout: 10000 });
    assert.equal(result.status, 1);
    assert.match(result.stderr, /headline/);
    let after = null;
    try { after = await readFile(latest, "utf8"); } catch {}
    assert.equal(after, before);
  } finally { await unlink(input); await rmdir(folder); }
});
