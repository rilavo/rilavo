# Rilavo Product — Customer Success (E-21)

**Tree:** Product
**Wave:** 3 — Commercial Core
**Status:** Decided
**Depends on:** E-07
**Closes when:** At the first real renewal — retention is a claim this document can only actually validate once, for real, at that moment.

## The principle

Retention comes from compounding value, not withheld interoperability. A customer must be able to export their data and leave, and return later without losing compatibility with the network (P-32, E-08) — anything less would directly contradict every anti-lock-in commitment made elsewhere in this tree.

## What actually compounds — named specifically, not just asserted

**False-block rate.** As the network observes more traffic and the fraud-intelligence feed (E-09) accumulates more cross-customer pattern data, the false-positive rate on legitimate agent traffic should improve — a customer integrated for a year should see fewer wrongly-rejected legitimate requests than they did in month one, purely from network-wide learning they didn't have to build themselves.

**Fraud-catch rate.** The inverse metric — genuinely malicious traffic caught — should also improve for the same reason.

## Worked example — one customer's first year

Month 1: baseline false-block rate established during initial integration, whatever it happens to be for that customer's traffic pattern. Month 6: with six months of accumulated cross-customer fraud-pattern data feeding the aggregate intelligence (subject to the five-account threshold in E-09), the false-block rate should be measurably lower — not because anything about this specific customer's own traffic changed, but because the network as a whole got smarter. Month 12: the renewal conversation is grounded in this measured trend, not in habit or switching cost — a customer renewing because the product demonstrably improved is a fundamentally more durable form of retention than one renewing because leaving is annoying.

## Retention metrics this document commits to tracking

False-block rate over time, per customer. Fraud-catch rate over time, in aggregate. Time-to-first-value (how quickly a new integration sees a real, attributable benefit). Renewal rate, obviously — but read alongside the other three, not in isolation, since a renewal rate that's high only because switching costs are high would be exactly the wrong kind of retention for this business to optimize toward.

## Edge case — a customer whose metrics don't improve

**Decided:** if a specific customer's false-block rate genuinely isn't improving over time, that's a real signal worth investigating directly with them, not a metric to quietly stop reporting. A customer-success function that only surfaces good news isn't customer success, it's marketing wearing a different title.

## What would change this decision

The first real renewal cycle — which either confirms that measurable improvement drives retention the way this document assumes, or reveals that customers renew (or don't) for reasons this document hasn't yet identified.
