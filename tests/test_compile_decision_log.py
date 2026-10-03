"""C3/P-44: the compiled decision log regenerates correctly from both
repository logs + register statuses."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "compile_decision_log.py"

spec = importlib.util.spec_from_file_location("compile_decision_log", SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules["compile_decision_log"] = mod
spec.loader.exec_module(mod)


def test_compiled_output_contains_both_repo_sections():
    compiled = mod.compile_all()
    assert "rilavo-protocol (protocol decisions)" in compiled
    assert "rilavo-enterprise (commercial-layer decisions)" in compiled


def test_register_statuses_flow_through_verbatim():
    compiled = mod.compile_all()
    # known register status strings must appear verbatim:
    assert "Closes once legal sets the window" in compiled      # P-23 row
    assert "First load test" in compiled                        # P-29 row
    assert "Reopens only at a post-quantum migration trigger" in compiled
    # infra entries read Decided:
    assert "| Decided |" in compiled


def test_no_hand_edit_note_and_regenerable_header():
    compiled = mod.compile_all()
    assert "NEVER hand-edit" in compiled
    assert "Regenerable artifact" in compiled


def test_idempotent_regeneration(tmp_path):
    out = tmp_path / "DECISION_LOG_COMPILED.md"
    first = mod.compile_all()
    second = mod.compile_all()
    # everything but the generation timestamp is stable across runs:
    strip = lambda s: "\n".join(s.splitlines()[5:])
    assert strip(first) == strip(second)
    write_dashboard = None  # no-op guard
    out.write_text(second)
    reread = out.read_text()
    assert strip(reread) == strip(first)


def test_cli_writes_file(tmp_path):
    import subprocess
    out = tmp_path / "compiled.md"
    proc = subprocess.run([sys.executable, str(SCRIPT),
                           "--out", str(out)],
                          capture_output=True, text=True, timeout=60,
                          cwd=str(REPO))
    assert proc.returncode == 0, proc.stderr
    assert out.exists() and "Compiled Decision Log" in out.read_text()
