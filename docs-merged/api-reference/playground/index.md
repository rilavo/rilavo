---
title: Interactive Playground
description: Try Rilavo credentials hands-on with our interactive playground - issue, verify, and test proof-of-possession in the browser
---

# Rilavo Interactive Playground

The Rilavo Playground is an interactive web-based tool for experimenting with Rilavo credentials **without writing code or setting up infrastructure**. It runs entirely in your browser using the Web Crypto API (Ed25519).

## Quick Start

1. **Open the Playground**: Visit [playground.rilavo.org](https://playground.rilavo.org) (or [run locally](#running-locally))
2. **Generate Keys**: Create an issuer keypair and agent keypair (Tab 1)
3. **Issue a Credential**: Fill in the subject, agent, audience, and action class (Tab 2)
4. **Verify the Credential**: Check the credential against the issuer directory with optional revocation log (Tab 3)
5. **Proof-of-Possession**: Create and verify PoP signatures for requests (Tab 4)

<RilavoPlayground />

## Features

### Tab 1: Key Generation
- **Generate Issuer Keypair**: Creates an Ed25519 keypair for the issuer and derives an issuer directory entry (issuer ID + public key PEM)
- **Generate Agent Keypair**: Creates an Ed25519 keypair for the agent; outputs the agent's public key in base64url (required for credential issuance)
- **Directory Entry**: Automatically generated from issuer keypair - contains issuer ID and public key for verification

### Tab 2: Issue Credential
- **Principal (sub)**: The subject/organization identifier (e.g., `acme-corp`)
- **Agent (agt)**: The agent identifier (e.g., `agent-runner-04`)
- **Agent Public Key (apk)**: Base64url-encoded Ed25519 public key (auto-filled from Tab 1)
- **Action Class (act)**: The authorized action (e.g., `data.read`, `data.write`, `admin`, `payment.initiate`)
- **Audience (aud)**: The verifier identifier (e.g., `verifier:api.example.com`)
- **Context (ctx)**: Optional JSON metadata
- **TTL**: Credential lifetime in seconds (default 3600, max 86400)

### Tab 3: Verify Credential
- Verifies the issued credential against the issuer directory entry
- Checks: expiration, issuer directory membership, directory entry validity, issuer signature
- **Revocation Log**: Optional - paste revocation entries (one per line, format: `issuer:principal:agent`)

### Tab 4: Proof-of-Possession (PoP)
- **Create PoP Request**: Signs a request payload (method, path, action, audience, nonce, timestamp) with the agent's private key
- **Verify PoP Request**: Validates the PoP signature against the agent's public key from the credential
- Demonstrates that holding a credential is not enough - each request must be signed by the agent's key

## Integration Examples

### Python SDK
```python
from rilavo import issue_credential, verify_credential, pop_request_payload

# Issue a credential
cred = issue_credential(
    issuer_seed_b64url="...",
    principal="my-org:runner-01",
    agent="agent-01",
    agent_public_key_b64url="...",
    action_class="data.read",
    audience="api.example.com"
)

# Create PoP request
pop = pop_request_payload("POST", "/api/data", "data.read", "nonce-123")
signature = sign_with_agent_key(agent_private_key, pop)
```

### TypeScript SDK
```typescript
import { issueCredential, popRequestPayload } from '@rilavo/sdk';

const cred = await issueCredential({
  issuerSeedB64url: '...',
  principal: 'my-org:runner-01',
  agent: 'agent-01',
  agentPublicKeyB64url: '...',
  actionClass: 'data.read',
  audience: 'api.example.com'
});
```

### Go SDK
```go
import "github.com/rilavo/rilavo-go"

cred, _ := rilavo.IssueCredential(rilavo.IssueOptions{
    IssuerSeedB64url: "...",
    Principal: "my-org:runner-01",
    Agent: "agent-01",
    AgentPublicKeyB64url: "...",
    ActionClass: "data.read",
    Audience: "api.example.com",
})
```

## Running Locally

```bash
cd docs-site
npm install
npm run dev
```

The playground will be available at `http://localhost:5173/playground`

## How It Works

The playground implements the full Rilavo credential lifecycle client-side:

1. **Key Generation**: Ed25519 keypairs via Web Crypto API (`crypto.subtle.generateKey`)
2. **Credential Issuance**: Canonicalizes credential fields (RFC 8785 JCS), signs with issuer private key
3. **Verification**: Validates signature against issuer public key from directory, checks expiry/audience/revocation
4. **Proof-of-Possession**: Agent signs request payload (method + path + action + nonce) with their private key

All cryptographic operations use the browser's native Web Crypto API - no dependencies, no server required.

## API Reference

See [API Explorer](api-explorer.md) for detailed endpoint specifications and error codes.

## Next Steps

- [Getting Started Tutorial](getting-started.md) - Step-by-step walkthrough
- [API Explorer](api-explorer.md) - Complete API reference
- [T1: Verify Your First Credential](../getting-started/T1-verify-your-first-credential.md) - Full tutorial with SDK
- [API Reference](../api/reference.md) - Complete SDK documentation
