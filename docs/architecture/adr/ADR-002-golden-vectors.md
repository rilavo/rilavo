---
title: Golden Vectors as Source of Truth
status: Accepted
date: 2024-01-20
deciders: [Rilavo Core Team]
consulted: [SDK Maintainers, Security Team]
informed: [All Contributors]
---

# ADR-002: Golden Vectors as Source of Truth

## Context and Problem Statement

Cross-SDK interoperability is critical for Rilavo. Each SDK (TypeScript, Go, Python, Next.js, WordPress) must produce and verify credentials identically. Without a single source of truth, subtle differences in canonicalization, signature generation, or verification logic can cause interoperability failures that are difficult to debug.

## Decision Drivers

- Byte-for-byte parity required across all SDK implementations
- Golden vectors must be language-agnostic
- Easy to add new test cases
- Vectors must cover both accept and reject paths
- Changes to vectors must be intentional and reviewed

## Considered Options

### Option 1: Per-SDK Test Vectors

Each SDK maintains its own test vectors in its native test format.

**Pros:**
- Natural fit for each language's test framework
- No cross-language coordination needed

**Cons:**
- High risk of divergence
- Difficult to verify cross-SDK parity
- Duplication of test case maintenance

### Option 2: Shared JSON Golden Vectors (Chosen)

Single `golden/golden.json` and `golden/rejects.json` files at repository root. All SDKs load these files in their tests.

**Pros:**
- Single source of truth
- Language-agnostic (JSON)
- Easy to review changes in PRs
- Conformance CLI can validate all SDKs against same vectors
- Easy to add new test cases

**Cons:**
- Requires each SDK to implement JSON loading
- Must handle JSON number precision (use strings for large integers)

### Option 3: Protocol Buffers / Binary Format

Use a binary schema (protobuf) for golden vectors.

**Pros:**
- Precise binary representation
- Schema evolution support

**Cons:**
- Adds build complexity (protoc)
- Less human-readable for review
- Overkill for current vector complexity

## Decision Outcome

Chosen option: **Option 2: Shared JSON Golden Vectors** because it provides a single source of truth that is human-readable, language-agnostic, and easily reviewable in pull requests.

### Positive Consequences

- All SDKs test against identical vectors
- Conformance CLI validates parity automatically
- Easy to add new test cases (single PR updates all SDKs)
- Reject vectors document expected failure modes

### Negative Consequences

- JSON number precision requires string encoding for large integers (credential IDs, timestamps)
- Each SDK must implement JSON loading logic

## Implementation Plan

1. Maintain `golden/golden.json` and `golden/rejects.json` at repo root
2. Each SDK implements vector loading (TypeScript: `golden_vectors.ts`, Go: embedded, Python: fixture)
3. Conformance CLI validates all SDKs against vectors
4. CI fails if any SDK deviates from golden vectors

## Links

- [golden/golden.json](/golden/golden.json)
- [golden/rejects.json](/golden/rejects.json)
- [SDK Specification](../wave_2/20_SDK_SPECIFICATION.md)
