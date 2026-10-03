# Rilavo Protocol — Horizon 3: Human Verification (P-35)

**Tree:** Protocol
**Wave:** 6 — Future Horizons
**Status:** Decided (architectural principle only); Open (first market — an Product decision, not made here)
**Depends on:** P-13
**Closes when:** An Product market decision is made, real legal review (E-28, E-29) has happened, and a committed pilot partner exists — three separate preconditions, not one.

## Why this document stays at the principle level, deliberately, unlike P-08

P-08's direction rested on mature, well-tested prior art (Biscuit, AIP) and touched no personal data — designing it in detail carried little risk even before its trigger fires. This document is different in kind: it concerns real human identity, plausibly biometric data, and jurisdictions with serious legal consequences for getting data handling wrong (E-28's own reference to Nigeria's Data Protection Act, which carries criminal penalties, is not incidental context here — it's exactly why this document doesn't go further than principle). A detailed technical spec sitting next to an undecided market and unreviewed legal exposure would misrepresent how settled this actually is.

## The one architectural principle that is decided, and non-negotiable when this horizon does open

Edge-computed, zero-knowledge proofs, from day one — not retrofitted after launch. The verifier learns that a claim is true — a principal meets some threshold or holds some credential — without learning the underlying attribute itself. This is the specific mechanism that lets "is a human real" avoid becoming exactly what it should never become: a central biometric data store.

## The cautionary case this principle is built to avoid repeating

A real venture already live-testing almost this exact model — planetary human-verification, biometric collection, aiming at global scale — has drawn serious regulatory pushback: suspensions and forced data deletion across multiple countries, a GDPR corrective order, an outright ban with exposure to daily fines in at least one jurisdiction. Notably, that same venture's own response to the pressure has been to pivot toward partnering with existing consumer platforms rather than continuing to push a standalone consumer identity product — which is independent, real-world evidence for exactly the distribution posture this project has held from its earliest strategic discussion onward: consumer identity products succeed as something bundled into an existing platform, not as something people are asked to adopt on their own.

## What is genuinely, structurally undecided here

Which market opens first — an Product decision requiring real evaluation this document does not make. Whether any biometric modality is used at all, or whether the claim class can be satisfied through non-biometric attestation instead. The specific claim format and field schema, which shouldn't be designed before the market and legal questions above are settled, unlike P-08 where the design could safely precede the trigger.

## What would need to happen before this document earns P-08's level of technical depth

A market decision (E-10), completed jurisdiction-specific legal review (E-28, E-29), and a committed pilot partner willing to test the architecture in that specific market — in that order, not skipped or reordered for the sake of moving faster.

## What would change this decision

Any of the three preconditions above actually being met — at which point this document graduates to real technical design, informed by a specific market and specific legal findings rather than the general principle stated here.
