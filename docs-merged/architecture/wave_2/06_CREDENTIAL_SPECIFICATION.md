# Rilavo Protocol — Credential Specification (P-06)

**Tree:** Protocol
**Wave:** 2 — Engineering Core
**Status:** Decided (draft), not yet frozen
**Depends on:** P-02, P-05
**Closes when:** Survives one production partner's real traffic without a breaking field change.

## Field table

| Field | Type | Required | Meaning |
|---|---|---|---|
| `iss` | string | Yes | Issuer identifier — fingerprint of the issuer's public key |
| `sub` | string | Yes | Principal identifier, issuer-assigned, opaque outside that relationship |
| `agt` | string | Yes | Agent identifier for this specific agent instance |
| `apk` | string | Yes | Agent's Ed25519 public key, base64url, no padding |
| `act` | string | Yes | Action-class this credential authorizes |
| `aud` | string | Yes | The one verifier this credential is valid for |
| `iat` | integer | Yes | Issued-at, Unix seconds |
| `exp` | integer | Yes | Expires-at, Unix seconds |
| `nonce` | string | Yes | Single-use random value, ≥128 bits entropy |
| `dlg` | integer | No | Delegation depth. `0` or omitted at v0 |
| `ctx` | string | No | Free-form context, not interpreted by the protocol |
| `sig` | string | Yes | Ed25519 signature over every preceding field |

## Worked examples

**1. A straightforward credential**, an agent authorized to initiate payments on a checkout endpoint:
```json
{
  "iss": "rilavo:iss:8f2a...c91", "sub": "acme-corp:agent-runner-04",
  "agt": "agt_7d3e1c", "apk": "MCowBQYDK2VwAyEA...",
  "act": "payments.initiate", "aud": "verifier:checkout.example.com",
  "iat": 1755000000, "exp": 1755014400,
  "nonce": "kQ2f9xVh7pR1mT8w", "sig": "base64url(...)"
}
```

**2. A context-bound credential**, the same agent but scoped to one specific order:
```json
{
  "iss": "rilavo:iss:8f2a...c91", "sub": "acme-corp:agent-runner-04",
  "agt": "agt_7d3e1c", "apk": "MCowBQYDK2VwAyEA...",
  "act": "payments.initiate", "aud": "verifier:checkout.example.com",
  "iat": 1755000000, "exp": 1755003600,
  "nonce": "vD8k2NpQz4rL9wXs",
  "ctx": "order_id:9f31a-772",
  "sig": "base64url(...)"
}
```
Note the shorter `exp` window here — a context-bound, single-order credential has no reason to outlive the transaction it was issued for, even though the protocol default allows up to four hours.

**3. A malformed credential, and why it's rejected before signature verification is even attempted:** `aud` empty, or `exp` earlier than `iat`. Both are structural violations checkable without touching cryptography at all, and a correct implementation checks structure before signature — there's no reason to spend a signature verification on an object that's already invalid by construction.

## Size and transport budget

A full credential in this format runs roughly 350–450 bytes as compact JSON, or under 600 bytes base64url-encoded for header transport. That's comfortably inside typical HTTP header size limits, which is why the field list stays deliberately short — every optional field added later has to justify its cost against this budget, not just its usefulness.

## Edge cases

- **`exp` in the past at issuance:** rejected at issuance, not left to the verifier to catch. An issuer should never produce an already-expired credential.
- **Empty `act`:** rejected at issuance — an authorization with no scope authorizes nothing and shouldn't be mistaken for a broad grant.
- **Duplicate `nonce` across two different issuers:** harmless. Nonce uniqueness is tracked per-issuer, not globally, since a verifier already trusts a specific issuer's key before it ever inspects the nonce.

## Alternatives considered

**CBOR instead of JSON:** more compact, genuinely worth revisiting once transport size becomes a real constraint at scale — rejected for v0 because JSON's debuggability during the first pilot integration matters more than the byte savings right now.

**Including the full agent identity chain instead of a flat `agt` string:** rejected — v0 has no delegation (§`dlg` is always 0), so a chain structure would be complexity with nothing yet to represent.

## What would change this decision

A pilot partner needing a field not on this list, evidence that the size budget above is wrong for a real transport path (e.g., a gateway with a tighter header limit than assumed), or a security review finding that flat opaque `sub`/`agt` strings create an unanticipated correlation risk beyond the one already flagged in the threat model (P-22).
