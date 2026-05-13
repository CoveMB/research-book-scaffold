from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import render_manuscript


class RenderScriptTests(unittest.TestCase):
    def test_render_fails_when_quarto_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as empty_path:
            python_link = Path(empty_path) / "python3"
            python_link.symlink_to(sys.executable)
            result = subprocess.run(
                ["/bin/sh", "scripts/render.sh"],
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
                ["/bin/sh", "scripts/render.sh"],
                check=False,
                capture_output=True,
                text=True,
                env={"PATH": path},
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("No TeX engine found for PDF rendering: lualatex.", result.stdout)

    def test_configured_pdf_engine_is_used(self) -> None:
        config = "format:\n  pdf:\n    pdf-engine: xelatex\n"

        self.assertEqual(render_manuscript.configured_pdf_engine(config), "xelatex")

    def test_html_render_does_not_require_pdf_engine(self) -> None:
        self.assertFalse(render_manuscript.requires_pdf_engine("html", "format:\n  pdf:\n    toc: true\n"))


if __name__ == "__main__":
    unittest.main()
