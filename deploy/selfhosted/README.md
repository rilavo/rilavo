# Self-hosted issuance (P-31 path 2 / P-32)

For teams with the security engineering capacity to own key custody, or with
data-residency/independence requirements. Everything runs under your key, on
your infrastructure, with zero dependency on Rilavo Enterprise.

## Run it (start to finish)

From the `rilavo-protocol/` repo root:

```bash
uv sync

# 1. Generate YOUR issuer keypair + its publishable key-directory entry:
uv run rilavo keygen --out deploy/selfhosted/issuer.pem > deploy/selfhosted/directory_entry.json

# 2. Start your issuance server under that key (terminal 1):
uv run python deploy/selfhosted/server.py --key deploy/selfhosted/issuer.pem --port 8090

# 3. In another terminal, run the client drill against your issuer:
uv run python deploy/selfhosted/client_drill.py --server http://127.0.0.1:8090
```

Expected output of step 3:

```
directory: rilavo:iss:<your-fingerprint> | verifier: verifier:rilavo-self-hosted
issued: rilavo:iss:<your-fingerprint> -> my-org:runner-01 nonce <...>
verify: {"accepted": true, "reason_code": "accept"}
```

Exit code `0`.Steps 1–2 are the P-32 checklist made literal: a keypair, an /issue
endpoint, and a publishable key-directory entry — no external dependency.
The expected output of step 2 is a JSON directory entry printed at startup
and a line `self-hosted issuer live on http://127.0.0.1:8090`.

A full issue→verify drill over HTTP (with agent proof-of-possession keys)
ships as an automated test in `tests/test_service.py`, so the path above is
exercised continuously rather than only documented.

## Choosing this path

All three deployment paths are equally legitimate, equally supported choices
— this walkthrough never steers you toward whichever path is commercially
preferable for anyone. Pick self-hosted if you have security engineering
capacity or independence requirements. If you'd rather not own custody and
uptime, see `../hosted/`. If you only ever verify credentials,
`../embedded/` needs no issuer at all. Moving between paths later is
specified at E-08 and applies symmetrically regardless of where you start.

## Custody honesty note (P-12/P-32)

This demo stores the private key as a PEM file. Real deployments should use
KMS-backed custody — named in P-12 as an acknowledged gap at v0 scale, not a
solved problem.
