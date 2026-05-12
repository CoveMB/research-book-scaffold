from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class RenderScriptTests(unittest.TestCase):
    def test_render_fails_when_quarto_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as empty_path:
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
        self.assertIn("No TeX engine found for PDF rendering.", result.stdout)


if __name__ == "__main__":
    unittest.main()
