# Rilavo Protocol — Actor & Trust Model (P-05)

**Tree:** Protocol
**Wave:** 1 — System Foundation
**Status:** Decided (v0 scope); Open (principal-held signing keys)
**Depends on:** P-02
**Closes when:** v0 scope is closed now. Reopens in full at Horizon 2, when delegation makes the actor model more complex.

## Before defining a credential, this has to be settled

Every other technical document assumes an answer to one question: **who is allowed to say what?** This document is that answer.

## Roles

Defined precisely in P-02. In brief: a **principal** holds the underlying authority; an **agent** acts on the principal's behalf and holds a credential; an **issuer** signs the credential attesting the grant; a **verifier** checks a credential before acting on it; an **operator** runs issuer and/or verifier infrastructure — a role Rilavo Product fills first, but does not own.

## Who holds the private signing key

At v0, the **issuer** holds and uses the signing key on the principal's instruction. Principal-held signing — where the principal or their own tooling holds the key directly — is a stated future direction, not v0 scope. **Open, honestly:** client-side key custody has real UX and account-recovery costs that haven't been designed yet, and pretending otherwise would be exactly the kind of manufactured certainty this project avoids.

## Who can revoke

Both the **issuer** and the **principal**, independently. A principal must be able to kill their own agent's authority without waiting on the issuer to act — this is a hard requirement, not a convenience feature, because an issuer-only revocation path would make the principal dependent on the very party they're supposed to be delegating *from*, not *to*.

## Liability allocation

- The **issuer** is liable for a credential it wrongly issued.
- The **verifier** is liable for accepting a credential it should have rejected — expired, revoked, or audience-mismatched.
- The **operator**, at the protocol level, is liable only for a provable protocol-level failure — chiefly, signing-key compromise.

**Status: Deferred to legal counsel.** This allocation is a sound working position, reused consistently across every document in both trees that touches liability. It is not yet enforceable contract language, and this document does not claim otherwise.

## Why this model, not a simpler one

A model with only "user" and "server" — no separate principal/agent/issuer distinction — cannot express the one thing this whole protocol exists to express: that software is acting *for* someone, under *specific*, *revocable*, *time-boxed* terms, rather than simply *as* someone. Collapsing these roles would collapse the actual value proposition along with them.
