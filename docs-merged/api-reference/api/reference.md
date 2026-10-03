---
title: API Reference
description: Complete API reference for all Rilavo SDKs
---

# API Reference

> **Interactive testing:** [Interactive Playground](../playground/index.md) — test credential issuance and verification in your browser.


Choose your SDK to view the complete API reference:

- [Python SDK](python/index.md)
- [TypeScript SDK](typescript/index.md)
- [Go SDK](go/index.md)
- [Next.js Middleware](nextjs/index.md)
- [WordPress Plugin](wordpress/index.md)

## Quick Links

| SDK | Package | Version | Status |
|-----|---------|---------|--------|
| Python | `rilavo` | 0.1.0 | ✅ Stable |
| TypeScript | `@rilavo/sdk` | 0.1.0 | ✅ Stable |
| Go | `github.com/rilavo/rilavo-go` | 0.1.0 | ✅ Stable |
| Next.js | `@rilavo/next` | 0.1.0 | ✅ Stable |
| WordPress | `rilavo/rilavo-wp` | 0.1.0 | ✅ Stable |

## Common Types

All SDKs share these core types:

### Credential Fields

```json
{
  "iss": "string",      // Issuer ID
  "sub": "string",      // Subject (principal)
  "agt": "string",      // Agent DID
  "apk": "string",      // Agent public key (base64url)
  "act": "string",      // Action class
  "aud": "string",      // Audience
  "iat": "integer",     // Issued at (Unix timestamp)
  "exp": "integer",     // Expires at (Unix timestamp)
  "nonce": "string",    // Single-use nonce (base64url)
  "sig": "string",      // Issuer signature (base64url)
  "ver": "integer"      // Version (default: 1)
}
```

### Proof-of-Possession Request

```json
{
  "method": "string",           // HTTP method
  "path": "string",             // Request path
  "requestedAction": "string",  // Action being performed
  "signature": "string",        // Ed25519 signature (base64url)
  "requestNonce": "string"      // Request-specific nonce
}
```

### Verification Result

```json
{
  "accepted": "boolean",
  "reasonCode": "string | null"
}
```

## Reason Codes

| Code | Description |
|------|-------------|
| `missing_field` | Required field missing or empty |
| `malformed_credential` | Invalid field type/format |
| `unrecognized_version` | Version not supported |
| `audience_mismatch` | Credential audience doesn't match verifier |
| `expired` | Credential has expired |
| `not_yet_valid` | Credential not yet valid (clock skew) |
| `unknown_issuer` | Issuer not in directory or directory unreachable |
| `key_not_valid_at_issuance` | Issuer key compromised retroactively |
| `invalid_signature` | Issuer signature verification failed |
| `replay_detected` | Nonce already used |
| `revoked` | Nonce in revocation log |
| `proof_of_possession_failed` | PoP signature invalid or mismatch |
| `delegation_not_permitted` | Delegation not allowed (`dlg > 0`) |
| `scope_mismatch` | Delegated action not in scope |
