# Rilavo Protocol — Authorization Model (P-07)

**Tree:** Protocol  
**Wave:** 2 — Engineering Core  
**Status:** Decided  
**Depends on:** P-06 (Credential Specification)  
**Closes when:** Same freeze condition as P-06 — they change together or not at all.

---

## The Big Picture: Three Checks, Three Questions

When a verifier receives a credential, it must answer **three independent questions** before allowing a request. Each question is answered by a distinct mechanism, and **all three must pass**.

| Question | Mechanism | Field | What It Protects |
|----------|-----------|-------|------------------|
| **"Is this credential valid *here*?"** | Audience Binding | `aud` | Prevents credential misuse at wrong destination |
| **"Is the presenter the true holder?"** | Proof-of-Possession | `apk` + PoP signature | Prevents credential theft/replay |
| **"Is this request inside the grant?"** | Action-Class Match | `act` | Prevents scope creep / privilege escalation |

**All three must pass.** If any fails, the request is rejected — no partial credit, no "close enough."

---

## 1. Audience Binding — "Is this credential valid *here*?"

### The Rule
The credential's `aud` field must **exactly equal** the verifier's own registered identifier.

### Why It Matters
A credential issued for `verifier:checkout.example.com` is **cryptographically inert** at any other verifier. Not policy-inert — **structurally inert**. The verifier's own check rejects it before anything else runs.

This is deliberately borrowed from **OAuth 2.1's Resource Indicators (RFC 8707)** rather than invented. It solves the **confused-deputy problem** the same well-tested way.

### Example
```json
{
  "aud": "verifier:checkout.example.com"
}
```

- ✅ Accepted at `verifier:checkout.example.com`
- ❌ Rejected at `verifier:payments.example.com` (different `aud`)
- ❌ Rejected at `verifier:checkout.example.com:8080` (different string)

**No wildcards. No prefixes. Exact match only.**

---

## 2. Proof-of-Possession (PoP) — "Is the presenter the true holder?"

### The Rule
Holding a valid credential is **not sufficient** to act on it. The agent must additionally sign the **specific request being made** with the private key matching `apk`.

### What Gets Signed (PoP Payload)
```json
{
  "method": "POST",
  "path": "/charge",
  "act": "payments.initiate",
  "nonce": "request-level-nonce-123"
}
```

The agent signs this with its private key. The verifier checks the signature against `apk` from the credential.

### Why This Matters
> **A copied credential is useless without the private key.**

A verifier that checks only the credential's own signature and skips PoP has implemented the model incorrectly. That gap is exactly how a *copied but not stolen* credential becomes exploitable — copying the credential doesn't copy the private key.

### What the Agent Sends
| Header | Value |
|--------|-------|
| `x-rilavo-credential` | Base64url-encoded credential JSON |
| `x-rilavo-pop-signature` | Base64url Ed25519 signature of PoP payload |
| `x-rilavo-request-nonce` | Request-level nonce (fresh per request) |
| `x-rilavo-action` | The action class being requested |
| `x-rilavo-method` | HTTP method (e.g., `POST`) |
| `x-rilavo-path` | Request path (e.g., `/charge`) |

---

## 3. Action-Class Matching — "Is this request inside the grant?"

### The Rule
The `act` field is a **dot-namespaced string** (e.g., `payments.initiate`, `orders.create`, `data.read`).

**v0 Decision: Exact match only. No wildcards. No hierarchy.**

| Credential `act` | Request `act` | Result |
|------------------|---------------|--------|
| `payments.initiate` | `payments.initiate` | ✅ Match |
| `payments.initiate` | `payments.refund` | ❌ No match |
| `payments.initiate` | `payments.initiate.foo` | ❌ No match |
| `payments.*` | `payments.initiate` | ❌ Invalid (wildcards not allowed) |

**No wildcards. No hierarchy. Exact string match only.**

### Why No Hierarchy/Wildcards?
1. **Predictability**: Developers know exactly what each credential permits
2. **Auditability**: Easy to audit — no implicit permissions
3. **Principle of least privilege**: Issuers grant exactly what's needed

---

## Worked Example — Full Cycle

### 1. Principal Authorizes Agent
```
Principal: acme-corp
Agent: agent-runner-04
Action: payments.initiate
Audience: verifier:checkout.example.com
TTL: 1 hour
```

### 2. Issuer Signs Credential
Issuer creates credential per P-06 (Credential Specification), returns to agent.

```json
{
  "iss": "rilavo:iss:8f2a...c91",
  "sub": "acme-corp:agent-runner-04",
  "agt": "agt_7d3e1c",
  "apk": "MCowBQYDK2VwAyEA...",
  "act": "payments.initiate",
  "aud": "verifier:checkout.example.com",
  "iat": 1755000000,
  "exp": 1755014400,
  "nonce": "kQ2f9xVh7pR1mT8w",
  "sig": "base64url(...)"
}
```

### 3. Agent Makes Request
Agent sends request to verifier:
```http
POST /charge HTTP/1.1
Host: checkout.example.com
x-rilavo-credential: <base64url-credential>
x-rilavo-pop-signature: <base64url-Ed25519-signature>
x-rilavo-request-nonce: req-nonce-123
x-rilavo-action: payments.initiate
```

### 4. Verifier Runs All Checks
1. ✅ Parse & validate structure
2. ✅ Verify Ed25519 signature over credential (using `apk`)
3. ✅ Check expiration (`now < exp` && `now >= iat`)
3. ✅ Check audience (`cred.aud == "verifier:checkout.example.com"`)
4. ✅ Check revocation (nonce not in revocation log)
5. ✅ Check PoP (verify request signature against `apk`)
6. ✅ Check action class (`request.act == "payments.initiate" == cred.act`)
7. ✅ **ACCEPT** → logs audit receipt, proceeds

### 5. Verifier Logs Audit Receipt
```json
{
  "issuer": "rilavo:iss:8f2a...c91",
  "credential_hash": "sha256:71ac...409",
  "outcome": "accept",
  "reject_reason": null,
  "verified_at": 1755000012
}
```

---

## Naming Convention for Action Classes

**Format:** Dot-namespaced, verb-object or object-verb, issuer-scoped by convention.

| Good Examples | Why |
|---------------|-----|
| `payments.initiate` | Verb-object, clear intent |
| `payments.refund` | Distinct from initiate |
| `orders.create` | Clear domain |
| `orders.cancel` | Distinct action |
| `data.read` / `data.write` | Clear CRUD mapping |
| `messages.send` | Clear intent |

**Known edge case (named honestly):** Two unrelated issuers could independently choose the same string — e.g., both use `data.read` to mean different things. v0 has **no global registry** to prevent this.

**Working mitigation:** `aud` binding already scopes a credential to one verifier, and a verifier only has to interpret action-class strings meaningfully within its own domain.

---

## Summary: The Three Checks Visualized

```
                    ┌─────────────────────┐
                    │  Credential Received │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
       │  Audience   │  │  Proof of   │  │   Action    │
       │  Binding    │  │  Possession │  │    Match    │
       │   (aud)     │  │   (PoP)     │  │   (act)     │
       └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                    ┌─────────────────────┐
                    │   ALL MUST PASS     │
                    │     → ACCEPT        │
                    │   ANY FAIL → REJECT │
                    └─────────────────────┘
```

---

## Common Implementation Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Skip PoP check | Copied credentials work | Always verify PoP signature |
| Skip audience check | Credential works at wrong verifier | Always check `aud == me` |
| Use prefix matching for `act` | `payments.*` matches `payments.refund` | Exact string match only |
| Skip revocation check | Revoked credentials still work | Check revocation log (with cache) |
| Accept expired credentials | `exp` in past still works | Check `now < exp` |

---

## Summary

| Check | Field | Rule | Failure Code |
|-------|-------|------|--------------|
| Audience Binding | `aud` | Exact match to verifier ID | `audience_mismatch` |
| Proof-of-Possession | `apk` + PoP sig | Signs request (method, path, act, nonce) | `proof_of_possession_failed` |
| Action-Class Match | `act` | Exact string match | `action_mismatch` |

**All three are mandatory. No exceptions. No shortcuts.**

---

> **Try it first:** [Interactive Playground](../playground/index.md) — issue and verify credentials in your browser without setting up infrastructure.