from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import check_placeholders
from script_utils import replace_placeholders


SOURCE_NOTE_TRACEABILITY_FIELDS = [
    "citekey:",
    "zotero_uri:",
    "DOI:",
    "URL:",
    "archive_url:",
    "access_date:",
    "source_type:",
    "evidence_type:",
    "peer_review_status:",
    "source_status:",
    "locator_quality:",
    "relevance_to_project:",
    "main_use:",
    "limitations:",
    "last_checked:",
]

SOURCE_NOTE_REQUIRED_SECTIONS = [
    "## Summary",
    "## Key passages with locators",
    "## Claims this source supports",
    "## Claims this source complicates or weakens",
    "## Methodological limitations",
    "## Relation to other sources",
    "## Follow-up tasks",
]

SOURCE_NOTE_STATUS_FIELD = "source_status"
OBSOLETE_SOURCE_NOTE_STATUS_FIELD = "reading" + "_status"
SOURCE_NOTE_SCAFFOLD_FILES = [
    Path("templates/source-note-template.md"),
    Path("notes/10-evidence/source-notes/README.md"),
    Path("end-2-end-tests/fixtures/release_seed/project/notes/10-evidence/source-notes/qa-seed-source.md"),
]


def metadata_value(template: str, field_name: str) -> str:
    prefix = f"{field_name}:"
    for line in template.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    raise AssertionError(f"Missing metadata field: {field_name}")


class TemplateToolTests(unittest.TestCase):
    def test_new_from_template_replaces_explicit_placeholders(self) -> None:
        text = replace_placeholders(
            "{{Title}}\n{{ Claim }}\n{{  Claim  }}\n",
            {"Title": "Chapter 1", "Claim": "Supported claim"},
        )

        self.assertEqual(text, "Chapter 1\nSupported claim\nSupported claim\n")

    def test_placeholder_checker_flags_explicit_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "note.md"
            path.write_text("## Summary\n\n{{BRIEF_SUMMARY}}\n", encoding="utf-8")

            findings = check_placeholders.scan_file(path)

        self.assertEqual(findings, [(3, "{{BRIEF_SUMMARY}}")])

    def test_placeholder_checker_ignores_normal_bracketed_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "note.md"
            path.write_text("This is [not a placeholder] in prose.\n", encoding="utf-8")

            findings = check_placeholders.scan_file(path)

        self.assertEqual(findings, [])

    def test_source_note_template_has_compact_traceability_metadata(self) -> None:
        template = Path("templates/source-note-template.md").read_text(encoding="utf-8")

        for field in SOURCE_NOTE_TRACEABILITY_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field, template)

        for empty_reference_field in ["DOI", "URL", "archive_url", "access_date", "evidence_type"]:
            with self.subTest(field=empty_reference_field):
                self.assertEqual("", metadata_value(template, empty_reference_field))

    def test_source_note_template_uses_source_status_without_legacy_duplicate(self) -> None:
        template = Path("templates/source-note-template.md").read_text(encoding="utf-8")

        self.assertIn(f"{SOURCE_NOTE_STATUS_FIELD}:", template)
        self.assertNotIn(f"{OBSOLETE_SOURCE_NOTE_STATUS_FIELD}:", template)

    def test_source_note_scaffold_files_do_not_use_obsolete_status_field(self) -> None:
        for path in SOURCE_NOTE_SCAFFOLD_FILES:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(OBSOLETE_SOURCE_NOTE_STATUS_FIELD, text)
                if path.suffix == ".md":
                    self.assertIn(SOURCE_NOTE_STATUS_FIELD, text)

    def test_source_note_template_preserves_traceability_sections(self) -> None:
        template = Path("templates/source-note-template.md").read_text(encoding="utf-8")

        for section in SOURCE_NOTE_REQUIRED_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(section, template)


if __name__ == "__main__":
    unittest.main()
