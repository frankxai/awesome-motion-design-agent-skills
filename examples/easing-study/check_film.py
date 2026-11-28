"""Independently measure the encoded distance marker at scene boundaries and in motion."""

import argparse
import json
from pathlib import Path
import subprocess

from PIL import Image
from io import BytesIO

FRAMES = (
    0,
    18,
    24,
    32,
    41,
    71,
    72,
    90,
    96,
    104,
    113,
    143,
    144,
    162,
    168,
    176,
    185,
    215,
)


def measure(path):
    metadata = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_streams",
                "-of",
                "json",
                path,
            ]
        )
    )["streams"][0]
    width, height = metadata["width"], metadata["height"]
    assert (width, height) in {(1280, 720), (720, 1280)}
    assert int(metadata["nb_frames"]) == 216 and metadata["avg_frame_rate"] == "24/1"
    y, pad = (1162, 50) if height > width else (627, 68)
    errors = []
    for frame in FRAMES:
        png = subprocess.check_output(
            [
                "ffmpeg",
                "-v",
                "error",
                "-ss",
                str(frame / 24),
                "-i",
                path,
                "-frames:v",
                "1",
                "-c:v",
                "png",
                "-f",
                "image2pipe",
                "-",
            ]
        )
        with Image.open(BytesIO(png)) as image:
            row = [image.getpixel((x, y))[:3] for x in range(width)]
        marker = [
            x for x, (r, g, b) in enumerate(row) if r > 215 and 95 < g < 180 and b < 145
        ]
        if not marker:
            raise ValueError(f"Missing encoded distance marker at frame {frame}")
        observed = (marker[0] + marker[-1]) / 2
        t = max(0, min(1, (frame % 72) / 24 - 0.72))
        expected = (t, 1 - (1 - t) ** 3, t * t * (3 - 2 * t))[frame // 72]
        error = abs(observed - (pad + (width - 2 * pad) * expected))
        errors.append(error)
        if error > 3:
            raise ValueError(
                f"Marker at frame {frame} is {error:.2f} pixels from requested position"
            )
    return {
        "file": path.name,
        "decoded_samples": len(FRAMES),
        "max_error_px": round(max(errors), 2),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("films", type=Path, nargs="+")
    print(json.dumps([measure(path) for path in parser.parse_args().films], indent=2))
