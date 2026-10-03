# Rilavo Product — Product Portfolio (E-06)

**Tree:** Product
**Wave:** 3 — Commercial Core
**Status:** Decided
**Depends on:** E-05, Protocol Wave 2 complete
**Closes when:** Re-tested against "why not just the free protocol" every time an item is added — not a one-time check.

## The portfolio, tested item by item

| Product | Wraps | What's proprietary | Price mechanism |
|---|---|---|---|
| Hosted issuance & verification | P-19 API, P-06 credential format | Uptime, operations, key custody | Usage-based (E-14) |
| Fraud intelligence feed | Aggregated verification telemetry, per the Boundary Map | Cross-customer pattern data no single customer can generate alone | Subscription tier |
| Compliance tooling | Horizon 3 claim classes, gated on P-35/P-36 | Audit packaging, jurisdiction mapping | Per-jurisdiction tier |
| SLA-backed infrastructure | Hosted issuance | Uptime guarantee and credits (E-12) | Tier upgrade |
| Incident response | P-23 protocol-level response, staffed | Escalation staffing | Included above an SLA threshold |
| Developer dashboard | P-19, P-20 | Analytics UI | Free + paid tier |

Each row passes the same test: does it consume an open protocol primitive and add something genuinely proprietary on top, or is it just the free protocol with a markup? A row that fails this test doesn't belong on the list — none currently do, but the test is applied to every future addition, not just this initial six.

## Worked example — one customer's actual stack

Acme Corp buys hosted issuance, the fraud intelligence feed, and Tier 2 SLA. They don't buy compliance tooling, because Horizon 3 hasn't shipped yet and they have no current need for it. They self-host nothing, because they lack dedicated security engineering headcount — which is exactly the customer profile E-08 is built around. This is not a hypothetical persona; it's the shape E-04's segment-1 customer is expected to take.

## Edge case — unbundling, deliberately allowed

Can a customer self-host issuance (per P-32) but still buy the fraud intelligence feed on its own? **Decided: yes.** Intelligence is valuable independent of who operates issuance, and refusing to sell it unbundled would be an artificial lock-in tactic — exactly the kind of move the anti-lock-in commitments elsewhere in this tree (E-07, E-08, E-21) exist to rule out, even where it would be commercially convenient to bundle.

## Alternatives considered

**A single flat "Product" bundle**, all six rows sold as one package: rejected. A la carte pricing is commercially messier — more surface area to price, more sales conversations about what's included — but bundling would force customers to pay for products that don't fit their stack (a self-hoster paying for uptime guarantees they don't use), which contradicts the value-proposition discipline set in E-05 directly.

## What would change this decision

Real sales friction data showing a la carte pricing is costing more in lost deals than it's worth — at which point a bundled tier could be *added* as a convenience option alongside a la carte, not as a replacement for it.
