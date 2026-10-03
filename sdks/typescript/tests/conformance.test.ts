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
  getGoldenVectors,
  getRejectVectors,
  getGoldenCredentialFields,
  getGoldenIssuerPubB64url,
  getGoldenPopSig,
  getGoldenJcsVectors,
  getGoldenPopVector,
} from "./golden_vectors.js";

const V = getGoldenVectors();
const REJECTS = getRejectVectors();

const CRED_FIELDS: any = V.credential_fields;
const AUD = CRED_FIELDS.aud as string;
// Merge pop_sig with pop to get method, path, act (like golden_vectors.ts does)
const POP_SIG = { ...V.pop_sig, ...V.pop };

const POP = {
  method: POP_SIG.method,
  path: POP_SIG.path,
  requestedAction: POP_SIG.act,
  signature: POP_SIG.sig_b64url,
  requestNonce: POP_SIG.nonce,
};

function directory(overrides: { validUntil?: number; unreachable?: boolean } = {}) {
  return {
    unreachable: overrides.unreachable ?? false,
    lookup(issuerId: string) {
      if (issuerId !== CRED_FIELDS.iss) return null;
      return {
        issuerId,
        publicKeyPem: pemFromRaw(b64urlDecode(V.issuer_pub_b64url)),
        validUntil: overrides.validUntil ?? 9999999999,
      };
    },
  };
}

function revocationLog(revokedNonces = new Set<string>()) {
  return { isRevoked: (nonce: string) => revokedNonces.has(nonce) };
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

function verifyWith(fields: any, pop: any, opts: {
  now?: number;
  cache?: NonceCache;
  dir?: ReturnType<typeof directory>;
  revLog?: ReturnType<typeof revocationLog>;
  verifierAudience?: string;
} = {}) {
  return verifyCredential(fields, {
    method: pop.method,
    path: pop.path,
    requestedAction: pop.requestedAction,
    signature: pop.signature,
    requestNonce: pop.requestNonce,
  }, {
    issuerDirectory: opts.dir ?? directory(),
    revocationLog: opts.revLog ?? revocationLog(),
    nonceCache: opts.cache ?? new NonceCache(),
    verifierAudience: opts.verifierAudience ?? AUD,
    nowSeconds: opts.now ?? (CRED_FIELDS.iat as number + 1),
  });
}

// =============================================================================
// CONFORMANCE TEST SUITE
// Validates SDK implementation against shared golden vectors
// =============================================================================

test("conformance: JCS subset matches Python canonical.py byte-for-byte", () => {
  for (const v of getGoldenJcsVectors()) {
    assert.equal(
      Buffer.from(canonicalize(v.input as Record<string, unknown>)).toString(),
      v.expected,
      `JCS mismatch for input: ${JSON.stringify(v.input)}`
    );
  }
});

test("conformance: PoP payload is byte-identical to Python pop.py", () => {
  const popVec = getGoldenPopVector();
  const payload = popRequestPayload(popVec.method, popVec.path, popVec.act, popVec.nonce);
  assert.equal(Buffer.from(payload).toString("hex"), popVec.payload_hex);
});

test("conformance: accepts the Python-signed credential and PoP signature", () => {
  const r = verifyWith({ ...CRED_FIELDS }, POP);
  assert.equal(r.accepted, true);
  assert.equal(r.reasonCode, null);
});

test("conformance: absent ver implies version 1", () => {
  const fields = { ...CRED_FIELDS };
  delete fields.ver;
  const r = verifyWith(fields, POP);
  assert.equal(r.accepted, true);
});

test("conformance: rejects ver=2 with unrecognized_version (P-26)", () => {
  const r = verifyWith({ ...CRED_FIELDS, ver: 2 }, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "unrecognized_version");
});

test("conformance: rejects non-integer ver with unrecognized_version", () => {
  const r = verifyWith({ ...CRED_FIELDS, ver: "2" }, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "unrecognized_version");
});

test("conformance: audience binding rejects a foreign verifier", () => {
  const r = verifyWith({ ...CRED_FIELDS }, POP, { verifierAudience: "verifier:other.example" });
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "audience_mismatch");
});

test("conformance: expired credential rejected", () => {
  const r = verifyWith({ ...CRED_FIELDS }, POP, { now: (CRED_FIELDS.exp as number) + 1 });
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "expired");
});

test("conformance: not-yet-valid credential rejected", () => {
  const r = verifyWith({ ...CRED_FIELDS }, POP, { now: (CRED_FIELDS.iat as number) - 1 });
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "not_yet_valid");
});

test("conformance: unknown issuer rejected fail-closed", () => {
  const r = verifyWith({ ...CRED_FIELDS }, POP, { dir: { unreachable: false, lookup: () => null } });
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "unknown_issuer");
});

test("conformance: issuer directory unreachable fails closed", () => {
  const r = verifyWith({ ...CRED_FIELDS }, POP, { dir: { unreachable: true, lookup: () => null } });
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "unknown_issuer");
});

test("conformance: key_not_valid_at_issuance enforced on retroactive cutoff", () => {
  const r = verifyWith({ ...CRED_FIELDS }, POP, { dir: directory({ validUntil: (CRED_FIELDS.iat as number) - 1 }) });
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "key_not_valid_at_issuance");
});

test("conformance: tampered field invalidates issuer signature", () => {
  const r = verifyWith({ ...CRED_FIELDS, sub: "attacker" }, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "invalid_signature");
});

test("conformance: replayed nonce rejected on second presentation (shared cache)", () => {
  const cache = new NonceCache();
  const r1 = verifyWith({ ...CRED_FIELDS }, POP, { cache });
  assert.equal(r1.accepted, true);
  const r2 = verifyWith({ ...CRED_FIELDS }, POP, { cache });
  assert.equal(r2.accepted, false);
  assert.equal(r2.reasonCode, "replay_detected");
});

test("conformance: revocation honored when log reports the nonce", () => {
  const r = verifyWith({ ...CRED_FIELDS }, POP, { revLog: revocationLog(new Set([CRED_FIELDS.nonce as string])) });
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "revoked");
});

test("conformance: proof-of-possession binds to method+path+action+nonce", () => {
  const wrongPop = { ...POP, method: "WRONG" };
  const r = verifyWith({ ...CRED_FIELDS }, wrongPop);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "proof_of_possession_failed");
});

test("conformance: proof-of-possession binds to path", () => {
  const wrongPop = { ...POP, path: "/wrong" };
  const r = verifyWith({ ...CRED_FIELDS }, wrongPop);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "proof_of_possession_failed");
});

test("conformance: proof-of-possession binds to action", () => {
  const wrongPop = { ...POP, requestedAction: "wrong.action" };
  const r = verifyWith({ ...CRED_FIELDS }, wrongPop);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "proof_of_possession_failed");
});

test("conformance: proof-of-possession binds to nonce", () => {
  const wrongPop = { ...POP, requestNonce: "wrong-nonce" };
  const r = verifyWith({ ...CRED_FIELDS }, wrongPop);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "proof_of_possession_failed");
});

// ---- reject vectors ---------------------------------------------------------

test("conformance: reject vector unknown_version", () => {
  const reject = REJECTS.unknown_version;
  const fields = { ...CRED_FIELDS, ...reject.credential_fields };
  const r = verifyWith(fields, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "unrecognized_version");
});

test("conformance: reject vector wrong_audience", () => {
  const reject = REJECTS.wrong_audience;
  const fields = { ...CRED_FIELDS, ...reject.credential_fields };
  const r = verifyWith(fields, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "audience_mismatch");
});

test("conformance: reject vector expired", () => {
  const reject = REJECTS.expired;
  const r = verifyWith(reject.credential_fields, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "expired");
});

// ---- delegation (dlg != 0) --------------------------------------------------

test("conformance: delegation not permitted (dlg=1)", () => {
  const r = verifyWith({ ...CRED_FIELDS, dlg: 1 }, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "delegation_not_permitted");
});

test("conformance: delegation not permitted (dlg=2)", () => {
  const r = verifyWith({ ...CRED_FIELDS, dlg: 2 }, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "delegation_not_permitted");
});

// ---- shape validation -------------------------------------------------------

test("conformance: missing required field iss rejected", () => {
  const fields = { ...CRED_FIELDS };
  delete fields.iss;
  const r = verifyWith(fields, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "missing_field");
});

test("conformance: missing required field sub rejected", () => {
  const fields = { ...CRED_FIELDS };
  delete fields.sub;
  const r = verifyWith(fields, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "missing_field");
});

test("conformance: malformed iat (non-integer) rejected", () => {
  const fields = { ...CRED_FIELDS, iat: 1.5 };
  const r = verifyWith(fields, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "malformed_credential");
});

test("conformance: malformed exp (non-integer) rejected", () => {
  const fields = { ...CRED_FIELDS, exp: 1.5 };
  const r = verifyWith(fields, POP);
  assert.equal(r.accepted, false);
  assert.equal(r.reasonCode, "malformed_credential");
});
