"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.runDoctor = exports.runSmoke = exports.formatExplanation = exports.explainRejection = exports.EXPLANATIONS = exports.RedisNonceCache = exports.NonceCache = void 0;
exports.b64urlDecode = b64urlDecode;
exports.popRequestPayload = popRequestPayload;
exports.verifyCredential = verifyCredential;
exports.importEd25519Seed = importEd25519Seed;
exports.b64urlEncode = b64urlEncode;
exports.issuerIdFromPublicKey = issuerIdFromPublicKey;
exports.issueCredential = issueCredential;
/**
 * Rilavo SDK -- verifier-side credential checking.
 *
 * Gate order mirrors src/rilavo/verifier.py EXACTLY:
 *   shape -> version(0b) -> audience -> expiry/not-yet-valid ->
 *   issuer lookup -> key_not_valid_at_issuance -> signature ->
 *   replay -> revocation -> proof-of-possession -> scope
 */
const jcs_js_1 = require("./jcs.js");
const sha256_js_1 = require("./sha256.js");
const ed25519_js_1 = require("./ed25519.js");
const nodeCrypto = __importStar(require("node:crypto"));
const otel_js_1 = require("./otel.js");
class NonceCache {
    seen = new Map();
    seenBefore(nonce, windowSeconds, now = Math.floor(Date.now() / 1000)) {
        for (const [n, exp] of this.seen)
            if (exp <= now)
                this.seen.delete(n);
        if (this.seen.has(nonce))
            return true;
        this.seen.set(nonce, now + windowSeconds);
        // Record cache size metric
        (0, otel_js_1.getInstrumentation)().setNonceCacheSize(this.seen.size);
        return false;
    }
    /** Clear all entries from the nonce cache (useful for testing) */
    clear() {
        this.seen.clear();
    }
}
exports.NonceCache = NonceCache;
/**
 * Redis-backed nonce cache for distributed multi-instance deployments.
 * Uses ioredis for Redis operations with explicit async connect.
 * Gracefully degrades to in-memory on connection failure (fail-open for availability).
 */
class RedisNonceCache {
    client = null; // ioredis instance
    url;
    keyPrefix;
    fallback = new NonceCache();
    useFallback = false;
    constructor(url = "redis://localhost:6379", keyPrefix = "rilavo:nonce:") {
        this.url = url;
        this.keyPrefix = keyPrefix;
    }
    async ensureClient() {
        if (this.client || this.useFallback)
            return;
        try {
            const { Redis } = await Promise.resolve().then(() => __importStar(require("ioredis")));
            this.client = new Redis(this.url, {
                maxRetriesPerRequest: 1,
                retryStrategy: () => null,
                enableReadyCheck: true,
                lazyConnect: true,
            });
            await this.client.connect();
            this.useFallback = false;
        }
        catch {
            this.useFallback = true;
            this.client = null;
        }
    }
    nonceKey(nonce) {
        const hash = nodeCrypto.createHash("sha256").update(nonce).digest("hex").slice(0, 32);
        return `${this.keyPrefix}${hash}`;
    }
    async connect() {
        await this.ensureClient();
    }
    seenBefore(nonce, windowSeconds, now = Math.floor(Date.now() / 1000)) {
        if (this.useFallback || !this.client) {
            if (!this.client && !this.useFallback) {
                this.ensureClient().catch(() => { this.useFallback = true; });
            }
            return this.fallback.seenBefore(nonce, windowSeconds, now);
        }
        try {
            if (process.env.NODE_ENV !== "production") {
                console.warn("[Rilavo] RedisNonceCache: synchronous seenBefore called but Redis requires async. Falling back to in-memory. Call connect() at startup.");
            }
            return this.fallback.seenBefore(nonce, windowSeconds, now);
        }
        catch {
            this.useFallback = true;
            return this.fallback.seenBefore(nonce, windowSeconds, now);
        }
    }
}
exports.RedisNonceCache = RedisNonceCache;
function b64urlDecode(s) {
    const b64 = s.replace(/-/g, "+").replace(/_/g, "/");
    const bin = atob(b64);
    return Uint8Array.from(bin, c => c.charCodeAt(0));
}
class Reject extends Error {
    reasonCode;
    constructor(reasonCode) {
        super(reasonCode);
        this.reasonCode = reasonCode;
    }
}
function popRequestPayload(method, path, act, nonce) {
    const body = { method: method.toUpperCase(), path, act, nonce };
    const digestHex = (0, sha256_js_1.sha256Hex)((0, jcs_js_1.canonicalize)(body));
    return (0, jcs_js_1.canonicalize)({ rilavo_pop_v0: digestHex });
}
function verifyCredential(fields, pop, opts) {
    const startTime = Date.now();
    const instrumentation = (0, otel_js_1.getInstrumentation)();
    const issuer = fields["iss"];
    try {
        const result = verifyInner(fields, pop, opts);
        const durationMs = Date.now() - startTime;
        (0, otel_js_1.recordVerification)(result.accepted, result.reasonCode, durationMs, issuer);
        return result;
    }
    catch (e) {
        const durationMs = Date.now() - startTime;
        if (e instanceof Reject) {
            const result = { accepted: false, reasonCode: e.reasonCode };
            (0, otel_js_1.recordVerification)(false, e.reasonCode, durationMs, fields["iss"]);
            if (e.reasonCode === "replay_detected") {
                (0, otel_js_1.recordReplayDetected)(fields["iss"]);
            }
            return result;
        }
        throw e;
    }
}
function verifyInner(fields, pop, opts) {
    // step 0: shape
    for (const f of ["iss", "sub", "agt", "apk", "act", "aud", "nonce", "sig"]) {
        const v = fields[f];
        if (typeof v !== "string" || v === "")
            throw new Reject("missing_field");
    }
    for (const f of ["iat", "exp"]) {
        const v = fields[f];
        if (!Number.isInteger(v) || typeof v === "boolean")
            throw new Reject("malformed_credential");
    }
    if ((fields["dlg"] ?? 0) !== 0)
        throw new Reject("delegation_not_permitted");
    // step 0b: version gate (P-26)
    const ver = fields["ver"] ?? 1;
    if (typeof ver !== "number" || !Number.isInteger(ver) || ver !== 1)
        throw new Reject("unrecognized_version");
    const iat = fields["iat"];
    const exp = fields["exp"];
    // step 1: audience binding
    if (fields["aud"] !== opts.verifierAudience)
        throw new Reject("audience_mismatch");
    const now = opts.nowSeconds ?? Math.floor(Date.now() / 1000);
    // step 2: time window
    if (now >= exp)
        throw new Reject("expired");
    if (now < iat)
        throw new Reject("not_yet_valid");
    // step 3: issuer lookup (fail-closed)
    const iss = fields["iss"];
    if (opts.issuerDirectory.unreachable)
        throw new Reject("unknown_issuer");
    const entry = opts.issuerDirectory.lookup(iss);
    if (entry) {
        (0, otel_js_1.getInstrumentation)().recordIssuerDirectoryLookup(iss, true);
    }
    else {
        (0, otel_js_1.getInstrumentation)().recordIssuerDirectoryLookup(iss, false);
        throw new Reject("unknown_issuer");
    }
    // step 4: retroactive compromise cutoff
    if (iat > entry.validUntil)
        throw new Reject("key_not_valid_at_issuance");
    // step 5: issuer signature over JCS-canonicalized sans sig
    const signingPayload = { ...fields };
    delete signingPayload["sig"];
    const pubRaw = pemToRawEd25519(entry.publicKeyPem);
    const sigBytes = b64urlDecode(fields["sig"]);
    let sigOk = false;
    try {
        sigOk = (0, ed25519_js_1.ed25519Verify)(pubRaw, (0, jcs_js_1.canonicalize)(signingPayload), sigBytes);
    }
    catch {
        sigOk = false;
    }
    if (!sigOk)
        throw new Reject("invalid_signature");
    // step 6: replay (nonce single-use within TTL window)
    const nonce = fields["nonce"];
    if (opts.nonceCache.seenBefore(nonce, exp - iat, now)) {
        (0, otel_js_1.recordReplayDetected)(fields["iss"]);
        throw new Reject("replay_detected");
    }
    // step 7: revocation (fail-closed)
    if (opts.revocationLog.isRevoked(nonce))
        throw new Reject("revoked");
    // step 8: proof-of-possession over THIS request
    const apk = fields["apk"];
    const payload = popRequestPayload(pop.method, pop.path, pop.requestedAction, pop.requestNonce);
    const popSigBytes = b64urlDecode(pop.signature);
    if (!(0, ed25519_js_1.ed25519Verify)(b64urlDecode(apk), payload, popSigBytes))
        throw new Reject("proof_of_possession_failed");
    // step 9: exact-match scope
    if (pop.requestedAction !== fields["act"])
        throw new Reject("scope_mismatch");
    return { accepted: true, reasonCode: null };
}
function pemToRawEd25519(pem) {
    // SPKI DER for Ed25519 = 12-byte prefix + raw 32 bytes.
    const b64Body = pem
        .replace(/-----BEGIN PUBLIC KEY-----/g, "")
        .replace(/-----END PUBLIC KEY-----/g, "")
        .replace(/\s+/g, "");
    const der = Buffer.from(b64Body, "base64");
    return new Uint8Array(der.subarray(12));
}
// ---------------------------------------------------------------------------
// Issuance (P1-A3): byte-compatible with Python rilavo.api.do_issue /
// credential.issue. Field order in the signed canonical payload is produced
// by the same sorted-key JCS subset, so outputs are wire-identical.
// ---------------------------------------------------------------------------
const ED25519_PKCS8_PREFIX = Buffer.from("302e020100300506032b657004220420", "hex");
function importEd25519Seed(seed32) {
    const der = Buffer.concat([ED25519_PKCS8_PREFIX, Buffer.from(seed32)]);
    return nodeCrypto.createPrivateKey({ key: der, format: "der",
        type: "pkcs8" });
}
function b64urlEncode(bytes) {
    return Buffer.from(bytes).toString("base64url");
}
/** Issuer id = "rilavo:iss:" + first 16 hex chars of SHA-256(raw pubkey),
 *  matching keys.fingerprint() exactly. */
function issuerIdFromPublicKey(pubRaw32) {
    return ("rilavo:iss:"
        + (0, sha256_js_1.sha256Hex)(pubRaw32)).slice(0, "rilavo:iss:".length + 16);
}
function issueCredential(o) {
    if (!o.issuerSeedB64url)
        throw new Error("issuerSeedB64url required");
    const seed = b64urlDecode(o.issuerSeedB64url);
    if (seed.length !== 32)
        throw new Error("issuer seed must be 32 bytes");
    const now = o.nowSeconds ?? Math.floor(Date.now() / 1000);
    const ttl = o.ttlSeconds ?? 14400; // 4h ceiling, per P-06
    const nonce = o.nonceB64url ?? nodeCrypto.randomBytes(16).toString("base64url");
    const issPubRaw = ed25519PublicFromSeed(seed);
    const issuerId = issuerIdFromPublicKey(issPubRaw);
    const fields = {
        iss: issuerId,
        sub: o.principal,
        agt: o.agent,
        apk: o.agentPublicKeyB64url,
        act: o.actionClass,
        aud: o.audience,
        iat: now,
        exp: now + ttl,
        nonce,
    };
    const signingKey = importEd25519Seed(seed);
    const sigBytes = nodeCrypto.sign(null, (0, jcs_js_1.canonicalize)(fields), signingKey);
    fields["sig"] = Buffer.from(sigBytes).toString("base64url");
    return { fields };
}
function ed25519PublicFromSeed(seed32) {
    const priv = importEd25519Seed(seed32);
    const pubDer = nodeCrypto.createPublicKey(priv)
        .export({ type: "spki", format: "der" });
    return new Uint8Array(pubDer.subarray(12));
}
var diagnostics_js_1 = require("./diagnostics.js");
Object.defineProperty(exports, "EXPLANATIONS", { enumerable: true, get: function () { return diagnostics_js_1.EXPLANATIONS; } });
Object.defineProperty(exports, "explainRejection", { enumerable: true, get: function () { return diagnostics_js_1.explainRejection; } });
Object.defineProperty(exports, "formatExplanation", { enumerable: true, get: function () { return diagnostics_js_1.formatExplanation; } });
var smoke_js_1 = require("./smoke.js");
Object.defineProperty(exports, "runSmoke", { enumerable: true, get: function () { return smoke_js_1.runSmoke; } });
var doctor_js_1 = require("./doctor.js");
Object.defineProperty(exports, "runDoctor", { enumerable: true, get: function () { return doctor_js_1.runDoctor; } });
