#!/usr/bin/env python3
"""Allow an older packaged revision only when current main has identical release inputs."""

import argparse
from fnmatch import fnmatchcase
import json
from pathlib import PurePosixPath
import re
import subprocess
import sys


# Keep the push filter aligned; a regression test checks this contract.
RELEASE_PATHS = (
    "skills/**",
    ".github/workflows/skills-release.yml",
    "scripts/verify-skill-packages.py",
    "scripts/release-policy.py",
    "tests/**",
    "rubrics/motion-quality-rubric.md",
    "rubrics/site-motion-excellence-gate.md",
    "templates/site-motion/SITE_MOTION_SPEC.md",
)
MODES = {"100644": "blob", "100755": "blob", "120000": "blob",
         "040000": "tree", "160000": "commit"}


def inventory(response):
    if not isinstance(response, dict) or response.get("truncated") is not False:
        raise ValueError("Release comparison requires complete Git trees")
    entries = response.get("tree")
    if not isinstance(entries, list):
        raise ValueError("Git tree entries are missing")
    found, selected = set(), {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Malformed Git tree entry")
        path, mode, kind, sha = (entry.get(key) for key in ("path", "mode", "type", "sha"))
        if (not isinstance(path, str) or not path or path in found
                or PurePosixPath(path).is_absolute() or "\\" in path or ":" in path
                or any(part in {"", ".", ".."} for part in path.split("/"))
                or not isinstance(mode, str) or mode not in MODES or MODES[mode] != kind
                or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha)):
            raise ValueError("Malformed or duplicate Git tree entry")
        found.add(path)
        if any(fnmatchcase(path, pattern) for pattern in RELEASE_PATHS):
            selected[path] = (mode, kind, sha)
    if "skills" not in found or ".github/workflows/skills-release.yml" not in selected:
        raise ValueError("Git tree lacks required release inputs")
    return selected


def fetch_tree(repository, revision):
    result = subprocess.run(
        ["gh", "api", f"repos/{repository}/git/trees/{revision}?recursive=1"],
        capture_output=True, text=True, timeout=20, check=False,
    )
    if result.returncode:
        raise ValueError("GitHub could not supply the release input tree")
    return json.loads(result.stdout)


def may_publish(repository, packaged, current, fetch=fetch_tree):
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
        raise ValueError("Invalid repository")
    if not all(re.fullmatch(r"[0-9a-f]{40}", revision) for revision in (packaged, current)):
        raise ValueError("Release comparisons require full commit SHAs")
    if packaged == current:
        return True
    return inventory(fetch(repository, packaged)) == inventory(fetch(repository, current))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--packaged", required=True)
    parser.add_argument("--current", required=True)
    args = parser.parse_args()
    try:
        publish = may_publish(args.repository, args.packaged, args.current)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        print("Cannot verify current release inputs; publication is blocked.", file=sys.stderr)
        return 1
    print(f"publish={str(publish).lower()}")
    print("reason=" + ("Release inputs match current main." if publish else
                       "Release inputs changed; their qualifying main push schedules a replacement."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
