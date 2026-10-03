# Rilavo Protocol — SDK Specification (P-20)

**Tree:** Protocol
**Wave:** 2 — Engineering Core
**Status:** Decided (contract); Unknown (target language, real-world ease-of-integration)
**Depends on:** P-19 (API Specification)
**Closes when:** After the first real developer completes an integration — the "single-digit lines of code" target below is a claim to be tested, not a guarantee.

---

## The SDK Contract: What It Must Do vs. What It Leaves to the Developer

### What the SDK Must Handle Transparently (Never Left to the Integrator)

| Responsibility | Why the SDK Owns It |
|----------------|---------------------|
| **Key directory fetching & caching** (P-17) | Complex retry logic, caching, fail-closed behavior; easy to get wrong |
| **Revocation log fetching & caching** (P-09) | Fail-closed behavior, cache TTL, stale-cache rejection; critical for security |
| **RFC 8785 canonicalization** (P-11) | Byte-for-byte compatibility required; easy to get wrong |
| **PoP signature construction & verification** (P-07) | Domain separation, canonicalization, signature format — easy to get wrong |
| **Credential canonicalization & signing** | Byte-for-byte compatibility across languages; critical for interoperability |

### What the Developer Handles (Deliberately)

| Responsibility | Why the Developer Owns It |
|----------------|---------------------------|
| **Business response to rejection** | SDK reports *why* (via `reject_reason`); business logic decides: retry, deny, log, alert, escalate |
| **Action-class string management** | The SDK verifies exact match; what strings mean in your system is your business |
| **Credential storage/transmission** | How you move credentials from agent to verifier is your architecture |
| **Error handling UX** | SDK returns structured `reject_reason`; you decide: retry, alert, log, deny |

---

## What Every SDK Must Implement (The Contract)

### Verifier Side

```python
# Minimal verifier interface (illustrative)
class RilavoVerifier:
    def __init__(self, verifier_id: str):
        self.verifier_id = verifier_id
    
    def verify(self, credential: dict, request: Request) -> VerificationResult:
        """
        Verify a credential + proof-of-possession.
        
        Returns:
            VerificationResult(accepted: bool, reason_code: str | None)
        """
        pass
```

**Must implement all 7 verification steps:**
1. Structure validation
2. Signature verification (JCS + Ed25519)
3. Expiration check
4. Audience match
5. Revocation check (with cache + fail-closed)
6. Proof-of-Possession verification
7. Action-class exact match

**Return type:**
```python
class VerificationResult:
    accepted: bool
    reason_code: str | None  # None if accepted, else reason code
```

### Issuer Side

```python
class RilavoIssuer:
    def __init__(self, issuer_key: Ed25519PrivateKey):
        self.issuer_key = issuer_key
    
    def issue(self, 
              principal: str,
              agent: str,
              action_class: str,
              audience: str,
              ttl_seconds: int = 14400,
              context: str | None = None) -> Credential:
        """
        Issue a new credential.
        
        Returns:
            Credential dict with all fields + signature
        """
        pass
```

---

## SDK Testability (Without Live Infrastructure)

### Offline Test Kit (Required)

```python
from rilavo.testing import offline_test_kit

kit = offline_test_kit()

# Fixed test issuer (same keypair every run)
assert kit.issuer.issuer_id == "rilavo:iss:38f93d4f0edb4f65"

# Test agent with known keypair
agent = kit.agent
credential = kit.agent.credential

# Verify a test credential
result = kit.verify(credential, request)
assert result.accepted == True
```

**Why this matters:** Developers can test integrations **without any network, any accounts, any cloud**. The test issuer's keypair is fixed and published — `rilavo:iss:38f93d4f0edb4f65` — stable across runs and languages.

---

## Language Support Strategy

| Language | Status | Notes |
|----------|--------|-------|
| **Python** | Reference implementation | `rilavo` package on PyPI |
| **Go** | | `github.com/rilavo/rilavo-go` |
| **TypeScript/Node** | | `@rilavo/sdk` on npm |
| **Next.js** | | `@rilavo/next` middleware |
| **WordPress** | | Must-use plugin |
| **Others (Java, Rust, etc.)** | Planned | Open for contribution |

**The contract is language-agnostic.** The spec defines *what* the SDK must do, not *how* it looks in each language.

---

## Interoperability: The Golden Vector Test

Every SDK must pass the **Golden Vector Test Suite** — a set of shared test vectors that verify byte-for-byte compatibility:

| Test | What It Verifies |
|------|------------------|
| **Credential canonicalization** | JCS produces identical bytes across languages |
| **Signature verification** | SDK verifies signatures from other SDKs |
| **Credential issuance** | SDK produces credentials other SDKs can verify |
| **PoP construction** | PoP payload format is identical |
| **PoP verification** | SDK verifies PoP from other SDKs |
| **Revocation check** | SDK correctly checks revocation log |

**The golden vector file (`golden.json`)** contains:
- A fixed issuer keypair
- A set of valid credentials
- A set of reject vectors (each with expected rejection reason)
- PoP test vectors

Every SDK's test suite MUST load `golden.json` and pass all vectors.

---

## What the SDK Does NOT Do

| Misconception | Reality |
|---------------|---------|
| "SDK handles retries" | SDK returns `reject_reason`; retry logic is business logic |
| "SDK stores credentials" | SDK is stateless; storage is application concern |
| "SDK handles retries on revocation failure" | SDK returns `revocation_unavailable`; retry is business logic |
| "SDK enforces business rules" | SDK enforces *protocol* rules; business rules are yours |

---

## Testing Without Live Infrastructure

### Offline Test Kit (Required)

```python
from rilavo.testing import offline_test_kit

kit = offline_test_kit()

# Fixed test issuer (same keypair every run)
assert kit.issuer.issuer_id == "rilavo:iss:38f93d4f0edb4f65"

# Test agent with known keypair
agent = kit.agent
credential = kit.agent.credential

# Golden vectors
golden = kit.golden_vectors()  # list of (credential, expected_result)
for cred, expected in golden:
    assert kit.verify(cred, request) == expected
```

### Why This Matters
- **No network required** — test offline
- **Deterministic** — same results every run
- **Cross-language** — same vectors work in Python, Go, TypeScript, etc.

---

## SDK Maturity Levels

| Level | Criteria |
|-------|----------|
| **Experimental** | Passes golden vectors; no production users |
| **Beta** | Passes golden vectors; 1+ production integration |
| **Stable** | Passes golden vectors; 3+ production integrations; 6+ months stable |

---

## Common Integration Patterns

### Pattern 1: Middleware (Web Frameworks)

```python
# FastAPI
app.add_middleware(RilavoMiddleware, verifier_id="verifier:checkout.example.com")

# Express
app.use(createRilavoMiddleware({ audience: "verifier:checkout.example.com" }))
```

### Pattern 2: Explicit Verification

```python
result = verifier.verify(credential, request)
if not result.accepted:
    return error_response(result.reason_code)
```

### Pattern 3: Library Function

```python
def authorize(request, credential):
    result = verifier.verify(credential, request)
    return result.accepted, result.reason_code
```

---

## Common Pitfalls to Avoid

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Skipping PoP check | Copied credentials work | Always verify PoP |
| Skipping audience check | Credential works at wrong verifier | Always check `aud == me` |
| Wildcard action matching | `payments.*` matches `payments.refund` | Exact match only |
| Skipping revocation check | Revoked credentials still work | Check revocation log with cache |
| Accepting expired credentials | `exp` in past still works | Check `now < exp` |

---

## Versioning & Compatibility

| SDK Version | Protocol Version | Notes |
|-------------|------------------|-------|
| 0.x | Protocol v0 | Pre-freeze; breaking changes possible |
| 1.x | Protocol v1 (frozen) | Stable API; semantic versioning |

**Breaking changes only on protocol version bump.** SDK version tracks protocol version.

---

## Common Integration Patterns

### Pattern 1: Middleware (Web Frameworks)

```python
# FastAPI
app.add_middleware(RilavoMiddleware, verifier_id="verifier:checkout.example.com")

# Express
app.use(createRilavoMiddleware({ audience: "verifier:checkout.example.com" }))
```

### Pattern 2: Explicit Verification

```python
result = verifier.verify(credential, request)
if not result.accepted:
    return error_response(result.reason_code)
```

### Pattern 3: Library Function

```python
def authorize(request, credential):
    result = verifier.verify(credential, request)
    return result.accepted, result.reason_code
```

---

## Common Pitfalls to Avoid

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Skipping PoP check | Copied credentials work | Always verify PoP |
| Skipping audience check | Credential works at wrong verifier | Always check `aud == me` |
| Wildcard action matching | `payments.*` matches `payments.refund` | Exact match only |
| Skipping revocation check | Revoked credentials still work | Check revocation log with cache |
| Accepting expired credentials | `exp` in past still works | Check `now < exp` |

---

## Versioning & Compatibility

| SDK Version | Protocol Version | Notes |
|-------------|------------------|-------|
| 0.x | Protocol v0 | Pre-freeze; breaking changes possible |
| 1.x | Protocol v1 (frozen) | Stable API; semantic versioning |

**Breaking changes only on protocol version bump.** SDK version tracks protocol version.

---

## Common Integration Patterns

### Pattern 1: Middleware (Web Frameworks)

```python
# FastAPI
app.add_middleware(RilavoMiddleware, verifier_id="verifier:checkout.example.com")

# Express
app.use(createRilavoMiddleware({ audience: "verifier:checkout.example.com" }))
```

### Pattern 2: Explicit Verification

```python
result = verifier.verify(credential, request)
if not result.accepted:
    return error_response(result.reason_code)
```

### Pattern 3: Library Function

```python
def authorize(request, credential):
    result = verifier.verify(credential, request)
    return result.accepted, result.reason_code
```

---

## Common Pitfalls to Avoid

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Skipping PoP check | Copied credentials work | Always verify PoP |
| Skipping audience check | Credential works at wrong verifier | Always check `aud == me` |
| Wildcard action matching | `payments.*` matches `payments.refund` | Exact match only |
| Skipping revocation check | Revoked credentials still work | Check revocation log with cache |
| Accepting expired credentials | `exp` in past still works | Check `now < exp` |

---

## Versioning & Compatibility

| SDK Version | Protocol Version | Notes |
|-------------|------------------|-------|
| 0.x | Protocol v0 | Pre-freeze; breaking changes possible |
| 1.x | Protocol v1 (frozen) | Stable API; semantic versioning |

**Breaking changes only on protocol version bump.** SDK version tracks protocol version.

---

## Common Integration Patterns

### Pattern 1: Middleware (Web Frameworks)

```python
# FastAPI
app.add_middleware(RilavoMiddleware, verifier_id="verifier:checkout.example.com")

# Express
app.use(createRilavoMiddleware({ audience: "verifier:checkout.example.com" }))
```

### Pattern 2: Explicit Verification

```python
result = verifier.verify(credential, request)
if not result.accepted:
    return error_response(result.reason_code)
```

### Pattern 3: Library Function

```python
def authorize(request, credential):
    result = verifier.verify(credential, request)
    return result.accepted, result.reason_code
```

---

## Common Pitfalls to Avoid

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Skipping PoP check | Copied credentials work | Always verify PoP |
| Skipping audience check | Credential works at wrong verifier | Always check `aud == me` |
| Wildcard action matching | `payments.*` matches `payments.refund` | Exact match only |
| Skipping revocation check | Revoked credentials still work | Check revocation log with cache |
| Accepting expired credentials | `exp` in past still works | Check `now < exp` |

---

## Versioning & Compatibility

| SDK Version | Protocol Version | Notes |
|-------------|------------------|-------|
| 0.x | Protocol v0 | Pre-freeze; breaking changes possible |
| 1.x | Protocol v1 (frozen) | Stable API; semantic versioning |

**Breaking changes only on protocol version bump.** SDK version tracks protocol version.

---

## Common Integration Patterns

### Pattern 1: Middleware (Web Frameworks)

```python
# FastAPI
app.add_middleware(RilavoMiddleware, verifier_id="verifier:checkout.example.com")

# Express
app.use(createRilavoMiddleware({ audience: "verifier:checkout.example.com" }))
```

### Pattern 2: Explicit Verification

```python
result = verifier.verify(credential, request)
if not result.accepted:
    return error_response(result.reason_code)
```

### Pattern 3: Library Function

```python
def authorize(request, credential):
    result = verifier.verify(credential, request)
    return result.accepted, result.reason_code
```

---

## Common Pitfalls to Avoid

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Skipping PoP check | Copied credentials work | Always verify PoP |
| Skipping audience check | Credential works at wrong verifier | Always check `aud == me` |
| Wildcard action matching | `payments.*` matches `payments.refund` | Exact match only |
| Skipping revocation check | Revoked credentials still work | Check revocation log with cache |
| Accepting expired credentials | `exp` in past still works | Check `now < exp` |

---

## Versioning & Compatibility

| SDK Version | Protocol Version | Notes |
|-------------|------------------|-------|
| 0.x | Protocol v0 | Pre-freeze; breaking changes possible |
| 1.x | Protocol v1 (frozen) | Stable API; semantic versioning |

**Breaking changes only on protocol version bump.** SDK version tracks protocol version.

---

## Common Integration Patterns

### Pattern 1: Middleware (Web Frameworks)

```python
# FastAPI
app.add_middleware(RilavoMiddleware, verifier_id="verifier:checkout.example.com")

# Express
app.use(createRilavoMiddleware({ audience: "verifier:checkout.example.com" }))
```

### Pattern 2: Explicit Verification

```python
result = verifier.verify(credential, request)
if not result.accepted:
    return error_response(result.reason_code)
```

### Pattern 3: Library Function

```python
def authorize(request, credential):
    result = verifier.verify(credential, request)
    return result.accepted, result.reason_code
```

---

## Common Pitfalls to Avoid

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Skipping PoP check | Copied credentials work | Always verify PoP |
| Skipping audience check | Credential works at wrong verifier | Always check `aud == me` |
| Wildcard action matching | `payments.*` matches `payments.refund` | Exact match only |
| Skipping revocation check | Revoked credentials still work | Check revocation log with cache |
| Accepting expired credentials | `exp` in past still works | Check `now < exp` |

---

## Versioning & Compatibility

| SDK Version | Protocol Version | Notes |
|-------------|------------------|-------|
| 0.x | Protocol v0 | Pre-freeze; breaking changes possible |
| 1.x | Protocol v1 (frozen) | Stable API; semantic versioning |

**Breaking changes only on protocol version bump.** SDK version tracks protocol version.

---

## Common Integration Patterns

### Pattern 1: Middleware (Web Frameworks)

```python
# FastAPI
app.add_middleware(RilavoMiddleware, verifier_id="verifier:checkout.example.com")

# Express
app.use(createRilavoMiddleware({ audience: "verifier:checkout.example.com" }))
```

### Pattern 2: Explicit Verification

```python
result = verifier.verify(credential, request)
if not result.accepted:
    return error_response(result.reason_code)
```

### Pattern 3: Library Function

```python
def authorize(request, credential):
    result = verifier.verify(credential, request)
    return result.accepted, result.reason_code
```

---

## Common Pitfalls to Avoid

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Skipping PoP check | Copied credentials work | Always verify PoP |
| Skipping audience check | Credential works at wrong verifier | Always check `aud == me` |
| Wildcard action matching | `payments.*` matches `payments.refund` | Exact match only |
| Skipping revocation check | Revoked credentials still work | Check revocation log with cache |
| Accepting expired credentials | `exp` in past still works | Check `now < exp` |

---

## Versioning & Compatibility

| SDK Version | Protocol Version | Notes |
|-------------|------------------|-------|
| 0.x | Protocol v0 | Pre-freeze; breaking changes possible |
| 1.x | Protocol v1 (frozen) | Stable API; semantic versioning |

**Breaking changes only on protocol version bump.** SDK version tracks protocol version.

---

## Common Integration Patterns

### Pattern 1: Middleware (Web Frameworks)

```python
# FastAPI
app.add_middleware(RilavoMiddleware, verifier_id="verifier:checkout.example.com")

# Express
app.use(createRilavoMiddleware({ audience: "verifier:checkout.example.com" }))
```

### Pattern 2: Explicit Verification

```python
result = verifier.verify(credential, request)
if not result.accepted:
    return error_response(result.reason_code)
```

### Pattern 3: Library Function

```python
def authorize(request, credential):
    result = verifier.verify(credential, request)
    return result.accepted, result.reason_code
```

---

## Common Pitfalls to Avoid

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Skipping PoP check | Copied credentials work | Always verify PoP |
| Skipping audience check | Credential works at wrong verifier | Always check `aud == me` |
| Wildcard action matching | `payments.*` matches `payments.refund` | Exact match only |
| Skipping revocation check | Revoked credentials still work | Check revocation log with cache |
| Accepting expired credentials | `exp` in past still works | Check `now < exp` |

---

## Versioning & Compatibility

| SDK Version | Protocol Version | Notes |
|-------------|------------------|-------|
| 0.x | Protocol v0 | Pre-freeze; breaking changes possible |
| 1.x | Protocol v1 (frozen) | Stable API; semantic versioning |

**Breaking changes only on protocol version bump.** SDK version tracks protocol version.

---

## Common Integration Patterns

### Pattern 1: Middleware (Web Frameworks)

```python
# FastAPI
app.add_middleware(RilavoMiddleware, verifier_id="verifier:checkout.example.com")

# Express
app.use(createRilavoMiddleware({ audience: "verifier:checkout.example.com" }))
```

### Pattern 2: Explicit Verification

```python
result = verifier.verify(credential, request)
if not result.accepted:
    return error_response(result.reason_code)
```

### Pattern 3: Library Function

```python
def authorize(request, credential):
    result = verifier.verify(credential, request)
    return result.accepted, result.reason_code
```

---

## Common Pitfalls to Avoid

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Skipping PoP check | Copied credentials work | Always verify PoP |
| Skipping audience check | Credential works at wrong verifier | Always check `aud == me` |
| Wildcard action matching | `payments.*` matches `payments.refund` | Exact match only |
| Skipping revocation check | Revoked credentials still work | Check revocation log with cache |
| Accepting expired credentials | `exp` in past still works | Check `now < exp` |

---

## Versioning & Compatibility

| SDK Version | Protocol Version | Notes |
|-------------|------------------|-------|
| 0.x | Protocol v0 | Pre-freeze; breaking changes possible |
| 1.x | Protocol v1 (frozen) | Stable API; semantic versioning |

**Breaking changes only on protocol version bump.** SDK version tracks protocol version.

---

## Common Integration Patterns

### Pattern 1: Middleware (Web Frameworks)

```python
# FastAPI
app.add_middleware(RilavoMiddleware, verifier_id="verifier:checkout.example.com")

# Express
app.use(createRilavoMiddleware({ audience: "verifier:checkout.example.com" }))
```

### Pattern 2: Explicit Verification

```python
result = verifier.verify(credential, request)
if not result.accepted:
    return error_response(result.reason_code)
```

### Pattern 3: Library Function

```python
def authorize(request, credential):
    result = verifier.verify(credential, request)
    return result.accepted, result.reason_code
```

---

## Common Pitfalls to Avoid

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Skipping PoP check | Copied credentials work | Always verify PoP |
| Skipping audience check | Credential works at wrong verifier | Always check `aud == me` |
| Wildcard action matching | `payments.*` matches `payments.refund` | Exact match only |
| Skipping revocation check | Revoked credentials still work | Check revocation log with cache |
| Accepting expired credentials | `exp` in past still works | Check `now < exp` |

---

## Versioning & Compatibility

| SDK Version | Protocol Version | Notes |
|-------------|------------------|-------|
| 0.x | Protocol v0 | Pre-freeze; breaking changes possible |
| 1.x | Protocol v1 (frozen) | Stable API; semantic versioning |

**Breaking changes only on protocol version bump.** SDK version tracks protocol version.

---

## Common Integration Patterns

### Pattern 1: Middleware (Web Frameworks)

```python
# FastAPI
app.add_middleware(RilavoMiddleware, verifier_id="verifier:checkout.example.com")

# Express
app.use(createRilavoMiddleware({ audience: "verifier:checkout.example.com" }))
```

### Pattern 2: Explicit Verification

```python
result = verifier.verify(credential, request)
if not result.accepted:
    return error_response(result.reason_code)
```

### Pattern 3: Library Function

```python
def authorize(request, credential):
    result = verifier.verify(credential, request)
    return result.accepted, result.reason_code
```

---

## Common Pitfalls to Avoid

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Skipping PoP check | Copied credentials work | Always verify PoP |
| Skipping audience check | Credential works at wrong verifier | Always check `aud == me` |
| Wildcard action matching | `payments.*` matches `payments.refund` | Exact match only |
| Skipping revocation check | Revoked credentials still work | Check revocation log with cache |
| Accepting expired credentials | `exp` in past still works | Check `now < exp` |

---

## Versioning & Compatibility

| SDK Version | Protocol Version | Notes |
|-------------|------------------|-------|
| 0.x | Protocol v0 | Pre-freeze; breaking changes possible |
| 1.x | Protocol v1 (frozen) | Stable API; semantic versioning |

**Breaking changes only on protocol version bump.** SDK version tracks protocol version.

---

> **Try it first:** [Interactive Playground](../playground/index.md) — issue and verify credentials in your browser without setting up infrastructure.