PRE_COMMIT ?= pre-commit

.PHONY: help start-project doctor render render-html render-pdf render-docx test lint check-placeholders check-citations check-citations-strict check-links check-external-references external-reference-report check-manuscript-readiness check-external-skills install-external-skills install-subagent-orchestrator update-skills-vendors check-obsidian-panel check-obsidian-artifacts install-obsidian-panel install-hooks precommit-run audit release-audit ci

help:
	@echo "Targets:"
	@echo "  start-project          Initialize a real scholarly project from guided answers"
	@echo "  doctor                 Check local tools and scaffold files"
	@echo "  render                 Render manuscript when Quarto is installed"
	@echo "  render-html            Render manuscript HTML only"
	@echo "  render-pdf             Render manuscript PDF only"
	@echo "  render-docx            Render manuscript DOCX only"
	@echo "  test                   Run script unit tests"
	@echo "  lint                   Compile-check local Python scripts"
	@echo "  check-placeholders     Scan Markdown/QMD placeholders"
	@echo "  check-citations        Check manuscript citekeys"
	@echo "  check-citations-strict Check manuscript citekeys and require at least one citation"
	@echo "  check-links            Check wiki-style internal links"
	@echo "  check-external-references Check external URLs and DOIs without archive lookup"
	@echo "  external-reference-report Write an external-reference JSON report"
	@echo "  check-manuscript-readiness Check release manuscript files for scaffold entries"
	@echo "  check-external-skills  Check external skill/plugin integration"
	@echo "  install-external-skills Vendor external skills and update marketplace"
	@echo "  install-subagent-orchestrator Refresh guarded subagent wrappers and marketplace"
	@echo "  update-skills-vendors  Fast-forward skill vendors and refresh integrations"
	@echo "  check-obsidian-panel   Check Codex Panel install in the project root vault"
	@echo "  check-obsidian-artifacts Check .base and .canvas Obsidian artifacts"
	@echo "  install-obsidian-panel Install Codex Panel in the project root vault"
	@echo "  install-hooks          Install local pre-commit hooks"
	@echo "  precommit-run          Run pre-commit hooks across the repository"
	@echo "  audit                  Run repository checks"
	@echo "  release-audit          Run strict manuscript readiness checks"
	@echo "  ci                     Run checks suitable for hosted CI"

start-project:
	python3 scripts/start_project.py

doctor:
	bash scripts/operations/health/doctor.sh

render:
	bash scripts/research-writing/render.sh

render-html:
	bash scripts/research-writing/render.sh --to html

render-pdf:
	bash scripts/research-writing/render.sh --to pdf

render-docx:
	bash scripts/research-writing/render.sh --to docx

test:
	python3 -m unittest discover scripts/tests
	python3 -m unittest discover end-2-end-tests/tests

lint:
	python3 -m compileall -q scripts end-2-end-tests/tools end-2-end-tests/tests

check-placeholders:
	python3 scripts/research-writing/check_placeholders.py .

check-citations:
	python3 scripts/research-writing/check_citations.py

check-citations-strict:
	python3 scripts/research-writing/check_citations.py --include-notes --require-citations

check-links:
	python3 scripts/research-writing/check_broken_internal_links.py

check-external-references:
	python3 scripts/research-writing/check_external_references.py

external-reference-report:
	python3 scripts/research-writing/check_external_references.py --json-report reports/external-reference-check.json

check-manuscript-readiness:
	python3 scripts/research-writing/check_manuscript_readiness.py

check-external-skills:
	python3 scripts/operations/vendors/check_external_skills.py

install-external-skills:
	python3 scripts/operations/vendors/install_external_skills.py --yes

install-subagent-orchestrator:
	python3 scripts/operations/vendors/install_external_skills.py --yes --skip-ars --skip-rbs --skip-obsidian-skills

update-skills-vendors:
	bash scripts/operations/vendors/update-skills-vendors.sh

check-obsidian-panel:
	python3 scripts/operations/obsidian/check_obsidian_panel.py

check-obsidian-artifacts:
	python3 scripts/operations/obsidian/check_obsidian_artifacts.py

install-obsidian-panel:
	bash scripts/operations/obsidian/install_obsidian_panel.sh

install-hooks:
	$(PRE_COMMIT) install --hook-type pre-commit

precommit-run:
	$(PRE_COMMIT) run --all-files --show-diff-on-failure

audit: test check-placeholders check-citations check-links check-external-skills check-obsidian-artifacts

release-audit: test check-placeholders check-citations-strict check-links check-manuscript-readiness check-external-skills check-obsidian-artifacts

ci: lint audit
