# Rilavo Protocol - Makefile
# Common development tasks

.PHONY: help test test-cov lint fmt clean install build publish smoke conformance doctor

# Default target
help:
	@echo "Rilavo Protocol - Development Commands"
	@echo ""
	@echo "  make install      - Install dependencies with uv"
	@echo "  make test         - Run test suite"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run linters (ruff, mypy)"
	@echo "  make fmt          - Format code (ruff format)"
	@echo "  make smoke        - Run smoke test"
	@echo "  make conformance  - Run conformance self-check"
	@echo "  make doctor       - Run health check"
	@echo "  make build        - Build distribution packages"
	@echo "  make publish      - Publish to PyPI (requires auth)"
	@echo "  make clean        - Clean build artifacts"

install:
	uv sync --group dev

test:
	uv run pytest tests/ -q

test-cov:
	uv run pytest tests/ --cov=src/rilavo --cov-report=term-missing

lint:
	uv run ruff check .
	uv run mypy src/rilavo

fmt:
	uv run ruff format .

smoke:
	uv run rilavo smoke

conformance:
	uv run rilavo conformance

doctor:
	uv run rilavo doctor

build:
	uv build

publish:
	uv publish

clean:
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
