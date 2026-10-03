import * as nodeCrypto from "node:crypto";
export interface CredentialFields {
    iss?: unknown;
    sub?: unknown;
    agt?: unknown;
    apk?: unknown;
    act?: unknown;
    aud?: unknown;
    iat?: number;
    exp?: number;
    nonce?: string;
    sig?: string;
    ver?: number;
    dlg?: number;
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
    validUntil: number;
}
export interface KeyDirectory {
    lookup(issuerId: string): IssuerKeyEntry | null;
    unreachable?: boolean;
}
export interface PopRequest {
    method: string;
    path: string;
    requestedAction: string;
    signature: string;
    requestNonce: string;
}
export interface NonceCacheLike {
    seenBefore(nonce: string, windowSeconds: number, now?: number): boolean;
}
export declare class NonceCache implements NonceCacheLike {
    private seen;
    seenBefore(nonce: string, windowSeconds: number, now?: number): boolean;
    /** Clear all entries from the nonce cache (useful for testing) */
    clear(): void;
}
/**
 * Redis-backed nonce cache for distributed multi-instance deployments.
 * Uses ioredis for Redis operations with explicit async connect.
 * Gracefully degrades to in-memory on connection failure (fail-open for availability).
 */
export declare class RedisNonceCache implements NonceCacheLike {
    private client;
    private readonly url;
    private readonly keyPrefix;
    private readonly fallback;
    private useFallback;
    constructor(url?: string, keyPrefix?: string);
    private ensureClient;
    private nonceKey;
    connect(): Promise<void>;
    seenBefore(nonce: string, windowSeconds: number, now?: number): boolean;
}
export interface VerifyOptions {
    issuerDirectory: KeyDirectory;
    revocationLog: {
        isRevoked(nonce: string): boolean;
    };
    nonceCache: NonceCache;
    verifierAudience: string;
    nowSeconds?: number;
}
export declare function b64urlDecode(s: string): Uint8Array;
export declare function popRequestPayload(method: string, path: string, act: string, nonce: string): Uint8Array;
export declare function verifyCredential(fields: Credential, pop: PopRequest, opts: VerifyOptions): VerifyResult;
export declare function importEd25519Seed(seed32: Uint8Array): nodeCrypto.KeyObject;
export declare function b64urlEncode(bytes: Uint8Array): string;
/** Issuer id = "rilavo:iss:" + first 16 hex chars of SHA-256(raw pubkey),
 *  matching keys.fingerprint() exactly. */
export declare function issuerIdFromPublicKey(pubRaw32: Uint8Array): string;
export interface IssueOptions {
    issuerSeedB64url: string;
    principal: string;
    agent: string;
    agentPublicKeyB64url: string;
    actionClass: string;
    audience: string;
    ttlSeconds?: number;
    nowSeconds?: number;
    /** Deterministic override for tests/goldens. Production callers MUST NOT
     *  set this: nonces come from the OS CSPRNG (secrets.token_urlsafe(16)). */
    nonceB64url?: string;
    context?: string;
}
export interface IssuedCredential {
    fields: Record<string, unknown>;
}
export declare function issueCredential(o: IssueOptions): IssuedCredential;
export type { Explanation } from "./diagnostics";
export { EXPLANATIONS, explainRejection, formatExplanation } from "./diagnostics.js";
export { runSmoke } from "./smoke.js";
export { runDoctor } from "./doctor.js";
