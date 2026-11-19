"""Render the same nine-second motion study with pinned local renderers."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

SOURCE = Path(__file__).resolve().parent
FPS = 24
SECONDS = 9

# Both adapters call the same frame-indexed function. The only animated input is time.
REMOTION_ENTRY = """
import React from 'react';
import {Composition, registerRoot, useCurrentFrame, useVideoConfig} from 'remotion';
import './study.js';
function Film() {
  const frame=useCurrentFrame(), {width,height,fps}=useVideoConfig();
  const svg=globalThis.MotionStudy.filmFrame(frame/fps,width,height);
  return React.createElement('div',{dangerouslySetInnerHTML:{__html:svg}});
}
registerRoot(()=>React.createElement(Composition,{
  id:'EasingStudy',component:Film,width:WIDTH,height:HEIGHT,fps:FPS,durationInFrames:FRAMES
}));
"""
HYPERFRAMES_ENTRY = """<!doctype html>
<meta charset="utf-8"><style>*{box-sizing:border-box}body{margin:0}svg{display:block}</style>
<div id="film" data-composition-id="study" data-start="0" data-duration="9" data-width="WIDTH" data-height="HEIGHT" data-fps="FPS"></div>
<script src="gsap.min.js"></script><script src="study.js"></script>
<script>
const clock={time:0}, film=document.getElementById('film');
function draw(){film.innerHTML=MotionStudy.filmFrame(clock.time,WIDTH,HEIGHT);}
draw();
const timeline=gsap.timeline({paused:true});
timeline.to(clock,{time:9,duration:9,ease:'none',onUpdate:draw},0);
window.__timelines={study:timeline};
</script>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine", choices=["remotion", "hyperframes"])
    parser.add_argument("layout", choices=["landscape", "portrait"])
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--tools",
        type=Path,
        required=True,
        help="Directory containing npm-installed node_modules",
    )
    parser.add_argument(
        "--browser", type=Path, help="Optional installed Chrome headless shell"
    )
    args = parser.parse_args()
    width, height = (1280, 720) if args.layout == "landscape" else (720, 1280)
    modules = args.tools.resolve() / "node_modules"
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        parser.error("Choose a new output path to preserve previous renders.")
    env = {
        **os.environ,
        "DO_NOT_TRACK": "1",
        "HYPERFRAMES_NO_TELEMETRY": "1",
        "HYPERFRAMES_NO_UPDATE_CHECK": "1",
    }
    with tempfile.TemporaryDirectory(
        prefix="motion-render-", dir=output.parent
    ) as temp:
        work = Path(temp)
        shutil.copy2(SOURCE / "study.js", work / "study.js")
        if args.engine == "remotion":
            # The bundler resolves peer dependencies relative to its input project.
            (work / "node_modules").symlink_to(modules, target_is_directory=True)
            entry = work / "entry.jsx"
            template = REMOTION_ENTRY
            command = [
                modules / ".bin/remotion",
                "render",
                "entry.jsx",
                "EasingStudy",
                "film.mp4",
                "--concurrency=1",
                "--codec=h264",
                "--crf=17",
                "--log=error",
            ]
            if args.browser:
                command.append("--browser-executable=" + str(args.browser.resolve()))
        else:
            entry = work / "index.html"
            template = HYPERFRAMES_ENTRY
            shutil.copy2(modules / "gsap/dist/gsap.min.js", work / "gsap.min.js")
            command = [
                modules / ".bin/hyperframes",
                "render",
                ".",
                "--output",
                "film.mp4",
                "--fps",
                str(FPS),
                "--quality",
                "looks",
                "--workers",
                "1",
            ]
            if args.browser:
                env["HYPERFRAMES_BROWSER_PATH"] = str(args.browser.resolve())
        entry.write_text(
            template.replace("WIDTH", str(width))
            .replace("HEIGHT", str(height))
            .replace("FPS", str(FPS))
            .replace("FRAMES", str(SECONDS * FPS))
        )
        started = time.monotonic()
        subprocess.run(command, cwd=work, env=env, check=True)
        elapsed = time.monotonic() - started
        probe = json.loads(
            subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_streams",
                    "-show_format",
                    "-of",
                    "json",
                    work / "film.mp4",
                ]
            )
        )
        stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
        if (stream["width"], stream["height"], int(stream["nb_frames"])) != (
            width,
            height,
            SECONDS * FPS,
        ):
            raise ValueError("Unexpected render geometry or frame count")
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-xerror",
                "-i",
                str(work / "film.mp4"),
                "-f",
                "null",
                "-",
            ],
            check=True,
        )
        shutil.move(work / "film.mp4", output)
        print(
            json.dumps(
                {
                    "engine": args.engine,
                    "layout": args.layout,
                    "render_seconds": round(elapsed, 2),
                    "width": width,
                    "height": height,
                    "frames": int(stream["nb_frames"]),
                    "codec": stream["codec_name"],
                    "bytes": output.stat().st_size,
                }
            )
        )


if __name__ == "__main__":
    main()
