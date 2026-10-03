# Rilavo Protocol — Delegation & Attenuation (P-08)

**Tree:** Protocol
**Wave:** 6 — Future Horizons
**Status:** Decided (target design, specified below); **NOT triggered.** This is a specification-in-waiting, not an activation — nothing here ships until the trigger fires.
**Depends on:** P-07
**Closes when:** v0 proves single-hop authorization is actually constraining real integrations — an observed fact, not a date on a calendar.

## Why designing this now doesn't violate the gating principle

There's a real difference between building Horizon 2 into v0 and having a well-reasoned target design ready for when its trigger fires. The former is exactly what this project has repeatedly warned against. The latter means that if and when the trigger fires, the team isn't designing under pressure from a blank page — it's implementing something already reasoned through carefully, adapted from real prior art rather than invented in a rush.

## The target design — adapted from Biscuit and the IETF Agent Identity Protocol draft, not invented fresh

**Credential extension:** a `chain` array, each element one delegation hop, carrying its own scope — a strict subset of its parent hop's scope across four dimensions: tools, budget, domain, and time. A `max_depth` field on the root credential, declared once and enforced at every hop — any chain attempting to exceed it is rejected structurally, not by policy.

**Verification extension to the reference algorithm (core specification, §6):** for a delegated credential, a verifier checks every hop's signature, checks that each hop's scope is a genuine subset of its parent's (never equal in a way that defeats the point of attenuation, never broader), and checks total chain depth against the declared maximum — before proceeding to the same audience, expiry, revocation, and proof-of-possession checks v0 already performs on a single-hop credential.

**Trust levels for delegated completion data**, adopted directly from AIP's model: self-reported, counter-signed, and third-party-attested — letting a verifier judge not just whether a sub-agent was authorized, but how strongly the result it's reporting back can be trusted.

## Worked example — a three-hop chain

A principal authorizes a root agent for `payments.initiate`, `max_depth: 2`. The root agent delegates a narrower grant — `payments.initiate` scoped to a single vendor domain — to a sub-agent. That sub-agent delegates further, attenuating again, to a sub-sub-agent scoped to a single transaction. A verifier checking the final hop confirms: every signature in the chain, strict scope-narrowing at each step, total depth of two respected, and — because completion data from the sub-sub-agent is self-reported rather than counter-signed — treats its result with correspondingly lower trust than it would a counter-signed one.

## What stays genuinely unresolved even in this design

Exact wire-format field names, which would benefit from real integration feedback the project doesn't have yet. Whether a verifier should check the *entire* chain or only the final derived capability — a real, named tradeoff between verification cost and full auditability that the earlier blueprint flagged as open and that remains open here, deliberately not resolved just to make this document look more finished.

## What would change this decision

The trigger firing — real evidence that v0's single-hop model is constraining actual integrations. Until then, this document's only job is to exist, correctly designed, so it doesn't need to be invented under time pressure later.
