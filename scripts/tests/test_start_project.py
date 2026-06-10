from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import start_project
import check_placeholders
import check_manuscript_readiness


def write_minimal_scaffold(root: Path) -> None:
    (root / "templates").mkdir()
    (root / "manuscript" / "chapters").mkdir(parents=True)
    (root / "bibliography").mkdir()
    (root / "notes" / "00-inbox").mkdir(parents=True)

    (root / "templates" / "project-charter-template.md").write_text(
        "\n".join(
            [
                "---",
                "type: project-charter",
                "status: draft",
                "---",
                "",
                "# Project charter",
                "",
                "## Working title",
                "",
                "{{TITLE}}",
                "",
                "## Book purpose",
                "",
                "{{PURPOSE}}",
                "",
                "## Audience",
                "",
                "{{PRIMARY_READERS}}",
                "",
                "## Central question",
                "",
                "{{QUESTION}}",
                "",
                "## Scope boundaries",
                "",
                "### In scope",
                "",
                "- {{IN_SCOPE_BOUNDARY}}",
                "",
                "### Out of scope",
                "",
                "- {{OUT_OF_SCOPE_BOUNDARY}}",
                "",
                "## Source base",
                "",
                "- {{KNOWN_SOURCE_BASE}}",
                "",
                "## Key uncertainties",
                "",
                "- {{KEY_UNCERTAINTY}}",
                "",
                "## First research tasks",
                "",
                "- {{FIRST_RESEARCH_TASK}}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "manuscript" / "_quarto.yml").write_text(
        "\n".join(
            [
                "project:",
                "  type: book",
                "  output-dir: _book",
                "",
                "book:",
                '  title: "Research Scaffold Verification Manuscript"',
                "  chapters:",
                "    - index.qmd",
                "    - chapters/00-front-matter.qmd",
                "    - chapters/99-back-matter.qmd",
                "",
                "bibliography: ../bibliography/references.bib",
                "",
                "format:",
                "  html:",
                "    toc: true",
                "  pdf:",
                "    toc: true",
                "  docx:",
                "    toc: true",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "manuscript" / "index.qmd").write_text(
        "\n".join(
            [
                "# Overview",
                "",
                "This manuscript scaffold is generic. Replace this page with project-level front matter when the project has a defined scope.",
                "",
                "Use citations only after the citekey exists in `../bibliography/references.bib`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "manuscript" / "chapters" / "00-front-matter.qmd").write_text("# Front matter\n", encoding="utf-8")
    (root / "manuscript" / "chapters" / "99-back-matter.qmd").write_text("# Back matter\n", encoding="utf-8")
    (root / "bibliography" / "references.bib").write_text(
        "% Add verified BibTeX records here.\n% Zotero or this file is the citation source of truth.\n",
        encoding="utf-8",
    )


def example_answers() -> dict[str, object]:
    return {
        "working_title": "Careful Research",
        "subtitle": "Evidence Before Argument",
        "author_name": "A. Scholar",
        "project_slug": "careful-research",
        "project_type": "book",
        "central_research_question": "How should this project define its evidence base?",
        "working_thesis": "unknown yet",
        "primary_audience": "Scholars in the field",
        "secondary_audience": "Graduate students",
        "fields_disciplines": ["history", "media studies"],
        "theories_to_engage": ["archival studies"],
        "contested_theories": ["platform determinism"],
        "scope_included": ["verified sources", "auditable notes"],
        "scope_excluded": ["unsupported claims"],
        "main_uncertainties": ["source corpus is incomplete"],
        "initial_research_tasks": ["Build Zotero collection", "Draft search protocol"],
        "output_formats": ["html", "docx"],
        "chapter_names": ["Introduction", "Evidence Base"],
        "citation_style": "IEEE",
        "target_venue": "undecided",
        "bibliography_path": "bibliography/references.bib",
        "better_bibtex_auto_export": "not yet",
        "use_obsidian": "yes",
        "use_codex_agents": "yes",
        "strict_placeholder_detection": "yes",
        "run_audit_after_initialization": "no",
        "render_after_initialization": "yes",
    }


class StartProjectTests(unittest.TestCase):
    def test_dry_run_makes_no_changes_and_reports_planned_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            before = {
                path.relative_to(root): path.read_text(encoding="utf-8")
                for path in root.rglob("*")
                if path.is_file()
            }

            result = start_project.initialize_project(
                root,
                example_answers(),
                start_project.StartProjectOptions(dry_run=True, skip_audit=True, skip_render=True),
            )

            after = {
                path.relative_to(root): path.read_text(encoding="utf-8")
                for path in root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(after, before)
            self.assertIn(root / "manuscript" / "_quarto.yml", result.planned_files)
            self.assertIn(root / "notes" / "00-inbox" / "project-charter.md", result.planned_files)

    def test_answers_file_mode_updates_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            answers_path = root / "project-start.json"
            answers_path.write_text(json.dumps(example_answers()), encoding="utf-8")

            result = start_project.run_cli(
                ["--answers", str(answers_path), "--non-interactive", "--skip-audit", "--skip-render"],
                project_root=root,
                emit_summary=False,
            )

            self.assertEqual(result.exit_code, 0)
            config = (root / "manuscript" / "_quarto.yml").read_text(encoding="utf-8")
            index = (root / "manuscript" / "index.qmd").read_text(encoding="utf-8")
            charter = (root / "notes" / "00-inbox" / "project-charter.md").read_text(encoding="utf-8")
            saved_answers = (root / "project-start.yml").read_text(encoding="utf-8")

            self.assertIn('title: "Careful Research"', config)
            self.assertIn('subtitle: "Evidence Before Argument"', config)
            self.assertIn("chapters/01-introduction.qmd", config)
            self.assertNotIn("manuscript/chapters/01-introduction.qmd", config)
            self.assertIn("format:\n  html:", config)
            self.assertIn("  docx:", config)
            self.assertNotIn("  pdf:", config)
            self.assertIn("# Careful Research", index)
            self.assertIn("How should this project define its evidence base?", charter)
            self.assertIn("source corpus is incomplete", charter)
            self.assertIn("working_title: Careful Research", saved_answers)

    def test_interactive_mode_resumes_from_existing_project_start_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            (root / "project-start.yml").write_text(
                start_project.dump_answers_yaml(start_project.normalize_answers(example_answers())),
                encoding="utf-8",
            )

            def fail_if_prompted(_prompt: str) -> str:
                raise AssertionError("Existing project-start.yml should provide all answers.")

            result = start_project.run_cli(
                ["--skip-audit", "--skip-render"],
                project_root=root,
                input_func=fail_if_prompted,
                emit_summary=False,
            )

            self.assertEqual(result.exit_code, 0)
            config = (root / "manuscript" / "_quarto.yml").read_text(encoding="utf-8")
            self.assertIn('title: "Careful Research"', config)
            self.assertTrue(any("Resumed answers from project-start.yml" in warning for warning in result.warnings))

    def test_preflight_summary_prints_before_interactive_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            (root / "project-start.yml").write_text(
                start_project.dump_answers_yaml(start_project.normalize_answers(example_answers())),
                encoding="utf-8",
            )
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = start_project.run_cli(
                    ["--dry-run", "--skip-audit", "--skip-render"],
                    project_root=root,
                    input_func=lambda _prompt: "",
                    which_func=lambda _name: None,
                )

            text = output.getvalue()
            self.assertEqual(result.exit_code, 0)
            self.assertLess(text.index("Preflight summary"), text.index("Project initialization summary"))
            self.assertIn("Existing project-start.yml: found", text)
            self.assertIn("Quarto: not found", text)
            self.assertIn("Pandoc: not found", text)

    def test_preflight_does_not_inspect_bibliography_outside_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "project"
            root.mkdir()
            write_minimal_scaffold(root)
            outside_bibliography = Path(temp_dir) / "outside.bib"
            outside_bibliography.write_text("@book{outside,title={Outside}}\n", encoding="utf-8")

            lines = start_project.preflight_summary_lines(
                root,
                {"bibliography_path": outside_bibliography.as_posix()},
                which_func=lambda _name: None,
            )

            bibliography_line = next(line for line in lines if line.startswith("Bibliography path:"))
            self.assertIn("outside project root", bibliography_line)
            self.assertNotIn("has verified-looking entries", bibliography_line)

    def test_collect_interactive_answers_accepts_unknowns_without_real_stdin(self) -> None:
        supplied_values = iter(
            [
                "Interactive Title",
                "",
                "Interactive Author",
                "interactive-title",
                "article",
                "unknown",
                "unknown",
                "specialists",
                "",
                "history, sociology",
                "",
                "",
                "case material",
                "general claims",
                "archive access",
                "find sources, verify citekeys",
                "html, pdf",
                "",
                "",
                "",
                "",
                "not sure",
                "yes",
                "yes",
                "yes",
                "no",
                "no",
            ]
        )

        answers = start_project.collect_interactive_answers(input_func=lambda _prompt: next(supplied_values))

        self.assertEqual(answers["working_title"], "Interactive Title")
        self.assertEqual(answers["working_thesis"], "unknown yet")
        self.assertEqual(answers["chapter_names"], start_project.default_chapter_names("article"))

    def test_running_twice_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            options = start_project.StartProjectOptions(skip_audit=True, skip_render=True)

            first = start_project.initialize_project(root, example_answers(), options)
            second = start_project.initialize_project(root, example_answers(), options)

            self.assertGreater(len(first.changed_files), 0)
            self.assertEqual(second.changed_files, [])
            self.assertIn(root / "manuscript" / "_quarto.yml", second.unchanged_files)

    def test_generated_file_user_edits_are_preserved_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            options = start_project.StartProjectOptions(skip_audit=True, skip_render=True)
            start_project.initialize_project(root, example_answers(), options)
            index_path = root / "manuscript" / "index.qmd"
            edited_text = index_path.read_text(encoding="utf-8") + "\n## Local addition\n\nDo not remove this.\n"
            index_path.write_text(edited_text, encoding="utf-8")

            result = start_project.initialize_project(root, example_answers(), options)

            self.assertEqual(index_path.read_text(encoding="utf-8"), edited_text)
            self.assertIn(index_path, result.skipped_files)
            self.assertTrue(
                any("generated file differs from the planned initializer output" in warning for warning in result.warnings)
            )

    def test_force_dry_run_reports_protected_files_that_would_be_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            index_path = root / "manuscript" / "index.qmd"
            index_path.write_text("# Existing Draft\n\nDo not replace this without review.\n", encoding="utf-8")

            result = start_project.initialize_project(
                root,
                example_answers(),
                start_project.StartProjectOptions(dry_run=True, force=True, skip_audit=True, skip_render=True),
            )

            self.assertEqual(index_path.read_text(encoding="utf-8"), "# Existing Draft\n\nDo not replace this without review.\n")
            self.assertIn(index_path, result.protected_force_files)

    def test_non_scaffold_content_is_not_overwritten_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            index_path = root / "manuscript" / "index.qmd"
            index_path.write_text("# Existing Draft\n\nDo not replace this.\n", encoding="utf-8")

            result = start_project.initialize_project(
                root,
                example_answers(),
                start_project.StartProjectOptions(skip_audit=True, skip_render=True),
            )

            self.assertEqual(index_path.read_text(encoding="utf-8"), "# Existing Draft\n\nDo not replace this.\n")
            self.assertIn(index_path, result.skipped_files)
            self.assertTrue(any("non-scaffold content" in warning for warning in result.warnings))

    def test_scaffold_title_text_is_removed_after_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)

            start_project.initialize_project(
                root,
                example_answers(),
                start_project.StartProjectOptions(skip_audit=True, skip_render=True),
            )

            self.assertNotIn(
                "Research Scaffold Verification Manuscript",
                (root / "manuscript" / "_quarto.yml").read_text(encoding="utf-8"),
            )
            self.assertNotIn(
                "This manuscript scaffold is generic",
                (root / "manuscript" / "index.qmd").read_text(encoding="utf-8"),
            )

    def test_current_front_and_back_matter_defaults_are_replaced_after_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            (root / "manuscript" / "chapters" / "00-front-matter.qmd").write_text(
                "# Front matter\n\nUse this file for generic front matter such as acknowledgments, preface, or author notes when needed.\n",
                encoding="utf-8",
            )
            (root / "manuscript" / "chapters" / "99-back-matter.qmd").write_text(
                "# Back matter\n\nUse this file for references to appendices, glossary notes, or other closing material when needed.\n",
                encoding="utf-8",
            )

            start_project.initialize_project(
                root,
                example_answers(),
                start_project.StartProjectOptions(skip_audit=True, skip_render=True),
            )

            config = (root / "manuscript" / "_quarto.yml").read_text(encoding="utf-8")
            front_matter = (root / "manuscript" / "chapters" / "00-front-matter.qmd").read_text(encoding="utf-8")
            back_matter = (root / "manuscript" / "chapters" / "99-back-matter.qmd").read_text(encoding="utf-8")

            self.assertIn("chapters/00-front-matter.qmd", config)
            self.assertIn("chapters/99-back-matter.qmd", config)
            self.assertIn("# Front matter for Careful Research", front_matter)
            self.assertIn("Project type: book", front_matter)
            self.assertIn("# Back matter for Careful Research", back_matter)
            self.assertIn("Bibliography path: `bibliography/references.bib`", back_matter)
            self.assertEqual(check_manuscript_readiness.scan_release_manuscript(root), [])

    def test_missing_optional_render_tool_warns_without_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)

            result = start_project.initialize_project(
                root,
                example_answers(),
                start_project.StartProjectOptions(skip_audit=True, skip_render=False),
                which_func=lambda _name: None,
            )

            self.assertEqual(result.exit_code, 0)
            self.assertTrue(any("Quarto is not available" in warning for warning in result.warnings))

    def test_next_steps_report_manual_citation_and_tool_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            answers = example_answers()
            answers["better_bibtex_auto_export"] = "not yet"
            answers["render_after_initialization"] = "yes"

            result = start_project.initialize_project(
                root,
                answers,
                start_project.StartProjectOptions(skip_audit=True, skip_render=False),
                which_func=lambda _name: None,
            )

            self.assertTrue(any("Set up Zotero + Better BibTeX auto-export" in step for step in result.next_steps))
            self.assertTrue(any("Install Quarto before rendering" in step for step in result.next_steps))

    def test_bibliography_path_cannot_escape_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            answers = example_answers()
            answers["bibliography_path"] = "../outside.bib"

            result = start_project.initialize_project(
                root,
                answers,
                start_project.StartProjectOptions(skip_audit=True, skip_render=True),
            )

            self.assertFalse((root.parent / "outside.bib").exists())
            self.assertTrue(any("outside the project root" in warning for warning in result.warnings))
            config = (root / "manuscript" / "_quarto.yml").read_text(encoding="utf-8")
            self.assertIn("bibliography: ../bibliography/references.bib", config)
            self.assertIn("csl: ../bibliography/csl/ieee.csl", config)

    def test_explicit_undecided_citation_style_remains_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            answers = example_answers()
            answers["citation_style"] = "undecided"

            result = start_project.initialize_project(
                root,
                answers,
                start_project.StartProjectOptions(skip_audit=True, skip_render=True),
            )

            config = (root / "manuscript" / "_quarto.yml").read_text(encoding="utf-8")
            self.assertNotIn("csl: ../bibliography/csl/ieee.csl", config)
            self.assertTrue(any("Choose a citation style" in step for step in result.next_steps))

    def test_strict_placeholder_detection_marks_unresolved_decisions_for_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_scaffold(root)
            answers = example_answers()
            answers["central_research_question"] = "unknown"
            answers["primary_audience"] = "unknown"
            answers["scope_included"] = []
            answers["scope_excluded"] = []
            answers["main_uncertainties"] = []
            answers["initial_research_tasks"] = []
            answers["strict_placeholder_detection"] = "yes"

            start_project.initialize_project(
                root,
                answers,
                start_project.StartProjectOptions(skip_audit=True, skip_render=True),
            )

            index_path = root / "manuscript" / "index.qmd"
            self.assertIn("TODO: decide later.", index_path.read_text(encoding="utf-8"))
            self.assertTrue(check_placeholders.scan_file(index_path))

            chapter_path = root / "manuscript" / "chapters" / "01-introduction.qmd"
            chapter_text = chapter_path.read_text(encoding="utf-8")
            self.assertIn("TODO:", chapter_text)
            self.assertNotIn("Unresolved: define this chapter", chapter_text)
            self.assertTrue(check_placeholders.scan_file(chapter_path))

    def test_blank_yaml_scalar_stays_empty_in_answers_file(self) -> None:
        answers = start_project.normalize_answers(
            start_project.parse_simple_yaml(
                "\n".join(
                    [
                        "working_title: Test Project",
                        "subtitle:",
                        "chapter_names:",
                        "  - Introduction",
                        "",
                    ]
                )
            )
        )

        self.assertEqual(answers["subtitle"], "")
        config = start_project.render_quarto_config(Path("."), answers)
        self.assertNotIn('subtitle: "[]"', config)
        self.assertNotIn("subtitle:", config)

    def test_chapter_file_slugs_do_not_create_codex_prefixed_names(self) -> None:
        answers = start_project.normalize_answers(
            {
                **example_answers(),
                "chapter_names": ["Codex Methods"],
            }
        )

        self.assertEqual(
            [path.as_posix() for path in start_project.chapter_file_paths(answers)],
            ["manuscript/chapters/01-section-codex-methods.qmd"],
        )
        self.assertEqual(
            [path.as_posix() for path in start_project.chapter_quarto_paths(answers)],
            ["chapters/01-section-codex-methods.qmd"],
        )


if __name__ == "__main__":
    unittest.main()
