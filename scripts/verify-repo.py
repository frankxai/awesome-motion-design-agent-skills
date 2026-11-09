#!/usr/bin/env python3
import hashlib, json, pathlib, re, sys

errs = []
root = pathlib.Path(__file__).resolve().parent.parent

# 1. Validate SKILL.md frontmatter
for skill in sorted(root.glob("skills/*/SKILL.md")):
    text = skill.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errs.append(f"{skill.relative_to(root)}: missing YAML frontmatter")
        continue
    fm = dict(re.findall(r"^(\w[\w-]*):\s*(.+)$", m.group(1), re.M))
    name, desc = fm.get("name", "").strip(), fm.get("description", "").strip()
    if name != skill.parent.name:
        errs.append(f"{skill.relative_to(root)}: name '{name}' != folder '{skill.parent.name}'")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        errs.append(f"{skill.relative_to(root)}: name must be kebab-case, <=64 chars")
    if not desc or len(desc) > 1024:
        errs.append(f"{skill.relative_to(root)}: description missing or >1024 chars")

# 2. Validate JSON manifests
for mf in [".claude-plugin/marketplace.json", ".claude-plugin/plugin.json", "skills-lock.json", ".github/repo-metadata.json"]:
    p = root / mf
    if not p.exists():
        errs.append(f"{mf}: missing required manifest")
    else:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if mf == ".github/repo-metadata.json":
                if not data.get("description") or len(data.get("topics", [])) < 10:
                    errs.append(f"{mf}: must include description and >=10 topics")
                sp = root / data.get("socialPreviewImage", "")
                if not sp.exists():
                    errs.append(f"{mf}: socialPreviewImage {sp} does not exist")
        except Exception as e:
            errs.append(f"{mf}: invalid JSON ({e})")

# 3. Validate visual asset provenance sidecars & SHA-256 digests
for asset in sorted((root / "assets").iterdir()):
    if asset.name.endswith(".vis.provenance.json") or asset.is_dir():
        continue
    sidecar = root / "assets" / f"{asset.name}.vis.provenance.json"
    if not sidecar.exists():
        errs.append(f"assets/{asset.name}: missing provenance sidecar {sidecar.name}")
        continue
    try:
        sc = json.loads(sidecar.read_bytes().decode("utf-8"))
        actual_sha = hashlib.sha256(asset.read_bytes()).hexdigest()
        if sc.get("sha256") != actual_sha:
            errs.append(f"assets/{asset.name}: provenance sha256 mismatch ({sc.get('sha256')} != {actual_sha})")
    except Exception as e:
        errs.append(f"{sidecar.name}: invalid JSON ({e})")

# 4. Validate internal Markdown links
for md in sorted(root.rglob("*.md")):
    if ".git" in md.parts:
        continue
    text = md.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        target = m.group(1).strip().split()[0]
        if target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        clean = target.split("#")[0]
        if clean and not (md.parent / clean).exists():
            errs.append(f"{md.relative_to(root)}: broken relative link -> {target}")

# 5. Validate public-safety (no local machine paths and no Higgsfield references)
leak = re.compile(r"[A-Za-z]:\\Users\\|/Users/[A-Za-z]+/|/home/[a-z]+/")
for f in sorted(root.rglob("*")):
    if f.is_file() and f.suffix in {".md", ".json", ".yml", ".yaml"} and ".git" not in f.parts:
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if leak.search(line):
                errs.append(f"{f.relative_to(root)}:{i}: private local path")
            if re.search(r"higgsfield", line, re.I):
                errs.append(f"{f.relative_to(root)}:{i}: prohibited Higgsfield reference")

if errs:
    print("\n".join(errs))
    sys.exit(1)
print("OK: skills, manifests, asset provenance sidecars, internal links, and public-safety verified")
