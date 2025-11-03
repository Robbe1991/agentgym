.PHONY: help install install-dev test test-cov lint format type-check check clean clean-build docs docs-serve build publish

help:
	@echo "AgentGym Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install core dependencies"
	@echo "  make install-dev    Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test           Run tests"
	@echo "  make test-cov       Run tests with coverage"
	@echo "  make lint           Run all linters"
	@echo "  make format         Auto-format code"
	@echo "  make type-check     Run type checking"
	@echo "  make check          Run all quality checks (lint + type + test)"
	@echo ""
	@echo "Clean:"
	@echo "  make clean          Remove cache files"
	@echo "  make clean-build    Remove build artifacts"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs           Build documentation"
	@echo "  make docs-serve     Serve docs locally"
	@echo ""
	@echo "Release:"
	@echo "  make build          Build distribution"
	@echo "  make publish        Publish to PyPI"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest

test-cov:
	pytest --cov=agentgym --cov-report=html --cov-report=term-missing

lint:
	@echo "Running black..."
	black --check .
	@echo "Running ruff..."
	ruff check .

format:
	@echo "Formatting with black..."
	black .
	@echo "Fixing with ruff..."
	ruff check --fix .

type-check:
	mypy src/agentgym

check: lint type-check test
	@echo "All checks passed!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf htmlcov/
	rm -rf .coverage

clean-build: clean
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

docs:
	mkdocs build

docs-serve:
	mkdocs serve

build: clean-build
	python -m build

publish: build
	python -m twine upload dist/*

# Development shortcuts
dev-setup: install-dev
	@echo "Development environment ready!"

run-example:
	python examples/basic_training.py

watch-test:
	pytest-watch
