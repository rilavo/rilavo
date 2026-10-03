#!/usr/bin/env python3
"""Pilot metrics collector: runs against a live service and emits the data
needed for the pilot readiness report. Reuses observability.Metrics exports.

Usage:
    uv run python scripts/pilot_metrics.py [--cycles 500]
"""

from __future__ import annotations

import json
import sys
import time as _time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rilavo.api import Issuer, do_issue, do_verify
from rilavo.keys import KeyDirectory
from rilavo.pop import Request, sign_request
from rilavo.revocation import RevocationLog
from rilavo.testing import local_test_agent
from rilavo.observability import Metrics
from rilavo.verifier import NonceCache


def collect(cycles=200):
    V = "verifier:pilot-metrics"
    issuer = Issuer()
    d = KeyDirectory()
    d.publish(issuer.directory_entry())
    agent_priv, agent_pub = local_test_agent()
    nonces = NonceCache()

    def issue():
        return do_issue(issuer, principal="pilot:cust-01", agent="agt-metrics",
                        agent_public_key=agent_pub,
                        action_class="data.read", audience=V)

    def check(cred):
        sig, nonce = sign_request(agent_priv, "GET", "/data", "data.read")
        req = Request("GET", "/data", "data.read", sig, nonce)
        return do_verify(V, cred, req, d, RevocationLog(),
                         nonces=NonceCache(), now=cred.fields["iat"] + 1)

    # Warm up:
    for _ in range(10):
        cred = issue()
        r = check(cred)
        assert r.accepted

    # Measure:
    latencies_ms = []
    accept_count = 0
    reject_reasons = {}

    t_start = _time.perf_counter_ns()
    for i in range(cycles):
        cred = issue()
        sig, n = __import__("rilavo.pop", fromlist=["sign_request"]).sign_request(
            agent_priv, "GET", "/data", "data.read")
        req = Request("GET", "/data", "data.read", sig, n)
        t0 = _time.perf_counter_ns()
        result = do_verify(V, cred, req, d, RevocationLog(),
                           nonces=NonceCache(), now=cred.fields["iat"] + 1)
        dt = (_time.perf_counter_ns() - t0) / 1e6
        if not result.accepted:
            reason = result.reason_code
            reject_reasons[reason] = reject_reasons.get(reason, 0) + 1
        else:
            accept_count += 1
        latencies_ms.append(dt)
    total_s = (_time.perf_counter_ns() - t_start) / 1e9

    latencies_ms.sort()
    n = len(latencies_ms)
    p50 = latencies_ms[n // 2]
    p95 = latencies_ms[int(n * 0.95)]
    p99 = latencies_ms[min(n - 1, int(n * 0.99))]

    return {
        "cycles": cycles,
        "accepts": accept_count,
        "rejects": {k: v for k, v in reject_reasons.items()},
        "latency_p50_ms": round(p50, 4),
        "latency_p95_ms": round(p95, 4),
        "latency_p99_ms": round(p99, 4),
        "throughput_per_s": round(cycles / (total_s or 1), 0),
        "credential_bytes": len(json.dumps(cred.fields)),
    }



def compute_wave6_indicators(results):
    """Computes Wave-6 trigger indicators from metrics results."""
    return {
        "indicator_batch_issue_uptake": "requires production traffic",
        "indicator_multi_audience_sessions": "requires production traffic",
        "indicator_reissuance_frequency": "requires production traffic",
        "indicator_cross_verifier_sub_reuse": "requires multi-verifier traffic",
        "note": ("All indicators require production traffic per P-34 trigger. "
                 "Synthetic benchmarks do not satisfy the trigger condition."),
    }


def main():
    cycles = int(sys.argv[sys.argv.index("--cycles") + 1]) \
        if "--cycles" in sys.argv else 200
    show_w6 = "--wave6-indicators" in sys.argv
    results = collect(cycles)

    if show_w6:
        from rilavo.correlation import CorrelationGapMonitor
        w6 = {
            "indicator_batch_issue_uptake": "requires production traffic",
            "indicator_multi_audience_sessions": "requires production traffic",
            "indicator_reissuance_frequency": "requires production traffic",
            "indicator_cross_verifier_sub_reuse": "requires multi-verifier traffic",
            "note": ("All indicators require production traffic per P-34 trigger. "
                     "Synthetic benchmarks do not satisfy the trigger condition."),
        }
        results["wave6_indicators"] = w6

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
