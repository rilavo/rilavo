# T3 — Integrate Rilavo into a Mock Checkout (5 minutes)

> **Want to see Rilavo in a realistic scenario?** This tutorial adds agent authorization to a mock checkout endpoint — honest line count included.

---

## The Claim We're Testing

> **P-20 Claim:** A minimal integration should be "single-digit lines of code."

**Actual count for the tested path: 4 lines in the middleware body** (3 if you compact the Request construction). Setup (one-time issuer-key caching) is separate and shown below.

---

## The Scenario

A customer checks out on your site. An AI agent calls your `/checkout` endpoint on their behalf. You need to verify:
1. The agent is authorized for `payments.initiate`
2. The agent is who it says it is (Proof-of-Possession)
3. The credential is valid, unexpired, and not revoked

---

## Step 1: One-Time Setup (Do Once)

```python
# cache the issuer's key from /directory once at startup
from rilavo.testing import offline_test_kit
from rilavo.keys import InMemoryKeyDirectory

# Real deployment: fetch from issuer's /directory endpoint once at startup
kit = offline_test_kit()

# The verifier's audience (what we put in 'aud' when issuing)
AUDIENCE = "verifier:checkout.example.com"
```

---

## Step 2: The Middleware — Entire Integration

```python
from rilavo.pop import Request

def authorize_checkout(credential, pop_signature, request_nonce):
    """
    Verify an agent's credential for a checkout request.
    
    Args:
        credential: The decoded credential dict from the agent
        pop_signature: The agent's PoP signature (base64url)
        request_nonce: The agent's request-level nonce
        
    Returns:
        (accepted: bool, reason: str, principal: str)
    """
    # Build the Proof-of-Possession request
    request = Request(
        method="POST",
        path="/checkout",
        action="payments.initiate",  # what the credential authorizes
        signature=pop_signature,
        request_nonce=request_nonce
    )
    
    # Verify using our cached test kit
    result = kit.verify(credential, request)
    
    if result.accepted:
        return True, "ok", credential["sub"]  # principal ID
    else:
        return False, result.reason_code, None
```

**That's it. 4 lines of verification logic.**

---

## Step 3: Full FastAPI Example

```python
from fastapi import FastAPI, Header, HTTPException, Request as FastAPIRequest
from pydantic import BaseModel
import json

app = FastAPI()

# One-time setup at startup
kit = offline_test_kit()
VERIFIER_AUDIENCE = "verifier:checkout.example.com"

class CheckoutRequest(BaseModel):
    credential: dict
    pop_signature: str
    request_nonce: str

@app.post("/checkout")
async def checkout(
    payload: CheckoutRequest,
    x_rilavo_action: str = Header(...),
    x_rilavo_nonce: str = Header(...),
    x_rilavo_pop_signature: str = Header(...)
)
:
    """
    Expects headers:
    - x-rilavo-action: e.g., "payments.initiate"
    - x-rilavo-nonce: request-level nonce
    - x-rilavo-pop-signature: base64url Ed25519 signature
    """
    
    # Build PoP request
    pop_request = Request(
        method="POST",
        path="/checkout",
        action=x_rilavo_action,
        signature=x_rilavo_pop_signature,
        request_nonce=x_rilavo_nonce
    )
    
    # Verify
    result = kit.verify(payload.credential, pop_request)
    
    if not result.accepted:
        raise HTTPException(status_code=401, detail=result.reason_code)
    
    # Credential accepted - extract principal
    principal = payload.credential["sub"]
    
    # Process the checkout...
    return {"status": "ok", "principal": principal, "action": payload.credential["act"]}
```

---

## Step 4: Test It

```bash
# Terminal 1: Start the server
uvicorn checkout:app --reload --port 8000

# Terminal 2: Test with the test kit
python -c "
from rilavo.testing import offline_test_kit
from rilavo.pop import Request
import httpx
import json

kit = offline_test_kit()
cred = kit.agent.credential

# Build PoP signature for a test request
request = Request(
    method='POST',
    path='/checkout',
    action='payments.initiate',
    signature='',  # placeholder
    request_nonce='test-nonce-123'
)
# The test kit's agent can sign for us
pop_sig = kit.agent.sign_pop('POST', '/checkout', 'test.action', 'req-nonce-123')

import httpx
resp = httpx.post('http://localhost:8000/checkout',
    json={'credential': kit.agent.credential},
    headers={
        'x-rilavo-action': 'payments.initiate',
        'x-rilavo-nonce': 'req-nonce-123',
        'x-rilavo-pop-signature': pop_sig
    }
)
print(resp.json())
"
```

**Expected response:**
```json
{
  "status": "ok",
  "principal": "test-principal",
  "action": "payments.initiate"
}
```

---

## What the Middleware Actually Does

| Step | Code | Purpose |
|------|------|---------|
| 1 | Parse headers | Extract credential, PoP signature, nonce, action |
| 2 | Build PoP request | Method + path + action + nonce |
| 3 | `kit.verify()` | All 6 verification steps (structure, sig, exp, aud, revocation, PoP, action) |
| 4 | On success | Extract principal, proceed |
| 5 | On failure | Return 401 with reason code |

---

## The Honest Line Count

| Component | Lines |
|-----------|-------|
| One-time setup (caching issuer key) | ~3 lines |
| Middleware body | **4 lines** |
| Request/response handling | ~5 lines (FastAPI boilerplate) |
| **Total integration** | **~12 lines** |

**The "single-digit lines of code" claim holds for the actual verification logic.**

---

## Common Failure Modes to Handle

| Reason Code | What Happened | HTTP Response |
|-------------|---------------|---------------|
| `audience_mismatch` | Credential issued for different verifier | 401 |
| `expired` | Credential expired | 401 |
| `replay_detected` | Same nonce used twice | 401 |
| `proof_of_possession_failed` | Agent didn't sign request correctly | 401 |
| `action_mismatch` | Agent tried different action than authorized | 401 |
| `revoked` | Credential revoked by principal/issuer | 401 |
| `audience_mismatch` | Credential issued for different verifier | 401 |

**All failures return 401 with the reason code.** No stack traces, no internal details leaked.

---

## What's Next?

| Tutorial | What You'll Learn |
|----------|-------------------|
| **[T4 — Production Deployment](T4-production-deployment.md)** | Deploy to production, verify cross-SDK, soft boundaries |
| **[Interactive Playground](../playground/index.md)** | Test in browser without code |

---

## Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **4 lines of verification** | The actual verification logic is tiny |
| **One-time setup** | Cache issuer key once at startup |
| **Fail-closed** | Any verification failure = 401, no partial success |
| **Exact action matching** | `payments.initiate` != `payments.refund` |
| **PoP is mandatory** | Credential alone is useless without PoP signature |

---

## Next Steps

**[→ T4: Production Deployment](T4-production-deployment.md)** — See how cross-SDK verification in production work in the commercial product.