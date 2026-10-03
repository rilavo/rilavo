#!/usr/bin/env python3
"""P-29 synthetic load-test harness.

SYNTHETIC LOAD TEST -- INFORMATIVE ONLY, NOT VALIDATED PERFORMANCE.

Per docs/As-Needed/29_PERFORMANCE_REQUIREMENTS.md: every number there is a
design TARGET; whether targets survive REAL production-shaped load stays
Open. A synthetic benchmark passing is informative but NEVER sufficient to
call a target validated. This script measures; it does not validate.

What it measures (offline, via the published test kit):
  - local credential verification end-to-end through do_verify, with a FRESH
    proof-of-possession signature per iteration (so replay caching never
    trivializes the work) and a FRESH nonce cache per call (stateless-
    verifier semantics);
  - optionally issuance (--with-issue). Issuance has NO numeric target by
    design ("not the bottleneck"), so its numbers are reported WITHOUT a
    pass/fail verdict.

Reproducibility: the workload shape (N, warmup, target) is fully determined
by flags; credential nonces come from the OS CSPRNG, which is deliberately
not seedable -- timings therefore vary run to run even though the workload
does not. This is stated rather than hidden.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rilavo.api import do_issue, do_verify
from rilavo.keys import generate_keypair
from rilavo.pop import Request, sign_request
from rilavo.testing import offline_test_kit

LABEL = "SYNTHETIC - informative only, NOT validated performance"
DEFAULT_N = 2000
DEFAULT_WARMUP = 100
DEFAULT_TARGET_MS = 10.0   # P-29 component target: local verification sub-10ms


def percentile(sorted_xs, p):
    """Nearest-rank percentile on a pre-sorted list."""
    if not sorted_xs:
        return None
    idx = min(len(sorted_xs) - 1, max(0, int(round(p / 100 * len(sorted_xs))) - 1))
    return sorted_xs[idx]


def stats_ms(latencies_ms):
    s = sorted(latencies_ms)
    return {
        "n": len(s),
        "p50_ms": round(percentile(s, 50), 4),
        "p95_ms": round(percentile(s, 95), 4),
        "p99_ms": round(percentile(s, 99), 4),
        "mean_ms": round(statistics.fmean(s), 4),
        "max_ms": round(s[-1], 4),
    }


def run_benchmark(n: int = DEFAULT_N, warmup: int = DEFAULT_WARMUP,
                  target_ms: float = DEFAULT_TARGET_MS,
                  with_issue: bool = False,
                  verifier_id: str | None = None) -> dict:
    """Run the synthetic workload; returns a structured result dict."""
    assert n > 0 and warmup >= 0
    kit = offline_test_kit()
    agent_priv, agent_pub = __import__(
        "rilavo.testing", fromlist=["local_test_agent"]).local_test_agent()

    issued = kit.issue(principal="loadtest", agent_public_key=agent_pub,
                       action_class="data.read")
    audience = issued.fields["aud"]

    def one_request():
        sig, nonce = sign_request(agent_priv, "POST", "/resource", "data.read")
        return Request("POST", "/resource", "data.read", sig, nonce)

    def timed_verify():
        req = one_request()                      # fresh PoP every iteration
        t0 = time.perf_counter_ns()
        result = do_verify(kit.verifier_id, issued, req, kit.key_directory,
                           kit.revocation_log, nonces=__import__(
                               "rilavo.verifier", fromlist=["NonceCache"]).NonceCache())
        dt = (time.perf_counter_ns() - t0) / 1e6
        if not result.accepted:
            raise RuntimeError(f"verify unexpectedly rejected: {result.reason_code}")
        return dt

    for _ in range(warmup):
        timed_verify()

    latencies = [timed_verify() for _ in range(n)]
    results = {
        "label": LABEL,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
        },
        "workload": {"n": n, "warmup": warmup, "fresh_pop_per_iteration": True,
                     "fresh_nonce_cache_per_call": True,
                     "randomness_note": ("credential nonces use the OS CSPRNG "
                                         "(not seedable); workload shape is "
                                         "deterministic, timings are not")},
        "verify": stats_ms(latencies),
        "throughput_verify_per_s": round(n / (sum(latencies) / 1000.0), 1),
        "target_ms": target_ms,
        "target_source": "P-29 component target: local credential verification sub-10ms",
        "target_comparison": {},
        "caveats": [
            "SYNTHETIC workload: single issuer, offline test kit, no network hops.",
            "Informative only -- NOT validated performance. Real-load validation "
            "requires production-shaped traffic (P-29 closing condition).",
            "p99 is reported explicitly because P-29 names tail behavior as the "
            "common failure mode that healthy p50s hide.",
            "Latency is not cost: volume economics are E-16's concern, kept "
            "deliberately separate.",
        ],
    }
    for stat in ("p50", "p95", "p99"):
        results["target_comparison"][f"{stat}_within_target"] = (
            results["verify"][f"{stat}_ms"] <= target_ms)
    results["all_reported_percentiles_within_target"] = all(
        results["target_comparison"].values())

    if with_issue:
        issue_latencies = []
        for _ in range(min(n, 1000)):
            t0 = time.perf_counter_ns()
            do_issue(kit.issuer, principal="loadtest", agent="a",
                     agent_public_key=agent_pub,
                     action_class="data.read", audience=audience)
            issue_latencies.append((time.perf_counter_ns() - t0) / 1e6)
        results["issue"] = stats_ms(issue_latencies)
        # P-29 gives issuance NO numeric target ("not the bottleneck") --
        # so deliberately no pass/fail here, numbers only.
        results["issue"]["target_verdict"] = (
            "none -- P-29 sets no numeric issuance target; 'not the bottleneck' "
            "is testable only against a real agent workflow")

    return results


def human_table(results: dict) -> str:
    v = results["verify"]
    lines = [
        "=" * 72,
        "Rilavo P-29 SYNTHETIC LOAD TEST",
        LABEL,
        "(real-load validation requires production-shaped traffic)",
        "=" * 72,
        f"timestamp : {results['timestamp_utc']}",
        f"env       : python {results['environment']['python']} | "
        f"cpus {results['environment']['cpu_count']} | {results['environment']['platform']}",
        "",
        f"{'operation':<12}{'n':>8}{'p50 ms':>12}{'p95 ms':>12}{'p99 ms':>12}{'max ms':>12}",
        "-" * 68,
        f"{'verify':<12}{v['n']:>8}{v['p50_ms']:>12.4f}{v['p95_ms']:>12.4f}"
        f"{v['p99_ms']:>12.4f}{v['max_ms']:>12.4f}",
        f"{'throughput':<12}{results['throughput_verify_per_s']:>8.1f} verify/s",
        "",
        f"target    : verify < {results['target_ms']} ms  ({results['target_source']})",
        f"comparison: " + ", ".join(
            f"{k}={v}" for k, v in results["target_comparison"].items()),
        f"overall   : {'within target' if results['all_reported_percentiles_within_target'] else 'TARGET EXCEEDED'}"
        "  [synthetic observation only]",
    ]
    if "issue" in results:
        i = results["issue"]
        lines += ["",
                  f"{'issue':<12}{i['n']:>8}{i['p50_ms']:>12.4f}{i['p95_ms']:>12.4f}"
                  f"{i['p99_ms']:>12.4f}{i['max_ms']:>12.4f}",
                  f"issue verdict: {i['target_verdict']}"]
    lines += ["", "Caveats:"]
    lines += [f"  - {cv}" for cv in results["caveats"]]
    return chr(10).join(lines)


def build_report(results: dict) -> str:
    """Compose the markdown report body without writing to disk."""
    return "# P-29 Synthetic Load Test Report\n\n**" + LABEL + ".**\n\n" \
           "Synthetic numbers never substitute for pilot data.\n\n```\n" \
           + human_table(results) + "\n```"


def write_report(results: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "# P-29 Synthetic Load Test Report\n\n**" + LABEL + ".**\n\n" \
           "Synthetic numbers never substitute for pilot data; P-29 treats a " \
           "synthetic benchmark as informative but NOT sufficient to call " \
           "targets validated.\n\n```\n" + human_table(results) + "\n```\n\n" \
           "## Machine-readable results\n\n```json\n" \
           + json.dumps(results, indent=2) + "\n```\n"
    path.write_text(body)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=DEFAULT_N,
                    help=f"timed verify iterations (default {DEFAULT_N})")
    ap.add_argument("--warmup", type=int, default=DEFAULT_WARMUP)
    ap.add_argument("--target-ms", type=float, default=DEFAULT_TARGET_MS,
                    help="P-29 verify target, passed in as a parameter")
    ap.add_argument("--with-issue", action="store_true",
                    help="also benchmark issuance (reported without verdict)")
    ap.add_argument("--json", action="store_true", help="emit JSON to stdout")
    ap.add_argument("--report", default=None,
                    help="write markdown report here (default pilot/LOADTEST_REPORT.md)")
    ap.add_argument("--no-report", action="store_true")
    args = ap.parse_args(argv)

    results = run_benchmark(n=args.n, warmup=args.warmup,
                            target_ms=args.target_ms, with_issue=args.with_issue)
    if args.json:
        print(json.dumps(results, indent=2))
    print(human_table(results))
    if not args.no_report:
        default_path = Path(__file__).resolve().parents[1] / "pilot" / "LOADTEST_REPORT.md"
        out = write_report(results, Path(args.report) if args.report else default_path)
        print(f"\nreport written: {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
