# Rilavo Protocol — Versioning (P-26)

**Tree:** Protocol
**Wave:** 2 — Engineering Core
**Status:** Decided (policy)
**Depends on:** P-06
**Closes when:** Exercised, not closed, at the first breaking change — a versioning policy is only really tested the first time it's used under real pressure.

## Version negotiation mechanism

A `ver` field is reserved in the credential format (not listed in P-06's v0 table because v0 has only one version and an implicit `ver: 1` is assumed when absent — the field exists in the schema's design space, ready to be made explicit the moment a second version exists, without requiring a structural change to add it then).

## Policy

Semantic versioning at the wire-format level. The credential format is explicitly not frozen (P-06) until it survives one production partner's real traffic. Once frozen, breaking changes require a new major version that verifiers opt into — never a silent change applied to an existing version.

## What counts as breaking versus non-breaking

**Breaking:** removing a required field, changing a field's type or meaning, changing the canonicalization or signing procedure.
**Non-breaking:** adding a new optional field that older verifiers can safely ignore, clarifying documentation without changing wire behavior.

## Worked example — a hypothetical future breaking change

Suppose a future version needs a genuinely new required field for a Horizon 3 claim class. That becomes `ver: 2`. A `ver: 1` verifier encountering a `ver: 2` credential rejects it as an unrecognized version — a clear, explicit failure, not a silent misinterpretation of fields it doesn't understand. A `ver: 2` verifier can still be built to accept `ver: 1` credentials during a transition period, by explicit design choice at that time, not by default.

## Deprecation policy

Not yet specified in detail — there is no version to deprecate yet, and inventing a deprecation timeline for a version that doesn't exist would be exactly the kind of manufactured precision this project avoids elsewhere. What is decided: deprecation of a version, when it happens, will be announced with a defined advance-notice period before verifiers are required to stop accepting it — the specific period is a Wave 5/6 decision, made when there's an actual second version to deprecate the first one in favor of.

## Alternatives considered

**No explicit versioning, evolve the format in place:** rejected outright — this is precisely how silent breaking changes happen, and it would directly undermine every verifier's ability to trust that a credential means what its own implementation expects it to mean.

## What would change this decision

The first real breaking change request — at which point this policy either proves itself workable or reveals a gap that gets fixed before `ver: 2` ships, not after.
