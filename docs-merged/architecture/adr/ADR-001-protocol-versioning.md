---
title: Protocol Versioning Strategy
status: Accepted
date: 2024-01-15
deciders: [Rilavo Core Team]
consulted: [Security Team, SDK Maintainers]
informed: [All Contributors]
---

# ADR-001: Protocol Versioning Strategy

## Context and Problem Statement

The Rilavo protocol needs a clear versioning strategy that balances stability for production users with the ability to evolve the protocol. The protocol uses a `ver` field in credentials (currently `ver: 1`). We need to define how versions are assigned, when breaking changes are allowed, and how SDKs handle multiple versions.

## Decision Drivers

- Production users need stability and predictable upgrades
- Protocol must evolve to address security issues and new features
- SDKs must maintain backward compatibility where possible
- Clear communication of breaking changes is essential

## Considered Options

### Option 1: Semantic Versioning (SemVer) for Protocol

Protocol versions follow SemVer (MAJOR.MINOR.PATCH). Credentials include `ver` as MAJOR version only.

**Pros:**
- Industry standard, well understood
- Clear signal for breaking changes (MAJOR)
- Allows non-breaking additions (MINOR)

**Cons:**
- Protocol is simple (single `ver` field), SemVer may be overkill
- `ver` field in credential is integer, not full SemVer string

### Option 2: Integer Version with Explicit Gates

Protocol version is a single integer (`ver: 1`, `ver: 2`, etc.). Each version is a complete, immutable specification. SDKs implement version gates that reject unknown versions.

**Pros:**
- Simple, matches current `ver` field design
- Clear failure mode: unknown version = reject (fail-closed)
- Easy to implement in all SDKs

**Cons:**
- No distinction between breaking and non-breaking changes
- All version increments are treated as major

### Option 3: Version with Feature Flags

Protocol version + optional feature flags for backward-compatible extensions.

**Pros:**
- Allows gradual feature rollout
- Maintains single version number

**Cons:**
- Adds complexity to verification logic
- Feature flags can become technical debt

## Decision Outcome

Chosen option: **Option 2: Integer Version with Explicit Gates** because it matches the current credential structure, is simple to implement correctly across all SDKs, and the fail-closed behavior for unknown versions provides strong security guarantees.

### Positive Consequences

- Simple, auditable version checking in all SDKs
- Fail-closed by default for unknown versions
- Easy to audit and test

### Negative Consequences

- Any protocol change requires version increment
- No graceful degradation for unknown versions

## Implementation Plan

1. Document version gate logic in SDK specification
2. Add `unrecognized_version` reason code to all SDKs
3. Create conformance test for version gate
4. Document upgrade process for version increments

## Links

- [Credential Specification](../wave_2/06_CREDENTIAL_SPECIFICATION.md)
- [SDK Specification](../wave_2/20_SDK_SPECIFICATION.md)
- [Security Threat Model](../wave_2/22_SECURITY_THREAT_MODEL.md)
