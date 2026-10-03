# Rilavo Product — Data & Intelligence Policy (E-27)

**Tree:** Product
**Wave:** 4 — Survival & Defensibility
**Status:** Decided (guardrail and enforcement mechanism, below) — the one Wave 4 document that closes further rather than staying open, because this question is actually structural, not competitive.
**Depends on:** E-09, P-13
**Closes when:** An external audit confirms the architectural enforcement below matches reality — a real check, not a permanent close.

## The guardrail, restated

What Product learns from operating the network must never silently become protocol governance power, or the claim that the protocol is neutral becomes false in substance while staying true on paper.

## The enforcement mechanism, made concrete rather than left as policy

**Architectural, not just procedural: no Product-internal system — product, engineering, or sales — may query raw, pre-aggregation protocol data. Every internal Product system consumes the same k-anonymized, five-account-threshold aggregate feed defined in E-09 that a paying customer receives.** There is no privileged internal tier that sees more than the product does. This is the difference between "we promise not to misuse this" and "the misuse isn't architecturally possible without a deliberate, detectable system change" — the latter is what this document commits to.

## Worked example — what this rules out concretely

A product manager wanting to understand "which customers are seeing the most fraud" cannot query raw per-customer receipt data directly, even internally, even for a legitimate-sounding product reason. They can query the same aggregate signal feed a customer subscribing to E-09 would see. If the aggregate feed doesn't answer the question, the answer to "how do we learn this" is "we don't, not this way" — not "we build an internal-only exception."

## What would make this checkable, not just asserted

An external security or privacy audit verifying that no internal Product system has a data-access path to raw protocol telemetry that bypasses the aggregation layer — a specific, falsifiable architectural claim an auditor can actually check, unlike a policy statement alone.

## Edge case — a security incident requiring raw data access

**Decided:** an active security investigation (per P-23/E-13) is the one legitimate exception, time-boxed and logged, with the access itself auditable after the fact — not a standing privilege, a specific, recorded, temporary one triggered only by an active incident.

## Why this is more resolvable than the rest of Wave 4

This isn't a question about competitors, markets, or the protocol's fate — it's a question about Product's own internal architecture, which Product fully controls. That's exactly why it doesn't belong in the same "Open, by design" category as E-25, E-26, or E-41–43: those depend on what the world does. This depends on what Rilavo builds, which can simply be decided and then checked.

## What would change this decision

Only evidence that the architecture described above isn't actually implemented as stated — at which point this document would need to honestly downgrade back to Open until it's fixed, not stay marked Decided on the strength of intent alone.
