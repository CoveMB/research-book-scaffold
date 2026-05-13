from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import check_placeholders
from script_utils import replace_placeholders


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


if __name__ == "__main__":
    unittest.main()
