# Rilavo Protocol

**Stateless, cryptographically signed agent authorization credentials — verify without a network call.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0%2B-blue.svg)](https://www.typescriptlang.org/)
[![Go](https://img.shields.io/badge/go-1.21%2B-blue.svg)](https://golang.org/)
[![Tests](https://img.shields.io/badge/tests-393%20passing-brightgreen.svg)]()

---

## 🎯 What is Rilavo?

**Rilavo** is a protocol that lets any receiving system **verify — instantly, offline, and without learning anything beyond what the credential discloses** — that an AI agent, service, or automated actor holds a specific, time-boxed authorization from a specific principal.

### The Problem

Modern systems face a critical gap: **AI agents and automated services make real requests on behalf of users and organizations, but receiving systems have no portable, standard way to know if an inbound request is authorized.**

- **Block everything** — lose legitimate business and agent-driven automation
- **Accept blindly** — assume liability for unauthorized actions
- **Build custom auth** — fragmented, incompatible, expensive to maintain

**Rilavo solves this** with a cryptographically signed credential format that verifies in microseconds using only the issuer's public key — no token introspection endpoint, no shared secrets, no central authority required at verification time.

### The Solution in One Sentence

> Issue a claim → Sign it with Ed25519 → Let anyone with the issuer's public key verify it offline in <1ms.

---

## 🏗️ Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Principal  │────▶│   Issuer    │────▶│   Agent     │────▶│  Verifier   │
│ (Authorizes)│     │  (Signs)    │     │ (Presents)  │     │  (Verifies) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                    │                    │
                           ▼                    ▼                    ▼
                    ┌─────────────────────────────────────────────────────┐
                    │              Rilavo Credential                      │
                    │  {iss, sub, agt, apk, act, aud, iat, exp, nonce,   │
                    │   dlg:0, ctx?, sig}  —  JCS canonicalized + Ed25519 │
                    └─────────────────────────────────────────────────────┘
```

### Core Properties

| Property | Description |
|----------|-------------|
| **Stateless verification** | No database, no network call — verify with cached public key |
| **Proof-of-Possession** | Agent signs each request with bound private key — stolen credential alone is useless |
| **Audience binding** | Credential cryptographically bound to one verifier — prevents confused-deputy attacks |
| **Short-lived** | Max 4-hour TTL — limits blast radius of compromise |
| **Revocation** | Append-only hash-chained log — fail-closed on unavailability |
| **Delegation-ready** | `dlg` field reserved for Wave 6 (Horizon 2) — v0 requires `dlg=0` or absent |
| **Multi-language** | Reference SDKs: Python, TypeScript, Go, PHP/WordPress |

---

## 📦 SDKs & Integrations

### Official SDKs

| Language | Package | Install | Documentation |
|----------|---------|---------|---------------|
| **Python** | `rilavo` | `pip install rilavo` / `uv add rilavo` | [API Reference](docs/api-reference/api/python/index.md) |
| **TypeScript** | `@rilavo/sdk` | `npm install @rilavo/sdk` | [API Reference](docs/api-reference/api/typescript/index.md) |
| **Go** | `github.com/rilavo/rilavo-go` | `go get github.com/rilavo/rilavo-go` | [API Reference](docs/api-reference/api/go/index.md) |
| **PHP/WordPress** | `rilavo-wp` | Composer / Must-use plugin | [API Reference](docs/api-reference/api/wordpress/index.md) |

### Framework Middleware (Ready to Use)

| Framework | Integration | Quick Start |
|-----------|-------------|-------------|
| **FastAPI** | `from rilavo.fastapi import rilavo_verify` | `rilavo init --framework fastapi` |
| **Next.js (App Router)** | `import { createMiddleware } from '@rilavo/next'` | `rilavo init --framework nextjs` |
| **Express.js** | `app.use(rilavoMiddleware())` | `rilavo init --framework express` |
| **Go `net/http`** | `middleware.RequireCredential()` | See [Go SDK](packages/rilavo-go/README.md) |
| **WSGI/ASGI (Any Python)** | `from rilavo.middleware import rilavo_middleware` | Built into protocol |
| **WordPress** | Must-use plugin zip | [WordPress SDK](packages/rilavo-wp/README.md) |

### Example Integrations

See [`examples/integrations/`](examples/integrations/) for complete, runnable projects:

- **FastAPI** — `examples/integrations/fastapi/`
- **Express.js** — `examples/integrations/express/`
- **Next.js** — `examples/integrations/nextjs/`
- **Go** — `examples/integrations/go/`
- **MCP Server** — `examples/integrations/mcp_server/` (gate MCP tools with Rilavo)
- **Verifier Middleware** — `examples/integrations/verifier_middleware/` (FastAPI, Express, Go)
- **WordPress** — `examples/integrations/wordpress/`

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- Python 3.10+ and [`uv`](https://github.com/astral-sh/uv) (recommended) or pip
- Node.js 18+ for TypeScript SDK
- Go 1.21+ for Go SDK

### 1. Install & Generate Keys

```bash
# Clone and install
git clone https://github.com/rilavo/rilavo.git
cd rilavo
uv sync

# Generate issuer keypair + directory entry
uv run rilavo keygen --out issuer.pem > directory_entry.json
```

### 2. Generate Agent Keypair

```bash
# Using Python (built into quickstart)
uv run python -c "
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import base64
k = Ed25519PrivateKey.generate()
open('agent.pem','wb').write(k.private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption()))
print(base64.urlsafe_b64encode(
    k.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode().rstrip('='))
" > agent_pub.txt
```

### 3. Issue a Credential

```bash
uv run rilavo issue --key issuer.pem   --principal myorg:worker-1 --agent agt_001   --agent-key $(cat agent_pub.txt)   --action-class data.read --audience verifier:api.example.com   > credential.json
```

### 4. Verify (Offline — No Network Call)

```python
import json
from cryptography.hazmat.primitives import serialization
from rilavo.api import do_verify
from rilavo.credential import Credential
from rilavo.keys import IssuerKeyEntry, KeyDirectory
from rilavo.pop import Request, sign_request
from rilavo.revocation import RevocationLog
from rilavo.verifier import NonceCache

# Load credential
credential = Credential(fields=json.load(open("credential.json")))

# Load issuer directory (cache this in production)
directory = KeyDirectory()
entry = json.load(open("directory_entry.json"))
directory.publish(IssuerKeyEntry(entry["issuer_id"],
                                 entry["public_key_pem"].encode(),
                                 entry["valid_until"]))

# Agent signs the specific request (Proof-of-Possession)
agent_priv = serialization.load_pem_private_key(open("agent.pem","rb").read(), password=None)
sig, nonce = sign_request(agent_priv, "GET", "/data/42", "data.read")
request = Request(method="GET", path="/data/42",
                  requested_action="data.read", signature=sig, request_nonce=nonce)

# Verify — OFFLINE, no network call
result = do_verify("verifier:api.example.com", credential, request,
                   directory, RevocationLog(), nonces=NonceCache())

assert result.accepted  # True if valid
print("✅ Credential accepted:", result.reason_code)
```

> **Key insight:** The verifier needs only the issuer's public key (cached locally). No call to the issuer, no shared database, no token introspection.

---

## 🔐 Credential Format (v1)

```json
{
  "ver": 1,                                    // Protocol version (1 = current)
  "iss": "rilavo:iss:abc123...",              // Issuer fingerprint (Ed25519 pubkey hash)
  "sub": "acme-corp:runner-04",               // Principal (opaque, issuer-assigned)
  "agt": "agt_7d3e1c",                        // Agent instance identifier
  "apk": "base64url-ed25519-pubkey",          // Agent public key (base64url, no padding)
  "act": "data.read",                         // Action class (exact match required)
  "aud": "verifier:checkout.example.com",     // Single audience (confused-deputy defense)
  "iat": 1700000000,                          // Issued at (Unix seconds)
  "exp": 1700003600,                          // Expires at (Unix seconds, max iat+4h)
  "nonce": "base64url-random-128bits",        // Single-use nonce (≥128 bits entropy)
  "dlg": 0,                                   // Delegation depth (0 at v0, Wave 6)
  "ctx": "optional-context",                  // Free-form context (not interpreted)
  "sig": "base64url-ed25519-signature"        // Ed25519 over JCS-canonicalized payload
}
```

### Field Details

| Field | Required | Constraints |
|-------|----------|-------------|
| `ver` | Yes | Integer, must be `1` (v0) |
| `iss` | Yes | Valid issuer fingerprint format |
| `sub` | Yes | Non-empty string, issuer-assigned |
| `agt` | Yes | Non-empty string, identifies agent instance |
| `apk` | Yes | Valid base64url Ed25519 public key (32 bytes raw) |
| `act` | Yes | Non-empty, exact-match action class string |
| `aud` | Yes | Non-empty, verifier identifier (e.g., `verifier:api.example.com`) |
| `iat` | Yes | Unix timestamp, not in future (with leeway) |
| `exp` | Yes | Unix timestamp, `exp > iat`, `exp - iat ≤ 14400` (4h) |
| `nonce` | Yes | Base64url, ≥128 bits entropy, single-use |
| `dlg` | No | Integer, must be `0` or absent at v0 |
| `ctx` | No | Free-form string, not interpreted by protocol |
| `sig` | Yes | Ed25519 signature over all above fields (JCS canonicalized) |

---

## ✅ Verification Algorithm (Core Spec §6)

Implemented literally in [`verifier.py`](src/rilavo/verifier.py) — **10 steps, all fail-closed:**

1. **Audience binding** — `cred.aud == verifier_id` (confused-deputy defense)
2. **Time window** — `now ∈ [iat - leeway, exp + leeway]` (default leeway: 60s)
3. **Issuer lookup** — Fetch issuer key from directory — **fail-closed if unreachable**
4. **Compromise cutoff** — `cred.iat ≤ key.valid_until` (retroactive key compromise)
5. **Signature verification** — Ed25519 over JCS-canonicalized payload (sans `sig`)
6. **Replay detection** — Check nonce cache bounded by credential TTL — **fail-closed**
7. **Revocation check** — Query revocation log — **fail-closed if unreachable/stale**
8. **Proof-of-Possession** — Verify agent signature over `(method, path, action, nonce)`
9. **Scope match** — `requested_action == cred.act` (exact match, no wildcards)
10. **Audit receipt** — Emit receipt (nonce hash + issuer + outcome + timestamp)

---

## 🛡️ Security Model

### Threat Coverage (P-22)

| Threat Category | Mitigation | Verifying Tests |
|----------------|------------|-----------------|
| **Spoofing** (fake credential) | Ed25519 signature + JCS canonicalization | `test_signature_verifies...`, `test_unknown_issuer_rejected` |
| **Spoofing** (stolen credential) | Proof-of-Possession (agent must sign request) | `test_copied_credential_alone_is_inert`, `test_pop_binds_to_method_path_and_action` |
| **Tampering** (any field) | Signature covers all fields | `test_tampering_any_field_invalidates_signature` |
| **Tampering** (revocation log) | Hash-chained append-only log | `test_hash_chain_detects_history_rewrite` |
| **Replay** | Nonce cache bounded by TTL | `test_replayed_nonce_rejected_within_validity_window` |
| **Revocation bypass** | Fail-closed on unreachable/stale log | `test_unreachable_revocation_log_fails_closed`, `test_stale_revocation_cache_fails_closed` |
| **Info disclosure** | Minimum disclosure, audience binding | `test_credentials_for_different_audiences_do_not_share_correlatable_state` |
| **Correlation** | Per-relationship identifier scoping (optional) | `test_mode_on_scopes_identifier_per_relationship` |

### Cryptographic Choices

- **Ed25519** — 256-bit security, deterministic nonces, 64-byte signatures, ~44-char public keys
- **JCS (RFC 8785)** — Deterministic JSON canonicalization for signature verification
- **Base64URL (no padding)** — URL-safe, compact wire format
- **No custom crypto** — Only standard, audited primitives

---

## 🌐 Deployment Options

### 1. Embedded Verifier (Zero Dependencies)

```python
# Just import and use — no service to run
from rilavo.api import do_verify
# ... verify with cached directory and revocation log
```

**Use when:** You control the verifier code, want zero operational overhead.

### 2. Self-Hosted HTTP Service

```bash
# Run the service (includes /issue, /verify, /directory, /healthz, /metrics)
uv run rilavo service --port 8090 --metrics-port 9090   --issuer-key issuer.pem --verifier-id verifier:api.example.com
```

**Endpoints:**
- `POST /issue` — Issue credentials (requires issuer key)
- `POST /verify` — Verify credentials with PoP
- `GET /directory` — Public key directory entry
- `GET /healthz` — Health check
- `GET /metrics` — Prometheus metrics (port 9090)

**Use when:** Multiple verifiers, need centralized issuance, want metrics/observability.

### 3. Docker Deployment

```bash
docker build -t rilavo-service .
docker run -d -p 8090:8090 -p 9090:9090   -v /etc/rilavo:/keys:ro   rilavo-service rilavo service --port 8090 --metrics-port 9090     --issuer-key /keys/issuer.pem --verifier-id verifier:api.example.com
```

See [`deploy/`](deploy/) for:
- **Self-hosted** — `deploy/selfhosted/` (systemd, Docker, key management)
- **Hosted** — `deploy/hosted/` (docker-compose, multi-service)
- **Embedded** — `deploy/embedded/` (library-only integration)

### 4. Kubernetes

See [`docs/deployment/kubernetes.md`](docs/deployment/kubernetes.md) for Helm charts and K8s manifests.

---

## 🧪 Testing & Conformance

### Run All Tests

```bash
# Protocol tests (247 tests)
uv run pytest tests/ -q

# Enterprise tests (146 tests) — in separate repo
cd ../rilavo-enterprise && uv run pytest tests/ -q
```

### Conformance Testing

```bash
# Local self-check (6 checks)
uv run rilavo conformance --target local

# Against running service
uv run rilavo conformance --target http://localhost:8090

# JSON output for CI
uv run rilavo conformance --target local --json
```

**Checks performed:**
- `directory` — Key directory well-formed
- `roundtrip_accept` — Issue → verify accepts
- `wrong_audience` — Audience binding rejects foreign credentials
- `tampered_credential` — Tampered signature rejected
- `scope_mismatch` — Exact-match scope enforced
- `replay` — Replayed credential+nonce rejected

### Cross-SDK Golden Vectors

```bash
# Generate golden vectors for SDK parity
uv run python scripts/generate_golden_vectors.py

# Test against golden corpus
uv run pytest tests/test_golden_corpus.py -v
```

---

## 📚 Documentation

### Tutorials (Hands-On)

| Tutorial | Time | Description |
|----------|------|-------------|
| [T1 — Verify your first credential](docs/tutorials/T1-verify-your-first-credential.md) | ~10 min | Offline verification, no network |
| [T2 — Self-host an issuer](docs/tutorials/T2-self-host-an-issuer.md) | ~10 min | Run your own issuance server |
| [T3 — Mock checkout integration](docs/tutorials/T3-mock-checkout.md) | ~5 min | Add agent auth to an endpoint |
| [T4 — Production deployment & cross-SDK verification](docs/tutorials/T4-production-deployment.md) | ~15 min | Deploy service, test Python/TS/Go |

### Reference

- **[API Reference](docs/api-reference/api/reference.md)** — Complete HTTP API specification
- **[SDK Parity](docs/api-reference/sdks/parity.md)** — Cross-SDK behavior matrix
- **[Security](docs/api-reference/SECURITY.md)** — Security model, threat coverage
- **[Self-Hosting Guide](docs/architecture/32_SELF_HOSTING_GUIDE.md)** — Production deployment
- **[Migrations](docs/api-reference/migrations/)** — Version upgrade guides

### Architecture

- **[Core Specification](docs/architecture/Rilavo_Protocol_Core_Specification.md)** — P-06, P-07, P-09, P-11, P-12, P-22
- **[Project Audit](docs/architecture/Rilavo_Project_Audit_and_Specification.md)** — Decisions, open questions, threat model
- **[Mother Blueprint](docs/architecture/Rilavo_Protocol_Mother_Blueprint.md)** — 45-document decision tree
- **[ADRs](docs/architecture/adr/)** — Architecture Decision Records

---

## 🔧 CLI Reference

```bash
rilavo --help                    # Show all commands
rilavo keygen --out key.pem      # Generate Ed25519 keypair + directory entry
rilavo issue --key key.pem ...   # Issue a credential
rilavo conformance --target local|http://...  # Run conformance checks
rilavo explain <reason-code>     # Human-readable error explanation
rilavo doctor [--online]         # Installation health check
rilavo smoke                     # End-to-end smoke test
rilavo init --framework <fw>     # Scaffold framework integration
rilavo openapi [--server-url]    # Generate OpenAPI 3.1 spec
rilavo service [--port N]        # Run HTTP service
rilavo completion <shell>        # Generate shell completions
```

---

## 📖 Protocol Specification Highlights

### Versioning (P-26)
- Credentials carry `ver` field (v0 = `1`)
- Verifiers reject unrecognized versions — **fail-closed**
- Format freezes after first production partner (P-06)

### Key Management (P-12)
- **Rotation:** 90-day default, overlap window = max credential TTL (4h)
- **Compromise:** Retroactive cutoff via `valid_until` on directory entry
- **Discovery:** `/.well-known/rilavo` directory (P-17), HTTPS enforced

### Revocation (P-09)
- Append-only hash-chained log (SHA-256)
- Revocation by **issuer** or **principal**
- Verifier caches log — **fail-closed if stale (>5min) or unreachable**

### Observability (P-29)
- Prometheus metrics at `/metrics`
- OpenTelemetry tracing (optional)
- Structured JSON logging
- Target: **sub-10ms p99 verify latency**

---

## 🌍 Project Status

### ✅ Decided & Implemented (v0)

- Core credential format (P-06)
- Authorization model with PoP (P-07)
- Revocation log (P-09)
- Audit receipts (P-10)
- Ed25519 + JCS crypto (P-11)
- Key management & rotation (P-12)
- Discovery directory (P-17)
- Minimal API: issue + verify (P-19)
- Offline testing kit (P-20)
- Versioning (P-26)
- Self-hosting CLI (P-32)
- Threat model with test coverage (P-22)
- 393 tests passing (247 protocol + 146 enterprise)

### 🔬 Open / Horizon 2+ (Not in v0)

| Feature | Status | Target |
|---------|--------|--------|
| Delegation & attenuation | Wave 6 (P-08, P-34) | Horizon 2 |
| Human identity (ZK proofs) | Wave 6 (P-35) | Horizon 3 |
| Content provenance | Wave 6 (P-36) | Horizon 3 |
| Attestation framework | Wave 6 (P-37) | Horizon 4 |
| Multi-operator governance | Wave 5 (P-24, P-25) | Post-v0 |
| HSM/KMS key custody | Open | Production hardening |

> **Honest status:** This is a **decided-draft reference implementation**. The credential format freezes only after surviving one production partner's real traffic without breaking changes (P-06). TTL (4h), rotation (90d), revocation refresh (5min) are starting defaults needing pilot data.

---

## 🤝 Contributing

We welcome contributions! Please see:

- [Contributing Guide](CONTRIBUTING.md) — Code style, testing, PR process
- [Code of Conduct](CODE_OF_CONDUCT.md) — Community standards
- [Security Policy](SECURITY.md) — Vulnerability disclosure
- [Development Setup](docs/deployment/docker.md) — Local environment

### Development Workflow

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest tests/ -q

# Run conformance
uv run rilavo conformance --target local

# Generate docs
cd docs-site && npm run build
```

---

## 📄 License

**Apache-2.0** — Permissive licensing was a deliberate correction from earlier copyleft consideration.

> **Why not GPL/AGPL?** Copyleft only triggers on *distribution* — a competitor running a modified fork as SaaS never distributes, so copyleft doesn't apply. The AGPL's network-use clause is legally contested and slow to enforce. The real moat is the **trust graph** (installed verifier base, issuer reputation, fraud intelligence, standards standing) — none of which lives in the codebase. A permissive license maximizes adoption; a restrictive one only adds friction.

See [Protocol Licensing Decision](docs/architecture/39_PROTOCOL_LICENSING.md) for full rationale.

---

## 👨‍💻 Author & Links

**Ericfranzee (Abah Francis)** — Creator & Lead Developer

- **GitHub:** [github.com/ericfranzee](https://github.com/ericfranzee)
- **Website:** [ericfranzee.com](https://ericfranzee.com)
- **Project Site:** [rilavo.com](https://rilavo.com)

---

## 🙏 Acknowledgments

- **OAuth 2.1 / RFC 8707** — Audience binding pattern (confused-deputy defense)
- **Biscuit Tokens** — Offline attenuation inspiration for Horizon 2
- **Ed25519 / RFC 8032** — Modern elliptic curve signatures
- **JCS / RFC 8785** — JSON canonicalization for deterministic signatures
- **OpenTelemetry** — Observability framework

---

## 📊 Quick Links

| Resource | Link |
|----------|------|
| **Protocol Spec** | [Core Specification](docs/architecture/Rilavo_Protocol_Core_Specification.md) |
| **Python SDK** | [src/rilavo/](src/rilavo/) |
| **TypeScript SDK** | [packages/rilavo-next/](packages/rilavo-next/) |
| **Go SDK** | [packages/rilavo-go/](packages/rilavo-go/) |
| **WordPress SDK** | [packages/rilavo-wp/](packages/rilavo-wp/) |
| **Examples** | [examples/integrations/](examples/integrations/) |
| **Deploy Guides** | [deploy/](deploy/) |
| **Security** | [SECURITY.md](SECURITY.md) |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) |

---

*Rilavo — Protocol first, network second, product third. Verify authorization without collecting identity.*