# Rilavo Product — Risk Register (E-37)

**Tree:** Product
**Wave:** 4 — Survival & Defensibility
**Status:** Decided, as a living list — this document is never "finished," only current as of its last review.
**Depends on:** All of Wave 4
**Closes when:** Never — reviewed every wave, updated whenever a source document changes status.

## The register

| Risk | Source | Status | Mitigation | Review cadence |
|---|---|---|---|---|
| Revenue concentration — one customer too large to lose | E-17 | Open (cap set, untested) | 20% concentration cap, deal-structuring around it | Every wave |
| Hyperscaler or well-funded competitor replicates the service | E-25, E-26 | **Open, by design** | Speed on non-forkable assets — trust graph, not code | Continuous |
| Product's data advantage quietly becomes governance power | E-27 | Decided (architectural enforcement) | Aggregation-only internal access, no privileged internal tier | Annual external audit |
| Regulatory characterization changes at Horizon 3 | Wave 5 (not yet generated) | Deferred | Legal review before any Horizon 3 launch, not after | At the Horizon 3 trigger |
| Single-issuer signing-key compromise | P-12, P-23 | Decided (runbook exists) | KMS-backed custody, rotation, retroactive cutoff enforcement | Continuous |
| Protocol declines relative to a competing standard | E-43 | **Open — least resolved item in the project** | Monitor adjacent-standard adoption at the verifier level | Continuous |
| Unit economics don't hold at real scale | E-16 | Open — genuinely unknown | Real cost data past first few thousand customers | Per cohort |
| Free-tier developer conversion doesn't materialize | E-07 | Unknown | 90-day cohort tracking | Per cohort |

## What this table is for, and what it isn't for

It exists so none of these risks can quietly drop out of view by living only inside their own individual document. It is explicitly not a claim that every risk here is equally likely, equally severe, or equally close to resolving — the **Status** column already carries that distinction, and collapsing it into a single risk score would hide more than it reveals at this stage.

## Worked example — how this table gets used in practice

At the next scheduled review, each row is checked against its source document: has the status changed? If E-16 has produced real cost data since the last review, its row updates from "Open" to whatever the data actually shows — this table follows its source documents, it never gets edited independently of them.

## The one honest pattern visible across every row

Look at the **Status** column as a whole: two rows are fully architecture-controlled and already Decided. The rest depend on real operation, real markets, or real competitors — none of them close by more analysis, only by time and evidence. That's not a weakness specific to this register; it's the accurate summary of where the entire project actually stands.

## What would change this document

Nothing changes the register's own structure. Its content changes constantly, by design, as its source documents do.
