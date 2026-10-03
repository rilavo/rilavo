# Embedded — verification-only deployment (P-31, path 1 of 3)

For systems that only ever *check* credentials. No issuer infrastructure is
required: just this SDK, the issuer's public key (fetched once from its key
directory), and a cached revocation log.

This is the lightest possible integration — nothing to deploy, nothing to
operate beyond your own application.

## Run it (start to finish, offline)

From the `rilavo-protocol/` repo root:

```bash
uv sync
uv run python deploy/embedded/verify_app.py
```

Expected output:

```
verifier ready: issuer rilavo:iss:<fingerprint> | audience verifier:test.rilavo.example
verification result: {"accepted": true, "reason_code": "accept"}
```

Exit code `0`.

## What the demo does

1. Seeds a local key directory with ONE issuer's public key — in production
   you fetch this once from that issuer's published `/directory` endpoint and
   refresh on your own interval.
2. Holds a revocation-log cache with a bounded refresh interval.
3. Holds one process-wide nonce cache (your replay defense).
4. Verifies an inbound credential **without any network call** — the entire
   point of the stateless design.

## Choosing this path

Pick embedded if your system only ever receives agent traffic and never
authorizes its own agents. If you also need to ISSUE credentials, see
`../selfhosted/` or `../hosted/`. All three paths are equally legitimate;
this guide never steers you toward one.

## Swapping in a real issuer

Replace `offline_test_kit()` with a `KeyDirectory` seeded from your issuer's
real `/directory` response, and keep everything else identical.
