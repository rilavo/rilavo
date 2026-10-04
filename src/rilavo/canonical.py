"""RFC 8785 JSON Canonicalization Scheme (JCS), scoped to credential values.

Rilavo credentials contain only strings and Unix-second integers, so this
module implements exactly that subset of JCS: lexicographic key ordering by
UTF-16 code units, no insignificant whitespace, minimal string escaping with
lowercase hex, ES6 number formatting for integers. Full JCS (floats) is out of
scope by construction — credentials never carry floats.
"""

from __future__ import annotations

from typing import Any

# ECMAScript short escapes; everything else < 0x20 uses \u00xx lowercase hex.
_SHORT_ESCAPES = {
    0x08: "\\b",
    0x09: "\\t",
    0x0A: "\\n",
    0x0C: "\\f",
    0x0D: "\\r",
}


def _escape_string(s: str) -> str:
    out = ['"']
    for ch in s:
        code = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif code < 0x20:
            if code in _SHORT_ESCAPES:
                out.append(_SHORT_ESCAPES[code])
            else:
                out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _serialize(value: Any) -> str:
    if isinstance(value, bool):
        # JCS/ES6: booleans serialize as literals. Credentials never carry them,
        # but rejecting them silently here would be worse than handling them.
        return "true" if value else "false"
    if isinstance(value, str):
        return _escape_string(value)
    if isinstance(value, int):
        # Integers within the double-precision safe range serialize as-is,
        # matching ES6 Number::toString for integral values.
        if not -(2**53) + 1 <= value <= 2**53 - 1:
            raise ValueError("integer outside RFC 8785 safe range")
        return str(value)
    if isinstance(value, float):
        raise ValueError("floats are not representable in Rilavo credentials")  # noqa: TRY004
    if isinstance(value, list):
        return "[" + ",".join(_serialize(v) for v in value) + "]"
    if isinstance(value, dict):
        # Sort keys by UTF-16 code unit sequence (not raw code point).
        sorted_keys = sorted(value.keys(), key=lambda k: k.encode("utf-16-be"))
        return "{" + ",".join(
            _escape_string(k) + ":" + _serialize(value[k]) for k in sorted_keys
        ) + "}"
    raise TypeError(f"unsupported type for JCS: {type(value)!r}")


def canonicalize(obj: Any) -> bytes:
    """Serialize to canonical UTF-8 bytes per RFC 8785."""
    return _serialize(obj).encode("utf-8")
