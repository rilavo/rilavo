# Rilavo Protocol — Reliability Requirements (P-30)

**Tree:** Protocol
**Wave:** Continuous / As-Needed
**Status:** Decided, illustratively (target below); Open (validated against real operational history)
**Depends on:** P-15
**Closes when:** Real operational data either confirms or corrects the target.

## Why this document exists separately from E-12's SLA

This is the reference implementation's own baseline reliability target — the floor anyone running the protocol, including an independent self-hosted operator (P-32), should reasonably aim for. E-12 is Rilavo Product's *commercial, customer-facing* commitment, which should meet or exceed this baseline, not define it. Collapsing the two would make it look like reliability is a Rilavo-Product-specific promise rather than a protocol-wide property any operator should be able to achieve.

## Illustrative baseline target

99.9% availability for issuance and revocation-log freshness, matching the same asymmetry established throughout this tree: verification itself, once a key is cached, has no dependency on this target at all (P-15) — the number here concerns the parts of the system that genuinely can go down.

## Worked example — how this relates to E-12's commercial tiers

Rilavo Product's Standard SLA tier (E-12) targets the same 99.9% as this document's baseline — meaning the commercial "Standard" tier is, honestly, the reference implementation's ordinary expected reliability, not a premium feature. Priority and Critical tiers (99.95%, 99.99%) represent Product actually engineering *beyond* this protocol-wide baseline, which is the correct relationship: the baseline is a floor, not a ceiling any operator should feel they've maxed out by meeting.

## What this document is honest about not knowing

Whether 99.9% is actually achievable at solo-founder-stage operational maturity, or whether real incident history reveals a lower initial baseline that improves over time as operational practices mature. Setting an aspirational target now and being honest when early performance falls short of it is more useful than setting a target already calibrated to expected early shortfalls.

## What would change this decision

The first six to twelve months of real uptime data — informing whether this baseline was realistic from day one or needed to be an explicit, disclosed ramp toward 99.9% rather than an immediate commitment.
