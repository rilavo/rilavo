# Rilavo Product — Revenue Model (E-17)

**Tree:** Product
**Wave:** 3 — Commercial Core (Economics block)
**Status:** Decided (layers); Open (concentration cap number)
**Depends on:** E-14, E-15, E-16
**Closes when:** A concentration cap is set before the first large customer signs — not after, when it would be politically harder to impose.

## The layers, combined into one worked example

Continuing the illustrative Acme Corp customer from E-06, E-08, and E-09:

| Layer | Illustrative usage | Illustrative annual revenue |
|---|---|---|
| API usage (E-14) | 2,000,000 verifications/month at $0.001 | $24,000 |
| Fraud intelligence subscription (E-09) | Standard tier | $6,000 |
| SLA — Priority tier (E-12) | — | $12,000 |
| **Total, one illustrative customer** | | **$42,000/year** |

**Every figure here is illustrative**, chosen to make the combination concrete rather than to predict a real customer's actual bill — E-16 is where the real cost side of this gets resolved, and this table doesn't imply the $42,000 is profit, only revenue.

## Revenue concentration risk, made concrete rather than left abstract

**Illustrative starting policy: no single customer should exceed 20% of total revenue.** Worked through: if Acme's $42,000/year represented 20% of total revenue, that implies the company's entire revenue base is under $210,000/year — a threshold that matters enormously early, when one customer easily could be that large a share, and matters progressively less as the customer base diversifies. The cap is a design constraint on *how sales is run* during exactly this early period — declining or structuring around a deal that would blow past the cap — not a permanent ceiling on any one customer's absolute size once the base has grown past the point where 20% of revenue is itself a large number.

## Why a cap at all, rather than taking the largest deal available

A customer at 40–50% of revenue is a customer whose churn is an existential event, not a bad quarter. This connects directly to the Product Risk Register (E-37) and to the honesty already established in E-25's competitive-strategy audit — revenue concentration is a second, independent way the "can Product survive" question could fail, separate from competitive replication, and one that's actually within Product's own control to manage through how deals are structured.

## Edge case — an inbound deal that would exceed the cap

**Decided, in principle:** such a deal isn't necessarily declined outright, but it should be structured to include contractual terms (extended notice periods, phased ramp, diversification incentives) that reduce the sharpness of a sudden loss, rather than accepted on the same terms as any other deal. The specific contractual mechanism is not designed here — this document sets the principle a sales process (E-22) has to build around.

## What would change this decision

Real revenue diversification data showing the 20% figure is either too conservative (costing real deals unnecessarily) or too loose (a near-miss on an actual concentration scare) — the number is a starting policy, explicitly not a permanent one.
