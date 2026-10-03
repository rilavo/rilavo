"""P4-D golden-file tests: `rilavo init` output is byte-locked to the
Phase 1-2 middleware integration patterns."""
import subprocess
import sys
from pathlib import Path

import pytest

from rilavo.init_scaffold import FRAMEWORKS, TEMPLATES, scaffold

FIXTURES = Path(__file__).parent / "fixtures" / "init"


def test_all_frameworks_have_golden_fixtures():
    for fw in FRAMEWORKS:
        for name in TEMPLATES[fw]:
            assert (FIXTURES / fw / name).exists(), f"missing golden fixture {fw}/{name}"


@pytest.mark.parametrize("fw", sorted(TEMPLATES))
def test_generated_files_match_golden(tmp_path, fw):
    written = scaffold(fw, tmp_path / "app")
    for path in written:
        expected = (FIXTURES / fw / path.name).read_text(encoding="utf-8")
        assert path.read_text(encoding="utf-8") == expected


def test_unknown_framework_rejected(tmp_path):
    with pytest.raises(ValueError):
        scaffold("django", tmp_path)


def test_refuses_overwrite(tmp_path):
    (tmp_path / "main.py").write_text("existing")
    with pytest.raises(FileExistsError):
        scaffold("fastapi", tmp_path)


def test_cli_end_to_end(tmp_path):
    out = tmp_path / "svc"
    proc = subprocess.run(
        [sys.executable, "-m", "rilavo.cli", "init",
         "--framework", "nextjs", "--dir", str(out), "--project-name", "test-project"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    generated = out / "middleware.ts"
    assert generated.exists()
    assert generated.read_text(encoding="utf-8") == (
        FIXTURES / "nextjs" / "middleware.ts").read_text(encoding="utf-8")
