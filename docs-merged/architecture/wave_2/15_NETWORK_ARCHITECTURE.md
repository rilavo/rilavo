# Rilavo Protocol — Network Architecture (P-15)

**Tree:** Protocol
**Wave:** 2 — Engineering Core
**Status:** Decided (v0: single issuer)
**Depends on:** P-05
**Closes when:** Reopens in full at the decentralization trigger (P-25) — this is one of the documents most directly gated by that trigger firing.

## v0 topology, described plainly

One issuer. N verifiers. No consensus mechanism, because there is nothing yet to reach consensus about. A single issuer's key is trusted directly by any verifier that has fetched it from the key directory — the same trust shape as a certificate authority being trusted directly, not a novel arrangement invented for this project.

```
        [ Issuer ]
       /    |     \
  [Verifier A] [Verifier B] [Verifier C] ...
```

Each verifier independently trusts the issuer's published key. Verifiers do not need to trust or even be aware of each other.

## Why consensus isn't needed yet, and exactly when it becomes needed

Consensus exists to let mutually distrusting parties agree on shared state without a central referee. At v0, there is exactly one issuer producing the revocation log — there's no second party whose disagreement needs resolving. **The trigger for this changing:** the moment a second, independent issuer exists, and both issuers need verifiers to agree on a combined view of "what's currently revoked" without either issuer being able to unilaterally control that combined view. That's a Horizon-2-or-later problem, deliberately not solved here.

## Target topology at Horizon 2+, sketched not specified

```
    [ Issuer A ]     [ Issuer B ]     [ Issuer C ]
          \               |               /
           \              |              /
          [ Shared, federated revocation state ]
                          |
              [Verifiers, trusting any/all issuers they choose]
```

This diagram is illustrative, not a commitment to a specific federation mechanism — the actual design (gossip protocol, federated log, or something else) is Horizon-2 work, gated on a second real issuer existing, per P-16 and P-25.

## Failure mode comparison, v0 vs. target

At v0, if the single issuer goes down, no new credentials can be issued, but every verifier that already has a cached public key keeps verifying existing credentials without interruption — issuance availability and verification availability are already decoupled, even in this simplest topology. At the target topology, the same decoupling holds, but additionally no single issuer's outage affects credentials issued by the others.

## What would change this decision

A second issuer being proposed for real — at that point this document's "target topology, sketched not specified" section becomes the actual next thing to specify in detail, not before.
