# Rilavo Protocol — Revocation Specification (P-09)

**Tree:** Protocol  
**Wave:** 2 — Engineering Core  
**Status:** Decided (mechanism); Open (fail-open/closed default across risk profiles)  
**Depends on:** P-06 (Credential), P-07 (Authorization)  
**Closes when:** The fail-closed default is revisited once verifiers with genuinely different risk tolerances exist — v0 ships one default for everyone.

---

## Why Revocation Matters

Credentials are short-lived (default 4 hours), but a lot can happen in 4 hours:
- Agent's host machine gets compromised
- Principal ends relationship with agent
- Issuer detects fraudulent issuance
- Key rotation requires invalidating old credentials

Revocation provides a **mechanism to invalidate a credential before its natural expiration**.

---

## The Revocation Log

### Format

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

### Why Hash Chaining?

The `prev_hash` chains entries together. **Anyone who cached an earlier log state can detect retroactive tampering** — including tampering by the log operator itself. This is the actual mechanism behind "the log is trustworthy," not just a claim about intent.

| Property | Why It Matters |
|----------|----------------|
| Append-only | No deletion, no modification of history |
| Hash-chained | Retroactive tampering detectable |
| `revoked_by` field | Accountability — who revoked and why |
| `reason_code` | Machine-readable reason for automation |

---

## Who Can Revoke (And Why Both, Independently)

| Who | Can Revoke | When |
|-----|------------|------|
| **Issuer** | Any credential it issued | Compromise detection, policy violation, key rotation |
| **Principal** | Their own agent's credential | Suspected compromise, end of relationship |

**Neither needs the other's cooperation.** A principal who suspects their agent has been compromised cannot be made to wait on the issuer to act. An issuer that detects fraud shouldn't need the principal's permission to cut off a credential it never should have issued.

---

## The Revocation Check (What Verifiers Do)

### The Check
When a verifier receives a credential, it checks:
1. Is the credential's `nonce` in the revocation log?
2. If yes → **REJECT** (`revoked`)

### Caching (Not a Live Call)
Revocation checks are **not live network calls** per verification:
- Verifiers cache the revocation log locally
- **Default refresh interval: 5 minutes**
- Cache includes the full log + its hash chain

### Fail-Closed Default
If a verifier cannot reach a **current** revocation log state:
1. Cache is fresh (< 5 min) → use cache
2. Cache is stale (> 5 min) AND can't refresh → **REJECT (fail-closed)**

> **Fail-closed** means: if we can't prove the credential is NOT revoked, we assume it IS revoked.

This isn't a live call per verification — it's a local cache check. But once the cache is stale and can't refresh, the default flips to **reject**.

---

## Who Operates the Revocation Log?

| Deployment | Who Runs It |
|------------|-------------|
| **Self-hosted issuer** | You (the issuer operator) |
| **Rilavo Cloud (hosted)** | Rilavo operates the log |
| **Hybrid** | You run your log; Rilavo Cloud runs theirs |

**Key point:** The revocation log is a **separate service** from the issuer. They can be operated independently.

---

## Reason Codes

| Code | Meaning | Who Uses It |
|------|---------|-------------|
| `principal_requested` | Principal requested revocation | Principal |
| `issuer_policy` | Issuer policy violation | Issuer |
| `key_compromise` | Suspected key compromise | Issuer |
| `issuer_rotation` | Key rotation | Issuer |
| `fraud_detected` | Fraud detected | Issuer |
| `principal_ended` | Principal ended relationship | Principal |

---

## Fail-Open vs Fail-Closed: The Trade-off

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Fail-Closed (default)** | Can't reach log → REJECT | High-security, financial, healthcare |
| **Fail-Open** | Can't reach log → ACCEPT (with audit) | Low-risk, high-availability |

**v0 default: Fail-closed.** This is conservative — it prefers false rejections over false acceptances.

> **Open question:** The fail-closed default may need per-risk-profile configuration in the future. This is tracked as an open item.

---

## What Happens During Revocation

### Timeline Example

```
T=0:     Agent credential issued (nonce: kQ2f9xVh7pR1mT8w, exp: +4h)
T=+1h:   Principal discovers agent's laptop stolen
T=+1h:   Principal revokes credential (nonce: kQ2f9xVh7pR1mT8w)
T=+1h:   Entry appended to revocation log
T=+1h:   Verifier cache refreshes (within 5 min)
T=+1h:   Next verification → REJECT (revoked)
T=+4h:   Credential would have expired naturally
```

### What the Agent Sees
- First request after revocation → 401 `revoked`
- All subsequent requests → 401 `revoked`
- No retry, no retry-after — the credential is dead

---

## Cache Behavior Details

| Parameter | Default | Configurable |
|-----------|---------|--------------|
| Cache refresh interval | 5 minutes | Yes |
| Cache TTL (staleness threshold) | 5 minutes | Yes |
| Max cache size | 10,000 entries | Yes |
| Fallback on cache miss | Fail-closed | Yes |

---

## Common Questions

### Q: Why use `nonce` as the revocation target, not `sub` or `agt`?
**A:** The `nonce` is unique per credential. Revoking by `sub` or `agt` would revoke ALL credentials for that principal/agent — too broad. Per-credential revocation is surgical.

### Q: Can a revoked credential be "unrevoked"?
**A:** No. The log is append-only. To restore access, issue a new credential.

### Q: What if the revocation log operator is compromised?
**A:** The hash chain lets verifiers detect retroactive tampering. If the operator tries to remove an entry, the hash chain breaks. Verifiers with an older cached copy will detect the inconsistency.

### Q: What if the revocation log is unavailable at startup?
**A:** Verifier starts with empty cache. First successful fetch populates cache. Until first successful fetch, all verifications fail (fail-closed).

---

## Summary: The Revocation Check in the Verification Algorithm

```
Step 6 (of 7): CHECK REVOCATION
    Is credential.nonce in revocation log?
        → YES → REJECT (revoked)
        → NO  → continue
    Is cache stale (>5 min) AND can't refresh?
        → REJECT (revocation_unavailable)
```

**This is the fail-closed gate. If we can't prove it's NOT revoked, we assume it IS revoked.**

---

> **Try it first:** [Interactive Playground](../playground/index.md) — issue and verify credentials in your browser without setting up infrastructure.