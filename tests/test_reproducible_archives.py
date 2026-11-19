import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("packages", ROOT / "scripts/verify-skill-packages.py")
packages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packages)


class ReproducibleArchives(unittest.TestCase):
    def test_checkout_time_does_not_change_any_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = shutil.copytree(ROOT / "skills", root / "skills")
            digests = []
            for timestamp in (1000000000, 1700000000):
                for file in source.rglob("*"):
                    os.utime(file, (timestamp, timestamp))
                output = root / str(timestamp)
                packages.build_archives(source, output)
                self.assertEqual(packages.validate_release_archives(root, output), [])
                digests.append({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()})
            self.assertEqual(len(digests[0]), 6)
            self.assertEqual(digests[0], digests[1])
            with self.assertRaises(ValueError):
                packages.build_archives(source, output)
