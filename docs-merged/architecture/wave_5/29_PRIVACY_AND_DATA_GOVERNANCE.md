# Rilavo Product — Privacy & Data Governance (E-29)

**Tree:** Product
**Wave:** 5 — Governance & Institutionalization
**Status:** Open
**Depends on:** E-27
**Closes when:** Resolved per-jurisdiction, as each is genuinely entered — this document specifies how that resolution happens, not what it concludes for any specific market.

## Why "resolved per-jurisdiction" is the right shape for this document, not a deferral in disguise

Privacy regulation is not uniform, and pretending a single global answer exists would misrepresent the actual legal landscape rather than simplify it. This document's job is the *process* any new jurisdiction gets run through, so that process doesn't need to be invented fresh each time.

## The framework — the questions asked of every new jurisdiction before operating there

1. **Controller or processor, or something else entirely, under this jurisdiction's specific framework** — not assumed to match how the last jurisdiction categorized the same activity.
2. **Does local law require data residency** — does data related to principals or transactions in this jurisdiction need to stay physically within it, which would interact directly with the network architecture (P-15) and could, for federated deployments, mean a local operator rather than Rilavo directly serving that jurisdiction.
3. **What does local law require of the aggregation mechanism** (E-09) — does the five-account k-anonymity threshold satisfy this jurisdiction's standard for "sufficiently anonymized," or does it require adjustment.
4. **What breach-notification and penalty regime applies** — concretely, at a level of severity worth taking seriously: Nigeria's Data Protection Act, for instance, carries criminal penalties for unauthorized access to identity records, a materially higher stakes profile than a purely civil-penalty regime.

## What this document explicitly does not conclude

An answer to any of the four questions above for any specific jurisdiction. This is a genuine, structural Open — not because no one has gotten around to it, but because the honest answer depends on real counsel reviewing Rilavo's actual data flows against actual local law, market by market, which hasn't happened for any market yet because v0 hasn't launched in one.

## Worked example — how this framework would actually get used

Before Rilavo Product operates in a new jurisdiction for the first time, the four questions above get run against that jurisdiction specifically, with real legal review, and the results get recorded — becoming that jurisdiction's own entry, not a generic global policy retrofitted to fit every market Rilavo eventually enters.

## What would change this document

The first real jurisdiction-specific legal review, for any market — at which point this document gains its first actual entry, and the framework above gets tested against a real case for the first time.
