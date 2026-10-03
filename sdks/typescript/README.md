# @rilavo/sdk

Rilavo SDK - verify stateless signed agent authorization credentials.
Byte-compatible with the Python reference implementation
(`rilavo-protocol/src/rilavo/`): same JCS canonicalization, same
proof-of-possession payload derivation, same gate order and reason codes.

## Install

```bash
npm install @rilavo/sdk          # from registry when published
npm install ../rilavo-ts         # local path install (current dev flow)
```

Dual-format package: ESM (`import`) and CJS (`require`) via `exports` map.
Zero runtime dependencies. Node >= 18 recommended (uses node:crypto for
Ed25519 verification).

## Quickstart (rehearsed against the test suite)

```ts
import {
  verifyCredential,
  popRequestPayload,
  b64urlDecode,
  b64urlEncode,
  NonceCache,
} from "@rilavo/sdk";
import { createPublicKey } from "node:crypto";

// One nonce cache per verifier process (your replay defense):
const nonceCache = new NonceCache();

function verifyRequest(headers: Record<string, string>): VerifyResult {
  const credential = JSON.parse(headers["x-rilavo-credential"]);
  const request = {
    method: headers["x-request-method"],
    path: headers["x-request-path"],
    requestedAction: headers["x-requested-action"],
    signature: headers["x-pop-signature"],
    requestNonce: headers["x-request-nonce"],
  };
  return verifyCredential(credential, request, {
    issuerDirectory: {
      lookup: (iss) => cachedDirectory[iss] ?? null,
      unreachable: false,
    },
    revocationLog: { isRevoked: () => false },   // wire your cache refresh
    nonceCache,
    verifierAudience: YOUR_AUDIENCE,
  });
}

function YOUR_AUDIENCE() { return "verifier:yourdomain.example"; }
```

Hold `nonceCache` across requests: replay defense depends on seeing every
nonce your verifier has served.

## Issue (agent/issuer side)

```ts
import { issueCredential } from "@rilavo/sdk";
const issued = issueCredential({
  issuerSeedB64url: YOUR_ISSUER_SEED,       // base64url Ed25519 seed
  principal: "acme-corp:runner-01",
  agent: "agt-01",
  agentPublicKeyB64url: agentPubB64url,
  actionClass: "data.read",
  audience: "verifier:yourdomain.example",
});
```

## License

Apache-2.0
