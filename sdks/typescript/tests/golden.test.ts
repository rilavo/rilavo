import { test } from "node:test";
import assert from "node:assert/strict";
import {
  verifyCredential,
  popRequestPayload,
  b64urlDecode,
  b64urlEncode,
  NonceCache,
} from "../src/index.js";
import { canonicalize } from "../src/jcs.js";
import { sha256Hex } from "../src/sha256.js";
import {
  createPrivateKey,
  createPublicKey,
  sign as nodeSign,
} from "node:crypto";
import {
  getGoldenVectors,
  getRejectVectors,
  getGoldenCredentialFields,
  getGoldenIssuerPubB64url,
  getGoldenAgentPubB64url,
  getGoldenPopSig,
  getGoldenJcsVectors,
  getGoldenPopVector,
} from "./golden_vectors.js";

const V = getGoldenVectors();
const REJECTS = getRejectVectors();

const CRED_FIELDS: any = V.credential_fields;
const AUD = CRED_FIELDS.aud as string;
const POP_SIG = V.pop_sig;

const POP = {
  method: POP_SIG.method,
  path: POP_SIG.path,
  requestedAction: POP_SIG.act,
  signature: POP_SIG.sig_b64url,
  requestNonce: POP_SIG.nonce,
};

function directory() {
  return {
    unreachable: false,
    lookup(issuerId: string) {
      if (issuerId !== CRED_FIELDS.iss) return null;
      return {
        issuerId,
        publicKeyPem: pemFromRaw(b64urlDecode(V.issuer_pub_b64url)),
        validUntil: 9999999999,
      };
    },
  };
}

function pemFromRaw(raw: Uint8Array): string {
  const der = Buffer.concat([
    Buffer.from("302a300506032b6570032100", "hex"),
    Buffer.from(raw),
  ]);
  return (
    "-----BEGIN PUBLIC KEY-----\n" +
    der.toString("base64").replace(/(.{64})/g, "$1\n") +
    "\n-----END PUBLIC KEY-----\n"
  );
}

function verifyWith(fields: any, pop: any,
                    opts?: { now?: number; cache?: NonceCache }) {
  return verifyCredential(fields, {
    method: pop.method, path: pop.path,
    requestedAction: pop.requestedAction,
    signature: pop.signature, requestNonce: pop.requestNonce,
  }, {
    issuerDirectory: directory(),
    revocationLog: { isRevoked: () => false },
    nonceCache: opts?.cache ?? new NonceCache(),
    verifierAudience: AUD,
    nowSeconds: opts?.now ?? (CRED_FIELDS.iat as number + 1),
  });
}

// ---- byte-parity primitives -------------------------------------------------

test("JCS subset matches Python canonical.py byte-for-byte", () => {
  for (const v of getGoldenJcsVectors())
    assert.equal(
      Buffer.from(canonicalize(v.input as Record<string, unknown>)).toString(),
      v.expected);
});

test("PoP payload is byte-identical to Python pop.py", () => {
  const popVec = getGoldenPopVector();
  const payload = popRequestPayload(popVec.method, popVec.path,
                                    popVec.act, popVec.nonce);
  assert.equal(Buffer.from(payload).toString("hex"), popVec.payload_hex);
});

// ---- gate order and outcomes -------------------------------------------------

test("accepts the Python-signed credential and PoP signature", () => {
  const r = verifyWith({ ...CRED_FIELDS }, POP);
  assert.equal(r.accepted, true);
  assert.equal(r.reasonCode, null);
});

test("absent ver implies version 1", () => {
  const fields = { ...CRED_FIELDS };
  delete fields.ver;
  assert.equal(verifyWith(fields, POP).accepted, true);
});

test("rejects ver=2 with unrecognized_version (P-26)", () => {
  const r = verifyWith({ ...CRED_FIELDS, ver: 2 }, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "unrecognized_version");
});

test("rejects non-integer ver with unrecognized_version", () => {
  for (const bad of ["2", 2.5]) {
    const r = verifyWith({ ...CRED_FIELDS, ver: bad }, POP);
    assert.equal(r.reasonCode, "unrecognized_version");
  }
});

test("audience binding rejects a foreign verifier", () => {
  const r = verifyCredential(CRED_FIELDS, POP, {
    issuerDirectory: directory(),
    revocationLog: { isRevoked: () => false },
    nonceCache: new NonceCache(),
    verifierAudience: "verifier:someone-else.example",
    nowSeconds: CRED_FIELDS.iat as number + 1,
  });
  assert.equal(r.reasonCode, "audience_mismatch");
});

test("expired credential rejected", () => {
  const r = verifyWith({ ...CRED_FIELDS }, POP,
                       { now: (CRED_FIELDS.exp as number) + 1 });
  assert.equal(r.reasonCode, "expired");
});

test("not-yet-valid credential rejected", () => {
  const r = verifyWith({ ...CRED_FIELDS }, POP,
                       { now: (CRED_FIELDS.iat as number) - 1 });
  assert.equal(r.reasonCode, "not_yet_valid");
});

test("unknown issuer rejected fail-closed", () => {
  const r = verifyWith({ ...CRED_FIELDS, iss: "rilavo:iss:stranger" }, POP);
  assert.equal(r.reasonCode, "unknown_issuer");
});

test("key_not_valid_at_issuance enforced on retroactive cutoff", () => {
  const dir = directory();
  const entry: any = dir.lookup(CRED_FIELDS.iss as string)!;
  const r = verifyCredential(CRED_FIELDS, POP, {
    issuerDirectory: {
      lookup: () => ({ ...entry, validUntil: (CRED_FIELDS.iat as number) - 1 }),
      unreachable: false,
    },
    revocationLog: { isRevoked: () => false },
    nonceCache: new NonceCache(),
    verifierAudience: AUD,
    nowSeconds: (CRED_FIELDS.iat as number) + 1,
  });
  assert.equal(r.reasonCode, "key_not_valid_at_issuance");
});

test("tampered field invalidates issuer signature", () => {
  const r = verifyWith({ ...CRED_FIELDS, sub: "attacker" }, POP);
  assert.equal(r.reasonCode, "invalid_signature");
});

test("replayed nonce rejected on second presentation (shared cache)", () => {
  const cache = new NonceCache();
  const t0 = (CRED_FIELDS.iat as number) + 1;
  const first = verifyWith({ ...CRED_FIELDS }, POP, { now: t0, cache });
  const second = verifyWith({ ...CRED_FIELDS }, POP, { now: t0 + 1, cache });
  assert.equal(first.reasonCode, null);
  assert.equal(second.reasonCode, "replay_detected");
});

test("revocation honored when log reports the nonce", () => {
  const nonce = CRED_FIELDS.nonce as string;
  const r = verifyCredential(CRED_FIELDS, POP, {
    issuerDirectory: directory(),
    revocationLog: { isRevoked: (n: string) => n === nonce },
    nonceCache: new NonceCache(),
    verifierAudience: AUD,
    nowSeconds: (CRED_FIELDS.iat as number) + 1,
  });
  assert.equal(r.reasonCode, "revoked");
});

test("proof-of-possession binds to method+path+action+nonce", () => {
  const wrongPath: any = { ...POP, path: "/other" };
  const r = verifyWith({ ...CRED_FIELDS }, wrongPath);
  assert.equal(r.reasonCode, "proof_of_possession_failed");
});


// ---------------------------------------------------------------------------
// P1-A3: issuance parity with Python do_issue (golden-vector driven)
// ---------------------------------------------------------------------------

const GOLDEN_ISSUE: any = {
  "agent_pub_b64url": "Kay64UG8yvCyLhqU000LxzYeUm0L_hLIl5S8kyKWbdc",
  "agent_seed_b64url": "ICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj8",
  "fields": {
    "act": "data.read",
    "agt": "agt-ts-parity",
    "apk": "Kay64UG8yvCyLhqU000LxzYeUm0L_hLIl5S8kyKWbdc",
    "aud": "verifier:parity.example",
    "exp": 1760003600,
    "iat": 1760000000,
    "iss": "rilavo:iss:56475aa75463474c",
    "nonce": "FIXEDNONCE123456",
    "sig": "dJiaW9N9zW-OjKtN-xYrDLBieElaFcLRop2dzhRA5K4LCYOtCpLQzQKBbcQjf9LI4ggbAA3REP0c3NZHpCQGDA",
    "sub": "acme-corp:runner-01"
  },
  "issuer_seed_b64url": "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8",
  "now": 1760000000,
  "ttl": 3600
};

import { issueCredential } from "../src/index.js";

function importSeed(b64url: string) {
  const seed = b64urlDecode(b64url);
  const der = Buffer.concat([
    Buffer.from("302e020100300506032b657004220420", "hex"),
    Buffer.from(seed),
  ]);
  return createPrivateKey({ key: der, format: "der", type: "pkcs8" });
}

test("P1-A3: TS issue reproduces the Python golden credential EXACTLY", () => {
  const issued = issueCredential({
    issuerSeedB64url: GOLDEN_ISSUE.issuer_seed_b64url,
    principal: "acme-corp:runner-01",
    agent: "agt-ts-parity",
    agentPublicKeyB64url: GOLDEN_ISSUE.agent_pub_b64url,
    actionClass: "data.read",
    audience: "verifier:parity.example",
    ttlSeconds: GOLDEN_ISSUE.ttl,
    nowSeconds: GOLDEN_ISSUE.now,
    nonceB64url: GOLDEN_ISSUE.fields.nonce,
  });
  assert.deepEqual(issued.fields, GOLDEN_ISSUE.fields);
});

test("P1-A3: canonical payload bytes equal the golden's (sans sig)", () => {
  const issued = issueCredential({
    issuerSeedB64url: GOLDEN_ISSUE.issuer_seed_b64url,
    principal: "acme-corp:runner-01",
    agent: "agt-ts-parity",
    agentPublicKeyB64url: GOLDEN_ISSUE.agent_pub_b64url,
    actionClass: "data.read",
    audience: "verifier:parity.example",
    ttlSeconds: GOLDEN_ISSUE.ttl,
    nowSeconds: GOLDEN_ISSUE.now,
    nonceB64url: GOLDEN_ISSUE.fields.nonce,
  });
  const strip = (f: Record<string, unknown>) => {
    const c = { ...f }; delete c.sig;
    return Buffer.from(canonicalize(c)).toString("hex");
  };
  assert.equal(strip(issued.fields), strip(GOLDEN_ISSUE.fields));
});

function signPop(privKey: any, method: string, path: string,
                 act: string, nonce: string): string {
  const body = { method: method.toUpperCase(), path, act, nonce };
  const digestHex = sha256Hex(canonicalize(body));
  const payload = canonicalize({ rilavo_pop_v0: digestHex });
  return b64urlEncode(nodeSign(null, payload, privKey));
}

test("P1-A3: TS-issued credential round-trips through the TS verifier", () => {
  const agentPriv = importSeed(GOLDEN_ISSUE.agent_seed_b64url);

  const pubDer = createPublicKey(agentPriv)
    .export({ type: "spki", format: "der" });
  const pubRaw = new Uint8Array(pubDer.subarray(12));

  const issued = issueCredential({
    issuerSeedB64url: GOLDEN_ISSUE.issuer_seed_b64url,
    principal: "roundtrip", agent: "agt-rt",
    agentPublicKeyB64url: b64urlEncode(pubRaw),
    actionClass: "data.read",
    audience: "verifier:parity.example",
    ttlSeconds: GOLDEN_ISSUE.ttl,
    nowSeconds: GOLDEN_ISSUE.now,
    nonceB64url: GOLDEN_ISSUE.fields.nonce,
  });

  const popSig = signPop(agentPriv, "POST", "/x", "data.read", "n-rt-1");
  const dir = directory();
  const entry: any = dir.lookup((issued.fields.iss as string))!;
  const parityIssuerPriv = importSeed(GOLDEN_ISSUE.issuer_seed_b64url);
  const parityIssuerPub = new Uint8Array(
    createPublicKey(parityIssuerPriv).export({ type: "spki", format: "der" })
    .subarray(12));
  const pop = { method: "GET", path: "/x", requestedAction: "data.read", signature: popSig, requestNonce: "n-rt-1" };
  const r = verifyCredential(issued.fields, pop, {
    issuerDirectory: {
      lookup: (id: string) => id === (issued.fields.iss as string)
        ? { issuerId: id,
            publicKeyPem: pemFromRaw(parityIssuerPub),
            validUntil: 9999999999 }
        : null,
      unreachable: false,
    },
    revocationLog: { isRevoked: () => false },
    nonceCache: new NonceCache(),
    verifierAudience: "verifier:parity.example",
    nowSeconds: (issued.fields.iat as number) + 1,
  });
  assert.equal(r.accepted, true);
  assert.equal(r.reasonCode, null);
});

// ---------------------------------------------------------------------------
// Reject vector tests (from shared golden/rejects.json)
// ---------------------------------------------------------------------------

test("rejects unknown_version from shared reject vectors", () => {
  const fields = REJECTS.unknown_version.credential_fields;
  const r = verifyCredential(fields, POP, {
    issuerDirectory: directory(),
    revocationLog: { isRevoked: () => false },
    nonceCache: new NonceCache(),
    verifierAudience: AUD,
    nowSeconds: (fields.iat as number) + 1,
  });
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "unrecognized_version");
});

test("rejects wrong_audience from shared reject vectors", () => {
  const fields = REJECTS.wrong_audience.credential_fields;
  const r = verifyCredential(fields, POP, {
    issuerDirectory: directory(),
    revocationLog: { isRevoked: () => false },
    nonceCache: new NonceCache(),
    verifierAudience: AUD,
    nowSeconds: (fields.iat as number) + 1,
  });
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "audience_mismatch");
});

test("rejects expired from shared reject vectors", () => {
  const fields = REJECTS.expired.credential_fields;
  const r = verifyCredential(fields, POP, {
    issuerDirectory: directory(),
    revocationLog: { isRevoked: () => false },
    nonceCache: new NonceCache(),
    verifierAudience: AUD,
    nowSeconds: (fields.exp as number) + 1,
  });
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "expired");
});
