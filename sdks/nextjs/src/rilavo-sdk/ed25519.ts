/**
 * Ed25519 verification via node:crypto (OpenSSL-backed).
 *
 * CHOICE JUSTIFICATION: WebCrypto Ed25519 is not uniformly available across
 * Node/jest runtimes, and this environment has no npm registry access for
 * @noble/ed25519. node:crypto ships with every Node >= 12 and its Ed25519
 * implementation is OpenSSL-audited. A pure-TS or @noble backend can be
 * swapped in behind this function later without changing call sites.
 */
import { createPublicKey, KeyObject, verify as cryptoVerify } from "node:crypto";

// SPKI prefix for raw Ed25519 public keys:
const ED25519_SPKI_PREFIX = Buffer.from("302a300506032b6570032100", "hex");

export function importRawEd25519PublicKey(raw32: Uint8Array): KeyObject {
  const der = Buffer.concat([ED25519_SPKI_PREFIX, Buffer.from(raw32)]);
  return createPublicKey({ key: der, format: "der", type: "spki" });
}

export function ed25519Verify(
  publicKeyRaw32: Uint8Array,
  message: Uint8Array,
  signature64: Uint8Array,
): boolean {
  if (publicKeyRaw32.length !== 32 || signature64.length !== 64) return false;
  const key = importRawEd25519PublicKey(publicKeyRaw32);
  return cryptoVerify(null, Buffer.from(message), key, Buffer.from(signature64));
}

export function rawToPem(raw32: Uint8Array): string {
  const der = Buffer.concat([ED25519_SPKI_PREFIX, Buffer.from(raw32)]);
  return "-----BEGIN PUBLIC KEY-----\n" +
    der.toString("base64").replace(/(.{64})/g, "$1\n") +
    "\n-----END PUBLIC KEY-----\n";
}
