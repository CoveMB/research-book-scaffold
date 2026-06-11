# Pre-commit hooks

Pre-commit hooks catch obvious citation, formatting, Python syntax, and link issues before a commit. They are a writing hygiene aid, not a release gate and not a substitute for source review.

## Install

Install `pre-commit` with your usual Python tooling, then install the hook:

```sh
python3 -m pip install pre-commit
make install-hooks
```

`make install-hooks` runs `pre-commit install --hook-type pre-commit`. If your `pre-commit` executable lives somewhere unusual, pass it through the Makefile variable:

```sh
make PRE_COMMIT="python3 -m pre_commit" install-hooks
```

## Run manually

Run the default commit hooks across the repository:

```sh
make precommit-run
```

Run one hook when you are narrowing down a failure:

```sh
pre-commit run make-check-citations --all-files
```

Run the manuscript readiness hook manually after manuscript setup or before manuscript release review:

```sh
pre-commit run make-check-manuscript-readiness --hook-stage manual --all-files
```

## Blocking hooks

These hooks block a commit when they fail:

- Basic file hygiene from `pre-commit-hooks`: trailing whitespace with Markdown/Quarto hard line breaks preserved, end-of-file fixer, YAML/TOML/JSON syntax checks, merge-conflict marker detection, private-key detection, and a 5 MB large-file guard outside `skill-plugins/` and `exports/`.
- Python compile check: `make lint`.
- Manuscript citation check: `make check-citations`.
- Internal wiki link check: `make check-links`.

The local scholarly hooks call existing Makefile targets. Keep those Makefile targets as the source of truth when check behavior changes.

`make check-citations` can warn when no citations are present without blocking the commit. Strict citation requirements remain release-only.

`make-check-manuscript-readiness` is configured as a manual hook because early scaffold and writing commits can legitimately contain generic manuscript text. Run it before manuscript release review or whenever a manuscript setup pass needs a check.

## Intentional skips

Skip a single hook when you have a reason and will follow up:

```sh
SKIP=make-check-citations git commit
```

Skip all hooks for one commit:

```sh
git commit --no-verify
```

Use skips for intentional checkpoint commits, work-in-progress manuscript setup, or cases where the hook is known to be noisy. Record the unresolved issue in an audit note or follow-up task when it affects scholarship hygiene.

## Release-only checks

These checks stay out of normal pre-commit runs to keep writing commits fast:

- Base scaffold release audit: `make release-audit`.
- Initialized manuscript release audit: `make manuscript-release-audit`.
- Placeholder check: `make check-placeholders`, which remains part of `make audit`, `make release-audit`, and `make manuscript-release-audit`.
- Strict citation pass: `make check-citations-strict`.
- Manuscript readiness enforcement through `make check-manuscript-readiness`, which is included in `make manuscript-release-audit` and available as a manual hook.
- Quarto renders: `make render`, `make render-html`, `make render-pdf`, and `make render-docx`.
- Network-dependent external reference checks: `make check-external-references` and `make external-reference-report`.
- Source, external skill, and integration refresh workflows such as `make install-external-skills`, `make update-skill-plugins`, and setup commands.

Run `make audit` during normal local review, `make release-audit` before scaffold release checks, and `make manuscript-release-audit` before sharing or exporting initialized manuscript work.
