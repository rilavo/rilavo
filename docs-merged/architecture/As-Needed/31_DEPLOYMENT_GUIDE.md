# Rilavo Protocol — Deployment Guide (P-31)

**Tree:** Protocol
**Wave:** Continuous / As-Needed
**Status:** Decided
**Depends on:** P-19, P-20
**Closes when:** Updated as new deployment paths are added — a living guide, not a one-time document.

## Three paths, and how to choose

**Hosted issuance (via Rilavo Product or another operator).** Choose this if the team has no dedicated security engineering capacity and wants to avoid owning key custody and uptime (E-08's exact framing, restated here from the protocol side rather than the commercial one).

**Self-hosted issuance (P-32).** Choose this if the team has the security engineering capacity to run the P-32 checklist properly, or has specific data-residency or independence requirements a hosted option can't satisfy.

**Embedded, verification-only.** For a system that only ever needs to *check* credentials, never issue them — no issuer infrastructure required at all. This is the lightest possible integration: a verifier needs only the SDK (P-20) and a way to fetch the relevant issuer's public key (P-17), nothing more.

## Worked example — matching a scenario to a path

A checkout platform that only ever receives agent traffic and never authorizes its own agents needs only the embedded, verification-only path — no issuer of its own required. A company building and deploying its own fleet of agents that need to authenticate to third-party systems needs issuance, and chooses between hosted and self-hosted based on the criteria above.

## What this guide does not do

Recommend one path as generally superior. Per the anti-lock-in commitments made throughout this project (E-08, P-32), all three are equally legitimate, equally supported choices — this document's job is helping someone pick correctly for their own situation, not steering them toward whichever path is commercially preferable for Rilavo Product.

## Edge case — starting on one path, moving to another

Already specified in detail at E-08 (managed-to-self-hosted migration) — this document doesn't duplicate that mechanism, only confirms it applies symmetrically regardless of which path someone starts on.

## What would change this decision

A genuinely new deployment shape emerging that doesn't fit any of the three paths above — at which point this guide gains a fourth path, rather than forcing a new pattern into an existing category it doesn't actually match.
