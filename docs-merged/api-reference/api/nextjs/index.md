---
title: Next.js Middleware API Reference
description: Complete API reference for the Rilavo Next.js Middleware
---

# Next.js Middleware API Reference (@rilavo/next)

> **Quick test:** [Interactive Playground](../../playground/index.md) — try credential issuance and verification in your browser.


Complete API reference for the Rilavo Next.js Middleware. Provides drop-in credential verification for Next.js App Router.

## Installation

```bash
npm install @rilavo/next @rilavo/sdk
```

## Core Exports

```typescript
import {
  createMiddleware,
  withRilavo,
  injectVerifyCredential,
  injectNextResponse,
  RilavoNextConfig,
} from '@rilavo/next';
```

---

## `createMiddleware`

Creates a Next.js middleware function that verifies Rilavo credentials.

```typescript
function createMiddleware(config: RilavoNextConfig): (req: NextRequest) => Promise<NextResponse>
```

### `RilavoNextConfig`

```typescript
interface RilavoNextConfig {
  /** The audience this site expects on credentials */
  audience: string;

  /** Header carrying the base64url credential (default: "x-rilavo-credential") */
  headerName?: string;

  /** Paths exempt from verification, e.g. ["/health", "/public/*"] */
  publicPaths?: string[];

  /** Issuer keys this site trusts */
  issuerDirectory?: {
    unreachable?: boolean;
    lookup(issuerId: string): {
      issuerId: string;
      publicKeyPem: string;
      validUntil: number;
    } | null;
  };

  /** Revocation-log cache */
  revocationLog?: { isRevoked(nonce: string): boolean };

  /** Override current time for testing (Unix seconds) */
  nowSeconds?: number;
}
```

### Usage

```typescript
// middleware.ts
import { createMiddleware } from '@rilavo/next';

export default createMiddleware({
  audience: 'myapp.example.com',
  publicPaths: ['/health', '/public/*'],
  issuerDirectory: {
    lookup: async (issuerId) => {
      // Fetch from issuer's /directory endpoint
      const res = await fetch(`https://${issuerId}/.well-known/rilavo`);
      if (!res.ok) return null;
      const data = await res.json();
      return {
        issuerId: data.issuer_id,
        publicKeyPem: data.public_key_pem,
        validUntil: data.valid_until,
      };
    },
  },
  revocationLog: {
    isRevoked: async (nonce) => {
      // Check your revocation store
      return false;
    },
  },
});
```

### `withRilavo` (alias)

```typescript
const { withRilavo } = require('@rilavo/next');
// or
import { withRilavo } from '@rilavo/next';

// Same as createMiddleware
export default withRilavo({ audience: 'myapp.example.com' });
```

---

## Testing Utilities

### `injectVerifyCredential`

Inject a custom verification function for testing.

```typescript
import { injectVerifyCredential } from '@rilavo/next';
import * as sdk from '@rilavo/sdk';

// Inject SDK for testing
injectVerifyCredential(sdk.verifyCredential);
```

### `injectNextResponse`

Inject a NextResponse stub for testing.

```typescript
import { injectNextResponse } from '@rilavo/next';

injectNextResponse({
  next() { return { kind: 'next' }; },
  json(body, init) { return { kind: 'json', body, status: init?.status ?? 200 }; },
});
```

---

## Proof-of-Possession Headers

The middleware expects these headers from the calling agent:

| Header | Description |
|--------|-------------|
| `x-rilavo-credential` | Base64url-encoded credential (configurable via `headerName`) |
| `x-rilavo-method` | HTTP method (e.g., "POST") |
| `x-rilavo-path` | Request path (e.g., "/api/data") |
| `x-rilavo-action` | Action being performed (e.g., "data.read") |
| `x-rilavo-pop-signature` | Ed25519 signature (base64url) |
| `x-rilavo-request-nonce` | Request-specific nonce |

---

## Error Responses

| Status | Error Code | Description |
|--------|------------|-------------|
| 401 | `no_credentials` | Credential header missing |
| 401 | `malformed_credential` | Invalid base64url or JSON |
| 401 | `audience_mismatch` | Credential audience doesn't match verifier |
| 401 | `expired` | Credential has expired |
| 401 | `not_yet_valid` | Credential not yet valid (clock skew) |
| 401 | `unknown_issuer` | Issuer not found or directory unreachable |
| 401 | `key_not_valid_at_issuance` | Issuer key compromised retroactively |
| 401 | `invalid_signature` | Issuer signature invalid |
| 401 | `replay_detected` | Nonce already used |
| 401 | `revoked` | Nonce in revocation log |
| 401 | `proof_of_possession_failed` | PoP signature invalid or mismatch |
| 401 | `unrecognized_version` | Credential version not supported |

---

## Error Handling

The middleware follows fail-closed principles:
- Missing/invalid credentials → 401 with error code
- Issuer directory unreachable → 401 `unknown_issuer`
- Revocation log unavailable → 401 (fail-closed)
- Network failures → 401 (fail-closed)

---

## Testing

```typescript
// tests/middleware.test.ts
import { injectVerifyCredential, injectNextResponse } from '@rilavo/next';
import * as sdk from '@rilavo/sdk';

// Inject SDK for testing
injectVerifyCredential(sdk.verifyCredential);

// Inject NextResponse stub
injectNextResponse({
  next() { return { kind: 'next' }; },
  json(body, init) { return { kind: 'json', body, status: init?.status ?? 200 }; },
});

// Now createMiddleware will use your injected dependencies
```

---

## Integration with @rilavo/sdk

The Next.js middleware uses `@rilavo/sdk` internally for verification. The following types are re-exported from `@rilavo/sdk`:

- `CredentialFields`
- `VerifyResult`
- `VerifyOptions`
- `PopRequest`
- `IssuerKeyEntry`
- `KeyDirectory`
- `NonceCacheLike`
- `NonceCache`
- `RedisNonceCache`

See [TypeScript SDK API Reference](../typescript/) for complete details.
