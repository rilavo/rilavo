---
title: Multi-SDK Conformance Testing Framework
status: Accepted
date: 2024-02-01
deciders: [Rilavo Core Team]
consulted: [SDK Maintainers, CI/CD Team]
informed: [All Contributors]
---

# ADR-003: Multi-SDK Conformance Testing Framework

## Context and Problem Statement

Rilavo has 5 SDKs (TypeScript, Go, Python, Next.js, WordPress) that must all implement the same protocol correctly. We need a systematic way to validate that all SDKs conform to the protocol specification and to each other.

## Decision Drivers

- All SDKs must pass the same conformance tests
- Tests must run in CI for every PR
- Fast feedback for contributors
- Extensible for new SDKs
- Clear pass/fail criteria

## Considered Options

### Option 1: Per-SDK Test Suites Only

Each SDK has its own test suite. No cross-SDK validation.

**Pros:**
- Simple, each team owns their tests

**Cons:**
- No guarantee of cross-SDK parity
- Interoperability bugs discovered late

### Option 2: Central Conformance CLI (Chosen)

Single `rilavo-conformance` CLI that runs tests for all SDKs and produces a unified report.

**Pros:**
- Single command validates all SDKs
- Unified JSON report for CI integration
- Extensible for new SDKs
- Can run subset of SDKs for quick feedback
- Machine-readable output for dashboards

**Cons:**
- Requires maintaining the CLI
- Must handle SDK-specific test invocation differences

### Option 3: External Conformance Suite

Separate repository with conformance tests that each SDK implements as a plugin.

**Pros:**
- Clear separation of concerns
- SDK-agnostic test definitions

**Cons:**
- Higher maintenance burden
- Version synchronization complexity
- Overhead for current scope

## Decision Outcome

Chosen option: **Option 2: Central Conformance CLI** because it provides immediate value with manageable maintenance, integrates cleanly with existing CI, and produces actionable reports.

### Positive Consequences

- Single command (`rilavo-conformance`) validates all SDKs
- JSON output enables CI integration and dashboards
- Easy to add new SDKs (implement runner interface)
- Fast feedback: can run subset for quick iteration

### Negative Consequences

- CLI maintenance burden
- Must handle SDK-specific test runners (npm, go, pytest, composer)

## Implementation Plan

1. `scripts/rilavo-conformance` with SDK runner abstraction
2. JSON output with pass/fail, timing, error details
3. CI integration (GitHub Actions)
4. SDK-specific test discovery (golden vector tests, unit tests)
5. Exit code reflects overall pass/fail

## Links

- [scripts/rilavo-conformance](../../scripts/rilavo-conformance)
- [Conformance CLI Design](./ADR-003-conformance-testing.md)
