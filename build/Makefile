# hexa-physics build/Makefile — verify/test/ci fan-out.

ROOT     := ..
PYTHON   ?= python3
HEXA     ?= hexa
HX       ?= hx

.PHONY: all verify verify-json test test-hexa selftest install-test ci everything help check clean

all: ci

verify:
	@cd $(ROOT) && $(PYTHON) verify/cli.py all

verify-json:
	@cd $(ROOT) && $(PYTHON) verify/cli.py all --json

test:
	@cd $(ROOT) && $(PYTHON) -m pytest tests/ -m auto -v

test-hexa:
	@cd $(ROOT) && $(PYTHON) -m pytest tests/ -m hexa -v

selftest:
	@cd $(ROOT) && HEXA_PHYSICS_ROOT=$$PWD $(HEXA) run cli/hexa-physics.hexa selftest

install-test:
	@$(HX) install $(ROOT) --entry cli/hexa-physics.hexa --as hexa-physics

ci: verify test
	@echo "  ci surface PASSED  -  hexa-physics"

everything: ci
	@echo "  everything PASSED  -  hexa-physics"

check:
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "MISSING: $(PYTHON)"; exit 1; }
	@$(PYTHON) --version
	@echo "OK"

clean:
	@find $(ROOT) -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find $(ROOT) -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

help:
	@echo "hexa-physics/build/Makefile targets:"
	@echo "  verify       run all verifiers (n6 + inventory)"
	@echo "  verify-json  JSON output"
	@echo "  test         pytest -m auto"
	@echo "  selftest     cli/hexa-physics.hexa selftest"
	@echo "  ci           verify + test"
	@echo "  everything   ci surface"
