"""Reject reason codes, one per verification failure mode.

Reason codes are stable wire values: verifiers return them to callers and they
appear in audit receipts. Never rename one; only add.
"""

from __future__ import annotations


class VerificationError(Exception):
    """Raised when a credential or request fails verification."""

    def __init__(self, reason_code: str, detail: str = "") -> None:
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(f"{reason_code}: {detail}" if detail else reason_code)


# Reason codes, in the order the reference algorithm checks them (Core Spec §6).
AUDIENCE_MISMATCH = "audience_mismatch"
EXPIRED = "expired"
NOT_YET_VALID = "not_yet_valid"
UNKNOWN_ISSUER = "unknown_issuer"                # fail-closed on directory
KEY_NOT_VALID_AT_ISSUANCE = "key_not_valid_at_issuance"  # post-compromise
INVALID_SIGNATURE = "invalid_signature"
MALFORMED_CREDENTIAL = "malformed_credential"
UNRECOGNIZED_VERSION = "unrecognized_version"    # P-26: ver present and != 1
MISSING_FIELD = "missing_field"
REPLAY_DETECTED = "replay_detected"
REVOKED = "revoked"
REVOCATION_STATE_UNAVAILABLE = "revocation_state_unavailable"  # fail-closed
PROOF_OF_POSSESSION_FAILED = "proof_of_possession_failed"
SCOPE_MISMATCH = "scope_mismatch"
DELEGATION_NOT_PERMITTED = "delegation_not_permitted"  # v0: dlg must be absent/0


# Re-export diagnostics for CLI compatibility
from .diagnostics import (
    EXPLANATIONS,
    Explanation,
    explain_rejection,
    format_explanation,
)

__all__ = [
    "AUDIENCE_MISMATCH",
    "DELEGATION_NOT_PERMITTED",
    "EXPIRED",
    "EXPLANATIONS",
    "INVALID_SIGNATURE",
    "KEY_NOT_VALID_AT_ISSUANCE",
    "MALFORMED_CREDENTIAL",
    "MISSING_FIELD",
    "NOT_YET_VALID",
    "PROOF_OF_POSSESSION_FAILED",
    "REPLAY_DETECTED",
    "REVOCATION_STATE_UNAVAILABLE",
    "REVOKED",
    "SCOPE_MISMATCH",
    "UNKNOWN_ISSUER",
    "UNRECOGNIZED_VERSION",
    "Explanation",
    "VerificationError",
    "explain_rejection",
    "format_explanation",
]
