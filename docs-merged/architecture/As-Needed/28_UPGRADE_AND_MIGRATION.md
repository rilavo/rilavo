# Rilavo Protocol — Upgrade & Migration (P-28)

**Tree:** Protocol
**Wave:** Continuous / As-Needed
**Status:** Decided (mechanism, specified below); Deferred (post-quantum work itself — a standing watch item, not active development)
**Depends on:** P-11
**Closes when:** Never fully, by design — this document describes an ongoing capability, not a one-time migration event.

## The mechanism, distinct from an ordinary format version bump

P-26 governs changes to the *credential format's structure* — fields added, removed, or reinterpreted. This document governs changes to the *cryptographic primitive itself* — a genuinely different kind of change, because it affects every credential ever issued, not just future ones written against a new field list.

**How it works:** the credential format's algorithm identifier (referenced but not yet exercised in P-11) becomes a real field the moment a second algorithm exists. A verifier checks this field and applies the matching verification procedure — Ed25519 for `alg: "ed25519"`, whatever a future algorithm requires for its own identifier. This is what "designed in from day one even though only one algorithm is used" (P-11) actually means in practice: the schema has somewhere for a second value to go without needing a structural rewrite when that day comes.

## Worked example — a hypothetical future migration

Suppose a credible post-quantum threat timeline eventually makes migration urgent. New issuers begin signing with a post-quantum algorithm, tagged with its own identifier. Existing verifiers, unaware of the new algorithm, correctly reject credentials using it — a safe, explicit failure, not a silent misinterpretation. Updated verifiers recognize both identifiers during a dual-support period, sized to whatever migration window is deemed appropriate at that time, after which the old algorithm can be formally deprecated per P-26's own deprecation policy.

## Why post-quantum migration itself stays deferred rather than actively worked on now

Not because it's unimportant — because it's not urgent at v0's actual stakes. Credentials are short-lived (P-06) and low-value by design; a cryptographic break that takes years to become practical poses far less risk to hours-long authorization tokens than it would to, say, a permanent identity credential. This is a standing watch item specifically because the risk profile genuinely doesn't justify active engineering effort yet — revisiting that calculus is exactly what "standing watch" means, not "ignored."

## What would change this decision

A credible, dated timeline for practical quantum attacks on Ed25519 becoming public — at which point this moves from a watch item to active engineering work, using the mechanism already specified above rather than needing one invented under pressure.
