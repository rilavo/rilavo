# Rilavo Protocol — Cryptographic Specification (P-11)

**Tree:** Protocol  
**Wave:** 2 — Engineering Core  
**Status:** Decided, Confirmed  
**Depends on:** None — self-contained  
**Closes when:** Reopens only at a post-quantum migration trigger (P-28), not before.

---

## The Short Answer

**Algorithm: Ed25519 (RFC 8032).**  
No exceptions. No custom primitives. No algorithm agility.

---

## Why Ed25519? (With Numbers, Not Just Claims)

| Property | Ed25519 | RSA-3072 (comparable security) | ECDSA P-256 |
|----------|---------|--------------------------------|-------------|
| Public key size | 32 bytes | ~384 bytes | 33 bytes (compressed) |
| Signature size | 64 bytes | ~384 bytes | ~72 bytes |
| Verification speed | Fast, constant-time by design | Slower | Comparable, but nonce-sensitive |
| Nonce generation | **Deterministic** (RFC 6979-equivalent, built-in) | N/A for signing | Requires fresh random nonce per signature, externally |

### The One Property Worth Explaining: Deterministic Nonces

**ECDSA's security depends on never reusing a random nonce across two signatures with the same key.**

If a broken RNG — or a bug that resets state — causes nonce reuse, a private key can be recovered from as few as **two signatures**. This is not theoretical:

> **Real-world example:** The 2010 Sony PlayStation 3 signing-key compromise. A **constant** (not even reused-but-random, but literally constant) nonce let the console's private signing key be recovered directly from released firmware signatures.

**Ed25519 removes this entire failure class** by deriving the nonce **deterministically** from the message and the private key itself (RFC 6979-equivalent, built into the scheme). There's no external randomness to get wrong at signing time.

---

## Encoding

| Item | Format | Size | Example |
|------|--------|------|---------|
| Public key | base64url, no padding | 32 raw bytes → 43 chars | `MCowBQYDK2VwAyEA...` |
| Signature | base64url, no padding | 64 raw bytes → 86 chars | `MEUCIQDR...` |

**No padding characters (`=`)** — avoids ambiguity in header/URL contexts where padding characters sometimes get stripped or misinterpreted.

---

## Key Derivation

### Issuer Keys
- Generated via Ed25519 key generation (RFC 8032)
- Issuer ID = `rilavo:iss:` + first 16 hex chars of SHA-256(raw public key)
- Example: `rilavo:iss:8f2a...c91`

### Agent Keys
- Generated per agent instance
- `apk` in credential = agent's Ed25519 public key (base64url)
- Agent keeps private key; `apk` goes in credential

---

## Canonicalization (JCS / RFC 8785)

Before signing, the credential is canonicalized using **JSON Canonicalization Scheme (JCS)** — a subset of RFC 8785 restricted to the types the credential uses (strings, integers, objects).

### JCS Rules (Simplified)

| Rule | Example |
|------|---------|
| Object keys sorted lexicographically (Unicode code point order) | `{"a":1,"b":2}` → `{"a":1,"b":2}` (already sorted) |
| Strings in UTF-8, escaped per JSON spec | `"hello"` → `"hello"` |
| Integers in shortest decimal form | `42` → `42` (no `+`, no leading zeros) |
| No whitespace outside string values | `{"a":1}` not `{ "a" : 1 }` |
| No trailing commas | `{"a":1}` not `{"a":1,}` |

### Why Canonicalization Matters

The signature covers the **canonical form**, not the original JSON. Two semantically equivalent JSON objects must produce identical canonical bytes, or signatures won't verify across implementations.

> **Test it:** The Rilavo test suite includes golden-vector byte-parity tests that verify canonicalization produces identical bytes across Python, TypeScript, Go, and WordPress implementations.

---

## Signing Process

### Credential Signing
```python
# 1. Remove 'sig' field from credential
# 2. Canonicalize remaining fields (JCS)
# 3. Sign canonical bytes with issuer's Ed25519 private key
# 4. Encode signature as base64url (no padding)
# 5. Add 'sig' field back to credential
```

### Proof-of-Possession Signing
```python
# 1. Build PoP payload:
{
  "method": "POST",
  "path": "/charge",
  "act": "payments.initiate",
  "nonce": "request-level-nonce"
}

# 2. Canonicalize (JCS)
# 3. Sign with agent's Ed25519 private key
# 4. Encode as base64url (no padding)
```

### Domain Separation
All PoP signatures use a **domain separator** to prevent cross-protocol replay:
```
PopRequest = "rilavo_pop_v0" || JCS(payload)
```
This ensures a PoP signature can never be confused with a credential signature or any other signature type.

---

## Key Management

| Aspect | Recommendation |
|--------|----------------|
| **Issuer keys** | Generate with HSM/KMS; rotate annually; revoke on compromise |
| **Agent keys** | Generated per agent instance; rotate on compromise |
| **Key storage** | HSM/KMS in production; never raw keys on disk |
| **Rotation** | Issuer: annual (or on compromise); Agent: per-instance |

### Key Rotation
1. Generate new keypair
2. Publish new directory entry with `valid_from` = now
2. Set old key's `valid_until` = rotation time
3. Wait for all verifiers to refresh (5 min cache + grace)
4. Old credentials naturally expire (max 4h TTL)

---

## Post-Quantum Readiness (P-28)

| Aspect | Status |
|--------|--------|
| Current algorithm | Ed25519 (classical) |
| Post-quantum candidate | TBD (tracking NIST PQC standardization) |
| Migration trigger | NIST standardization + credible quantum threat |
| Migration path | Dual-signature period → algorithm switch |

**P-28 is a trigger, not a timeline.** Reopens only when there's a credible quantum threat to Ed25519 and a standardized replacement exists.

---

## Security Considerations

| Threat | Mitigation |
|--------|------------|
| Nonce reuse | Ed25519 deterministic nonces eliminate this class |
| Side-channel attacks | Ed25519 constant-time by design |
| Fault injection | Ed25519 constant-time + no branches on secret data |
| Key extraction | HSM/KMS in production; no raw keys in memory |
| Algorithm substitution | No algorithm agility — fixed to Ed25519 |

---

## References

- **RFC 8032** — Edwards-Curve Digital Signature Algorithm (EdDSA)
- **RFC 8785** — JSON Canonicalization Scheme (JCS)
- **RFC 6979** — Deterministic DSA/EdDSA Nonce Generation
- **RFC 8707** — OAuth 2.0 Resource Indicators

---

> **Try it first:** [Interactive Playground](../playground/index.md) — issue and verify credentials in your browser without setting up infrastructure.