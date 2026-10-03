---
layout: doc
---

# TypeScript SDK API Reference

## Installation

```bash
npm install @rilavo/sdk
```

## Core Functions

### `verifyCredential(fields, pop, options)`

Verifies a Rilavo credential with proof-of-possession.

**Returns:** `VerifyResult` - `{ accepted: boolean, reasonCode: string | null }`

### `issueCredential(options)`

Issues a new credential (issuer side).

**Returns:** `IssuedCredential` - `{ fields: Record<string, unknown> }`

### `popRequestPayload(method, path, action, nonce)`

Creates the PoP payload for signing.

**Returns:** `Uint8Array` - Canonicalized payload

## Classes

### `NonceCache`

In-memory replay detection cache.

```typescript
const cache = new NonceCache();
cache.seenBefore(nonce, windowSeconds, now?);
```

## Types

See [source](https://github.com/rilavo/rilavo/tree/main/packages/rilavo-ts/src/index.ts) for full type definitions.
