# T1 — Verify your first credential (10 minutes, fully offline)

**What you'll do:** act as a verifier — check that an agent's credential is
valid, bound to you, unexpired, unrevoked, and signed by its holder.
**What you need:** nothing running. No network. No accounts.

## 0. Setup (one time)

```bash
cd /home/admin/rilavo/rilavo-protocol
uv sync
```

## 1. Start a local test issuer

Real verifiers fetch an issuer's public key once and cache it. Offline, we use
the SDK's published fixed test issuer as a stand-in:

```python
from rilavo.testing import offline_test_kit
kit = offline_test_kit()
print(kit.issuer.issuer_id)
# -> rilavo:iss:38f93d4f0edb4f65   (stable across runs -- it's a fixed keypair)
```

> **Try it first:** [Interactive Playground](../playground/index.md) -- issue and verify credentials in your browser.

```python
print(kit.verifier_id)
# -> verifier:test.rilavo.example
```

## 2. Your agent gets a credential

```python
from rilavo.testing import local_test_agent
agent_priv, agent_pub = local_test_agent()          # agents own their keys

cred = kit.issue(principal="my-org:runner-01",
                 agent_public_key=agent_pub,
                 action_class="data.read")
print(cred.fields["nonce"])    # e.g. U6T3x8i7rmBdHghbZFRESg (random per issue)
```

## 3. The agent signs THIS request (proof-of-possession)

Holding a credential is not enough to act on it — each request is signed by
the agent's own key:

```python
from rilavo.pop import sign_request, Request
sig, nonce = sign_request(agent_priv, "POST", "/resource", "data.read")
request = Request("POST", "/resource", "data.read", sig, nonce)
```

## 4. Verify

```python
result = kit.verify(cred, request)
print(result.accepted, result.reason_code)
# -> True accept
```

## 5. See the rejections too

```python
# (a) a request signed for a DIFFERENT action fails scope check:
sig2, n2 = sign_request(agent_priv, "POST", "/resource", "data.write")
bad_action = kit.verify(cred,
    Request("POST", "/resource", "data.write", sig2, n2))
print(bad_action.reason_code)   # -> scope_mismatch

# (b) replay: presenting the SAME credential+request twice.
# Replay defense needs YOUR verifier-held nonce cache, so drop to the
# underlying do_verify with an explicit cache (what a real verifier does):
from rilavo.api import do_verify
from rilavo.verifier import NonceCache

nonce_cache = NonceCache()      # hold this across ALL your verifications
sig3, n3 = sign_request(agent_priv, "POST", "/resource", "data.read")
req3 = Request("POST", "/resource", "data.read", sig3, n3)

first  = do_verify(kit.verifier_id, cred, req3, kit.key_directory,
                   kit.revocation_log, nonces=nonce_cache,
                   now=cred.fields["iat"] + 1)
print(first.reason_code)        # -> accept

second = do_verify(kit.verifier_id, cred, req3, kit.key_directory,
                   kit.revocation_log, nonces=nonce_cache,
                   now=cred.fields["iat"] + 2)
print(second.reason_code)       # -> replay_detected
```

> Why the cache matters: the default in lower-level helpers creates a fresh
> cache per call, which cannot see replays across calls. A real verifier
> holds ONE cache per process. This is the single most common integration
> mistake, so the tutorial makes you do it right once here.

## What just happened

You performed the entire verification chain offline: audience binding, expiry,
issuer signature over a canonically serialized payload, replay check,
revocation state, proof-of-possession, and exact-match scope — the reference
algorithm from the Core Specification, steps 1–10.

**Next:** [T2 — self-host an issuer](T2-self-host-an-issuer.md)
