# Rilavo Product — Survival If Protocol Forked (E-41)

**Tree:** Product
**Wave:** 4 — Survival & Defensibility
**Status:** Open. This document defines what would need to be watched to answer this question honestly, in real time — it does not answer it in advance.
**Depends on:** E-26, P-25
**Closes when:** Only through real operation, per E-26's scorecard actually being tested against a real fork event.

## The scenario, precisely

A separate operator — of any of the three archetypes in E-25 — runs a competing hosted service on the same open protocol, using the reference implementation Rilavo published under a permissive license (P-39). This is not a hypothetical failure mode; it is the direct, intended consequence of the licensing and openness decisions made throughout the Protocol tree. The protocol being forkable is a feature, not an oversight — the question this document exists for is narrower: does *Product* survive that, not whether the fork itself is legitimate.

## What would need to be tracked, in real time, to actually know the answer

Customer migration in either direction between Rilavo and the fork. Relative uptime and incident history between the two (E-26's scorecard, applied comparatively rather than in isolation). Whether new customer acquisition slows for Rilavo relative to the fork's growth. Whether the fork can replicate the fraud-intelligence feed's value — which, per E-09's own five-account threshold, requires the fork to independently accumulate its own multi-customer aggregate data, not simply copy Rilavo's, since Rilavo's own aggregate signals are themselves privacy-architected to not be portable in raw form.

## The one asymmetry worth naming explicitly

A fork starts with zero verifiers trusting it and zero accumulated fraud-pattern history — it cannot copy either, no matter how much capital or engineering talent it has, because both are properties of *time spent operating*, not of the codebase. This is the actual substance behind "trust doesn't transfer with capital," made specific to this scenario rather than left as a general claim.

## What this document is honest about not knowing

Whether that asymmetry is large enough to matter in practice. A fork with dramatically more resources could plausibly out-execute on customer acquisition and support quality fast enough that the trust-graph head start becomes irrelevant before it compounds meaningfully. This document does not claim to know which outcome is more likely — only that this is the actual fork in the road the survival question turns on.

## Response options, cross-referenced rather than duplicated

See E-38 for the trigger-to-response mapping this scenario activates, and E-25 for which competitor archetype a given fork most resembles — the response depends heavily on whether the forker is a hyperscaler bundling for free, a funded competitor racing to out-execute, or a genuine community effort worth engaging rather than opposing.

## What would change this document

A real fork actually happening. Until then, this document's only job is making sure the tracking described above is actually being collected from day one of operation, so that if a fork does happen, the answer comes from real data assembled in advance, not reconstructed defensively after the fact.
