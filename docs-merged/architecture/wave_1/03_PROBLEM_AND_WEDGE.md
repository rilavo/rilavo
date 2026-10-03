# Rilavo Protocol — Problem & Wedge (P-03)

**Tree:** Protocol
**Wave:** 1 — System Foundation
**Status:** Decided
**Depends on:** P-01
**Closes when:** Same condition as P-01 — confirmed by real pilot behavior, not re-argued from first principles each time it's questioned.

## The wedge, stated narrowly on purpose

**Agent authorization across organizational boundaries.** Not "trust." Not "identity." Not "security" in general. A vague trust-layer pitch is unfalsifiable and unbuildable; this one is neither.

## Why this specific wedge, and not one of the alternatives

Three problem candidates existed at the outset: fraud cost from synthetic identities, the agent-authorization gap, and content provenance. Agent authorization was chosen because it is a greenfield problem — unlike KYC (already served, if imperfectly, by Persona, Onfido, Jumio) or content provenance (already has C2PA as prior art), nobody yet owns "prove this agent is authorized." That absence of an incumbent is the entire reason this is a viable wedge rather than a feature request to an existing vendor.

## What existing solutions leave unsolved

OAuth 2.1 solves human-session authorization well. It was never built for autonomous, long-running, non-interactive callers. Service-account and client-credentials patches exist and work, but they require stateful token orchestration — refresh rotation, per-tenant isolation — that's disproportionate for a single, short, scoped machine-to-machine call. A developer facing this gap today either builds a bespoke internal system that doesn't interoperate with anyone else's, or accepts agent traffic without real verification at all.

## Evidence this is a real, current problem — not a future one

Independent 2026 measurements from Wiz Research, Bloomberry, and Censys converge on roughly 38–40% of internet-exposed MCP servers running with no declared authentication. A separate, dynamic audit — testing actual enforcement rather than declared configuration — found over 90% of servers lack working OAuth authentication in practice, because the MCP specification treats authentication as optional. This is the exact failure pattern the wedge is built to make structurally harder to fall into: a stateless, self-verifying credential either checks out or it doesn't, which removes the "declared but not enforced" failure mode entirely.

## Excluded from v0, and the re-entry trigger for each

| Excluded | Re-entry trigger |
|---|---|
| Delegation beyond one hop | Proof that single-hop authorization is actually constraining real integrations, not speculative demand |
| Human verification | An Product market decision that a specific jurisdiction or vertical justifies it (see E-10) |
| Content provenance | Either shipped voluntarily or effectively forced by the EU AI Act's own interoperability deadline |
| Device / software attestation | A specific partner requiring it |
| Organization verification | Federation existing — this needs multi-party corroboration that doesn't exist at v0 |

Each trigger is a fact to be observed, not a date to wait out.
