"""Regression cases for broken installation payloads, not motion-quality scores."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/verify-skill-packages.py"
SPEC = importlib.util.spec_from_file_location("verify_skill_packages", SCRIPT)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class PayloadTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="motion-package-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.folder = self.root / "motion-director"
        self.folder.mkdir()
        self.entry = self.folder / "SKILL.md"
        self.header = "---\nname: motion-director\ndescription: Use for motion direction.\n---\n"
        self.entry.write_text(self.header, encoding="utf-8")
        self.required = self.folder / "references/motion-quality-rubric.md"
        self.required.parent.mkdir()
        self.required.write_text("Required rubric", encoding="utf-8")

    def link(self, target):
        self.entry.write_text(self.header + f"[Required reference]({target})\n", encoding="utf-8")

    def test_standalone_reference_survives(self):
        reference = self.folder / "references/rubric.md"
        reference.parent.mkdir(exist_ok=True)
        reference.write_text("Rubric", encoding="utf-8")
        self.link("references/rubric.md#purpose")
        self.assertEqual(CHECK.validate_payload(self.folder), [])

    def test_repo_file_cannot_mask_missing_install_reference(self):
        (self.root / "rubric.md").write_text("Outside installed folder", encoding="utf-8")
        self.link("references/rubric.md")
        self.assertTrue(any("missing reference" in e for e in CHECK.validate_payload(self.folder)))

    def test_parent_escape_is_rejected_even_if_file_exists(self):
        (self.root / "rubric.md").write_text("Outside installed folder", encoding="utf-8")
        self.link("../rubric.md")
        self.assertTrue(any("escapes skill" in e for e in CHECK.validate_payload(self.folder)))

    def test_encoded_parent_escape_is_rejected(self):
        self.link("%2e%2e/rubric.md")
        self.assertTrue(any("escapes skill" in e for e in CHECK.validate_payload(self.folder)))

    def test_machine_specific_reference_is_rejected(self):
        self.link("/private/operator/rubric.md")
        self.assertTrue(any("non-portable" in e for e in CHECK.validate_payload(self.folder)))

    def test_external_documentation_is_not_a_local_dependency(self):
        self.link("https://agentskills.io/specification")
        self.assertEqual(CHECK.validate_payload(self.folder), [])

    def test_invalid_name_is_rejected(self):
        self.entry.write_text(self.header.replace("name: motion-director", "name: another-skill"), encoding="utf-8")
        self.assertTrue(any("invalid skill name" in e for e in CHECK.validate_payload(self.folder)))

    def test_required_reference_is_checked_without_a_markdown_link(self):
        self.required.unlink()
        self.assertTrue(any("missing required reference" in e for e in CHECK.validate_payload(self.folder)))

    def test_reference_drift_is_rejected(self):
        skill_root = self.root / "skills"
        for name in CHECK.SKILLS:
            folder = skill_root / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Use for motion.\n---\n", encoding="utf-8")
        for bundle, source in CHECK.BUNDLED_REFERENCES.items():
            packaged, canonical = skill_root / bundle, self.root / source
            packaged.parent.mkdir(parents=True, exist_ok=True)
            canonical.parent.mkdir(parents=True, exist_ok=True)
            packaged.write_text("Canonical reference", encoding="utf-8")
            canonical.write_text("Canonical reference", encoding="utf-8")
        self.assertEqual(CHECK.validate_repository(self.root), [])
        (skill_root / next(iter(CHECK.BUNDLED_REFERENCES))).write_text("Stale copy", encoding="utf-8")
        self.assertTrue(any("differs from canonical" in e for e in CHECK.validate_repository(self.root)))


class ReleaseArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="motion-release-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.archives = self.root / "dist"
        self.archives.mkdir()
        for name in CHECK.SKILLS:
            folder = self.root / "skills" / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Use for motion.\n---\n", encoding="utf-8")
        for bundle in CHECK.BUNDLED_REFERENCES:
            file = self.root / "skills" / bundle
            file.parent.mkdir(exist_ok=True)
            file.write_text("Required reference", encoding="utf-8")
        for name in CHECK.SKILLS | {"all-skills"}:
            self.package(name)

    def package(self, name, omit=None, change=None):
        names = CHECK.SKILLS if name == "all-skills" else {name}
        with zipfile.ZipFile(self.archives / f"{name}.zip", "w") as archive:
            for skill in sorted(names):
                for file in (self.root / "skills" / skill).rglob("*"):
                    if file.is_file():
                        relative = file.relative_to(self.root / "skills").as_posix()
                        if relative != omit:
                            archive.writestr(relative, b"Changed" if relative == change else file.read_bytes())

    def errors(self):
        return CHECK.validate_release_archives(self.root, self.archives)

    def test_complete_individual_and_combined_archives_match(self):
        self.assertEqual(self.errors(), [])

    def test_reference_missing_from_actual_archive_is_rejected(self):
        self.package("motion-director", omit="motion-director/references/motion-quality-rubric.md")
        self.assertTrue(any("payload differs" in error for error in self.errors()))

    def test_modified_archive_content_is_rejected(self):
        self.package("all-skills", change="motion-director/SKILL.md")
        self.assertTrue(any("content differs" in error for error in self.errors()))

    def test_path_traversal_is_rejected_without_extracting(self):
        with zipfile.ZipFile(self.archives / "motion-director.zip", "a") as archive:
            archive.writestr("../outside.txt", "Unsafe")
        self.assertTrue(any("unsafe member path" in error for error in self.errors()))
        self.assertFalse((self.root / "outside.txt").exists())

    def test_duplicate_paths_are_rejected(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.archives / "motion-director.zip", "a") as archive:
                archive.writestr("motion-director/SKILL.md", "Different duplicate")
        self.assertTrue(any("duplicate member" in error for error in self.errors()))

    def test_symlink_member_is_rejected(self):
        info = zipfile.ZipInfo("motion-director/link")
        info.create_system = 3
        info.external_attr = 0o120777 << 16
        with zipfile.ZipFile(self.archives / "motion-director.zip", "a") as archive:
            archive.writestr(info, "../../outside")
        self.assertTrue(any("non-regular member" in error for error in self.errors()))

    def test_missing_archive_is_rejected(self):
        (self.archives / "web-motion-auditor.zip").unlink()
        self.assertTrue(any("archive inventory differs" in error for error in self.errors()))


if __name__ == "__main__":
    unittest.main()
