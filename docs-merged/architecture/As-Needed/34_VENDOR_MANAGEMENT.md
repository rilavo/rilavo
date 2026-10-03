# Rilavo Product — Vendor Management (E-34)

**Tree:** Product
**Wave:** Continuous / As-Needed
**Status:** Deferred
**Depends on:** None
**Closes when:** The first real vendor contract — most plausibly a cloud KMS provider (P-12) or an eventual insurance carrier (E-31), neither of which is under contract yet.

## Why this document doesn't invent process the company doesn't have

No vendor relationship exists yet substantial enough to warrant a management policy. The most likely first real vendor — a cloud KMS provider, closing the key-custody gap named honestly in P-12 — hasn't been selected, let alone contracted.

## What's flagged for later, not decided now

Vendor security review requirements, particularly for anything touching signing infrastructure (P-12) or customer data (E-27) — these should inherit the same rigor this project applies to its own architecture, not a lighter standard just because the component is outsourced. Contract terms ensuring a vendor relationship doesn't quietly become a dependency this document's anti-lock-in commitments elsewhere (E-08, P-32) would object to if it were Rilavo's own infrastructure.

## Why the KMS vendor specifically deserves more scrutiny than an ordinary vendor, once selected

A compromised or unreliable KMS provider is functionally equivalent to a compromised or unreliable in-house key-custody practice — the risk doesn't diminish by being outsourced, and this document should treat that vendor relationship with the same severity P-12 already assigns to key management generally, not as routine procurement.

## What would change this decision

An actual vendor contract, most plausibly the KMS provider closing P-12's custody gap — at which point this document records the real terms and real review process used, rather than a generic policy invented in advance of any specific vendor.
