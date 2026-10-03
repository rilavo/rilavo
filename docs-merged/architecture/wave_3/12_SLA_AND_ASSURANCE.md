# Rilavo Product — SLA & Assurance (E-12)

**Tree:** Product
**Wave:** 3 — Commercial Core
**Status:** Open (specific tier numbers below are illustrative, not committed)
**Depends on:** E-08, P-30
**Closes when:** Real uptime history exists to validate or correct the tiers below — this document is explicit that it's publishing a starting proposal, not a measured commitment.

## Why this is worth paying for at all

Verification itself has no dependency on Rilavo's uptime once a key is cached (P-15) — the case for paying is narrower and more honest than "pay us to be up." It's specifically about issuance and revocation-log freshness, which do depend on live infrastructure, and about bounding the risk for any customer who has put Rilavo in a live transaction path.

## Illustrative tiers

| Tier | Target uptime | Approx. allowed downtime/month | Credit if breached |
|---|---|---|---|
| Standard | 99.9% | ~43 minutes | 10% of monthly fee |
| Priority | 99.95% | ~22 minutes | 25% of monthly fee |
| Critical | 99.99% | ~4 minutes | 50% of monthly fee |

**Every number in this table is illustrative** — a standard, industry-familiar shape borrowed deliberately rather than invented, so the tiers are legible to a customer's procurement team on sight, but not yet validated against Rilavo's own real infrastructure history.

## Worked example

A 30-minute outage in a given month. A Standard-tier customer's allowance (~43 minutes) isn't exceeded — no credit owed, even though the outage was real and inconvenient. A Priority-tier customer's allowance (~22 minutes) is exceeded by the same outage — a credit is owed, calculated proportionally to the overage, not a flat penalty.

## Edge case — scheduled maintenance

**Decided:** planned maintenance, announced with reasonable advance notice, does not count against the uptime commitment. Unplanned outages, regardless of cause — including a key-compromise incident under P-12's runbook — do count, without exception, since the SLA is a promise about availability the customer can depend on, not a promise conditioned on the cause being someone else's fault.

## What this document explicitly does not yet know

Whether 99.9%/99.95%/99.99% are the right tier boundaries for this specific kind of infrastructure, or whether real operating history will show a different natural breakpoint. Whether the credit percentages are calibrated correctly against what actually motivates a customer versus what actually costs Rilavo too much to sustain. Neither question can be answered by more analysis — both need real incident and uptime history.

## What would change this decision

The first two or three quarters of real production uptime data. This document is a placeholder with real structure, not a final commitment — and should be read that way by anyone selling against it before that data exists.
