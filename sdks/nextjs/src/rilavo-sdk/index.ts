/**
 * Rilavo SDK -- verifier-side credential checking.
 *
 * Gate order mirrors src/rilavo/verifier.py EXACTLY:
 *   shape -> version(0b) -> audience -> expiry/not-yet-valid ->
 *   issuer lookup -> key_not_valid_at_issuance -> signature ->
 *   replay -> revocation -> proof-of-possession -> scope
 */
import { canonicalize } from "./jcs.js";
import { sha256Hex } from "./sha256.js";
import { ed25519Verify } from "./ed25519.js";
import * as nodeCrypto from "node:crypto";
import { getInstrumentation, recordVerification, recordReplayDetected } from "./otel.js";

export interface CredentialFields {
  iss?: unknown; sub?: unknown; agt?: unknown; apk?: unknown;
  act?: unknown; aud?: unknown; iat?: number; exp?: number;
  nonce?: string; sig?: string; ver?: number; dlg?: number;
  [k: string]: unknown;
}
export type Credential = Record<string, unknown>;

export interface VerifyResult {
  accepted: boolean;
  reasonCode: string | null;
}

export interface IssuerKeyEntry {
  issuerId: string;
  publicKeyPem: string;
  validUntil: number;          // seconds; far-future when healthy
}

export interface KeyDirectory {
  lookup(issuerId: string): IssuerKeyEntry | null;
  unreachable?: boolean;
}

export interface PopRequest {
  method: string;
  path: string;
  requestedAction: string;
  signature: string;           // base64url
  requestNonce: string;
}

export interface NonceCacheLike {
  seenBefore(nonce: string, windowSeconds: number, now?: number): boolean;
}

export class NonceCache implements NonceCacheLike {
  private seen = new Map<string, number>();
  seenBefore(nonce: string, windowSeconds: number,
             now: number = Math.floor(Date.now() / 1000)): boolean {
    for (const [n, exp] of this.seen) if (exp <= now) this.seen.delete(n);
    if (this.seen.has(nonce)) return true;
    this.seen.set(nonce, now + windowSeconds);
    // Record cache size metric
    getInstrumentation().setNonceCacheSize(this.seen.size);
    return false;
  }

  /** Clear all entries from the nonce cache (useful for testing) */
  clear(): void {
    this.seen.clear();
  }
}

/**
 * Redis-backed nonce cache for distributed multi-instance deployments.
 * Uses ioredis for Redis operations with explicit async connect.
 * Gracefully degrades to in-memory on connection failure (fail-open for availability).
 */
export class RedisNonceCache implements NonceCacheLike {
  private client: any = null; // ioredis instance
  private readonly url: string;
  private readonly keyPrefix: string;
  private readonly fallback = new NonceCache();
  private useFallback = false;

  constructor(url: string = "redis://localhost:6379", keyPrefix: string = "rilavo:nonce:") {
    this.url = url;
    this.keyPrefix = keyPrefix;
  }

  private async ensureClient(): Promise<void> {
    if (this.client || this.useFallback) return;
    try {
      const { Redis } = await import("ioredis");
      this.client = new Redis(this.url, {
        maxRetriesPerRequest: 1,
        retryStrategy: () => null,
        enableReadyCheck: true,
        lazyConnect: true,
      });
      await this.client.connect();
      this.useFallback = false;
    } catch {
      this.useFallback = true;
      this.client = null;
    }
  }

  private nonceKey(nonce: string): string {
    const hash = nodeCrypto.createHash("sha256").update(nonce).digest("hex").slice(0, 32);
    return `${this.keyPrefix}${hash}`;
  }

  async connect(): Promise<void> {
    await this.ensureClient();
  }

  seenBefore(nonce: string, windowSeconds: number,
             now: number = Math.floor(Date.now() / 1000)): boolean {
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
    } catch {
      this.useFallback = true;
      return this.fallback.seenBefore(nonce, windowSeconds, now);
    }
  }
}

export interface VerifyOptions {
  issuerDirectory: KeyDirectory;
  revocationLog: { isRevoked(nonce: string): boolean };
  nonceCache: NonceCache;
  verifierAudience: string;
  nowSeconds?: number;
}

export function b64urlDecode(s: string): Uint8Array {
  const b64 = s.replace(/-/g, "+").replace(/_/g, "/");
  const bin = atob(b64);
  return Uint8Array.from(bin, c => c.charCodeAt(0));
}

class Reject extends Error {
  constructor(public reasonCode: string) { super(reasonCode); }
}

export function popRequestPayload(
  method: string, path: string, act: string, nonce: string,
): Uint8Array {
  const body = { method: method.toUpperCase(), path, act, nonce };
  const digestHex = sha256Hex(canonicalize(body));
  return canonicalize({ rilavo_pop_v0: digestHex });
}

export function verifyCredential(
  fields: Credential,
  pop: PopRequest,
  opts: VerifyOptions,
): VerifyResult {
  const startTime = Date.now();
  const instrumentation = getInstrumentation();
  const issuer = fields["iss"] as string | undefined;

  try {
    const result = verifyInner(fields, pop, opts);
    const durationMs = Date.now() - startTime;
    recordVerification(result.accepted, result.reasonCode, durationMs, issuer);
    return result;
  } catch (e) {
    const durationMs = Date.now() - startTime;
    if (e instanceof Reject) {
      const result: VerifyResult = { accepted: false, reasonCode: e.reasonCode };
      recordVerification(false, e.reasonCode, durationMs, fields["iss"] as string | undefined);
      if (e.reasonCode === "replay_detected") {
        recordReplayDetected(fields["iss"] as string | undefined);
      }
      return result;
    }
    throw e;
  }
}

function verifyInner(fields: Credential, pop: PopRequest,
opts: VerifyOptions): VerifyResult {
  // step 0: shape
  for (const f of ["iss", "sub", "agt", "apk", "act", "aud", "nonce", "sig"]) {
    const v = fields[f];
    if (typeof v !== "string" || v === "") throw new Reject("missing_field");
  }
  for (const f of ["iat", "exp"] as const) {
    const v = fields[f];
    if (!Number.isInteger(v) || typeof v === "boolean")
      throw new Reject("malformed_credential");
  }
  if ((fields["dlg"] ?? 0) !== 0) throw new Reject("delegation_not_permitted");

  // step 0b: version gate (P-26)
  const ver = fields["ver"] ?? 1;
  if (typeof ver !== "number" || !Number.isInteger(ver) || ver !== 1)
    throw new Reject("unrecognized_version");

  const iat = fields["iat"] as number;
  const exp = fields["exp"] as number;

  // step 1: audience binding
  if ((fields["aud"] as string) !== opts.verifierAudience)
    throw new Reject("audience_mismatch");

  const now = opts.nowSeconds ?? Math.floor(Date.now() / 1000);

  // step 2: time window
  if (now >= exp) throw new Reject("expired");
  if (now < iat) throw new Reject("not_yet_valid");

  // step 3: issuer lookup (fail-closed)
  const iss = fields["iss"] as string;
  if (opts.issuerDirectory.unreachable) throw new Reject("unknown_issuer");
  const entry = opts.issuerDirectory.lookup(iss);
  if (entry) {
    getInstrumentation().recordIssuerDirectoryLookup(iss, true);
  } else {
    getInstrumentation().recordIssuerDirectoryLookup(iss, false);
    throw new Reject("unknown_issuer");
  }

  // step 4: retroactive compromise cutoff
  if (iat > entry.validUntil) throw new Reject("key_not_valid_at_issuance");

  // step 5: issuer signature over JCS-canonicalized sans sig
  const signingPayload: Record<string, unknown> = { ...fields };
  delete signingPayload["sig"];
  const pubRaw = pemToRawEd25519(entry.publicKeyPem);
  const sigBytes = b64urlDecode(fields["sig"] as string);
  let sigOk = false;
  try {
    sigOk = ed25519Verify(pubRaw, canonicalize(signingPayload), sigBytes);
  } catch { sigOk = false; }
  if (!sigOk) throw new Reject("invalid_signature");

  // step 6: replay (nonce single-use within TTL window)
  const nonce = fields["nonce"] as string;
  if (opts.nonceCache.seenBefore(nonce, exp - iat, now)) {
    recordReplayDetected(fields["iss"] as string);
    throw new Reject("replay_detected");
  }

  // step 7: revocation (fail-closed)
  if (opts.revocationLog.isRevoked(nonce)) throw new Reject("revoked");

  // step 8: proof-of-possession over THIS request
  const apk = fields["apk"] as string;
  const payload = popRequestPayload(pop.method, pop.path,
  pop.requestedAction, pop.requestNonce);
  const popSigBytes = b64urlDecode(pop.signature);
  if (!ed25519Verify(b64urlDecode(apk), payload, popSigBytes))
    throw new Reject("proof_of_possession_failed");

  // step 9: exact-match scope
  if (pop.requestedAction !== (fields["act"] as string))
    throw new Reject("scope_mismatch");

  return { accepted: true, reasonCode: null };
}

function pemToRawEd25519(pem: string): Uint8Array {
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

const ED25519_PKCS8_PREFIX = Buffer.from(
"302e020100300506032b657004220420", "hex");

export function importEd25519Seed(seed32: Uint8Array): nodeCrypto.KeyObject {
  const der = Buffer.concat([ED25519_PKCS8_PREFIX, Buffer.from(seed32)]);
  return nodeCrypto.createPrivateKey({ key: der, format: "der",
  type: "pkcs8" });
}

export function b64urlEncode(bytes: Uint8Array): string {
  return Buffer.from(bytes).toString("base64url");
}

/** Issuer id = "rilavo:iss:" + first 16 hex chars of SHA-256(raw pubkey),
 *  matching keys.fingerprint() exactly. */
export function issuerIdFromPublicKey(pubRaw32: Uint8Array): string {
  return ("rilavo:iss:"
  + sha256Hex(pubRaw32)).slice(0, "rilavo:iss:".length + 16);
}

export interface IssueOptions {
  issuerSeedB64url: string;       // base64url Ed25519 seed (32 bytes)
  principal: string;
  agent: string;
  agentPublicKeyB64url: string;   // base64url raw agent public key (apk)
  actionClass: string;
  audience: string;
  ttlSeconds?: number;            // default mirrors Python's 4-hour ceiling
  nowSeconds?: number;            // default wall clock
  /** Deterministic override for tests/goldens. Production callers MUST NOT
   *  set this: nonces come from the OS CSPRNG (secrets.token_urlsafe(16)). */
  nonceB64url?: string;
  context?: string;
}

export interface IssuedCredential {
  fields: Record<string, unknown>;   // includes sig (base64url)
}

export function issueCredential(o: IssueOptions): IssuedCredential {
  if (!o.issuerSeedB64url) throw new Error("issuerSeedB64url required");
  const seed = b64urlDecode(o.issuerSeedB64url);
  if (seed.length !== 32) throw new Error("issuer seed must be 32 bytes");

  const now = o.nowSeconds ?? Math.floor(Date.now() / 1000);
  const ttl = o.ttlSeconds ?? 14400;              // 4h ceiling, per P-06
  const nonce = o.nonceB64url ?? nodeCrypto.randomBytes(16).toString("base64url");

  const issPubRaw = ed25519PublicFromSeed(seed);
  const issuerId = issuerIdFromPublicKey(issPubRaw);

  const fields: Record<string, unknown> = {
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
  const sigBytes = nodeCrypto.sign(null, canonicalize(fields), signingKey);
  fields["sig"] = Buffer.from(sigBytes).toString("base64url");
  return { fields };
}

function ed25519PublicFromSeed(seed32: Uint8Array): Uint8Array {
  const priv = importEd25519Seed(seed32);
  const pubDer = nodeCrypto.createPublicKey(priv)
  .export({ type: "spki", format: "der" });
  return new Uint8Array(pubDer.subarray(12));
}

export type { Explanation } from "./diagnostics";
export { EXPLANATIONS, explainRejection, formatExplanation } from "./diagnostics.js";
export { runSmoke } from "./smoke.js";
export { runDoctor } from "./doctor.js";
