# Rilavo Product — Legal & Regulatory (E-28)

**Tree:** Product
**Wave:** 5 — Governance & Institutionalization
**Status:** Deferred beyond v0
**Depends on:** P-41
**Closes when:** Before any Horizon 3 launch, not after — the framework below exists so that review isn't scrambled together at the last minute.

## Why v0 genuinely doesn't need this yet

At v0, Product is not a data controller of anything sensitive by design — no biometric data, no long-lived personal identifiers (P-13). Operating a hosted issuer for agent-authorization credentials, at v0's stakes, doesn't clearly trigger the kind of regulated-activity status that would require specialized legal structuring beyond ordinary commercial terms of service.

## What genuinely will need real counsel, named specifically rather than left vague

**Data controller/processor determination**, once Horizon 3 introduces claim classes that touch personal data more directly (human verification, content provenance) — this status varies by jurisdiction and by exactly how data flows through Rilavo's architecture, not something a technical document can determine on its own.

**Biometric-data-specific regulation by jurisdiction**, if human verification (P-35) is pursued — the research already gathered for this project includes concrete examples of the kind of regime this would need to be checked against: Nigeria's NIMC Act and CBN tiered customer-due-diligence rules, the EU AI Act's Article 50 transparency obligations for synthetic media. These are cited here as illustrations of the *kind* of regulatory landscape ahead, not as legal conclusions about Rilavo's specific obligations under them — that determination requires real counsel reviewing Rilavo's actual architecture against each regime, not this document inferring it.

## What this document explicitly refuses to do

Offer a legal opinion on controller/processor status, on GDPR-equivalent applicability, or on any jurisdiction-specific compliance question. Doing so here, without real counsel, would be exactly the kind of manufactured certainty this entire project has avoided elsewhere — the stakes of getting this specific category wrong (real regulatory and criminal liability, per the Nigeria NDPA example) are too high to treat as a documentation exercise.

## What would change this decision

A Horizon 3 launch decision (E-10, P-35, P-36) becoming real enough to warrant commissioning actual legal review — at which point this document's job shifts from "name what will need review" to "record what the review found."
