from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import setup_environment


class ObsidianInstallerTests(unittest.TestCase):
    def test_sha256_file_returns_expected_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "archive.zip"
            path.write_bytes(b"release")

            self.assertEqual(setup_environment.sha256_file(path), hashlib.sha256(b"release").hexdigest())

    def test_safe_extract_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "bad.zip"
            destination = Path(temp_dir) / "extract"
            destination.mkdir()
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../evil.txt", "bad")

            with zipfile.ZipFile(archive_path) as archive:
                with self.assertRaises(ValueError):
                    setup_environment.safe_extract_zip(archive, destination)


if __name__ == "__main__":
    unittest.main()
