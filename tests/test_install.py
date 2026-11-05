"""Installation and migration filesystem regressions; no PASP/DFT jobs run."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
INSTALLER = REPO / "scripts/install-pasp-skills.sh"
PACKAGE = ".agents/skills/pasp-helper"
CONTRACT = f"{PACKAGE}/subskills/pasp-verifier/skill.md"


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
        package = self.project / PACKAGE
        expected = (package / "SKILL.md").read_bytes()
        self.assertEqual(
            (self.project / ".claude/skills/pasp-helper/SKILL.md").read_bytes(), expected
        )
        self.assertEqual((self.project / ".claude/skills/pasp-helper").resolve(), package.resolve())
        wrapper = self.project / ".agents/skills/pasp-verifier/SKILL.md"
        self.assertIn(CONTRACT, wrapper.read_text())
        self.assertTrue((self.project / CONTRACT).is_file())
        for path in (".codex/agents/pasp-verifier.toml", ".claude/agents/pasp-verifier.md"):
            self.assertIn(CONTRACT, (self.project / path).read_text())
        self.assertFalse((self.project / ".codex/skills/pasp-helper").exists())
        self.assertFalse((self.project / ".codex/skills/pasp-verifier").exists())

    def source_fixture(self, path):
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text("---\nname: pasp-helper\ndescription: fixture\n---\n")
        (path / "knowledge").mkdir()
        (path / "subskills/pasp-verifier").mkdir(parents=True)
        (path / "subskills/pasp-verifier/skill.md").write_text("verifier contract")
        script = path / "knowledge/check.sh"
        script.write_text("#!/bin/sh\nexit 0\n")
        script.chmod(0o755)
        return path

    def old_install(self, linked=False):
        self.project.mkdir()
        old = self.project / "skills"
        if linked:
            old.symlink_to(REPO / "skills", target_is_directory=True)
        else:
            shutil.copytree(REPO / "skills", old)
            (old / "user-customization.txt").write_text("must be backed up")
        for area in (".agents/skills", ".codex/skills", ".claude/skills"):
            folder = self.project / area
            folder.mkdir(parents=True)
            (folder / "pasp-helper").symlink_to("../../skills", target_is_directory=True)
        verifier = self.project / ".agents/skills/pasp-verifier"
        verifier.mkdir()
        (verifier / "SKILL.md").write_text("old verifier")
        (self.project / ".codex/skills/pasp-verifier").symlink_to(
            "../../.agents/skills/pasp-verifier", target_is_directory=True
        )
        return old

    def test_default_copy_is_clean_and_preserves_package(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / "skills").exists())
        self.assertFalse((self.project / ".codex/skills").exists())
        self.assertFalse((self.project / PACKAGE).is_symlink())
        self.assertEqual(inventory(REPO / "skills"), inventory(self.project / PACKAGE))
        self.assert_entries()

    def test_explicit_copy_remains_accepted(self):
        result = self.install("--copy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / PACKAGE).is_symlink())
        self.assert_entries()

    def test_explicit_link_targets_source_without_root_hop(self):
        result = self.install("--link")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / PACKAGE).is_symlink())
        self.assertEqual((self.project / PACKAGE).resolve(), REPO / "skills")
        self.assertFalse((self.project / "skills").exists())
        self.assert_entries()

    def test_source_symlink_copy_is_independent(self):
        source = self.root / "linked source"
        source.symlink_to(REPO / "skills", target_is_directory=True)
        result = self.install(source=source)
        self.assertEqual(result.returncode, 0, result.stderr)
        source.unlink()
        self.assertEqual(inventory(REPO / "skills"), inventory(self.project / PACKAGE))
        self.assert_entries()

    def test_copied_project_survives_relocation_and_source_removal(self):
        source = self.source_fixture(self.root / "temporary source")
        expected = inventory(source)
        result = self.install(source=source)
        self.assertEqual(result.returncode, 0, result.stderr)
        shutil.rmtree(source)
        relocated = self.root / "relocated project"
        self.project.rename(relocated)
        self.project = relocated
        self.assertEqual(inventory(self.project / PACKAGE), expected)
        self.assert_entries()

    def test_force_reinstall_preserves_unrelated_project_and_user_skills(self):
        self.assertEqual(self.install("--link").returncode, 0)
        for area in (".agents/skills", ".codex/skills", ".claude/skills"):
            folder = self.project / area / "unrelated-skill"
            folder.mkdir(parents=True)
            (folder / "keep.txt").write_text("unrelated")
        user_entry = Path(self.env["CLAUDE_SKILLS_DIR"]) / "pasp-helper"
        user_entry.mkdir(parents=True)
        (user_entry / "keep.txt").write_text("user entry")
        result = self.install("--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / PACKAGE).is_symlink())
        for area in (".agents/skills", ".codex/skills", ".claude/skills"):
            self.assertEqual((self.project / area / "unrelated-skill/keep.txt").read_text(), "unrelated")
        self.assertEqual((user_entry / "keep.txt").read_text(), "user entry")
        self.assert_entries()

    def test_force_copy_reinstall_and_link_switch(self):
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(self.install("--force").returncode, 0)
        result = self.install("--force", "--link")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / PACKAGE).is_symlink())
        self.assert_entries()

    def test_no_force_conflict_preserves_existing_discovery_entry(self):
        existing = self.project / PACKAGE
        existing.mkdir(parents=True)
        marker = existing / "SKILL.md"
        marker.write_text("user content")
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to overwrite", result.stderr)
        self.assertEqual(marker.read_text(), "user content")
        self.assertFalse((self.project / ".claude").exists())

    def test_unrelated_root_skills_is_not_touched(self):
        folder = self.project / "skills"
        folder.mkdir(parents=True)
        (folder / "user.txt").write_text("not a PASP install")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((folder / "user.txt").read_text(), "not a PASP install")
        self.assert_entries()

    def test_unrecognized_root_package_is_not_assumed_installer_owned(self):
        source = self.source_fixture(self.project / "skills")
        before = inventory(source)
        result = self.install("--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(inventory(source), before)
        self.assert_entries()

    def test_old_copied_root_is_backed_up_and_migrated(self):
        old = self.old_install()
        before = inventory(old)
        result = self.install("--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(old.exists())
        backups = list((self.project / ".agents/pasp-install-backups").glob("*/skills"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(inventory(backups[0]), before)
        self.assertIn("Migration backup:", result.stdout)
        self.assertFalse((self.project / PACKAGE / "user-customization.txt").exists())
        self.assert_entries()

    def test_old_symlink_root_is_unlinked_without_touching_source(self):
        old = self.old_install(linked=True)
        before = inventory(REPO / "skills")
        result = self.install("--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(old.is_symlink())
        self.assertFalse(old.exists())
        self.assertEqual(inventory(REPO / "skills"), before)
        self.assert_entries()

    def test_old_install_requires_force_before_any_migration(self):
        old = self.old_install()
        before = inventory(old)
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(inventory(old), before)
        self.assertTrue((self.project / PACKAGE).is_symlink())
        self.assertFalse((self.project / ".agents/pasp-install-backups").exists())

    def test_installed_package_can_seed_another_project(self):
        self.assertEqual(self.install().returncode, 0)
        source_project = self.project
        self.project = self.root / "second project"
        result = self.install(source=source_project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(inventory(source_project / PACKAGE), inventory(self.project / PACKAGE))
        self.assert_entries()

    def test_install_into_source_repository_preserves_authoring_package(self):
        repo = self.root / "source repo"
        source = self.source_fixture(repo / "skills")
        before = inventory(source)
        result = self.install("--force", source=repo, target=repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(inventory(source), before)
        self.assertEqual(inventory(repo / PACKAGE), before)

    def test_old_source_repository_root_is_not_migrated_away(self):
        old = self.old_install()
        before = inventory(old)
        result = self.install("--force", source=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(inventory(old), before)
        self.assertEqual(inventory(self.project / PACKAGE), before)
        self.assertIn("Preserved root skills/", result.stdout)
        self.assert_entries()

    def test_same_installed_source_force_is_rejected_before_deletion(self):
        source = self.source_fixture(self.project / PACKAGE)
        before = inventory(source)
        result = self.install("--force", source=source)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Source skills are inside the destination", result.stderr)
        self.assertEqual(inventory(source), before)
        self.assertFalse((self.project / ".claude").exists())

    def test_nested_installed_source_force_is_rejected_before_deletion(self):
        source = self.source_fixture(self.project / PACKAGE / "nested source")
        before = inventory(source)
        result = self.install("--force", source=source)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(inventory(source), before)

    def test_symlinked_installation_parent_cannot_redirect_overwrite(self):
        external = self.root / "external"
        external.mkdir()
        (external / "keep.txt").write_text("unchanged")
        self.project.mkdir()
        (self.project / ".agents").symlink_to(external, target_is_directory=True)
        result = self.install("--force")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing symlinked installation parent", result.stderr)
        self.assertEqual(list(external.iterdir()), [external / "keep.txt"])

    def test_package_cannot_be_copied_into_its_own_subtree(self):
        source = self.source_fixture(self.root / "source package")
        before = inventory(source)
        result = self.install("--force", source=source, target=source)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Destination is inside the source package", result.stderr)
        self.assertEqual(inventory(source), before)
        self.assertFalse((source / ".agents").exists())

    def test_empty_source_is_rejected(self):
        result = self.install("--source=")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing value for --source", result.stderr)


if __name__ == "__main__":
    unittest.main()
