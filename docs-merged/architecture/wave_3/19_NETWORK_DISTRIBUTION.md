# Rilavo Product — Network Distribution (E-19)

**Tree:** Product
**Wave:** 3 — Commercial Core
**Status:** Decided
**Depends on:** Protocol Wave 2 loops (verification and AI-agent loops)
**Closes when:** Inherited, not separately closed — this document doesn't introduce a new mechanism, it traces the protocol-level ones through a commercial lens.

## The principle

Product's distribution is mostly a byproduct of protocol adoption working, not a parallel effort requiring its own separate growth engine.

## Worked example — Loop D traced end to end

A checkout platform, Verifier Co., decides to require a valid Rilavo credential on all inbound AI-agent traffic — a decision made for its own risk-management reasons, independent of any Rilavo sales effort aimed at the developers who'll eventually be affected. Somewhere else, a team is building an agent that needs to make purchases through Verifier Co.'s API. Their agent's very first attempt fails — rejected, with a specific, actionable reason (per the API contract, P-19) — not because Rilavo marketed to them, but because Verifier Co.'s own requirement made the rejection happen. That team now has a mechanical, self-discovered reason to integrate issuance. No outreach was required to create that reason; Verifier Co.'s adoption created it automatically.

## Worked example — Loop A traced end to end

The same team, once integrated as an issuer, later builds a second agent that needs to reach a different verifier, Second Co. Second Co. has never required Rilavo credentials before — but because verification requires no account and no cost (P-19), Second Co. can adopt verification with effectively zero friction the moment it sees value in doing so, having already observed the first team's agent showing up with a credential Second Co. didn't ask for but can check for free.

## Why this compounds, not just adds

Each loop cycle doesn't just add one new participant — it makes the *next* cycle easier, because there are more verifiers already checking credentials and more issuers already producing them. This is the actual mechanism behind "network effect," made concrete rather than asserted: the growth rate itself increases as the network grows, not just the absolute count.

## Edge case — a verifier that adopts Rilavo but never tells anyone

**Decided, and important:** this is fine, and expected. Loop D doesn't require Verifier Co. to announce its requirement — the loop fires the moment a real agent attempts to reach it and gets rejected, which happens automatically regardless of whether Verifier Co. did any promotion at all. Distribution here depends on usage, not marketing.

## What this document is honest about not yet knowing

Whether these loops, mechanically sound on paper, actually produce the growth rate they imply once real usage exists — this is exactly the Protocol tree's own Go/No-Go gate finding (P-00): the loops are plausible, not yet proven. This document doesn't restate that finding as resolved just because it's now being described from the commercial side.

## What would change this decision

Real pilot data on how many Loop D "forced" integrations actually convert into active issuers within a defined window, versus how many never follow through — the first real test of whether this document's confidence is earned.
