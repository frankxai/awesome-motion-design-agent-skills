"""Measure project-scoped native discovery before installation, after it, and after removal."""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile


def run(command, *, cwd, env, stdin=None):
    result = subprocess.run(command, cwd=cwd, env=env, input=stdin, text=True,
                            capture_output=True, check=True, timeout=45)
    return result.stdout.strip()


async def codex_skills(executable, project, env):
    proc = await asyncio.create_subprocess_exec(
        executable, "app-server", "--stdio", cwd=project, env=env,
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL, limit=2**22,
    )

    async def request(request_id, method, params):
        message = {"id": request_id, "jsonrpc": "2.0", "method": method, "params": params}
        proc.stdin.write(json.dumps(message).encode() + b"\n")
        await proc.stdin.drain()
        while line := await proc.stdout.readline():
            response = json.loads(line)
            if response.get("id") == request_id:
                if "error" in response:
                    raise RuntimeError(response["error"])
                return response["result"]
        raise RuntimeError("Native discovery server closed its response stream")

    try:
        await asyncio.wait_for(request(1, "initialize", {"clientInfo": {
            "name": "skill-discovery", "version": "1"}}), timeout=20)
        proc.stdin.write(b'{"jsonrpc":"2.0","method":"initialized"}\n')
        await proc.stdin.drain()
        result = await asyncio.wait_for(request(2, "skills/list", {
            "cwds": [str(project)], "forceReload": True}), timeout=25)
        entry, = result["data"]
        if entry["errors"]:
            raise RuntimeError("Native Codex skill scan reported errors")
        return {row["name"]: Path(row["path"]) for row in entry["skills"]
                if row["enabled"] and row["scope"] == "repo"}
    finally:
        if proc.returncode is None:
            proc.kill()
        await proc.wait()


def claude_skills(executable, project, env):
    data = run([executable, "-p", "--setting-sources", "project", "--strict-mcp-config",
                "--tools", "", "--verbose", "--no-session-persistence", "--output-format",
                "stream-json", "--input-format", "stream-json"], cwd=project, env=env,
               stdin='{"type":"control_request","request_id":"probe","request":{"subtype":"initialize"}}\n')
    for row in map(json.loads, data.splitlines()):
        if row["type"] != "control_response":
            continue
        response = row["response"]
        if response["request_id"] == "probe" and response["subtype"] == "success":
            # Claude exposes command names. Resolve each candidate below in the isolated install.
            return {cmd["name"]: project / ".claude/skills" / cmd["name"] / "SKILL.md"
                    for cmd in response["response"]["commands"] if not cmd.get("builtin")}
    raise RuntimeError("No successful Claude initialize response")


def observe(args, project, env, source):
    if args.target == "codex":
        entries = asyncio.run(codex_skills(args.runtime, project, env))
    elif args.target == "claude-code":
        entries = claude_skills(args.runtime, project, env)
    else:
        data = run([args.runtime, "debug", "skill", "--pure"], cwd=project, env=env)
        entries = {}
        for row in json.loads(data):
            if row["name"] not in source:
                continue
            file = Path(row["location"])
            if not file.resolve().is_relative_to(project):
                raise ValueError("OpenCode returned a skill outside the isolated project")
            body = file.read_text().split("---", 2)[2]
            if row["content"].strip() != body.strip():
                raise ValueError(f"{row['name']}: native skill content differs")
            entries[row["name"]] = file
    discovered = []
    for name in sorted(entries.keys() & source.keys()):
        file = entries[name]
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        if not file.resolve().is_relative_to(project) or digest != source[name]:
            raise ValueError(f"{name}: entrypoint does not match isolated source")
        discovered.append({"name": name, "entrypoint": file.relative_to(project).as_posix(),
                           "sha256": digest})
    return discovered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--skills-cli", required=True, help="Installed skills executable")
    parser.add_argument("--target", choices=["claude-code", "codex", "opencode"], required=True)
    parser.add_argument("--runtime", required=True, help="Installed native runtime executable")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for name in ("skills_cli", "runtime"):
        value = getattr(args, name)
        if os.sep in value:
            setattr(args, name, str(Path(value).absolute()))
    repo = args.repo.resolve()
    with tempfile.TemporaryDirectory(prefix="skill-discovery-") as temp:
        root = Path(temp)
        for folder in ("home", "codex-home", "project", "source"):
            (root / folder).mkdir()
        # No provider credentials, inherited agent profiles or user prompts are supplied.
        env = {"PATH": os.environ["PATH"], "HOME": str(root / "home"),
               "CODEX_HOME": str(root / "codex-home"), "DISABLE_TELEMETRY": "1",
               "DO_NOT_TRACK": "1", "CI": "1", "NO_COLOR": "1",
               "OPENCODE_DISABLE_MODELS_FETCH": "1", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}
        project = root / "project"
        revision = run(["git", "rev-parse", "--verify", f"{args.commit}^{{commit}}"], cwd=repo, env=env)
        with (root / "source.tar").open("wb") as archive:
            subprocess.run(["git", "archive", revision, "skills"], cwd=repo, env=env,
                           stdout=archive, check=True, timeout=20)
        with tarfile.open(root / "source.tar") as archive:
            archive.extractall(root / "source", filter="data")
        source = {p.parent.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (root / "source/skills").glob("*/SKILL.md")}
        if not source:
            raise ValueError("No source entrypoints found")
        run(["git", "init", "-q"], cwd=project, env=env)
        # Codex treats this newly created, test-only repository as trusted.
        (root / "codex-home/config.toml").write_text(
            f'[projects.{json.dumps(str(project))}]\ntrust_level="trusted"\n')
        runtime_version = run([args.runtime, "--version"], cwd=project, env=env)
        cli_version = run([args.skills_cli, "--version"], cwd=project, env=env)
        before = observe(args, project, env, source)
        run([args.skills_cli, "add", str(root / "source"), "--agent", args.target,
             "--skill", "*", "--yes"], cwd=project, env=env)
        installed = observe(args, project, env, source)
        run([args.skills_cli, "remove", *sorted(source), "--agent", args.target, "--yes"],
            cwd=project, env=env)
        removed = [r["name"] for r in observe(args, project, env, source)]
        final = removed
        if removed:
            # The check owns this entire project. Unscoped removal can affect other agents.
            for name in removed:
                run([args.skills_cli, "remove", name, "--yes"], cwd=project, env=env)
            final = [r["name"] for r in observe(args, project, env, source)]
        receipt = {"sourceRevision": revision, "target": args.target, "runtime": runtime_version,
                   "installerVersion": cli_version, "before": before, "installed": installed,
                   "afterTargetedRemoval": removed, "afterCleanup": final, "modelTurns": 0}
        args.output.write_text(json.dumps(receipt, indent=2) + "\n")
        if before or [r["name"] for r in installed] != sorted(source) or final:
            raise RuntimeError("Unexpected install, discovery or cleanup result. See output receipt.")
        if removed:
            raise SystemExit("Targeted removal left skills discoverable. See output receipt.")



if __name__ == "__main__":
    main()
