# Rilavo Protocol — Protocol Economics (P-38)

**Tree:** Protocol
**Wave:** 1 — System Foundation
**Status:** Decided
**Depends on:** None
**Closes when:** Reopens only if a future governance body formally proposes a protocol-level fee — expected, on the reasoning below, to be rejected again if it does.

## The decision

The protocol — credential format, verification standard, revocation log, core API — is free, permanently. Not as a promotional stance. Structurally.

## Why permanent, not just "for now"

Metering the base layer would add friction at exactly the moment network effects need maximum velocity: every additional verifier and issuer makes the format more valuable to the next one, and a fee at that layer taxes the mechanism the entire growth model depends on (see the verification and developer loops in the Product tree, E-19). Every commercial layer built on top — the entire Product tree — depends on the base format being something nobody has to negotiate to use. Charging for it would not just slow adoption; it would quietly convert an open protocol into a metered product, which is precisely the outcome the two-tree separation exists to prevent.

## Where "zero marginal cost" stops being literally true — stated plainly, not hidden

Signature verification is computationally cheap and does approach zero marginal cost per event. Revocation-log storage growth, issuer signing throughput at real scale, and the infrastructure behind the key directory are not free, and this document does not claim they are. "Near-zero marginal cost" is a useful approximation for a single verification event; it is not a claim about the protocol's total operating cost at scale. That distinction matters because pricing decisions in the Product tree (E-14 through E-17) are built on the honest version of this claim, not the rounded-up one.

## Could a future governance body introduce a protocol-level fee?

Technically, yes — nothing in the cryptography prevents it. **Decision: rejected as a direction**, not merely undecided. Nothing about the current economics requires it, and introducing one would hand a future governance body exactly the kind of taxing power over the whole ecosystem that Principle 5 (P-04) and the Boundary Map both exist to foreclose. A governance body that could vote itself a toll on protocol access is a governance body that has quietly become a private owner wearing public-interest language.
