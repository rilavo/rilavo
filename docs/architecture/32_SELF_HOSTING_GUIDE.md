# Rilavo Protocol — Self-Hosting Guide (P-32)

**Tree:** Protocol
**Wave:** 2 — Engineering Core (corrected from a later, lower-urgency slot — see note)
**Status:** Decided
**Depends on:** P-06, P-19, P-20
**Closes when:** Must exist and work before v0 launch, not after.

## Why this document's priority was corrected

The original blueprint's own prose said self-hosting "must be possible from day one, not added later," while its priority field read P2 — an internal contradiction the project's own audit process caught. Fixed here: this is Wave 2, not a later convenience, because it's the actual, checkable test of whether "the protocol survives without the company" (P-43) is true or just claimed.

## Requirements checklist for an independent issuer

1. **Generate a keypair** per P-11 and P-12 — Ed25519, from a cryptographically secure random source, stored with access control appropriate to production use.
2. **Implement `POST /issue`** per the P-19 contract — accepting principal, agent, action-class, audience, and TTL, returning a signed credential in the P-06 format.
3. **Publish a key-directory entry** per P-17, at a location any verifier can fetch without needing an account or special permission.
4. **Implement or connect to a revocation log** per P-09 — append-only, hash-chained, publicly readable.
5. **Test against the SDK's offline test issuer** (P-20) before accepting any real traffic — confirming the self-hosted issuer produces credentials that verify correctly against a standard verifier implementation, without ever touching Rilavo's own infrastructure.

## What is explicitly NOT required to self-host

Fraud intelligence, SLA guarantees, compliance packaging, incident response staffing, a developer dashboard. These are Product product (E-06), not protocol requirements — a self-hosted issuer is a complete, valid protocol participant without any of them. Someone reading this guide and concluding they need to replicate Rilavo Product's full product to self-host has misread it; self-hosting the *protocol* is deliberately a much smaller task than operating a commercial service around it.

## Worked example — the actual test that proves this works

A self-hosted issuer, running independently with no connection to Rilavo's infrastructure, issues a credential. A verifier using the standard SDK, having fetched this issuer's key from its independently-published directory entry, correctly accepts a valid request and correctly rejects an invalid one — expired, wrong audience, bad signature — using exactly the same reference verification algorithm (core specification, §6) it would use against a Rilavo-issued credential. If this works, self-hosting is real. If it only works when quietly falling back to Rilavo's infrastructure somewhere in the chain, self-hosting was never actually implemented, only described.

## Migration path

An existing customer moving from Rilavo-hosted issuance to self-hosted: exports their configuration (principal/agent mappings, action-class conventions already in use), stands up their own issuer per the checklist above, and switches which key-directory entry their existing verifiers trust. Credentials already issued under Rilavo's key remain valid until their natural expiry — no forced cutover moment, no window where nothing verifies.

## What would change this decision

Nothing should change this document's priority back down — if a future review found self-hosting quietly harder in practice than this checklist implies, that's a signal to fix the gap, not to deprioritize documenting it.
