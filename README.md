# Rilavo Protocol — Reference Implementation

A stateless, cryptographically signed credential format that lets a receiving system verify,
**without a network call** and without learning anything beyond what the credential discloses,
that an agent holds a specific, time-boxed authorization from a specific principal.

This is the v0 reference implementation of the **Rilavo Protocol Core Technical Specification**
(`../docs/Rilavo_Protocol_Core_Specification.md`), built against the decisions recorded in
`../docs/Rilavo_Protocol_Mother_Blueprint.md`. It is a decided-draft: per P-06, the credential
format freezes only after surviving one production partner's real traffic.

## Install & test

```bash
uv sync
uv run pytest tests/ -q          # 40 conformance + 8 HTTP integration tests
```

## What it implements

| Spec item | Module | Notes |
|---|---|---|
| P-06 Credential format | `credential.py` | 9 mandatory fields + `sig`; `dlg` must be absent/0 at v0; max TTL 4h |
| P-07 Authorization model | `verifier.py`, `pop.py` | exact-match action classes, audience binding, proof-of-possession |
| P-09 Revocation | `revocation.py` | append-only hash-chained log; issuer OR principal; fail-closed |
| P-10 Audit receipts | `receipts.py` | nonce hash + issuer + outcome + timestamp, never full contents |
| P-11 Crypto | `keys.py`, `canonical.py` | Ed25519 only, base64url no padding, RFC 8785 JCS canonicalization |
| P-12 Key management | `keys.py` | rotation with overlap window; retroactive compromise cutoff via `valid_until` |
| P-17 Discovery | `keys.KeyDirectory` | single versioned directory; fail-closed when unreachable |
| P-19 Minimal API | `api.py` | exactly two operations: issue, verify |
| P-22 Threat model | `tests/test_conformance.py` | every §7 threat row has a passing test |
| P-29 Performance | — | measured ~0.6 ms per full verify cycle (target: sub-10 ms) |
| P-32 Self-hosting | `cli.py` | keygen → directory entry → issue, zero external dependencies |

## The verification algorithm (Core Spec §6)

Implemented literally in `verifier.py::verify`:

1. audience binding (`aud == verifier_id`) — confused-deputy defense
2. time window (`exp`, `iat`)
3. issuer lookup — **fail-closed** on unreachable directory
4. retroactive compromise cutoff (`iat <= key.valid_until`)
5. Ed25519 signature over JCS-canonicalized credential sans `sig`
6. replay detection, bounded by the credential's own TTL
7. revocation — **fail-closed** on revoked, unreachable, or stale cache
8. proof-of-possession over this specific request
9. exact-match action class
10. audit receipt, then accept

## Usage

### As a verifier (embedded SDK — no deployment)

```python
from rilavo.api import do_verify
from rilavo.keys import KeyDirectory
from rilavo.revocation import RevocationLog
from rilavo.verifier import NonceCache

directory = KeyDirectory()        # cache issuer keys locally
log = RevocationLog()             # cached copy of the shared log
nonces = NonceCache()             # held across verifications — this is your replay defense

result = do_verify(
    verifier_id="verifier:checkout.example.com",
    credential=credential,
    request=request,              # signed request (proof-of-possession)
    key_directory=directory,
    revocation_log=log,
    nonces=nonces,                # pass YOUR cache; default creates a fresh one per call
)
result.accepted, result.reason_code
```

> **Important:** always pass your own persistent `NonceCache`. The default creates a new
> cache per call, which cannot see replays across calls.

### Self-hosted issuance (CLI)

```bash
uv run rilavo keygen --out issuer.pem > directory_entry.json
uv run rilavo issue --key issuer.pem \
  --principal acme-corp:runner-04 --agent agt_7d3e1c \
  --agent-key "<agent ed25519 public key, base64url>" \
  --action-class data.read --audience verifier:checkout.example.com
```

No dependency on any external infrastructure — that is the checkable test of whether
self-hosting is real (Core Spec §8).

## HTTP deployment

```python
from rilavo.service import RilavoService, post, get
from rilavo.pop import sign_request

svc = RilavoService().start()          # binds an ephemeral port; svc.url is the base
status, entry = get(svc.url, "/directory")   # publishable key-directory entry (P-17/P-32)
status, cred  = post(svc.url, "/issue", {
    "principal": "acme-corp:runner-04", "agent": "agt_7d3e1c",
    "agent_public_key": agent_pub_b64,
    "action_class": "data.read", "audience": entry["verifier_id"]})
status, result = post(svc.url, "/verify",
                      {"credential": cred, "request": signed_request_dict})
```

Endpoints: `POST /issue`, `POST /verify`, `GET /directory`, `GET /health`,
`POST /revoke` (operational extension — explicitly outside the frozen protocol surface).
The service holds **one process-wide `NonceCache`**, so replay detection works across requests.

## Pilot readiness

```bash
uv run python scripts/pilot_readiness.py
```

Runs a simulated first-production-partner workload (3,000 credentials, mixed valid/invalid,
8 concurrent verifiers, outage drills) and writes `pilot/PILOT_REPORT.md`. Six gates:
zero wrong-accepts, sub-10 ms p95 latency, wire size, concurrency safety, mid-TTL revocation,
fail-closed degradation. This rehearses — but does not replace — the Go/No-Go gate's open item.

## Honest gaps (carried from the docs, not hidden)

- TTL (4h), rotation period (90d), and revocation refresh interval (5 min) are **starting
  defaults**, not derived constants — they need pilot data before P-06 freezes.
- Correlation risk: reusing `sub`/`agt` across unrelated verifier relationships is **not yet
  technically enforced** (Core Spec §7 flags this honestly).
- Fail-closed-on-stale-revocation-cache is shipped as one default for everyone; whether it
  should vary by verifier risk tolerance is still an open question.
- True HSM/KMS-backed issuer key custody is the correct target and not guaranteed at v0.
- Verification proves authorization, never agent conduct ("was this agent allowed to try
  this", not "should it be trusted to behave well").

## License

Apache-2.0 (per protocol doc 39: permissive licensing was a deliberate correction of the
earlier copyleft idea).
