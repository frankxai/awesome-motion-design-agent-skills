#!/usr/bin/env python3
"""Refresh the "N★" counts in README tables from the GitHub API.

Counts were typed by hand and drifted. This rewrites each count from the
repository linked in the same row, then re-pads only the tables it touched so
awesome-lint's table-pipe-alignment rule keeps passing.

Usage:
  GITHUB_TOKEN=... python3 scripts/update-stars.py          # rewrite README.md
  GITHUB_TOKEN=... python3 scripts/update-stars.py --dry-run
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

REPO_LINK = re.compile(r"\]\(https://github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?/?\)")
STAR_CELL = re.compile(r"(?<![\w.])\d+(?:\.\d+)?k?★")


def format_stars(count):
    if count < 1000:
        return f"{count}★"
    if count < 100_000:
        return f"{count / 1000:.1f}".rstrip("0").rstrip(".") + "k★"
    return f"{round(count / 1000)}k★"


def split_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(cells):
    return all(re.fullmatch(r":?-+:?", cell) for cell in cells)


def align_table(lines):
    """Rebuild a pipe table with every column padded to its widest cell."""
    rows = [split_row(line) for line in lines]
    widths = [max(len(row[i]) for row in rows if not is_separator(row)) for i in range(len(rows[0]))]
    widths = [max(width, 3) for width in widths]
    out = []
    for row in rows:
        if is_separator(row):
            cells = []
            for cell, width in zip(row, widths):
                left, right = cell.startswith(":"), cell.endswith(":")
                cells.append((":" if left else "-") + "-" * (width - 2) + (":" if right else "-"))
        else:
            cells = [cell.ljust(width) for cell, width in zip(row, widths)]
        out.append("| " + " | ".join(cells) + " |")
    return out


def rewrite(text, lookup):
    """Return (new_text, changes). lookup(owner, repo) -> int or None."""
    lines = text.split("\n")
    changes, touched = [], set()
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|") or "★" not in line:
            continue
        link = REPO_LINK.search(line)
        if not link:
            continue
        count = lookup(link.group(1), link.group(2))
        if count is None:
            continue
        new_cell = format_stars(count)
        new_line, n = STAR_CELL.subn(new_cell, line, count=1)
        if n and new_line != line:
            old_cell = STAR_CELL.search(line).group(0)
            changes.append(f"{link.group(1)}/{link.group(2)}: {old_cell} -> {new_cell}")
            lines[i] = new_line
            touched.add(i)

    # Re-align each contiguous table block that had a changed row.
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            start = i
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                i += 1
            if touched & set(range(start, i)):
                lines[start:i] = align_table(lines[start:i])
        else:
            i += 1
    return "\n".join(lines), changes


def github_lookup(token):
    cache = {}

    def lookup(owner, repo):
        key = f"{owner}/{repo}".lower()
        if key not in cache:
            request = urllib.request.Request(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers={"Accept": "application/vnd.github+json", "User-Agent": "awesome-list-star-refresh",
                         **({"Authorization": f"Bearer {token}"} if token else {})},
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    cache[key] = json.load(response)["stargazers_count"]
            except urllib.error.HTTPError as error:
                # A moved or deleted repo keeps its old count; the link checker reports the dead link.
                print(f"warn: {owner}/{repo}: HTTP {error.code}, count left unchanged", file=sys.stderr)
                cache[key] = None
        return cache[key]

    return lookup


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="README.md")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # "★" crashes the default Windows console codec
    path = Path(args.file)
    new_text, changes = rewrite(path.read_text(encoding="utf-8"), github_lookup(os.environ.get("GITHUB_TOKEN")))
    print("\n".join(changes) or "No star counts changed.")
    if changes and not args.dry_run:
        path.write_text(new_text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
