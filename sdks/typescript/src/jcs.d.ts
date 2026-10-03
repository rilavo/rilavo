/**
 * JSON Canonicalization Scheme subset matching rilavo.canonical.py exactly:
 * lexicographically sorted keys, minimal escaping, integers only (floats
 * rejected), UTF-8 output.
 */
export declare class FloatInCredentialError extends Error {
    constructor();
}
export declare function canonicalize(obj: Record<string, unknown>): Uint8Array;
