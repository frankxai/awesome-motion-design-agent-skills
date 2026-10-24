# Contributing to Awesome Motion Design Agent Skills

This repository earns trust by staying small, current, and verifiable. A pull request is welcome when it helps an operator or AI coding agent choose the right motion tool or ship cleaner animation tomorrow.

---

## 1. Adding or updating a curated catalog entry

An entry qualifies when:

- **Primary source:** It links directly to the official GitHub repository or specification (not a blog post, wrapper, or affiliate link).
- **One-sentence job:** It states in one plain sentence when to reach for it and what it does better than existing entries.
- **Active maintenance & clear license:** It has commits or releases within the last six months and states its SPDX license (or `Custom license` when non-standard, such as GSAP or Remotion).
- **Safety & accessibility caveats:** Tools that run headless browsers, execute local binaries (`ffmpeg`, `playwright`), or require external API keys state those requirements explicitly.

### Table format & `awesome-lint` alignment

Entries in [`README.md`](README.md) sit inside one of the four mobile-scannable category tables under `## Curated catalog`:

1. `### Web and UI animation`
2. `### Programmatic video and 3D scenes`
3. `### Interactive vector runtimes`
4. `### Agent standards and reference discovery`

Every table in `README.md` must have space-aligned pipes (`|`) so `npx --yes awesome-lint` passes (`remark-lint:table-pipe-alignment`). If listing an item in a bulleted doc outside `README.md`, use:

```markdown
- [GSAP](https://github.com/greensock/GSAP) - Timeline-grade JavaScript animation and ScrollTrigger choreography.
```

---

## 2. Adding or updating an installable skill in `skills/`

Each skill lives in `skills/<skill-name>/SKILL.md` and follows the open [`agentskills`](https://github.com/agentskills/agentskills) specification:

1. **YAML frontmatter (`name` and `description`):**
   - `name` must be kebab-case (`[a-z0-9-]+`), `<= 64` characters, and identical to the parent folder name (`skills/<name>/SKILL.md`).
   - `description` must be `<= 1024` characters and state *when* the skill should fire.
2. **Required content in `SKILL.md`:**
   - **When to use / When not to use**
   - **Decision tree or workflow steps**
   - **Reduced-motion requirement (`prefers-reduced-motion: reduce`)** — every motion skill must specify the static or reduced-motion path, not merely disable CSS transitions.
   - **Verification checklist** (frame budget, mobile layout, accessibility).
3. **Manifest sync:**
   - If adding a new first-party skill folder under `skills/`, update `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `README.md`, and `GETTING_STARTED.md`.

---

## 3. Visual assets & provenance sidecars (`assets/`)

Every tracked image in `assets/` (`.png`, `.svg`, `.jpg`, `.webp`) must have a companion `<filename>.vis.provenance.json` sidecar recording:

- `asset_id`, `image_path`, and `sidecar_path`
- `source_method` (`hand-authored-svg`, `deterministic-svg-render`, or `product-capture`)
- `sha256` (exact lowercase hex SHA-256 of the image bytes, verified in CI by `.github/workflows/skills-validate.yml`)
- `alt`, `viewport` (`width`, `height`), `rights`, and `timestamp`

---

## 4. Not accepted

- Affiliate, referral, or tracking links
- Unverified marketing superlatives or benchmark claims without reproducible source files
- Bulk skill dumps or unsigned third-party `.zip` blobs
- Private local machine or home-directory paths (blocked by CI)

---

## 5. Pre-PR verification checklist

Run these three checks from a clean checkout before opening a pull request:

```bash
# 1. Validate README formatting and table pipe alignment
npx --yes awesome-lint

# 2. Validate SKILL.md frontmatter, JSON manifests, internal links, and asset SHA-256 provenance
python3 scripts/verify-repo.py

# 3. Verify fresh-checkout installation for Claude Code and Codex
tmpdir="$(mktemp -d)"
git -C "$tmpdir" init -q
npx --yes skills add "$PWD" -a claude-code -y --cwd "$tmpdir"
npx --yes skills add "$PWD" -a codex -y --cwd "$tmpdir"
rm -rf "$tmpdir"
```

By contributing, you dedicate your contribution to the public domain under [CC0 1.0](LICENSE).
