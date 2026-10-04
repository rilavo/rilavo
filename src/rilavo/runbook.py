"""Key-compromise incident runbook as code (P-12 first-cut runbook +
P-23 Sev1 ladder). Implements ONLY decided mechanics:

  1. Detect/suspect compromise.
  2. Immediately publish revocation of the suspected key to the key directory
     with valid_until set to DETECTION time -- erring early is the safer
     failure mode (P-12 step 2).
  3. Generate and publish a new key immediately (P-12 step 3).
  4. Verifiers enforce the cutoff automatically via the EXISTING reference
     algorithm step 4 (key_not_valid_at_issuance) -- no new mechanism is
     invented at incident time (P-23 worked example step 3).
  5. Disclosure happens publicly per the P-23 window -- whose exact length is
     OPEN pending legal review. It is therefore a constructor parameter,
     NEVER hardcoded: None means "unset until legal decides".

Pre-cutoff credentials under the compromised key remain verifiable until
their natural expiry; anything claiming issuance after the cutoff is rejected
outright. Scheduled rotation shares the same enforcement path (P-12 worked
example), with the overlap window equal to the maximum credential TTL.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import UTC, datetime

from cryptography.hazmat.primitives import serialization

from .credential import DEFAULT_MAX_TTL_SECONDS
from .keys import (
    FAR_FUTURE,
    IssuerKeyEntry,
    KeyDirectory,
    fingerprint,
    generate_keypair,
)
from .revocation import RevocationLog

SEV1 = "Sev1"
# Escalation ladder restated at protocol level (P-23): reused, not reinvented.
ESCALATION_LADDER = ("detector", "operator_of_compromised_component",
                     "affected_verifiers", "public_disclosure")
ENFORCEMENT_PATH = "key_not_valid_at_issuance"   # reference algorithm step 4
# P-23 Authority: emergency action sits with the operator of the compromised
# component. At v0 that is Rilavo (single issuer); this concentration is
# acceptable only because v0 failure modes are fully disclosed. It is recorded
# here as Deferred status, per the governance transition flagged in P-24 --
# a second issuer REQUIRES moving this to a documented, appealable process.
AUTHORITY_NOTE = ("operator_of_compromised_component; Rilavo at v0 (single "
                  "issuer); DEFERRED to documented appealable process on "
                  "second issuer (P-24)")


def _now() -> float:
    return time.time()


@dataclass
class IncidentRecord:
    severity: str
    reason: str
    detected_at: float
    revoked_at: float
    rotated_at: float
    compromised_issuer_id: str
    new_issuer_id: str
    new_private_key_pem: bytes
    new_public_key_pem: bytes
    cutoff_enforced_via: str          # always ENFORCEMENT_PATH -- no new mechanism
    disclosure_window_seconds: float | None   # None == OPEN until legal decides
    authority: str = AUTHORITY_NOTE           # P-23 Authority section, Deferred per P-24
    escalation_ladder: tuple = ESCALATION_LADDER

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d["escalation_ladder"] = list(self.escalation_ladder)
        d["new_public_key_pem"] = self.new_public_key_pem.decode()
        # Private material is returned to the OPERATOR once, at execution --
        # deliberately NOT included in shareable/exportable form.
        d.pop("new_private_key_pem")
        d["disclosure_status"] = ("open_pending_legal_review"
                                  if self.disclosure_window_seconds is None
                                  else f"within_{self.disclosure_window_seconds}s")
        return d


class IncidentRunbook:
    """Executable P-12/P-23 playbook over the EXISTING key-directory and
    verification mechanisms."""

    def __init__(self, directory: KeyDirectory,
                 revocations: RevocationLog | None = None,
                 disclosure_window_seconds: float | None = None) -> None:
        # P-23: the disclosure window is Open pending legal review. It is a
        # parameter with default None -- never a hardcoded number.
        self.directory = directory
        self.revocations = revocations if revocations is not None else RevocationLog()
        self.disclosure_window_seconds = disclosure_window_seconds
        self.actions: list[dict] = []      # auditable action log

    def _log(self, action: str, detail: dict) -> None:
        self.actions.append({"action": action, "ts": _now(), **detail})

    # -- step 2 ----------------------------------------------------------
    def revoke_key(self, issuer_id: str, reason: str,
                   cutoff: float | None = None) -> dict:
        """Publish retroactive cutoff for the suspect key at DETECTION time.

        P-12 step 2: the cutoff is the detection time -- NOT a future time.
        A future timestamp would leave attacker-issued credentials trusted
        for its duration, so it is refused outright (1s slack for clock skew).
        """
        cut = cutoff if cutoff is not None else _now()
        if cut > _now() + 1.0:
            raise ValueError(
                "refusing future cutoff: valid_until must be the DETECTION "
                "time, not a future time (P-12 step 2)")
        self.directory.revoke_key(issuer_id, at=datetime.fromtimestamp(cut, tz=UTC))
        record = {"issuer_id": issuer_id, "cutoff": cut, "reason": reason}
        self._log("revoke_key", record)
        return record

    # -- step 3 ----------------------------------------------------------
    def rotate_key(self, overlap_seconds: float | None = None) -> dict:
        """Generate + publish a fresh Ed25519 issuer key immediately.

        Overlap semantics (P-12): the OLD entry stays published until its
        valid_until closes, so pre-rotation credentials remain verifiable
        until natural expiry; default overlap equals the MAXIMUM credential
        TTL because after one max-TTL nothing signed under the old key can
        still be unexpired. For COMPROMISE response use execute_sev1, where
        the old key's cutoff is detection time, not rotation time.
        """
        overlap = (overlap_seconds if overlap_seconds is not None
                   else DEFAULT_MAX_TTL_SECONDS)
        private_key, public_key = generate_keypair()
        new_id = fingerprint(public_key)
        pem_pub = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        self.directory.publish(IssuerKeyEntry(
            fingerprint_id=new_id, public_key_pem=pem_pub, valid_until=FAR_FUTURE))
        result = {
            "new_issuer_id": new_id,
            "new_private_key": private_key,
            "new_public_key_pem": pem_pub,
            "old_entries_still_published": True,   # overlap: both keys live
            "overlap_note": ("old key remains published per its own "
                             f"valid_until (default overlap {overlap}s = max TTL)"),
        }
        self._log("rotate_key", {"new_issuer_id": new_id})
        return result

    # -- Sev1 orchestration (P-23 worked example) -------------------------
    def execute_sev1(self, compromised_issuer_id: str, reason: str,
                     detected_at: float | None = None) -> IncidentRecord:
        detected = detected_at if detected_at is not None else _now()
        rev = self.revoke_key(compromised_issuer_id, reason, cutoff=detected)
        rot = self.rotate_key()
        record = IncidentRecord(
            severity=SEV1,
            reason=reason,
            detected_at=detected,
            revoked_at=rev["cutoff"],
            rotated_at=_now(),
            compromised_issuer_id=compromised_issuer_id,
            new_issuer_id=rot["new_issuer_id"],
            new_private_key_pem=rot["new_private_key"].private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ),
            new_public_key_pem=rot["new_public_key_pem"],
            cutoff_enforced_via=ENFORCEMENT_PATH,
            disclosure_window_seconds=self.disclosure_window_seconds,
        )
        self._log("execute_sev1_complete",
                  {"incident": record.to_dict(), "severity": SEV1})
        return record


def run_drill(directory: KeyDirectory, issue_fn, verify_fn,
              detected_at: float | None = None) -> dict:
    """Offline Sev1 drill (P-12: 'a runbook that's never been tested is a
    draft'). issue_fn/verify_fn are the caller's existing issue/verify paths;
    returns explicit pass/fail observations for each drill assertion."""
    drill_runbook = IncidentRunbook(directory)
    old_cred = issue_fn(runbook=drill_runbook, phase="pre_compromise")
    detected = detected_at if detected_at is not None else _now()
    post_cred = issue_fn(runbook=drill_runbook, phase="post_compromise",
                         at=detected + 60)
    record = drill_runbook.execute_sev1(old_cred.fields["iss"],
                                        "drill:suspected_key_compromise",
                                        detected_at=detected)
    r_old = verify_fn(old_cred, now=detected + 30)       # pre-cutoff, mid-TTL
    r_post = verify_fn(post_cred, now=post_cred.fields["iat"] + 1)
    new_issuer_ok = directory.lookup(record.new_issuer_id) is not None
    return {
        "pre_cutoff_credential_verifies": r_old.accepted,
        "post_compromise_credential_rejected_with":
            None if r_post.accepted else r_post.reason_code,
        "cutoff_enforced_via": record.cutoff_enforced_via,
        "new_issuer_published_and_active": new_issuer_ok,
        "disclosure_window_open": record.disclosure_window_seconds is None,
        "incident": record.to_dict(),
    }
