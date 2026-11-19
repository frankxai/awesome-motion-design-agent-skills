"""Check Claude Code slash-command expansion using only a loopback Messages fixture."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import threading
from urllib.parse import urlsplit

ANSWER = "dispatch-fixture-complete"
PROMPT = "Report the probe result."


def sse_response():
    """One inert assistant turn, with no tool calls or generated assessment."""
    message = {"id": "msg_fixture", "type": "message", "role": "assistant",
               "model": "local-fixture", "content": [], "stop_reason": None,
               "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 0}}
    events = [
        ("message_start", {"message": message}),
        ("content_block_start", {"index": 0, "content_block": {"type": "text", "text": ""}}),
        ("content_block_delta", {"index": 0, "delta": {"type": "text_delta", "text": ANSWER}}),
        ("content_block_stop", {"index": 0}),
        ("message_delta", {"delta": {"stop_reason": "end_turn", "stop_sequence": None},
                           "usage": {"output_tokens": 1}}),
        ("message_stop", {}),
    ]
    return "".join(f"event: {event}\ndata: {json.dumps({'type': event, **fields})}\n\n"
                   for event, fields in events).encode()


class MessagesFixture(BaseHTTPRequestHandler):
    def log_message(self, *args):
        # Request headers, full model requests and runtime environment stay out of receipts.
        pass

    def do_POST(self):
        if urlsplit(self.path).path != "/v1/messages":
            self.send_error(404)
            return
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        texts = [block["text"] for message in payload["messages"]
                 for block in message["content"] if isinstance(block, dict) and block.get("type") == "text"]
        matched = [name for name, body in self.server.bodies.items()
                   if any(body in text for text in texts)]
        self.server.observations.append(sorted(matched))
        data = sse_response()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def resolve_cli(value):
    return str(Path(value).absolute()) if os.sep in value else value


def run(command, cwd, env):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=35)
    if result.returncode:
        raise RuntimeError(f"{Path(command[0]).name} exited {result.returncode}")
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--skills-cli", default="skills")
    parser.add_argument("--claude", default="claude")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cli, claude = resolve_cli(args.skills_cli), resolve_cli(args.claude)
    with tempfile.TemporaryDirectory(prefix="skill-dispatch-") as scratch:
        root = Path(scratch)
        project, source, profile = [root / name for name in ("project", "source", "profile")]
        for directory in (project, source, profile):
            directory.mkdir()
        # The child receives no inherited credentials or user settings. The placeholder is
        # accepted only by this local HTTP fixture. No provider SDK or proxy forwards requests.
        env = {"HOME": str(profile), "PATH": os.environ["PATH"], "CI": "1", "NO_COLOR": "1",
               "DO_NOT_TRACK": "1", "DISABLE_TELEMETRY": "1", "DISABLE_AUTOUPDATER": "1",
               "DISABLE_ERROR_REPORTING": "1", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}
        revision = run(["git", "rev-parse", "--verify", f"{args.commit}^{{commit}}"], args.repo, env)
        with (root / "skills.tar").open("wb") as output:
            subprocess.run(["git", "archive", revision, "skills"], cwd=args.repo,
                           env=env, stdout=output, check=True, timeout=20)
        with tarfile.open(root / "skills.tar") as archive:
            archive.extractall(source, filter="data")
        bodies = {file.parent.name: file.read_text().split("---", 2)[2].strip()
                  for file in sorted((source / "skills").glob("*/SKILL.md"))}
        if not bodies or not all(bodies.values()):
            raise ValueError("No complete tracked skill bodies found")
        run(["git", "init", "-q"], project, env)
        cli_version = run([cli, "--version"], project, env)
        runtime_version = run([claude, "--version"], project, env)
        run([cli, "add", str(source), "--skill", "*", "--agent", "claude-code", "--yes"], project, env)
        rows = []
        with ThreadingHTTPServer(("127.0.0.1", 0), MessagesFixture) as server:
            server.bodies = bodies
            server.observations = []
            local = f"http://127.0.0.1:{server.server_port}"
            env.update(ANTHROPIC_BASE_URL=local, ANTHROPIC_API_KEY="local-fixture-only",
                       HTTP_PROXY=local, HTTPS_PROXY=local, NO_PROXY="127.0.0.1,localhost")
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                for name in [None, *bodies]:
                    before = len(server.observations)
                    prompt = f"/{name} {PROMPT}" if name else PROMPT
                    answer = run([claude, "-p", "--setting-sources", "project", "--strict-mcp-config",
                                  "--tools", "", "--no-session-persistence", "--model", "sonnet",
                                  prompt], project, env)
                    matches = server.observations[before:]
                    expected = [[name]] if name else [[]]
                    rows.append({"command": f"/{name}" if name else None,
                                 "completeBodiesPerRequest": matches,
                                 "passed": answer == ANSWER and matches == expected})
            finally:
                server.shutdown()
                worker.join(timeout=5)
        receipt = {"sourceRevision": revision, "runtime": runtime_version, "installer": cli_version,
                   "transport": "loopback HTTP Messages fixture, synthetic SSE response",
                   "comparison": "complete Markdown body after removing frontmatter and outer whitespace",
                   "bodySha256": {name: hashlib.sha256(body.encode()).hexdigest()
                                  for name, body in bodies.items()}, "runs": rows}
        args.output.write_text(json.dumps(receipt, indent=2) + "\n")
        if not all(row["passed"] for row in rows):
            raise SystemExit("Explicit dispatch mismatch; inspect the receipt.")


if __name__ == "__main__":
    main()
