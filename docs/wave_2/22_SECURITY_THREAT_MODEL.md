# Rilavo Protocol — Security Threat Model (P-22)

**Tree:** Protocol
**Wave:** 2 — Engineering Core
**Status:** Decided
**Depends on:** P-06, P-07, P-09
**Closes when:** Re-audited every time P-06, P-07, or P-09 change — this document is a function of those three, not independent of them.

## Organized by STRIDE, for rigor beyond the earlier plain mechanism table

**Spoofing** (pretending to be an agent or issuer you're not)
- *Threat:* an attacker presents a credential without holding the matching agent private key.
- *Mitigation:* proof-of-possession (P-07) — a copied credential alone is inert without the key.
- *Threat:* an attacker signs a fake credential claiming to be the issuer.
- *Mitigation:* signature verification against the issuer's published public key (P-11); an attacker without the issuer's private key cannot produce a valid signature.

**Tampering** (altering a credential or the revocation log)
- *Threat:* modifying any field of a signed credential.
- *Mitigation:* any field change invalidates the signature (P-06, P-11) — tampering is detected, not just discouraged.
- *Threat:* retroactively editing revocation-log history.
- *Mitigation:* hash-chaining (P-09) makes this cryptographically detectable by anyone who cached an earlier state.

**Repudiation** (denying an action occurred)
- *Threat:* a verifier later denies having accepted a specific credential.
- *Mitigation:* audit receipts (P-10) — a hash-bound, timestamped record the verifier itself created.

**Information Disclosure** (leaking more than intended)
- *Threat:* a verifier or issuer learning more about a principal than necessary.
- *Mitigation:* minimum-disclosure field design (P-13) — the credential format has structurally nowhere to put raw personal data.
- *Threat (residual, not fully solved):* correlating a principal across verifiers via reused `sub`/`agt` values.
- *Status:* named honestly in P-13 as a recommendation, not yet a technical enforcement.

**Denial of Service** (making the system unavailable or unusable)
- *Threat:* revocation-log unavailability exploited to force acceptance of a credential that should be rejected.
- *Mitigation:* fail-closed default (P-09) — unavailability causes rejection, not acceptance, closing the exploit even though it costs some availability.
- *Threat:* issuer outage blocking new issuance.
- *Mitigation:* verification remains fully functional against already-cached keys during an issuance outage (P-15) — the two are deliberately decoupled.

**Elevation of Privilege** (acting beyond what was authorized)
- *Threat:* a credential scoped to one action-class used for another.
- *Mitigation:* exact-match action-class checking (P-07) — no wildcard interpretation exists to be exploited.
- *Threat:* a credential presented to a different verifier than intended.
- *Mitigation:* mandatory audience binding (P-07).

## Explicitly out of scope, stated as a hard boundary

A malicious or compromised agent that is *correctly authorized* and behaving badly is not something this specification defends against. Rilavo answers "was this agent allowed to try this," never "should this agent be trusted to behave well." Conflating the two would be a scope failure, not a missing feature — the moment this document starts making claims about agent conduct, it has silently expanded its own mandate past what a stateless authorization protocol can honestly promise.

## What would change this document

Any change to P-06, P-07, or P-09 triggers a mandatory re-pass through every STRIDE category above — not an optional review, a required one, since this table's entire value is staying synchronized with the mechanisms it describes.
