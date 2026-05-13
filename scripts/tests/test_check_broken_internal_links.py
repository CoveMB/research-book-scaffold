from __future__ import annotations

import unittest
from pathlib import Path


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import check_broken_internal_links


class CheckBrokenInternalLinksTests(unittest.TestCase):
    def test_ambiguous_stem_targets_are_reported(self) -> None:
        files = [Path("notes/a/topic.md"), Path("research/topic.md")]
        target_index = check_broken_internal_links.build_target_index(files)

        status = check_broken_internal_links.link_status("topic", Path("notes/source.md"), target_index)

        self.assertEqual(status.kind, "ambiguous")


if __name__ == "__main__":
    unittest.main()
