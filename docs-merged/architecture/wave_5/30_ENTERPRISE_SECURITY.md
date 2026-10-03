# Rilavo Product — Product Security (E-30)

**Tree:** Product
**Wave:** 5 — Governance & Institutionalization
**Status:** Decided
**Depends on:** P-12
**Closes when:** Same gate as the original solo-founder security review — this document specifies the ongoing practice, not just the one-time launch gate.

## The baseline, restated and made specific

Least-privilege internal access to signing infrastructure. No single employee able to unilaterally rotate a production issuer key. A mandatory human security review gate before any liability-bearing release — directly inheriting the original solo-founder development gate rather than inventing a separate product standard.

## What "least-privilege" means concretely, not just as a phrase

Access to production signing infrastructure requires a specific, logged justification, not standing default access by virtue of role or seniority. This connects directly to E-27's architectural enforcement: the same discipline that keeps raw protocol data out of ordinary product-team hands applies to key material specifically, with an even stricter bar, since key compromise (P-12) is the single most severe operational event the protocol can experience.

## Ongoing practice, not just a launch gate

**Access logging:** every access to signing infrastructure recorded, reviewable, and itself subject to periodic audit — not just restricted, but auditable after the fact. **Review cadence:** security review isn't a one-time pre-launch gate alone; any change touching the credential-issuance or verification path (P-06, P-07, P-09) triggers the same mandatory review, on an ongoing basis, matching the discipline Protocol Principle 2 (P-04) already requires of every security claim in the tree.

## Worked example

A change to the SDK's request-signing logic (P-20) is proposed to fix a minor developer-experience issue. Because this touches the proof-of-possession mechanism (P-07), it triggers mandatory security review before merge — regardless of how minor the original motivation seemed, because the review gate is triggered by *what's touched*, not by how significant the change was intended to be.

## The honest gap, carried forward from P-12 rather than hidden here

True HSM- or KMS-backed custody is the target; it is not yet guaranteed at solo-founder stage (P-12). This document's internal-access discipline reduces the *number of people* who could misuse key material, but doesn't by itself solve the *custody infrastructure* gap named there — the two are related but distinct, and conflating them would understate the real risk.

## What would change this decision

Real KMS-backed custody closing the gap named in P-12; or a security incident revealing that the access-logging discipline above wasn't sufficient in practice, which would be exactly the kind of finding that updates this document immediately, not on the next scheduled review.
