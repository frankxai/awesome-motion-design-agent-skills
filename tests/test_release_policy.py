import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_policy", ROOT / "scripts/release-policy.py")
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class ReleasePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Release fixture")
        self.write("skills/example/SKILL.md", "original skill")
        self.write("skills/other/SKILL.md", "another skill")
        self.write(".github/workflows/skills-release.yml", "release workflow")
        self.write("README.md", "original readme")
        self.base = self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True,
                                       stderr=subprocess.PIPE).strip()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def fetch(self, repository, revision):
        entries = []
        for record in self.git("ls-tree", "-r", "-t", revision).splitlines():
            metadata, path = record.split("\t", 1)
            mode, kind, sha = metadata.split()
            entries.append({"path": path, "mode": mode, "type": kind, "sha": sha})
        return {"truncated": False, "tree": entries}

    def test_readme_only_commit_does_not_drop_packaged_release(self):
        self.write("README.md", "new discovery copy")
        current = self.commit()
        self.assertTrue(policy.may_publish("fixture/repo", self.base, current, self.fetch))

    def test_changed_release_inputs_supersede_old_package(self):
        for path in policy.RELEASE_PATHS:
            with self.subTest(path=path):
                self.git("reset", "--hard", self.base)
                self.write(path.replace("**", "nested/changed.txt"), "changed release input")
                self.assertFalse(policy.may_publish("fixture/repo", self.base, self.commit(), self.fetch))

    def test_removal_supersedes_old_package(self):
        (self.root / "skills/example/SKILL.md").unlink()
        self.assertFalse(policy.may_publish("fixture/repo", self.base, self.commit(), self.fetch))

    def test_same_revision_needs_no_api(self):
        with patch.object(policy, "fetch_tree") as fetch:
            self.assertTrue(policy.may_publish("fixture/repo", self.base, self.base, fetch))
            fetch.assert_not_called()

    def test_incomplete_or_malformed_api_data_blocks_publication(self):
        valid = self.fetch("fixture/repo", self.base)
        bad_entry = copy.deepcopy(valid)
        bad_entry["tree"][0]["sha"] = "invalid"
        duplicate = copy.deepcopy(valid)
        duplicate["tree"].append(duplicate["tree"][0])
        bad_mode = copy.deepcopy(valid)
        bad_mode["tree"][0].update(mode="invalid", type=None)
        for response in ({"truncated": True, "tree": valid["tree"]}, {"tree": []},
                         {"truncated": False, "tree": []}, bad_entry, duplicate, bad_mode):
            with self.subTest(response=response), self.assertRaises(ValueError):
                policy.inventory(response)

    def test_file_mode_changes_are_release_changes(self):
        self.git("update-index", "--chmod=+x", "skills/example/SKILL.md")
        self.git("commit", "-qm", "change file mode")
        current = self.git("rev-parse", "HEAD")
        self.assertFalse(policy.may_publish("fixture/repo", self.base, current, self.fetch))

    def test_invalid_identity_is_rejected_before_fetch(self):
        for repository, revision in (("fixture/repo?other=1", self.base), ("fixture/repo", "main")):
            with self.subTest(repository=repository), self.assertRaises(ValueError):
                policy.may_publish(repository, revision, self.base, self.fetch)

    def test_api_failure_is_not_a_successful_skip(self):
        with patch.object(policy.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "")):
            with self.assertRaises(ValueError):
                policy.fetch_tree("fixture/repo", self.base)

    def test_push_filter_schedules_every_superseding_input(self):
        workflow = (ROOT / ".github/workflows/skills-release.yml").read_text(encoding="utf-8")
        paths = json.loads(re.search(r"    paths: (\[.*\])", workflow).group(1))
        self.assertEqual(set(paths), set(policy.RELEASE_PATHS))


if __name__ == "__main__":
    unittest.main()
