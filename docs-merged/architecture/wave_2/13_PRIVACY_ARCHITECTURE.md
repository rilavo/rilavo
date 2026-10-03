# Rilavo Protocol — Privacy Architecture (P-13)

**Tree:** Protocol  
**Wave:** 2 — Engineering Core  
**Status:** Decided  
**Depends on:** P-06 (Credential Specification)  
**Closes when:** Re-audited at every future horizon (P-34 through P-37) — this document's job gets harder, not easier, as claim classes expand.

---

## The Principle: Minimum Disclosure by Construction

> **The credential reveals only the action-class and audience.** It never reveals the principal's broader identity, unless the verifier's own business requires more — and that's the verifier's choice to request through its own separate onboarding, not something the protocol volunteers by default.

This is **not a policy promise layered on top**. It's the actual field list in P-06 (Credential Specification) — there is simply no field to put personal data in.

---

## What's in the Credential (And What's Not)

| Field | Contains | Privacy Implication |
|-------|----------|---------------------|
| `iss` | Issuer fingerprint | Public — identifies the issuer, not the principal |
| `sub` | Opaque principal ID | Opaque string assigned by issuer; no inherent meaning |
| `agt` | Opaque agent ID | Opaque string; identifies agent instance, not person |
| `apk` | Agent public key | Cryptographic key, no personal data |
| `act` | Action class | Authorization scope, not personal data |
| `aud` | Verifier ID | Public — identifies the verifier |
| `iat` / `exp` | Timestamps | Operational metadata |
| `nonce` | Random value | Single-use, no linkage |
| `ctx` | Optional context | Free-form; **should not contain PII** |

**No name. No email. No phone. No device fingerprint. No biometric. No location.**

---

## Tracing the Data, Hop by Hop

### 1. Principal → Issuer
**What flows:** Principal's instruction: "Grant agent X scope Y for verifier Z for TTL T."

**What's visible:** The principal's full identity (they're the customer).

**Trust model:** This hop is inherently trusted — the principal is asserting their own authority.

### 2. Issuer → Agent
**What flows:** The signed credential.

**What's visible:** `sub` (opaque principal ID), `agt` (opaque agent ID), `act`, `aud`, timestamps.

**What's NOT visible:** Principal's name, email, device info, location, biometrics.

### 3. Agent → Verifier
**What flows:** Credential + Proof-of-Possession signature.

**What's visible:** Credential fields (see above) + request-specific PoP signature.

**What the verifier learns:** "An agent holding this credential is authorized for `act` at this verifier until `exp`."

**What the verifier does NOT learn:** Who the principal is, beyond what `sub` happens to encode (which should be opaque by convention).

### 4. Verifier → Audit Receipt
**What flows:** Audit receipt (P-10).

**What's visible:** Hash of credential, outcome (accept/reject), timestamp, reject reason.

**What's NOT visible:** Full credential contents — only their hash persists.

---

## Worked Example: What Two Verifiers Can (and Can't) Learn

### Scenario
- Verifier A: `verifier:checkout.example.com`
- Verifier B: `verifier:analytics.example.com`
- Same principal, different agents, different times

### What Each Verifier Sees

| Data | Verifier A | Verifier B |
|------|------------|------------|
| `sub` | `acme-corp:agent-runner-04` | `acme-corp:analytics-agent-07` |
| `agt` | `agt_7d3e1c` | `agt_9f2a1b` |
| `act` | `payments.initiate` | `analytics.record` |
| `aud` | `verifier:checkout.example.com` | `verifier:analytics.example.com` |
| `nonce` | `kQ2f9xVh7pR1mT8w` | `vD8k2NpQz4rL9wXs` |

### What They Can Infer
- ✅ Each knows the agent is authorized for their specific action
- ✅ Each knows the credential is valid for their specific audience

### What They CANNOT Infer
- ❌ That the same principal is behind both (different `sub`/`agt`)
- ❌ That the two agents belong to the same organization (opaque IDs)
- ❌ Any personal data about the principal

**The protocol provides unlinkability by default** — unless the issuer or principal chooses to reuse the same `sub`/`agt` values across relationships.

---

## The Residual Gap (Honest Disclosure)

> **This is a real, current limitation of v0, not fully solved by the credential format alone.**

If the issuer or principal reuses the same `sub` value across multiple verifiers, those verifiers **can** correlate that they're seeing the same principal. This is documented in P-22's threat table as a known gap.

**Future mitigation (Horizon 3 / P-34+):**
- Per-relationship identifiers (`agt` per verifier)
- Zero-knowledge proofs for attribute disclosure
- Issuer-enforced per-verifier identifier derivation

---

## What Zero-Knowledge Proofs Unlock Later (And Why Not in v0)

### What ZK Unlocks (Horizon 3 / P-34+)
A verifier could confirm a claim — **"this principal is over 18," "this principal is a licensed operator in this jurisdiction," "this principal has a valid business license"** — **without learning the underlying attribute itself.**

### Why Not in v0?
1. **Scope creep:** v0 solves agent authorization, not identity verification
2. **Complexity:** ZK adds significant implementation complexity
3. **Verifier expectations:** In v0, the verifier *is supposed to know* which principal it's dealing with (in the ordinary sense of "which account is this") — it's the agent's `sub` that provides that link
4. **Spec freeze risk:** ZK standards are still evolving (W3C, IETF)

**When it arrives:** Horizon 3 (P-34+), with dedicated ZK claim format, separate from v0 credentials.

---

## What the Protocol Does NOT Do (By Design)

| What It Doesn't Do | Why |
|--------------------|-----|
| Collect personal data | No fields for it in the credential |
| Link credentials across verifiers | `aud` binding + opaque `sub`/`agt` prevent correlation |
| Require principal consent per verification | Verification is stateless; consent is implicit in issuance |
| Track user behavior across sessions | No session IDs, no tracking cookies, no fingerprinting |
| Build user profiles | No profile API, no analytics, no tracking |

---

## Comparison: Rilavo vs. Traditional Approaches

| Aspect | OAuth 2.0 / OIDC | mTLS / Certificates | **Rilavo Protocol** |
|--------|------------------|---------------------|---------------------|
| **Personal data in token** | Yes (email, name, etc.) | Often yes (CN, OU) | **No — no fields for it** |
| **Central validation** | Yes (introspection/token endpoint) | Often (OCSP/CRL) | **No — stateless verification** |
| **Verifier learns identity** | Yes (claims) | Yes (certificate subject) | **Only what `sub` encodes** |
| **Central revocation** | Yes (introspection) | CRL/OCSP | **Append-only log, local cache** |
| **Cross-verifier tracking** | Yes (same token) | Yes (same cert) | **Prevented by `aud` binding** |

---

## Summary: Privacy by Construction

| Guarantee | How It's Achieved |
|-----------|-------------------|
| **No PII in credentials** | No fields for PII in P-06 schema |
| **Unlinkability across verifiers** | `aud` binding + opaque `sub`/`agt` |
| **No central tracking** | Stateless verification, no central log |
| **Minimal audit retention** | Receipts store hashes, not full credentials |
| **Verifier-controlled onboarding** | Verifier chooses what identity it needs |

---

## Future Horizons (P-34+)

| Horizon | Privacy Enhancement |
|---------|---------------------|
| **Horizon 1 (v0)** | Current: stateless, minimal disclosure, unlinkability by default |
| **Horizon 2 (P-34)** | Delegation with per-relationship identifiers |
| **Horizon 3 (P-34+)** | ZK attribute proofs, selective disclosure |
| **Horizon 4 (P-36+)** | Anonymous credentials, threshold issuance |

---

## Summary

| Guarantee | How It's Achieved |
|-----------|-------------------|
| **No PII in credentials** | No fields for PII in P-06 schema |
| **Unlinkability across verifiers** | `aud` binding + opaque `sub`/`agt` |
| **No central tracking** | Stateless verification, no central log |
| **Minimal audit retention** | Receipts store hashes, not full credentials |
| **Verifier-controlled onboarding** | Verifier chooses what identity it needs |

---

> **Try it first:** [Interactive Playground](../playground/index.md) — issue and verify credentials in your browser without setting up infrastructure.