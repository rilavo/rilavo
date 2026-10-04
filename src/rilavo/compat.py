"""Verifier-side compatibility layer (P-18): dual acceptance adapter.

Decided posture (docs/wave_2/18_INTEROPERABILITY_SPECIFICATION.md): Rilavo
is complementary to OAuth 2.1, not a competitor. During a transition period
a verifier may accept BOTH an OAuth bearer token AND a Rilavo credential in
parallel, treating them as INDEPENDENT authentication mechanisms rather than
requiring a hard cutover -- decided explicitly, because forcing all-or-nothing
migration would be an adoption barrier for exactly the audience P-03 needs.

This module ONLY DISPATCHES between mechanisms. It deliberately does NOT
implement OAuth: bearer-token validation is a pluggable callable supplied by
the operator (token -> principal claims, or None if rejected). No bet is
made on CIMD, ID-JAG, AAuth, or any other adjacent standard -- they are
tracked, not adopted.

PRECEDENCE, documented and enforced (both credentials present):
  The Rilavo credential path is attempted FIRST. If it fails, the adapter
  returns that failure WITHOUT falling back to the bearer token. Rationale:
  silently degrading to a weaker mechanism after a stronger one failed would
  be a downgrade vulnerability. Senders should send one mechanism, or a valid
  one of each.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .api import VerifyResult, do_verify
from .credential import Credential
from .errors import VerificationError
from .keys import KeyDirectory
from .pop import Request
from .receipts import ReceiptLog
from .revocation import RevocationLog
from .verifier import NonceCache

MECHANISM_OAUTH_BEARER = "oauth_bearer"
MECHANISM_RILAVO_CREDENTIAL = "rilavo_credential"

REASON_NO_CREDENTIALS = "no_credentials"
REASON_BEARER_REJECTED = "oauth_bearer_rejected"


# BearerValidator: callable(token: str) -> dict principal-claims | None.
# The adapter never inspects the token beyond handing it over.
BearerValidator = Callable[[str], "dict | None"]


@dataclass(frozen=True)
class AuthResult:
    authenticated: bool
    mechanism: str | None          # MECHANISM_OAUTH_BEARER | MECHANISM_RILAVO_CREDENTIAL | None
    reason_code: str | None        # None when authenticated
    principal_claims: dict | None = None   # populated on the bearer path only


def authenticate(
    *,
    bearer_token: str | None = None,
    bearer_validator: BearerValidator | None = None,
    credential: Credential | None = None,
    pop_request: Request | None = None,
    verifier_id: str,
    key_directory: KeyDirectory,
    revocation_log: RevocationLog,
    nonces: NonceCache | None = None,
    receipts: ReceiptLog | None = None,
    now: float | None = None,
) -> AuthResult:
    """Dispatch authentication across the two accepted mechanisms.

    Exactly one of the two paths runs:
      * credential present -> the full reference verification algorithm
        (do_verify semantics, unchanged);
      * else bearer token present -> the operator's pluggable validator;
      * neither -> explicit REASON_NO_CREDENTIALS rejection.
    """
    # --- Rilavo credential path (precedence: attempted first) --------------
    if credential is not None:
        if pop_request is None:
            return AuthResult(False, MECHANISM_RILAVO_CREDENTIAL,
                              "missing_pop_request", None)
        try:
            result: VerifyResult = do_verify(
                verifier_id=verifier_id,
                credential=credential,
                request=pop_request,       # proof-of-possession required (P-07)
                key_directory=key_directory,
                revocation_log=revocation_log,
                nonces=nonces or NonceCache(),
                receipts=receipts,
                now=now,
            )
        except VerificationError as exc:
            return AuthResult(False, MECHANISM_RILAVO_CREDENTIAL,
                              exc.reason_code, None)
        if result.accepted:
            return AuthResult(True, MECHANISM_RILAVO_CREDENTIAL, None, None)
        # Anti-downgrade: a FAILED credential attempt is reported as-is.
        # No fallback to the bearer token.
        return AuthResult(False, MECHANISM_RILAVO_CREDENTIAL,
                          result.reason_code, None)

    # --- OAuth bearer path (dispatch only -- validation is pluggable) ------
    if bearer_token is not None:
        if bearer_validator is None:
            # An operator accepting bearer tokens MUST supply their own
            # validator; the protocol refuses to invent OAuth semantics.
            return AuthResult(False, MECHANISM_OAUTH_BEARER,
                              REASON_BEARER_REJECTED, None)
        claims = bearer_validator(bearer_token)
        if claims is None:
            return AuthResult(False, MECHANISM_OAUTH_BEARER,
                              REASON_BEARER_REJECTED, None)
        return AuthResult(True, MECHANISM_OAUTH_BEARER, None, claims)

    # --- neither mechanism presented ---------------------------------------
    return AuthResult(False, None, REASON_NO_CREDENTIALS, None)
