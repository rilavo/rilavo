# Rilavo Protocol — Master Specification (P-00)

**Tree:** Protocol
**Wave:** 1 — System Foundation
**Status:** Open — this is a dashboard, not new content. It does not freeze until P-06, P-07, P-09, and P-22 freeze underneath it.
**Depends on:** P-01, P-02, P-04, P-05 (all Decided)
**Closes when:** The load-bearing Wave 2 core survives one production partner's real traffic without a breaking change.

## What this document is

Not a restatement of every decision — those live in their own documents, and this one links to them rather than duplicates them. This is the index: what exists, what wave it belongs to, and whether it's safe to build against yet.

## Governing definition, repeated here because everything else depends on it

Rilavo is a stateless, cryptographically signed credential format that lets a receiving system verify — without a network call, and without learning anything beyond what the credential discloses — that an agent holds a specific, time-boxed authorization from a specific principal. Rilavo Product is an operator of this protocol, not a privileged component of it.

## Full document status

| ID | Document | Wave | Status |
|---|---|---|---|
| 01 | Mission & Scope | 1 | Decided |
| 02 | Terminology & Semantics | 1 | Decided |
| 03 | Problem & Wedge | 1 | Decided |
| 04 | Protocol Principles | 1 | Decided |
| 05 | Actor & Trust Model | 1 | Decided (v0); Open (principal-held keys) |
| 38 | Protocol Economics | 1 | Decided |
| 39 | Protocol Licensing | 1 | Decided |
| 06 | Credential Specification | 2 | Decided, not yet frozen |
| 07 | Authorization Model | 2 | Decided |
| 09 | Revocation Specification | 2 | Decided (mechanism); Open (fail-open/closed default) |
| 10 | Audit Receipts | 2 | Decided (format); Open (retention vs. erasure) |
| 11 | Cryptographic Specification | 2 | Decided, Confirmed |
| 12 | Key Management | 2 | Decided (mechanism); Open (incident runbook) |
| 13 | Privacy Architecture | 2 | Decided |
| 14 | Data Model | 2 | Decided |
| 15 | Network Architecture | 2 | Decided (v0: one issuer) |
| 17 | Discovery & Key Directory | 2 | Decided (v0) |
| 18 | Interoperability Specification | 2 | Decided (posture); Open (which adjacent standard wins) |
| 19 | API Specification | 2 | Decided |
| 20 | SDK Specification | 2 | Decided (contract); Unknown (target language) |
| 22 | Security Threat Model | 2 | Decided |
| 23 | Security Response Model | 2 | Decided (ladder); Open (disclosure window) |
| 26 | Versioning | 2 | Decided |
| 32 | Self-Hosting Guide | 2 | Decided, launch-critical |
| 16 | Node & Operator Specification | 5 | Deferred |
| 21 | Conformance Tests | 5 | Deferred |
| 24 | Governance | 5 | Decided (Model A now) |
| 25 | Decentralization Trigger | 5 | Decided (primary trigger); Open (secondary thresholds) |
| 33 | Operator Requirements | 5 | Deferred |
| 40 | Ethics & Abuse | 5 | Decided |
| 41 | Regulatory Architecture | 5 | Decided (posture) |
| 42 | Disaster Recovery | 5 | Open |
| 43 | Sunset & Succession | 5 | Decided |
| 44 | Decision Log | 5 | Decided (practice), never closes |
| 45 | Changelog | 5 | Deferred, opens at first release |
| 08 | Delegation & Attenuation | 6 | Decided (direction), gated |
| 34 | Horizon 2 Specification | 6 | Decided (direction), gated |
| 35 | Horizon 3: Human Verification | 6 | Decided (direction), gated |
| 36 | Horizon 3: Content Provenance | 6 | Decided (direction), gated |
| 37 | Horizon 4: Attestation | 6 | Deferred |
| 27 | Backward Compatibility | Continuous | Deferred, honestly empty |
| 28 | Upgrade & Migration | Continuous | Decided (mechanism); Deferred (PQC work) |
| 29 | Performance Requirements | Continuous | Decided (targets); Open (load-tested reality) |
| 30 | Reliability Requirements | Continuous | Open |
| 31 | Deployment Guide | Continuous | Decided |

## Reading this table

Fourteen documents carry a plain "Decided" with no caveat. Eleven more are decided in direction but explicitly Open on a specific number or mechanism — that split is not a weakness in the tree, it's the tree being honest about which parts are architecture and which parts are measurements that don't exist yet. Nothing on this list was marked Decided to make the table look more finished than the project actually is.
