from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import check_obsidian_artifacts


class CheckObsidianArtifactsTests(unittest.TestCase):
    def run_check(self, root: Path) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = check_obsidian_artifacts.main([str(root)])
        return exit_code, output.getvalue()

    def test_empty_tree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            exit_code, output = self.run_check(Path(temp_dir))

        self.assertEqual(exit_code, 0)
        self.assertIn("PASS no Obsidian artifact files found", output)

    def test_canvas_edge_must_reference_existing_node(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            canvas_path = Path(temp_dir) / "research" / "canvases" / "bad.canvas"
            canvas_path.parent.mkdir(parents=True)
            canvas_path.write_text(
                json.dumps(
                    {
                        "nodes": [{"id": "known", "type": "text", "x": 0, "y": 0, "width": 100, "height": 100}],
                        "edges": [{"id": "edge-1", "fromNode": "known", "toNode": "missing"}],
                    }
                ),
                encoding="utf-8",
            )

            exit_code, output = self.run_check(Path(temp_dir))

        self.assertEqual(exit_code, 1)
        self.assertIn("edge edge-1 references missing toNode missing", output)

    def test_valid_canvas_and_base_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            canvas_path = root / "research" / "canvases" / "map.canvas"
            canvas_path.parent.mkdir(parents=True)
            canvas_path.write_text(
                json.dumps(
                    {
                        "nodes": [{"id": "note", "type": "text", "x": 0, "y": 0, "width": 100, "height": 100}],
                        "edges": [],
                    }
                ),
                encoding="utf-8",
            )
            base_path = root / "research" / "views" / "claims.base"
            base_path.parent.mkdir(parents=True)
            base_path.write_text(
                'views:\n  - type: table\n    name: "Claims"\n',
                encoding="utf-8",
            )

            exit_code, output = self.run_check(root)

        self.assertEqual(exit_code, 0)
        self.assertIn(f"PASS canvas OK: {canvas_path}", output)
        self.assertIn(f"PASS base OK: {base_path}", output)


if __name__ == "__main__":
    unittest.main()
