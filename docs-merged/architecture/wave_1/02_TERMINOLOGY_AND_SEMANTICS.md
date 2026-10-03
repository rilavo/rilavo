# Rilavo Protocol — Terminology & Semantics (P-02)

**Tree:** Protocol
**Wave:** 1 — System Foundation
**Status:** Decided
**Depends on:** None
**Closes when:** A new term enters the canon only via a decision-log entry, never silently through a later document using it undefined.

## Why this document is P0, not the P1 it might look like

Every specification downstream — the credential format, the authorization model, the threat model — depends on these words meaning exactly one thing each. A glossary that arrives late, after other documents have already used these terms loosely, is far more expensive to fix than one written first.

## Canonical glossary — v0 scope

| Term | Definition | Notes |
|---|---|---|
| **Principal** | The human or organization whose authority is being delegated | Never the same thing as the agent acting on their behalf |
| **Agent** | Software acting on a principal's behalf, holder of a credential | The agent has its own keypair, distinct from the principal's identity |
| **Issuer** | The party that signs a credential attesting a principal's grant | One issuer exists at v0: Rilavo. This is disclosed, not hidden |
| **Verifier** | Any receiving system checking a credential before acting on it | Never needs an account with the issuer to verify |
| **Operator** | An entity running issuer and/or verifier infrastructure | Rilavo Product is one instance of this role, not a distinct or privileged one |
| **Credential / proof** | The signed object itself | Used interchangeably in this project; "credential" is preferred in technical documents |
| **Authorization** | The specific scope — action-class, time, audience — a credential grants | Not identity. A credential proves permission, not who someone "is" |
| **Delegation / attenuation** | A credential deriving from another, narrower or equal in scope, never broader | Out of scope for v0 — see P-08, Horizon 2 |
| **Revocation** | An issuer or principal invalidating a credential before its natural expiry | Independent power — either party alone is sufficient |
| **Expiry** | A credential's built-in, unextendable time limit | The primary defense against a stolen credential, not revocation speed |
| **Nonce** | A single-use value preventing replay | Tracked by the verifier for the credential's validity window |
| **Audit receipt** | A verifier's local record that a specific verification occurred | Never contains the full credential — see the privacy architecture (P-13) |
| **Root proof / sub-agent proof** | A credential issued directly to a principal's primary agent, versus one derived from it | Meaningful only once delegation (Horizon 2) exists |

## What's deliberately not defined here

Terms for Horizon 3+ claim classes — human, content, device, organization — are not defined yet. Defining them before those horizons are reached would manufacture precision the project doesn't have evidence for. When each horizon opens, its own document extends this glossary; this document is not frozen, only disciplined about when it grows.
