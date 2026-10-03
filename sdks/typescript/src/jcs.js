"use strict";
/**
 * JSON Canonicalization Scheme subset matching rilavo.canonical.py exactly:
 * lexicographically sorted keys, minimal escaping, integers only (floats
 * rejected), UTF-8 output.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.FloatInCredentialError = void 0;
exports.canonicalize = canonicalize;
class FloatInCredentialError extends Error {
    constructor() {
        super("floats are not representable in Rilavo credentials");
        this.name = "FloatInCredentialError";
    }
}
exports.FloatInCredentialError = FloatInCredentialError;
function escapeString(s) {
    let out = '"';
    for (const ch of s) {
        const code = ch.codePointAt(0);
        switch (true) {
            case ch === '"':
                out += '\\"';
                break;
            case ch === "\\":
                out += "\\\\";
                break;
            case code === 0x08:
                out += "\\b";
                break;
            case code === 0x09:
                out += "\\t";
                break;
            case code === 0x0a:
                out += "\\n";
                break;
            case code === 0x0c:
                out += "\\f";
                break;
            case code === 0x0d:
                out += "\\r";
                break;
            default:
                if (code < 0x20)
                    out += "\\u" + code.toString(16).padStart(4, "0");
                else
                    out += ch;
        }
    }
    return out + '"';
}
function serialize(value) {
    if (typeof value === "string")
        return escapeString(value);
    if (typeof value === "number") {
        if (!Number.isInteger(value))
            throw new FloatInCredentialError();
        if (!Number.isSafeInteger(value))
            throw new Error("integer outside safe range");
        return String(value);
    }
    if (Array.isArray(value))
        return "[" + value.map(serialize).join(",") + "]";
    if (value !== null && typeof value === "object") {
        const record = value;
        // JS default string sort == UTF-16 code unit order, matching Python's
        // sort matches Python byte-ordering for ASCII keys (JCS spec).
        const keys = Object.keys(record).sort();
        return ("{" +
            keys.map(k => `${escapeString(k)}:${serialize(record[k])}`).join(",") +
            "}");
    }
    throw new Error(`unsupported value in credential: ${String(value)}`);
}
function canonicalize(obj) {
    return new TextEncoder().encode(serialize(obj));
}
