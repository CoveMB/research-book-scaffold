#!/usr/bin/env python3
"""Apply, inspect, or clean the synthetic release QA seed fixture."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


END_TO_END_TEST_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_ROOT = END_TO_END_TEST_ROOT / "fixtures" / "release_seed" / "project"
DEFAULT_PROJECT_ROOT = END_TO_END_TEST_ROOT.parent
RESTORE_TARGETS = (
    Path("bibliography/references.bib"),
    Path("manuscript/_quarto.yml"),
    Path("manuscript/index.qmd"),
)


class OperationResult(NamedTuple):
    target: Path
    status: str
    changed: bool


def seed_targets(fixture_root: Path = DEFAULT_FIXTURE_ROOT) -> tuple[Path, ...]:
    return tuple(
        sorted(
            path.relative_to(fixture_root)
            for path in fixture_root.rglob("*")
            if path.is_file()
        )
    )


SEED_TARGETS = seed_targets()


def seed_only_targets(fixture_root: Path = DEFAULT_FIXTURE_ROOT) -> tuple[Path, ...]:
    return tuple(target for target in seed_targets(fixture_root) if target not in RESTORE_TARGETS)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fixture_text(target: Path, fixture_root: Path = DEFAULT_FIXTURE_ROOT) -> str:
    return read_text(fixture_root / target)


def target_matches_fixture(project_root: Path, target: Path, fixture_root: Path = DEFAULT_FIXTURE_ROOT) -> bool:
    target_path = project_root / target
    return target_path.is_file() and read_text(target_path) == fixture_text(target, fixture_root)


def apply_seed(
    project_root: Path = DEFAULT_PROJECT_ROOT,
    *,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    dry_run: bool = False,
) -> list[OperationResult]:
    results: list[OperationResult] = []
    for target in seed_targets(fixture_root):
        source_path = fixture_root / target
        target_path = project_root / target
        source_text = read_text(source_path)
        if target_path.is_file() and read_text(target_path) == source_text:
            results.append(OperationResult(target, "already-current", False))
            continue
        if dry_run:
            results.append(OperationResult(target, "would-write", False))
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(source_text, encoding="utf-8")
        results.append(OperationResult(target, "written", True))
    return results


def seed_status(
    project_root: Path = DEFAULT_PROJECT_ROOT,
    *,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
) -> list[OperationResult]:
    results: list[OperationResult] = []
    for target in seed_targets(fixture_root):
        target_path = project_root / target
        if not target_path.exists():
            results.append(OperationResult(target, "missing", False))
            continue
        if target_matches_fixture(project_root, target, fixture_root):
            results.append(OperationResult(target, "applied", False))
            continue
        results.append(OperationResult(target, "different", False))
    return results


def restore_from_head(project_root: Path, target: Path) -> bool:
    result = subprocess.run(
        ["git", "show", f"HEAD:{target.as_posix()}"],
        cwd=project_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return False
    (project_root / target).write_bytes(result.stdout)
    return True


def remove_seed_only_target(
    project_root: Path,
    target: Path,
    fixture_root: Path,
    dry_run: bool,
) -> OperationResult:
    target_path = project_root / target
    if not target_path.exists():
        return OperationResult(target, "already-absent", False)
    if not target_matches_fixture(project_root, target, fixture_root):
        return OperationResult(target, "manual-review", False)
    if dry_run:
        return OperationResult(target, "would-remove", False)
    target_path.unlink()
    return OperationResult(target, "removed", True)


def restore_tracked_target(
    project_root: Path,
    target: Path,
    fixture_root: Path,
    dry_run: bool,
) -> OperationResult:
    target_path = project_root / target
    if not target_path.exists():
        return OperationResult(target, "missing", False)
    if not target_matches_fixture(project_root, target, fixture_root):
        return OperationResult(target, "manual-review", False)
    if dry_run:
        return OperationResult(target, "would-restore", False)
    if restore_from_head(project_root, target):
        return OperationResult(target, "restored", True)
    return OperationResult(target, "restore-failed", False)


def clean_seed(
    project_root: Path = DEFAULT_PROJECT_ROOT,
    *,
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
    dry_run: bool = False,
) -> list[OperationResult]:
    results = [
        remove_seed_only_target(project_root, target, fixture_root, dry_run)
        for target in seed_only_targets(fixture_root)
    ]
    results.extend(
        restore_tracked_target(project_root, target, fixture_root, dry_run)
        for target in RESTORE_TARGETS
    )
    return results


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["apply", "clean", "status"])
    parser.add_argument("--dry-run", action="store_true", help="Print intended changes without writing.")
    parser.add_argument(
        "--project-root",
        default=str(DEFAULT_PROJECT_ROOT),
        help="Project root to seed. Defaults to this repository root.",
    )
    return parser.parse_args(argv)


def print_results(results: list[OperationResult]) -> None:
    for result in results:
        print(f"{result.status}: {result.target}")


def has_blocker(results: list[OperationResult]) -> bool:
    return any(result.status in {"manual-review", "restore-failed", "different", "missing"} for result in results)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root).expanduser().resolve()
    if args.action == "apply":
        results = apply_seed(project_root, dry_run=args.dry_run)
    elif args.action == "clean":
        results = clean_seed(project_root, dry_run=args.dry_run)
    else:
        results = seed_status(project_root)
        print_results(results)
        return 0
    print_results(results)
    return 1 if has_blocker(results) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
