from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_placeholders
import new_from_template


class TemplateToolTests(unittest.TestCase):
    def test_new_from_template_replaces_bracket_placeholders(self) -> None:
        text = new_from_template.apply_replacements("[Title]\n[Claim.]\n", {"Title": "Chapter 1", "Claim": "Supported claim"})

        self.assertEqual(text, "Chapter 1\nSupported claim\n")

    def test_placeholder_checker_flags_bracket_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "note.md"
            path.write_text("## Summary\n\n[Brief summary.]\n", encoding="utf-8")

            findings = check_placeholders.scan_file(path)

        self.assertEqual(findings, [(3, "[Brief summary.]")])


if __name__ == "__main__":
    unittest.main()
