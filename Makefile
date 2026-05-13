.PHONY: help doctor render render-html render-pdf render-docx test lint check-placeholders check-citations check-citations-strict check-links check-manuscript-readiness check-external-skills install-external-skills install-subagent-orchestrator update-skills-vendors check-obsidian-codex install-obsidian-codex audit release-audit

help:
	@echo "Targets:"
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
	@echo "  check-manuscript-readiness Check release config for scaffold manuscript entries"
	@echo "  check-external-skills  Check external skill/plugin integration"
	@echo "  install-external-skills Vendor external skills and update marketplace"
	@echo "  install-subagent-orchestrator Install optional subagent plugin in project scope"
	@echo "  update-skills-vendors  Fast-forward skill vendors and refresh integrations"
	@echo "  check-obsidian-codex   Check Obsidian plugin install in the project root vault"
	@echo "  install-obsidian-codex Install Obsidian plugin in the project root vault"
	@echo "  audit                  Run repository checks"
	@echo "  release-audit          Run strict manuscript readiness checks"

doctor:
	bash scripts/doctor.sh

render:
	bash scripts/render.sh

render-html:
	bash scripts/render.sh --to html

render-pdf:
	bash scripts/render.sh --to pdf

render-docx:
	bash scripts/render.sh --to docx

test:
	python3 -m unittest discover scripts/tests

lint:
	python3 -m compileall -q scripts

check-placeholders:
	python3 scripts/check_placeholders.py .

check-citations:
	python3 scripts/check_citations.py

check-citations-strict:
	python3 scripts/check_citations.py --include-notes --require-citations

check-links:
	python3 scripts/check_broken_internal_links.py

check-manuscript-readiness:
	python3 scripts/check_manuscript_readiness.py

check-external-skills:
	python3 scripts/check_external_skills.py

install-external-skills:
	python3 scripts/install_external_skills.py --yes

install-subagent-orchestrator:
	python3 scripts/install_external_skills.py --yes --skip-ars --skip-rbs --install-subagent-orchestrator

update-skills-vendors:
	bash scripts/update-skills-vendors.sh

check-obsidian-codex:
	python3 scripts/check_obsidian_codex.py

install-obsidian-codex:
	bash scripts/install_obsidian_codex.sh

audit: test check-placeholders check-citations check-links check-external-skills

release-audit: test check-placeholders check-citations-strict check-links check-manuscript-readiness check-external-skills
