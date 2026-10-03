# P3-A1 PROPOSAL — Discovery Document Format (.well-known/rilavo)

**Status: PROPOSED — not a Decided register item.**
**Traces to:** P-17 (Discovery & Key Directory), D3 (directory signing proposal)

## What this is

A versioned JSON document format for `https://<domain>/.well-known/rilavo`
that carries issuer key directory entries and an optional signed-directory
payload. This is the discovery layer's wire format — the thing a verifier
fetches to learn which issuers it should trust.

## What this is NOT (yet)

- No consumer fetching logic (P3-A3 scope).
- No publisher serving logic (P3-A2 scope).
- Does NOT change any verifier defaults or gate order.
- Does NOT solve bootstrap trust (P-17 names TOFU/TLS as the acknowledged
  limitation; this format inherits that limitation).

## Schema

```json
{
  "rilavo_discovery_version": 1,
  "entries": [
    {
      "issuer_id": "rilavo:iss:<hex16>",
      "public_key_pem": "-----BEGIN PUBLIC KEY-----...",
      "valid_until": <unix_seconds|int|null>,
      "audience_hints": ["verifier:a.example", "verifier:b.example"],
      "directory_signed_payload": { ... optional D3 signed envelope ... }
    }
  ]
}
```

### Field semantics

| Field | Type | Required | Semantics |
|---|---|---|---|
| `rilavo_discovery_version` | integer | Yes | Absent means 1 (P-26 style). Non-1 values are reserved for future breaking changes. |
| `entries` | array | Yes | List of issuer key entries. Empty array = no trusted issuers (fail-closed). |
| `entries[].issuer_id` | string | Yes | Fingerprint-style id: `rilavo:iss:<hex16>`. |
| `entries[].public_key_pem` | string | Yes | PEM-encoded Ed25519 public key (SPKI DER). |
| `entries[].valid_until` | int\|null | No | Unix seconds. Null/absent = currently active. Rotated/compromised keys carry a concrete timestamp per P-12. |
| `entries[].audience_hints` | array[string] | No | Audience ids this issuer issues credentials for. Informational only — verifiers still check `aud` on each credential. |
| `entries[].directory_signed_payload` | object | No | Optional D3 signed envelope (see directory_signing.py). If present, verifiers MAY verify against a trusted directory-signer key but MUST NOT treat unsigned entries differently from signed ones at v0. |

### Unknown-field tolerance

Consumers of this document MUST ignore fields they do not recognize
(fail-open at the discovery parsing layer). The verification pipeline itself
remains fail-closed: unknown fields in the discovery document never affect
credential gate outcomes.

## Version semantics

Absent `rilavo_discovery_version` implies version 1, consistent with P-26.
A future `version: 2` would signal a breaking schema change requiring
explicit opt-in by verifiers (same pattern as credential-level P-26).

## Bootstrap trust (inherited limitation)

First-fetch trust rests on TLS plus a well-known location (P-17). This
format does not solve that. The optional `directory_signed_payload` field
(D3) provides a mechanism for integrity verification AFTER the signer key
is pinned out-of-band, but does not eliminate TOFU.

## Relationship to existing decisions

This is a FORMAT PROPOSAL only. It does not:
- Change P-17's Decided status or add enforcement mechanisms.
- Implement consumer fetching (P3-A3) or publisher serving (P3-A2).
- Touch Wave 6 items, P-06 freeze, or E-28..E-36.
