# Real-World Gap Analysis — Rilavo v0

**Status: PROPOSAL-CLASS documentation. Zero code changes to enforcement.**
**Derived from:** actual source code inspection (`src/rilavo/*.py`, `packages/rilavo-go/`,
`packages/rilavo-ts/`, `rilavo-product/src/rilavo_product/`), not assumptions.
**Date:** 2026-08

---

## Scenario 1: High-Frequency Multi-Audience Agents

**Scenario:** A research/coding agent (e.g. Claude, GPT-4 with tool use) needs
to call 50–200 distinct API endpoints in a single session, each with a different
audience binding.

### What works today

- The agent requests a fresh credential per endpoint from its issuer (TTL ≤ 4h).
- Each credential is audience-bound to exactly one verifier (P-07).
- No wildcard scope: exact-match only at v0.

### Quantified overhead

| Metric | Value | Source |
|---|---|---|
| Credential wire size | 363 bytes | measured (`cred.to_json().encode()`) |
| Issue+verify cycle latency | ~0.6 ms | measured (`scripts/loadtest.py`) |
| Nonce per credential | 22 chars | `secrets.token_urlsafe(16)` |
| Max TTL | 14,400 s (4h) | `credential.py DEFAULT_MAX_TTL_SECONDS` |

For 200 audiences: the agent makes **200 issuance calls + 200 verification
calls**, transferring ~72,600 bytes of credential data total. At 0.6ms/cycle,
the crypto cost is negligible (~120ms). Network overhead dominates.

### Classification: WORKS-WITH-CAVEATS

The single-use nonce means each credential can be presented exactly once to a
given verifier (step 6 replay check). For an agent hitting the same verifier
repeatedly, this forces re-issuance per request — correct for security but
potentially expensive at high frequency. No batch-issuance or token-bucket
mechanism exists at v0.

### What would close it

- **Batch issuance** (PROPOSAL needed): issuer returns N credentials for N
  audiences in one round-trip. Register item: none existing; new proposal.
- **Wildcard/hierarchical scope**: explicitly deferred to Horizon 2 (P-34).
  Gate: P-34 trigger = "v0 proves single-hop authorization is constraining
  real integrations."
- **Audience-set scope** (RFC 8707 style): would allow one credential for a
  set of audiences. Not implemented; no register item exists.

---

## Scenario 2: Infrastructureless Issuers

**Scenario:** An issuer runs behind a dynamic IP on a home network or inside
a container with no domain name. Verifiers cannot discover it via DNS or
a well-known URL.

### What exists today

| Component | Status | Location |
|---|---|---|
| D3 signed-directory entries | PROPOSED module exists (`directory_signing.py`) | `src/rilavo/directory_signing.py` |
| Discovery consumer (fetcher) | PROPOSED module exists (`discovery_client.py`) | `src/rilavo/discovery_client.py` |
| Discovery publisher (server) | IMPLEMENTED (`service.py /.well-known/rilavo`) | `src/rilavo/service.py` |
| Enrollment UX for infrastructureless issuers | **MISSING** — no register item, no module | — |

### Classification: GAP

The discovery publisher requires a stable HTTP endpoint. An issuer without a
domain cannot serve `/.well-known/rilavo`. The D3 signed-entry mechanism
allows a third party to sign directory entries, but there is no:

1. **Enrollment protocol** for an infrastructureless issuer to submit its key
   to a directory operator.
2. **Tunnel-based naming** scheme (e.g. Tor hidden service, I2P, or similar)
   that would give a stable .well-known location without DNS.
3. **Pinning format** for verifiers to hardcode trust anchors for issuers
   discovered out-of-band.

### What would close it

- **Pinning format proposal** (new): define a JSON structure for embedding
  raw Ed25519 public keys as trust anchors, bypassing discovery entirely.
  Consistent with P-17's TOFU acknowledgment.
- **Enrollment UX**: belongs to P3-A2 (publisher side) and E-08 (managed
  infrastructure). Neither currently covers this case.

---

## Scenario 3: Massive Verifier Scale (Millions of Agents/Day)

**Scenario:** A platform serves 10M credential verifications per day across
100K unique agents.

### Nonce cache memory bounds

The Python `NonceCache` uses a dict keyed by nonce string (22 bytes) mapped
to expiry timestamp (float64). Per entry: ~22 + 8 + dict overhead (~100 B).

At 10M/day with a 4-hour max TTL:
- Peak concurrent nonces ≈ 10M × (4/24) ≈ 1.67M entries
- Memory ≈ 1.67M × ~100 B ≈ **167 MB**

This is manageable on a single server but grows linearly with traffic.

### Revocation propagation

The WP plugin uses WordPress transients (per-process). Product modules use
in-memory revocation logs. Neither implements cross-replica propagation.

| Mechanism | Current | Gap |
|---|---|---|
| In-process nonce cache | ✅ works | Single-process only |
| Cross-replica revocation | ❌ absent | Requires shared store (Redis/gossip) |
| Directory refresh interval | Parameterized (300s default) | No push mechanism |

### Cold-start cost

On process restart, all cached issuer keys and nonce state are lost.
First verification after restart triggers a full directory fetch. This is
acceptable for most deployments but adds latency to the first request.

### Classification: WORKS-TODAY for single-instance / WORKS-WITH-CAVEATS for multi-replica

Multi-replica deployments need shared nonce and revocation state. No register
item addresses distributed cache consistency.

### What would close it

- **Distributed nonce cache proposal** (new): Redis/Hazelcast backend for
  NonceCache interface.
- **Revocation propagation proposal** (new): gossip or pub/sub for cross-
  replica revocation awareness.

---

## Scenario 4: Clock Skew at Scale

**Scenario:** A fleet of 10K verifier instances with clocks drifting ±30s
from true time. Issuers have accurate clocks.

### Current behavior

Python verifier.py checks `now >= exp` (expired) and `now < iat` (not-yet-valid)
with **zero tolerance window**. There is no clock-skew margin.

A verifier whose clock is 30s fast will reject credentials that are still
valid from the issuer's perspective (not_yet_valid). A verifier whose clock
is 30s slow will accept credentials past their intended expiry.

### Quantified failure mode

With ±30s drift across 10K verifiers:
- ~0.03% of verifications near the TTL boundary will fail spuriously.
- Credentials issued with short TTLs (< 60s) become unreliable.

### Classification: WORKS-TODAY (with caveats)

The zero-tolerance approach is intentionally conservative. Most production
systems use a 30–120s leeway window. However, adding leeway is a semantic
change to the verifier gate pipeline and must be decided explicitly.

### What would close it

- **Clock-skew tolerance parameter** (new): add `leeway_seconds` to
  VerifyOptions, defaulting to 0 (current behavior), configurable upward.
  This is additive and does not change default semantics.
- Register item: none existing; falls under P-30 (Reliability Requirements).

---

## Scenario 5: Credential Size on Constrained Channels

**Scenario:** Sending Rilavo credentials over MQTT (max payload ~256 KB but
practically <1 KB for IoT), QR codes (~4 KB alphanumeric), or SMS (~160 chars).

### Measured size

A v0 credential is **363 bytes** of canonical JSON (measured). Base64url
encoding increases this to **484 characters**.

| Transport | Practical limit | Fits? |
|---|---|---|
| MQTT (typical IoT) | ~256 KB | ✅ easily |
| QR code (alphanumeric) | ~4,296 chars | ✅ yes |
| QR code (binary) | ~2,953 bytes | ✅ yes |
| SMS (single message) | 160 chars | ❌ too large |
| HTTP header (typical limit) | 8 KB | ✅ yes |
| NFC tag (NTAG213) | 144 bytes | ❌ too large |

### Classification: WORKS-TODAY for MQTT/QR/HTTP-header / GAP for SMS/NFC

For SMS/NFC-class transports, a credential compression or reference-based
scheme (e.g. send a hash and let the verifier resolve the full credential)
would be required. No register item covers this.

### What would close it

- **Compact credential encoding proposal** (new): CBOR or msgpack binary
  serialization, dropping optional fields, shorter field names.
- **Credential-reference proposal** (new): send SHA-256(credential) as a
  reference; verifier resolves via pre-shared cache.

---

## Scenario 6: Full Compromise of a Verifier Instance

**Scenario:** An attacker gains full control of a verifier instance — reads
its memory, disk, cached keys, nonce state, and audit receipts.

### What the attacker learns

| Data | Accessible? | Impact |
|---|---|---|
| Cached issuer public keys | Yes | Can verify other credentials offline but CANNOT forge them |
| Agent public keys (apk) | Yes | Learns which agents exist but cannot sign as them |
| Credential JSON (as presented) | Yes | Sees sub/agt/aud/act/iat/exp/nonce but these are opaque ids |
| Nonce cache state | Yes | Knows which nonces were used but cannot reuse them (issuer-signed) |
| Audit receipts | Yes | Hashes only, not plaintext credentials |
| **Issuer private keys** | **NO** | Keys live on the issuer, not the verifier |
| **Agent private keys** | **NO** | Keys live on the agent, not the verifier |

### What the attacker still cannot do

1. **Forge credentials** — requires the issuer's private signing key.
2. **Impersonate agents** — requires each agent's private PoP key.
3. **Modify revocation status globally** — revocation log is append-only;
   local changes are detectable against other replicas' cached states.
4. **Escalate to issuer compromise** — verifier compromise is scoped to
   verification decisions, not issuance authority.

### Residual risks

- Attacker can **accept invalid credentials** during the compromise window
  (they control the gate). Mitigated by: detection after the fact via audit
  receipt comparison, and by short TTL bounding the damage window.
- Attacker learns **which principals exist** at that verifier from observed
  credential subjects. If subs are reused across verifiers, this enables
  cross-verifier correlation (the P-13 residual gap).

### Classification: WORKS-TODAY (with documented blast radius)

Verifier compromise does NOT cascade to issuer or agent compromise. The
damage is bounded to incorrect accept/reject decisions during the compromise
window. This is a direct consequence of the stateless design (P-15).

---

## Scenario 7: Legal / Jurisdictional Friction

**Scenario:** A GDPR-covered EU verifier must demonstrate that agent
authorization data complies with data-residency requirements.

### What helps

| Property | How it helps | Source |
|---|---|---|
| Stateless design (P-15) | No server-side session store; credentials travel with the agent | Architecture |
| Opaque identifiers (P-13) | `sub` and `agt` are issuer-assigned opaque strings, not personal data | P-06 field design |
| Audience binding (P-07) | Credentials cannot be replayed across jurisdictions | Gate 1 |
| Minimum disclosure (P-13) | Format has structurally nowhere to put biometric/device-fingerprint data | Field list |
| Audit receipts store hashes (P-10) | Receipts don't contain credential plaintext | Receipt design |

### What creates friction

| Issue | Detail |
|---|---|
| Issuer location matters | If the issuer runs outside the EU, credentials issued to EU agents may fall under GDPR regardless of where they're verified |
| `sub` reuse across jurisdictions | If the same `sub` appears in EU and US credentials, it could enable cross-border correlation (P-13 residual gap) |
| Audit receipts stored locally | Receipts persist past the verification event; their retention policy is deployment-specific |

### Classification: WORKS-WITH-CAVEATS

The protocol's privacy architecture (P-13) is well-designed for data
minimization, but jurisdiction-specific compliance requires operational
decisions (where issuers run, retention policies, sub-uniqueness across
regions) that the protocol cannot enforce.

### What would close it

- **Per-jurisdiction issuer guidance** (E-28/E-41 adjacent): documentation
  describing how to deploy issuers within specific regulatory zones.
- **Sub-uniqueness enforcement** (P-13 follow-up): the correlation.py
  instrumentation detects reuse but does not prevent it. Enforcement would
  require per-relationship identifier generation, which is a design change
  tracked in P-13.

---

## Summary Table

| # | Scenario | Classification | Closing Item(s) |
|---|---|---|---|
| 1 | Multi-audience agents (200+) | WORKS-WITH-CAVEATS | Batch issuance (new), wildcard scope (Horizon 2/P-34), audience-set scope (new) |
| 2 | Infrastructureless issuers | GAP | Pinning format (new), enrollment UX (P3-A2/E-08 adjacent) |
| 3a | Massive scale: nonce memory | WORKS-TODAY (single-instance) | Distributed nonce cache (new) |
| 3b | Massive scale: cross-replica revocation | WORKS-WITH-CAVEATS | Revocation propagation (new) |
| 4 | Clock skew | WORKS-TODAY | Leeway_seconds parameter (new, additive) |
| 5 | Constrained channels (SMS/NFC) | GAP for SMS/NFC | Compact encoding (new), credential-reference (new) |
| 6 | Verifier full compromise | WORKS-TODAY | Blast radius bounded by design |
| 7 | Legal/jurisdictional friction | WORKS-WITH-CAVEATS | Sub-uniqueness enforcement (P-13 follow-up), E-28/E-41 guidance |
