# Security Policy

## What Rilavo is

Rilavo is a stateless, cryptographically signed credential format that lets a
receiving system verify — without a network call — that an AI agent holds a
specific, time-boxed authorization from a specific principal. Credentials are
Ed25519-signed JSON, bound to one audience verifier, single-use per nonce,
revocable via an append-only hash-chained log, and verifiable offline against
a cached public key.

## Supported versions

| Version | Supported | Notes |
|---|---|---|
| 0.1.x (v0 wire format) | Yes | The only version. Per P-26, `ver` absent implies v1; any other version is rejected with `unrecognized_version`. |
| < 0.1 | No | Never publicly released. |

## Reporting a vulnerability

- Contact: **security@rilavo.example** *(PLACEHOLDER format — no public inbox
  is operated yet; reserved for when one exists)*.
- Disclosure window: **OPEN** — deliberately unset pending legal review
  (P-23/E-13). No window length is committed anywhere in this project. Until
  legal sets it, reports receive acknowledgment and best-effort status
  updates.

## Threat model

See [`docs/threat_model_summary.md`](./threat_model_summary.md) for the
P-22 STRIDE traceability matrix: each threat row mapped to its mitigating
module and the named tests that verify it, with coverage status derived from
the actual test suites (nothing claimed covered without an existing test).

The detailed security policy — including the protocol/product boundary
impact analysis — lives in
[`rilavo-protocol/SECURITY.md`](./rilavo-protocol-SECURITY.md).

## Scope boundary

Rilavo verifies authorization ("was this agent allowed to try this"), never
agent conduct ("should it be trusted to behave well"). A correctly authorized
agent behaving badly is out of scope by design (P-22).
