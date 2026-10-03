# Rilavo Protocol — API Specification (P-19)

**Tree:** Protocol
**Wave:** 2 — Engineering Core
**Status:** Decided
**Depends on:** P-06, P-07
**Closes when:** Stable barring a breaking credential-format change — this API surface is deliberately small specifically so it rarely needs to change.

## Two calls, minimum viable, on purpose

Everything else — dashboards, analytics, billing — is product surface (E-06), not protocol API. A small, frozen API is itself a defensibility property: it's hard to accidentally fragment a two-call interface.

### `POST /issue`

**Request:**
```json
{
  "principal": "acme-corp",
  "agent": "agent-runner-04",
  "action_class": "payments.initiate",
  "audience": "verifier:checkout.example.com",
  "ttl_seconds": 14400
}
```

**Response (success):**
```json
{ "credential": { "...full P-06 object..." } }
```

**Response (error):**
```json
{ "error": "ttl_exceeds_maximum", "max_ttl_seconds": 14400 }
```

### `POST /verify`

**Request:**
```json
{
  "credential": { "...full P-06 object..." },
  "request": {
    "method": "POST",
    "path": "/charge",
    "signature": "base64url(...)",
    "request_nonce": "..."
  },
  "verifier_id": "verifier:checkout.example.com"
}
```

**Response:**
```json
{ "outcome": "accept", "reject_reason": null }
```
or
```json
{ "outcome": "reject", "reject_reason": "expired" }
```

`reject_reason` maps directly to the reference verification algorithm's named rejection points in the core specification — `audience_mismatch`, `expired`, `not_yet_valid`, `unknown_issuer`, `key_not_valid_at_issuance`, `invalid_signature`, `replay_detected`, `revoked`, `proof_of_possession_failed`, `scope_mismatch`. A caller should never have to guess why a verification failed from a generic error string.

## Worked example — a full failed verification, explained

A credential presented past its expiry: the verifier responds `{"outcome": "reject", "reject_reason": "expired"}`. The calling application can distinguish this from, say, `scope_mismatch` (the agent tried an action outside what it was granted) and react differently — an expired credential might trigger automatic reissuance; a scope mismatch should not, since silently reissuing broader scope than originally intended would defeat the purpose of scoping in the first place.

## Why not a single combined endpoint

A combined `/issue_and_verify` convenience call was considered and rejected: issuance and verification happen in different trust contexts, on different systems, at different times — collapsing them into one endpoint would blur a distinction the whole authorization model depends on being explicit about.

## What would change this decision

A pilot partner surfacing a real, recurring need this two-call surface can't express — at which point the addition gets evaluated against the "small, frozen API" principle explicitly, not added reflexively.
