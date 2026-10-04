"""D3 PROPOSAL -- signed key-directory entries (P-17 adjacent).

STATUS: PROPOSED, NOT DECIDED. docs/wave_2/17_DISCOVERY_AND_KEY_DIRECTORY.md
(P-17, Decided v0) specifies a single published versioned directory and does
NOT decide whether entries themselves are signed. P-17 explicitly names the
bootstrap-trust problem as an acknowledged limitation: first-fetch trust rests
on TLS plus a well-known location. This module therefore ships ONLY:

  - an OPTIONAL envelope type (SignedDirectoryEntry),
  - an OPTIONAL signer/verifier pair,
  - zero integration into KeyDirectory or the verification path.

Enabling nothing here changes nothing anywhere. If a future cycle DECIDES to
adopt signed directories, the decision must also answer what this module
deliberately does not: signing the directory does NOT solve first-fetch trust
unless the directory-signer key itself is authenticated out-of-band (an
attacker who can substitute the directory can substitute the signer key too).
"""

from __future__ import annotations

from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

PROPOSAL_STATUS = ("PROPOSED -- not a Decided register item; P-17 v0 leaves "
                   "directory-entry signing undecided")

WIRE_FIELDS = ("issuer_id", "public_key_pem", "valid_until",
               "directory_version")


@dataclass(frozen=True)
class DirectoryPayload:
    """The signable projection of a key-directory entry. Field set mirrors
    P-17's illustrative entry exactly -- nothing added, nothing removed."""

    issuer_id: str
    public_key_pem: str
    valid_until: float          # None => currently active (serialized as -1)
    directory_version: int

    def canonical_bytes(self) -> bytes:
        # Deterministic serialization of the four wire fields (JCS-compatible
        # for this string/int-only shape): sorted keys, no whitespace.
        import json
        obj = {
            "directory_version": self.directory_version,
            "issuer_id": self.issuer_id,
            "public_key_pem": self.public_key_pem,
            "valid_until": (-1 if self.valid_until is None
                            else self.valid_until),
        }
        return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


@dataclass(frozen=True)
class SignedDirectoryEntry:
    payload: DirectoryPayload
    signature: str              # base64url, Ed25519 over canonical_bytes()
    signer_id: str              # fingerprint-style id of the DIRECTORY signer


class DirectorySigner:
    """Signs directory payloads with a DEDICATED Ed25519 key distinct from
    any issuer signing key (the directory operator's identity, per the
    Horizon-2 federation direction P-17 names as its successor design)."""

    def __init__(self, private_key: Ed25519PrivateKey | None = None) -> None:
        import hashlib

        from .keys import generate_keypair
        self._private_key = private_key or generate_keypair()[0]
        pub = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.signer_id = ("rilavo:dir:"
                          + hashlib.sha256(pub).hexdigest()[:16])

    @property
    def public_key(self) -> Ed25519PublicKey:
        return self._private_key.public_key()

    def public_key_pem(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def sign(self, payload: DirectoryPayload) -> SignedDirectoryEntry:
        sig = self._private_key.sign(payload.canonical_bytes())
        import base64
        return SignedDirectoryEntry(payload=payload,
                                    signature=base64.urlsafe_b64encode(sig)
                                    .decode().rstrip("="),
                                    signer_id=self.signer_id)


def verify_signed_entry(signed: SignedDirectoryEntry,
                        directory_signer_public_key: Ed25519PublicKey) -> bool:
    """Verify a signed entry against an EXPLICITLY TRUSTED directory-signer
    public key. The caller must have obtained that key out-of-band -- passing
    a key fetched from the same untrusted channel would make this check
    theater. Returns True only when the signature validates."""
    try:
        directory_signer_public_key.verify(
            _b64decode(signed.signature), signed.payload.canonical_bytes())
        return True
    except (InvalidSignature, ValueError):
        return False


def _b64decode(s: str) -> bytes:
    import base64
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
