# Pyright Dev Type Checking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Pyright as the project-level static type checker, installed through the existing `dev` extra and runnable through `make typecheck`/CI.

**Architecture:** Keep Pyright configuration in `pyproject.toml` beside Ruff so VS Code/Pylance, CLI checks, and CI share the same typing contract. Start with `typeCheckingMode = "standard"` and explicit script import paths; fix the current baseline diagnostics before making the check part of `ci`.

**Tech Stack:** Python 3.11 target, Pyright 1.1.410, Ruff 0.15.16, Make, unittest, GitHub Actions.

---

## Current State

- Branch check: `main`, tracking `origin/main`, clean worktree before planning.
- Dev install check: `make install-dev` succeeds.
- Local venv check: `.venv/bin/python --version` returns `Python 3.14.3`; CI still targets Python 3.11, so Pyright should target `pythonVersion = "3.11"`.
- Ruff check: `.venv/bin/python -m ruff --version` returns `ruff 0.15.16`; `make lint` passes.
- Pyright package check: PyPI reports current `pyright` version `1.1.410`; installing `pyright==1.1.410` into `.venv` succeeds.
- Existing config check: no committed `pyrightconfig.json`, `.vscode/settings.json`, or `[tool.pyright]` exists.
- Raw Pyright check without config: 117 errors, mostly missing imports caused by dynamic script import paths.
- Root-relative trial config with `extraPaths`: 24 errors, all in tractable code/test typing mismatches.

## File Map

- Modify `pyproject.toml`: add `pyright==1.1.410` to `[project.optional-dependencies].dev`; add `[tool.pyright]`.
- Modify `Makefile`: add `.require-pyright`, `typecheck`, help text, and include `typecheck` in `ci`.
- Modify `.github/workflows/ci.yml`: run `make typecheck` after lint and before tests.
- Modify `scripts/tests/test_project_tooling.py`: assert Pyright dependency, config, Makefile target, and CI step.
- Modify `scripts/operations/setup/setup_environment.py`: make `Report.print_summary` signature compatible with `StatusReport.print_summary`.
- Modify `scripts/research-writing/check_external_references.py`: introduce a small HTTP client protocol so test fakes type-check.
- Modify `scripts/tests/helpers.py`: tighten helper annotations from `object` to concrete unittest/argparse types.
- Modify `scripts/tests/test_check_external_references.py`: make `FakeHttpClient` response storage type precise.
- Modify `scripts/tests/test_obsidian_research_plugins.py`: return `argparse.Namespace` from `setup_args_with_releases`.
- Modify `scripts/tests/test_update_skill_plugins.py`: type helper argument as `argparse.Namespace`.
- Modify `scripts/tests/test_render_script.py`: make the fake command runner return `subprocess.CompletedProcess[str]`.

### Task 1: Add Tooling Tests First

**Files:**
- Modify: `scripts/tests/test_project_tooling.py`

- [ ] **Step 1: Update the pyproject tooling assertions**

Change the existing dev dependency assertion to:

```python
self.assertIn('dev = ["ruff==0.15.16", "pyright==1.1.410"]', pyproject)
```

Add Pyright config assertions inside `test_pyproject_declares_python_tooling_defaults`:

```python
self.assertIn("[tool.pyright]", pyproject)
self.assertIn('pythonVersion = "3.11"', pyproject)
self.assertIn('typeCheckingMode = "standard"', pyproject)
self.assertIn('include = ["scripts", "end-2-end-tests/tools", "end-2-end-tests/tests"]', pyproject)
self.assertIn('extraPaths = [', pyproject)
self.assertIn('"scripts/lib"', pyproject)
self.assertIn('"scripts/research-writing"', pyproject)
self.assertIn('"scripts/operations/health"', pyproject)
self.assertIn('"scripts/operations/obsidian"', pyproject)
self.assertIn('"scripts/operations/setup"', pyproject)
self.assertIn('"scripts/operations/skill_plugins"', pyproject)
```

- [ ] **Step 2: Add a Makefile typecheck test**

Add this test after `test_lint_target_runs_compileall_and_ruff`:

```python
def test_makefile_exposes_pyright_typecheck(self) -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    self.assertIn("typecheck", makefile)
    self.assertIn(".require-pyright:", makefile)
    self.assertIn("Pyright is not installed in $(VENV). Run: make install-dev", makefile)
    self.assertIn(
        "typecheck: .require-pyright\n"
        "\t$(VENV_PYTHON) -m pyright",
        makefile,
    )
```

- [ ] **Step 3: Update CI target and workflow assertions**

In `test_ci_target_uses_hosted_safe_checks_without_placeholder_gate`, expect:

```python
self.assertIn(
    "ci: lint typecheck test check-citations check-links check-external-skills check-obsidian-artifacts",
    makefile,
)
```

In `test_github_workflow_uses_descriptive_scaffold_check_steps`, insert:

```python
"Type-check Python scripts and QA tools",
```

and assert:

```python
self.assertIn("run: make typecheck", workflow)
```

- [ ] **Step 4: Run the focused tests and confirm they fail**

Run:

```sh
python3 -m unittest scripts.tests.test_project_tooling
```

Expected: failure because Pyright is not yet declared in `pyproject.toml`, `Makefile`, or CI.

### Task 2: Add Pyright Dependency and Configuration

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add Pyright to the dev extra**

Replace:

```toml
dev = ["ruff==0.15.16"]
```

with:

```toml
dev = ["ruff==0.15.16", "pyright==1.1.410"]
```

- [ ] **Step 2: Add the Pyright config**

Add this section after `[tool.ruff.lint]`:

```toml
[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "standard"
include = ["scripts", "end-2-end-tests/tools", "end-2-end-tests/tests"]
exclude = [
  ".venv",
  ".quarto",
  "exports",
  "manuscript/_book",
  "research_book_boilerplate.egg-info",
  "skill-plugins",
]
extraPaths = [
  "scripts/lib",
  "scripts/research-writing",
  "scripts/operations/health",
  "scripts/operations/obsidian",
  "scripts/operations/setup",
  "scripts/operations/skill_plugins",
]
```

- [ ] **Step 3: Run the focused tooling test**

Run:

```sh
python3 -m unittest scripts.tests.test_project_tooling
```

Expected: remaining failures only for Makefile/CI wiring.

### Task 3: Add `make typecheck`

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Add `typecheck` to `.PHONY`**

Update the `.PHONY` line to include `typecheck` and `.require-pyright`.

- [ ] **Step 2: Add help text**

Add:

```make
	@echo "  typecheck              Run Pyright static type checks"
```

after the existing `lint` help text.

- [ ] **Step 3: Add the Pyright guard and target**

Add this block after `.require-ruff`:

```make
.require-pyright:
	@test -x "$(VENV_PYTHON)" || { \
		echo "Project virtual environment missing. Run: make install-dev"; \
		exit 1; \
	}
	@$(VENV_PYTHON) -m pyright --version >/dev/null 2>&1 || { \
		echo "Pyright is not installed in $(VENV). Run: make install-dev"; \
		exit 1; \
	}

typecheck: .require-pyright
	$(VENV_PYTHON) -m pyright
```

- [ ] **Step 4: Add typecheck to CI target**

Replace:

```make
ci: lint test check-citations check-links check-external-skills check-obsidian-artifacts
```

with:

```make
ci: lint typecheck test check-citations check-links check-external-skills check-obsidian-artifacts
```

- [ ] **Step 5: Run tooling tests**

Run:

```sh
python3 -m unittest scripts.tests.test_project_tooling
```

Expected: remaining failure only for GitHub Actions workflow wiring.

### Task 4: Add CI Workflow Step

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Add the workflow step**

Add this after the lint step:

```yaml
      - name: Type-check Python scripts and QA tools
        run: make typecheck
```

- [ ] **Step 2: Run tooling tests**

Run:

```sh
python3 -m unittest scripts.tests.test_project_tooling
```

Expected: pass.

### Task 5: Fix Pyright Baseline Diagnostics

**Files:**
- Modify: `scripts/operations/setup/setup_environment.py`
- Modify: `scripts/research-writing/check_external_references.py`
- Modify: `scripts/tests/helpers.py`
- Modify: `scripts/tests/test_check_external_references.py`
- Modify: `scripts/tests/test_obsidian_research_plugins.py`
- Modify: `scripts/tests/test_update_skill_plugins.py`
- Modify: `scripts/tests/test_render_script.py`

- [ ] **Step 1: Fix `Report.print_summary` override**

Change:

```python
class Report(StatusReport):
    def print_summary(self) -> None:
        super().print_summary("Final setup report")
```

to:

```python
class Report(StatusReport):
    def print_summary(self, title: str = "Final setup report") -> None:
        super().print_summary(title)
```

- [ ] **Step 2: Add an HTTP client protocol**

In `scripts/research-writing/check_external_references.py`, import `Protocol`:

```python
from typing import Protocol
```

Add this before `class UrlLibHttpClient`:

```python
class HttpClient(Protocol):
    def request(
        self,
        method: str,
        url: str,
        timeout: float,
        headers: dict[str, str],
    ) -> HttpResponse:
        raise NotImplementedError
```

Change the `client` annotation from `UrlLibHttpClient` to `HttpClient` in these functions:

```python
def check_url(reference: Reference, client: HttpClient, timeout: float, dns_attempts: int) -> Finding:
def check_doi(reference: Reference, client: HttpClient, timeout: float, dns_attempts: int) -> Finding:
def check_reference(
    reference: Reference,
    client: HttpClient,
    *,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    dns_attempts: int = DEFAULT_DNS_ATTEMPTS,
    check_archives: bool = False,
    create_archives: bool = False,
    allow_private_url_checks: bool = False,
    allow_private_archive_submission: bool = False,
) -> list[Finding]:
def check_references(
    references: list[Reference],
    client: HttpClient,
    *,
    timeout: float,
    dns_attempts: int,
    check_archives: bool,
    create_archives: bool,
    allow_private_url_checks: bool,
    allow_private_archive_submission: bool,
) -> list[Finding]:
```

- [ ] **Step 3: Tighten helper annotations**

In `scripts/tests/helpers.py`, add:

```python
import argparse
import unittest
```

Change:

```python
test_case: object,
```

to:

```python
test_case: unittest.TestCase,
```

Change:

```python
def install_in_directory(work_dir: Path, args: object, report: setup_environment.Report) -> None:
```

to:

```python
def install_in_directory(work_dir: Path, args: argparse.Namespace, report: setup_environment.Report) -> None:
```

- [ ] **Step 4: Tighten `FakeHttpClient` response type**

In `scripts/tests/test_check_external_references.py`, change:

```python
def __init__(self, responses: dict[tuple[str, str], object]) -> None:
```

to:

```python
def __init__(
    self,
    responses: dict[
        tuple[str, str],
        check_external_references.HttpResponse | check_external_references.ReferenceCheckError,
    ],
) -> None:
```

- [ ] **Step 5: Tighten Obsidian research plugin test args**

In `scripts/tests/test_obsidian_research_plugins.py`, add:

```python
import argparse
```

Change:

```python
def setup_args_with_releases(release_urls: dict[str, str], *extra_args: str) -> object:
```

to:

```python
def setup_args_with_releases(release_urls: dict[str, str], *extra_args: str) -> argparse.Namespace:
```

- [ ] **Step 6: Tighten update skill plugin test args**

In `scripts/tests/test_update_skill_plugins.py`, add:

```python
import argparse
```

Change:

```python
args: object,
```

in `run_update_and_capture_commands` to:

```python
args: argparse.Namespace,
```

- [ ] **Step 7: Use a real `CompletedProcess` in render tests**

In `scripts/tests/test_render_script.py`, replace:

```python
class Result:
    returncode = 1

def runner(command: list[str], check: bool) -> Result:
    calls.append((command, check))
    return Result()
```

with:

```python
def runner(command: list[str], check: bool) -> subprocess.CompletedProcess[str]:
    calls.append((command, check))
    return subprocess.CompletedProcess(command, 1)
```

- [ ] **Step 8: Run Pyright**

Run:

```sh
make typecheck
```

Expected: `0 errors, 0 warnings, 0 informations`.

### Task 6: Refresh Dev Install and Run Verification

**Files:**
- No code changes expected beyond prior tasks.

- [ ] **Step 1: Reinstall dev dependencies from project metadata**

Run:

```sh
make install-dev
```

Expected: installs `ruff==0.15.16` and `pyright==1.1.410` into `.venv`.

- [ ] **Step 2: Verify tool versions**

Run:

```sh
.venv/bin/python -m ruff --version
.venv/bin/python -m pyright --version
```

Expected:

```text
ruff 0.15.16
pyright 1.1.410
```

- [ ] **Step 3: Run focused checks**

Run:

```sh
make lint
make typecheck
python3 -m unittest scripts.tests.test_project_tooling
```

Expected: all pass.

- [ ] **Step 4: Run broader checks**

Run:

```sh
make test
make ci
```

Expected: all pass.

### Task 7: Final Review

**Files:**
- Inspect all modified files.

- [ ] **Step 1: Check diff scope**

Run:

```sh
git diff -- pyproject.toml Makefile .github/workflows/ci.yml scripts/operations/setup/setup_environment.py scripts/research-writing/check_external_references.py scripts/tests/helpers.py scripts/tests/test_check_external_references.py scripts/tests/test_obsidian_research_plugins.py scripts/tests/test_update_skill_plugins.py scripts/tests/test_render_script.py scripts/tests/test_project_tooling.py
```

Expected: only Pyright dependency/config, Makefile/CI wiring, and focused type-annotation fixes.

- [ ] **Step 2: Check working tree**

Run:

```sh
git status --short --branch
```

Expected: only the intentional tracked files changed; `.venv/` and `*.egg-info/` remain ignored.

- [ ] **Step 3: Record remaining risk**

Expected remaining risk to report:

```text
Pyright targets Python 3.11 for CI consistency, while local make install-dev may create .venv from a newer python3 unless the user runs PYTHON=python3.11 make install-dev.
```
