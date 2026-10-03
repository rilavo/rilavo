/**
 * Rilavo Interactive Playground
 * Client-side credential issuance and verification using Web Crypto API
 * No backend required - runs entirely in browser
 */

(function() {
  'use strict';

  // ============================================================================
  // Utility Functions
  // ============================================================================

  function b64urlEncode(bytes) {
    return btoa(String.fromCharCode(...new Uint8Array(bytes)))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
  }

  function b64urlDecode(str) {
    str = str.replace(/-/g, '+').replace(/_/g, '/');
    const pad = str.length % 4;
    if (pad) str += '='.repeat(4 - pad);
    const binary = atob(str);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return bytes;
  }

  function bytesToHex(bytes) {
    return Array.from(new Uint8Array(bytes))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  function hexToBytes(hex) {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < hex.length; i += 2) {
      bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
    }
    return bytes;
  }

  function utf8Encode(str) {
    return new TextEncoder().encode(str);
  }

  function utf8Decode(bytes) {
    return new TextDecoder().decode(bytes);
  }

  async function sha256(data) {
    const hash = await crypto.subtle.digest('SHA-256', data);
    return new Uint8Array(hash);
  }

  async function canonicalize(obj) {
    // RFC 8785 (JCS) canonicalization - simplified for playground
    // In production, use a proper JCS implementation
    const sorted = JSON.stringify(obj, Object.keys(obj).sort());
    return utf8Encode(sorted);
  }

  // ============================================================================
  // Ed25519 Key Operations (using Web Crypto API)
  // ============================================================================

  async function generateEd25519Keypair() {
    const keyPair = await crypto.subtle.generateKey(
      { name: 'Ed25519' },
      true,
      ['sign', 'verify']
    );
    return keyPair;
  }

  async function exportPublicKeyRaw(publicKey) {
    const raw = await crypto.subtle.exportKey('raw', publicKey);
    return new Uint8Array(raw);
  }

  async function exportPrivateKeyPkcs8(privateKey) {
    const pkcs8 = await crypto.subtle.exportKey('pkcs8', privateKey);
    return new Uint8Array(pkcs8);
  }

  async function importPublicKeyRaw(raw) {
    return crypto.subtle.importKey('raw', raw, { name: 'Ed25519' }, true, ['verify']);
  }

  async function importPrivateKeyPkcs8(pkcs8) {
    return crypto.subtle.importKey('pkcs8', pkcs8, { name: 'Ed25519' }, true, ['sign']);
  }

  async function signEd25519(privateKey, data) {
    const signature = await crypto.subtle.sign('Ed25519', privateKey, data);
    return new Uint8Array(signature);
  }

  async function verifyEd25519(publicKey, signature, data) {
    return crypto.subtle.verify('Ed25519', publicKey, signature, data);
  }

  // ============================================================================
  // PEM Encoding/Decoding
  // ============================================================================

  function pemToRaw(pem, type) {
    const lines = pem.trim().split('
');
    const b64 = lines.slice(1, -1).join('');
    return b64urlDecode(b64);
  }

  function rawToPem(raw, type) {
    const b64 = b64urlEncode(raw).match(/.{1,64}/g).join('
');
    return `-----BEGIN ${type}-----
${b64}
-----END ${type}-----`;
  }

  // ============================================================================
  // Rilavo Credential Operations
  // ============================================================================

  async function createIssuerKeyEntry(issuerPrivateKey, validUntil = '9999-12-31T23:59:59Z') {
    const publicKey = await exportPublicKeyRaw(issuerPrivateKey.publicKey);
    const issuerId = b64urlEncode(await sha256(publicKey)).slice(0, 22);
    const publicKeyPem = rawToPem(publicKey, 'PUBLIC KEY');

    return {
      issuer_id: issuerId,
      public_key_pem: publicKeyPem,
      valid_until: validUntil
    };
  }

  async function issueCredential(issuerPrivateKey, request) {
    const { principal, agent, agent_public_key_b64, action_class, audience, context, ttl_seconds = 3600 } = request;

    const now = Math.floor(Date.now() / 1000);
    const expiry = now + ttl_seconds;

    const agentPubKeyBytes = b64urlDecode(agent_public_key_b64);
    const agentPubKey = await importPublicKeyRaw(agentPubKeyBytes);

    const credential = {
      version: '0.1',
      issuer: (await createIssuerKeyEntry(issuerPrivateKey)).issuer_id,
      principal,
      agent,
      agent_public_key_b64,
      action_class,
      audience,
      issued_at: now,
      expires_at: expiry,
      context: context || null
    };

    // Canonicalize and sign
    const canonical = await canonicalize(credential);
    const signature = await signEd25519(issuerPrivateKey, canonical);

    return {
      ...credential,
      signature_b64: b64urlEncode(signature)
    };
  }

  async function verifyCredential(credential, directoryEntry, revocationLog, now = Math.floor(Date.now() / 1000)) {
    const errors = [];

    // 1. Check expiry
    if (credential.expires_at <= now) {
      errors.push('CREDENTIAL_EXPIRED');
    }

    // 2. Check issuer in directory
    if (credential.issuer !== directoryEntry.issuer_id) {
      errors.push('ISSUER_NOT_IN_DIRECTORY');
    }

    // 3. Check directory entry validity
    const dirExpiry = new Date(directoryEntry.valid_until).getTime() / 1000;
    if (dirExpiry <= now) {
      errors.push('DIRECTORY_ENTRY_EXPIRED');
    }

    // 4. Verify signature
    const { signature_b64, ...credWithoutSig } = credential;
    const canonical = await canonicalize(credWithoutSig);
    const signature = b64urlDecode(signature_b64);
    const issuerPubKey = await importPublicKeyRaw(b64urlDecode(
      directoryEntry.public_key_pem.split('
').slice(1, -1).join('')
    ));

    const sigValid = await verifyEd25519(issuerPubKey, signature, canonical);
    if (!sigValid) {
      errors.push('INVALID_SIGNATURE');
    }

    // 5. Check revocation (simplified - check if issuer or principal in revlog)
    const revKey = `${credential.issuer}:${credential.principal}:${credential.agent}`;
    if (revocationLog.includes(revKey)) {
      errors.push('REVOKED');
    }

    return {
      accepted: errors.length === 0,
      errors,
      credential
    };
  }

  // ============================================================================
  // Proof-of-Possession
  // ============================================================================

  async function createPoPRequest(agentPrivateKey, method, path, actionClass, audience) {
    const now = Math.floor(Date.now() / 1000);
    const nonce = b64urlEncode(crypto.getRandomValues(new Uint8Array(16)));

    const request = {
      method,
      path,
      requested_action: actionClass,
      audience,
      request_nonce: nonce,
      timestamp: now
    };

    const canonical = await canonicalize(request);
    const signature = await signEd25519(agentPrivateKey, canonical);

    return {
      ...request,
      signature_b64: b64urlEncode(signature)
    };
  }

  async function verifyPoPRequest(request, agentPublicKeyB64) {
    const { signature_b64, ...reqWithoutSig } = request;
    const canonical = await canonicalize(reqWithoutSig);
    const signature = b64urlDecode(signature_b64);
    const agentPubKey = await importPublicKeyRaw(b64urlDecode(agentPublicKeyB64));
    return verifyEd25519(agentPubKey, signature, canonical);
  }

  // ============================================================================
  // UI Helpers
  // ============================================================================

  function showOutput(element, content, type = 'info') {
    element.textContent = typeof content === 'string' ? content : JSON.stringify(content, null, 2);
    element.className = 'playground-output ' + type;
  }

  function setOutput(element, content, type = 'info') {
    showOutput(element, content, type);
  }

  function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
      // Could show toast notification
    });
  }

  // ============================================================================
  // Playground State
  // ============================================================================

  const state = {
    issuerKeypair: null,
    agentKeypair: null,
    directoryEntry: null,
    credential: null,
    popRequest: null,
    revocationLog: []
  };

  // ============================================================================
  // Tab Handlers
  // ============================================================================

  async function initPlayground() {
    const container = document.getElementById('rilavo-playground');
    if (!container) return;

    // Tab switching
    container.querySelectorAll('.playground-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        container.querySelectorAll('.playground-tab').forEach(t => t.classList.remove('active'));
        container.querySelectorAll('.playground-panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.panel).classList.add('active');
      });
    });

    // ---- TAB 1: Key Generation ----
    const genIssuerBtn = document.getElementById('gen-issuer-btn');
    const genAgentBtn = document.getElementById('gen-agent-btn');
    const issuerOutput = document.getElementById('issuer-output');
    const agentOutput = document.getElementById('agent-output');
    const dirOutput = document.getElementById('directory-output');

    genIssuerBtn?.addEventListener('click', async () => {
      genIssuerBtn.disabled = true;
      genIssuerBtn.textContent = 'Generating...';
      try {
        state.issuerKeypair = await generateEd25519Keypair();
        state.directoryEntry = await createIssuerKeyEntry(state.issuerKeypair);

        const privPem = rawToPem(await exportPrivateKeyPkcs8(state.issuerKeypair.privateKey), 'PRIVATE KEY');
        const pubPem = rawToPem(await exportPublicKeyRaw(state.issuerKeypair.publicKey), 'PUBLIC KEY');

        showOutput(issuerOutput, {
          issuer_id: state.directoryEntry.issuer_id,
          private_key_pem: privPem,
          public_key_pem: pubPem
        }, 'success');

        showOutput(dirOutput, state.directoryEntry, 'success');
      } catch (e) {
        showOutput(issuerOutput, `Error: ${e.message}`, 'error');
      }
      genIssuerBtn.disabled = false;
      genIssuerBtn.textContent = 'Generate Issuer Keypair';
    });

    genAgentBtn?.addEventListener('click', async () => {
      genAgentBtn.disabled = true;
      genAgentBtn.textContent = 'Generating...';
      try {
        state.agentKeypair = await generateEd25519Keypair();
        const privPem = rawToPem(await exportPrivateKeyPkcs8(state.agentKeypair.privateKey), 'PRIVATE KEY');
        const pubRaw = await exportPublicKeyRaw(state.agentKeypair.publicKey);
        const pubB64 = b64urlEncode(pubRaw);

        showOutput(agentOutput, {
          agent_public_key_b64: pubB64,
          private_key_pem: privPem
        }, 'success');
      } catch (e) {
        showOutput(agentOutput, `Error: ${e.message}`, 'error');
      }
      genAgentBtn.disabled = false;
      genAgentBtn.textContent = 'Generate Agent Keypair';
    });

    // ---- TAB 2: Issue Credential ----
    const issueBtn = document.getElementById('issue-btn');
    const credOutput = document.getElementById('credential-output');
    const issueForm = document.getElementById('issue-form');

    issueBtn?.addEventListener('click', async () => {
      if (!state.issuerKeypair || !state.agentKeypair) {
        showOutput(credOutput, 'Error: Generate issuer and agent keypairs first (Tab 1)', 'error');
        return;
      }

      const formData = new FormData(issueForm);
      const request = {
        principal: formData.get('principal') || 'acme-corp',
        agent: formData.get('agent') || 'agent-1',
        agent_public_key_b64: formData.get('agentPubKey') || (await exportPublicKeyRaw(state.agentKeypair.publicKey)).then(b64urlEncode),
        action_class: formData.get('actionClass') || 'data.read',
        audience: formData.get('audience') || 'verifier:api.example.com',
        context: formData.get('context') || null,
        ttl_seconds: parseInt(formData.get('ttl') || '3600', 10)
      };

      issueBtn.disabled = true;
      issueBtn.textContent = 'Issuing...';
      try {
        state.credential = await issueCredential(state.issuerKeypair.privateKey, request);
        showOutput(credOutput, state.credential, 'success');
      } catch (e) {
        showOutput(credOutput, `Error: ${e.message}`, 'error');
      }
      issueBtn.disabled = false;
      issueBtn.textContent = 'Issue Credential';
    });

    // ---- TAB 3: Verify Credential ----
    const verifyBtn = document.getElementById('verify-btn');
    const verifyOutput = document.getElementById('verify-output');
    const verifyForm = document.getElementById('verify-form');

    verifyBtn?.addEventListener('click', async () => {
      if (!state.credential || !state.directoryEntry) {
        showOutput(verifyOutput, 'Error: Issue a credential and generate directory entry first', 'error');
        return;
      }

      const formData = new FormData(verifyForm);
      const revlogText = formData.get('revocationLog') || '';
      const revlog = revlogText.split('
').map(s => s.trim()).filter(Boolean);

      verifyBtn.disabled = true;
      verifyBtn.textContent = 'Verifying...';
      try {
        const result = await verifyCredential(state.credential, state.directoryEntry, revlog);
        showOutput(verifyOutput, result, result.accepted ? 'success' : 'error');
      } catch (e) {
        showOutput(verifyOutput, `Error: ${e.message}`, 'error');
      }
      verifyBtn.disabled = false;
      verifyBtn.textContent = 'Verify Credential';
    });

    // ---- TAB 4: Proof-of-Possession ----
    const popBtn = document.getElementById('pop-btn');
    const popOutput = document.getElementById('pop-output');
    const popVerifyBtn = document.getElementById('pop-verify-btn');
    const popVerifyOutput = document.getElementById('pop-verify-output');
    const popForm = document.getElementById('pop-form');
    const popVerifyForm = document.getElementById('pop-verify-form');

    popBtn?.addEventListener('click', async () => {
      if (!state.agentKeypair || !state.credential) {
        showOutput(popOutput, 'Error: Generate agent keypair and issue credential first', 'error');
        return;
      }

      const formData = new FormData(popForm);
      const request = await createPoPRequest(
        state.agentKeypair.privateKey,
        formData.get('method') || 'GET',
        formData.get('path') || '/data/42',
        formData.get('actionClass') || 'data.read',
        formData.get('audience') || 'verifier:api.example.com'
      );

      state.popRequest = request;
      showOutput(popOutput, request, 'success');
    });

    popVerifyBtn?.addEventListener('click', async () => {
      if (!state.popRequest || !state.credential) {
        showOutput(popVerifyOutput, 'Error: Create a PoP request first', 'error');
        return;
      }

      const formData = new FormData(popVerifyForm);
      const agentPubKeyB64 = formData.get('agentPubKey') || state.credential.agent_public_key_b64;

      popVerifyBtn.disabled = true;
      popVerifyBtn.textContent = 'Verifying...';
      try {
        const valid = await verifyPoPRequest(state.popRequest, agentPubKeyB64);
        showOutput(popVerifyOutput, { 
          valid, 
          message: valid ? 'Proof-of-possession verified' : 'Invalid signature' 
        }, valid ? 'success' : 'error');
      } catch (e) {
        showOutput(popVerifyOutput, `Error: ${e.message}`, 'error');
      }
      popVerifyBtn.disabled = false;
      popVerifyBtn.textContent = 'Verify PoP';
    });

    // ---- Copy Buttons ----
    container.querySelectorAll('.playground-copy').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.dataset.target;
        const target = document.getElementById(targetId);
        if (target) {
          copyToClipboard(target.textContent);
          btn.textContent = 'Copied!';
          setTimeout(() => btn.textContent = 'Copy', 2000);
        }
      });
    });

    // ---- Load Sample Data ----
    const loadSampleBtn = document.getElementById('load-sample-btn');
    loadSampleBtn?.addEventListener('click', async () => {
      loadSampleBtn.disabled = true;
      loadSampleBtn.textContent = 'Loading...';
      try {
        // Generate sample keypairs
        state.issuerKeypair = await generateEd25519Keypair();
        state.agentKeypair = await generateEd25519Keypair();
        state.directoryEntry = await createIssuerKeyEntry(state.issuerKeypair);

        const agentPubRaw = await exportPublicKeyRaw(state.agentKeypair.publicKey);
        const agentPubB64 = b64urlEncode(agentPubRaw);

        state.credential = await issueCredential(state.issuerKeypair.privateKey, {
          principal: 'acme-corp',
          agent: 'agent-runner-04',
          agent_public_key_b64: agentPubB64,
          action_class: 'data.read',
          audience: 'verifier:checkout.example.com',
          ttl_seconds: 3600
        });

        // Update all outputs
        const issuerPrivPem = rawToPem(await exportPrivateKeyPkcs8(state.issuerKeypair.privateKey), 'PRIVATE KEY');
        const issuerPubPem = rawToPem(await exportPublicKeyRaw(state.issuerKeypair.publicKey), 'PUBLIC KEY');
        const agentPrivPem = rawToPem(await exportPrivateKeyPkcs8(state.agentKeypair.privateKey), 'PRIVATE KEY');

        showOutput(issuerOutput, {
          issuer_id: state.directoryEntry.issuer_id,
          private_key_pem: issuerPrivPem,
          public_key_pem: issuerPubPem
        }, 'success');

        showOutput(agentOutput, {
          agent_public_key_b64: agentPubB64,
          private_key_pem: agentPrivPem
        }, 'success');

        showOutput(dirOutput, state.directoryEntry, 'success');
        showOutput(credOutput, state.credential, 'success');

        // Switch to verify tab
        container.querySelectorAll('.playground-tab').forEach(t => t.classList.remove('active'));
        container.querySelectorAll('.playground-panel').forEach(p => p.classList.remove('active'));
        container.querySelector('[data-panel="verify-panel"]').classList.add('active');
        document.getElementById('verify-panel').classList.add('active');

      } catch (e) {
        console.error(e);
      }
      loadSampleBtn.disabled = false;
      loadSampleBtn.textContent = 'Load Complete Example';
    });
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPlayground);
  } else {
    initPlayground();
  }

  // Export for module usage
  window.RilavoPlayground = {
    generateEd25519Keypair,
    exportPublicKeyRaw,
    exportPrivateKeyPkcs8,
    importPublicKeyRaw,
    importPrivateKeyPkcs8,
    signEd25519,
    verifyEd25519,
    b64urlEncode,
    b64urlDecode,
    canonicalize,
    sha256,
    createIssuerKeyEntry,
    issueCredential,
    verifyCredential,
    createPoPRequest,
    verifyPoPRequest
  };
})();
