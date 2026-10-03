---
title: Getting Started with Playground
description: Quick start guide for the Rilavo Playground - issue and verify your first credential in 5 minutes
---

# Getting Started with the Rilavo Playground

The Rilavo Playground lets you experiment with credential issuance and verification **without setting up any infrastructure**. Everything runs in your browser.

## Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)
- No installation required for the hosted playground
- For local development: Node.js 18+ and npm

## Your First Credential (5 minutes)

### 1. Open the Playground

Visit [playground.rilavo.org](https://playground.rilavo.org) or run locally (see [Running Locally](#running-locally)).

You'll see four tabs: **Keys**, **Issue Credential**, **Verify Credential**, **Proof-of-Possession**.

### 2. Generate Keys (Tab 1: Keys)

Click **"Generate Issuer Keypair"**:
- Creates an Ed25519 keypair for the issuer
- Outputs: Issuer ID, Private Key (PEM), Public Key (PEM)
- **Save the private key** - you'll need it to issue credentials

Click **"Generate Agent Keypair"**:
- Creates an Ed25519 keypair for the agent
- Outputs: Agent Public Key (base64url), Private Key (PEM)
- **Copy the Agent Public Key** - you'll paste it in the next step

The **Issuer Directory Entry** is generated automatically - it contains the Issuer ID and Public Key PEM that verifiers will use.

### 3. Issue a Credential (Tab 2: Issue Credential)

Fill in the form:

| Field | Value | Description |
|-------|-------|-------------|
| Principal | `acme-corp` | The subject/organization |
| Agent | `agent-runner-04` | The agent identifier |
| Agent Public Key | *(paste from Step 2)* | Base64url Ed25519 public key |
| Action Class | `data.read` | What the agent is authorized to do |
| Audience | `verifier:api.example.com` | The verifier that will accept this credential |
| Context | `{"dept": "engineering"}` | Optional metadata (JSON) |
| TTL | `3600` | Lifetime in seconds (1 hour) |

Click **"Issue Credential"**.

You'll see the full credential JSON with all fields including the `sig` (issuer signature).

### 4. Verify the Credential (Tab 3: Verify Credential)

Click **"Verify Credential"**.

The playground verifies:
- ✅ Credential not expired
- ✅ Issuer in directory
- ✅ Directory entry valid
- ✅ Issuer signature valid
- ✅ Not revoked (revocation log empty by default)

**Result**: `{ "accepted": true, "reason_code": "accept" }`

### 5. Proof-of-Possession (Tab 4: Proof-of-Possession)

Holding a credential isn't enough - the agent must **sign each request** with their private key.

**Create PoP Request:**
- Method: `POST`
- Path: `/api/data`
- Action: `data.read`
- Audience: `verifier:api.example.com`

Click **"Create PoP Request"**.

You'll see a signed request with a `signature` field.

**Verify PoP Request:**
- Agent Public Key: *(auto-filled from credential)*

Click **"Verify PoP Request"**.

**Result**: `{ "valid": true, "message": "Proof-of-possession verified" }`

## Why Proof-of-Possession?

A credential proves the **issuer** authorized the agent. But anyone who gets the credential could replay it. PoP proves the **agent** actually holds the private key - each request is signed, binding the credential to that specific request.

## Running Locally

```bash
cd docs-site
npm install
npm run dev
```

Open `http://localhost:5173/playground`

## Load Complete Example

Click **"Load Complete Example"** at the bottom of the playground - it generates keys, issues a credential, and populates all tabs with a working example.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Generate keys first" | Complete Tab 1 before Tab 2 |
| "Invalid agent public key" | Ensure you copied the full base64url key from Tab 1 |
| "Verification failed" | Check all fields match; credential may be expired |
| "PoP verification failed" | Ensure agent public key matches the one used to sign |

## Next Steps

- [Interactive Playground Overview](index.md) - Feature reference
- [API Explorer](api-explorer.md) - Complete API reference
- [T1: Verify Your First Credential](../getting-started/T1-verify-your-first-credential.md) - Full tutorial with SDK code
- [Python SDK Quickstart](../api/python/index.md) - Use in your Python app
- [TypeScript SDK Quickstart](../api/typescript/index.md) - Use in your TypeScript app
