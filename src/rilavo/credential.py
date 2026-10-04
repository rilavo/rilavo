"""Credential issuance and field validation (P-06).

Field contract (Core Spec §1): iss, sub, agt, apk, act, aud, iat, exp, nonce
required; dlg (must be 0/absent at v0) and ctx optional; sig last. Default TTL
is 4 hours maximum, configurable shorter — never longer.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .canonical import canonicalize
from .errors import MALFORMED_CREDENTIAL, MISSING_FIELD, VerificationError
from .keys import b64url_encode

REQUIRED_FIELDS = ("iss", "sub", "agt", "apk", "act", "aud", "iat", "exp", "nonce", "sig")
OPTIONAL_FIELDS = ("dlg", "ctx")
# P-26 versioning: `ver` is RESERVED in the credential format's design space.
# It is deliberately NOT emitted by issue() -- v0 has one version and absent
# ver implicitly means 1 -- but a credential carrying ver is structurally
# valid, so a second version can be made explicit later without any
# format change. CREDENTIAL FORMAT NOT YET FROZEN (P-26): freeze triggers
# only after a production partner's real traffic; no such event has occurred.
# structural change to this format (P-06 stays untouched/unfrozen).
RESERVED_FIELDS = ("ver",)
SUPPORTED_CREDENTIAL_VERSION = 1

DEFAULT_MAX_TTL_SECONDS = int(timedelta(hours=4).total_seconds())
MIN_NONCE_ENTROPY_BITS = 128


@dataclass
class IssueRequest:
    principal: str          # sub
    agent: str              # agt
    agent_public_key_b64: str  # apk
    action_class: str       # act
    audience: str           # aud
    ttl_seconds: int = DEFAULT_MAX_TTL_SECONDS
    context: str | None = None  # ctx

    def __post_init__(self) -> None:
        if self.ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        if self.ttl_seconds > DEFAULT_MAX_TTL_SECONDS:
            raise ValueError(
                f"ttl_seconds exceeds protocol maximum of {DEFAULT_MAX_TTL_SECONDS}"
            )


@dataclass
class Credential:
    fields: dict = field(default_factory=dict)

    @property
    def nonce(self) -> str:
        return self.fields["nonce"]

    @property
    def audience(self) -> str:
        return self.fields["aud"]

    @property
    def action_class(self) -> str:
        return self.fields["act"]

    @property
    def ttl_seconds(self) -> int:
        return int(self.fields["exp"]) - int(self.fields["iat"])

    def validate_shape(self) -> None:
        if not isinstance(self.fields, dict):
            raise VerificationError(MALFORMED_CREDENTIAL, "credential is not an object")
        for name in REQUIRED_FIELDS:
            if name not in self.fields or self.fields[name] in (None, ""):
                raise VerificationError(MISSING_FIELD, name)
        string_fields = ("iss", "sub", "agt", "apk", "act", "aud", "nonce")
        for name in string_fields:
            if not isinstance(self.fields[name], str):
                raise VerificationError(MALFORMED_CREDENTIAL, f"{name} must be a string")
        for name in ("iat", "exp"):
            if not isinstance(self.fields[name], int) or isinstance(self.fields[name], bool):
                raise VerificationError(MALFORMED_CREDENTIAL, f"{name} must be an integer")
        dlg = self.fields.get("dlg", 0)
        if dlg != 0:
            # v0: no delegation exists yet (Wave 6).
            raise VerificationError("delegation_not_permitted", f"dlg={dlg!r}")
        # P-26: ver is reserved; presence alone is structural OK. Its VALUE
        # gate (must be 1 when present) lives in verifier.py step 0b with its
        # own reason code, so version failures never read as shape failures.

    def signing_payload(self) -> dict:
        return {k: v for k, v in self.fields.items() if k != "sig"}

    def to_json(self) -> str:
        import json
        return json.dumps(self.fields, separators=(",", ":"))

    @classmethod
    def from_json(cls, s: str) -> Credential:
        import json
        try:
            return cls(fields=json.loads(s))
        except json.JSONDecodeError as exc:
            raise VerificationError(MALFORMED_CREDENTIAL, str(exc)) from exc


def new_nonce() -> str:
    """Single-use random value, >= 128 bits of entropy (Core Spec §1)."""
    return secrets.token_urlsafe(16)


def issue(
    issuer_private_key: Ed25519PrivateKey,
    issuer_id: str,
    request: IssueRequest,
    now: datetime | None = None,
) -> Credential:
    """The smallest atomic function: claim it, sign it (Mother Blueprint Part I)."""
    now_dt = now or datetime.now(UTC)
    iat = int(now_dt.timestamp())
    exp = iat + request.ttl_seconds

    fields = {
        "iss": issuer_id,
        "sub": request.principal,
        "agt": request.agent,
        "apk": request.agent_public_key_b64,
        "act": request.action_class,
        "aud": request.audience,
        "iat": iat,
        "exp": exp,
        "nonce": new_nonce(),
    }
    if request.context is not None:
        fields["ctx"] = request.context

    signature = issuer_private_key.sign(canonicalize(fields))
    fields["sig"] = b64url_encode(signature)
    return Credential(fields=fields)
