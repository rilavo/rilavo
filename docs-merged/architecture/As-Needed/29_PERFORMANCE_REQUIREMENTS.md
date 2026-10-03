# Rilavo Protocol — Performance Requirements (P-29)

**Tree:** Protocol
**Wave:** Continuous / As-Needed
**Status:** Decided (targets below); Open (whether they hold under real load)
**Depends on:** P-11
**Closes when:** After the first real load test — every number here is a design target, not a measured result.

## Targets, with reasoning per operation rather than one blanket number

| Operation | Target | Reasoning |
|---|---|---|
| Local credential verification | Sub-10ms | Ed25519 signature checks run at microsecond scale; the budget is almost entirely network and application overhead, not cryptography |
| Issuance | Low enough not to be the bottleneck in an agent's request path | No hard number yet — "not the bottleneck" is itself testable once a real agent workflow exists to measure against |
| Revocation-log cache refresh | Within the 5-minute default interval (P-09) | Chosen to bound exposure without requiring a live call per verification |
| Key-directory fetch | Within its own longer refresh interval (P-17) | Key rotation is far rarer than revocation, so this budget is looser by design, not by oversight |

## Where "near-zero marginal cost" stops being a performance claim and becomes a cost claim

Verification latency and verification *cost* are related but distinct — a fast operation can still be expensive at sufficient volume if it's inefficiently implemented. This document only commits to the latency side; E-16's unit-economics framework is where the cost side gets resolved, deliberately kept separate so a fast-but-expensive implementation isn't mistaken for a solved problem here.

## Worked example — what "not the bottleneck" would actually mean

An agent workflow that takes 200ms end-to-end for its own business logic should not become a 500ms workflow because of Rilavo's verification step. If verification adds a measurable, user-noticeable delay to a workflow that would otherwise be fast, that's a failure against this document's actual target, even if it technically clears the "sub-10ms local verification" number — the sub-10ms figure is a component target, not the whole promise.

## What this document does not yet know

Whether these targets survive real production load, especially at the tail — p50 latency looking fine while p99 latency reveals a real problem is a common failure mode in systems that look performant in early testing.

## What would change this decision

The first real load test against production-shaped traffic, not synthetic benchmarks — this document treats a synthetic benchmark passing as informative but not sufficient to call these targets validated.
