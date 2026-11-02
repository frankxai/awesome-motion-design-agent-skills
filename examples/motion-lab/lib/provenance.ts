import { createHash } from "node:crypto";
import { basename } from "node:path";

type ProvenanceInput = {
  file: string;
  mediaType: "image" | "video";
  prompt: string;
  provider: string;
  tool: string;
  toolVersion: string;
  hash?: string | null;
  sourceRevision?: string | null;
  settings?: Record<string, unknown>;
  reviewState: string;
};

export function makeProvenance(input: ProvenanceInput) {
  return {
    $schema: "https://frankx.ai/schemas/vis-provenance-sidecar.schema.json",
    schema_version: "1.0.0",
    asset: { asset_id: input.hash ? `sha256:${input.hash}` : null, media_type: input.mediaType, sha256: input.hash || null, relative_path: basename(input.file) },
    generation: {
      provider: input.provider, model: null, prompt: input.prompt, seed: null,
      settings: { tool: input.tool, tool_version: input.toolVersion, source_revision: input.sourceRevision || null, ...input.settings },
      output_paths: [basename(input.file)], created_at: new Date().toISOString(),
    },
    agent: { coding_agent: "Codex", repo: "frankxai/awesome-motion-design-agent-skills", session_ref: "motion-audit-20261102", summary: "Deterministic example render or browser capture; no image/video generation model used." },
    evaluation: { review_state: input.reviewState, prompt_sha256: createHash("sha256").update(input.prompt).digest("hex"), schema_source_revision: "9458fab2540eab49d26e42e13d481e00b4486960", reproducibility: "Inputs and frame timing recorded; bit-identical encoding not asserted." },
    rights: { state: "unreviewed", source: "Example code and user-supplied text. No external footage, audio, or likenesses." },
  };
}
