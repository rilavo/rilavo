"""Ed25519 key generation, encoding, and issuer key-directory entries (P-11, P-12).

Encoding rules (Core Spec §2): public keys and signatures are base64url,
no padding. A public key is 32 raw bytes; a signature is 64 raw bytes.
"""

from __future__ import annotations

import base64
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization

from .canonical import canonicalize


def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def b64url_decode(s: str) -> bytes:
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


def generate_keypair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generate an Ed25519 keypair from the OS CSPRNG (Core Spec §4)."""
    private_key = Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def public_key_bytes(public_key: Ed25519PublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def fingerprint(public_key: Ed25519PublicKey) -> str:
    """Stable issuer identifier: the SHA-256 fingerprint of the public key."""
    import hashlib

    digest = hashlib.sha256(public_key_bytes(public_key)).hexdigest()[:16]
    return f"rilavo:iss:{digest}"


@dataclass
class IssuerKeyEntry:
    """One published entry in the key directory (Core Spec §4).

    `valid_until` is the retroactive compromise cutoff: verifiers must reject
    any credential whose `iat` is after this timestamp. A healthy key uses a
    far-future sentinel; a compromised key gets its actual cutoff time.
    """

    fingerprint_id: str
    public_key_pem: bytes
    valid_until: float

    def verify_credential_signature(self, payload_no_sig: dict, sig: str) -> bool:
        pem_key = serialization.load_pem_public_key(self.public_key_pem)
        raw = pem_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        public_key = Ed25519PublicKey.from_public_bytes(raw)
        try:
            public_key.verify(b64url_decode(sig), canonicalize(payload_no_sig))
            return True
        except Exception:
            return False


FAR_FUTURE = datetime(9999, 1, 1, tzinfo=timezone.utc).timestamp()


class KeyDirectory:
    """In-memory key directory (v0: single versioned directory, Core Spec P-17).

    Verifiers cache entries locally; `unreachable` models a fetch failure so
    the fail-closed path in the verifier can be exercised.
    """

    def __init__(self) -> None:
        self._entries: dict[str, IssuerKeyEntry] = {}
        self.unreachable: bool = False

    def publish(self, entry: IssuerKeyEntry) -> None:
        self._entries[entry.fingerprint_id] = entry

    def revoke_key(self, fingerprint_id: str, at: datetime | None = None) -> None:
        """Compromise response (Core Spec §4): publish retroactive cutoff."""
        entry = self._entries[fingerprint_id]
        cutoff = (at or datetime.now(timezone.utc)).timestamp()
        self._entries[fingerprint_id] = IssuerKeyEntry(
            entry.fingerprint_id, entry.public_key_pem, cutoff
        )

    def lookup(self, issuer_id: str) -> IssuerKeyEntry | None:
        if self.unreachable:
            return None
        return self._entries.get(issuer_id)
