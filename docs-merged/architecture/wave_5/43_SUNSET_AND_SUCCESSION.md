# Rilavo Protocol — Sunset & Succession (P-43)

**Tree:** Protocol
**Wave:** 5 — Governance & Institutionalization
**Status:** Decided (today's honest state, target state, and now the actual transition process below)
**Depends on:** P-06, P-24
**Closes when:** Closes exactly when P-25's trigger fires — a fact that can be checked, not a date to estimate toward.

## Today's honest state

If the operating company disappeared right now: issuance halts, but exported, principal-held credentials remain valid until natural expiry — meaningfully better than total failure, because portability was a day-one requirement (P-06), not a feature added later.

## Target end-state

Once P-25's trigger fires: the protocol, standard, and other operators continue; only the commercial layer built on top disappears with its operator.

## The process, specified now rather than left to be improvised during an actual crisis

**Trigger events for formal succession:** insolvency, founder incapacitation or departure without a designated successor, or a voluntary wind-down decision. **Sequence, once triggered:**

1. **Public announcement**, as early as practically possible — silence during a succession event is exactly the kind of surprise that damages trust in infrastructure people depend on.
2. **Formal handover period**, length dependent on whether P-25's trigger has already fired. If it has — multiple independent issuers already exist — succession is close to a non-event for the network as a whole: other operators simply continue, and the departing operator's specific customers migrate per the ordinary managed-to-self-hosted path already specified (P-32).
3. **If the trigger has not yet fired** — Rilavo is still the sole or dominant issuer — succession requires active effort: signing-key material and the reference implementation's stewardship transfer to a successor entity or a caretaker arrangement among remaining participants, rather than simply lapsing.
4. **Final public accounting**, closing the loop on what was transferred, to whom, and what changed for existing users.

## Worked example — the harder case, walked through

Suppose the founder departs unexpectedly before a second issuer has ever existed. Per the sequence above: public announcement immediately, followed by an active handover — not a passive one — because there's no second operator yet for the network to fall back on. This is precisely why the earlier stages of this project treat getting past P-25's trigger as urgent from a resilience standpoint, not just a governance-purity standpoint: the difference between "succession is a formality" and "succession is a crisis" is entirely a function of whether that trigger has already fired by the time it's needed.

## What would change this decision

Nothing about the process itself — the honest gap it exposes (succession is much harder before P-25 fires than after) is exactly why that trigger firing sooner rather than later is valuable for reasons beyond decentralization ideology, and this document makes that connection explicit rather than leaving it implicit.
