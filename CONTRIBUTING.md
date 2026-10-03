# Contributing to Rilavo

Thank you for your interest in contributing to Rilavo! This document outlines the process for contributing to the Rilavo Protocol reference implementation.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Search existing issues to avoid duplicates
2. Use the issue templates when available
3. Provide clear reproduction steps
4. Include relevant environment details (OS, Python version, etc.)

### Submitting Changes

1. **Fork the repository** and create a feature branch from `main`
2. **Make your changes** with clear, focused commits
3. **Add tests** for new functionality
4. **Run the test suite**: `uv run pytest tests/ -q`
5. **Run linting**: `uv run ruff check .` (if configured)
6. **Update documentation** if needed
7. **Submit a pull request** with a clear description

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/rilavo.git
cd rilavo

# Install development dependencies
uv sync --group dev

# Run tests
uv run pytest tests/ -q

# Run smoke test
uv run rilavo smoke

# Run conformance
uv run rilavo conformance
```

### Pull Request Guidelines

- Keep PRs focused on a single change
- Write clear commit messages following conventional commits
- Include tests for new features and bug fixes
- Update relevant documentation
- Ensure all CI checks pass

### Security Issues

Please report security vulnerabilities privately to security@rilavo.com rather than creating a public issue.

## Development Standards

### Code Style

- Python: Follow PEP 8, use type hints
- Use `ruff` for linting (if configured)
- Write docstrings for public APIs

### Testing

- All new code must have tests
- Run full test suite before submitting: `uv run pytest tests/`
- Conformance tests must pass: `uv run rilavo conformance`

### Documentation

- Update README.md if CLI changes
- Update relevant .md files in docs/
- Add docstrings for new public functions

## Architecture Decisions

Major architectural changes should be documented as ADRs (Architecture Decision Records) in `docs/adr/`. See existing ADRs for the format.

## Release Process

Releases are managed by maintainers. The process:
1. Update CHANGELOG.md
2. Update version in pyproject.toml
3. Create git tag
4. Publish to PyPI
5. Create GitHub release

## Questions?

Open a discussion or issue for any questions about contributing.

---

*This document is adapted from the Rilavo project governance model. The protocol is designed to be operator-agnostic — Rilavo Enterprise is the first reference operator, not a privileged one.*
