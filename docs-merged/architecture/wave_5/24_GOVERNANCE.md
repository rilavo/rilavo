# Rilavo Protocol — Governance (P-24)

**Tree:** Protocol
**Wave:** 5 — Governance & Institutionalization
**Status:** Decided (Model A now, with the transition mechanism below now specified)
**Depends on:** P-05
**Closes when:** Transition begins at P-25's trigger — this document specifies the process in advance so it doesn't need to be improvised at that moment.

## v0: Model A, stated plainly

The founder controls the reference implementation, sets initial issuer standards, and can patch security issues fast. This is not disguised as anything more decentralized than it is.

## The transition mechanism, specified now rather than left to invent later

**Proposed governance body composition, once P-25's trigger fires:** seats for active issuers, seats for active operators/verifiers at meaningful scale, and at least one seat reserved for a party with no commercial stake in any operator — a public-interest or independent seat, structurally similar to how standards bodies and some regulated-utility boards include non-industry representation specifically to check industry capture.

**Admission process for a new issuer:** application, review against security and operational criteria (feeding P-33 once that document is no longer gated), a provisional/trial admission period, then full admission. This process itself is decided now, in advance, even though the *specific bar* (P-33) isn't set until there's a real applicant to calibrate it against.

**Two tiers of decision, not one:** routine decisions (approving a new issuer that clears the provisional bar, adjusting a non-structural operational parameter) require only ordinary process. Structural decisions — changing the credential format, altering the decentralization trigger itself, admitting an entirely new claim class (Horizon 3+) — require supermajority agreement across the seated body, deliberately harder to change than routine operation.

## Worked example — a hypothetical future decision, walked through the process

Suppose, post-federation, the body considers deprecating credential format v1 in favor of v2 (P-26). This is structural — it affects every existing issuer and verifier — and requires supermajority agreement, with the public-interest seat's vote carrying equal weight to any commercial operator's, specifically so the transition timeline can't be forced by whichever operator has the most to gain from a fast cutover.

## Powers governance must never hold, restated here as an enforceable constraint on the body being designed, not just a principle

No introducing a protocol-level fee (P-38) — structural rejection, not routine-reversible. No granting any single issuer exclusive privilege inconsistent with the Boundary Map. No unilateral, undisclosed change to credential portability. A governance body that could do any of these would have become a private owner wearing public-interest language, which is exactly the failure mode Principle 5 (P-04) exists to prevent.

## What would change this decision

The actual arrival of a second real issuer — at which point this document's proposed structure gets tested against a real admission, for the first time, rather than remaining a design on paper.
