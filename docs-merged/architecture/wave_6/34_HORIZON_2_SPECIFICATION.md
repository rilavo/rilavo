# Rilavo Protocol — Horizon 2 Specification (P-34)

**Tree:** Protocol
**Wave:** 6 — Future Horizons
**Status:** Decided (scope and direction); **NOT triggered**
**Depends on:** P-08
**Closes when:** Same trigger as P-08 — this document doesn't have an independent gate.

## What this document is

Not a duplicate of P-08. P-08 specifies delegation's technical design. This document specifies everything *else* that changes across the tree once delegation is real — the parts of Horizon 2 that are easy to miss if only the credential format itself gets updated.

## What else Horizon 2 touches, beyond the credential format

**Threat model (P-22):** multi-hop chains introduce a correlation risk single-hop credentials don't have — a verifier observing a full chain can potentially trace a request back through every prior delegation hop, which is a new information-disclosure surface P-22's STRIDE categories will need a new row for, not an automatic extension of the existing ones.

**Performance (P-29):** chain verification cost scales with depth — checking three signatures and three scope-subset relationships is real additional latency compared to v0's single check. The `max_depth` field in P-08's design exists partly for this reason: an unbounded chain is not just an audit problem, it's an unbounded verification-cost problem.

**Interoperability (P-18):** delegation changes how Rilavo compares to Biscuit and AIP specifically, since those are exactly what this design was adapted from — the compatibility notes P-18 already commits to publishing become more directly relevant once delegation ships, not less.

**Privacy (P-13):** the correlation risk above interacts directly with the minimum-disclosure principle — a chain that reveals every hop's identity to a verifier is a different privacy posture than v0's single, audience-bound credential, and this needs its own review before activation, not an assumption that P-13's existing analysis automatically covers it.

## What this document does not attempt

A commitment to when Horizon 2 ships. That's not a date to project — it's a fact to observe, exactly as P-08 and P-03 already state, and repeating a target date here would contradict both.

## What would change this decision

The same trigger as P-08. When it fires, this document's job is to make sure P-22, P-29, P-18, and P-13 all get revisited together, as one coordinated update — not patched individually and left to drift out of sync with each other.
