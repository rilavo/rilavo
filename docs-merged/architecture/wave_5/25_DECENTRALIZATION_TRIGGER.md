# Rilavo Protocol — Decentralization Trigger (P-25)

**Tree:** Protocol
**Wave:** 5 — Governance & Institutionalization
**Status:** Decided (primary trigger); Decided, illustratively (secondary thresholds below — proposed, not yet validated)
**Depends on:** P-24
**Closes when:** The secondary thresholds are tested against real network composition data, not derived from first principles alone.

## The primary trigger, unchanged

No single issuer, including Rilavo, holds a majority of proof-issuance volume. This remains the automatic, primary condition that starts the governance transition specified in P-24.

## Why the primary trigger alone was already flagged as insufficient

Issuance share doesn't capture every centralization risk — a single verifier implementation, a single discovery point, or a single SDK distribution channel could each recentralize the network independently of how many issuers exist.

## Secondary thresholds, now given illustrative numbers rather than left as unquantified concerns

| Concentration risk | Illustrative threshold | Trigger type |
|---|---|---|
| Verifier concentration | A single verifier implementation or library represents more than 50% of active verification traffic | Mandatory governance *review*, not automatic transition |
| Discovery concentration | A single entity operates the key directory (P-17) after a second issuer exists | Mandatory review — this one is closer to a hard rule than a threshold, since any single-operator directory post-federation is itself the risk |
| SDK/distribution concentration | A single package-registry entry or distribution channel accounts for the overwhelming majority of new integrations | Mandatory review |

**Every number above is a proposed starting point, not a derived optimum** — the 50% figure in particular is a round, defensible-but-arbitrary choice, chosen to be meaningfully permissive of natural early concentration (a new network's first popular library will always be disproportionately used) while still catching genuine lock-in before it calcifies.

## Why these trigger review, not automatic action

Unlike the primary trigger, these three are noisier signals — a verifier library legitimately dominating early adoption isn't necessarily evidence of harmful concentration, just evidence that one implementation shipped first and well. Automatic action on a noisy signal risks punishing early quality. A mandatory review, by contrast, forces the governance body to actually look and decide, rather than letting concentration compound unnoticed.

## Worked example

A single open-source verifier library reaches 60% of observed verification traffic eighteen months after launch, purely because it shipped first and is well-maintained. The secondary threshold fires a review, not a penalty — the governance body examines whether this reflects healthy natural adoption of good software or an emerging chokepoint, and the outcome of that review, not the threshold crossing itself, determines what happens next.

## What would change this decision

Real network composition data from the first eighteen to twenty-four months of operation — at which point these illustrative thresholds either hold up or get recalibrated against what concentration actually looks like on a live network, rather than what it was guessed to look like in advance.
