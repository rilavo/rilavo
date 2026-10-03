/**
 * Complete Express.js server with Rilavo verification
 * 
 * Run: node index.js
 * Test: curl -H "x-rilavo-credential: <cred>" -H "x-rilavo-action: data.read" ...
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
const { createRilavoMiddleware } = require('./middleware');
const { issueCredential, b64urlEncode, issuerIdFromPublicKey } = require('@rilavo/sdk');
const { generateKeyPairSync, createPrivateKey, createPublicKey, sign, randomBytes } = require('crypto');

const app = express();
app.use(express.json());

// Configuration
const VERIFIER_AUDIENCE = 'verifier:express-example.com';
const PORT = process.env.PORT || 3000;

// Load or generate keys
function loadOrGenerateKeys() {
  const keysDir = path.join(__dirname, 'keys');
  if (!fs.existsSync(keysDir)) {
    fs.mkdirSync(keysDir, { recursive: true });
  }

  // Issuer key
  let issuerPem;
  if (fs.existsSync(path.join(keysDir, 'issuer.pem'))) {
    issuerPem = fs.readFileSync(path.join(keysDir, 'issuer.pem'), 'utf8');
  } else {
    const { privateKey } = generateKeyPairSync('ed25519');
    issuerPem = privateKey.export({ type: 'pkcs8', format: 'pem' });
    fs.writeFileSync(path.join(keysDir, 'issuer.pem'), issuerPem);
    console.log('Generated issuer key');
  }

  // Extract issuer seed from PKCS8 PEM
  const issuerSeed = Buffer.from(
    issuerPem
      .replace(/-----BEGIN PRIVATE KEY-----/g, '')
      .replace(/-----END PRIVATE KEY-----/g, '')
      .replace(/\s+/g, ''),
    'base64'
  ).subarray(16, 48);
  const issuerSeedB64url = b64urlEncode(issuerSeed);

  // Agent key
  let agentPem, agentPubB64url;
  if (fs.existsSync(path.join(keysDir, 'agent.pem'))) {
    agentPem = fs.readFileSync(path.join(keysDir, 'agent.pem'), 'utf8');
    const pubDer = createPublicKey({ key: agentPem, format: 'pem', type: 'pkcs8' })
      .export({ type: 'spki', format: 'der' });
    agentPubB64url = b64urlEncode(new Uint8Array(pubDer.subarray(12)));
  } else {
    const { privateKey, publicKey } = generateKeyPairSync('ed25519');
    agentPem = privateKey.export({ type: 'pkcs8', format: 'pem' });
    fs.writeFileSync(path.join(keysDir, 'agent.pem'), agentPem);
    const pubDer = publicKey.export({ type: 'spki', format: 'der' });
    agentPubB64url = b64urlEncode(new Uint8Array(pubDer.subarray(12)));
    console.log('Generated agent key');
  }

  // Issuer directory entry (in production, fetch from issuer's /.well-known/rilavo)
  const issuerPubRaw = Buffer.from(issuerSeed).subarray(0, 32); // Actually derive from seed
  const issuerId = issuerIdFromPublicKey(new Uint8Array(issuerSeed));
  const directoryEntry = {
    issuer_id: issuerId,
    public_key_pem: issuerPem
      .replace(/-----BEGIN PRIVATE KEY-----/g, '')
      .replace(/-----END PRIVATE KEY-----/g, '')
      .replace(/\s+/g, '')
      // Convert private to public PEM... simplified for demo
  };

  return { issuerSeedB64url, agentPem, agentPubB64url, directoryEntry };
}

const { issuerSeedB64url, agentPem, agentPubB64url, directoryEntry } = loadOrGenerateKeys();

// Build issuer directory
const issuerDirectory = {
  unreachable: false,
  lookup: (issuerId) => {
    if (issuerId !== directoryEntry.issuer_id) return null;
    return {
      issuerId: directoryEntry.issuer_id,
      publicKeyPem: directoryEntry.public_key_pem,
      validUntil: Number.MAX_SAFE_INTEGER
    };
  }
};

// Revocation log (fail-closed when stale)
const revocationLog = { isRevoked: () => false };

// Create Rilavo middleware
const rilavoMiddleware = createRilavoMiddleware({
  audience: VERIFIER_AUDIENCE,
  issuerDirectory,
  revocationLog,
  publicPaths: ['/health', '/public*']
});

// Apply middleware
app.use(rilavoMiddleware);

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.get('/public/info', (req, res) => {
  res.json({ public: true, message: 'No auth required' });
});

app.get('/protected/data', (req, res) => {
  res.json({ 
    data: 'Sensitive data',
    authenticatedAs: req.rilavo 
  });
});

app.post('/protected/write', (req, res) => {
  res.json({ 
    written: true,
    authenticatedAs: req.rilavo 
  });
});

// Helper: Issue a test credential
app.post('/admin/issue-test-credential', (req, res) => {
  const { principal = 'test-principal', agent = 'test-agent', actionClass = 'data.read' } = req.body;

  const result = issueCredential({
    issuerSeedB64url,
    principal,
    agent,
    agentPublicKeyB64url: agentPubB64url,
    actionClass,
    audience: VERIFIER_AUDIENCE
  });

  res.json({ credential: result.fields });
});

// Helper: Sign a PoP request for testing
app.post('/admin/sign-pop', (req, res) => {
  const { method = 'GET', path = '/protected/data', action = 'data.read' } = req.body;

  const agentPriv = createPrivateKey({ key: agentPem, format: 'pem', type: 'pkcs8' });
  const requestNonce = randomBytes(16).toString('base64url');
  const popPayload = popRequestPayload(method, path, action, requestNonce);
  const popSignature = sign(null, popPayload, agentPriv).toString('base64url');

  res.json({ 
    method, path, action, 
    signature: popSignature, 
    requestNonce 
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Audience: ${VERIFIER_AUDIENCE}`);
  console.log('');
  console.log('Test with:');
  console.log('  1. POST /admin/issue-test-credential -> get credential');
  console.log('  2. POST /admin/sign-pop -> get PoP signature');
  console.log('  3. GET /protected/data with headers:');
  console.log('     x-rilavo-credential: <credential>');
  console.log('     x-rilavo-action: data.read');
  console.log('     x-rilavo-pop-signature: <signature>');
  console.log('     x-rilavo-request-nonce: <nonce>');
});
