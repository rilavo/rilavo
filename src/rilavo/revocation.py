"""Append-only, hash-chained revocation log (P-09).

Each entry: {target, revoked_at, revoked_by, reason_code, prev_hash}.
prev_hash chains to the previous entry, so any retroactive tampering —
including by the operator itself — is detectable against any cached earlier
log state (Core Spec §5).
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

GENESIS_PREV_HASH = "0" * 64

REVOKED_BY_ISSUER = "issuer"
REVOKED_BY_PRINCIPAL = "principal"


@dataclass
class RevocationEntry:
    target: str            # credential nonce
    revoked_at: float      # unix seconds
    revoked_by: str        # issuer | principal
    reason_code: str
    prev_hash: str

    def digest(self) -> str:
        payload = "|".join(
            [self.target, repr(self.revoked_at), self.revoked_by, self.reason_code, self.prev_hash]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "revoked_at": self.revoked_at,
            "revoked_by": self.revoked_by,
            "reason_code": self.reason_code,
            "prev_hash": self.prev_hash,
        }


class RevocationLog:
    """In-memory append-only log. A production deployment persists each append
    before acknowledging; entries are never mutated or removed."""

    def __init__(self) -> None:
        self.entries: list[RevocationEntry] = []
        self.unreachable: bool = False

    def append(
        self,
        target_nonce: str,
        revoked_by: str,
        reason_code: str = "unspecified",
        at: float | None = None,
    ) -> RevocationEntry:
        prev_hash = self.head_hash()
        entry = RevocationEntry(
            target=target_nonce,
            revoked_at=at if at is not None else time.time(),
            revoked_by=revoked_by,
            reason_code=reason_code,
            prev_hash=prev_hash,
        )
        self.entries.append(entry)
        return entry

    def head_hash(self) -> str:
        return self.entries[-1].digest() if self.entries else GENESIS_PREV_HASH

    def verify_chain(self) -> bool:
        """Anyone who cached an earlier log state can detect tampering."""
        prev = GENESIS_PREV_HASH
        for entry in self.entries:
            if entry.prev_hash != prev:
                return False
            prev = entry.digest()
        return True

    def is_revoked(self, nonce: str) -> bool:
        if self.unreachable:
            raise UnavailableError("revocation log unreachable")
        return any(e.target == nonce for e in self.entries)

    def is_stale(self, refreshed_at: float, max_age_seconds: float = 300.0) -> bool:
        """Cache staleness check; v0 default refresh interval is 5 minutes."""
        return (time.time() - refreshed_at) > max_age_seconds


class UnavailableError(Exception):
    pass
