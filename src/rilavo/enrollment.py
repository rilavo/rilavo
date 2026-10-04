"""P3-A3/B PROPOSAL — Rilavo ACME enrollment protocol primitives.

STATUS: PROPOSED -- not a Decided register item.
Implements enrollment request creation/verification and signed-directory-entry
issuance per docs/ADOPTION_DEEP_WORK.md Scenario B ("Rilavo ACME").

Domain separation follows pop.py's pattern exactly:
  PoP payload = SHA256(canonicalize({"rilavo_enrollment_v0": hex_digest}))
where hex_digest = SHA256(pubkey_raw || b64url(timestamp_bytes) || b64url(ttl_bytes))

No network code. No server. Pure protocol primitives only.
"""

from __future__ import annotations

import base64
import hashlib
import time
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .directory_signing import DirectoryPayload

# Enrollment constraints (Open/parameterized -- not hardcoded policy)
DEFAULT_MAX_ENROLLMENT_TTL_SECONDS = 7 * 86400       # 7 days
DEFAULT_MAX_CLOCK_SKEW_SECONDS = 300                  # 5 minutes


@dataclass(frozen=True)
class EnrollmentRequest:
    pubkey: bytes              # raw Ed25519 public key (32 bytes)
    claimed_identity: str      # human-readable name (informational only)
    requested_ttl_seconds: int
    timestamp: int             # unix seconds at request creation


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64ud(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def proof_of_possession(privkey: Ed25519PrivateKey,
                        pubkey_raw: bytes,
                        timestamp: int,
                        ttl_seconds: int) -> str:
    """Signs SHA256(pubkey || timestamp_be || ttl_be) with domain separation.

    Follows pop.py's canonicalize-then-domain-separate pattern:
    1. Concatenate pubkey_raw + timestamp as 8-byte big-endian + ttl as 8-byte BE
    2. Hash with SHA-256
    3. Wrap digest in canonicalized envelope with domain tag
    4. Sign the envelope bytes
    Returns base64url-encoded signature.
    """
    # Step 1: raw material
    ts_be = timestamp.to_bytes(8, "big")
    ttl_be = ttl_seconds.to_bytes(8, "big")
    raw_material = pubkey_raw + ts_be + ttl_be

    # Step 2: hash
    digest = hashlib.sha256(raw_material).digest()

    # Step 3: domain-separated envelope (canonical JSON like pop.py)
    envelope_body = '{"rilavo_enrollment_v0":"' + digest.hex() + '"}'
    envelope_bytes = envelope_body.encode("utf-8")

    # Step 4: sign
    sig = privkey.sign(envelope_bytes)
    return _b64u(sig)


def verify_enrollment_proof(
    pubkey_raw: bytes,
    timestamp: int,
    ttl_seconds: int,
    signature_b64url: str,
    max_clock_skew: int = DEFAULT_MAX_CLOCK_SKEW_SECONDS,
    max_ttl: int = DEFAULT_MAX_ENROLLMENT_TTL_SECONDS,
) -> tuple[bool, str]:
    """Verify an enrollment request's PoP without needing the private key.

    Returns (ok, reason). ok=False on any failure with a specific reason.
    """
    # Check timestamp freshness (anti-replay):
    now = int(time.time())
    if abs(now - timestamp) > max_clock_skew:
        return False, "stale_timestamp"

    # Check TTL bound:
    if ttl_seconds > max_ttl or ttl_seconds <= 0:
        return False, "ttl_exceeds_maximum" if ttl_seconds > 0 else "invalid_ttl"

    # Reconstruct expected PoP payload:
    ts_be = timestamp.to_bytes(8, "big")
    ttl_be = ttl_seconds.to_bytes(8, "big")
    raw_material = pubkey_raw + ts_be + ttl_be
    digest = hashlib.sha256(raw_material).digest()
    expected_envelope = ('{"rilavo_enrollment_v0":"' + digest.hex() + '"}').encode()

    # Verify PoP signature:
    try:
        pub_key = Ed25519PublicKey.from_public_bytes(pubkey_raw)
        pub_key.verify(_b64ud(signature_b64url), expected_envelope)
        return True, ""
    except (InvalidSignature, ValueError):
        return False, "proof_of_possession_failed"


class EnrollmentAuthority:
    """Trust operator that validates enrollment requests and issues signed
    directory entries using DirectorySigner from directory_signing.py."""

    def __init__(self, directory_signer):
        self.signer = directory_signer

    def process_enrollment(
        self,
        pubkey_raw: bytes,
        claimed_identity: str,
        timestamp: int,
        ttl_seconds: int,
        pop_signature_b64url: str,
        max_skew: int = DEFAULT_MAX_CLOCK_SKEW_SECONDS,
        max_ttl: int = DEFAULT_MAX_ENROLLMENT_TTL_SECONDS,
    ) -> tuple[bool, object | None, str]:
        """Validates and processes an enrollment. Returns (ok, entry_or_none, reason)."""
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        # Verify PoP first (fail-closed):
        ok, reason = verify_enrollment_proof(
            pubkey_raw, timestamp, ttl_seconds,
            pop_signature_b64url, max_skew, max_ttl)
        if not ok:
            return False, None, reason

        # Create directory payload:
        pem = _public_key_to_pem(Ed25519PublicKey.from_public_bytes(pubkey_raw))
        payload = DirectoryPayload(
            issuer_id=_issuer_id_from_raw(pubkey_raw),
            public_key_pem=pem,
            valid_until=int(time.time()) + ttl_seconds,
            directory_version=1,
        )
        signed = self.signer.sign(payload)
        return True, signed, ""


def is_renewal_due(valid_until_ts: float, within: int = 86400) -> bool:
    """Returns True if the entry expires within `within` seconds."""
    return time.time() >= valid_until_ts - within


def _public_key_to_pem(key: Ed25519PublicKey) -> str:
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    key.public_bytes(
        encoding=Encoding.Raw, format=PublicFormat.Raw)
    # Actually we want SPKI PEM format:
    spki_der = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return spki_der.decode()


def _issuer_id_from_raw(pubkey_raw: bytes) -> str:
    fp = hashlib.sha256(pubkey_raw).hexdigest()[:16]
    return f"rilavo:iss:{fp}"

