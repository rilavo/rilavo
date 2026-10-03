"""Diagnostics module tests."""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

from rilavo import errors as _errors
from rilavo.diagnostics import EXPLANATIONS, Explanation, explain_rejection

# Collect ALL public string constants from errors.py
REASON_CODES = {
    getattr(_errors, name): name
    for name in dir(_errors)
    if name.isupper() and isinstance(getattr(_errors, name), str)
}


class TestExplanationsComplete:

    def test_every_reason_code_has_explanation(self):
        for code in REASON_CODES:
            assert code in EXPLANATIONS, f"missing: {code}"

    def test_non_empty_summary(self):
        for code, exp in EXPLANATIONS.items():
            assert len(exp.summary) > 10, code

    def test_at_least_2_causes(self):
        for code, exp in EXPLANATIONS.items():
            assert len(exp.likely_causes) >= 2, code

    def test_at_least_1_remediation(self):
        for code, exp in EXPLANATIONS.items():
            assert len(exp.remediation) >= 1, code

    def test_non_empty_doc_pointer(self):
        for code, exp in EXPLANATIONS.items():
            assert len(exp.doc_pointer) > 5, code


def test_unknown_raises_keyerror():
    with pytest.raises(KeyError):
        explain_rejection("bogus_code")


def test_known_returns_explanation():
    exp = explain_rejection("expired")
    assert isinstance(exp, Explanation)
    assert len(exp.summary) > 10


class TestCLI:

    def _run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "rilavo.cli", "explain", *args],
            capture_output=True, text=True,
            cwd=str(REPO.parent), timeout=30)

    def test_known_code_exits_zero(self):
        proc = self._run_cli("expired")
        assert proc.returncode == 0
        assert "Summary:" in proc.stdout
        assert "Likely causes:" in proc.stdout

    def test_unknown_code_nonzero_exit(self):
        proc = self._run_cli("bogus_code_xyz")
        assert proc.returncode != 0
        assert "Unknown reason code" in proc.stderr
