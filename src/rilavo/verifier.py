"""Reference verification algorithm — the literal implementation of Core Spec §6.

Steps 3 and 7 are the two fail-closed points. Every reject returns a stable
reason code from errors.py and is recorded as an audit receipt.
"""

from __future__ import annotations

import time

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .canonical import canonicalize
from .credential import REQUIRED_FIELDS, Credential, SUPPORTED_CREDENTIAL_VERSION
from .errors import (
    AUDIENCE_MISMATCH,
    EXPIRED,
    INVALID_SIGNATURE,
    KEY_NOT_VALID_AT_ISSUANCE,
    NOT_YET_VALID,
    PROOF_OF_POSSESSION_FAILED,
    REPLAY_DETECTED,
    REVOCATION_STATE_UNAVAILABLE,
    REVOKED,
    SCOPE_MISMATCH,
    UNRECOGNIZED_VERSION,
    UNKNOWN_ISSUER,
    VerificationError,
)
from .otel import get_instrumentation, record_verification, record_replay_detected
from .keys import IssuerKeyEntry, KeyDirectory, b64url_decode
from .pop import Request, verify_request_signature
from .receipts import ReceiptLog
from .revocation import RevocationLog

VERIFIED_REASON = "accept"


class NonceCache:
    """Replay defense (step 6): nonces tracked within the credential's TTL."""

    def __init__(self) -> None:
        self._seen: dict[str, float] = {}  # nonce -> expiry unix seconds

    def seen_before(self, nonce: str, window_seconds: int, now: float | None = None) -> bool:
        current = now if now is not None else time.time()
        self._evict(current)
        if nonce in self._seen:
            return True
        self._seen[nonce] = current + window_seconds
        # Record cache size metric
        try:
            from .otel import get_instrumentation
            get_instrumentation().set_nonce_cache_size(len(self._seen))
        except ImportError:
            pass
        return False

    def _evict(self, now: float) -> None:
        expired = [n for n, exp in self._seen.items() if exp <= now]
        for n in expired:
            del self._seen[n]


def verify(
    credential: Credential,
    request: Request,
    verifier_id: str,
    key_directory: KeyDirectory,
    revocation_log: RevocationLog,
    nonces: NonceCache | None = None,
    revocation_cache_refreshed_at: float | None = None,
    revocation_max_age_seconds: float = 300.0,
    receipts: ReceiptLog | None = None,
    now: float | None = None,
    leeway_seconds: float = 0.0,
) -> str:
    """Returns "accept" or raises VerificationError with a reason code."""
    import time as _time
    start_time = _time.perf_counter()
    current = now if now is not None else _time.time()
    outcome = "reject"

    # Get OTel instrumentation
    _otel = None
    try:
        from .otel import get_instrumentation
        _otel = get_instrumentation()
    except ImportError:
        pass

    def record_receipt(cred: Credential, outcome_str: str) -> None:
        if receipts is not None:
            receipts.record(cred.fields.get("iss", ""), cred.fields.get("nonce", ""), outcome_str, current)

    def reject(code: str, detail: str = "") -> str:
        nonce = credential.fields.get("nonce") if isinstance(credential.fields, dict) else None
        if receipts is not None and nonce is not None:
            record_receipt(credential, outcome)

        # Record OTel metrics for rejection
        if _otel:
            duration_ms = (_time.perf_counter() - start_time) * 1000
            issuer = credential.fields.get("iss") if isinstance(credential.fields, dict) else None
            record_verification(False, code, duration_ms=duration_ms * 1000, credential_issuer=issuer)
            if code == "replay_detected":
                record_replay_detected(credential_issuer=issuer)

        raise VerificationError(code, detail)

    def accept() -> str:
        record_receipt(credential, "accept")

        # Record OTel metrics for acceptance
        if _otel:
            duration_ms = (_time.perf_counter() - start_time) * 1000
            issuer = credential.fields.get("iss") if isinstance(credential.fields, dict) else None
            record_verification(True, duration_ms=duration_ms * 1000, credential_issuer=issuer)

        return VERIFIED_REASON

    try:
        # 0. Shape validation happens before any trust decision.
        credential.validate_shape()
    except VerificationError as exc:
        return reject(exc.reason_code, exc.detail)

    # 0b. Version gate (P-26): absent ver implicitly means 1; a credential
    #     carrying any other value is rejected as an unrecognized version --
    #     a clear, explicit failure, never a silent misinterpretation.
    _ver = credential.fields.get("ver", SUPPORTED_CREDENTIAL_VERSION)
    if _ver != SUPPORTED_CREDENTIAL_VERSION or isinstance(_ver, bool):
        return reject(UNRECOGNIZED_VERSION, f"ver={_ver!r}")

    # 1. Audience binding — the confused-deputy defense (RFC 8707 discipline).
    if credential.audience != verifier_id:
        return reject(AUDIENCE_MISMATCH, f"aud={credential.audience!r}")

    # 2. Time window (with optional clock-skew leeway).
    # Default leeway_seconds=0.0 preserves current behavior byte-for-byte.
    # Nonzero values widen the acceptance window symmetrically:
    #   expired check relaxes from now >= exp to now >= exp + leeway
    #   not-yet-valid check relaxes from now < iat to now < iat - leeway
    if current >= credential.fields["exp"] + leeway_seconds:
        return reject(EXPIRED)
    if current + leeway_seconds < credential.fields["iat"]:
        return reject(NOT_YET_VALID)

    # 3. Issuer lookup — fail-closed on unreachable directory.
    issuer_entry: IssuerKeyEntry | None = key_directory.lookup(credential.fields["iss"])
    if _otel:
        _otel.record_issuer_directory_lookup(credential.fields["iss"], issuer_entry is not None)
    if issuer_entry is None:
        return reject(UNKNOWN_ISSUER, credential.fields["iss"])

    # 4. Retroactive compromise cutoff.
    if credential.fields["iat"] > issuer_entry.valid_until:
        return reject(KEY_NOT_VALID_AT_ISSUANCE)

    # 5. Signature over JCS-canonicalized credential sans sig.
    if not issuer_entry.verify_credential_signature(
        credential.signing_payload(), credential.fields["sig"]
    ):
        return reject(INVALID_SIGNATURE)

    # 6. Replay detection, bounded by the credential's own validity window.
    cache = nonces or NonceCache()
    if cache.seen_before(credential.nonce, credential.ttl_seconds, current):
        # Record replay detection in OTel
        if _otel:
            issuer = credential.fields.get("iss") if isinstance(credential.fields, dict) else None
            record_replay_detected(credential_issuer=issuer)
        return reject(REPLAY_DETECTED)

    # 7. Revocation — fail-closed both on explicit revocation and on stale
    #    cache that cannot refresh.
    log_unreachable = bool(getattr(revocation_log, "unreachable", False))
    if not log_unreachable:
        try:
            nonce_is_revoked = revocation_log.is_revoked(credential.nonce)
        except Exception:
            log_unreachable = True  # a log that errors is a log we cannot trust
    cache_stale = (
        revocation_cache_refreshed_at is not None
        and revocation_log.is_stale(revocation_cache_refreshed_at, revocation_max_age_seconds)
    )
    if log_unreachable or cache_stale:
        return reject(REVOCATION_STATE_UNAVAILABLE)
    if nonce_is_revoked:
        return reject(REVOKED)

    # 8. Proof-of-possession: the agent's key over THIS request.
    if not verify_request_signature(credential.fields["apk"], request):
        return reject(PROOF_OF_POSSESSION_FAILED)

    # 9. Action-class match — exact match only at v0, no wildcards.
    if request.requested_action != credential.action_class:
        return reject(SCOPE_MISMATCH, f"cred={credential.action_class!r} req={request.requested_action!r}")

    # 10. Audit receipt, then accept.
    return accept()

