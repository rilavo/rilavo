"""D4 packaging hygiene: metadata completeness, entry points, container
assets. No Docker required at test time."""

from __future__ import annotations

import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _pyproject() -> dict:
    return tomllib.loads((REPO / "pyproject.toml").read_text())


def test_pyproject_parses_with_complete_metadata():
    data = _pyproject()
    proj = data["project"]
    for field in ("name", "version", "description", "readme", "license",
                  "requires-python", "dependencies"):
        assert field in proj, f"missing {field}"
    assert proj["name"] == "rilavo"
    assert proj["requires-python"].startswith(">=3.10")


def test_console_entry_points_declared():
    scripts = _pyproject()["project"]["scripts"]
    assert scripts["rilavo"] == "rilavo.cli:main"
    assert scripts["rilavo-service"] == "rilavo.service_entry:main"
    assert scripts["rilavo-conformance"] == "rilavo.conformance_cli:main"


def test_src_layout_package_discovery():
    build = _pyproject()["tool"]["hatch"]["build"]["targets"]["wheel"]
    assert build["packages"] == ["src/rilavo"]
    assert (REPO / "src" / "rilavo" / "__init__.py").exists()


def test_dockerfile_exists_non_root():
    dockerfile = (REPO / "Dockerfile").read_text()
    assert "USER rilavo" in dockerfile          # explicit non-root line
    assert "FROM python:3.12-slim" in dockerfile
    # no secrets baked in:
    assert "BEGIN PRIVATE KEY" not in dockerfile
    assert "rlk_" not in dockerfile


def test_dockerignore_exists_and_excludes_secrets_patterns():
    text = (REPO / ".dockerignore").read_text()
    assert ".git" in text and ".venv" in text


def test_service_entry_module_importable_and_runs_offline():
    import subprocess
    import sys
    proc = subprocess.run(
        [sys.executable, "-c",
         "from rilavo.service_entry import main; print('entry ok')"],
        capture_output=True, text=True, timeout=60)
    assert "entry ok" in proc.stdout
