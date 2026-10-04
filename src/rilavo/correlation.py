"""Correlation-gap instrumentation (P-13). INSTRUMENTATION ONLY.

LABEL: INSTRUMENTATION -- measurement and opt-in mitigation tooling. This
module NEVER declares P-13's residual risk resolved: docs/wave_2/
13_PRIVACY_ARCHITECTURE.md names reused sub/agt identifiers across unrelated
verifier relationships as "a real, current limitation of v0", with
per-relationship identifiers RECOMMENDED rather than enforced. Closing it by
default is a design change deliberately not yet made, gated on pilot evidence
that the gap is being exploited (the doc's own escalation trigger).

What lives here:
  1. CorrelationGapMonitor -- measures/detects cross-verifier reuse of `sub`
     or `agt` values in issuance records (distinct audiences sharing one
     identifier value = a correlation surface).
  2. RelationshipIdGenerator + CorrelationPolicy -- the OPTIONAL issuer-side
     per-relationship identifier mode. OFF by default; enabling is issuer
     configuration only: no spec change, no wire-format change, and default
     behavior stays byte-for-byte what it was.
"""

from __future__ import annotations

import hashlib
import hmac
from collections import defaultdict
from dataclasses import dataclass, field

LABEL = ("INSTRUMENTATION -- measurement only; the P-13 correlation gap "
         "remains OPEN")

# --------------------------------------------------------------------------
# Measurement side
# --------------------------------------------------------------------------

def _hash_identifier(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


@dataclass(frozen=True)
class IssuanceRecord:
    subject: str        # SHA-256 hex of `sub` -- the raw identifier is
                        # NEVER retained (the instrument must not become a
                        # secondary identity database, P-10 discipline)
    agent: str          # SHA-256 hex of `agt` -- same rule
    audience: str       # `aud` (not a principal identifier)


@dataclass(frozen=True)
class Collision:
    field_name: str             # "sub" | "agt"
    value_hash: str             # SHA-256 of the value -- never the raw value,
                                # so the instrument itself cannot become a
                                # secondary identity database (P-10 discipline)
    audiences: tuple
    distinct_audiences: int


class CorrelationGapMonitor:
    """Detects when one identifier value spans multiple verifier
    relationships -- the exact surface two colluding-or-compromised verifiers
    (or one noisy log leak) would need to correlate a principal."""

    def __init__(self) -> None:
        self.records: list[IssuanceRecord] = []

    def record_issuance(self, subject: str, agent: str, audience: str) -> None:
        # Hashed at ingestion: raw identifiers are never stored, even
        # transiently. Hashing is deterministic, so grouping by hash finds
        # exactly the same collisions as grouping by raw value.
        self.records.append(IssuanceRecord(
            _hash_identifier(subject), _hash_identifier(agent), audience))

    _FIELD_TO_ATTR = {"sub": "subject", "agt": "agent"}

    def _collisions_for(self, attr: str) -> list[Collision]:
        record_attr = self._FIELD_TO_ATTR[attr]
        by_value: dict[str, set[str]] = defaultdict(set)
        for rec in self.records:
            value = getattr(rec, record_attr)
            if value:
                by_value[value].add(rec.audience)
        out = []
        for value, auds in by_value.items():
            if len(auds) > 1:
                out.append(Collision(
                    field_name=attr,
                    value_hash=value,   # already a SHA-256 hex digest
                                        # (hashed at ingestion)
                    audiences=tuple(sorted(auds)),
                    distinct_audiences=len(auds)))
        return sorted(out, key=lambda c: (c.field_name, -c.distinct_audiences))

    def detect_reuse(self) -> list[Collision]:
        """All current cross-verifier reuse events, `sub` and `agt`."""
        return self._collisions_for("sub") + self._collisions_for("agt")

    def summary(self) -> dict:
        subs = self._collisions_for("sub")
        agts = self._collisions_for("agt")
        return {
            "label": LABEL,
            "issuances_observed": len(self.records),
            "subjects_reused_across_audiences": len(subs),
            "agents_reused_across_audiences": len(agts),
            "open_question_status": (
                "OPEN -- P-13 leaves per-relationship identifiers "
                "recommended, not enforced; closing requires pilot evidence"),
        }


# --------------------------------------------------------------------------
# Mitigation side (OPTIONAL, OFF by default -- recommended, not enforced)
# --------------------------------------------------------------------------

def relationship_subject_id(secret_key: bytes, subject: str, audience: str,
                            length_bytes: int = 12) -> str:
    """Deterministic, relationship-scoped identifier.

    Same (subject, audience) pair always yields the same opaque id -- the
    principal keeps a STABLE identity at that one verifier -- while different
    audiences see cryptographically unrelated ids (HMAC-SHA256, issuer-keyed,
    truncated to `length_bytes`). Output format stays an opaque,
    issuer-assigned string exactly as P-06 describes `sub`.
    """
    digest = hmac.new(secret_key, f"{subject}|{audience}".encode(),
                      hashlib.sha256).digest()[:length_bytes]
    return digest.hex()


@dataclass
class CorrelationPolicy:
    """Issuer-side configuration. DEFAULT IS OFF: P-13 recommends
    per-relationship identifiers but does not enforce them; enforcement by
    default is a design change gated on pilot evidence, not this module."""

    enabled: bool = False
    secret_key: bytes | None = None

    def __post_init__(self) -> None:
        if self.enabled and not self.secret_key:
            raise ValueError("enabled policy requires a secret_key")

    def scope_subject(self, subject: str, audience: str) -> str:
        if not self.enabled:
            return subject                    # OFF: pass through untouched
        assert self.secret_key is not None, "enabled policy requires a secret_key"
        return relationship_subject_id(self.secret_key, subject, audience)


def scoped_issue_args(subject: str, audience: str,
                      policy: CorrelationPolicy) -> str:
    """Single integration point for issuance tooling: wrap the principal
    before calling issue(). With the policy OFF this returns the input
    unchanged, so default-issued credentials are byte-identical to before."""
    return policy.scope_subject(subject, audience)
