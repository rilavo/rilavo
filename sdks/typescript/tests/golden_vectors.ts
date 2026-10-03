/**
 * Shared golden test vectors loaded from golden/golden.json
 * Ensures byte-for-byte parity with Python reference implementation
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";

// Use __dirname which is available in CommonJS
// For ESM compatibility, we use a fallback
declare const __dirname: string;
const _dirname = typeof __dirname !== "undefined" ? __dirname : ".";
const _repoRoot = join(_dirname, "..", "..", "..", "..", "..");
const _goldenDir = join(_repoRoot, "golden");

export interface GoldenVectors {
  jcs: Array<{ input: Record<string, unknown>; expected: string }>;
  pop: {
    method: string;
    path: string;
    act: string;
    nonce: string;
    payload_hex: string;
  };
  credential_fields: Record<string, unknown>;
  issuer_pub_b64url: string;
  agent_pub_b64url: string;
  pop_sig: {
    method: string;
    path: string;
    act: string;
    nonce: string;
    sig_b64url: string;
  };
}

export interface RejectVectors {
  unknown_version: { credential_fields: Record<string, unknown> };
  wrong_audience: { credential_fields: Record<string, unknown> };
  expired: { credential_fields: Record<string, unknown> };
}

let _golden: GoldenVectors | null = null;
let _rejects: RejectVectors | null = null;

function getJsonPath(filename: string): string {
  return join(_goldenDir, filename);
}

export function getGoldenVectors(): GoldenVectors {
  if (!_golden) {
    const path = getJsonPath("golden.json");
    _golden = JSON.parse(readFileSync(path, "utf8")) as GoldenVectors;
  }
  return _golden!;
}

export function getRejectVectors(): RejectVectors {
  if (!_rejects) {
    const path = getJsonPath("rejects.json");
    _rejects = JSON.parse(readFileSync(path, "utf8")) as RejectVectors;
  }
  return _rejects!;
}

export function getGoldenCredentialFields(): Record<string, unknown> {
  return getGoldenVectors().credential_fields;
}

export function getGoldenIssuerPubB64url(): string {
  return getGoldenVectors().issuer_pub_b64url;
}

export function getGoldenAgentPubB64url(): string {
  return getGoldenVectors().agent_pub_b64url;
}

export function getGoldenPopSig(): GoldenVectors["pop_sig"] {
  return getGoldenVectors().pop_sig;
}

export function getGoldenJcsVectors(): GoldenVectors["jcs"] {
  return getGoldenVectors().jcs;
}

export function getGoldenPopVector(): GoldenVectors["pop"] {
  return getGoldenVectors().pop;
}
