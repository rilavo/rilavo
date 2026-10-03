---
title: JCS Canonicalization Implementation
status: Accepted
date: 2024-02-10
deciders: [Rilavo Core Team]
consulted: [Cryptography Experts, SDK Maintainers]
informed: [All Contributors]
---

# ADR-004: JCS Canonicalization Implementation

## Context and Problem Statement

RFC 8785 (JCS - JSON Canonicalization Scheme) is used for deterministic serialization of credentials before signing and verification. All SDKs must produce identical canonical output for the same input to ensure signature compatibility.

## Decision Drivers

- Byte-for-byte identical canonical output across all SDKs
- RFC 8785 compliance
- Performance acceptable for high-throughput verification
- No external dependencies where possible
- Testable against official JCS test vectors

## Considered Options

### Option 1: Custom JCS Implementation per SDK

Each SDK implements JCS from RFC 8785 specification.

**Pros:**
- No external dependencies
- Full control over implementation
- Can optimize for language-specific patterns

**Cons:**
- High risk of subtle differences
- Significant implementation effort
- Must maintain compliance with RFC updates

### Option 2: Shared Reference Implementation (Chosen)

Single reference implementation in Python (`src/rilavo/canonical.py`), other SDKs port the algorithm with byte-parity tests against Python output.

**Pros:**
- Single authoritative implementation
- Python reference is readable and auditable
- Other SDKs validate against Python output (byte-parity)
- Easier to audit single implementation

**Cons:**
- Other SDKs must port algorithm correctly
- Requires byte-parity test infrastructure

### Option 3: External Library (e.g., `jcs` npm, `go-jcs`)

Use existing JCS libraries from package managers.

**Pros:**
- Less implementation work
- Community maintained

**Cons:**
- Adds external dependencies
- Version synchronization across languages
- May not match exact RFC version
- Harder to audit

## Decision Outcome

Chosen option: **Option 2: Shared Reference Implementation** with Python as the authoritative implementation and byte-parity tests in all other SDKs.

### Positive Consequences

- Single authoritative implementation to audit
- Byte-parity tests catch divergence immediately
- Conformance CLI validates parity automatically
- Clear ownership: Python team owns canonicalization

### Negative Consequences

- Other SDKs must port algorithm correctly
- Requires comprehensive byte-parity test suite
- Python implementation becomes critical path

## Implementation Plan

1. Python `canonical.py` as reference (RFC 8785 compliant)
2. TypeScript `jcs.ts` ported with byte-parity tests
3. Go `canonical.go` ported with byte-parity tests
4. Golden vectors include JCS test cases
4. Conformance CLI validates JCS parity

## Links

- [RFC 8785](https://datatracker.ietf.org/doc/rfc8785/)
- [src/rilavo/canonical.py](/rilavo-protocol/src/rilavo/canonical.py)
- [packages/rilavo-ts/src/jcs.ts](/packages/rilavo-ts/src/jcs.ts)
- [packages/rilavo-go/canonical.go](/packages/rilavo-go/canonical.go)
