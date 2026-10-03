import type { NextRequest } from 'next/server';

import { NonceCache } from '@rilavo/sdk';
// OTel instrumentation
let _otelInitialized = false;
async function ensureOtelInitialized() {
  if (_otelInitialized) return;
  try {
    const { initializeInstrumentation } = await import('./otel.js');
    await initializeInstrumentation();
    _otelInitialized = true;
  } catch {
    // OTel optional - continue without metrics if not available
  }
}

async function recordVerification(accepted: boolean, reasonCode: string | null, durationMs: number, credentialIssuer?: string) {
  try {
    const { recordVerification: record } = await import('./otel.js');
    record(accepted, reasonCode, durationMs, credentialIssuer);
  } catch {}
}

async function recordReplayDetected(credentialIssuer?: string) {
  try {
    const { recordReplayDetected: record } = await import('./otel.js');
    record(credentialIssuer);
  } catch {}
}

async function recordIssuerDirectoryLookup(issuerId: string, found: boolean) {
  try {
    const { recordIssuerDirectoryLookup: record } = await import('./otel.js');
    record(issuerId, found);
  } catch {}
}

// NextResponse interface for injection/testing
export interface NextResponseLike {
  next(): any;
  json(body: any, init?: { status?: number }): any;
}

// Optional NextResponse injection for testing
let _injectedNextResponse: NextResponseLike | null = null;

export function injectNextResponse(nr: NextResponseLike) {
  _injectedNextResponse = nr;
}

export function clearInjectedNextResponse() {
  _injectedNextResponse = null;
}

function getNextResponse(): NextResponseLike {
  if (_injectedNextResponse) return _injectedNextResponse;
  const { NextResponse } = require('next/server');
  return NextResponse;
}
import type { Credential, PopRequest, VerifyOptions, VerifyResult } from '@rilavo/sdk';

// Optional SDK injection for testing
type VerifyCredentialFn = (
  fields: Credential,
  pop: PopRequest,
  opts: VerifyOptions
) => VerifyResult;

let _injectedVerifyCredential: VerifyCredentialFn | null = null;

export function injectVerifyCredential(fn: VerifyCredentialFn) {
  _injectedVerifyCredential = fn;
}

export function clearInjectedVerifyCredential() {
  _injectedVerifyCredential = null;
}

function getVerifyCredential(): VerifyCredentialFn {
  if (_injectedVerifyCredential) return _injectedVerifyCredential;
  const { verifyCredential } = require('@rilavo/sdk');
  return verifyCredential;
}

export interface RilavoNextConfig {
  /** The audience this site expects on credentials */
  audience: string;
  /** Header carrying the base64url credential (default: x-rilavo-credential) */
  headerName?: string;
  /** Paths exempt from verification, e.g. ['/', '/public/:path*'] */
  publicPaths?: string[];
  /** Issuer keys this site trusts (fetched once from their /directory). */
  issuerDirectory?: {
    unreachable?: boolean;
    lookup(issuerId: string): {
      issuerId: string;
      publicKeyPem: string;
      validUntil: number;
    } | null;
  };
  /** Revocation-log cache (fail-closed when stale/unreachable). */
  revocationLog?: { isRevoked(nonce: string): boolean };
  /** Override current time for testing (Unix seconds). */
  nowSeconds?: number;
}

function decodeCredential(raw: string): Record<string, unknown> {
  const bin = atob(raw.replace(/-/g, '+').replace(/_/g, '/'));
  const json = new TextDecoder().decode(Uint8Array.from(bin, c => c.charCodeAt(0)));
  return JSON.parse(json) as Record<string, unknown>;
}

function isPublic(pathname: string, patterns: string[]): boolean {
  return patterns.some(p => pathname === p || pathname.startsWith(p + '/'));
}

/**
 * Fail-closed Rilavo gate for a Next.js app.
 *
 * Proof-of-possession headers (added by the calling agent):
 *   x-rilavo-method, x-rilavo-path, x-rilavo-action,
 *   x-rilavo-pop-signature, x-rilavo-request-nonce
 *
 * Usage in middleware.ts:
 *   export default withRilavo({ audience: 'mystore.com',
 *                               issuerDirectory });
 */

// Shared nonce cache for replay protection (P-10 discipline)
const nonceCache = new NonceCache();

export function createMiddleware(config: RilavoNextConfig) {
  const header = config.headerName ?? 'x-rilavo-credential';

  // Use proper NonceCache from SDK for replay protection (P-10 discipline)

  return async function middleware(req: NextRequest): Promise<any> {
    const startTime = Date.now();
    const path = req.nextUrl.pathname;

    if (isPublic(path, config.publicPaths ?? [])) {
      return getNextResponse().next();
    }

    const raw = req.headers.get(header);
    if (!raw) {
      return getNextResponse().json(
        { error: 'no_credentials' },
        { status: 401 }
      );
    }

    let credential: Record<string, unknown>;
    try {
      credential = decodeCredential(raw);
    } catch {
      return getNextResponse().json(
        { error: 'malformed_credential' },
        { status: 401 }
      );
    }

    const nonce = req.headers.get('x-rilavo-request-nonce') ?? '';

    // Use injected SDK or dynamic import
    const verifyCredential = getVerifyCredential();
    // Extract issuer for metrics
    const issuer = credential.iss as string | undefined;

    // Wrap issuerDirectory lookup to record OTel metrics
    const originalLookup = config.issuerDirectory?.lookup;
    const wrappedLookup = originalLookup ? (issuerId: string) => {
      const entry = originalLookup(issuerId);
      recordIssuerDirectoryLookup(issuerId, entry !== null);
      return entry;
    } : undefined;

    const result = verifyCredential(
      credential as any,
      {
        method: req.method,
        path,
        requestedAction: req.headers.get('x-rilavo-action')
          ?? 'unspecified.action',
        signature: req.headers.get('x-rilavo-pop-signature') ?? '',
        requestNonce: nonce,
      },
      {
        issuerDirectory: config.issuerDirectory ?? {
          unreachable: false,
          lookup: () => null,
        },
        revocationLog: config.revocationLog ?? { isRevoked: () => false },
        nonceCache,
        verifierAudience: config.audience,
        nowSeconds: config.nowSeconds,
      } as any,
    );

    const durationMs = Date.now() - startTime;

    // Record OTel metrics
    await recordVerification(result.accepted, result.reasonCode, durationMs, issuer);
    if (!result.accepted && result.reasonCode === 'replay_detected') {
      await recordReplayDetected(issuer);
    }

    if (result.accepted) return getNextResponse().next();
    return getNextResponse().json(
      { error: result.reasonCode },
      { status: 401 }
    );
  };
}

export { createMiddleware as withRilavo };
