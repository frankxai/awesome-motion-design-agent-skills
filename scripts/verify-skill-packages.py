#!/usr/bin/env python3
"""Check the files users receive in a single-skill ZIP, without dependencies."""

import argparse
import io
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile


SKILLS = {
    "generative-media-director",
    "motion-director",
    "remotion-video-agent",
    "site-motion-excellence-director",
    "web-motion-auditor",
}

# Bundles are release payloads; the existing repo documents remain canonical.
BUNDLED_REFERENCES = {
    "motion-director/references/motion-quality-rubric.md": "rubrics/motion-quality-rubric.md",
    "web-motion-auditor/references/motion-quality-rubric.md": "rubrics/motion-quality-rubric.md",
    "site-motion-excellence-director/references/site-motion-spec.md": "templates/site-motion/SITE_MOTION_SPEC.md",
    "site-motion-excellence-director/references/site-motion-excellence-gate.md": "rubrics/site-motion-excellence-gate.md",
}


def validate_payload(folder):
    """Validate one standalone installed folder, with no repository fallback."""
    errors = []
    entry = folder / "SKILL.md"
    if not entry.is_file() or entry.is_symlink():
        return [f"{folder.name}: missing regular SKILL.md"]
    text = entry.read_text(encoding="utf-8")
    for bundle in BUNDLED_REFERENCES:
        skill, reference = bundle.split("/", 1)
        if skill == folder.name and not (folder / reference).is_file():
            errors.append(f"{folder.name}: missing required reference: {reference}")
    frontmatter = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not frontmatter:
        errors.append(f"{folder.name}: missing frontmatter")
    else:
        fields = dict(re.findall(r"^([a-z][a-z-]*):\s*(.+)$", frontmatter[1], re.M))
        name, description = fields.get("name", ""), fields.get("description", "")
        if name != folder.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            errors.append(f"{folder.name}: invalid skill name")
        if not description or len(description) > 1024:
            errors.append(f"{folder.name}: invalid description")

    for file in sorted(folder.rglob("*")):
        if file.is_symlink():
            errors.append(f"{folder.name}: symlink cannot be packaged: {file.relative_to(folder)}")
            continue
        if not file.is_file() or file.suffix != ".md":
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
            target = target.strip().split()[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme in {"https", "http", "mailto"} or target.startswith("#"):
                continue
            relative = unquote(parsed.path)
            if parsed.scheme or relative.startswith(("/", "\\")) or "\\" in relative:
                errors.append(f"{folder.name}: non-portable reference: {target}")
                continue
            resolved = (file.parent / relative).resolve()
            if not resolved.is_relative_to(folder.resolve()):
                errors.append(f"{folder.name}: reference escapes skill: {target}")
            elif not resolved.is_file():
                errors.append(f"{folder.name}: missing reference: {target}")
    return errors


def validate_repository(root):
    errors = []
    skill_root = root / "skills"
    found = {p.name for p in skill_root.iterdir() if p.is_dir()} if skill_root.exists() else set()
    if found != SKILLS:
        errors.append(f"skill inventory differs: missing={sorted(SKILLS - found)}, extra={sorted(found - SKILLS)}")
    for bundle, source in BUNDLED_REFERENCES.items():
        packaged, canonical = skill_root / bundle, root / source
        if not packaged.is_file():
            errors.append(f"missing bundled reference: {bundle}")
        elif not canonical.is_file() or packaged.read_bytes() != canonical.read_bytes():
            errors.append(f"bundled reference differs from canonical source: {bundle}")

    for name in sorted(found):
        folder = skill_root / name
        if folder.is_symlink():
            errors.append(f"{name}: skill folder must not be a symlink")
            continue
        payload_errors = validate_payload(folder)
        errors.extend(payload_errors)
        if payload_errors:
            continue
        # Match skills-release.yml: one top-level folder per individual ZIP.
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as package:
            for file in sorted(folder.rglob("*")):
                if file.is_file():
                    package.writestr(f"{name}/{file.relative_to(folder).as_posix()}", file.read_bytes())
        with tempfile.TemporaryDirectory(prefix="motion-skill-check-") as temporary:
            with zipfile.ZipFile(archive) as package:
                package.extractall(temporary)
            errors.extend(validate_payload(Path(temporary) / name))
    return errors


def validate_release_archives(root, archives):
    """Check actual release bytes without extracting untrusted ZIP paths."""
    errors = []
    names = SKILLS | {"all-skills"}
    found = {p.stem for p in archives.glob("*.zip")}
    if found != names:
        errors.append(f"release archive inventory differs: missing={sorted(names - found)}, extra={sorted(found - names)}")
    for name in sorted(names & found):
        folders = SKILLS if name == "all-skills" else {name}
        expected = {
            f"{skill}/{file.relative_to(root / 'skills' / skill).as_posix()}": file.read_bytes()
            for skill in folders for file in (root / "skills" / skill).rglob("*") if file.is_file()
        }
        try:
            with zipfile.ZipFile(archives / f"{name}.zip") as package:
                members = package.infolist()
                files = [item for item in members if not item.is_dir()]
                paths = [item.filename for item in files]
                if len(paths) != len(set(paths)):
                    errors.append(f"{name}.zip: duplicate member paths")
                for item in members:
                    path = PurePosixPath(item.filename)
                    if path.is_absolute() or ".." in path.parts or "\\" in item.filename or ":" in item.filename:
                        errors.append(f"{name}.zip: unsafe member path: {item.filename}")
                    mode = stat.S_IFMT(item.external_attr >> 16)
                    if mode not in ({0, stat.S_IFDIR} if item.is_dir() else {0, stat.S_IFREG}):
                        errors.append(f"{name}.zip: non-regular member: {item.filename}")
                actual = set(paths)
                if actual != set(expected):
                    errors.append(f"{name}.zip: payload differs: missing={sorted(set(expected) - actual)}, extra={sorted(actual - set(expected))}")
                for item in files:
                    if item.filename in expected and (item.file_size != len(expected[item.filename]) or package.read(item) != expected[item.filename]):
                        errors.append(f"{name}.zip: content differs from source: {item.filename}")
        except (OSError, RuntimeError, NotImplementedError, zipfile.BadZipFile) as error:
            errors.append(f"{name}.zip: cannot read archive: {error}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--archives", type=Path, help="Also verify the six actual ZIPs produced for release")
    args = parser.parse_args()
    errors = validate_repository(args.root.resolve())
    if args.archives:
        errors.extend(validate_release_archives(args.root.resolve(), args.archives.resolve()))
    print("\n".join(errors) if errors else "OK: five standalone skill payloads, four canonical references" + (", and six actual release archives" if args.archives else ""))
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
