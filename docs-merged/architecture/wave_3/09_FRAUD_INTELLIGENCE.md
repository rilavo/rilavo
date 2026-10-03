# Rilavo Product — Fraud Intelligence (E-09)

**Tree:** Product
**Wave:** 3 — Commercial Core
**Status:** Decided (what's aggregable and the privacy mechanism)
**Depends on:** E-06, P-10
**Closes when:** Privacy counsel confirms the aggregation method below — the mechanism is specified here in enough detail to actually be reviewed, not left abstract.

## What gets aggregated

Behavioral patterns drawn from audit receipts (P-10) — velocity anomalies, credential-reuse signatures, revocation-triggering behavior clusters. Never raw credential contents, since receipts themselves never contain them (P-10).

## The privacy mechanism, specified concretely rather than promised abstractly

**A k-anonymity threshold: a pattern is only surfaced as a signal if it has been independently observed across at least five distinct customer accounts.** A single customer's single incident, however unusual, never becomes a shared signal on its own — it has to recur across enough independent relationships to be pattern rather than anecdote. This is the actual mechanism behind "no customer can infer another's specific activity" (Mother Blueprint, E-09) — not a policy promise, a threshold built into what gets published at all.

## Worked example

Thirty-seven issuance requests from the same principal identifier within sixty seconds, each targeting a different audience — an illustrative velocity-anomaly shape. Observed once, at one customer, this stays entirely local to that customer's own receipts; it is not surfaced to anyone else, because it hasn't cleared the five-account threshold. Observed as a recurring shape across six independent customers within the same week, it becomes a shared signal: "this request pattern correlates with credential-stuffing attempts," available to all subscribing customers, with no customer able to identify which of the other five contributed it.

## Edge case — opting out

**Decided:** a customer can opt out of contributing to the aggregate program. They lose access to receiving aggregate signals as a result — a free-rider problem would otherwise let non-contributors benefit from data they never contributed to, which undermines the entire mechanism's incentive to participate. **What opting out never affects:** a customer's own individual receipts and their own local fraud visibility remain entirely theirs regardless of aggregate participation — opting out only removes the cross-customer layer, never the customer's own data about their own traffic.

## Why five, and not a different number

No rigorous derivation — five is a starting default chosen to be meaningfully harder to reverse-engineer than a smaller number like two or three, while not being so high that genuine early signals never clear the bar during the network's early, lower-volume period. **This number is explicitly a placeholder to be revisited once real volume exists to test it against**, not a value with independent justification.

## What would change this decision

Real volume data showing five is either too low (patterns still traceable to a small identifiable group) or too high (genuine early threats never surfacing in time to matter) — this is exactly the kind of number that should move as soon as evidence exists, not stay fixed out of inertia.
