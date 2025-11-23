LIBRARY_NAME := $(shell hatch project metadata name 2> /dev/null)
LIBRARY_VERSION := $(shell hatch version 2> /dev/null)

.PHONY: usage install uninstall check pytest qa build-deps check tag wheel sdist clean dist testdeploy deploy
usage:
ifdef LIBRARY_NAME
	@echo "Library: ${LIBRARY_NAME}"
	@echo "Version: ${LIBRARY_VERSION}\n"
else
	@echo "WARNING: You should 'make dev-deps'\n"
endif
	@echo "Usage: make <target>, where target is one of:\n"
	@echo "dev-install:  install the library locally for development"
	@echo "dev-deps:     install Python dev dependencies with UV"
	@echo "format:       format code with ruff (auto-fix)"
	@echo "qa:           run QA checks (ruff + codespell)"
	@echo "pytest:       run Python test fixtures"
	@echo "check:        run basic integrity checks"
	@echo "shellcheck:   lint shell scripts"
	@echo "clean:        clean Python build and dist directories"
	@echo "build:        build Python distribution files"
	@echo "tag:          tag the repository with the current version\n"
	@echo "Note: Use GitHub Actions for PyPI deployment (see PYPI_PUBLISHING.md)\n"

version:
	@hatch version

dev-install:
	@echo "Installing enviroplus-community for development..."
	uv pip install -e .
	@echo "✓ Installed! Use 'enviroplus-setup --install' for hardware configuration"

dev-deps:
	@echo "Installing development dependencies with UV..."
	uv sync --group dev
	@echo "Installing system tools..."
	@command -v shellcheck > /dev/null || sudo apt install shellcheck
	@echo "✓ Dev dependencies installed!"

check:
	@bash check.sh

shellcheck:
	@echo "Linting shell scripts..."
	@shellcheck check.sh 2>/dev/null || echo "⚠ shellcheck not installed (optional)"

qa:
	@echo "Running QA checks..."
	@echo "→ Checking code with ruff..."
	ruff check .
	@echo "→ Checking formatting..."
	ruff format --check .
	@echo "→ Spell checking..."
	codespell
	@echo "✓ All QA checks passed!"

pytest:
	@echo "Running tests..."
	pytest tests/ --cov=enviroplus --cov-report=term-missing

format:
	@echo "Formatting code with ruff..."
	ruff check --fix .
	ruff format .
	@echo "✓ Code formatted!"

nopost:
	@bash check.sh --nopost

tag: version
	git tag -a "v${LIBRARY_VERSION}" -m "Version ${LIBRARY_VERSION}"

build: check
	@hatch build

clean:
	-rm -r dist

testdeploy: build
	twine upload --repository testpypi dist/*

deploy: nopost build
	twine upload dist/*
