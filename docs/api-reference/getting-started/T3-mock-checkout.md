# T3 — Integrate the SDK into a mock checkout (honest line-count edition)

> **Try it first:** [Interactive Playground](../playground/index.md) — test checkout flow credentials in your browser.


**What you'll do:** add agent-authorization to a pretend checkout endpoint.
**The claim under test:** P-20 says a minimal integration should be
"single-digit lines of code". Here is the actual count for the tested path:
**4 lines** in the middleware body (3 if you compact the Request
construction). Setup (one-time issuer-key caching) is separate and shown too.

## The middleware — the entire integration

```python
from rilavo.testing import offline_test_kit   # real deployment: cache the
kit = offline_test_kit()                      #   issuer's key from /directory

def authorize_checkout(credential, signature, nonce):
    request = Request("POST", "/checkout", "checkout.complete",
                      signature, nonce)
    return kit.verify(credential, request)
```

Line-by-line: line 1 is the function; lines 2–3 build the signed-request
handle from values your endpoint already has; line 4 verifies everything —
signature, expiry, audience binding, replay, revocation state, scope.

## Drive it

```python
from rilavo.pop import Request, sign_request
from rilavo.testing import local_test_agent
agent_priv, agent_pub = local_test_agent()
cred = kit.issue(principal="shopper:01", agent_public_key=agent_pub,
                 action_class="checkout.complete", audience=kit.verifier_id)

sig, nonce = sign_request(agent_priv, "POST", "/checkout", "checkout.complete")
result = authorize_checkout(cred, sig, nonce)
print(result.accepted, result.reason_code)     # -> True accept
```

## Honesty notes (P-20's own discipline)

- The 4-line count covers the middleware body only. Setup — caching the
  issuer's key and holding ONE process-wide nonce cache — is one-time work
  outside the hot path, but it is real work; do not skip the nonce cache.
- Whether real integrations (error handling, business wiring) stay this small
  is Unknown until a real developer tries — tracked in P-20, not assumed here.

**Next:** [T4 — production deployment & cross-SDK verification](T4-production-deployment.md)
