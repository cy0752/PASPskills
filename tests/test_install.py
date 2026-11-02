"""Filesystem regressions for project installation; no external tools/jobs run."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
INSTALLER = REPO / "scripts/install-pasp-skills.sh"


def inventory(root: Path) -> dict[str, tuple[str, bool]]:
    return {
        str(p.relative_to(root)): (
            hashlib.sha256(p.read_bytes()).hexdigest(),
            bool(p.stat().st_mode & 0o111),
        )
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


class InstallerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pasp installer ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "target project"
        self.env = dict(os.environ, CLAUDE_SKILLS_DIR=str(self.root / "user skills"))

    def install(self, *args, source=REPO, target=None):
        return subprocess.run(
            ["bash", str(INSTALLER), "--source", str(source), *args,
             str(target or self.project)],
            cwd=self.root, env=self.env, text=True, capture_output=True,
        )

    def assert_entries(self):
        expected = (self.project / "skills/SKILL.md").read_bytes()
        for path in (".agents/skills/pasp-helper", ".codex/skills/pasp-helper",
                     ".claude/skills/pasp-helper"):
            self.assertEqual((self.project / path / "SKILL.md").read_bytes(), expected)
        wrapper = self.project / ".agents/skills/pasp-verifier/SKILL.md"
        self.assertIn("skills/subskills/pasp-verifier/skill.md", wrapper.read_text())
        self.assertEqual(
            (self.project / ".codex/skills/pasp-verifier/SKILL.md").read_bytes(),
            wrapper.read_bytes(),
        )
        for path in (".codex/agents/pasp-verifier.toml", ".claude/agents/pasp-verifier.md"):
            self.assertTrue((self.project / path).is_file())

    def test_symlink_install_discovers_all_project_entries(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / "skills").is_symlink())
        self.assertEqual((self.project / "skills").resolve(), REPO / "skills")
        self.assert_entries()

    def test_copy_install_preserves_bytes_and_executable_modes(self):
        result = self.install("--copy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / "skills").is_symlink())
        self.assertEqual(inventory(REPO / "skills"), inventory(self.project / "skills"))
        self.assert_entries()

    def test_source_symlink_copy_is_independent(self):
        source = self.root / "linked source"
        source.symlink_to(REPO / "skills", target_is_directory=True)
        result = self.install("--copy", source=source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / "skills").is_symlink())
        source.unlink()
        self.assertEqual(inventory(REPO / "skills"), inventory(self.project / "skills"))
        self.assert_entries()

    def test_copied_project_survives_relocation_and_source_removal(self):
        source = self.root / "temporary source"
        source.mkdir()
        (source / "SKILL.md").write_text("self-contained source")
        (source / "knowledge").mkdir()
        (source / "subskills").mkdir()
        (source / "subskills/pasp-verifier").mkdir()
        (source / "subskills/pasp-verifier/skill.md").write_text("verifier contract")
        result = self.install("--copy", source=source)
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = inventory(source)
        source.rename(self.root / "unavailable source")
        relocated = self.root / "relocated project"
        self.project.rename(relocated)
        self.project = relocated
        self.assertEqual(inventory(self.project / "skills"), expected)
        self.assert_entries()
        self.assertEqual(
            (self.project / "skills/subskills/pasp-verifier/skill.md").read_text(),
            "verifier contract",
        )

    def test_force_upgrade_from_symlink_to_copy_and_cleanup(self):
        self.assertEqual(self.install().returncode, 0)
        for area in (".agents/skills", ".codex/skills", ".claude/skills"):
            for name in ("pasp-dev", "paspskills", "unrelated-skill"):
                p = self.project / area / name
                p.mkdir()
                (p / "keep.txt").write_text("old entry")
        result = self.install("--force", "--copy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / "skills").is_symlink())
        for area in (".agents/skills", ".codex/skills", ".claude/skills"):
            self.assertFalse((self.project / area / "pasp-dev").exists())
            self.assertFalse((self.project / area / "paspskills").exists())
            self.assertEqual((self.project / area / "unrelated-skill/keep.txt").read_text(),
                             "old entry")
        self.assert_entries()

    def test_no_force_conflict_preserves_existing_discovery_entry(self):
        existing = self.project / ".agents/skills/pasp-helper"
        existing.mkdir(parents=True)
        marker = existing / "SKILL.md"
        marker.write_text("user content")
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to overwrite", result.stderr)
        self.assertEqual(marker.read_text(), "user content")
        self.assertFalse((self.project / "skills").exists())

    def source_fixture(self, relative):
        source = self.project / relative
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("source must survive")
        (source / "knowledge").mkdir()
        (source / "subskills").mkdir()
        return source

    def test_same_source_force_is_rejected_before_deletion(self):
        source = self.source_fixture("skills")
        before = inventory(source)
        result = self.install("--force", "--copy", source=source)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Source skills are inside the destination", result.stderr)
        self.assertEqual(inventory(source), before)
        self.assertFalse((self.project / ".agents").exists())

    def test_nested_source_force_is_rejected_before_deletion(self):
        source = self.source_fixture("skills/nested source")
        before = inventory(source)
        result = self.install("--force", source=source)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(inventory(source), before)


if __name__ == "__main__":
    unittest.main()
