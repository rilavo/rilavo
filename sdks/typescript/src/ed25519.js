"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.importRawEd25519PublicKey = importRawEd25519PublicKey;
exports.ed25519Verify = ed25519Verify;
exports.rawToPem = rawToPem;
/**
 * Ed25519 verification via node:crypto (OpenSSL-backed).
 *
 * CHOICE JUSTIFICATION: WebCrypto Ed25519 is not uniformly available across
 * Node/jest runtimes, and this environment has no npm registry access for
 * @noble/ed25519. node:crypto ships with every Node >= 12 and its Ed25519
 * implementation is OpenSSL-audited. A pure-TS or @noble backend can be
 * swapped in behind this function later without changing call sites.
 */
const node_crypto_1 = require("node:crypto");
// SPKI prefix for raw Ed25519 public keys:
const ED25519_SPKI_PREFIX = Buffer.from("302a300506032b6570032100", "hex");
function importRawEd25519PublicKey(raw32) {
    const der = Buffer.concat([ED25519_SPKI_PREFIX, Buffer.from(raw32)]);
    return (0, node_crypto_1.createPublicKey)({ key: der, format: "der", type: "spki" });
}
function ed25519Verify(publicKeyRaw32, message, signature64) {
    if (publicKeyRaw32.length !== 32 || signature64.length !== 64)
        return false;
    const key = importRawEd25519PublicKey(publicKeyRaw32);
    return (0, node_crypto_1.verify)(null, Buffer.from(message), key, Buffer.from(signature64));
}
function rawToPem(raw32) {
    const der = Buffer.concat([ED25519_SPKI_PREFIX, Buffer.from(raw32)]);
    return "-----BEGIN PUBLIC KEY-----\n" +
        der.toString("base64").replace(/(.{64})/g, "$1\n") +
        "\n-----END PUBLIC KEY-----\n";
}
