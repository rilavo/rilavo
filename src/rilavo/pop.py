"""Proof-of-possession request binding (P-07, Core Spec §3).

Holding a valid credential is NOT sufficient to act on it. The agent signs the
specific request — a hash of method, path, and a request-level nonce at v0 —
with the private key corresponding to the credential's apk.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .canonical import canonicalize
from .keys import b64url_decode, b64url_encode


def sign_request(
    agent_private_key: Ed25519PrivateKey,
    method: str,
    path: str,
    requested_action: str,
    request_nonce: str | None = None,
) -> tuple[str, str]:
    """Returns (signature, request_nonce). The verifier re-derives the same
    payload from the visible request fields, so nothing extra travels."""
    nonce = request_nonce or secrets.token_urlsafe(16)
    payload = request_payload(method, path, requested_action, nonce)
    signature = agent_private_key.sign(payload)
    return b64url_encode(signature), nonce


def request_payload(method: str, path: str, requested_action: str, nonce: str) -> bytes:
    body = {
        "method": method.upper(),
        "path": path,
        "act": requested_action,
        "nonce": nonce,
    }
    # Domain-separated hash keeps the signed thing compact and unambiguous.
    digest = hashlib.sha256(canonicalize(body)).hexdigest()
    return canonicalize({"rilavo_pop_v0": digest})


@dataclass
class Request:
    method: str
    path: str
    requested_action: str
    signature: str
    request_nonce: str

    def payload(self) -> bytes:
        return request_payload(self.method, self.path, self.requested_action, self.request_nonce)


def verify_request_signature(agent_public_key_b64: str, request: Request) -> bool:
    try:
        public_key = Ed25519PublicKey.from_public_bytes(b64url_decode(agent_public_key_b64))
        public_key.verify(b64url_decode(request.signature), request.payload())
        return True
    except (InvalidSignature, ValueError):
        return False
