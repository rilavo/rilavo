# Express.js Verifier Middleware Example

Complete Express.js integration using `@rilavo/sdk` for credential verification.

## Quick Start

```bash
cd examples/verifier_middleware/express
npm install
npm start
```

Server runs on `http://localhost:3000`.

## Usage

### 1. Install Dependencies

```bash
npm install @rilavo/sdk express
```

### 2. Create Middleware

```javascript
// middleware/rilavo.js
const { verifyCredential, NonceCache } = require('@rilavo/sdk');

// In-memory nonce cache (use Redis in production)
const nonceCache = new NonceCache();

// Issuer directory - in production, fetch from issuer's /directory endpoint
const issuerDirectory = {
  lookup: async (issuerId) => {
    // Example: fetch from known issuers
    const knownIssuers = {
      'did:example:issuer1': {
        issuerId: 'did:example:issuer1',
        publicKeyPem: `-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA...
-----END PUBLIC KEY-----`,
        validUntil: Math.floor(Date.now() / 1000) + 86400 * 365,
      },
    };
    return knownIssuers[issuerId] || null;
  },
  unreachable: false,
};

// Revocation log - in production, use Redis or database
const revocationLog = {
  isRevoked: async (nonce) => {
    // Check your revocation store
    return false;
  },
};

const AUDIENCE = 'myapp.example.com';

async function rilavoMiddleware(req, res, next) {
  // Skip for public paths
  const publicPaths = ['/health', '/public'];
  if (publicPaths.some(p => req.path.startsWith(p))) {
    return next();
  }

  // Get credential from header
  const credentialB64url = req.headers['x-rilavo-credential'];
  if (!credentialB64url) {
    return res.status(401).json({ error: 'no_credentials' });
  }

  // Decode credential
  let credential;
  try {
    const json = Buffer.from(credentialB64url, 'base64url').toString();
    credential = JSON.parse(json);
  } catch {
    return res.status(401).json({ error: 'malformed_credential' });
  }

  // Get PoP headers
  const pop = {
    method: req.method,
    path: req.path,
    requestedAction: req.headers['x-rilavo-action'] || 'unspecified',
    signature: req.headers['x-rilavo-pop-signature'] || '',
    requestNonce: req.headers['x-rilavo-request-nonce'] || '',
  };

  // Verify credential
  const { verifyCredential } = require('@rilavo/sdk');
  const result = await verifyCredential(credential, pop, {
    issuerDirectory,
    revocationLog,
    nonceCache,
    verifierAudience: AUDIENCE,
  });

  if (!result.accepted) {
    return res.status(401).json({ error: result.reasonCode });
  }

  // Attach credential to request for downstream use
  req.rilavo = { credential };
  next();
}

module.exports = { rilavoMiddleware };
```

### 3. Usage in Routes

```javascript
// app.js
const express = require('express');
const { rilavoMiddleware } = require('./middleware/rilavo');

const app = express();

// Apply middleware to protected routes
app.use('/api', rilavoMiddleware);

// Public routes (no middleware)
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// Protected routes
app.get('/api/data', (req, res) => {
  // req.rilavo.credential contains the verified credential
  res.json({ data: 'sensitive data', user: req.rilavo.credential.fields.sub });
});

app.post('/api/action', (req, res) => {
  // The agent must include PoP headers:
  // x-rilavo-method: POST
  // x-rilavo-path: /api/action
  // x-rilavo-action: data.write
  // x-rilavo-pop-signature: <base64url signature>
  // x-rilavo-request-nonce: <unique nonce>
  res.json({ success: true });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

## Client-Side: Agent Making Requests

```javascript
// Agent code (browser or Node.js)
const { createCredential, signPop } = require('@rilavo/sdk');

async function callProtectedApi(credential, agentPrivateKey) {
  const url = 'https://myapp.example.com/api/data';

  // Create PoP signature
  const popPayload = {
    method: 'GET',
    path: '/api/data',
    act: 'data.read',
    nonce: crypto.randomUUID(),
  };

  const popSignature = await signPop(agentPrivateKey, popPayload);

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'x-rilavo-credential': credential,  // base64url encoded
      'x-rilavo-method': 'GET',
      'x-rilavo-path': '/api/data',
      'x-rilavo-action': 'data.read',
      'x-rilavo-pop-signature': popSignature,
      'x-rilavo-request-nonce': popPayload.nonce,
    },
  });

  return response.json();
}
```

## Production Considerations

1. **Issuer Directory**: Fetch from `https://{issuer}/.well-known/rilavo` and cache
2. **Revocation Log**: Use Redis with TTL matching credential expiry
3. **Nonce Cache**: Use Redis with sliding window expiration
4. **Rate Limiting**: Add rate limiting per credential/agent
5. **Logging**: Log verification results for audit trails
6. **Error Handling**: Distinguish between auth errors and server errors

## Running Tests

```bash
cd examples/verifier_middleware/express
npm test
```
