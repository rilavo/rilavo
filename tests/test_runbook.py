"""Sev1 key-compromise drill (P-12 runbook / P-23 ladder), end to end offline.

Every assertion is explicit. The drill proves: pre-cutoff credentials still
verify per policy; post-compromise credentials are rejected via the EXISTING
key_not_valid_at_issuance check; the replacement key is live; and the
disclosure window stays an Open parameter, never a hardcoded number.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from rilavo.api import Issuer, do_issue, do_verify
from rilavo.credential import DEFAULT_MAX_TTL_SECONDS, IssueRequest, issue as raw_issue
from rilavo.errors import KEY_NOT_VALID_AT_ISSUANCE
from rilavo.keys import (
    FAR_FUTURE,
    KeyDirectory,
    b64url_encode,
    generate_keypair,
    public_key_bytes,
)
from rilavo.pop import Request, sign_request
from rilavo.runbook import (
    ENFORCEMENT_PATH,
    ESCALATION_LADDER,
    SEV1,
    IncidentRunbook,
    run_drill,
)
from rilavo.verifier import NonceCache

V = "verifier:drill.example.com"
T0 = 1_760_000_000.0


class World:
    """One issuer, one directory, one verifier — with controllable time."""

    def __init__(self):
        self.directory = KeyDirectory()
        self.issuer = Issuer()
        self.issuer.register_into(self.directory)
        self.agent_priv, self.agent_pub = generate_keypair()

    def issue(self, at=T0, signer=None):
        signer = signer or self.issuer._private_key
        issuer_id = self.issuer.issuer_id if signer is self.issuer._private_key \
            else None
        cred = raw_issue(
            signer,
            issuer_id or __import__("rilavo.keys", fromlist=["fingerprint"]).fingerprint(signer.public_key()),
            IssueRequest(principal="acme-corp:runner-04", agent="agt_drill",
                         agent_public_key_b64=b64url_encode(public_key_bytes(self.agent_pub)),
                         action_class="data.read", audience=V),
            now=datetime.fromtimestamp(at, tz=timezone.utc))
        return cred

    def verify(self, cred, now):
        s, n = sign_request(self.agent_priv, "POST", "/x", "data.read")
        return do_verify(V, cred, Request("POST","/x","data.read",s,n),
                         self.directory, RevocationLogHolder.log,
                         nonces=NonceCache(), now=now)


class RevocationLogHolder:
    from rilavo.revocation import RevocationLog as _RL
    log = _RL()


def test_sev1_end_to_end_drill():
    w = World()
    detected_at = T0 + 1000

    # Pre-compromise credential, issued under the soon-to-be-compromised key:
    pre_cred = w.issue(at=T0 + 500)

    # Attacker holding the compromised key mints a credential AFTER detection:
    post_cred = w.issue(at=detected_at + 60)

    runbook = IncidentRunbook(w.directory)
    record = runbook.execute_sev1(w.issuer.issuer_id,
                                  "drill:anomalous_issuance_volume",
                                  detected_at=detected_at)

    # (P-12 step 2) cutoff published at DETECTION time, not later:
    assert record.revoked_at == detected_at
    assert record.severity == SEV1

    # (a) Pre-cutoff credential still verifies per policy, mid-TTL:
    r_old = w.verify(pre_cred, now=detected_at + 30)
    assert r_old.accepted is True

    # (b) Post-compromise credential rejected via EXISTING step 4 mechanism:
    r_post = w.verify(post_cred, now=post_cred.fields["iat"] + 1)
    assert r_post.accepted is False
    assert r_post.reason_code == KEY_NOT_VALID_AT_ISSUANCE

    # (c) Replacement key published and active:
    new_entry = w.directory.lookup(record.new_issuer_id)
    assert new_entry is not None

    # New credentials under the replacement key verify:
    from rilavo.api import Issuer as I2
    new_priv = serialization.load_pem_private_key(record.new_private_key_pem,
                                                  password=None)
    assert isinstance(new_priv, Ed25519PrivateKey)
    new_cred = raw_issue(new_priv, record.new_issuer_id,
                         IssueRequest(principal="acme-corp:runner-04",
                                      agent="agt_drill",
                                      agent_public_key_b64=b64url_encode(public_key_bytes(w.agent_pub)),
                                      action_class="data.read", audience=V),
                         now=datetime.fromtimestamp(detected_at + 120, tz=timezone.utc))
    s, n = sign_request(w.agent_priv, "POST", "/x", "data.read")
    r_new = do_verify(V, new_cred, Request("POST","/x","data.read",s,n),
                      w.directory, RevocationLogHolder.log, nonces=NonceCache(),
                      now=new_cred.fields["iat"] + 1)
    assert r_new.accepted is True


def test_cutoff_boundary_exact_moment():
    """A credential with iat EXACTLY at the cutoff remains valid (step 4
    rejects only iat AFTER valid_until)."""
    w = World()
    detected_at = T0 + 1000
    boundary_cred = w.issue(at=detected_at)          # iat == cutoff
    runbook = IncidentRunbook(w.directory)
    record = runbook.execute_sev1(w.issuer.issuer_id, "drill", detected_at=detected_at)
    assert record.revoked_at == detected_at
    assert w.verify(boundary_cred, now=detected_at + 1).accepted is True


def test_disclosure_window_is_parameterized_never_hardcoded():
    """P-23: exact window Open pending legal review. Default None means
    'unset until legal decides'; a value may be supplied once legal sets it."""
    w = World()
    default_runbook = IncidentRunbook(w.directory)
    rec_default = default_runbook.execute_sev1(w.issuer.issuer_id, "r1",
                                               detected_at=T0)
    assert rec_default.disclosure_window_seconds is None      # Open, not a number
    assert rec_default.to_dict()["disclosure_status"] == "open_pending_legal_review"

    d2 = KeyDirectory()
    other = Issuer()
    other.register_into(d2)
    legal_set = IncidentRunbook(d2, disclosure_window_seconds=3600.0)
    rec_set = legal_set.execute_sev1(other.issuer_id, "r2", detected_at=T0)
    assert rec_set.disclosure_window_seconds == 3600.0

    # The number exists ONLY where a caller supplied it:
    import inspect
    src = inspect.getsource(__import__("rilavo.runbook", fromlist=["IncidentRunbook"]))
    assert "disclosure_window_seconds: float | None = None" in src


def test_no_new_mechanism_enforcement_via_existing_step4():
    """P-23 worked example step 3: no new mechanism invented at incident time."""
    w = World()
    runbook = IncidentRunbook(w.directory)
    record = runbook.execute_sev1(w.issuer.issuer_id, "drill", detected_at=T0)
    assert record.cutoff_enforced_via == ENFORCEMENT_PATH == "key_not_valid_at_issuance"
    assert record.escalation_ladder == ESCALATION_LADDER


def test_scheduled_rotation_overlap_both_keys_live():
    """Scheduled rotation shares the enforcement path: old entry stays
    published during overlap; old-key credentials remain verifiable until
    natural expiry; new issuance uses the new key."""
    w = World()
    pre_rot_cred = w.issue(at=T0)                    # TTL defaults to 3600s here
    runbook = IncidentRunbook(w.directory)
    rot = runbook.rotate_key()                        # overlap default = max TTL
    new_entry = w.directory.lookup(rot["new_issuer_id"])
    assert new_entry is not None
    assert rot["old_entries_still_published"] is True
    # Old-key credential still verifiable mid-TTL after rotation:
    assert w.verify(pre_rot_cred, now=T0 + 60).accepted is True


def test_rotation_overlap_defaults_to_max_credential_ttl():
    """P-12: overlap window equals the maximum credential TTL -- derived from
    the P-06 constant, not an arbitrary number."""
    w = World()
    runbook = IncidentRunbook(w.directory)
    rot = runbook.rotate_key(overlap_seconds=None)
    assert rot["overlap_note"].endswith(f"(default overlap "
                                        f"{DEFAULT_MAX_TTL_SECONDS}s = max TTL)")


def test_retroactive_compromise_edge_case_honest_limitation():
    """P-12 edge case, kept honest: when compromise is discovered AFTER it
    happened, the cutoff can only be set to DETECTION time -- the true
    compromise moment is usually unknowable. Credentials minted between those
    two moments stay verifiable until their own exp: an acknowledged window
    that cannot be un-accepted after the fact, only prevented from continuing."""
    w = World()
    true_compromise = T0              # attacker obtained the key here
    detection = T0 + 3 * 3600         # noticed only 3h later
    window_cred = w.issue(at=true_compromise + 60)   # minted inside the window

    runbook = IncidentRunbook(w.directory)
    record = runbook.execute_sev1(w.issuer.issuer_id, "drill",
                                  detected_at=detection)
    assert record.revoked_at == detection   # cutoff = detection, not earlier

    # Inside its TTL it still verifies -- this exact window is un-un-acceptable:
    assert w.verify(window_cred, now=detection + 30).accepted is True
    # But it stops at natural expiry; nothing new gets through afterwards:
    late_cred = w.issue(at=detection + 60)
    r_late = w.verify(late_cred, now=detection + 61)
    assert r_late.accepted is False
    assert r_late.reason_code == KEY_NOT_VALID_AT_ISSUANCE


def test_revoke_refuses_future_cutoff():
    """P-12 step 2: valid_until is set to DETECTION time -- 'not a future time'.
    A future cutoff would keep attacker-issued credentials trusted; refused."""
    w = World()
    runbook = IncidentRunbook(w.directory)
    import time as _time
    with pytest.raises(ValueError, match="future"):
        runbook.revoke_key(w.issuer.issuer_id, "drill",
                           cutoff=_time.time() + 10_000)
    # The directory entry is untouched by the refusal:
    entry = w.directory.lookup(w.issuer.issuer_id)
    assert entry.valid_until == FAR_FUTURE


def test_incident_record_carries_p23_authority_statement():
    """P-23 Authority section: emergency action authority = operator of the
    compromised component (Rilavo at v0); concentration disclosed, transfer to
    a documented appealable process REQUIRED on second issuer (P-24)."""
    from rilavo.runbook import AUTHORITY_NOTE
    w = World()
    record = IncidentRunbook(w.directory).execute_sev1(
        w.issuer.issuer_id, "drill", detected_at=T0)
    assert record.authority == AUTHORITY_NOTE
    assert "DEFERRED" in record.authority          # status named, not resolved
    d = record.to_dict()
    assert d["authority"] == AUTHORITY_NOTE        # survives export


def test_run_drill_entry_point():
    """The offline drill entry point produces explicit observations."""
    class DrillWorld:
        def __init__(self):
            self.directory = KeyDirectory()
            self.issuer = Issuer()
            self.issuer.register_into(self.directory)
            self.priv, self.pub = generate_keypair()

        def issue_fn(self, runbook, phase, at=None):
            return self.issue(at=at if at is not None else T0 + 500)

        def issue(self, at):
            return raw_issue(
                self.issuer._private_key, self.issuer.issuer_id,
                IssueRequest(principal="p", agent="a",
                             agent_public_key_b64=b64url_encode(public_key_bytes(self.pub)),
                             action_class="data.read", audience=V),
                now=datetime.fromtimestamp(at, tz=timezone.utc))

        def verify_fn(self, cred, now):
            s, n = sign_request(self.priv, "POST", "/x", "data.read")
            return do_verify(V, cred, Request("POST","/x","data.read",s,n),
                             self.directory, RevocationLogHolder.log,
                             nonces=NonceCache(), now=now)

    world = DrillWorld()
    obs = run_drill(world.directory, world.issue_fn, world.verify_fn,
                    detected_at=T0 + 1000)
    assert obs["pre_cutoff_credential_verifies"] is True
    assert obs["post_compromise_credential_rejected_with"] == KEY_NOT_VALID_AT_ISSUANCE
    assert obs["cutoff_enforced_via"] == "key_not_valid_at_issuance"
    assert obs["new_issuer_published_and_active"] is True
    assert obs["disclosure_window_open"] is True
