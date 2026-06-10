from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
END_TO_END_TESTS_ROOT = ROOT / "end-2-end-tests"
TOOL_PATH = END_TO_END_TESTS_ROOT / "tools" / "seed_release_qa.py"


def load_seed_tool():
    spec = importlib.util.spec_from_file_location("seed_release_qa", TOOL_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load {TOOL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_git(project_root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=project_root, check=True, capture_output=True, text=True)


def create_disposable_project() -> Path:
    temp_dir = Path(tempfile.mkdtemp())
    for directory in [
        "bibliography",
        "manuscript/chapters",
        "notes/10-evidence/source-notes",
        "notes/20-analysis/literature-maps",
        "notes/20-analysis/concept-notes",
        "notes/30-claims-and-argument/claim-ledger",
        "notes/40-writing-bridge/chapter-briefs",
        "notes/90-audits/audits",
        "research/extraction-tables",
        "research/search-logs",
        "research/source-matrices",
    ]:
        (temp_dir / directory).mkdir(parents=True, exist_ok=True)
    (temp_dir / "bibliography/references.bib").write_text("% original bibliography\n", encoding="utf-8")
    (temp_dir / "manuscript/_quarto.yml").write_text(
        'book:\n  title: "Untitled Scholarly Manuscript"\n', encoding="utf-8"
    )
    (temp_dir / "manuscript/index.qmd").write_text("# Original manuscript\n", encoding="utf-8")
    run_git(temp_dir, "init")
    run_git(temp_dir, "add", ".")
    subprocess.run(
        ["git", "-c", "user.email=qa@example.invalid", "-c", "user.name=QA", "commit", "-m", "baseline"],
        cwd=temp_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    return temp_dir


class SeedReleaseQaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.seed_tool = load_seed_tool()

    def test_apply_writes_complete_release_seed(self) -> None:
        project_root = create_disposable_project()

        results = self.seed_tool.apply_seed(project_root)

        self.assertTrue(all(result.changed or result.status == "already-current" for result in results))
        for target_path in self.seed_tool.SEED_TARGETS:
            self.assertTrue((project_root / target_path).exists(), target_path)
        references_text = (project_root / "bibliography/references.bib").read_text(encoding="utf-8")
        self.assertIn("@book{qaSeed2026", references_text)
        self.assertIn("QA Seed Manuscript", (project_root / "manuscript/_quarto.yml").read_text(encoding="utf-8"))

    def test_default_paths_use_end_to_end_test_layout(self) -> None:
        self.assertEqual(
            self.seed_tool.DEFAULT_FIXTURE_ROOT,
            END_TO_END_TESTS_ROOT / "fixtures" / "release_seed" / "project",
        )
        self.assertEqual(self.seed_tool.DEFAULT_PROJECT_ROOT, ROOT)

    def test_status_reports_missing_then_applied_seed_files(self) -> None:
        project_root = create_disposable_project()

        initial_states = {item.status for item in self.seed_tool.seed_status(project_root)}
        self.seed_tool.apply_seed(project_root)
        applied_states = {item.status for item in self.seed_tool.seed_status(project_root)}

        self.assertIn("missing", initial_states)
        self.assertEqual(applied_states, {"applied"})

    def test_apply_dry_run_does_not_write_files(self) -> None:
        project_root = create_disposable_project()

        results = self.seed_tool.apply_seed(project_root, dry_run=True)

        self.assertTrue(all(result.status == "would-write" for result in results))
        self.assertFalse((project_root / "manuscript/chapters/qa-seed-chapter.qmd").exists())
        self.assertEqual(
            "% original bibliography\n",
            (project_root / "bibliography/references.bib").read_text(encoding="utf-8"),
        )

    def test_clean_restores_tracked_files_and_removes_seed_only_files(self) -> None:
        project_root = create_disposable_project()
        self.seed_tool.apply_seed(project_root)

        results = self.seed_tool.clean_seed(project_root)

        self.assertTrue(results)
        self.assertEqual(
            "% original bibliography\n",
            (project_root / "bibliography/references.bib").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            'book:\n  title: "Untitled Scholarly Manuscript"\n',
            (project_root / "manuscript/_quarto.yml").read_text(encoding="utf-8"),
        )
        self.assertFalse((project_root / "manuscript/chapters/qa-seed-chapter.qmd").exists())

    def test_clean_uses_the_configured_fixture_root_for_seed_only_files(self) -> None:
        project_root = create_disposable_project()
        with tempfile.TemporaryDirectory() as fixture_dir:
            fixture_root = Path(fixture_dir)
            for target in self.seed_tool.RESTORE_TARGETS:
                fixture_path = fixture_root / target
                fixture_path.parent.mkdir(parents=True, exist_ok=True)
                fixture_path.write_text(f"seeded {target}\n", encoding="utf-8")
            seed_only_target = Path("notes/10-evidence/source-notes/custom-seed.md")
            seed_only_path = fixture_root / seed_only_target
            seed_only_path.parent.mkdir(parents=True, exist_ok=True)
            seed_only_path.write_text("custom seed\n", encoding="utf-8")

            self.seed_tool.apply_seed(project_root, fixture_root=fixture_root)
            self.seed_tool.clean_seed(project_root, fixture_root=fixture_root)

        self.assertFalse((project_root / seed_only_target).exists())

    def test_apply_is_idempotent(self) -> None:
        project_root = create_disposable_project()
        self.seed_tool.apply_seed(project_root)

        second_results = self.seed_tool.apply_seed(project_root)

        self.assertTrue(all(result.status == "already-current" for result in second_results))


if __name__ == "__main__":
    unittest.main()
