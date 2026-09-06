from __future__ import annotations

import argparse
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.tests.helpers import add_scripts_to_path, working_directory


add_scripts_to_path()

import install_external_skills


class SilentReport(install_external_skills.Report):
    def add(self, bucket: str, message: str) -> None:
        getattr(self, bucket).append(message)


class ArsCodexMigrationTests(unittest.TestCase):
    def git(self, cwd: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", "-c", "protocol.file.allow=always", *args],
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout.strip()

    def initialize_repository(self, path: Path, files: dict[str, str]) -> str:
        path.mkdir(parents=True)
        self.git(path, "init", "--initial-branch=main")
        self.git(path, "config", "user.name", "ARS migration test")
        self.git(path, "config", "user.email", "ars-migration@example.invalid")
        for relative_path, content in files.items():
            file_path = path / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
        self.git(path, "add", ".")
        self.git(path, "commit", "-m", "Initial fixture")
        return self.git(path, "rev-parse", "HEAD")

    def create_fixture(self, root: Path) -> tuple[Path, Path, Path, str, str, Path]:
        old_repository = root / "old-repository"
        new_repository = root / "new-repository"
        old_commit = self.initialize_repository(
            old_repository,
            {
                ".gitignore": "ignored.tmp\n",
                "SKILL.md": "legacy\n",
            },
        )
        new_commit = self.initialize_repository(
            new_repository,
            {
                "plugins/ars-codex/.codex-plugin/plugin.json": (
                    '{"name":"ars-codex","skills":"./skills/"}\n'
                ),
                "plugins/ars-codex/skills/academic-research-suite/SKILL.md": (
                    "---\nname: academic-research-suite\ndescription: Native suite.\n---\n"
                ),
            },
        )

        superproject = root / "superproject"
        superproject.mkdir()
        self.git(superproject, "init", "--initial-branch=main")
        self.git(superproject, "config", "user.name", "ARS migration test")
        self.git(superproject, "config", "user.email", "ars-migration@example.invalid")
        (superproject / "README.md").write_text("fixture\n", encoding="utf-8")
        self.git(superproject, "add", "README.md")
        self.git(superproject, "commit", "-m", "Initial superproject")

        legacy_path = Path("skill-plugins/academic-research-skills")
        native_path = Path("skill-plugins/academic-research-skills-codex")
        self.git(superproject, "submodule", "add", str(old_repository), legacy_path.as_posix())
        self.git(superproject, "commit", "-am", "Add legacy submodule")
        legacy_checkout = superproject / legacy_path
        legacy_git_dir = Path(self.git(legacy_checkout, "rev-parse", "--absolute-git-dir"))

        self.git(superproject, "rm", "--cached", legacy_path.as_posix())
        self.git(
            superproject,
            "config",
            "-f",
            ".gitmodules",
            "--remove-section",
            f"submodule.{legacy_path.as_posix()}",
        )
        self.git(superproject, "submodule", "add", str(new_repository), native_path.as_posix())
        self.git(superproject, "add", ".gitmodules", native_path.as_posix())
        self.git(superproject, "commit", "-m", "Configure native submodule")

        return superproject, legacy_path, native_path, old_commit, new_commit, legacy_git_dir

    def migrate(self, superproject: Path, legacy_path: Path, old_commit: str) -> tuple[bool, SilentReport]:
        report = SilentReport()
        args = argparse.Namespace(dry_run=False)
        with (
            working_directory(superproject),
            mock.patch.object(install_external_skills, "LEGACY_ARS_SOURCE", legacy_path),
            mock.patch.object(install_external_skills, "LEGACY_ARS_GITLINK", old_commit),
        ):
            migrated = install_external_skills.migrate_legacy_ars_checkout(args, report)
        return migrated, report

    def test_dirty_legacy_checkout_stops_without_removal_or_new_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            superproject, legacy_path, native_path, old_commit, _, _ = self.create_fixture(Path(temp_dir))
            legacy_checkout = superproject / legacy_path
            (legacy_checkout / "SKILL.md").write_text("changed\n", encoding="utf-8")
            (legacy_checkout / "notes.txt").write_text("untracked\n", encoding="utf-8")

            migrated, report = self.migrate(superproject, legacy_path, old_commit)

            self.assertFalse(migrated)
            self.assertTrue(legacy_checkout.exists())
            self.assertTrue((superproject / native_path).exists())
            message = "\n".join(report.failed)
            self.assertIn("SKILL.md", message)
            self.assertIn("notes.txt", message)
            self.assertIn("copy, branch, or commit", message)
            self.assertIn("legacy checkout was not removed and ARS Codex was not initialized", message)

    def test_clean_divergent_legacy_head_stops_without_removal_or_new_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            superproject, legacy_path, native_path, old_commit, _, _ = self.create_fixture(Path(temp_dir))
            legacy_checkout = superproject / legacy_path
            self.git(legacy_checkout, "config", "user.name", "ARS migration test")
            self.git(legacy_checkout, "config", "user.email", "ars-migration@example.invalid")
            (legacy_checkout / "SKILL.md").write_text("local commit\n", encoding="utf-8")
            self.git(legacy_checkout, "add", "SKILL.md")
            self.git(legacy_checkout, "commit", "-m", "Local legacy work")
            divergent_commit = self.git(legacy_checkout, "rev-parse", "HEAD")

            migrated, report = self.migrate(superproject, legacy_path, old_commit)

            self.assertFalse(migrated)
            self.assertTrue(legacy_checkout.exists())
            self.assertTrue((superproject / native_path).exists())
            message = "\n".join(report.failed)
            self.assertIn(divergent_commit, message)
            self.assertIn(old_commit, message)
            self.assertIn("Preserve the local commit/ref", message)
            self.assertIn("legacy checkout was not removed and ARS Codex was not initialized", message)

    def test_initialized_unrelated_legacy_checkout_migrates_without_deleting_legacy_gitdir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            superproject, legacy_path, native_path, old_commit, new_commit, legacy_git_dir = self.create_fixture(
                Path(temp_dir)
            )

            self.assertNotEqual(old_commit, new_commit)
            self.assertEqual(self.git(superproject / legacy_path, "rev-list", "--parents", "-n", "1", old_commit), old_commit)
            self.assertEqual(self.git(superproject / native_path, "rev-list", "--parents", "-n", "1", new_commit), new_commit)

            migrated, report = self.migrate(superproject, legacy_path, old_commit)

            self.assertTrue(migrated)
            self.assertFalse((superproject / legacy_path).exists())
            self.assertTrue((superproject / native_path).exists())
            self.assertTrue(legacy_git_dir.exists())
            self.git(
                superproject,
                f"--git-dir={legacy_git_dir}",
                f"--work-tree={superproject}",
                "cat-file",
                "-e",
                f"{old_commit}^{{commit}}",
            )
            self.assertEqual(report.failed, [])
            self.assertTrue(any("preserved legacy Git directory" in message for message in report.installed))

    def test_linked_worktree_migration_accepts_its_worktree_specific_module_gitdir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            superproject, legacy_path, _, old_commit, _, _ = self.create_fixture(root)
            legacy_superproject_commit = self.git(superproject, "rev-parse", "HEAD~1")
            final_superproject_commit = self.git(superproject, "rev-parse", "HEAD")
            linked_worktree = root / "linked-worktree"
            self.git(
                superproject,
                "worktree",
                "add",
                "--detach",
                str(linked_worktree),
                legacy_superproject_commit,
            )
            self.git(
                linked_worktree,
                "submodule",
                "update",
                "--init",
                "--recursive",
                "--",
                legacy_path.as_posix(),
            )
            legacy_checkout = linked_worktree / legacy_path
            legacy_git_dir = Path(self.git(legacy_checkout, "rev-parse", "--absolute-git-dir"))
            self.assertIn("worktrees", legacy_git_dir.parts)
            self.git(linked_worktree, "checkout", final_superproject_commit)

            migrated, report = self.migrate(linked_worktree, legacy_path, old_commit)

            self.assertTrue(migrated, report.failed)
            self.assertFalse(legacy_checkout.exists())
            self.assertTrue(legacy_git_dir.exists())

    def test_prepare_migrates_then_initializes_exact_native_pin_and_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            superproject, legacy_path, native_path, old_commit, new_commit, legacy_git_dir = self.create_fixture(root)
            new_repository = root / "new-repository"
            self.git(superproject, "submodule", "deinit", "-f", "--", native_path.as_posix())
            self.assertFalse((superproject / native_path / ".git").exists())
            report = SilentReport()
            args = argparse.Namespace(
                dry_run=False,
                preserve_skill_plugin_checkouts=False,
                update=False,
            )

            with (
                working_directory(superproject),
                mock.patch.object(install_external_skills, "LEGACY_ARS_SOURCE", legacy_path),
                mock.patch.object(install_external_skills, "LEGACY_ARS_GITLINK", old_commit),
                mock.patch.object(install_external_skills, "ARS_CODEX_SOURCE", native_path),
                mock.patch.object(install_external_skills, "ARS_CODEX_PIN", new_commit),
                mock.patch.object(install_external_skills, "ARS_CODEX_REPO", str(new_repository)),
            ):
                prepared = install_external_skills.prepare_ars_codex(args, report)

            self.assertTrue(prepared, report.failed)
            self.assertFalse((superproject / legacy_path).exists())
            self.assertTrue(legacy_git_dir.exists())
            self.assertEqual(self.git(superproject / native_path, "rev-parse", "HEAD"), new_commit)
            self.assertEqual(
                self.git(superproject / native_path, "remote", "get-url", "origin"),
                str(new_repository),
            )

    def test_ignored_legacy_path_stops_before_removal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            superproject, legacy_path, _, old_commit, _, _ = self.create_fixture(Path(temp_dir))
            ignored_path = superproject / legacy_path / "ignored.tmp"
            ignored_path.write_text("preserve me\n", encoding="utf-8")

            migrated, report = self.migrate(superproject, legacy_path, old_commit)

            self.assertFalse(migrated)
            self.assertTrue(ignored_path.exists())
            self.assertIn("ignored.tmp", "\n".join(report.failed))

    def test_non_git_legacy_path_stops_unless_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            superproject = Path(temp_dir)
            legacy_path = Path("skill-plugins/academic-research-skills")
            occupied_path = superproject / legacy_path
            occupied_path.mkdir(parents=True)
            (occupied_path / "notes.txt").write_text("preserve me\n", encoding="utf-8")

            migrated, report = self.migrate(superproject, legacy_path, "expected")

            self.assertFalse(migrated)
            self.assertTrue(occupied_path.exists())
            self.assertIn("nonempty path is not a Git checkout", "\n".join(report.failed))


if __name__ == "__main__":
    unittest.main()
