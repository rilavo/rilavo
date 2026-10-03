# P-29 Synthetic Load Test Report

**SYNTHETIC - informative only, NOT validated performance.**

Synthetic numbers never substitute for pilot data; P-29 treats a synthetic benchmark as informative but NOT sufficient to call targets validated.

```
========================================================================
Rilavo P-29 SYNTHETIC LOAD TEST
SYNTHETIC - informative only, NOT validated performance
(real-load validation requires production-shaped traffic)
========================================================================
timestamp : 2026-10-03T01:55:33.110269+00:00
env       : python 3.11.16 | cpus 2 | Linux-6.8.0-63-generic-x86_64-with-glibc2.39

operation          n      p50 ms      p95 ms      p99 ms      max ms
--------------------------------------------------------------------
verify          2000      0.7151      1.2913      1.4906      2.3083
throughput    1286.0 verify/s

target    : verify < 10.0 ms  (P-29 component target: local credential verification sub-10ms)
comparison: p50_within_target=True, p95_within_target=True, p99_within_target=True
overall   : within target  [synthetic observation only]

Caveats:
  - SYNTHETIC workload: single issuer, offline test kit, no network hops.
  - Informative only -- NOT validated performance. Real-load validation requires production-shaped traffic (P-29 closing condition).
  - p99 is reported explicitly because P-29 names tail behavior as the common failure mode that healthy p50s hide.
  - Latency is not cost: volume economics are E-16's concern, kept deliberately separate.
```

## Machine-readable results

```json
{
  "label": "SYNTHETIC - informative only, NOT validated performance",
  "timestamp_utc": "2026-10-03T01:55:33.110269+00:00",
  "environment": {
    "python": "3.11.16",
    "platform": "Linux-6.8.0-63-generic-x86_64-with-glibc2.39",
    "cpu_count": 2
  },
  "workload": {
    "n": 2000,
    "warmup": 100,
    "fresh_pop_per_iteration": true,
    "fresh_nonce_cache_per_call": true,
    "randomness_note": "credential nonces use the OS CSPRNG (not seedable); workload shape is deterministic, timings are not"
  },
  "verify": {
    "n": 2000,
    "p50_ms": 0.7151,
    "p95_ms": 1.2913,
    "p99_ms": 1.4906,
    "mean_ms": 0.7776,
    "max_ms": 2.3083
  },
  "throughput_verify_per_s": 1286.0,
  "target_ms": 10.0,
  "target_source": "P-29 component target: local credential verification sub-10ms",
  "target_comparison": {
    "p50_within_target": true,
    "p95_within_target": true,
    "p99_within_target": true
  },
  "caveats": [
    "SYNTHETIC workload: single issuer, offline test kit, no network hops.",
    "Informative only -- NOT validated performance. Real-load validation requires production-shaped traffic (P-29 closing condition).",
    "p99 is reported explicitly because P-29 names tail behavior as the common failure mode that healthy p50s hide.",
    "Latency is not cost: volume economics are E-16's concern, kept deliberately separate."
  ],
  "all_reported_percentiles_within_target": true
}
```
