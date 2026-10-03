# Rilavo Product — Sales Process (E-22)

**Tree:** Product
**Wave:** Continuous / As-Needed
**Status:** Decided (objection-handling below); Open (specific certification target)
**Depends on:** E-18
**Closes when:** The first real deal closes — the responses below are prepared, not yet tested against a real procurement process.

## Objections to prepare for, with the actual response angle for each

**"Show us a security questionnaire / certification."** Answered by pointing at what's real now — the published threat model (P-22), the documented key-management practice (P-12), the architectural enforcement of the data-policy guardrail (E-27) — rather than by claiming a certification that doesn't exist yet. **Certification target:** SOC 2 Type II is the natural target once real revenue justifies the audit cost, but this is not yet committed to a timeline — naming a target without a real date attached is more honest than either silence or a promise that isn't funded yet.

**"How do you handle our data?"** Answered cleanly, because the architecture makes it a short, confident answer rather than a defensive one: minimum-disclosure by design (P-13), no internal system with privileged access beyond the aggregate feed (E-27) — this is one of the few objections where the honest technical answer is also the most reassuring one.

**"Why trust a young company with this?"** The one objection this document refuses to answer with a claim about size or funding the company doesn't have. Answered instead by contractual specifics: the SLA and incident-response commitments (E-12, E-13) and, concretely, guaranteed exportability if the relationship doesn't work out (P-32, E-08) — a prospect isn't being asked to trust Rilavo forever, only to trust that leaving remains genuinely possible if trust turns out to be misplaced.

## Worked example — a full objection exchange

Prospect: "We need SOC 2 before we can sign anything." Response: not yet available, timeline tied to revenue that justifies the audit cost; offered instead, immediately available: the published threat model, the architectural data-handling commitments, and a reference to the exportability guarantee, so the prospect isn't just told "trust us" while waiting for a certification that doesn't exist.

## Why this document doesn't pretend the certification gap isn't real

A sales process built around implying a certification is closer than it is would create exactly the kind of misrepresentation risk this project's compliance-products document (E-10) explicitly warns against in a different context — the discipline is the same whether it's a compliance claim or a security claim.

## What would change this decision

The first real procurement process — which will either validate that these answers satisfy real buyers or surface an objection this document didn't anticipate, becoming a new row rather than a reason to soften the honest ones already here.
