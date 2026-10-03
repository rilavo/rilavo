# Rilavo Protocol — Data Model (P-14)

**Tree:** Protocol
**Wave:** 2 — Engineering Core
**Status:** Decided
**Depends on:** P-06, P-13
**Closes when:** Stable barring a new claim class — a genuinely different data model only becomes necessary at Horizon 3+, not before.

## What's ephemeral, what persists, and what's replicated — three different categories, deliberately not conflated

**Ephemeral (never stored past its own lifetime):** the credential itself. Once it expires, or once a verification event concludes, nothing requires the full credential object to be retained anywhere. A verifier that logs full credentials "just in case" has made a choice this data model doesn't require and P-13 actively discourages.

**Persistent, locally, per-verifier:** audit receipts (P-10) — a hash, an outcome, a timestamp. This is the only thing a verifier is expected to keep long-term.

**Replicated globally:** issuer public keys (via the key directory, P-17) and the revocation log (P-09). Both are safe to replicate widely by design, because neither contains personal data — a public key is meant to be public, and a revocation entry is a hash plus a timestamp plus a reason code.

## Rough scale estimate — order of magnitude, not a commitment

A revocation log entry is roughly 150–200 bytes (per the JSON shape in P-09). At an illustrative pilot volume of 10,000 verification events a day with a 1% revocation rate, that's on the order of 100 new log entries daily — under 20KB a day, trivial to replicate. This estimate exists to make the scaling conversation concrete, not to predict real volume; the honest answer to "how big does this get" is "unknown until a pilot generates real numbers," and this document does not pretend otherwise.

## What is explicitly never part of the data model

Raw personal data of any kind — names, biometrics, device fingerprints, physical addresses. This isn't a data-minimization *policy* bolted onto a data model that could otherwise hold it; there is structurally nowhere in this model for that data to go. If a future claim class (Horizon 3) needs to represent something like "verified age" or "verified organizational role," that's new schema work requiring its own privacy review — not an extension of this model by adding a field.

## Worked example — following one credential through its full lifecycle in storage terms

Issued at `T`, used once at `T+10min`, expires at `T+4h`. At `T+10min`, a verifier creates one audit receipt (persists). At `T+4h`, the credential itself, wherever it was held in memory by the agent, has no further validity and requires no explicit deletion step — it simply stops being usable, since every verifier will reject it on the expiry check alone. Nothing about "letting it expire" requires active data governance the way deleting a stored record would.

## What would change this decision

A future claim class that genuinely can't be represented without persistent, non-ephemeral principal-level state — at which point this document reopens alongside the horizon document that introduced the need, not in isolation.
