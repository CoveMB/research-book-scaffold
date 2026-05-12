.PHONY: help doctor render test check-placeholders check-citations check-citations-strict check-links check-external-skills install-external-skills check-obsidian-codex install-obsidian-codex audit

help:
	@echo "Targets:"
	@echo "  doctor                 Check local tools and scaffold files"
	@echo "  render                 Render manuscript when Quarto is installed"
	@echo "  test                   Run script unit tests"
	@echo "  check-placeholders     Scan Markdown/QMD placeholders"
	@echo "  check-citations        Check manuscript citekeys"
	@echo "  check-citations-strict Check manuscript citekeys and require at least one citation"
	@echo "  check-links            Check wiki-style internal links"
	@echo "  check-external-skills  Check external skill/plugin integration"
	@echo "  install-external-skills Vendor external skills and update marketplace"
	@echo "  check-obsidian-codex   Check Obsidian plugin install in the project root vault"
	@echo "  install-obsidian-codex Install Obsidian plugin in the project root vault"
	@echo "  audit                  Run repository checks"

doctor:
	bash scripts/doctor.sh

render:
	bash scripts/render.sh

test:
	python3 -m unittest discover scripts/tests

check-placeholders:
	python3 scripts/check_placeholders.py .

check-citations:
	python3 scripts/check_citations.py

check-citations-strict:
	python3 scripts/check_citations.py --include-notes --require-citations

check-links:
	python3 scripts/check_broken_internal_links.py

check-external-skills:
	python3 scripts/check_external_skills.py

install-external-skills:
	python3 scripts/install_external_skills.py --yes

check-obsidian-codex:
	python3 scripts/check_obsidian_codex.py

install-obsidian-codex:
	bash scripts/install_obsidian_codex.sh

audit: test check-placeholders check-citations check-links check-external-skills
