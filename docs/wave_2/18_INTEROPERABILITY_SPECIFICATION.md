# Rilavo Protocol — Interoperability Specification (P-18)

**Tree:** Protocol
**Wave:** 2 — Engineering Core
**Status:** Decided (posture); Open (which adjacent standard, if any, becomes dominant)
**Depends on:** P-07
**Closes when:** Revisited every time CIMD, ID-JAG, auth.md, or AAuth stabilize into wide adoption — this document tracks a moving field, deliberately.

## The posture

Rilavo is complementary to OAuth 2.1, not a competitor to it. It reuses OAuth's hard-won security lessons — audience restriction (RFC 8707), the general discipline around proof-of-possession — rather than reinventing them, while solving the specific stateless, non-interactive, machine-to-machine case OAuth 2.1 wasn't built for.

## Comparison, on the dimensions that actually matter for this decision

| | Rilavo v0 | OAuth 2.1 (client credentials) | Biscuit | AIP (draft) |
|---|---|---|---|---|
| Statelessness | Full — no session, no refresh cycle | Partial — token issuance is stateless, but refresh/rotation is stateful | Full | Full |
| Built for autonomous agents | Yes, from the start | No — retrofitted | Partially | Yes, from the start |
| Delegation/attenuation | Not yet (Horizon 2) | Not natively | Yes, native (Datalog-based) | Yes, native (IBCTs) |
| Revocation mechanism | Append-only hash-chained log | Token introspection endpoint (stateful) | Not specified centrally | Not fully specified |
| Real-world maturity, 2026 | New | Extremely mature, widely deployed | Emerging, real production use | Draft |

## MCP as the first integration surface

A natural fit precisely because the current MCP specification treats authentication as optional, and most real implementations skip it — independent measurements put roughly 38–40% of exposed MCP servers with no declared authentication at all, worse under dynamic enforcement testing. Rilavo slots in as the authorization layer MCP declines to mandate, rather than competing with anything MCP already does well.

## Compatibility during a transition period — decided explicitly, not left implicit

A verifier can and should be able to accept both an OAuth token and a Rilavo credential in parallel, treating them as independent authentication mechanisms rather than requiring a hard cutover from one to the other. This is a deliberate decision: forcing an all-or-nothing migration would be a real adoption barrier for exactly the audience (§P-03) this protocol needs first.

## What's tracked, not adopted, and why

CIMD, ID-JAG, and AAuth are all live 2026 attempts at overlapping problems from different angles. None is a v0 dependency. **Decision:** Rilavo publishes a compatibility note against each as they stabilize, rather than betting the credential format on any one becoming dominant before the field consolidates — committing early to interoperate with a draft that later gets abandoned would cost more than waiting for real signal.

## What would change this decision

Any one of the tracked standards reaching wide, durable adoption would move it from "track" to "publish a formal compatibility layer for" — a decision this document is structured to make easy to revisit without needing to reopen the whole interoperability posture.
