# T2 — Self-Host an Issuer (10 minutes, fully offline)

> **Want to run your own credential issuer?** This tutorial walks you through generating keys, running an issuer server, and publishing a key directory — all on your machine, no cloud required.

---

## What You'll Build

By the end, you'll have:
- Your own Ed25519 keypair (issuer identity)
- A running `/issue` endpoint that signs credentials
- A published key directory entry verifiers can fetch

---

## Prerequisites

- **Python 3.11+**
- **uv** for package management
- **10 minutes**

---

## The P-32 Checklist: What Makes a Real Issuer

The protocol defines a minimal checklist for a legitimate issuer (P-32):

| Requirement | What It Means |
|-------------|---------------|
| **1. Keypair** | Ed25519 keypair from cryptographically secure random source |
| **2. `/issue` endpoint** | HTTP endpoint that accepts principal/agent info and returns signed credentials |
| **3. Published directory** | A JSON entry any verifier can fetch with the issuer's public key |

---

## Step 1: Generate Your Keypair + Directory Entry

```bash
cd /home/admin/rilavo/rilavo-protocol
uv sync

# Generate keypair + directory entry in one command
uv run rilavo keygen --out my_issuer.pem > my_directory_entry.json

# What you get:
cat my_issuer.pem          # Your private key (KEEP SECRET)
cat my_directory_entry.json # Public directory entry (share with verifiers)
```

**Example output (`my_directory_entry.json`):**
```json
{
  "issuer": "rilavo:iss:a1b2...c3d4",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA...
-----END PUBLIC KEY-----",
  "valid_from": 1755000000,
  "valid_until": null,
  "directory_version": 1
}
```

**What you got:**
- **`my_issuer.pem`** — Your private key. **Never share this.** It's your issuer identity.
- **`my_directory_entry.json`** — Your public directory entry. **Share this with verifiers.** It contains your public key and validity window.

---

## Step 2: Start the Issuer Server

```bash
# Start the issuer on port 8080
uv run rilavo serve   --issuer-key my_issuer.pem   --directory my_directory_entry.json   --port 8080
```

**Output:**
```
Rilavo Issuer starting on http://localhost:8080
Issuer ID: rilavo:iss:a1b2...c3d4
Directory entry: my_directory_entry.json
Ready to issue credentials
```

The server is now running with **your key**. It exposes:
- `POST /issue` — Issue credentials
- `GET /directory` — Public key directory (for verifiers)

---

## Step 3: Issue Your First Credential

In a new terminal:

```bash
# Issue a credential for a test agent
uv run rilavo issue   --issuer-key my_issuer.pem   --principal "my-customer"   --agent "agent-001"   --agent-pubkey agent_pubkey.pem   --action "my.action"   --audience "verifier:my-service.com"   --ttl 3600
```

**Output:**
```json
{
  "iss": "rilavo:iss:a1b2...c3d4",
  "sub": "my-customer",
  "agt": "agent-001",
  "apk": "MCowBQYDK2VwAyEA...",
  "act": "my.action",
  "aud": "verifier:my-service.com",
  "iat": 1755000000,
  "exp": 1755003600,
  "nonce": "kQ2f9xVh7pR1mT8w",
  "dlg": 0,
  "sig": "base64url(...)"
}
```

**What happened:**
1. You specified the principal (`my-customer`), agent (`agent-001`), and what they can do (`my.action`)
2. The issuer signed a credential with **your private key**
3. The credential is valid for 1 hour (3600 seconds) for `verifier:my-service.com`

---

## Step 4: Verify It Works

Use the test kit to verify your credential:

```python
from rilavo.testing import offline_test_kit
from rilavo.pop import Request

# Load your issued credential
with open("issued_credential.json") as f:
    cred = json.load(f)

# Create a mock verifier with YOUR directory entry
from rilavo.keys import InMemoryKeyDirectory

dir_entry = json.load(open("my_directory_entry.json"))
directory = InMemoryKeyDirectory()
directory.add_entry(dir_entry)

# Verify
kit = offline_test_kit(issuer_dir=directory)

request = Request(
    method="POST",
    path="/api/test",
    action="my.action",
    signature=agent_sign_pop(...),  # agent's PoP signature
    request_nonce="req-nonce-123"
)

result = kit.verify(cred, request)
print("Accepted!" if result.accepted else f"Rejected: {result.reason_code}")
```

---

## Step 5: Share Your Directory Entry

Verifiers need your directory entry to verify credentials you issue. Share `my_directory_entry.json` with them (it's public — contains only your public key).

**In production:** Publish it at a well-known URL (e.g., `https://your-domain.com/.well-known/rilavo-directory.json`) and point verifiers there.

---

## What You Just Built

| Component | What It Does |
|-----------|--------------|
| `my_issuer.pem` | Your issuer private key (keep secret!) |
| `my_directory_entry.json` | Public directory entry (share freely) |
| `rilavo serve` | HTTP server that issues credentials |
| `POST /issue` | Endpoint that signs credentials |
| `GET /directory` | Public endpoint for verifiers |

---

## Production Considerations

| Concern | Recommendation |
|---------|----------------|
| **Key storage** | Use HSM or KMS in production; never store raw private keys on disk |
| **Directory publishing** | Publish at well-known URL with HTTPS; rotate keys periodically |
| **Revocation** | Hook up a revocation log (P-09) for production use |
| **Monitoring** | Log all issuance; alert on anomalies |
| **Rate limiting** | Protect `/issue` endpoint from abuse |

---

## What's Next?

| Tutorial | What You'll Learn |
|----------|-------------------|
| **[T3 — Mock Checkout](T3-mock-checkout.md)** | Integrate Rilavo into a realistic checkout flow |
| **[T4 — Product Metering](T4-product-metering.md)** | Track usage, enforce tier limits |
| **[Interactive Playground](../playground/index.md)** | Experiment in the browser |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Permission denied` on `.pem` | `chmod 600 my_issuer.pem` |
| `Address already in use` | Change port with `--port 8081` |
| `Invalid signature` | Ensure agent's `apk` matches credential's `apk` |

---

## Key Takeaways

| Concept | Key Point |
|---------|-----------|
| **You own the keys** | Self-hosting means you generate and control the signing keys |
| **No central authority** | No one but you can issue credentials for your issuers |
| **Fail-closed by default** | If anything is wrong, the verifier rejects — no silent failures |
| **Directory is public** | The directory entry is meant to be shared; it only has your public key |

---

## Next Steps

**[→ T3: Mock Checkout](T3-mock-checkout.md)** — Integrate Rilavo into a realistic checkout flow with a real middleware.