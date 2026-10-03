# Rilavo Pilot-Readiness Report

Generated: 2026-10-03T01:55:25.871772+00:00

Simulated first-production-partner workload against v0.
This is a measurable rehearsal of the Go/No-Go gate's open item;
it does not replace a live pilot.

| Gate | Result | Evidence |
|---|---|---|
| G1 | PASS | 0 wrong accepts across 600 deliberately-invalid and 2400 valid credentials; every valid one accepted |
| G2 | PASS | p50=0.484ms p95=1.100ms p99=1.482ms max=5.620ms |
| G3 | PASS | 367 bytes on the wire (HTTP-header safe) |
| G4 | PASS | 8 threads x 150 cycles, 0 anomalies |
| G5 | PASS | valid at t+10 (accept), revoked by principal at t+20 (revoked) |
| G6 | PASS | dir-down->unknown_issuer, log-down->revocation_state_unavailable |

**Overall: ALL GATES PASS** (harness runtime 3.7s)

## Honest scope limits

- Single machine, simulated partner; no live network partners yet.
- Latency figures are local-library calls (the stateless design point);
  they exclude any HTTP hop.
- The Go/No-Go item remains formally 'not yet' until a real external
  integration runs; this report is the pre-pilot evidence base.
