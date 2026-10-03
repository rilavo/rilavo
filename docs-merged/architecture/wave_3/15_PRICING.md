# Rilavo Product — Pricing, Including the $1 Audit (E-15)

**Tree:** Product
**Wave:** 3 — Commercial Core (Economics block)
**Status:** Decided — $1 is acquisition cost, not revenue
**Depends on:** E-14
**Closes when:** Re-litigated only by formal amendment — this is the most re-argued question across the whole project, and this document is where it stays settled.

## The $1 mechanic, worked through with real payment-processing arithmetic

Typical card processing runs around 2.9% plus a $0.30 fixed fee per transaction — a commonly quoted illustrative rate, not a specific processor's guaranteed number. Applied to a standalone $1.00 charge: 2.9% of $1.00 is $0.029, plus the $0.30 fixed fee, totals roughly $0.33 in processing cost alone. **That leaves about $0.67 of a $1.00 charge before any other cost — fraud risk, chargeback handling, dispute support on a transaction too small to justify the support time — is even considered.** This is the concrete version of a claim that was previously only argued qualitatively: a third of the charge disappears to the mechanics of charging it at all.

## The decision this arithmetic supports

If a $1 mechanic exists in any form, it must never be processed as a standalone card transaction. Two workable alternatives: **batch it** — bill it as one line item inside an existing annual cycle, amortizing the fixed processing cost across a larger charge — or **absorb it entirely as acquisition spend**, with no discrete billing event at all, funded out of the product revenue lines below rather than charged to the individual principal at all.

## Real pricing — worked table

| Layer | Illustrative rate | What it's billed against |
|---|---|---|
| API usage | $0.001 / verification, beyond free tier | Actual call volume (E-14) |
| Fraud intelligence subscription | Tiered monthly fee | Subscription, not usage |
| SLA tier | Tiered monthly fee | Subscription (E-12) |
| Compliance tooling | Per-jurisdiction tier | Subscription, gated on Horizon 3 |

**Every rate above is illustrative**, carried forward from earlier project material and tested here rather than newly invented — none are validated against real cost data (E-16).

## Would the user notice if the $1 charge disappeared?

Mostly no — and that's the actual test that disqualifies it as revenue in the first place, restated here with the arithmetic behind it rather than asserted on its own.

## Would Rilavo still get used if the product pays and the consumer pays nothing?

Yes. This is stated plainly because it's the whole point: the $1 line was never load-bearing to adoption, and the payment-processing math above is one more reason, not the only one, that it was correctly identified as a distribution mechanic rather than a revenue engine.

## What would change this decision

Nothing currently in view. The processing-cost arithmetic above is structural, not contingent on early-stage assumptions — it would take a fundamentally different payment rail (not card-based) with materially different per-transaction economics to reopen this, and even then, the underlying "would the user notice" test would still need to fail before $1 became a real revenue line rather than an acquisition cost.
