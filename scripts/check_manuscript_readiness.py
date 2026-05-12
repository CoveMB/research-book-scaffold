#!/usr/bin/env python3
"""Check whether scaffold manuscript entries still block release readiness."""

from __future__ import annotations

import sys
from pathlib import Path

from project_config import change_to_project_root
from script_utils import read_text


QUARTO_CONFIG = Path("manuscript/_quarto.yml")
SCAFFOLD_TITLE = "Untitled Scholarly Manuscript"
SAMPLE_CHAPTER = "chapters/01-chapter-template.qmd"
SAMPLE_APPENDIX = "appendices/appendix-template.qmd"


def readiness_findings(config_text: str) -> list[str]:
    findings: list[str] = []
    if SCAFFOLD_TITLE in config_text:
        findings.append("manuscript title is still Untitled Scholarly Manuscript")
    if SAMPLE_CHAPTER in config_text:
        findings.append("sample chapter is still included in manuscript/_quarto.yml")
    if SAMPLE_APPENDIX in config_text:
        findings.append("sample appendix is still included in manuscript/_quarto.yml")
    return findings


def main() -> int:
    change_to_project_root()
    if not QUARTO_CONFIG.is_file():
        print(f"FAIL missing {QUARTO_CONFIG}")
        return 1

    findings = readiness_findings(read_text(QUARTO_CONFIG))
    if findings:
        print("Manuscript release-readiness blockers:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("No scaffold manuscript entries found in release configuration.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
