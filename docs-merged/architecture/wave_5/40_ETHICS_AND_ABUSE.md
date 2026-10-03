# Rilavo Protocol — Ethics & Abuse (P-40)

**Tree:** Protocol
**Wave:** 5 — Governance & Institutionalization
**Status:** Decided
**Depends on:** P-24
**Closes when:** Re-audited at every future horizon (P-34 through P-37) — new claim classes introduce new abuse surfaces this document has to be re-checked against, not assumed to already cover.

## Unacceptable use, named explicitly

Using Rilavo to build a centralized blacklist of excluded people or agents. Using it as a de facto mandatory "real human" certificate that gates ordinary participation in digital life. Any use where a government or platform captures issuance to selectively deny service to specific principals based on identity, viewpoint, or affiliation rather than genuine authorization failure.

## Enforcement mechanism, made concrete

A public reporting channel for suspected abuse — separate from ordinary customer support, reviewed on a faster track than routine governance decisions (P-24), since abuse response has a different urgency profile than a structural protocol change. Review authority sits with the governance body once it exists (P-24); at v0, with the founder, disclosed as such rather than hidden behind more decentralized-sounding language than is currently true.

## Worked example — a hypothetical case, walked through rather than left abstract

A government agency approaches an issuer and requests that a specific list of principals be permanently denied issuance, framed as a compliance requirement. **This is refused.** The distinction this document draws: an issuer *can* decline to issue based on genuine authorization or fraud concerns specific to a request — that's the ordinary function of an issuer exercising judgment. An issuer *cannot* maintain a standing exclusion list applied categorically to specific people or organizations at a third party's direction, because that's the exact centralized-blacklist failure mode named above, regardless of who's asking or how the request is framed.

## Why this line matters more than it might seem to at v0's small scale

At v0, with low stakes and short-lived agent-authorization credentials, this boundary is easy to hold because little is at risk in holding it. It matters precisely because it needs to already be a bright line *before* the protocol has enough real-world weight that violating it would be tempting — a boundary adopted only once refusing it would cost something is not a boundary, it's a negotiating position.

## Edge case — a legitimate law-enforcement request

**Decided:** distinguished from the blacklist scenario above by scope and process. A specific, individually-justified legal request handled through the ordinary liability and disclosure framework (P-05, P-23) is different in kind from a standing, categorical exclusion list — the former is case-by-case accountability; the latter is infrastructure repurposed as a surveillance or exclusion tool. This document does not attempt to resolve every possible edge between these two poles in advance — that's what the review process above exists for.

## What would change this decision

Nothing softens the core boundary. What would genuinely require revisiting: a future claim class (Horizon 3+) introducing a scenario this document's current examples don't anticipate — at which point the *examples* expand, not the underlying principle.
