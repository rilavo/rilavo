# Adoption Deep Work — Architecture Study for Real-World Deployment Scenarios

**Status:** PROPOSAL-class architecture study. Zero enforcement changes.
**Derived from:** line-level inspection of `src/rilavo/verifier.py`,
`src/rilavo/credential.py`, `src/rilavo/api.py`, `src/rilavo/middleware.py`,
`src/rilavo/discovery_client.py`, `src/rilavo/observability.py`,
`rilavo-product/src/rilavo_product/*.py`.
**Wire format reference:** 354-byte v0 credential (10 fields + Ed25519 sig).

---

## Scenario A — Multi-Audience Agents (200+ audiences per session)

### Current behavior (grounded in code)

`verifier.py` step 1 (`# 1. Audience binding`, line 102) compares
`fields["aud"] != opts.Audience`. One credential = one audience. No wildcard,
no audience-set. `api.py do_issue()` requires `audience` per call.

An agent hitting 200 distinct API endpoints must:
1. Call its issuer 200 times (one per audience).
2. Store 200 credentials locally.
3. Present the matching credential to each endpoint.

At 354 bytes each: 70,800 bytes total credential storage. At 0.6ms issue+verify
cycle: 120ms aggregate crypto cost. Network dominates.

### Candidate mechanism 1 — Batch Issuance API

**Design:** Add `batch_issue(issuer, requests: list[IssueRequest]) -> list[Credential]`
to `api.py`. Returns N credentials in one round-trip.

**Wire format:** The response body is `{"credentials": [<cred1>, <cred2>, ...]}`.
For 200 credentials × 354 bytes ≈ 70.8 KB response body. With HTTP/2 header
compression and keep-alive, the network cost is one TLS handshake plus ~71 KB.

**Size math vs individual issuance:** Same bytes on the wire for credentials
themselves; savings come from eliminated round-trips (199 fewer HTTPS POSTs).
At typical API latency (~50ms/round-trip), this saves ~10 seconds of wall time.

**Verifier impact:** ZERO. Each credential is independently verifiable by the
existing gate pipeline. Batch issuance is an issuer-side optimization only.

**Failure modes:**
- Partial batch failure: issuer returns per-credential status array.
- Nonce uniqueness across batch: issuer's CSPRNG guarantees this.

**Migration path:** Additive to `api.py`. No verifier changes. New register
item needed: "Batch issuance" (PROPOSAL).

| Property | Individual | Batch |
|---|---|---|
| Round-trips for 200 audiences | 200 | 1 |
| Credential size each | 354 B | 354 B |
| Total credential bytes | 70,800 B | 70,800 B |
| Verifier changes needed | 0 | 0 |

### Candidate mechanism 2 — Audience-Set Scope (RFC 8707 style)

**Design:** Allow `aud` to be an array of audience strings. The verifier
checks `request_audience in credential.aud_set`.

**Wire format change:** `"aud": ["verifier:a", "verifier:b"]` instead of
`"aud": "verifier:a"`.

**Impact on verifier gate order:** Step 1 changes from equality check to
membership check. All other gates unchanged. Gate order preserved exactly.

```python
# Current (verifier.py line 102):
if fields["aud"] != opts.Audience:
    reject("audience_mismatch")

# Proposed:
aud_value = fields["aud"]
if isinstance(aud_value, list):
    if opts.Audience not in aud_value:
        reject("audience_mismatch")
elif aud_value != opts.Audience:
    reject("audience_mismatch")
```

**Security analysis:**
- Larger attack surface: a leaked credential works against multiple verifiers.
- Mitigation: cap set size (e.g. max 10), shorten TTL proportionally.
- P-07 discipline maintained: still bound to explicit audiences, just more than one.

**Canonicalization impact:** JCS subset handles arrays natively. `canonicalize`
already supports `[...]` via the list branch. Wire format grows by ~20 bytes
per additional audience.

**Compatibility:** Old verifiers see `aud` as a non-string type → shape
validation fails at step 0 → `missing_field` or `malformed_credential`.
This is a breaking wire-format change requiring version bump per P-26.

| Property | Single aud (current) | Audience-set |
|---|---|---|
| Verifier changes | 0 | Gate 1 modified |
| Wire size increase | 0 | +~30 B per extra audience |
| Backward compatible | ✅ | ❌ (version bump) |
| Blast radius per leak | 1 audience | N audiences |

### Candidate mechanism 3 — Delegated Local Sub-Issuer

**Design:** The agent's harness (Claude Code, Codex, etc.) holds an intermediate
signing key authorized by the root issuer to mint short-TTL credentials for a
scoped audience set.

**Delegation credential fields:**
```json
{
  "iss": "rilavo:iss:<root_issuer>",
  "sub": "<harness_id>",
  "agt": "<harness_key_fp>",
  "apk": "<harness_intermediate_pubkey>",
  "act": "issue:data.read,data.write",
  "aud": ["verifier:a", "verifier:b"],
  "iat": ...,
  "exp": ...,
  "nonce": "...",
  "dlg_depth": 1,
  "sig": "<root_issuer_signature>"
}
```

**Custody rules:**
- Intermediate key lives in harness process memory only.
- Root issuer sets `dlg_depth=1` and `exp` to a short window (e.g. 24h).
- Compromise of intermediate key exposes only the delegated scope.
- Revocation cascade: root issuer revokes intermediate → all child creds invalid.

**Wave-6 adjacency:** This IS delegation. P-34 explicitly gates it behind
"v0 proves single-hop authorization is constraining real integrations."
Implementing this NOW would violate that trigger. **Not proposed for v0.**

**Verifier impact:** Requires `dlg_depth` field handling (currently rejected
at step 0b delegation check). Requires chain verification logic. This is a
significant semantic change gated by Wave 6.

### Recommendation

**Default: Batch Issuance (mechanism 1).** Zero verifier impact, additive-only,
immediate value for multi-audience agents. Mechanism 2 (audience-set) is the
correct medium-term evolution but requires a P-26 version bump. Mechanism 3
is correctly deferred behind the Wave-6 trigger.

---

## Scenario B — Infrastructureless Issuers

### Current state

`discovery_client.py` refuses non-HTTPS schemes (line 29: `raise ValueError(
f"refusing non-HTTPS scheme..."`). `service.py` serves /.well-known/rilavo
when `serve_discovery=True`. Neither helps an issuer without a domain name.

`directory_signing.py` provides signed directory entries but has NO enrollment
protocol — it assumes entries are already published somewhere reachable.

### Design: "Rilavo ACME" enrollment protocol

**Message flow:**

```
Hidden Machine                    Trust Operator (Harness Vendor)
     |                                      |
     |  1. Generate Ed25519 keypair          |
     |  2. Create enrollment request         |
     |------------------------------------->|
     |     {pubkey, proof_of_possession,     |
     |      claimed_identity, ttl_request}   |
     |                                      |
     |  3. Operator validates + signs        |
     |     directory entry                   |
     |<-------------------------------------|
     |     {signed_directory_entry,          |
     |      well_known_url}                  |
     |                                      |
     |  4. Machine publishes at its URL      |
     |    (or operator publishes on behalf)  |
```

**Step 2 details:** Proof-of-possession uses Ed25519 sign over
`SHA256(pubkey || timestamp || requested_ttl)`, domain-separated as
`rilavo_enrollment_v0`. Prevents key-submission replay.

**Step 3 details:** Trust operator signs the directory entry using
`DirectorySigner.sign()` from `directory_signing.py`. The signed entry is
published either:
- On the operator's own directory (operator-hosted model), or
- Returned to the machine for self-publication (self-hosted model).

**Renewal cadence:** Tied to TTL expiry. Default enrollment TTL = 7 days.
Machine re-enrolls 24h before expiry. If offline past expiry → entry lapses
→ verifiers fail-closed (unknown_issuer). Self-revocation via short TTL.

**Emergency revocation SLA:** Only for infrastructure-anchored issuers
(domain-backed). For hidden machines, short TTL IS the revocation mechanism —
a compromised key becomes useless within hours without any revocation
infrastructure.

**Offline-revocation doctrine:** Short-TTL-as-self-revocation scales to any
number of hidden machines because there is no shared infrastructure to
coordinate. A 7-day TTL means worst-case exposure is bounded by the TTL, not
by how fast a revocation message propagates.

### What verifiers change

NOTHING. Discovery/pinning already supported:
- `DiscoveringKeyDirectory.lookup()` already returns `IssuerKeyEntry` objects
- `verifier.py` step 3 already does `Lookup(issuerID)` → nil check
- Step 4 already checks `iat > valid_until`

### Resource budget (1GB RAM / 2-vCPU host)

| Operation | Memory | CPU | Rate possible |
|---|---|---|---|
| Key generation | <1 KB | <1 ms | unlimited |
| Sign credential | <1 KB stack | <1 ms | >10K/s (Ed25519 is fast) |
| Verify PoP | <1 KB stack | <1 ms | >10K/s |
| Serve /.well-known | ~64 KB (PEM cache) | negligible | HTTP-bound |
| Enrollment processing | ~1 KB per pending request | <5 ms/request | limited by trust operator |

A 1GB-RAM host can comfortably run: OS (~200MB) → available ~800MB. At peak,
100 concurrent issuances × 1KB working set = ~100KB. CPU-bound on Ed25519
signing at ~3000 signs/sec/core × 2 cores. This is far beyond any home-machine
use case.

### Classification: GAP → PROPOSAL READY

Enrollment protocol is fully designed above but NOT implemented (no code).
Register item: new PROPOSAL ("Infrastructureless issuer enrollment").

---

## Scenario C — Millions of Verifications Per Day

### Verifier side

#### Sharded/pluggable NonceCache backends

Current Python implementation (`verifier.py` lines 39–56):
```python
class NonceCache:
    def __init__(self):
        self._seen: dict[str, float] = {}  # nonce -> expiry unix seconds
```

In-memory dict. Eviction scans ALL entries on every call (O(n) eviction).

**Memory math at scale:**

| Concurrent agents | Peak nonces | Dict overhead | Total memory |
|---|---|---|---|
| 1K | ~167K | 130B × 167K | ~21 MB |
| 100K | ~16.7M | 130B × 16.7M | ~2.1 GB |
| 1M | ~167M | 130B × 167M | ~21 GB |

At 100K+ concurrent agents, the in-memory dict becomes the bottleneck.

**SQLite backend design:**
```sql
CREATE TABLE seen_nonces (
    nonce TEXT PRIMARY KEY,
    expiry INTEGER NOT NULL
);
CREATE INDEX idx_expiry ON seen_nonces(expiry);
-- Cleanup: DELETE FROM seen_nonces WHERE expiry < strftime('%s','now');
```
Pros: persistent, survives restarts. Cons: disk I/O per verification (~1ms SQLite read).

**Redis backend design:**
```
SET nonce:{hex} {expiry} EX {ttl_seconds}
EXISTS nonce:{hex}
```
Pros: sub-ms, shared across replicas. Cons: adds dependency, network latency.

Both plug into the existing `NonceCache` interface (seen_before method).

#### Revocation propagation

Current: `RevocationLog` is in-memory per process. Cross-replica awareness
requires external coordination.

**Design options ranked by complexity:**
1. Polling: each replica polls the canonical log every N seconds. Simple, eventual consistency within N seconds.
2. Pub/sub (Redis pub/sub, NATS): push updates. Near-instant but adds dependency.
3. Gossip: anti-entropy protocol. Complex but resilient.

For v0: polling is sufficient. The 5-minute default refresh interval (P-09)
bounds staleness.

#### Cold-start costs

On restart: nonce cache empty → first request triggers full verification path.
Issuer keys re-fetched from directory. Latency spike: ~50ms for first request,
then normal (~0.6ms).

Mitigation: pre-warm by fetching directory on startup before accepting traffic.

### Issuer side at fleet scale

Home machines: local issuance only. Each machine is its own issuer → zero
hotspot. Signing throughput: Ed25519 signs at >10K/s/core. Even a Raspberry Pi
handles >1K/s.

Product issuers: signing throughput bounded by HSM if used (typically
~1K signatures/s for network-attached HSMs, ~10K/s for PCIe HSMs).

Key ceremony notes: root issuer key generation should happen in a controlled
environment (P-12 custody requirements). Ceremony involves: key generation,
public key distribution to directory, backup of encrypted private key,
and operational runbook for rotation.

### Classification: WORKS-TODAY (single-instance) / WORKS-WITH-CAVEATS (distributed)

Distributed deployments need shared nonce/revocation state. Register items
needed for distributed cache backends.

---

## Scenario D — Constrained Channels

### Measured baseline

V0 credential: **354 bytes** JSON (measured from actual output).

Field breakdown (approximate byte counts):
| Field | Example | Bytes |
|---|---|---|
| iss | rilavo:iss:38f93d4f0edb4f65 | 32 |
| sub | acme-corp:runner-01 | 22 |
| agt | agent:test-runner-01 | 22 |
| apk | base64url(32B pubkey) | 43 |
| act | data.read | 9 |
| aud | verifier:x.example | 23 |
| iat | 1787725987 | 10 |
| exp | 1787740387 | 10 |
| nonce | Ah0Tre8Z9NnleOofHNmYvw | 22 |
| sig | base64url(64B signature) | 86 |
| JSON overhead | braces, quotes, commas | ~65 |
| **Total** | | **~354** |

### Compact encoding proposal

Target: <160 bytes for SMS-class transport.

**Approach 1 — Field-name compaction:**
Map long field names to single characters:
| Original | Compact | Savings |
|---|---|---|
| iss | i | ~2 |
| sub | s | ~2 |
| agt | g | ~2 |
| apk | k | ~2 |
| act | a | ~2 |
| aud | d | ~2 |
| iat | t | ~2 |
| exp | e | ~2 |
| nonce | n | ~2 |
| sig | z | ~2 |
Total savings: ~18 bytes from names alone.

**Approach 2 — Binary encoding (CBOR):**
CBOR maps the same data structure to binary with type tags. Estimated size:

| Field | CBOR encoded | Notes |
|---|---|---|
| iss (28 chars) | 30 B | text string header + data |
| sub (~20 chars) | 22 B | text string |
| agt (~20 chars) | 22 B | text string |
| apk (32 raw bytes) | 34 B | byte string header + data |
| act (~10 chars) | 12 B | text string |
| aud (~25 chars) | 27 B | text string |
| iat (unix ts) | 5 B | integer |
| exp (unix ts) | 5 B | integer |
| nonce (16 raw bytes) | 18 B | byte string |
| sig (64 raw bytes) | 66 B | byte string |
| **Estimated total** | **~241 B** | fits SMS-class? borderline |

**Approach 3 — Minimal credential (drop optional fields):**
Strip `sub`, `agt` (agent identity carried out-of-band). Keep only what the
verifier needs for authorization decisions:
| Field | Raw size | CBOR size |
|---|---|---|
| iss fingerprint (8 raw bytes) | 10 B | |
| apk (32 raw bytes) | 34 B | |
| act hash (8 raw bytes) | 10 B | |
| aud hash (8 raw bytes) | 10 B | |
| iat | 5 B | |
| exp | 5 B | |
| nonce (16 raw bytes) | 18 B | |
| sig (64 raw bytes) | 66 B | |
| **Minimal total** | **~158 B** | **fits SMS-class target** |

This requires the verifier to resolve fingerprints back to full values via
the discovery document. Adds a resolution step but stays fail-closed.

### Hash-reference scheme

Send SHA-256(credential_json)[0:16] as a reference. Verifier resolves via:
1. Pre-shared cache (if verifier saw this credential before).
2. Out-of-band fetch from issuer (adds round-trip).

**Cache semantics:** Reference-based scheme requires the verifier to have
seen the exact credential before. First-contact always needs the full
credential. Subsequent presentations can use references IF the verifier
retains a mapping from hash → validation result within the TTL window.

**Replay implications:** Hash-reference inherits the same single-use nonce
semantics. The nonce is included in the hash input, so each presentation has
a unique hash even for the same underlying credential.

### Classification: WORKS-TODAY for MQTT/QR / GAP for SMS/NFC

Compact encoding is a PROPOSAL requiring CBOR support and a version bump
(wire format change). Not implementable without P-26 version management.

---

## Scenario E — GDPR / Jurisdictional

### Operational deployment matrix

| Issuer Location | Residency Zone | Sub-Uniqueness Policy | Compliance Posture |
|---|---|---|---|
| EU (Frankfurt) | EU GDPR | Unique sub per verifier relationship | Strongest — opaque ids prevent cross-border correlation |
| EU (Frankfurt) | EU GDPR | Global stable sub | Weaker — subs could correlate across jurisdictions |
| US (Virginia) | US (no federal privacy law) | Any | Protocol doesn't restrict; deployment-specific compliance needed |
| Multi-region | Mixed | Per-region sub namespace | Requires regional issuer instances |

### Per-jurisdiction guidance skeleton

For each jurisdiction, document:
1. Where the issuer runs (data residency for the signing key).
2. Whether audit receipts are stored and for how long (P-10 retention).
3. Whether `sub` values are globally unique or per-verifier unique.
4. Applicable data-transfer mechanisms (SCCs, adequacy decisions, etc.).

### Retention-policy defaults for receipts

E-21/P-10 specify receipts store hashes, not plaintext. Recommended default:
retain receipts for 90 days, then delete. This is a parameter, not hardcoded.

### Classification: WORKS-WITH-CAVEATS

Protocol design minimizes personal data exposure. Operational choices
(issuer location, retention policy, sub-uniqueness) determine actual
compliance posture.

---

## Adoption Architecture

### Trust-anchor/delegation model

```
Trust Hierarchy:

Root of Trust (out-of-band pinned key OR trusted directory operator)
    |
    ├── Product Issuer (domain-backed, serves /.well-known/rilavo)
    │       |
    │       └── Issues credentials to agents
    │               |
    │               └── Agent presents credential to verifier
    │                       |
    │                       └── Verifier checks against cached issuer key
    │
    ├── Harness Embedded Issuer (delegated, Wave-6 gated)
    │       |
    │       └── Mints short-TTL credentials for scoped audiences
    │
    └── Hidden Machine Issuer (infrastructureless, Rilavo ACME proposal)
            |
            └── Self-publishes or operator-publishes directory entry
```

### Integration path for harness vendors

| Harness | Integration point | Effort | Notes |
|---|---|---|---|
| Claude Code | Tool-call middleware (TS SDK) | Low | `withRilavo` pattern from `@rilavo/next` |
| Codex | API route decorator (FastAPI dep) | Low | `require_rilavo_agent` from `rilavo.fastapi` |
| VS Code extensions | Extension activation hook | Medium | Language-server proxy pattern |
| Hermes | Native Go middleware | Low | `WithRilavo` from Go SDK |
| OpenClaw | Plugin system integration | Medium | Depends on plugin API surface |

All harnesses embed the SDK as a silent issuer: they call `do_issue()`
(or TS `issueCredential()`) transparently when their agents need credentials.
The agent never sees the credential — the harness manages the full lifecycle.

### Incentive design for viral loop

Verified agents unlock access to protected resources. The incentive flow:
1. Developer integrates Rilavo middleware into their API.
2. Their users' agents get verified automatically (via harness embedding).
3. Other API providers see the demand and add Rilavo middleware.
4. More verifiers → more valuable for agents to carry credentials.
5. Network effect: each new verifier increases the value for all existing ones.

This mirrors the Let's Encrypt adoption loop: free certs drove HTTPS adoption,
which made HTTPS mandatory, which drove more cert issuance.

### Phased roadmap mapped to register items

| Phase | Mechanism | Register item | Status |
|---|---|---|---|
| Phase 1 (current) | Core verify pipeline | P-06/P-07/P-09/P-11/P-22 | ✅ Implemented |
| Phase 1 (current) | Middleware WSGI/ASGI | P-18 | ✅ Implemented |
| Phase 1 (current) | FastAPI dependency | P-18 | ✅ Implemented |
| Phase 1 (current) | Observability hooks | D1 proposal | ✅ Implemented |
| Phase 2 (near-term) | Batch issuance | NEW PROPOSAL | Designed, not implemented |
| Phase 2 (near-term) | Clock-skew leeway parameter | P-30 adjacent | Designed, not implemented |
| Phase 2 (near-term) | Compact credential encoding | NEW PROPOSAL | Designed, not implemented |
| Phase 3 (medium-term) | Audience-set scope | P-26 version bump required | Designed, breaking |
| Phase 3 (medium-term) | Delegated sub-issuer | P-34 (Wave 6 trigger required) | ⛔ DO NOT IMPLEMENT |
| Phase 3 (medium-term) | Distributed nonce cache | NEW PROPOSAL | Design sketched |
| Phase 4 (Horizon 2+) | Federated discovery | P-17 successor | ⛔ DO NOT IMPLEMENT |
| Phase 4 (Horizon 2+) | ZK proofs for claims | Horizon 3 (P-35) | ⛔ DO NOT IMPLEMENT |
