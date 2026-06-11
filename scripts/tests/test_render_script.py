from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys
from unittest import mock


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import render_manuscript


class RenderScriptTests(unittest.TestCase):
    def test_render_fails_when_quarto_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as empty_path:
            python_link = Path(empty_path) / "python3"
            python_link.symlink_to(sys.executable)
            result = subprocess.run(
                ["/bin/sh", "scripts/research-writing/render.sh"],
                check=False,
                capture_output=True,
                text=True,
                env={"PATH": empty_path},
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Quarto is not installed.", result.stdout)

    def test_render_fails_before_quarto_when_lualatex_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_path:
            python_link = Path(temp_path) / "python3"
            python_link.symlink_to(sys.executable)
            fake_quarto = Path(temp_path) / "quarto"
            fake_quarto.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            fake_quarto.chmod(0o755)
            path = os.pathsep.join([temp_path, "/usr/bin", "/bin"])
            result = subprocess.run(
                ["/bin/sh", "scripts/research-writing/render.sh"],
                check=False,
                capture_output=True,
                text=True,
                env={"PATH": path},
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("No TeX engine found for PDF rendering: lualatex.", result.stdout)
        self.assertIn("$HOME/Library/TinyTeX/bin/universal-darwin", result.stdout)

    def test_configured_pdf_engine_is_used(self) -> None:
        config = "format:\n  pdf:\n    pdf-engine: xelatex\n"

        self.assertEqual(render_manuscript.configured_pdf_engine(config), "xelatex")

    def test_html_render_does_not_require_pdf_engine(self) -> None:
        self.assertFalse(render_manuscript.requires_pdf_engine("html", "format:\n  pdf:\n    toc: true\n"))

    def test_citation_preflight_uses_repository_checker(self) -> None:
        calls: list[tuple[list[str], bool]] = []

        def runner(command: list[str], check: bool) -> subprocess.CompletedProcess[str]:
            calls.append((command, check))
            return subprocess.CompletedProcess(command, 1)

        self.assertEqual(render_manuscript.run_citation_preflight(runner), 1)
        self.assertEqual(calls, [([sys.executable, "scripts/research-writing/check_citations.py"], False)])

    def test_main_stops_before_quarto_when_citation_preflight_fails(self) -> None:
        with (
            mock.patch.object(render_manuscript, "change_to_project_root"),
            mock.patch.object(render_manuscript, "check_preconditions", return_value=0),
            mock.patch.object(render_manuscript, "run_citation_preflight", return_value=1),
            mock.patch.object(render_manuscript.subprocess, "run") as run,
        ):
            self.assertEqual(render_manuscript.main(["--to", "html"]), 1)

        run.assert_not_called()

    def test_mirror_html_render_outputs_copies_book_to_html_exports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            book_dir = root / "manuscript" / "_book"
            book_dir.mkdir(parents=True)
            (root / "exports" / "html").mkdir(parents=True)
            (root / "exports" / "html" / ".gitkeep").touch()
            (book_dir / "index.html").write_text("<h1>Draft</h1>\n", encoding="utf-8")
            (book_dir / "site_libs").mkdir()
            (book_dir / "site_libs" / "quarto.css").write_text("body {}\n", encoding="utf-8")

            render_manuscript.mirror_render_outputs("html", root)

            self.assertEqual((root / "exports" / "html" / "index.html").read_text(encoding="utf-8"), "<h1>Draft</h1>\n")
            self.assertTrue((root / "exports" / "html" / ".gitkeep").is_file())
            self.assertEqual((root / "exports" / "html" / ".gitkeep").read_text(encoding="utf-8"), "\n")
            self.assertTrue((root / "exports" / "html" / "site_libs" / "quarto.css").is_file())

    def test_mirror_all_render_outputs_copies_pdf_and_docx_exports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            book_dir = root / "manuscript" / "_book"
            book_dir.mkdir(parents=True)
            (book_dir / "index.html").write_text("<h1>Draft</h1>\n", encoding="utf-8")
            (book_dir / "book.pdf").write_text("pdf\n", encoding="utf-8")
            (book_dir / "book.docx").write_text("docx\n", encoding="utf-8")

            render_manuscript.mirror_render_outputs(None, root)

            self.assertTrue((root / "exports" / "html" / "index.html").is_file())
            self.assertTrue((root / "exports" / "pdf" / "book.pdf").is_file())
            self.assertTrue((root / "exports" / "docx" / "book.docx").is_file())


if __name__ == "__main__":
    unittest.main()
