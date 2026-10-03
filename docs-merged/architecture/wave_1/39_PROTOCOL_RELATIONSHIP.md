# Rilavo Product — Protocol Relationship (E-39)

**Tree:** Product
**Wave:** 1 — System Foundation
**Status:** Decided
**Depends on:** System Boundary Map, P-05
**Closes when:** Never, in the ordinary sense — re-audited every time a new Product product is proposed, since that's the moment this boundary is most likely to quietly erode.

## The exact interface, restated at the Product document level

Product consumes protocol primitives — `issue` and `verify` calls, the revocation log — and produces protocol-compatible credentials with no more privilege than any other operator could have. This is not a simplification for the sake of this document; it is the literal technical relationship, specified in full in the core specification.

## What flows from the protocol to Product

Verification events, in aggregate, feeding fraud intelligence (E-09). Nothing more privileged than what an independent operator running the same protocol could also observe from their own traffic.

## What must never flow

Anything that would let Product reconstruct an individual principal's identity from protocol-level data alone. This is a harder constraint than it sounds: it means Product's own product development has to be checked against this line before shipping, not just at this document's creation.

## The test that makes this real rather than aspirational

Product must be able to operate without any proprietary protocol privilege. This is stated as a standing test, not a one-time check: if a future audit ever found a privilege that only Rilavo Product held at the protocol layer — a faster verification path, an exclusive data feed, a governance veto — that finding would falsify the entire two-tree structure, not just this one document. Everything else in both trees is built on this test continuing to pass.

## Why this document exists separately from the Boundary Map

The Boundary Map states the constraint once, briefly, as a cross-tree reference. This document exists so the Product tree has its own load-bearing copy of the same constraint — because the risk isn't that the rule is unknown, it's that a future Product product decision gets made without anyone checking it against the rule. Having it live inside the Product tree itself, not only in a separate cross-tree document, makes it harder to miss.
