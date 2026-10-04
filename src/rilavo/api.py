"""Minimal protocol API surface (P-19): exactly two operations.

    issue(principal, agent, action_class, audience, ttl) -> credential
    verify(credential, request)                          -> accept/reject + reason

Everything else is enterprise product surface, deliberately outside the
protocol API. This module is a thin, embeddable facade over those two calls —
an HTTP deployment wraps these functions; it adds no third operation.
"""

from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .credential import Credential, IssueRequest, issue
from .errors import VerificationError
from .keys import FAR_FUTURE, IssuerKeyEntry, KeyDirectory, fingerprint
from .pop import Request
from .receipts import ReceiptLog
from .revocation import RevocationLog
from .tracing import trace_issue_credential, trace_verify_credential
from .verifier import NonceCache, verify


@dataclass
class VerifyResult:
    accepted: bool
    reason_code: str


class Issuer:
    """A self-hosted or hosted issuance service (Core Spec §4, §8)."""

    def __init__(self, private_key: Ed25519PrivateKey | None = None) -> None:
        from .keys import generate_keypair

        self._private_key = private_key or generate_keypair()[0]
        self.issuer_id = fingerprint(self._private_key.public_key())

    def public_key_pem(self) -> bytes:
        return self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def directory_entry(self) -> IssuerKeyEntry:
        return IssuerKeyEntry(
            fingerprint_id=self.issuer_id,
            public_key_pem=self.public_key_pem(),
            valid_until=FAR_FUTURE,
        )


    def register_into(self, directory: KeyDirectory) -> None:
        directory.publish(self.directory_entry())

    def issue_credential(
        self,
        principal: str,
        agent: str,
        agent_public_key: Ed25519PublicKey,
        action_class: str,
        audience: str,
        ttl_seconds: int | None = None,
        context: str | None = None,
    ) -> Credential:
        from .keys import b64url_encode, public_key_bytes

        kwargs = {}
        if ttl_seconds is not None:
            kwargs["ttl_seconds"] = ttl_seconds
        return issue(
            issuer_private_key=self._private_key,
            issuer_id=self.issuer_id,
            request=IssueRequest(
                principal=principal,
                agent=agent,
                agent_public_key_b64=b64url_encode(public_key_bytes(agent_public_key)),
                action_class=action_class,
                audience=audience,
                context=context,
                **kwargs,
            ),
        )


def do_issue(issuer: Issuer, **kwargs) -> Credential:
    """`POST /issue` equivalent."""
    principal = kwargs.get("principal", "unknown")
    action_class = kwargs.get("action_class", "unknown")
    audience = kwargs.get("audience", "unknown")
    with trace_issue_credential(principal=str(principal), action_class=str(action_class), audience=str(audience)):
        return issuer.issue_credential(**kwargs)


def do_verify(
    verifier_id: str,
    credential: Credential,
    request: Request,
    key_directory: KeyDirectory,
    revocation_log: RevocationLog,
    nonces: NonceCache | None = None,
    receipts: ReceiptLog | None = None,
    now: float | None = None,
    leeway_seconds: float = 0.0,
) -> VerifyResult:
    """`POST /verify` equivalent. Never raises; returns accept/reject + reason."""
    issuer_id = credential.fields.get("iss", "unknown")
    with trace_verify_credential(credential_issuer=str(issuer_id), audience=str(verifier_id)):
        try:
            reason = verify(
                credential=credential,
                request=request,
                verifier_id=verifier_id,
                key_directory=key_directory,
                revocation_log=revocation_log,
                nonces=nonces or NonceCache(),
                receipts=receipts,
                now=now,
                leeway_seconds=leeway_seconds,
            )
            return VerifyResult(accepted=True, reason_code=reason)
        except VerificationError as exc:
            return VerifyResult(accepted=False, reason_code=exc.reason_code)


def batch_issue(issuer: Issuer,
                requests: list[IssueRequest]) -> tuple[list[Credential],
                                                        list[dict]]:
    """Issues N credentials in one call. Each credential is independently
    verifiable with zero verifier changes. Reuses ALL existing semantics:
    nonce generation, TTL validation, signing.

    Returns (credentials, statuses). A single bad request in the batch does
    NOT fail the whole batch -- per-request status is reported instead.
    """
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    from .keys import b64url_decode

    creds: list[Credential] = []
    statuses: list[dict] = []
    for i, req in enumerate(requests):
        try:
            apk_raw = b64url_decode(req.agent_public_key_b64)
            agent_pub_key = Ed25519PublicKey.from_public_bytes(apk_raw)
            cred = do_issue(
                issuer,
                principal=req.principal,
                agent=req.agent,
                agent_public_key=agent_pub_key,
                action_class=req.action_class,
                audience=req.audience,
                ttl_seconds=req.ttl_seconds,
                context=req.context)
            creds.append(cred)
            statuses.append({"index": i, "ok": True})
        except Exception as exc:
            statuses.append({"index": i, "ok": False, "error": str(exc)})
    return creds, statuses

