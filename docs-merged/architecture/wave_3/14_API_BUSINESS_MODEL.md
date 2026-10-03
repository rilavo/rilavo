# Rilavo Product — API Business Model (E-14)

**Tree:** Product
**Wave:** 3 — Commercial Core (Economics block, built together with E-15–E-17)
**Status:** Decided (mechanism); Open (exact fee, pending real infrastructure cost data)
**Depends on:** E-06
**Closes when:** The illustrative fee below is checked against real infrastructure cost data — not before.

## The mechanism

The billable event is a verification call beyond a generous free tier (E-07), priced small and usage-based.

## Worked math, with the number carried forward from the original founding material, tested rather than just repeated

At an illustrative $0.001 per verification: a customer running 1,000,000 verifications a month pays $1,000/month. Compare that to the estimated cost of building and maintaining an equivalent in-house system — engineering time to build a comparable credential-checking pipeline, plus the ongoing cost of a security review process, plus the residual fraud rate a homegrown, unaudited system would likely carry versus one battle-tested across many customers' traffic. Even a conservative estimate of in-house engineering cost — a fraction of one engineer's time, ongoing — exceeds $1,000/month in short order. **This comparison is illustrative, not a validated claim** — the in-house cost side of it hasn't been measured against a real customer's real internal estimate.

## Why per-verification, not per-seat or flat-rate

**Per-verification** scales with actual usage and actual value delivered — a customer running more agent traffic through more verification checks is, definitionally, getting more value, and paying proportionally.
**Flat-rate**, considered and rejected: decouples price from usage, meaning a low-volume customer overpays relative to value received and a high-volume customer underpays relative to the infrastructure cost they actually generate — bad for both ends of the customer base at once.
**Per-seat**, considered and rejected: meaningless for this product. There's no natural "seat" — the billable unit is a machine-to-machine event, not a human logging in.

## Edge case — burst traffic

A customer with a sudden 10x traffic spike, e.g., a viral product moment driving agent-initiated signups: billed on the same per-verification basis as steady-state traffic, with no separate "burst pricing" tier at v0. **Decided deliberately simple for now** — a burst-pricing model adds real complexity for a problem that hasn't been observed yet; if burst traffic turns out to strain infrastructure disproportionately to its billed value, that's a finding for E-16 to surface, not something to price around speculatively today.

## What would change this decision

Real infrastructure cost data from E-16 confirming or correcting whether $0.001 actually clears a sustainable margin at realistic volume — this document's fee is provisional exactly until that data exists.
