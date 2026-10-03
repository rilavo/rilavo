---
title: Go SDK API Reference
description: Complete API reference for the Rilavo Go SDK
---

# Go SDK API Reference (github.com/rilavo/rilavo-go)

> **Quick test:** [Interactive Playground](../../playground/index.md) — try credential issuance and verification in your browser.


Complete API reference for the Rilavo Go SDK. All types and functions are exported from the main package.

## Installation

```bash
go get github.com/rilavo/rilavo-go
```

## Package Import

```go
import "github.com/rilavo/rilavo-go"
```

## Core Types

### `VerifyResult`
Carries accept/reject outcome and reason code.

```go
type VerifyResult struct {
    Accepted   bool
    ReasonCode string
}
```

### `IssuerKeyEntry`
Mirrors the issuer key entry structure.

```go
type IssuerKeyEntry struct {
    IssuerID     string
    PublicKeyPem string
    ValidUntil   int64 // Unix seconds; far-future when active
}
```

### `KeyDirectory`
Pluggable issuer-key lookup interface (fail-closed).

```go
type KeyDirectory interface {
    Lookup(issuerID string) *IssuerKeyEntry
}
```

### `NonceCache`
Pluggable replay-defense interface.

```go
type NonceCache interface {
    SeenBefore(nonce string, windowSeconds int64, now int64) bool
}
```

### `InMemoryNonceCache`
Thread-safe in-memory nonce cache with TTL-based expiration.

```go
type InMemoryNonceCache struct { /* internal */ }

// NewNonceCache creates a new in-memory nonce cache.
func NewNonceCache() *InMemoryNonceCache

// SeenBefore returns true if the nonce was already seen within the window.
func (c *InMemoryNonceCache) SeenBefore(nonce string, windowSeconds int64, now int64) bool
```

### `RedisNonceCache`
Redis-backed nonce cache for distributed deployments.

```go
type RedisNonceCache struct { /* internal */ }

// NewRedisNonceCache creates a new Redis nonce cache.
func NewRedisNonceCache(url, keyPrefix string) *RedisNonceCache

// Connect establishes the Redis connection.
func (c *RedisNonceCache) Connect(ctx context.Context) error

// SeenBefore returns true if the nonce was already seen within the window.
func (c *RedisNonceCache) SeenBefore(nonce string, windowSeconds int64, now int64) bool
```

### `RevocationChecker`
Pluggable revocation lookup.

```go
type RevocationChecker interface {
    IsRevoked(nonce string) bool
}
```

### `VerifyOptions`
Bundles all dependencies for the verification pipeline.

```go
type VerifyOptions struct {
    Audience        string
    IssuerDirectory KeyDirectory
    RevocationLog   RevocationChecker
    NonceCache      NonceCache
    NowSeconds      int64
    LeewaySeconds   int64
    Method          string
    Path            string
    RequestedAction string
    PopSignature    string
    PopNonce        string
}
```

## Core Functions

### `Verify`
Verifies a credential against the provided proof-of-possession and verification options.

```go
func Verify(credentialJSON []byte, opts VerifyOptions) *VerifyResult
```

**Parameters:**
- `credentialJSON`: The base64url-encoded credential
- `opts`: Verification options

**Returns:** `*VerifyResult` with `Accepted` (bool) and `ReasonCode` (string)

### `verifyFields`
Lower-level verification function for pre-parsed fields.

```go
func verifyFields(fields map[string]interface{}, opts VerifyOptions) *VerifyResult
```

## JCS & PoP Utilities

### `Canonicalize`
RFC 8785 (JCS) canonicalization.

```go
func Canonicalize(v interface{}) ([]byte, error)
```

### `PopRequestPayload`
Creates the PoP payload for signing.

```go
func PopRequestPayload(method, path, act, nonce string) []byte
```

### `B64urlEncode` / `B64urlDecode`
Base64url encoding/decoding.

```go
func B64urlEncode(data []byte) string
func B64urlDecode(s string) ([]byte, error)
```

## Nonce Cache

### `NewNonceCache`
Creates a new in-memory nonce cache.

```go
func NewNonceCache() *InMemoryNonceCache
```

### `NewRedisNonceCache`
Creates a new Redis nonce cache.

```go
func NewRedisNonceCache(url, keyPrefix string) *RedisNonceCache
```

## Reason Codes

```go
const (
    ReasonAudienceMismatch        = "audience_mismatch"
    ReasonExpired                 = "expired"
    ReasonNotYetValid             = "not_yet_valid"
    ReasonUnknownIssuer           = "unknown_issuer"
    ReasonKeyNotValidAtIssuance   = "key_not_valid_at_issuance"
    ReasonInvalidSignature        = "invalid_signature"
    ReasonMalformedCredential     = "malformed_credential"
    ReasonUnrecognizedVersion     = "unrecognized_version"
    ReasonMissingField            = "missing_field"
    ReasonReplayDetected          = "replay_detected"
    ReasonRevoked                 = "revoked"
    ReasonProofOfPossessionFailed = "proof_of_possession_failed"
    ReasonScopeMismatch           = "scope_mismatch"
    ReasonDelegationNotPermitted  = "delegation_not_permitted"
)
```

## Doctor & Smoke Testing

### `RunDoctor`
Executes a health check of the Go SDK.

```go
func RunDoctor(online bool) DoctorResult
```

### `RunSmoke`
Runs end-to-end smoke test.

```go
func RunSmoke() bool
```

## Error Handling

All functions follow fail-closed principles:
- Invalid inputs return rejected `VerifyResult`
- Unknown reason codes not possible (typed constants)
- Network failures in `RedisNonceCache` fail-open to in-memory fallback

## Security Notes

- All cryptographic operations use Ed25519 via stdlib (no external deps)
- JCS canonicalization per RFC 8785 (string+integer subset)
- Proof-of-possession uses domain-separated `rilavo_pop_v0`
- Nonce cache uses SHA-256 hashed keys (P-10 discipline)
- Fail-closed on all verification gates
- Stdlib-only crypto (crypto/ed25519)
