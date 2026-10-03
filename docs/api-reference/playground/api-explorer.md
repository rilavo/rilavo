---
title: API Explorer
description: Interactive API reference for Rilavo credential issuance and verification endpoints
---

# API Explorer

Test Rilavo API endpoints interactively. This page documents the HTTP API for credential issuance and verification.

## Issue Credential

**POST** `/issue`

Issues a new Rilavo credential.

### Request

```json
{
  "principal": "org:user-01",
  "agent": "agent-01",
  "agent_public_key": "base64url...",
  "action_class": "data.read",
  "audience": "https://api.example.com",
  "ttl_seconds": 3600,
  "context": {}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `principal` | string | Yes | Subject identifier (e.g., `acme-corp`) |
| `agent` | string | Yes | Agent identifier (e.g., `agent-runner-04`) |
| `agent_public_key` | string | Yes | Ed25519 public key in base64url encoding |
| `action_class` | string | Yes | Authorized action (e.g., `data.read`, `data.write`, `admin`) |
| `audience` | string | Yes | Verifier identifier (e.g., `verifier:api.example.com`) |
| `ttl_seconds` | integer | No | Lifetime in seconds (default: 3600, max: 86400) |
| `context` | object | No | Optional metadata |

### Response (Success)

```json
{
  "credential": "base64url...",
  "fields": {
    "iss": "did:example:issuer",
    "sub": "org:user-01",
    "agt": "agent-01",
    "apk": "base64url...",
    "act": "data.read",
    "aud": "https://api.example.com",
    "iat": 1700000000,
    "exp": 1700003600,
    "nonce": "random-nonce",
    "ver": 1,
    "sig": "base64url..."
  }
}
```

### Response (Error)

```json
{
  "error": "invalid_request",
  "message": "agent_public_key must be valid base64url Ed25519 public key"
}
```

## Verify Credential

**POST** `/verify`

Verifies a credential and proof-of-possession.

### Request

```json
{
  "credential": "base64url...",
  "pop": {
    "method": "POST",
    "path": "/api/data",
    "requested_action": "data.read",
    "signature": "base64url...",
    "request_nonce": "unique-nonce"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `credential` | string | Yes | Base64url-encoded credential |
| `pop.method` | string | Yes | HTTP method (GET, POST, PUT, DELETE, etc.) |
| `pop.path` | string | Yes | Request path |
| `pop.requested_action` | string | Yes | Action class being requested |
| `pop.signature` | string | Yes | Ed25519 signature in base64url |
| `pop.request_nonce` | string | Yes | Unique nonce for replay protection |

### Response (Success)

```json
{
  "accepted": true,
  "reason_code": "accept"
}
```

### Response (Failure)

```json
{
  "accepted": false,
  "reason_code": "audience_mismatch"
}
```

## Proof-of-Possession

The agent must sign a payload containing the request details to prove they hold the private key corresponding to the `apk` in the credential.

### PoP Payload Format

```json
{
  "method": "POST",
  "path": "/api/data",
  "act": "data.read",
  "nonce": "unique-nonce"
}
```

The payload is canonicalized using RFC 8785 (JCS - JSON Canonicalization Scheme) and signed with the agent's Ed25519 private key.

```
payload = canonicalize({
  "method": "POST",
  "path": "/api/data",
  "act": "data.read",
  "nonce": "unique-nonce"
})
signature = Ed25519(agent_private_key, payload)
```

The verifier validates the signature using the `apk` from the credential.

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `missing_field` | 400 | Required field missing or empty |
| `malformed_credential` | 400 | Invalid field type/format |
| `unrecognized_version` | 400 | Version not supported (only v1/absent) |
| `audience_mismatch` | 403 | Credential audience doesn't match verifier |
| `expired` | 403 | Credential has expired |
| `not_yet_valid` | 403 | Credential not yet valid (clock skew) |
| `unknown_issuer` | 403 | Issuer not in directory or directory unreachable |
| `key_not_valid_at_issuance` | 403 | Issuer key compromised retroactively |
| `invalid_signature` | 403 | Issuer signature verification failed |
| `replay_detected` | 403 | Nonce already used (within TTL) |
| `revoked` | 403 | Credential in revocation log |
| `proof_of_possession_failed` | 403 | PoP signature invalid or mismatch |
| `delegation_not_permitted` | 403 | Delegation not allowed (dlg > 0 at v0) |
| `scope_mismatch` | 403 | Requested action doesn't match credential act |

## Credential Fields Reference

| Field | Key | Type | Description |
|-------|-----|------|-------------|
| Issuer | `iss` | string | Issuer identifier (DID or issuer ID) |
| Subject | `sub` | string | Principal/organization identifier |
| Agent | `agt` | string | Agent identifier |
| Agent Public Key | `apk` | string | Base64url Ed25519 public key |
| Action Class | `act` | string | Authorized action class |
| Audience | `aud` | string | Intended verifier identifier |
| Issued At | `iat` | integer | Unix timestamp |
| Expires At | `exp` | integer | Unix timestamp |
| Nonce | `nonce` | string | Unique issuance nonce |
| Version | `ver` | integer | Reserved, not emitted (absent = 1) |
| Signature | `sig` | string | Base64url Ed25519 signature |
| Delegation | `dlg` | integer | Optional, must be 0/absent at v0 |
| Context | `ctx` | string | Optional JSON metadata |

## Verification Flow

1. **Decode** base64url credential
2. **Parse** JSON fields
3. **Check** required fields present
4. **Validate** version (absent or 1)
5. **Check** expiry (`exp > now`)
6. **Check** not before (`iat <= now + skew`)
7. **Lookup** issuer in directory
8. **Verify** directory entry not expired
9. **Verify** issuer signature over canonicalized payload
10. **Check** revocation log (fail-closed)
11. **Verify** PoP signature over canonicalized request payload
12. **Match** requested action to credential `act` (exact match)
13. **Match** audience to credential `aud`
14. **Accept** or **Reject** with reason code

## SDK Integration

### Python
```python
from rilavo import verify_credential, pop_request_payload

result = verify_credential(
    credential_b64url=cred,
    pop=pop_request_payload("POST", "/api/data", "data.read", "nonce-123"),
    pop_signature=signature,
    audience="verifier:api.example.com"
)
```

### TypeScript
```typescript
import { verifyCredential, popRequestPayload } from '@rilavo/sdk';

const result = await verifyCredential({
  credentialB64url: cred,
  pop: popRequestPayload("POST", "/api/data", "data.read", "nonce-123"),
  popSignature: signature,
  audience: "verifier:api.example.com"
});
```

### Go
```go
import "github.com/rilavo/rilavo-go"

result, _ := rilavo.VerifyCredential(rilavo.VerifyOptions{
    CredentialB64url: cred,
    Pop: rilavo.PoPRequest{
        Method: "POST",
        Path: "/api/data",
        RequestedAction: "data.read",
        RequestNonce: "nonce-123",
    },
    PopSignature: signature,
    Audience: "verifier:api.example.com",
})
```

## Related Documentation

- [Interactive Playground](index.md) - Try it in the browser
- [Getting Started](getting-started.md) - Step-by-step tutorial
- [API Reference](../api/reference.md) - Complete SDK documentation
