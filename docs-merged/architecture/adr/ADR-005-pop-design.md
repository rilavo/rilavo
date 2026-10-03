---
title: Proof-of-Possession (PoP) Design
status: Accepted
date: 2024-02-15
deciders: [Rilavo Core Team]
consulted: [Cryptography Experts, SDK Maintainers]
informed: [All Contributors]
---

# ADR-005: Proof-of-Possession (PoP) Design

## Context and Problem Statement

Proof-of-Possession (PoP) binds a credential to a specific request, preventing credential replay and ensuring the caller possesses the private key corresponding to the credential's public key. The PoP design must be secure, interoperable, and efficient.

## Decision Drivers

- Cryptographic binding of credential to specific request
- Replay protection (nonce-based)
- Method, path, and action binding
- Ed25519 signatures (consistent with credential signing)
- Replay detection via nonce cache
- Cross-SDK interoperability

## Considered Options

### Option 1: JWT-style PoP (Header + Payload + Signature)

Credential includes PoP key, agent signs JWT-like structure.

**Pros:**
- Familiar JWT-like structure
- Self-contained

**Cons:**
- Adds complexity to credential structure
- Requires key management in credential

### Option 2: Separate PoP Signature Header (Chosen)

Credential contains agent's public key (`apk`). Agent signs request-specific payload with corresponding private key. Signature sent in separate header (`x-rilavo-pop-signature`).

**Pros:**
- Clean separation: credential = authorization, PoP = request binding
- Agent public key in credential enables verification without extra lookup
- Minimal credential structure
- Works with existing Ed25519 keys

**Cons:**
- Requires agent to sign each request
- Must handle nonce generation/storage

### Option 3: TLS Client Certificate Binding

Use mutual TLS with client certificates for PoP.

**Pros:**
- Well-established pattern
- Built-in replay protection

**Cons:**
- Requires TLS termination with cert validation
- Not suitable for all deployment models
- Certificate management overhead

## Decision Outcome

Chosen option: **Option 2: Separate PoP Signature Header** because it provides clean separation of concerns, works with existing Ed25519 infrastructure, and is deployable in any HTTP environment.

### PoP Payload Structure

```json
{
  "rilavo_pop_v0": "<SHA-256 of JCS-canonicalized request>"
}
```

Where request includes:
- `method`: HTTP method (uppercase)
- `path`: Request path
- `act`: Action being performed
- `nonce`: Unique per-request nonce

### Signature Verification

1. Reconstruct PoP payload from request
2. Compute SHA-256 of JCS-canonicalized payload
3. Verify Ed25519 signature using agent's public key from credential (`apk`)
3. Check nonce not seen before (replay detection)

### Positive Consequences

- Minimal credential structure
- Strong cryptographic binding to request
- Replay protection via nonce cache
- Works with any HTTP framework

### Negative Consequences

- Agent must sign each request
- Nonce management required (generation, storage, cache)
- Clock synchronization not required (nonce-based replay)

## Implementation Plan

1. Define PoP payload structure in protocol spec
2. Implement `popRequestPayload` in all SDKs
3. Add PoP verification to all verifiers
4. Add replay detection via nonce cache
5. Golden vectors for PoP payload and signatures

## Links

- [Protocol Specification](../wave_2/06_CREDENTIAL_SPECIFICATION.md)
- [PoP Implementation (Python)](/rilavo-protocol/src/rilavo/pop.py)
- [PoP Implementation (TypeScript)](/packages/rilavo-ts/src/pop.ts)
- [PoP Implementation (Go)](/packages/rilavo-go/pop.go)
