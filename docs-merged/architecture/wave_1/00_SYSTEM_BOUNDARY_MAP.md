# Rilavo — System Boundary & Connection Map

**Tree:** Connection (cross-tree artifact, not a third 45-document tree)
**Wave:** 1 — System Foundation
**Status:** Decided
**Depends on:** None
**Closes when:** Never, in the ordinary sense — this is a standing constraint, re-audited every time a new Product product is proposed or a new protocol capability ships.

## Why this document exists, and why it isn't a tree

The project has two principal trees, Protocol and Product, by deliberate choice. Their relationship is nonetheless too important to leave scattered — it was originally housed only inside Product documents 39–43, which is where the detailed survival scenarios (fork, better-funded competitor, protocol decline) still live. This document is the compact, fast-reference version of the same boundary, meant to be checked in seconds, not read as a specification.

## Protocol → Product

**May flow:**
- `issue` and `verify` calls, per the core specification
- The revocation log
- Issuer public keys
- Aggregated verification telemetry, for fraud-intelligence purposes only

**Must never flow:**
- Exclusive issuance rights
- Secret or undisclosed governance powers
- Privileged access to any protocol-level data an independent operator could not equally obtain
- Unilateral protocol-modification authority

## Product → Protocol

**May flow:**
- The reference implementation and SDKs
- Interoperability and security research
- Ecosystem funding
- Governance participation — as one voice, not a controlling one

**The one hard constraint governing all of it:** money does not buy governance power. Governance seats are never proportional to funding contributed. This is stated once, here, as a system-level rule — not a clause buried inside a single Product document, because it is the constraint every other boundary decision ultimately depends on.

## The test this document exists to support

Three standing checks (detailed in the Dependency Register) hang directly off this boundary:

1. **Protocol Independence** — can the protocol function without Rilavo Product? Partially true today: issuance is centralized, but credentials are portable.
2. **Product Independence** — can Product survive without exclusive control of the protocol? Not yet proven — the central open risk of the entire project.
3. **Mutual Non-Capture** — can either side become powerful enough to capture the other's governance? Guarded against by the rules above, not yet tested by a real attempt.

If any future document — on either side — would require violating one of the flows above to make sense, that is a signal the document is wrong, not that this map needs an exception.
