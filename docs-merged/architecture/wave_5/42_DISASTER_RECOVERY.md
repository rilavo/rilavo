# Rilavo Protocol — Disaster Recovery (P-42)

**Tree:** Protocol
**Wave:** 5 — Governance & Institutionalization
**Status:** Decided, illustratively (targets below); Open (validated against real operational history)
**Depends on:** P-15, P-23
**Closes when:** Real operational history either confirms or corrects the targets below.

## The core insight this document is built around

For a stateless-verification design, "protocol availability" mostly means key-directory and revocation-log availability, not issuance availability — a verifier that already has a cached key keeps verifying through an issuance outage (P-15). Recovery targets should reflect that asymmetry directly, not treat every component as equally critical.

## Illustrative targets, with the reasoning shown rather than just the number

**Issuance service — RTO (Recovery Time Objective) of 4 hours.** This number isn't arbitrary: it matches the maximum credential TTL (P-06). If issuance is fully restored within the same window a credential would naturally have remained valid anyway, no legitimate in-flight authorization is lost to the outage that wouldn't have expired regardless — the recovery target and the credential design reinforce each other by construction.

**Revocation log — RPO (Recovery Point Objective) of near-zero.** Data loss here is far more dangerous than data loss in issuance: losing a revocation entry means a credential that should be rejected could be wrongly re-accepted. This asymmetry — tolerant RTO on issuance, near-zero RPO on revocation — is the single most important design decision in this document, and it follows directly from P-09's own fail-closed logic rather than being a separate judgment call.

**Key directory — RPO of zero, RTO measured in minutes.** The directory is small, infrequently changing, and trivially replicable (P-17) — there's no good reason for its recovery target to be looser than "effectively always available."

## Worked example

A regional infrastructure outage takes issuance offline for three hours. Per the RTO above, this is within tolerance — no credential that was validly issued before the outage becomes invalid because of it, and no verifier's ability to check existing credentials is affected at all, since verification depends on the separately-recovered key directory and revocation log, not on issuance being live.

## What this document does not yet know

Whether these targets are actually achievable at the infrastructure Rilavo can realistically operate at this stage, or whether they're aspirational numbers that real incident history will correct downward (more lenient) or upward (stricter, if the credential-loss risk from a real outage turns out worse than modeled here).

## What would change this decision

The first real infrastructure incident, of any severity — which either confirms these targets were achievable or reveals exactly where they weren't, informing a revision grounded in what actually happened rather than what was assumed in advance.
