"""D2 conformance self-check CLI: real mechanical checks against local and
HTTP targets; informational posture; exit codes reflect outcomes."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
from rilavo.conformance_cli import render_report  # noqa: E402
import rilavo.conformance_cli as cc               # noqa: E402


def test_local_target_all_checks_pass():
    report = cc.run_local_checks()
    assert len(report.results) == len(cc.HTTP_CHECKS)
    failed = [(r.check_id, r.detail) for r in report.results if r.passed is not True]
    assert not failed, failed
    assert report.all_passed and report.exit_code() == 0


def test_report_language_is_informational_never_certifying():
    from rilavo.conformance_cli import render_report, run_local_checks
    text = render_report(run_local_checks()).lower()
    for banned in ("certified", "certification granted", "approved", "compliant"):
        assert banned not in text, f"certification language found: {banned}"
    assert "informational" in text and "not conformance certification" in text


def test_http_target_full_pass():
    import threading

    from rilavo.service import RilavoService

    svc = RilavoService(port=0).start()
    try:
        report = cc.run_http_checks(svc.url)
        failed = [(r.check_id, r.detail) for r in report.results
                  if r.passed is not True]
        assert not failed, failed
        assert report.exit_code() == 0
    finally:
        svc.stop()


def test_dead_port_reports_failure_with_exit_1():
    """A target that cannot be reached produces FAIL rows (with reasons) and
    exit code 1 -- failures are reported, never swallowed."""
    report = cc.run_http_checks("http://127.0.0.1:1")
    assert report.exit_code() == 1
    for r in report.results:
        assert r.passed is False or r.passed is None
        assert r.detail       # every non-pass carries a reason


def test_check_ids_cover_p22_derived_surface():
    ids = {cid for cid, _title, _fn in cc.HTTP_CHECKS}
    assert {"directory", "roundtrip_accept", "wrong_audience",
            "tampered_credential", "scope_mismatch",
            "replay"} <= ids
