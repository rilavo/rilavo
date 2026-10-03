# Rilavo Product — Succession & Continuity (E-44)

**Tree:** Product
**Wave:** 5 — Governance & Institutionalization
**Status:** Decided, mirrors P-43
**Depends on:** P-43
**Closes when:** Same condition as P-43 — this is the same underlying fact, viewed from the Product document tree rather than a second, independent decision.

## Why this document is short by design

P-43 already specifies the trigger events, the announcement-then-handover sequence, and the harder-case walkthrough for succession when the decentralization trigger (P-25) hasn't yet fired. Restating that mechanism here in full would create exactly the kind of drift risk P-44 (Decision Log) warns about — two documents describing the same process, at risk of silently diverging over time as one gets updated and the other doesn't.

## What's genuinely different about the Product-side view

Not the mechanism — the *asset* being handed over. P-43 concerns itself with the protocol's signing-key material and reference-implementation stewardship. This document concerns itself with what's specific to the commercial layer: customer contracts, the fraud-intelligence feed's continuity (or graceful discontinuation) per E-09's own aggregation mechanism, and support continuity for existing paying customers during the transition.

## Today's honest state, restated exactly as P-43 states it

If Rilavo Product disappeared today: issuance halts, but exported credentials remain valid until natural expiry (P-06, P-32) — the same fact, because it is the same fact.

## Target end-state, restated exactly as P-43 states it

Once P-25's trigger fires: the protocol and other operators continue; only Rilavo Product's specific commercial layer — its fraud intelligence, its SLA commitments, its compliance tooling — disappears with it, and existing customers migrate to another operator or self-host, per the anti-lock-in commitments made throughout this tree (E-08, E-21).

## What would change this decision

Whatever changes P-43 — this document doesn't have an independent trigger, and shouldn't be edited independently of it.
