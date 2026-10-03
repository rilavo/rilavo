/**
 * Express.js middleware for Rilavo credential verification
 * 
 * Usage:
 *   const { rilavoMiddleware } = require('@rilavo/sdk/express');
 *   app.use(rilavoMiddleware({ audience: 'your-site.com', issuerDirectory }));
 */

const {
  verifyCredential,
  NonceCache,
  popRequestPayload
} = require('@rilavo/sdk');

/**
 * Creates Rilavo verification middleware for Express
 * @param {Object} config
 * @param {string} config.audience - The audience this verifier expects
 * @param {Object} config.issuerDirectory - Key directory with lookup(issuerId) method
 *   The lookup should return { issuerId, publicKeyPem, validUntil } where publicKeyPem
 *   is an SPKI-format PUBLIC KEY PEM (not private key)
 * @param {Object} [config.revocationLog] - Revocation log with isRevoked(nonce) method
 * @param {string} [config.headerName='x-rilavo-credential'] - Header carrying base64url credential
 * @param {string[]} [config.publicPaths=[]] - Paths exempt from verification
 * @returns {Function} Express middleware
 */
function createRilavoMiddleware(config) {
  const {
    audience,
    issuerDirectory,
    revocationLog = { isRevoked: () => false },
    headerName = 'x-rilavo-credential',
    publicPaths = []
  } = config;

  if (!audience) {
    throw new Error('audience is required');
  }
  if (!issuerDirectory || typeof issuerDirectory.lookup !== 'function') {
    throw new Error('issuerDirectory with lookup function is required');
  }

  // Process-wide replay cache (in production, use Redis or similar)
  const nonceCache = new NonceCache();

  function isPublicPath(pathname) {
    return publicPaths.some(p => {
      if (p.endsWith('*')) {
        const prefix = p.slice(0, -1);
        return pathname.startsWith(prefix);
      }
      return pathname === p || pathname.startsWith(p + '/');
    });
  }

  function decodeCredential(raw) {
    try {
      // base64url decode
      const b64 = raw.replace(/-/g, '+').replace(/_/g, '/');
      const bin = Buffer.from(b64, 'base64');
      return JSON.parse(bin.toString('utf8'));
    } catch {
      return null;
    }
  }

  return async function rilavoMiddleware(req, res, next) {
    // Skip public paths
    if (isPublicPath(req.path)) {
      return next();
    }

    // Get credential from header
    const rawCredential = req.headers[headerName.toLowerCase()];
    if (!rawCredential) {
      return res.status(401).json({ error: 'no_credentials' });
    }

    const credential = decodeCredential(rawCredential);
    if (!credential) {
      return res.status(401).json({ error: 'malformed_credential' });
    }

    // Extract PoP headers
    const method = req.method;
    const path = req.path;
    const action = req.headers['x-rilavo-action'] || 'unspecified.action';
    const signature = req.headers['x-rilavo-pop-signature'] || '';
    const requestNonce = req.headers['x-rilavo-request-nonce'] || '';

    if (!signature || !requestNonce) {
      return res.status(401).json({ error: 'proof_of_possession_failed' });
    }

    // Verify using SDK
    const result = await verifyCredential(
      credential,
      {
        method,
        path,
        requestedAction: action,
        signature,
        requestNonce
      },
      {
        issuerDirectory,
        revocationLog,
        nonceCache,
        verifierAudience: audience
      }
    );

    if (result.accepted) {
      // Attach verification info to request for downstream use
      req.rilavo = {
        principal: credential.sub,
        agent: credential.agt,
        actionClass: credential.act,
        audience: credential.aud
      };
      return next();
    }

    return res.status(401).json({ error: result.reasonCode });
  };
}

module.exports = { createRilavoMiddleware };
