# Rilavo Product — Developer Platform (E-07)

**Tree:** Product
**Wave:** 3 — Commercial Core
**Status:** Decided (free/paid split); Unknown (conversion rate)
**Depends on:** E-06, P-20
**Closes when:** Closes numerically after 90 days of real usage — the conversion rate below is a target to measure against, not a projection to plan around as though it were fact.

## Free tier

Unlimited sandbox usage — the sandbox never touches real infrastructure or real credentials, so there's no marginal cost being given away. A starting production allowance of 10,000 verification calls per month, free. **This number is illustrative, a starting default, not derived from real cost data** — it exists to be tested against Wave 3's own economics (E-16), not treated as fixed in advance of that data.

## Paid tier

Usage beyond the free allowance (E-14), plus dashboards, staging environments, and priority support. **Never paywalled, as a hard line inherited from the Mother Blueprint:** the ability to self-host and never touch Rilavo's infrastructure at all (P-32).

## Worked example — a developer's actual journey

Day 1: signs up, tests entirely in sandbox against the offline test issuer (P-20) — no account limits apply here. Week 2: integrates against production, low volume, comfortably inside the free allowance. Month 2: traffic grows, crosses 10,000 calls — this is the moment the free/paid boundary is actually tested, not before.

## Edge case — what happens at the free-tier boundary

**Decided: a soft warning with a grace period, not a hard cutoff.** A developer crossing the free allowance receives notice with several days' buffer before billing begins or access is restricted, rather than an immediate hard stop. Reasoning: a hard cutoff on a live production dependency — one that might be handling real checkout traffic, per E-06's example — is bad practice regardless of the underlying business model, and would directly contradict the trust this entire platform depends on customers extending to it.

## What "conversion rate" actually needs to mean here, stated precisely rather than left vague

Not "how many free users ever pay" in the abstract — that number is close to meaningless without a time window. The actual metric this document commits to tracking: of developers who cross the free allowance within their first 90 days, what fraction convert to paid within 30 days of crossing it. That's a specific, falsifiable number a first cohort can actually produce.

## Alternatives considered

**Metered from the first call, no free tier:** rejected — kills the exact adoption momentum the wedge (P-03) depends on; a technical audience evaluating whether to integrate at all needs a genuinely free way to try it first.

**Unlimited free forever, monetize only the product tiers below:** rejected — removes any organic path from "developer trying this out" to "revenue," pushing the entire business model onto sales-led product deals the go-to-market strategy (E-18) deliberately avoids leading with.

## What would change this decision

The first real 90-day cohort. If the free allowance turns out too generous (nobody ever crosses it) or too stingy (developers churn before finding value), this document is exactly where that gets corrected — not silently adjusted elsewhere.
