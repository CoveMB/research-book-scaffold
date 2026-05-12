from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_obsidian_codex


class CheckObsidianCodexTests(unittest.TestCase):
    def test_missing_vault_reports_single_failure(self) -> None:
        original_check_cli = check_obsidian_codex.check_cli
        check_obsidian_codex.check_cli = lambda: True
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                missing_vault = Path(temp_dir) / "missing"
                output = io.StringIO()

                with contextlib.redirect_stdout(output):
                    exit_code = check_obsidian_codex.main(["check", str(missing_vault)])

            text = output.getvalue()
        finally:
            check_obsidian_codex.check_cli = original_check_cli

        self.assertEqual(exit_code, 1)
        self.assertEqual(text.count("FAIL"), 1)
        self.assertNotIn("manifest.json missing", text)

    def test_community_plugins_must_be_a_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            obsidian_dir = Path(temp_dir) / ".obsidian"
            obsidian_dir.mkdir()
            (obsidian_dir / "community-plugins.json").write_text(
                json.dumps({"obsidian-codex": True}),
                encoding="utf-8",
            )
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                check_obsidian_codex.check_community_plugins(obsidian_dir)

        text = output.getvalue()
        self.assertIn("WARN invalid community-plugins.json", text)
        self.assertNotIn("PASS Obsidian plugin listed as enabled", text)


if __name__ == "__main__":
    unittest.main()
