"""Compact credential encoding (PROPOSAL -- wire format UNCHANGED).

Implements the minimal-credential scheme from ADOPTION_DEEP_WORK Scenario D
for constrained channels (SMS, NFC, QR). Target: <160 bytes.

THIS IS NOT WIRED INTO VERIFY. The v0 wire format is unchanged until a
P-26 version decision adds support for compact encoding.

Encoding: version tag 0xC0 prefix + CBOR array of:
  [issuer_fp8, agent_pubkey32, act_hash8, aud_hash8, iat, exp, nonce16, sig64]

Resolver callbacks rehydrate full values from fingerprints at the
receiving end (fail-closed on unknown fingerprints).
"""

import hashlib
from collections.abc import Callable

VERSION_TAG = 0xC0


def _encode_uint(n: int) -> bytes:
    """CBOR unsigned integer encoding (RFC 8949 section 3.1)."""
    if n < 24:
        return bytes([n])
    if n < 0x100:
        return bytes([0x18, n])
    if n < 0x10000:
        return bytes([0x19]) + n.to_bytes(2, "big")
    if n < 0x100000000:
        return bytes([0x1A]) + n.to_bytes(4, "big")
    return bytes([0x1B]) + n.to_bytes(8, "big")


def _encode_bytes(b: bytes) -> bytes:
    """CBOR byte string encoding."""
    ln = len(b)
    if ln < 24:
        return bytes([0x40 | ln]) + b
    if ln < 0x100:
        return bytes([0x58, ln]) + b
    return bytes([0x59]) + ln.to_bytes(2, "big") + b


def _encode_text(s: str) -> bytes:
    """CBOR text string encoding."""
    data = s.encode("utf-8")
    ln = len(data)
    if ln < 24:
        return bytes([0x60 | ln]) + data
    if ln < 0x100:
        return bytes([0x78, ln]) + data
    return bytes([0x79]) + ln.to_bytes(2, "big") + data


def _encode_array_header(n: int) -> bytes:
    if n < 24:
        return bytes([0x80 | n])
    return bytes([0x98, n])


def _hash_prefix(value: str, length: int = 8) -> bytes:
    return hashlib.sha256(value.encode("utf-8")).digest()[:length]


def to_compact(fields: dict) -> bytes:
    """Encodes a credential field dict into compact binary form.

    Requires: iss, apk, act, aud, iat, exp, nonce, sig in fields.
    Returns: VERSION_TAG + CBOR array of [fp8, pub32, act_h8, aud_h8,
              iat_uint, exp_uint, nonce_raw16, sig_raw64].
    """
    iss = fields["iss"]
    fp8 = hashlib.sha256(iss.encode()).digest()[:8]
    pub_raw = _b64url_decode(fields["apk"])
    act_hash = _hash_prefix(fields["act"], 8)
    aud_hash = _hash_prefix(fields["aud"], 8)
    nonce_raw = _b64url_decode(fields["nonce"])[:16]
    sig_raw = _b64url_decode(fields["sig"])

    body = (
        _encode_bytes(fp8)
        + _encode_bytes(pub_raw)
        + _encode_bytes(act_hash)
        + _encode_bytes(aud_hash)
        + _encode_uint(fields["iat"])
        + _encode_uint(fields["exp"])
        + _encode_bytes(nonce_raw)
        + _encode_bytes(sig_raw)
    )
    arr_header = _encode_array_header(8)
    return bytes([VERSION_TAG]) + arr_header + body


def from_compact(data: bytes, resolve_issuer: Callable,
                 resolve_act: Callable, resolve_aud: Callable) -> dict:
    """Decodes a compact credential back to a field dict via resolvers.

    Fail-closed on unknown fingerprints (resolvers must raise or return None).
    """
    # Parse CBOR array manually from the data after VERSION_TAG:
    offset = 1  # skip version tag
    # Array header:
    ah = data[offset]; offset += 1
    count = ah & 0x1F
    items: list[bytes | int] = []
    for _ in range(count):
        major = data[offset] >> 5
        minor = data[offset] & 0x1F
        offset += 1
        if major == 2:  # byte string
            if minor < 24:
                length = minor
            elif minor == 24:
                length = data[offset]; offset += 1
            elif minor == 25:
                length = int.from_bytes(data[offset:offset+2], "big"); offset += 2
            else:
                length = int.from_bytes(data[offset:offset+4], "big"); offset += 4
            items.append(bytes(data[offset:offset+length])); offset += length
        elif major == 0:  # unsigned int
            if minor < 24:
                items.append(minor)
            elif minor == 24:
                items.append(data[offset]); offset += 1
            elif minor == 25:
                items.append(int.from_bytes(data[offset:offset+2], "big")); offset += 2
            elif minor == 26:
                items.append(int.from_bytes(data[offset:offset+4], "big")); offset += 4
            else:
                items.append(int.from_bytes(data[offset:offset+8], "big")); offset += 8

    fp8, pub_raw, act_hash, aud_hash, iat, exp, nonce_raw, sig_raw = items

    iss = resolve_issuer(fp8)
    if iss is None:
        raise ValueError("unknown issuer fingerprint")
    act = resolve_act(act_hash.hex())  # type: ignore[union-attr]
    if act is None:
        raise ValueError("unknown action hash")
    aud = resolve_aud(aud_hash.hex())  # type: ignore[union-attr]
    if aud is None:
        raise ValueError("unknown audience hash")

    import base64 as b64mod
    return {
        "iss": iss,
        "apk": b64mod.urlsafe_b64encode(pub_raw).decode().rstrip("="),  # type: ignore[arg-type]
        "act": act,
        "aud": aud,
        "iat": iat,
        "exp": exp,
        "nonce": b64mod.urlsafe_b64encode(nonce_raw).decode().rstrip("="),  # type: ignore[arg-type]
        "sig": b64mod.urlsafe_b64encode(sig_raw).decode().rstrip("="),  # type: ignore[arg-type]
    }


def _b64url_decode(s: str) -> bytes:
    import base64
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
