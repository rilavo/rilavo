# Rilavo Protocol — Conformance Tests (P-21)

**Tree:** Protocol
**Wave:** 5 — Governance & Institutionalization
**Status:** Deferred
**Depends on:** P-06, P-07, P-09
**Closes when:** A second implementation of the protocol is actually proposed — before that, there's nothing for a conformance suite to check compatibility between.

## Why this stays gated

A conformance suite exists to let independent implementations prove they behave the same way. At v0, there is exactly one implementation. Testing it for "conformance" against itself is a tautology, not a useful exercise — the value of this document only exists once there's a second, independent thing to check against the first.

## What can honestly be sketched now

The reference verification algorithm (core specification) already defines exact, named rejection reasons — `audience_mismatch`, `expired`, `invalid_signature`, and so on. A future conformance suite would plausibly test that an independent implementation produces the same accept/reject outcome, with the same reason code, against the same set of test credentials — reusing the offline test issuer and fixed test keypair already required of the SDK (P-20), rather than inventing separate test infrastructure.

## What this document does not attempt

A full test-case enumeration. Building one now, with no second implementation to validate it against, risks encoding assumptions about where implementations are likely to disagree that turn out wrong once a real second implementation actually exists and reveals different, unanticipated disagreement points.

## What would change this document

A second implementation being proposed, in any language, by any party — at which point this becomes the single most urgent open item in the tree, not a passive placeholder, since two disagreeing implementations without a conformance suite to catch it is exactly the fragmentation risk the open-protocol model is supposed to avoid.
