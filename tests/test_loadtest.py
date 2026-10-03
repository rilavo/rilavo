"""P-29 load-test harness smoke tests.

These verify the harness's STRUCTURE and REPORTING — never wall-clock
performance. Timing assertions would be flaky and would conflate a slow CI
machine with a protocol regression; P-29 numbers are design targets whose
validation lives in real production-shaped load, not unit tests.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "loadtest.py"

from scripts.loadtest import (  # noqa: E402
    LABEL,
    build_report,
    human_table,
    percentile,
    run_benchmark,
    stats_ms,
    write_report,
)


def test_benchmark_structure_small_n():
    results = run_benchmark(n=20, warmup=3, target_ms=10.0)
    assert results["label"] == LABEL
    assert "NOT validated" in results["label"]
    v = results["verify"]
    for key in ("n", "p50_ms", "p95_ms", "p99_ms", "mean_ms", "max_ms"):
        assert key in v, f"missing {key}"
    assert v["n"] == 20
    # percentiles ordered sensibly:
    assert v["p50_ms"] <= v["p95_ms"] <= v["p99_ms"] <= v["max_ms"]
    # target comparison present and boolean-valued:
    assert set(results["target_comparison"]) == {
        "p50_within_target", "p95_within_target", "p99_within_target"}
    assert all(isinstance(b, bool) for b in results["target_comparison"].values())
    assert results["all_reported_percentiles_within_target"] == all(
        results["target_comparison"].values())
    assert results["throughput_verify_per_s"] > 0


def test_every_result_carries_the_synthetic_label_and_caveats():
    results = run_benchmark(n=5, warmup=1)
    assert "informative only" in results["label"].lower()
    joined = " ".join(results["caveats"]).lower()
    assert "not validated" in joined
    assert "production-shaped traffic" in joined   # P-29 closing condition
    assert "latency is not cost" in joined         # latency/cost separation
    env = results["environment"]
    for key in ("python", "platform", "cpu_count"):
        assert key in env


def test_issue_benchmark_reports_numbers_but_never_a_verdict():
    """P-29 deliberately sets NO numeric issuance target; the harness must
    not invent one."""
    results = run_benchmark(n=5, warmup=1, with_issue=True)
    assert "p50_ms" in results["issue"]
    assert "no numeric issuance target" in results["issue"]["target_verdict"]


def test_percentile_helper_nearest_rank():
    xs = sorted([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    assert percentile(xs, 50) == 5.0
    assert percentile(xs, 100) == 10.0
    assert percentile([], 50) is None


def test_stats_and_report_generation(tmp_path):
    results = run_benchmark(n=10, warmup=2)
    table = human_table(results)
    assert "SYNTHETIC" in table and "NOT validated" in table
    assert "p99" in table or "p99_ms" in table

    out = tmp_path / "report.md"
    written = write_report(results, out)
    text = written.read_text()
    assert "NOT validated" in text
    assert '"p99_ms"' in text                       # embedded machine-readable JSON
    parsed = json.loads(text.split("```json\n")[1].split("\n```")[0])
    assert parsed["verify"]["p95_ms"] >= parsed["verify"]["p50_ms"]

    # build_report composes the same content without touching disk:
    assert "SYNTHETIC" in build_report(results)


def test_cli_smoke_run_end_to_end(tmp_path):
    """Acceptance criterion: runnable via uv run python scripts/loadtest.py."""
    report_path = tmp_path / "LOADTEST.md"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--n", "30", "--warmup", "3",
         "--no-report"],
        capture_output=True, text=True, timeout=120)
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 0, combined
    assert "SYNTHETIC" in proc.stdout
    assert "p50" in proc.stdout and "p99" in proc.stdout


def test_cli_json_output_valid(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--n", "20", "--warmup", "2",
         "--json", "--no-report"],
        capture_output=True, text=True, timeout=120)
    # JSON block is on stdout before the human table:
    first_line_to_end = proc.stdout
    obj_start = first_line_to_end.index("{")
    obj_end = first_line_to_end.index("}") + 1
    # find the complete JSON document (pretty-printed, ends at last closing brace
    # before the table separator):
    doc = first_line_to_end[obj_start:first_line_to_end.rindex("}") + 1]
    parsed = json.loads(doc)
    assert {"p50_ms", "p95_ms", "p99_ms"} <= set(parsed["verify"])
    assert parsed["label"] == LABEL
