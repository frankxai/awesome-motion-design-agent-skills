import { test, expect, type Page } from "@playwright/test";
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { makeProvenance } from "../lib/provenance";

const storageKey = "motion-skills-launch-brief-v1";
const captureRoot = "output/captures";

async function capture(page: Page, name: string) {
  await mkdir(captureRoot, { recursive: true });
  const file = `${captureRoot}/${name}.png`;
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: file, animations: "disabled" });
  const sourceRevision = process.env.MOTION_SOURCE_REVISION || process.env.GITHUB_SHA || null;
  const prompt = `Capture the Motion lab at ${page.viewportSize()?.width}x${page.viewportSize()?.height}, state ${name}, from source revision ${sourceRevision || "local"}.`;
  await writeFile(`${file}.vis.provenance.json`, JSON.stringify(makeProvenance({ file, prompt, provider: "Playwright", tool: "@playwright/test", toolVersion: "1.64.1", mediaType: "image", hash: createHash("sha256").update(await readFile(file)).digest("hex"), sourceRevision, settings: { viewport: page.viewportSize(), state: name }, reviewState: "visual inspection pending" }), null, 2) + "\n");
}

async function noHorizontalOverflow(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
}

test("desktop supports keyboard, interruption, sequence selection, and source access", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await page.evaluate(() => document.fonts.ready);
  expect(await page.evaluate(() => document.fonts.check('500 16px "Onest Variable"'))).toBe(true);
  await expect(page.getByRole("heading", { name: "Try the motion. Keep the source." })).toBeVisible();
  await noHorizontalOverflow(page);
  await capture(page, "desktop");
  const toggle = page.locator('button[aria-controls="delivery-details"]');
  await toggle.focus();
  expect(await toggle.evaluate(element => getComputedStyle(element).outlineStyle)).not.toBe("none");
  await page.keyboard.press("Enter");
  await expect(toggle).toHaveAttribute("aria-expanded", "true");
  await expect(page.getByText("A useful still frame", { exact: true })).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(toggle).toHaveAttribute("aria-expanded", "false");
  await expect(toggle).toBeFocused();
  await toggle.click(); await page.waitForTimeout(60); await toggle.click(); await page.waitForTimeout(60); await toggle.click();
  await expect(toggle).toHaveAttribute("aria-expanded", "true");
  await expect.poll(async () => page.locator("#delivery-details").evaluate(element => element.getBoundingClientRect().height)).toBeGreaterThan(80);
  await toggle.click();
  await expect.poll(async () => page.locator("#delivery-details").evaluate(element => element.getBoundingClientRect().height)).toBeLessThan(1);
  const sequence = page.getByRole("group", { name: "Sequence stage" });
  await sequence.getByRole("button", { name: /^Inspect/ }).click();
  await page.waitForTimeout(80);
  await sequence.getByRole("button", { name: /^Brief/ }).click();
  await sequence.getByRole("button", { name: /^Choreograph/ }).click();
  await expect(sequence.getByRole("button", { name: /^Choreograph/ })).toHaveAttribute("aria-pressed", "true");
  await expect.poll(async () => page.locator(".traveller").evaluate(element => {
    const rect = element.getBoundingClientRect();
    const parent = element.parentElement!.getBoundingClientRect();
    return Math.round((rect.left - parent.left) / rect.width);
  })).toBe(1);
  await page.locator("#sequence").scrollIntoViewIfNeeded();
  await capture(page, "desktop-sequence");
  await expect(page.getByRole("link", { name: "View source", exact: true }).first()).toHaveAttribute("href", /components\/InterfaceStudy\.tsx$/);
  if (process.env.MOTION_SOURCE_REVISION) await expect(page.getByRole("link", { name: "View source", exact: true }).first()).toHaveAttribute("href", new RegExp(process.env.MOTION_SOURCE_REVISION));
  await expect(page.getByRole("link", { name: "FrankX field notes" })).toHaveAttribute("href", /utm_campaign=motion-skills/);
  expect(errors).toEqual([]);
});

test("brief edits survive reload and download the actual render inputs", async ({ page }) => {
  await page.goto("/#video");
  await page.getByLabel("Product name", { exact: true }).fill("Field notes");
  await page.getByLabel("Headline", { exact: true }).fill("One signal.\nA useful move.");
  await page.getByLabel("Supporting line", { exact: true }).fill("Make the next step easier to understand.");
  await expect.poll(async () => page.evaluate(key => JSON.parse(localStorage.getItem(key) || "{}").brief?.product, storageKey)).toBe("Field notes");
  await page.reload();
  await expect(page.getByLabel("Product name", { exact: true })).toHaveValue("Field notes");
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download render inputs" }).click();
  const download = await downloadPromise;
  const json = JSON.parse(await readFile((await download.path())!, "utf8"));
  expect(json.product).toBe("Field notes");
  expect(json.headline).toBe("One signal.\nA useful move.");
  await capture(page, "desktop-video");
  await page.getByLabel("Headline", { exact: true }).fill("");
  await page.getByRole("button", { name: "Download render inputs" }).click();
  await expect(page.locator("#video").getByRole("alert")).toContainText("headline");
});

test("a corrupt saved brief is preserved until the user resets it", async ({ page }) => {
  await page.addInitScript(key => localStorage.setItem(key, "broken JSON"), storageKey);
  await page.goto("/#video");
  await expect(page.locator("#video").getByRole("alert")).toContainText("saved data has been kept");
  expect(await page.evaluate(key => localStorage.getItem(key), storageKey)).toBe("broken JSON");
  await page.getByRole("button", { name: "Reset saved brief" }).click();
  await expect(page.locator("#video").getByRole("alert")).toHaveCount(0);
  expect(await page.evaluate(key => JSON.parse(localStorage.getItem(key)!).version, storageKey)).toBe(1);
});

test("a failed lazy preview preserves the brief and still-frame fallback", async ({ page }) => {
  await page.goto("/#video");
  await page.evaluate(() => document.fonts.ready);
  await page.getByLabel("Product name", { exact: true }).fill("Recoverable preview");
  await page.route("**/_next/static/chunks/**", route => route.abort("failed"));
  await page.getByRole("button", { name: "Load video preview" }).click();
  await expect(page.locator("#video").getByRole("alert")).toContainText("Your brief is intact");
  await expect(page.getByLabel("Product name", { exact: true })).toHaveValue("Recoverable preview");
  await capture(page, "preview-load-failure");
  await page.getByRole("button", { name: "Show still frame" }).click();
  await expect(page.locator("#video").getByRole("alert")).toHaveCount(0);
});

test("phone touch layout and reduced motion preserve the controls and content", async ({ browser }) => {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
  const page = await context.newPage();
  await page.goto("/");
  await noHorizontalOverflow(page);
  await capture(page, "mobile-reduced");
  await page.getByRole("button", { name: "Show delivery details" }).tap();
  await expect(page.getByText("A useful still frame", { exact: true })).toBeVisible();
  await page.getByRole("link", { name: "Video", exact: true }).tap();
  await expect(page.getByLabel("Headline", { exact: true })).toBeVisible();
  await page.getByLabel("Headline", { exact: true }).fill("W".repeat(80));
  await noHorizontalOverflow(page);
  await capture(page, "mobile-video-long-copy");
  await expect(page.getByRole("checkbox", { name: "Export the reduced-motion version" })).toBeChecked();
  await context.close();
});

test("essential explanations and source routes survive without JavaScript", async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await page.goto("/");
  // Playwright excludes noscript descendants from text selectors (microsoft/playwright#32542).
  const fallbackNotice = page.locator("noscript > p");
  await expect(fallbackNotice).toBeVisible();
  await expect(fallbackNotice).toContainText("JavaScript is needed for interactive previews");
  await expect(page.getByText("Give attention a path.", { exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "View composition source" })).toBeVisible();
  const poster = page.locator(".video-poster");
  await poster.scrollIntoViewIfNeeded();
  const frame = poster.locator(".launch-frame");
  const posterSize = await poster.boundingBox();
  const frameSize = await frame.boundingBox();
  expect(frameSize!.width).toBeLessThanOrEqual(posterSize!.width);
  expect(frameSize!.width).toBeGreaterThan(posterSize!.width - 4);
  await capture(page, "mobile-without-javascript");
  await noHorizontalOverflow(page);
  await context.close();
});

test("the rendered MP4 decodes and plays in the browser", async ({ page }) => {
  const receipt = JSON.parse(await readFile("output/latest.json", "utf8"));
  expect(receipt.state).toBe("passed");
  const bytes = await readFile(`output/${receipt.output}`);
  expect(createHash("sha256").update(bytes).digest("hex")).toBe(receipt.outputSha256);
  await page.setContent('<main><h1>Rendered output playback</h1><video controls muted style="width:960px;max-width:100%"></video></main>');
  await page.locator("video").evaluate(async (element, source) => {
    const video = element as HTMLVideoElement;
    video.src = `data:video/mp4;base64,${source}`;
    await video.play();
  }, bytes.toString("base64"));
  await expect.poll(async () => page.locator("video").evaluate(element => (element as HTMLVideoElement).currentTime)).toBeGreaterThan(0.25);
  expect(await page.locator("video").evaluate(element => [(element as HTMLVideoElement).videoWidth, (element as HTMLVideoElement).videoHeight])).toEqual([1920, 1080]);
  await page.locator("video").evaluate(element => (element as HTMLVideoElement).pause());
  await capture(page, "rendered-video-playback");
});
