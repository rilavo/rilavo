---
title: TypeScript SDK API Reference
description: Complete API reference for the Rilavo TypeScript SDK
---

# TypeScript SDK API Reference (@rilavo/sdk)

> **Quick test:** [Interactive Playground](../../playground/index.md) — try credential issuance and verification in your browser.


Complete API reference for the Rilavo TypeScript SDK. All types and functions are exported from the main entry point.

## Installation

```bash
npm install @rilavo/sdk
```

## Core Exports

```typescript
import {
  // Verification
  verifyCredential,
  VerifyOptions,
  VerifyResult,
  PopRequest,
  NonceCacheLike,
  NonceCache,
  RedisNonceCache,
  KeyDirectory,
  IssuerKeyEntry,

  // Cryptographic utilities
  popRequestPayload,
  b64urlDecode,
  b64urlEncode,
  canonicalize,
  sha256Hex,
  ed25519Verify,

  // Issuance
  issueCredential,
  IssueOptions,
  IssuedCredential,
  issuerIdFromPublicKey,
  importEd25519Seed,

  // Diagnostics
  Explanation,
  EXPLANATIONS,
  explainRejection,
  formatExplanation,

  // Testing utilities
  runSmoke,
  runDoctor,
} from '@rilavo/sdk';
```

---

## Verification API

### `verifyCredential`

Verifies a Rilavo credential against a proof-of-possession request.

```typescript
function verifyCredential(
  fields: CredentialFields,
  pop: PopRequest,
  opts: VerifyOptions
): VerifyResult
```

**Parameters:**
- `fields`: The parsed credential fields to verify
- `pop`: Proof-of-possession request (method, path, action, signature, nonce)
- `opts`: Verification options (issuer directory, revocation log, nonce cache, audience)

**Returns:** `VerifyResult` with `accepted: boolean` and `reasonCode: string | null`

**Reason codes:** `missing_field`, `malformed_credential`, `unrecognized_version`, `audience_mismatch`, `expired`, `not_yet_valid`, `unknown_issuer`, `key_not_valid_at_issuance`, `invalid_signature`, `replay_detected`, `revoked`, `proof_of_possession_failed`, `scope_mismatch`, `delegation_not_permitted`

---

### Types

#### `CredentialFields`
```typescript
interface CredentialFields {
  iss?: unknown;
  sub?: unknown;
  agt?: unknown;
  apk?: unknown;
  act?: unknown;
  aud?: unknown;
  iat?: number;
  exp?: number;
  nonce?: string;
  sig?: string;
  ver?: number;
  dlg?: number;
  [k: string]: unknown;
}
```

#### `VerifyOptions`
```typescript
interface VerifyOptions {
  issuerDirectory: KeyDirectory;
  revocationLog: { isRevoked(nonce: string): boolean };
  nonceCache: NonceCacheLike;
  verifierAudience: string;
  nowSeconds?: number;
}
```

#### `VerifyResult`
```typescript
interface VerifyResult {
  accepted: boolean;
  reasonCode: string | null;
}
```

#### `PopRequest`
```typescript
interface PopRequest {
  method: string;
  path: string;
  requestedAction: string;
  signature: string;        // base64url
  requestNonce: string;
}
```

#### `NonceCacheLike`
```typescript
interface NonceCacheLike {
  seenBefore(nonce: string, windowSeconds: number, now?: number): boolean;
}
```

#### `NonceCache`
In-memory nonce cache implementation.

```typescript
class NonceCache implements NonceCacheLike {
  seenBefore(nonce: string, windowSeconds: number, now?: number): boolean;
}
```

#### `RedisNonceCache`
Redis-backed nonce cache for distributed deployments.

```typescript
class RedisNonceCache implements NonceCacheLike {
  constructor(url?: string, keyPrefix?: string);
  async connect(): Promise<void>;
  seenBefore(nonce: string, windowSeconds: number, now?: number): boolean;
}
```

#### `KeyDirectory`
```typescript
interface KeyDirectory {
  lookup(issuerId: string): IssuerKeyEntry | null;
  unreachable?: boolean;
}
```

#### `IssuerKeyEntry`
```typescript
interface IssuerKeyEntry {
  issuerId: string;
  publicKeyPem: string;
  validUntil: number;  // Unix seconds; far-future when healthy
}
```

---

## Cryptographic Utilities

### `popRequestPayload`
Creates the PoP payload for signing.

```typescript
function popRequestPayload(
  method: string,
  path: string,
  act: string,
  nonce: string
): Uint8Array
```

### `b64urlDecode` / `b64urlEncode`
Base64url encoding/decoding utilities.

```typescript
function b64urlDecode(s: string): Uint8Array;
function b64urlEncode(bytes: Uint8Array): string;
```

### `canonicalize`
RFC 8785 (JCS) canonicalization for JSON.

```typescript
function canonicalize(obj: Record<string, unknown>): Uint8Array;
```

### `sha256Hex`
SHA-256 hash as hex string.

```typescript
function sha256Hex(data: Uint8Array): string;
```

### `ed25519Verify`
Ed25519 signature verification.

```typescript
function ed25519Verify(
  publicKey: Uint8Array,
  message: Uint8Array,
  signature: Uint8Array
): boolean;
```

---

## Issuance API

### `issueCredential`
Issues a new signed credential.

```typescript
function issueCredential(o: IssueOptions): IssuedCredential
```

#### `IssueOptions`
```typescript
interface IssueOptions {
  issuerSeedB64url: string;        // base64url Ed25519 seed (32 bytes)
  principal: string;
  agent: string;
  agentPublicKeyB64url: string;    // base64url raw agent public key (apk)
  actionClass: string;
  audience: string;
  ttlSeconds?: number;             // default: 14400 (4h ceiling, per P-06)
  nowSeconds?: number;
  nonceB64url?: string;            // deterministic override for tests
  context?: string;
}
```

#### `IssuedCredential`
```typescript
interface IssuedCredential {
  fields: Record<string, unknown>;  // includes sig (base64url)
}
```

### `issuerIdFromPublicKey`
Derives issuer ID from raw public key.

```typescript
function issuerIdFromPublicKey(pubRaw32: Uint8Array): string;
```

### `importEd25519Seed`
Imports Ed25519 seed as a CryptoKey.

```typescript
function importEd25519Seed(seed32: Uint8Array): nodeCrypto.KeyObject;
```

### `b64urlEncode`
```typescript
function b64urlEncode(bytes: Uint8Array): string;
```

---

## Diagnostics

### `Explanation`
```typescript
type Explanation = {
  code: string;
  summary: string;
  likelyCauses: string[];
  remediation: string[];
  docPointer: string;
};
```

### `EXPLANATIONS`
Map of all reason codes to explanations.

```typescript
const EXPLANATIONS: Record<string, Explanation>;
```

### `explainRejection`
```typescript
function explainRejection(code: string): Explanation;
```
Fails closed (throws) on unknown codes.

### `formatExplanation`
```typescript
function formatExplanation(exp: Explanation): string;
```

---

## Testing Utilities

### `runSmoke`
Runs end-to-end smoke test.

```typescript
function runDoctor(): { ok: boolean; checks: CheckResult[] };
```

### `runDoctor`
Runs health check.

```typescript
function runDoctor(online?: boolean): { ok: boolean; checks: CheckResult[] };
```

---

## Error Handling

All functions follow fail-closed principles:
- Invalid inputs throw or return rejected `VerifyResult`
- Unknown reason codes in `explainRejection` throw
- Network failures in `RedisNonceCache` fail-open to in-memory fallback

---

## Security Notes

- All cryptographic operations use Ed25519 (no algorithm negotiation)
- JCS canonicalization per RFC 8785 (string+integer subset)
- Proof-of-possession uses domain-separated `rilavo_pop_v0`
- Nonce cache uses SHA-256 hashed keys (P-10 discipline)
- Fail-closed on all verification gates
