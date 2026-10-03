# T2 — Self-host an issuer (the P-32 checklist, walked literally)

> **Try it first:** [Interactive Playground](../playground/index.md) — issue and verify credentials in your browser without setting up infrastructure.


**What you'll do:** run your own credential issuance server under your own
key. ~10 minutes.
**What you need:** the `rilavo-protocol/` repo. Nothing else — that is the
checkable test of self-hosting being real.

The P-32 checklist is three things:

1. a keypair generated from a cryptographically secure random source,
2. an `/issue` endpoint,
3. a published key-directory entry any verifier can fetch.

## Step 1 — keypair + directory entry

```bash
cd /home/admin/rilavo/rilavo-protocol
uv sync
uv run rilavo keygen --out my_issuer.pem > my_directory_entry.json
```

`my_issuer.pem` is your private signing key (guard it). `my_directory_entry.json`
is what verifiers fetch — publish it wherever you publish things.

Expected `my_directory_entry.json` shape:

```json
{
  "issuer_id": "rilavo:iss:<16-hex>",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...",
  "valid_until": 253402300800
}
```

## Step 2 — run your issuance server

```bash
uv run python deploy/selfhosted/server.py --key my_issuer.pem --port 8090
```

Expected output:

```
self-hosted issuer live on http://127.0.0.1:8090
directory entry:
{ ...your entry... }
```

## Step 3 — exercise it end to end

In another terminal:

```bash
uv run python deploy/selfhosted/client_drill.py --server http://127.0.0.1:8090
```

Expected output:

```
directory: rilavo:iss:<your-fingerprint> | verifier: verifier:rilavo-self-hosted
issued: rilavo:iss:<your-fingerprint> -> my-org:runner-01 nonce <random>
verify: {"accepted": true, "reason_code": "accept"}
```

Exit code `0`.

## Custody honesty note

This walkthrough stores the private key as a PEM file because it is a
tutorial. Production deployments should use KMS-backed custody — named in
P-12 as an acknowledged gap at v0 scale, not claimed solved anywhere.

**Next:** [T3 — integrate the SDK into a mock checkout](T3-mock-checkout.md)
