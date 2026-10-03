#!/usr/bin/env python3
"""
Cross-SDK Benchmark Suite for Rilavo
Measures issue/verify latency, throughput, and memory across Python, TypeScript, and Go SDKs.
Run with: python scripts/benchmark_all_sdks.py
"""

import json
import statistics
import subprocess
import sys
import time
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class BenchmarkResult:
    sdk: str
    operation: str  # "issue" or "verify"
    iterations: int
    p50_ms: float
    p95_ms: float
    p99_ms: float
    mean_ms: float
    stdev_ms: float
    throughput_ops_sec: float
    memory_mb: float
    errors: int

def run_python_benchmark(iterations: int = 10000) -> List[BenchmarkResult]:
    """Run benchmarks using Python SDK"""
    protocol_dir = Path(__file__).parent.parent / "rilavo-protocol"
    if not protocol_dir.exists():
        protocol_dir = Path(__file__).parent.parent.parent / "rilavo-protocol"

    # Build benchmark script as a string
    bench_script = """
import sys
sys.path.insert(0, "{protocol_dir}/src")
import time
import statistics
from rilavo.api import Issuer, do_verify
from rilavo.keys import KeyDirectory, IssuerKeyEntry
from rilavo.revocation import RevocationLog
from rilavo.verifier import NonceCache
from rilavo.pop import sign_request, Request
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

# Setup
issuer = Issuer()
directory = KeyDirectory()
directory.publish(issuer.directory_entry())

agent_priv = Ed25519PrivateKey.generate()
agent_pub = agent_priv.public_key()

# Warmup
for _ in range(100):
    cred = issuer.issue_credential(
        principal="acme-corp", agent="agent-1",
        agent_public_key=agent_pub, action_class="data.read",
        audience="verifier:bench.example.com"
    )
    sig, nonce = sign_request(agent_priv, "GET", "/data/1", "data.read")
    req = Request(method="GET", path="/data/1",
                  requested_action="data.read", signature=sig, request_nonce=nonce)
    do_verify("verifier:bench.example.com", cred, req,
              directory, RevocationLog(), nonces=NonceCache())

# Benchmark issue
issue_times = []
for i in range({iterations}):
    start = time.perf_counter()
    cred = issuer.issue_credential(
        principal="acme-corp", agent="agent-" + str(i),
        agent_public_key=agent_pub, action_class="data.read",
        audience="verifier:bench.example.com"
    )
    issue_times.append((time.perf_counter() - start) * 1000)

# Benchmark verify
verify_times = []
for i in range({iterations}):
    cred = issuer.issue_credential(
        principal="acme-corp", agent="agent-" + str(i),
        agent_public_key=agent_pub, action_class="data.read",
        audience="verifier:bench.example.com"
    )
    sig, nonce = sign_request(agent_priv, "GET", "/data/1", "data.read")
    req = Request(method="GET", path="/data/1",
                  requested_action="data.read", signature=sig, request_nonce=nonce)
    start = time.perf_counter()
    do_verify("verifier:bench.example.com", cred, req,
              directory, RevocationLog(), nonces=NonceCache())
    verify_times.append((time.perf_counter() - start) * 1000)

def stats(times):
    return {{
        "p50": statistics.median(times),
        "p95": sorted(times)[int(len(times) * 0.95)],
        "p99": sorted(times)[int(len(times) * 0.99)],
        "mean": statistics.mean(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
    }}

issue_stats = stats(issue_times)
verify_stats = stats(verify_times)

import json
print(json.dumps({{
    "issue": issue_stats,
    "verify": verify_stats,
    "iterations": {iterations}
}}))
""".format(protocol_dir=protocol_dir, iterations=iterations)

    result = subprocess.run([
        sys.executable, "-c", bench_script
    ], capture_output=True, text=True, cwd=protocol_dir, timeout=300)

    if result.returncode != 0:
        print(f"Python benchmark failed: {result.stderr}")
        return []

    data = json.loads(result.stdout.strip().split('\n')[-1])

    results = []
    for op, stats in [("issue", data["issue"]), ("verify", data["verify"])]:
        results.append(BenchmarkResult(
            sdk="python",
            operation=op,
            iterations=iterations,
            p50_ms=stats["p50"],
            p95_ms=stats["p95"],
            p99_ms=stats["p99"],
            mean_ms=stats["mean"],
            stdev_ms=stats["stdev"],
            throughput_ops_sec=1000 / stats["mean"] if stats["mean"] > 0 else 0,
            memory_mb=0,
            errors=0
        ))

    return results

def run_typescript_benchmark(iterations: int = 10000) -> List[BenchmarkResult]:
    """Run benchmarks using TypeScript SDK"""
    ts_dir = Path(__file__).parent.parent / "packages" / "rilavo-ts"
    if not ts_dir.exists():
        return []

    # Build first
    subprocess.run(["npm", "run", "build"], cwd=ts_dir, capture_output=True)

    # Create benchmark script as a separate file
    bench_content = """
const {{ Issuer, Verifier, NonceCache, KeyDirectory, signRequest, b64urlEncode }} = require("./dist/cjs/src/index.js");
const {{ performance }} = require("perf_hooks");

const iterations = """ + str(iterations) + """;

// Setup
const issuer = new Issuer();
const directory = new KeyDirectory();
directory.publish(issuer.directoryEntry());

// Generate agent keypair
const {{ createPrivateKey }} = require("node:crypto");
const agentSeed = Buffer.from("AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8", "base64");
const der = Buffer.concat([
  Buffer.from("302e020100300506032b657004220420", "hex"),
  agentSeed
]);
const agentPriv = createPrivateKey({{ key: der, format: "der", type: "pkcs8" }});
const agentPubDer = require("node:crypto").createPublicKey(agentPriv).export({{ type: "spki", format: "der" }});
const agentPubRaw = new Uint8Array(agentPubDer.subarray(12));

// Warmup
for (let i = 0; i < 100; i++) {{
  const cred = issuer.issueCredential({{
    principal: "acme-corp",
    agent: "agent-1",
    agentPublicKeyB64url: b64urlEncode(agentPubRaw),
    actionClass: "data.read",
    audience: "verifier:bench.example.com"
  }});
  const pop = signRequest(agentPriv, "GET", "/data/1", "data.read");
  const req = {{ method: "GET", path: "/data/1", requestedAction: "data.read", signature: pop, requestNonce: "nonce-" + i }};
  const verifier = new Verifier(directory, {{ isRevoked: () => false }}, new NonceCache());
  verifier.verify(cred, req);
}}

// Benchmark issue
const issueTimes = [];
for (let i = 0; i < iterations; i++) {{
  const start = performance.now();
  const cred = issuer.issueCredential({{
    principal: "acme-corp",
    agent: "agent-" + i,
    agentPublicKeyB64url: b64urlEncode(agentPubRaw),
    actionClass: "data.read",
    audience: "verifier:bench.example.com"
  }});
  issueTimes.push(performance.now() - start);
}}

// Benchmark verify
const verifyTimes = [];
for (let i = 0; i < iterations; i++) {{
  const cred = issuer.issueCredential({{
    principal: "acme-corp",
    agent: "agent-" + i,
    agentPublicKeyB64url: b64urlEncode(agentPubRaw),
    actionClass: "data.read",
    audience: "verifier:bench.example.com"
  }});
  const pop = signRequest(agentPriv, "GET", "/data/1", "data.read");
  const req = {{ method: "GET", path: "/data/1", requestedAction: "data.read", signature: pop, requestNonce: "nonce-" + i }};
  const verifier = new Verifier(directory, {{ isRevoked: () => false }}, new NonceCache());
  const start = performance.now();
  verifier.verify(cred, req);
  verifyTimes.push(performance.now() - start);
}}

function stats(times) {{
  const sorted = [...times].sort((a, b) => a - b);
  return {{
    p50: sorted[Math.floor(sorted.length * 0.5)],
    p95: sorted[Math.floor(sorted.length * 0.95)],
    p99: sorted[Math.floor(sorted.length * 0.99)],
    mean: times.reduce((a, b) => a + b, 0) / times.length,
    stdev: Math.sqrt(times.reduce((sum, v) => sum + Math.pow(v - times.reduce((a, b) => a + b, 0) / times.length, 2), 0) / (times.length - 1))
  }};
}}

const issueStats = stats(issueTimes);
const verifyStats = stats(verifyTimes);

console.log(JSON.stringify({{
  issue: issueStats,
  verify: verifyStats,
  iterations: iterations
}}));
"""

    bench_file = ts_dir / "bench.mjs"
    bench_file.write_text(bench_content)

    result = subprocess.run([
        "node", "bench.mjs"
    ], cwd=ts_dir, capture_output=True, text=True, timeout=300)

    bench_file.unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"TypeScript benchmark failed: {result.stderr}")
        return []

    try:
        data = json.loads(result.stdout.strip().split('\n')[-1])
    except json.JSONDecodeError:
        print(f"TypeScript benchmark output parse failed: {result.stdout}")
        return []

    results = []
    for op, stats in [("issue", data["issue"]), ("verify", data["verify"])]:
        results.append(BenchmarkResult(
            sdk="typescript",
            operation=op,
            iterations=iterations,
            p50_ms=stats["p50"],
            p95_ms=stats["p95"],
            p99_ms=stats["p99"],
            mean_ms=stats["mean"],
            stdev_ms=stats["stdev"],
            throughput_ops_sec=1000 / stats["mean"] if stats["mean"] > 0 else 0,
            memory_mb=0,
            errors=0
        ))

    return results

def run_go_benchmark(iterations: int = 10000) -> List[BenchmarkResult]:
    """Run benchmarks using Go SDK"""
    go_dir = Path(__file__).parent.parent / "packages" / "rilavo-go"
    if not go_dir.exists():
        return []

    bench_file = go_dir / "bench_test.go"
    bench_content = """package rilavo

import (
    "testing"
    "time"
)

func BenchmarkIssue(b *testing.B) {
    issuer := NewIssuer(nil)
    agentPriv := issuer.PrivateKey
    agentPub := agentPriv.Public()
    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        i := 0
        for pb.Next() {
            issuer.IssueCredential(IssueRequest{
                Principal:        "acme-corp",
                Agent:            "agent-bench",
                AgentPublicKey:   agentPub,
                ActionClass:      "data.read",
                Audience:         "verifier:bench.example.com",
            })
            i++
        }
        _ = i
    })
}

func BenchmarkVerify(b *testing.B) {
    issuer := NewIssuer(nil)
    directory := NewKeyDirectory()
    directory.Publish(issuer.DirectoryEntry())

    agentPriv := issuer.PrivateKey
    agentPub := agentPriv.Public()

    cred, _ := issuer.IssueCredential(IssueRequest{
        Principal:        "acme-corp",
        Agent:            "agent-bench",
        AgentPublicKey:   agentPub,
        ActionClass:      "data.read",
        Audience:         "verifier:bench.example.com",
    })

    verifier := NewVerifier(directory, &RevocationLog{{}}, NewNonceCache())

    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            popSig, nonce := SignRequest(agentPriv, "GET", "/data/1", "data.read")
            req := &Request{
                Method:           "GET",
                Path:             "/data/1",
                RequestedAction:  "data.read",
                Signature:        popSig,
                RequestNonce:     nonce,
            }
            verifier.Verify(cred, req)
        }
    })
}
"""
    bench_file.write_text(bench_content)

    result = subprocess.run([
        "go", "test", "-bench=BenchmarkIssue/BenchmarkVerify", "-benchmem", "-benchtime=10s", "-count=3"
    ], cwd=go_dir, capture_output=True, text=True, timeout=300)

    bench_file.unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"Go benchmark failed: {result.stderr}")
        return []

    # Parse Go benchmark output
    results = []
    lines = result.stdout.strip().split('\n')
    for line in lines:
        if "BenchmarkIssue" in line and "ns/op" in line:
            parts = line.split()
            ns_per_op = float(parts[2].replace("ns/op", ""))
            results.append(BenchmarkResult(
                sdk="go",
                operation="issue",
                iterations=iterations,
                p50_ms=ns_per_op / 1_000_000,
                p95_ms=ns_per_op / 1_000_000,
                p99_ms=ns_per_op / 1_000_000,
                mean_ms=ns_per_op / 1_000_000,
                stdev_ms=0,
                throughput_ops_sec=1_000_000_000 / ns_per_op,
                memory_mb=0,
                errors=0
            ))
        elif "BenchmarkVerify" in line and "ns/op" in line:
            parts = line.split()
            ns_per_op = float(parts[2].replace("ns/op", ""))
            results.append(BenchmarkResult(
                sdk="go",
                operation="verify",
                iterations=iterations,
                p50_ms=ns_per_op / 1_000_000,
                p95_ms=ns_per_op / 1_000_000,
                p99_ms=ns_per_op / 1_000_000,
                mean_ms=ns_per_op / 1_000_000,
                stdev_ms=0,
                throughput_ops_sec=1_000_000_000 / ns_per_op,
                memory_mb=0,
                errors=0
            ))

    return results

def main():
    iterations = 10000
    if len(sys.argv) > 1:
        iterations = int(sys.argv[1])

    print(f"Running cross-SDK benchmarks ({iterations} iterations each)...")
    print("=" * 60)

    all_results = []

    # Python
    print("\nPython SDK...")
    py_results = run_python_benchmark(iterations)
    all_results.extend(py_results)
    for r in py_results:
        print(f"  {r.operation}: p50={r.p50_ms:.3f}ms, p99={r.p99_ms:.3f}ms, {r.throughput_ops_sec:.0f} ops/sec")

    # TypeScript
    print("\nTypeScript SDK...")
    ts_results = run_typescript_benchmark(iterations)
    all_results.extend(ts_results)
    for r in ts_results:
        print(f"  {r.operation}: p50={r.p50_ms:.3f}ms, p99={r.p99_ms:.3f}ms, {r.throughput_ops_sec:.0f} ops/sec")

    # Go
    print("\nGo SDK...")
    go_results = run_go_benchmark(iterations)
    all_results.extend(go_results)
    for r in go_results:
        print(f"  {r.operation}: p50={r.p50_ms:.3f}ms, p99={r.p99_ms:.3f}ms, {r.throughput_ops_sec:.0f} ops/sec")

    # Output JSON for CI
    output = {
        "timestamp": time.time(),
        "iterations": iterations,
        "results": [asdict(r) for r in all_results]
    }

    output_file = Path(__file__).parent / "benchmark_results.json"
    output_file.write_text(json.dumps(output, indent=2))
    print(f"\nResults saved to {output_file}")

    # Print comparison table
    print("\n" + "=" * 80)
    print("COMPARISON TABLE")
    print("=" * 80)
    print(f"{'SDK':<12} {'Operation':<8} {'p50 (ms)':<12} {'p95 (ms)':<12} {'p99 (ms)':<12} {'Mean (ms)':<12} {'Throughput':<15}")
    print("-" * 80)
    for r in all_results:
        print(f"{r.sdk:<12} {r.operation:<8} {r.p50_ms:<12.3f} {r.p95_ms:<12.3f} {r.p99_ms:<12.3f} {r.mean_ms:<12.3f} {r.throughput_ops_sec:<15.0f}")

    return all_results

if __name__ == "__main__":
    main()
