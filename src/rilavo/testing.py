"""Day-one offline test kit (P-20, SDK Specification §"Testability without live Rilavo
infrastructure").

A developer must be able to write and run integration tests entirely offline — issuing
test credentials, verifying them against a known test issuer key, exercising accept and
reject paths — with zero network calls to real infrastructure. This module ships the
fixed pieces for that:

- A FIXED, deterministic test issuer Ed25519 keypair (literal PEM below). The fingerprint
  is stable across runs, machines, and versions, so tests can hardcode it.
- ``local_test_issuer()`` — an :class:`rilavo.api.Issuer` built from that fixed key.
- ``local_test_agent()`` — a FRESH RANDOM agent keypair (only the ISSUER is fixed; agent
  keys are per-credential proof-of-possession keys, so randomness is fine).
- ``offline_test_kit()`` — glue that wires the issuer into an in-memory key directory
  plus an empty in-memory revocation log, so a full issue -> proof-of-possession ->
  verify cycle runs with no network and no external infrastructure.

Nothing here changes the credential format or any protocol behavior; it only fixes
inputs that would otherwise be random.
"""

from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .api import Issuer, VerifyResult, do_issue, do_verify
from .keys import KeyDirectory
from .pop import Request, sign_request
from .revocation import RevocationLog

# Fixed test issuer private key (PKCS#8 PEM). Published deliberately: it signs ONLY
# credentials meant for offline testing against THIS kit's directory wiring. It must
# never be trusted by any real deployment's key directory.
TEST_ISSUER_PRIVATE_KEY_PEM = b"""-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIBujlHwIvGmjvIWxbIZdy2bZs8H8wrfVQlO0qCyKDDav
-----END PRIVATE KEY-----
"""

TEST_ISSUER_PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAI4NxaP5e6PsGtl7iFkjBOs0hCdxmPznnxASmKe1vCqU=
-----END PUBLIC KEY-----
"""

# Stable across runs; asserted by tests/test_testing_kit.py.
TEST_ISSUER_FINGERPRINT = "rilavo:iss:38f93d4f0edb4f65"

# Default audience used by the offline kit if the caller does not pick one.
DEFAULT_TEST_VERIFIER_ID = "verifier:test.rilavo.example"


def _fixed_private_key() -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(TEST_ISSUER_PRIVATE_KEY_PEM, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError("embedded test issuer key is not an Ed25519 private key")
    return key


def local_test_issuer() -> Issuer:
    """Issuer built from the fixed, published test keypair."""
    return Issuer(private_key=_fixed_private_key())


def local_test_agent() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Fresh random agent keypair (agents may be random; only the ISSUER is fixed)."""
    from .keys import generate_keypair

    return generate_keypair()


@dataclass
class OfflineTestKit:
    """End-to-end offline harness: fixed issuer + in-memory directory/log.

    Zero network, zero external infrastructure. Each ``verify`` call uses a fresh
    nonce cache, mirroring a stateless verifier request.
    """

    issuer: Issuer
    verifier_id: str

    def __post_init__(self) -> None:
        self.key_directory = KeyDirectory()
        self.revocation_log = RevocationLog()
        self.issuer.register_into(self.key_directory)

    def issue(self, principal: str, agent_public_key: Ed25519PublicKey,
              action_class: str, audience: str | None = None,
              ttl_seconds: int | None = None, context: str | None = None,
              agent: str = "agent:test-runner-01"):
        return do_issue(
            self.issuer,
            principal=principal,
            agent=agent,
            agent_public_key=agent_public_key,
            action_class=action_class,
            audience=audience or self.verifier_id,
            ttl_seconds=ttl_seconds,
            context=context,
        )

    def sign_request(self, agent_private_key: Ed25519PrivateKey, method: str, path: str,
                     requested_action: str) -> Request:
        signature, nonce = sign_request(agent_private_key, method, path, requested_action)
        return Request(method=method, path=path, requested_action=requested_action,
                       signature=signature, request_nonce=nonce)

    def verify(self, credential, request: Request) -> VerifyResult:
        return do_verify(
            self.verifier_id,
            credential,
            request,
            self.key_directory,
            self.revocation_log,
        )


def offline_test_kit(verifier_id: str = DEFAULT_TEST_VERIFIER_ID) -> OfflineTestKit:
    """Build the full offline kit in one call."""
    return OfflineTestKit(issuer=local_test_issuer(), verifier_id=verifier_id)
