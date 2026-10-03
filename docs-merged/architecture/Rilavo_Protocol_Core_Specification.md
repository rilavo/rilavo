# Rilavo Protocol — Core Specification

**Version:** 0.1 (Pre-freeze)  
**Status:** Draft — not frozen until surviving production traffic  
**Scope:** This document is the single source of truth for the Rilavo Protocol v0. It consolidates all wave-2 engineering decisions into one coherent reference.

---

## 1. What Is Rilavo, in Plain Language

Rilavo is a **stateless, cryptographically signed credential format** that lets a receiving system (a "verifier") verify that an AI agent holds a specific, time-boxed authorization from a specific principal — **without a network call to the issuer** and without learning anything beyond what the credential discloses.

**The one-sentence mental model:** An agent shows a signed note from its boss saying "this agent can do X for you until time Y." You check the signature, check the clock, check the revocation list, and you're done.

---

## 2. The Problem Rilavo Solves

Today, when an AI agent calls your API, you have three bad options:

| Approach | Problem |
|----------|---------|
| **Trust everything** | Any agent can do anything |
| **Build custom auth per partner** | Doesn't scale; each integration is custom |
| **Central token service (OAuth/OIDC)** | Requires network round-trip to token introspection endpoint; creates central point of failure and privacy leak |

Rilavo is a **fourth option**: The credential itself carries all the proof needed. Verification is local, stateless, and privacy-preserving by construction.

---

## 3. Core Concepts

### 3.1 The Actors

| Role | Description |
|------|-------------|
| **Principal** | The entity (human or organization) that authorizes an agent to act on their behalf |
| **Issuer** | The service that signs credentials on behalf of the principal |
| **Agent** | The AI/software that presents credentials to verifiers |
| **Verifier** | The receiving system that checks credentials and allows/denies requests |

### 3.2 The Credential

A **Rilavo Credential** is a single signed JSON object containing:

| Field | Description |
|-------|-------------|
| `iss` | Issuer identifier (fingerprint of the issuer's public key) |
| `sub` | Principal identifier (opaque, assigned by issuer) |
| `agt` | Agent identifier (specific agent instance) |
| `apk` | Agent's Ed25519 public key (base64url) |
| `act` | Action class this credential authorizes (e.g., `payments.initiate`) |
| `aud` | The one verifier this credential is valid for |
| `iat` / `exp` | Issued-at / Expires-at (Unix seconds) |
| `nonce` | Single-use random value (≥128 bits entropy) |
| `dlg` | Delegation depth (0 or omitted at v0) |
| `ctx` | Optional free-form context |
| `sig` | Ed25519 signature over all preceding fields |

### 3.3 The Verification Flow

```
┌─────────────┐     Credential + PoP      ┌─────────────┐
│    Agent    │ ─────────────────────────▶ │  Verifier   │
└─────────────┘                           └─────────────┘
        │                                        │
        │  1. Check credential signature        │
        │  2. Check expiration                  │
        │  3. Check audience (aud == me)        │
        │  4. Check revocation (local cache)    │
        │  5. Check proof-of-possession         │
        │  6. Check action class (act)          │
        ▼                                        ▼
        │                                ACCEPT / REJECT
```

**All checks are local. No network call to the issuer.**

---

## 4. The Credential Format (P-06)

### 4.1 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `iss` | string | Yes | Issuer identifier — fingerprint of the issuer's public key (e.g., `rilavo:iss:8f2a...c91`) |
| `sub` | string | Yes | Principal identifier — opaque, issuer-assigned, meaningful only within that issuer |
| `agt` | string | Yes | Agent identifier — identifies this specific agent instance |
| `apk` | string | Yes | Agent's Ed25519 public key, base64url, no padding |
| `act` | string | Yes | Action class this credential authorizes (e.g., `payments.initiate`) |
| `aud` | string | Yes | The **one** verifier this credential is valid for (e.g., `verifier:checkout.example.com`) |
| `iat` | integer | Yes | Issued-at, Unix seconds |
| `exp` | integer | Yes | Expires-at, Unix seconds |
| `nonce` | string | Yes | Single-use random value, ≥128 bits entropy |
| `dlg` | integer | No | Delegation depth. `0` or omitted at v0 (delegation not yet supported) |
| `ctx` | string | No | Free-form context, not interpreted by the protocol |
| `sig` | string | Yes | Ed25519 signature over **all preceding fields** (canonicalized) |

### 4.2 Canonicalization (RFC 8785 / JCS)

Before signing, the credential is canonicalized using **JSON Canonicalization Scheme (JCS)** — a subset of RFC 8785 restricted to the types the credential uses (strings, integers, objects). This ensures byte-for-byte identical canonical forms across all implementations.

Key rules:
- Object keys sorted lexicographically (Unicode code point order)
- Strings in UTF-8, escaped per JSON spec
- Integers in shortest decimal form (no leading zeros, no decimal point)
- No whitespace outside string values
- No trailing commas

### 4.3 Signature

The signature is an **Ed25519** signature (RFC 8032) over the JCS-canonicalized credential **excluding the `sig` field itself**. The signature is encoded as base64url, no padding.

---

## 5. The Authorization Model (P-07)

Three independent checks, each doing a distinct job:

### 5.1 Audience Binding (Audience Binding / `aud`)

> **"Is this credential valid *here*?"**

The credential's `aud` field must **exactly equal** the verifier's own registered identifier. A credential issued for `verifier:checkout.example.com` is cryptographically inert at any other verifier — not policy-inert, **structurally inert**, because the verifier's own check rejects it before anything else runs.

This is deliberately borrowed from OAuth 2.1's Resource Indicators (RFC 8707) — it solves the confused-deputy problem the same well-tested way.

### 5.2 Proof-of-Possession (PoP)

> **"Is the party presenting this credential the one it was issued to?"**

Holding a valid credential is **not sufficient** to act on it. The agent must additionally sign the **specific request being made** with the private key matching `apk`.

**The PoP payload** (canonicalized before signing):
```json
{
  "method": "POST",
  "path": "/charge",
  "act": "payments.initiate",
  "nonce": "request-level-nonce"
}
```

The agent signs this with its private key. The verifier checks the signature against `apk` from the credential.

**Why this matters:** A copied credential (without the private key) is useless. A verifier that checks only the credential's own signature and skips PoP has implemented the model incorrectly — that gap is exactly how a *copied but not stolen* credential becomes exploitable, since copying the credential doesn't copy the private key.

### 5.3 Action-Class Matching (`act`)

> **"Is this specific request inside what was granted?"**

The `act` field is a **dot-namespaced string** (e.g., `payments.initiate`, `orders.create`, `data.read`).

**v0 decision: exact match only. No wildcards, no hierarchy.** A credential scoped to `payments.initiate` does **not** authorize `payments.refund`, even though a person might read the two as related.

---

## 6. Revocation (P-09)

### 6.1 The Revocation Log

An **append-only, hash-chained log**. Each entry:

```json
{
  "target": "kQ2f9xVh7pR1mT8w",      // nonce of the revoked credential
  "revoked_at": 1755001200,          // Unix seconds
  "revoked_by": "principal",         // "issuer" or "principal"
  "reason_code": "principal_requested",
  "prev_hash": "sha256:9f3a...c22"   // hash of previous entry
}
```

The `prev_hash` chains entries. Anyone who cached an earlier log state can detect retroactive tampering — including tampering by the log operator itself.

### 6.2 Who Can Revoke

| Who | Can Revoke | When |
|-----|------------|------|
| **Issuer** | Any credential it issued | Compromise detection, policy violation, rotation |
| **Principal** | Their own agent's credential | Suspected compromise, end of relationship |

**Neither needs the other's cooperation.** A principal who suspects their agent has been compromised cannot be made to wait on the issuer to act, and an issuer that detects fraud shouldn't need the principal's permission to cut off a credential it never should have issued.

### 6.3 Fail-Closed Default

If a verifier cannot reach a **current** revocation log state, it treats the credential as **unverifiable and rejects**.

- Verifiers cache the log locally with a **5-minute default refresh interval**
- Once the cache is stale past that interval and can't refresh, the default flips to **reject**

This isn't a live call per verification — it's a local cache check. But once the cache is stale and can't refresh, the default flips to reject.

---

## 7. Cryptography (P-11)

### 7.1 Algorithm: Ed25519 (RFC 8032)

**No exceptions, no custom primitives.**

### Why Ed25519?

| Property | Ed25519 | RSA-3072 | ECDSA P-256 |
|----------|---------|----------|-------------|
| Public key size | 32 bytes | ~384 bytes | 33 bytes (compressed) |
| Signature size | 64 bytes | ~384 bytes | ~72 bytes |
| Verification speed | Fast, constant-time | Slower | Comparable, but nonce-sensitive |
| Nonce generation | **Deterministic** (RFC 6979-equivalent, built-in) | N/A | Requires fresh random nonce per signature |

**The key property:** Ed25519 derives the nonce **deterministically** from the message and private key (RFC 6979-equivalent). There's no external randomness to get wrong at signing time.

**Why this matters:** ECDSA's security depends on never reusing a random nonce across two signatures with the same key. A broken RNG — or a bug that resets state — lets a private key be recovered from as few as two signatures. This happened to Sony PlayStation 3 in 2010: a **constant** nonce let the console's private signing key be recovered from released firmware signatures. Ed25519 removes this entire failure class.

### 7.2 Encoding

| Item | Format |
|------|--------|
| Public keys | base64url, no padding (32 raw bytes → 43 chars) |
| Signatures | base64url, no padding (64 raw bytes → 86 chars) |

No padding characters (`=`) — avoids ambiguity in header/URL contexts.

---

## 8. The Verification Algorithm (Step by Step)

A verifier **must** perform these checks in order:

```
1. PARSE & VALIDATE STRUCTURE
   → All required fields present, correct types, valid base64url, valid JSON

2. CHECK SIGNATURE
   → Canonicalize (JCS), verify Ed25519 signature over canonical bytes using `apk`
   → FAIL if invalid → REJECT

3. CHECK EXPIRATION
   → now < exp AND now >= iat (with small clock skew tolerance)
   → FAIL → REJECT (expired / not_yet_valid)

4. CHECK AUDIENCE
   → credential.aud == verifier_identifier
   → FAIL → REJECT (audience_mismatch)

3. CHECK REVOCATION (local cache)
   → Is credential.nonce in revocation log?
   → If cache stale > 5 min and can't refresh → REJECT (fail-closed)
   → If nonce in log → REJECT (revoked)

5. CHECK PROOF-OF-POSSESSION
   → Reconstruct PoP payload (method, path, act, request_nonce)
   → Verify Ed25519 signature over payload using `apk`
   → FAIL → REJECT (proof_of_possession_failed)

6. CHECK ACTION CLASS
   → request.action == credential.act (exact match)
   → FAIL → REJECT (action_mismatch)

7. ACCEPT
```

**All failures are explicit with a stable reason code.**

---

## 9. Error Codes

| Code | Meaning | HTTP Status |
|------|---------|-------------|
| `missing_field` | Required field absent or empty | 400 |
| `malformed_credential` | JSON parse error, invalid base64url, wrong types | 400 |
| `invalid_signature` | Signature verification failed | 401 |
| `expired` | `now >= exp` | 401 |
| `not_yet_valid` | `now < iat` | 401 |
| `audience_mismatch` | `cred.aud != verifier_id` | 401 |
| `unknown_issuer` | Issuer not in directory | 401 |
| `key_not_valid_at_issuance` | `iat > issuer.valid_until` | 401 |
| `invalid_signature` | Signature verification failed | 401 |
| `replay_detected` | Nonce seen before | 401 |
| `revoked` | Nonce in revocation log | 401 |
| `proof_of_possession_failed` | PoP signature invalid | 401 |
| `action_mismatch` | `request.act != cred.act` | 401 |
| `delegation_not_permitted` | `dlg != 0` at v0 | 401 |
| `unrecognized_version` | `ver` present and `!= 1` | 401 |
| `revocation_unavailable` | Log unreachable + cache stale | 503 |

---

## 9. Versioning (P-26)

- **`ver` field is reserved.** It is **not emitted** by `issue()` at v0.
- Absent `ver` **implicitly means 1**.
- A credential carrying `ver != 1` is rejected with `unrecognized_version`.
- A credential carrying `ver = 1` is accepted (the field is structurally valid, covered by signature).
- **Freeze trigger:** P-06 freezes only after surviving one production partner's real traffic without a breaking field change.

---

## 10. Deployment Models

| Model | Description | Use Case |
|-------|-------------|----------|
| **Self-hosted issuer** | You run your own issuer, publish your own directory | Full control, no external dependency |
| **Hosted issuer (Rilavo Cloud)** | Rilavo operates the issuer; you manage principals/agents | Fastest start, managed operations |
| **Hybrid** | Your issuer for sensitive principals; Rilavo Cloud for others | Gradual migration |

---

## 11. Security Considerations

| Threat | Mitigation |
|--------|------------|
| Credential theft | Short TTL (default 4h), PoP binds to request, revocation |
| Replay attack | Nonce + short TTL + local nonce cache |
| Issuer key compromise | `valid_until` cutoff, key rotation, revocation |
| Verifier impersonation | Audience binding (`aud`) binds credential to one verifier |
| Replay attack | Single-use nonce + TTL-bound nonce cache |
| Replay via copied credential | Proof-of-possession binds to specific request |
| Revocation log tampering | Hash-chained log, verifiers can detect retroactive tampering |
| Centralization | Stateless verification, no central token service |

---

## 12. Open Questions (Pre-Freeze)

| Question | Status |
|----------|--------|
| Default TTL (currently 4h) | Tunable, but default needs production data |
| Revocation fail-closed default | May need per-risk-profile config |
| Clock skew tolerance | Needs production measurement |
| Delegation (P-34) | Not in v0; gate is `dlg` field |

---

## 13. References

- **RFC 8032** — Ed25519
- **RFC 8785** — JSON Canonicalization Scheme (JCS)
- **RFC 8707** — OAuth 2.0 Resource Indicators
- **RFC 6979** — Deterministic DSA/EdDSA Nonce Generation
- **RFC 8705** — OAuth 2.0 Mutual TLS Client Authentication

---

*This specification is the consolidation of Wave 2 engineering decisions (P-06 through P-26). It is the single source of truth for Rilavo Protocol v0 implementation.*

