/**
 * Ed25519 verification via node:crypto (OpenSSL-backed).
 *
 * CHOICE JUSTIFICATION: WebCrypto Ed25519 is not uniformly available across
 * Node/jest runtimes, and this environment has no npm registry access for
 * @noble/ed25519. node:crypto ships with every Node >= 12 and its Ed25519
 * implementation is OpenSSL-audited. A pure-TS or @noble backend can be
 * swapped in behind this function later without changing call sites.
 */
import { KeyObject } from "node:crypto";
export declare function importRawEd25519PublicKey(raw32: Uint8Array): KeyObject;
export declare function ed25519Verify(publicKeyRaw32: Uint8Array, message: Uint8Array, signature64: Uint8Array): boolean;
export declare function rawToPem(raw32: Uint8Array): string;
