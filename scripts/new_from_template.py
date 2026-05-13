#!/usr/bin/env python3
"""Create a new file from a template."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from project_config import change_to_project_root
from script_utils import replace_placeholders, write_text_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", help="Template file to copy.")
    parser.add_argument("destination", help="Destination file to create.")
    parser.add_argument("--force", action="store_true", help="Overwrite destination if it exists.")
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Replace {{KEY}} and {{ KEY }} placeholders.",
    )
    return parser.parse_args()


def parse_replacements(raw_values: list[str]) -> dict[str, str]:
    replacements: dict[str, str] = {}
    for raw_value in raw_values:
        if "=" not in raw_value:
            raise ValueError(f"Invalid --set value {raw_value!r}; expected KEY=VALUE")
        key, value = raw_value.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("Replacement key cannot be empty")
        replacements[key] = value
    return replacements


def main() -> int:
    change_to_project_root()
    args = parse_args()
    template_path = Path(args.template)
    destination_path = Path(args.destination)

    if not template_path.is_file():
        print(f"FAIL template not found: {template_path}")
        return 1

    if destination_path.exists() and not args.force:
        print(f"FAIL destination exists: {destination_path}")
        print("Use --force to overwrite.")
        return 1

    try:
        replacements = parse_replacements(args.set)
    except ValueError as error:
        print(f"FAIL {error}")
        return 1

    text = template_path.read_text(encoding="utf-8")
    text = replace_placeholders(text, replacements)

    write_text_file(destination_path, text)
    print(f"Created {destination_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
