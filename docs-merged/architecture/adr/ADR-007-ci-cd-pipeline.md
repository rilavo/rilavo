---
title: CI/CD Pipeline Design
status: Accepted
date: 2024-02-25
deciders: [Rilavo Core Team]
consulted: [DevOps Team, SDK Maintainers]
informed: [All Contributors]
---

# ADR-007: CI/CD Pipeline Design

## Context and Problem Statement

Rilavo is a multi-language monorepo (Python, TypeScript, Go, Next.js, WordPress) requiring a CI/CD pipeline that:
- Tests all SDKs on every PR
- Runs conformance testing across all SDKs
- Builds and deploys documentation
- Publishes packages to registries
- Runs security scans
- Provides fast feedback

## Decision Drivers

- Multi-language monorepo (Python, TypeScript, Go, Next.js, WordPress)
- Fast feedback for contributors (< 10 min for PR checks)
- Conformance testing across all SDKs
- Security scanning (dependencies, containers)
- Documentation build and deploy
- Package publishing to PyPI, npm, pkg.go.dev, Packagist
- Matrix testing (PHP versions for WordPress)

## Considered Options

### Option 1: Single Monolithic Pipeline

One large GitHub Actions workflow that does everything sequentially.

**Pros:**
- Simple to understand
- Single status check

**Cons:**
- Slow (sequential execution)
- Failure in one area blocks everything
- Hard to optimize individual stages
- Difficult to debug

### Option 2: Modular Pipeline with Reusable Workflows (Chosen)

Separate workflows for each concern, composed via reusable workflows and matrix strategies.

**Pros:**
- Parallel execution where possible
- Independent failure domains
- Reusable across repos
- Easy to add/remove stages
- Clear status checks per concern

**Cons:**
- More complex workflow configuration
- Requires understanding of reusable workflows

### Option 3: External CI System (GitLab CI, CircleCI, etc.)

Use external CI system with better monorepo support.

**Pros:**
- Advanced monorepo features (affected project detection)
- Better caching

**Cons:**
- Vendor lock-in
- Additional cost
- Team familiarity with GitHub Actions

## Decision Outcome

Chosen option: **Option 2: Modular Pipeline with Reusable Workflows** on GitHub Actions because it provides the best balance of parallelism, maintainability, and cost (free for public repos).

### Pipeline Structure

```
.github/workflows/
├── ci.yml                 # Main CI (runs on every PR)
├── conformance.yml        # Conformance testing (all SDKs)
├── security.yml           # Security scanning (Trivy, Dependabot)
├── docs.yml               # Documentation build + deploy
├── publish.yml            # Package publishing (on tag)
├── wp-tests.yml           # WordPress PHP matrix tests
└── benchmarks.yml         # Performance benchmarks (scheduled)
```

### Reusable Workflows

- `.github/workflows/reusable-sdk-test.yml` - Test any SDK
- `.github/workflows/reusable-conformance.yml` - Run conformance CLI
- `.github/workflows/reusable-security-scan.yml` - Trivy, Dependabot

### Positive Consequences

- Parallel execution reduces total CI time
- Independent failure domains
- Reusable across future repos
- Clear status checks for branch protection

### Negative Consequences

- More complex workflow files
- Requires careful dependency management between jobs

## Implementation Plan

1. Create reusable workflow templates
2. Implement SDK-specific test jobs with matrix
3. Add conformance CLI as reusable workflow
4. Add security scanning (Trivy, Dependabot)
5. Add documentation build/deploy
6. Add scheduled benchmark runs
7. Add package publishing workflows

## Links

- [.github/workflows/ci.yml](/.github/workflows/ci.yml)
- [.github/workflows/conformance.yml](/.github/workflows/conformance.yml)
- [.github/workflows/wp-tests.yml](/.github/workflows/wp-tests.yml)
