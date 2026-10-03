const { test } = require('node:test');
const assert = require('node:assert/strict');
const request = require('supertest');
const express = require('express');
const { createRilavoMiddleware } = require('../middleware');
const { issueCredential, b64urlEncode, issuerIdFromPublicKey, popRequestPayload } = require('@rilavo/sdk');
const { generateKeyPairSync, createPrivateKey, createPublicKey, sign, randomBytes } = require('crypto');

// Setup test keys
const { privateKey: issuerPriv, publicKey: issuerPub } = generateKeyPairSync('ed25519');
const issuerPem = issuerPriv.export({ type: 'pkcs8', format: 'pem' });
const issuerSeed = Buffer.from(
  issuerPem.replace(/-----BEGIN PRIVATE KEY-----/g, '')
    .replace(/-----END PRIVATE KEY-----/g, '')
    .replace(/\s+/g, ''), 'base64'
).subarray(16, 48);
const issuerSeedB64url = b64urlEncode(issuerSeed);

const { privateKey: agentPriv, publicKey: agentPub } = generateKeyPairSync('ed25519');
const agentPem = agentPriv.export({ type: 'pkcs8', format: 'pem' });
const agentPubDer = agentPub.export({ type: 'spki', format: 'der' });
const agentPubB64url = b64urlEncode(new Uint8Array(agentPubDer.subarray(12)));

// First issue a dummy credential to get the correct issuer ID
const { fields: dummyCred } = issueCredential({
  issuerSeedB64url,
  principal: 'dummy',
  agent: 'dummy',
  agentPublicKeyB64url: agentPubB64url,
  actionClass: 'data.read',
  audience: 'verifier:test.example.com'
});
const issuerId = dummyCred.iss;
const VERIFIER_AUDIENCE = 'verifier:test.example.com';

// Derive public key PEM from private key
const issuerPubKey = createPublicKey({ key: issuerPem, format: 'pem', type: 'pkcs8' });
const issuerPubPem = issuerPubKey.export({ type: 'spki', format: 'pem' });

const issuerDirectory = {
  unreachable: false,
  lookup: (id) => id === issuerId ? {
    issuerId: issuerId,
    publicKeyPem: issuerPubPem,
    validUntil: Number.MAX_SAFE_INTEGER
  } : null
};

const revocationLog = { isRevoked: () => false };

function createTestApp() {
  const app = express();
  app.use(express.json());
  app.use(createRilavoMiddleware({
    audience: VERIFIER_AUDIENCE,
    issuerDirectory,
    revocationLog,
    publicPaths: ['/health']
  }));
  app.get('/health', (req, res) => res.json({ ok: true }));
  app.get('/protected', (req, res) => res.json({ auth: req.rilavo }));
  return app;
}

test('public path bypasses verification', async () => {
  const app = createTestApp();
  const res = await request(app).get('/health');
  assert.equal(res.status, 200);
  assert.equal(res.body.ok, true);
});

test('missing credential returns 401', async () => {
  const app = createTestApp();
  const res = await request(app).get('/protected');
  assert.equal(res.status, 401);
  assert.equal(res.body.error, 'no_credentials');
});

test('valid credential with PoP is accepted', async () => {
  const app = createTestApp();

  // Issue credential
  const { fields: credential } = issueCredential({
    issuerSeedB64url,
    principal: 'test-principal',
    agent: 'test-agent',
    agentPublicKeyB64url: agentPubB64url,
    actionClass: 'data.read',
    audience: VERIFIER_AUDIENCE
  });

  // Sign PoP
  const requestNonce = randomBytes(16).toString('base64url');
  const popPayload = popRequestPayload('GET', '/protected', 'data.read', requestNonce);
  const popSignature = sign(null, popPayload, createPrivateKey({ key: agentPem, format: 'pem', type: 'pkcs8' }))
    .toString('base64url');

  const res = await request(app)
    .get('/protected')
    .set('x-rilavo-credential', Buffer.from(JSON.stringify(credential)).toString('base64url'))
    .set('x-rilavo-action', 'data.read')
    .set('x-rilavo-pop-signature', popSignature)
    .set('x-rilavo-request-nonce', requestNonce);

  assert.equal(res.status, 200);
  assert.ok(res.body.auth);
  assert.equal(res.body.auth.actionClass, 'data.read');
});

test('wrong audience is rejected', async () => {
  const app = createTestApp();

  const { fields: credential } = issueCredential({
    issuerSeedB64url,
    principal: 'test-principal',
    agent: 'test-agent',
    agentPublicKeyB64url: agentPubB64url,
    actionClass: 'data.read',
    audience: 'verifier:wrong.example.com'
  });

  const requestNonce = randomBytes(16).toString('base64url');
  const popPayload = popRequestPayload('GET', '/protected', 'data.read', requestNonce);
  const popSignature = sign(null, popPayload, createPrivateKey({ key: agentPem, format: 'pem', type: 'pkcs8' }))
    .toString('base64url');

  const res = await request(app)
    .get('/protected')
    .set('x-rilavo-credential', Buffer.from(JSON.stringify(credential)).toString('base64url'))
    .set('x-rilavo-action', 'data.read')
    .set('x-rilavo-pop-signature', popSignature)
    .set('x-rilavo-request-nonce', requestNonce);

  assert.equal(res.status, 401);
  assert.equal(res.body.error, 'audience_mismatch');
});

test('scope mismatch is rejected', async () => {
  const app = createTestApp();

  const { fields: credential } = issueCredential({
    issuerSeedB64url,
    principal: 'test-principal',
    agent: 'test-agent',
    agentPublicKeyB64url: agentPubB64url,
    actionClass: 'data.read',
    audience: VERIFIER_AUDIENCE
  });

  const requestNonce = randomBytes(16).toString('base64url');
  const popPayload = popRequestPayload('POST', '/protected', 'admin.write', requestNonce);
  const popSignature = sign(null, popPayload, createPrivateKey({ key: agentPem, format: 'pem', type: 'pkcs8' }))
    .toString('base64url');

  const res = await request(app)
    .post('/protected')
    .set('x-rilavo-credential', Buffer.from(JSON.stringify(credential)).toString('base64url'))
    .set('x-rilavo-action', 'admin.write')
    .set('x-rilavo-pop-signature', popSignature)
    .set('x-rilavo-request-nonce', requestNonce);

  assert.equal(res.status, 401);
  assert.equal(res.body.error, 'scope_mismatch');
});
