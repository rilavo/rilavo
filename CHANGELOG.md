# Changelog

All notable changes to the Rilavo Protocol reference implementation will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-03

### Added
- Core credential format (P-06): 9 mandatory fields + signature, Ed25519 + JCS canonicalization
- Authorization model (P-07): audience binding, exact-match action classes, proof-of-possession
- Revocation log (P-09): append-only hash-chained, fail-closed, issuer + principal revocation
- Cryptographic primitives (P-11): Ed25519 only, base64url encoding
- Key management (P-12): rotation with overlap window, retroactive compromise cutoff
- Discovery & key directory (P-17): single versioned directory, fail-closed
- Minimal API (P-19): `issue()` and `verify()` operations
- Threat model & conformance tests (P-22): all §7 threats covered
- Self-hosting CLI (P-32): `rilavo keygen`, `rilavo issue`, `rilavo service`
- Offline test kit (P-20): deterministic test issuer, zero-network integration testing
- Audit receipts (P-10): nonce-hash bound, no credential content retained
- Observability: OpenTelemetry tracing, Prometheus metrics
- Framework integrations: FastAPI, Express, Next.js, Go, WordPress scaffolding
- Deployment: self-hosted, embedded, Docker examples
- Cross-language SDKs: Python, TypeScript, Go, Next.js, WordPress

### Security
- Fail-closed defaults for unknown issuers and stale revocation cache
- Replay detection bounded by credential TTL
- No custom cryptographic primitives
- No hardcoded secrets or credentials

### Documentation
- Core Technical Specification (§1-8)
- Mother Blueprint (45 documents, Waves 1-6)
- Tutorials: T1 (verify), T2 (self-host), T3 (mock checkout), T4 (enterprise)
- ADRs for key architectural decisions

## [Unreleased]

### Planned
- Production pilot to freeze credential format (P-06)
- HSM/KMS-backed key custody
- Multi-issuer discovery federation
- Delegation/attenuation (Wave 6, P-34)
- Conformance test suite for independent implementations
