# Rilavo Product — Insurance & Liability (E-31)

**Tree:** Product
**Wave:** 5 — Governance & Institutionalization
**Status:** Decided (allocation, now worked through against harder cases below); Deferred (actual policy/ToS language, actual insurance product)
**Depends on:** P-05's liability allocation
**Closes when:** Real ToS and, eventually, an actual insurance product exist — the allocation logic below is sound; it isn't yet enforceable contract language.

## The base allocation, unchanged

Issuer liable for a wrongly issued credential. Verifier liable for accepting one it should have rejected. Operator (Product, at the protocol level) liable only for a provable protocol-level failure — chiefly, signing-key compromise.

## The harder case this document now works through: shared fault

**What happens when both an issuer error and a verifier error contribute to one incident?** This is not a hypothetical edge case — real-world liability disputes routinely involve more than one party's contributing failure, and a framework that only handles the clean single-fault case is incomplete.

**Worked example:** an issuer grants a broader action-class scope than it should have (issuer error, per P-06/P-07), and a verifier fails to check revocation status before accepting a since-revoked credential (verifier error, per P-09). Both failures contributed to the resulting harm. **Decided, as a principle rather than a fixed formula:** liability apportions between the two parties in proportion to each failure's contribution to the outcome — not automatically split evenly, and not assigned entirely to whichever party is easier to blame. **What this document does not do:** invent a specific apportionment formula. That's genuinely a legal-drafting question requiring real counsel, not something a technical specification should pre-decide by fiat.

## Why Product's own liability stays narrow even in the shared-fault case

Product, as protocol-level operator, isn't a party to either failure above unless the underlying cause traces to a protocol-level fault (a key compromise, a bug in the reference verification algorithm itself). An issuer's bad judgment about how broad a scope to grant, or a verifier's failure to implement the reference algorithm correctly, are failures of *their own* integration choices — not failures of the protocol Product operates, and the liability allocation should reflect that distinction consistently, not narrow it only when convenient.

## What genuinely needs an insurance product, and why one doesn't exist yet

A real insurance product would cover Product's own narrow liability band — protocol-level failures specifically — at a cost that only makes sense once real transaction volume and real incident history exist to price it against. Before that data exists, quoting a policy would be pricing blind, which is worse than not having a product yet.

## What would change this decision

Real legal counsel converting the apportionment principle above into actual contract language; real volume and incident history making an insurance product priceable rather than speculative.
