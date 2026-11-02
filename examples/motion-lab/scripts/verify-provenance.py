"""Validate every rendered asset's companion against the pinned VIS schema."""
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

root = Path(__file__).resolve().parents[1]
schema = json.loads((root / "schemas/vis-provenance-sidecar.schema.json").read_text())
validator = Draft202012Validator(schema, format_checker=FormatChecker())
count = 0
for asset in (root / "output").rglob("*"):
    if not asset.is_file() or asset.suffix not in {".png", ".mp4"}:
        continue
    sidecar = Path(str(asset) + ".vis.provenance.json")
    record = json.loads(sidecar.read_text())
    validator.validate(record)
    assert record["asset"]["sha256"] == hashlib.sha256(asset.read_bytes()).hexdigest(), asset
    assert record["generation"]["prompt"], asset
    count += 1
assert count >= 2, "No verified video/poster outputs were found."
print(f"PASS: {count} assets have schema-valid provenance and matching hashes.")
