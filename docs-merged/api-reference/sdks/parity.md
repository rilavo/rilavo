---
title: SDK Parity Matrix
description: Feature comparison across all Rilavo SDKs
---

# SDK Parity Matrix

This matrix tracks feature parity across all official Rilavo SDKs. The authoritative implementation is Python (`rilavo-protocol`); other SDKs target byte-for-byte compatibility with the golden test vectors.

| Feature | Python | Go | TypeScript | Next.js | WordPress |
|---|---:|---:|---:|---:|---:|
| **Core Credential** |
| Issue credential | ✅ | ✅ | ✅ | — | ✅ |
| Verify credential | ✅ | ✅ | ✅ | ✅ | ✅ |
| RFC 8785 canonicalization | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ed25519 signing | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Authorization** |
| Audience binding | ✅ | ✅ | ✅ | ✅ | ✅ |
| Exact-match action classes | ✅ | ✅ | ✅ | ✅ | ✅ |
| Proof-of-possession | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Revocation** |
| Hash-chained revocation log | ✅ | ✅ | ✅ | ✅ | ✅ |
| Fail-closed verification | ✅ | ✅ | ✅ | ✅ | ✅ |
| Issuer/principal revocation | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Key Management** |
| Key rotation with overlap | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Retroactive compromise cutoff | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Key directory publishing | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **Discovery** |
| Well-known discovery | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| JWKS endpoint | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **Middleware/Framework** |
| FastAPI dependency | ✅ | — | — | — | — |
| Express/Connect middleware | — | — | ✅ | — | — |
| Next.js middleware | — | — | — | ✅ | — |
| WordPress hook integration | — | — | — | — | ✅ |
| **Observability** |
| Structured logging | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Metrics (Prometheus) | ✅ | ⚠️ | ⚠️ | ⚠️ | — |
| Distributed tracing | ✅ | ⚠️ | ⚠️ | ⚠️ | — |
| Audit receipts | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Testing** |
| Golden vector tests | ✅ | ✅ | ✅ | ✅ | ✅ |
| Shared golden vectors | ✅ | ✅ | ✅ | — | — |
| Conformance CLI | ✅ | ✅ | ⚠️ | — | — |
| Property-based tests | ✅ | — | — | — | — |
| **Packaging** |
| PyPI / npm / Go modules | ✅ | ✅ | ✅ | ✅ | WordPress.org |
| Semantic versioning | ✅ | ✅ | ✅ | ✅ | ✅ |
| SBOM generation | ✅ | ✅ | ✅ | ✅ | — |
| Automated release pipeline | ✅ | ✅ | ✅ | ✅ | — |

## Legend

- ✅ **Full support** — Feature complete, tested against golden vectors
- ⚠️ **Partial / Planned** — Core logic works, some APIs missing
- — **Not applicable** — Feature doesn't apply to this SDK's scope

## Golden Test Vectors

All SDKs validate against shared golden fixtures:

- `golden/golden.json` — Valid credentials that MUST verify
- `golden/rejects.json` — Invalid credentials that MUST reject

```bash
# Python
uv run pytest tests/test_golden_corpus.py -v

# Go
go test -v ./... -run TestGolden

# TypeScript
npm test -- --testPathPattern=golden

# Next.js
node --test tests/middleware.test.mjs

# WordPress
php check.php
```

## Cross-SDK Benchmarks

Run with: `python scripts/benchmark_all_sdks.py`

| SDK | Operation | p50 (ms) | p99 (ms) | Throughput (ops/sec) |
|---|---|---:|---:|---:|
| Python | issue | 0.088 | 0.164 | ~10,560 |
| Python | verify | 0.388 | 0.623 | ~2,494 |
| TypeScript | issue | — | — | — |
| TypeScript | verify | — | — | — |
| Go | issue | — | — | — |
| Go | verify | — | — | — |

*Benchmarks run on CI; values updated per release.*

## Tracking Parity

The authoritative parity audit is maintained in [`docs/SDK_PARITY_AUDIT.md`](../SDK_PARITY_AUDIT.md).

Current status (as of v0.1):
- **Python**: 196 pass / 1 skip — authoritative
- **Go**: 10/10 PASS — uses copied `testdata/golden.json`
- **TypeScript**: 36/36 PASS — uses shared `golden/` vectors (18 CJS + 18 ESM)
- **Next.js**: 3/3 PASS — middleware only (expanded test suite in progress)
- **WordPress**: 14/14 PASS — PHP implementation

## Recent Improvements (Cycle 54)

- ✅ TypeScript now uses shared golden vectors (`golden/golden.json`, `golden/rejects.json`)
- ✅ TypeScript golden vector tests added (rejects: unknown_version, wrong_audience, expired)
- ✅ Cross-SDK benchmark suite created (`scripts/benchmark_all_sdks.py`)
- ✅ Publish pre-flight validation script created (`scripts/publish_preflight.py`)
- ✅ Automated release pipeline with multi-job workflow

## Contributing to Parity

When adding features:
1. Implement in Python first (authoritative)
2. Add golden vectors to `golden/golden.json` and `golden/rejects.json`
3. Port to other SDKs
4. Run conformance tests: `rilavo-conformance`
5. Update this matrix

---

*Last updated: Cycle 54 — Auto-generated from SDK_PARITY_AUDIT.md + test results*
