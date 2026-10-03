# T1 — Verify Your First Credential (10 minutes, fully offline)

> **New to Rilavo?** This tutorial walks you through verifying a credential from scratch — no servers, no network calls, just code running on your machine.

---

## What You'll Learn

By the end of this tutorial, you'll understand:
- How to verify a Rilavo credential using the Python SDK
- What each verification step does and why it matters
- How to handle common verification failures

---

## Prerequisites

- **Python 3.11+**
- **uv** (or pip) for package management
- **10 minutes** of uninterrupted time

---

## Step 0: One-Time Setup

```bash
# Clone the protocol repo (if you haven't already)
git clone https://github.com/rilavo/rilavo-protocol.git
cd rilavo-protocol

# Install dependencies (creates a virtual environment automatically)
uv sync
```

---

## Step 1: Use the Offline Test Kit

Real verifiers fetch an issuer's public key from a directory once and cache it. For this tutorial, we use the SDK's built-in **fixed test issuer** — a stable, known keypair that never changes.

```python
from rilavo.testing import offline_test_kit

# This gives you everything needed to verify: issuer key, verifier, nonce cache
kit = offline_test_kit()

# The test issuer has a stable identity — same every run
print(f"Test issuer: {kit.issuer.issuer_id}")
# Output: rilavo:iss:38f93d4f0edb4f65
```

**Why a fixed test issuer?** It lets you write deterministic tests and tutorials. In production, you'd fetch the issuer's public key from their directory endpoint once and cache it.

---

## Step 2: Create a Test Credential

```python
# The test kit includes a pre-made agent and credential
credential = kit.agent.credential

print("Credential fields:")
for k, v in credential.items():
    if k != "sig":  # signature is long
        print(f"  {k}: {v}")

# Example output:
# iss: rilavo:iss:38f93d4f0edb4f65
# sub: test-principal
# agt: test-agent
# apk: MCowBQYDK2VwAyEA...
# act: test.action
# aud: test-verifier
# iat: 1755000000
# exp: 1755014400
# nonce: kQ2f9xVh7pR1mT8w
# dlg: 0
# sig: (64-byte base64url signature)
```

---

## Step 3: Verify the Credential

```python
# Create a mock request (what the agent would send with the credential)
from rilavo.pop import Request

request = Request(
    method="POST",
    path="/api/charge",
    action="test.action",
    signature=kit.agent.sign_pop("POST", "/api/charge", "test.action", "request-nonce-123"),
    request_nonce="request-nonce-123"
)

# Verify!
result = kit.verify(credential, request)

if result.accepted:
    print("✅ Credential ACCEPTED")
else:
    print(f"❌ Credential REJECTED: {result.reason_code}")

# Expected output:
# ✅ Credential ACCEPTED
```

---

## Step 4: Understand What Just Happened

The `kit.verify()` call performed **6 checks** in order:

| Step | Check | What It Verifies |
|------|-------|------------------|
| 1 | **Structure** | All required fields present, correct types |
| 2 | **Signature** | Credential was signed by the issuer's private key |
| 3 | **Expiration** | `now < exp` and `now >= iat` |
| 3 | **Audience** | `cred.aud` matches our verifier ID |
| 4 | **Revocation** | Nonce not in revocation log (local cache) |
| 5 | **Proof-of-Possession** | Agent signed *this specific request* with its private key |
| 6 | **Action Class** | Requested action matches `cred.act` exactly |

**All checks are local.** No network call to any central service.

---

## Step 5: See Failure Modes

Let's see what happens when things go wrong:

```python
# 1. Wrong audience
bad_cred = kit.agent.credential.copy()
bad_cred["aud"] = "wrong-verifier"
result = kit.verify(bad_cred, request)
print(f"Wrong audience: {result.reason_code}")  # audience_mismatch

# 2. Expired credential
old_cred = kit.agent.credential.copy()
old_cred["exp"] = 1000000000  # long ago
result = kit.verify(old_cred, request)
print(f"Expired: {result.reason_code}")  # expired

# 3. Replay attack (same nonce twice)
result1 = kit.verify(credential, request)  # first use - OK
result2 = kit.verify(credential, request)  # second use - REPLAY!
print(f"Replay: {result2.reason_code}")  # replay_detected

# 4. Wrong action class
bad_request = Request(
    method="POST",
    path="/api/refund",  # different action!
    action="payments.refund",  # credential has "test.action"
    signature=kit.agent.sign_pop("POST", "/api/refund", "payments.refund", "nonce"),
    request_nonce="nonce"
)
result = kit.verify(credential, bad_request)
print(f"Wrong action: {result.reason_code}")  # action_mismatch
```

**Expected output:**
```
Wrong audience: audience_mismatch
Expired: expired
Replay: replay_detected
Wrong action: action_mismatch
```

---

## Step 6: Try It in the Interactive Playground

Want to experiment without installing anything? Try the **[Interactive Playground](../playground/index.md)** — issue and verify credentials in your browser, see the raw JSON, and experiment with failure modes.

---

## What's Next?

| Tutorial | What You'll Learn |
|----------|-------------------|
| **[T2 — Self-Host an Issuer](T2-self-host-an-issuer.md)** | Run your own credential issuer under your own key |
| **[T3 — Mock Checkout](T3-mock-checkout.md)** | Integrate Rilavo into a realistic checkout flow |
| **[T4 — Production Deployment](T4-production-deployment.md)** | See how cross-SDK verification and production deployment work |

---

## Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **No central server** | Verification is completely local — no API calls to Rilavo or any issuer |
| **Fail-closed by default** | If anything is wrong (expired, wrong audience, revoked, replay), the credential is rejected |
| **Proof-of-Possession is mandatory** | A credential alone is useless; the agent must prove it holds the private key for *each request* |
| **Exact action matching** | `payments.initiate` ≠ `payments.refund` — no wildcards, no hierarchy |
| **Revocation is local** | Verifiers cache the revocation log; no live call to a central service |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'rilavo'` | Run `uv sync` from the `rilavo-protocol` directory |
| `AttributeError: 'dict' object has no attribute 'accepted'` | You're using a dict instead of the `VerificationResult` object |
| `nonce` errors in tests | Each test needs a fresh request nonce |

---

## Next Steps

**[→ T2: Self-Host an Issuer](T2-self-host-an-issuer.md)** — Run your own credential issuer under your own key (10 minutes, fully offline).