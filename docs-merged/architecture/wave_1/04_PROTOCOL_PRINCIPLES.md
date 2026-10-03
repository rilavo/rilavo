# Rilavo Protocol — Principles (P-04)

**Tree:** Protocol
**Wave:** 1 — System Foundation
**Status:** Decided
**Depends on:** P-01
**Closes when:** Revisited only if a later decision would violate one of these — otherwise treated as settled.

## Purpose

These five rules function as architectural law, not aspiration. Every document in this tree, present and future, is checked against them before it's accepted — including this one, against itself.

## The five rules

**1. No architecture decision gets marketing language instead of evidence.** A claim like "near-zero marginal cost" is only usable if the document making it also states where that stops being literally true. See P-38 and the core specification's own treatment of infrastructure cost at scale.

**2. No security claim rests on "the cryptography prevents it" without a threat-model entry.** Every mitigation named anywhere in this tree must trace to a specific line in P-22's mechanism-mapping table. A mitigation that isn't in that table doesn't count as decided.

**3. No network-effect claim without a named mechanism.** "Usage creates value" is not an argument. "Every verifier that accepts the format makes issuance more valuable to the next issuer" is — because it names the actual loop, which can then be tested and falsified.

**4. No survivability claim rests on "the protocol is open" alone.** Openness is necessary and is not sufficient. A protocol can be fully open-source and still fail every practical independence test if, in practice, only one operator's implementation is trusted, discovered, or distributed. See the Decentralization Trigger (P-25) for why issuance-share alone isn't treated as sufficient either.

**5. The protocol never requires trusting Rilavo Product specifically — only trusting an issuer, which the principal or their tooling can choose.** This is the rule the entire two-tree structure exists to protect. Any future document that would only make sense if Rilavo Product held a permanent, structural advantage is, by definition, in violation of this rule and gets rejected on that basis alone, independent of how commercially attractive it might look.

## How these are used, in practice

Not as a checklist run once. Every document generated under P-06 through P-45 gets checked against these five before it's marked Decided — this is the actual mechanism behind the project's "don't manufacture certainty" discipline, not just a stated value.
