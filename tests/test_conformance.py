"""Rilavo conformance suite.

Each test maps to a row of the Core Spec section-7 threat-model table and/or a
step of the section-6 reference verification algorithm. If a field changes
(P-06), this file is what gets re-checked first.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime

import pytest

from rilavo.api import Issuer, do_issue, do_verify
from rilavo.canonical import canonicalize
from rilavo.credential import (
    DEFAULT_MAX_TTL_SECONDS,
    Credential,
    IssueRequest,
)
from rilavo.credential import (
    issue as raw_issue,
)
from rilavo.errors import (
    AUDIENCE_MISMATCH,
    DELEGATION_NOT_PERMITTED,
    EXPIRED,
    INVALID_SIGNATURE,
    KEY_NOT_VALID_AT_ISSUANCE,
    NOT_YET_VALID,
    PROOF_OF_POSSESSION_FAILED,
    REVOCATION_STATE_UNAVAILABLE,
    REVOKED,
    SCOPE_MISMATCH,
    UNKNOWN_ISSUER,
    VerificationError,
)
from rilavo.keys import KeyDirectory, b64url_encode, generate_keypair, public_key_bytes
from rilavo.pop import Request, sign_request
from rilavo.receipts import ReceiptLog
from rilavo.revocation import GENESIS_PREV_HASH, RevocationEntry, RevocationLog
from rilavo.verifier import NonceCache, verify

VERIFIER_ID = "verifier:checkout.example.com"
NOW = 1_750_000_000.0


class Harness:
    """One issuer, one agent, one verifier -- the v0 topology (P-15)."""

    def __init__(self) -> None:
        self.issuer = Issuer()
        self.directory = KeyDirectory()
        self.issuer.register_into(self.directory)
        self.agent_priv, self.agent_pub = generate_keypair()
        self.revocations = RevocationLog()
        self.receipts = ReceiptLog()
        self.nonces = NonceCache()

    def credential(self, action_class="data.read", audience=VERIFIER_ID, ttl=3600):
        return do_issue(
            self.issuer,
            principal="acme-corp:agent-runner-04",
            agent="agt_7d3e1c",
            agent_public_key=self.agent_pub,
            action_class=action_class,
            audience=audience,
            ttl_seconds=ttl,
        )

    def request(self, method="POST", path="/data", requested_action="data.read"):
        sig, nonce = sign_request(self.agent_priv, method, path, requested_action)
        return Request(method=method, path=path, requested_action=requested_action,
                       signature=sig, request_nonce=nonce)

    def do_verify(self, cred, req, now=None):
        if now is None:
            now = cred.fields.get("iat", time.time()) + 1
        return do_verify(
            verifier_id=VERIFIER_ID,
            credential=cred,
            request=req,
            key_directory=self.directory,
            revocation_log=self.revocations,
            nonces=self.nonces,
            receipts=self.receipts,
            now=now,
        )


# ---------------------------------------------------------------------------
# The happy path: the smallest atomic function works end to end.
# ---------------------------------------------------------------------------

def test_valid_credential_is_accepted():
    h = Harness()
    result = h.do_verify(h.credential(), h.request())
    assert result.accepted is True
    assert result.reason_code == "accept"


def test_accept_records_audit_receipt_without_full_contents():
    h = Harness()
    cred = h.credential()
    h.do_verify(cred, h.request())
    receipt = h.receipts.receipts[-1]
    assert receipt["outcome"] == "accept"
    assert receipt["iss"] == h.issuer.issuer_id
    # Never full credential contents -- only a hash of the nonce (P-10).
    assert cred.fields["sub"] not in str(receipt)
    assert "sig" not in receipt


# ---------------------------------------------------------------------------
# Step 1 -- audience binding (confused-deputy defense).
# ---------------------------------------------------------------------------

def test_credential_presented_to_wrong_verifier_rejected():
    h = Harness()
    other = do_verify(
        verifier_id="verifier:other.example.com",
        credential=h.credential(),
        request=h.request(),
        key_directory=h.directory,
        revocation_log=h.revocations,
        nonces=NonceCache(),
    )
    assert other.accepted is False
    assert other.reason_code == AUDIENCE_MISMATCH


# ---------------------------------------------------------------------------
# Step 2 -- expiry / not-yet-valid.
# ---------------------------------------------------------------------------

def test_expired_credential_rejected():
    h = Harness()
    cred = h.credential(ttl=600)
    result = h.do_verify(cred, h.request(), now=cred.fields["exp"] + 1)
    assert result.reason_code == EXPIRED


def test_not_yet_valid_credential_rejected():
    h = Harness()
    cred = h.credential()
    result = h.do_verify(cred, h.request(), now=cred.fields["iat"] - 5)
    assert result.reason_code == NOT_YET_VALID


def test_ttl_never_exceeds_four_hours():
    with pytest.raises(ValueError):
        IssueRequest(principal="p", agent="a", agent_public_key_b64="x",
                     action_class="act", audience="aud",
                     ttl_seconds=DEFAULT_MAX_TTL_SECONDS + 1)


# ---------------------------------------------------------------------------
# Steps 3/4 -- directory fail-closed and retroactive compromise cutoff.
# ---------------------------------------------------------------------------

def test_unreachable_directory_fails_closed():
    h = Harness()
    h.directory.unreachable = True
    result = h.do_verify(h.credential(), h.request())
    assert result.reason_code == UNKNOWN_ISSUER


def test_unknown_issuer_rejected():
    h = Harness()
    stranger = Issuer()  # never registered into the directory
    cred = do_issue(stranger, principal="p", agent="a", agent_public_key=h.agent_pub,
                    action_class="data.read", audience=VERIFIER_ID)
    result = h.do_verify(cred, h.request())
    assert result.reason_code == UNKNOWN_ISSUER


def test_post_compromise_credentials_invalidated_retroactively():
    """Step 4: iat after the key's valid_until cutoff is rejected even though
    the signature under that same (compromised) key is perfectly valid."""
    h = Harness()
    compromise_at = NOW + 1000
    cutoff = datetime.fromtimestamp(compromise_at, tz=UTC)

    # A credential issued AFTER compromise, signed by whoever holds the key:
    forged = raw_issue(
        h.issuer._private_key,
        h.issuer.issuer_id,
        IssueRequest(principal="victim", agent="a",
                     agent_public_key_b64=b64url_encode(public_key_bytes(h.agent_pub)),
                     action_class="data.read", audience=VERIFIER_ID),
        now=cutoff + __import__("datetime").timedelta(seconds=60),
    )
    h.directory.revoke_key(h.issuer.issuer_id, at=cutoff)
    result = h.do_verify(forged, h.request(),
                         now=forged.fields["iat"] + 1)
    assert result.reason_code == KEY_NOT_VALID_AT_ISSUANCE


def test_key_valid_before_compromise_still_accepted_within_ttl():
    """Credentials issued BEFORE the cutoff stay valid until natural expiry."""
    h = Harness()
    cred = h.credential(ttl=3600)
    iat_dt = datetime.fromtimestamp(cred.fields["iat"], tz=UTC)
    h.directory.revoke_key(h.issuer.issuer_id, at=iat_dt + __import__("datetime").timedelta(minutes=30))
    result = h.do_verify(cred, h.request())  # verify at iat+1 < cutoff
    assert result.accepted is True


# ---------------------------------------------------------------------------
# Step 5 -- signature integrity (tamper detection).
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("field,value", [
    ("sub", "attacker"),
    ("act", "payments.initiate"),
    ("exp", 9_999_999_999),
])
def test_tampering_any_field_invalidates_signature(field, value):
    h = Harness()
    cred = h.credential()
    fields = dict(cred.fields)
    fields[field] = value
    tampered = Credential(fields=fields)
    result = h.do_verify(tampered, h.request(), now=tampered.fields["iat"] + 1)
    assert result.reason_code == INVALID_SIGNATURE


# ---------------------------------------------------------------------------
# Step 6 -- replay defense.
# ---------------------------------------------------------------------------

def test_replayed_nonce_rejected_within_validity_window():
    h = Harness()
    cred = h.credential()
    t0 = cred.fields["iat"] + 1
    first = h.do_verify(cred, h.request(), now=t0)
    assert first.accepted
    replay = h.do_verify(cred, h.request(), now=t0 + 1)
    assert replay.reason_code == "replay_detected"


# ---------------------------------------------------------------------------
# Step 7 -- revocation, hash chain, fail-closed.
# ---------------------------------------------------------------------------

def test_revoked_by_principal_rejected():
    """Either issuer OR principal can revoke -- independently (P-09)."""
    h = Harness()
    cred = h.credential()
    h.revocations.append(cred.nonce, revoked_by="principal", reason_code="user_request")
    result = h.do_verify(cred, h.request())
    assert result.reason_code == REVOKED


def test_revoked_by_issuer_rejected():
    h = Harness()
    cred = h.credential()
    h.revocations.append(cred.nonce, revoked_by="issuer", reason_code="suspected_compromise")
    result = h.do_verify(cred, h.request())
    assert result.reason_code == REVOKED


def test_unreachable_revocation_log_fails_closed():
    h = Harness()
    cred = h.credential()
    h.revocations.unreachable = True
    result = h.do_verify(cred, h.request())
    assert result.reason_code == REVOCATION_STATE_UNAVAILABLE


def test_stale_revocation_cache_fails_closed():
    """Once the cache is stale past the refresh interval and cannot refresh,
    the default flips to reject, not accept (Core Spec section 5)."""
    h = Harness()
    cred = h.credential()
    now = cred.fields["iat"] + 1
    stale_refreshed_at = now - 10_000  # far past the 5-minute default
    from unittest.mock import patch
    with patch("rilavo.verifier.time") as fake_time:
        fake_time.time.return_value = now
        with pytest.raises(VerificationError) as excinfo:
            verify(credential=cred, request=h.request(), verifier_id=VERIFIER_ID,
                   key_directory=h.directory, revocation_log=h.revocations,
                   nonces=NonceCache(),
                   revocation_cache_refreshed_at=stale_refreshed_at,
                   revocation_max_age_seconds=300.0,
                   now=now)
    assert excinfo.value.reason_code == REVOCATION_STATE_UNAVAILABLE


# ---------------------------------------------------------------------------
# Step 8 -- proof-of-possession.
# ---------------------------------------------------------------------------

def test_copied_credential_alone_is_inert():
    """A copied credential without the agent's private key cannot act."""
    h = Harness()
    cred = h.credential()
    attacker_req = Request(method="POST", path="/data", requested_action="data.read",
                           signature=b64url_encode(b"\x00" * 64), request_nonce="forged-nonce")
    result = h.do_verify(cred, attacker_req)
    assert result.reason_code == PROOF_OF_POSSESSION_FAILED


def test_pop_binds_to_method_path_and_action():
    """A signature over one request does not authorize a different one."""
    h = Harness()
    cred = h.credential(action_class="data.read")
    sig, nonce = sign_request(h.agent_priv, "POST", "/data", "data.read")
    wrong_path = Request(method="POST", path="/admin", requested_action="data.read",
                         signature=sig, request_nonce=nonce)
    result = h.do_verify(cred, wrong_path)
    assert result.reason_code == PROOF_OF_POSSESSION_FAILED


def test_wrong_agent_key_fails_pop():
    h = Harness()
    _, other_pub = generate_keypair()
    cred = do_issue(h.issuer, principal="p", agent="a", agent_public_key=other_pub,
                    action_class="data.read", audience=VERIFIER_ID)
    # request signed by harness agent key, but credential binds another key:
    result = h.do_verify(cred, h.request())
    assert result.reason_code == PROOF_OF_POSSESSION_FAILED


# ---------------------------------------------------------------------------
# Step 9 -- exact-match scope, no wildcards at v0 (Core Spec section 3).
# ---------------------------------------------------------------------------

def test_scope_mismatch_rejected_exact_match_only():
    h = Harness()
    cred = h.credential(action_class="payments.initiate")
    result = h.do_verify(cred, h.request(requested_action="payments.refund"))
    assert result.reason_code == SCOPE_MISMATCH


def test_wildcard_never_matches():
    h = Harness()
    cred = h.credential(action_class="payments.*")
    result = h.do_verify(cred, h.request(requested_action="payments.initiate"))
    assert result.reason_code == SCOPE_MISMATCH


# ---------------------------------------------------------------------------
# P-06 field contract shape validation.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("missing", ["iss", "sub", "agt", "apk", "act", "aud",
                                     "iat", "exp", "nonce", "sig"])
def test_missing_required_field_rejected(missing):
    h = Harness()
    cred = h.credential()
    del cred.fields[missing]
    result = h.do_verify(cred, h.request(), now=NOW + 10)
    assert result.accepted is False


def test_delegation_depth_nonzero_rejected_at_v0():
    """v0: dlg must be absent or 0 -- delegation is Wave 6 (Horizon 2)."""
    h = Harness()
    cred = h.credential()
    fields = dict(cred.fields)
    fields["dlg"] = 1
    tampered = Credential(fields=fields)
    result = h.do_verify(tampered, h.request(), now=tampered.fields["iat"] + 1)
    assert result.reason_code == DELEGATION_NOT_PERMITTED


# ---------------------------------------------------------------------------
# Revocation log integrity -- hash chaining detects retroactive tampering.
# ---------------------------------------------------------------------------

def test_hash_chain_detects_history_rewrite():
    h = Harness()
    h.revocations.append("nonce-a", revoked_by="issuer", reason_code="r1")
    honest_head_cached_by_verifier = h.revocations.head_hash()
    h.revocations.append("nonce-b", revoked_by="principal", reason_code="r2")

    # An operator rewrites entry 0 in place after the fact:
    e0 = h.revocations.entries[0]
    h.revocations.entries[0] = RevocationEntry(
        target="nonce-forged", revoked_at=e0.revoked_at, revoked_by=e0.revoked_by,
        reason_code=e0.reason_code, prev_hash=GENESIS_PREV_HASH)

    assert h.revocations.verify_chain() is False
    assert h.revocations.head_hash() != honest_head_cached_by_verifier


def test_intact_chain_verifies():
    log = RevocationLog()
    log.append("a", revoked_by="issuer", reason_code="x")
    log.append("b", revoked_by="principal", reason_code="y")
    log.append("c", revoked_by="issuer", reason_code="z")
    assert log.verify_chain() is True


# ---------------------------------------------------------------------------
# Canonicalization determinism (RFC 8785 subset, P-11).
# ---------------------------------------------------------------------------

def test_canonicalization_is_key_order_independent():
    assert canonicalize({"b": "2", "a": "1"}) == canonicalize({"a": "1", "b": "2"})


def test_canonicalization_escapes_control_characters():
    out = canonicalize({"k": "line\nbreak"}).decode("utf-8")
    assert out == '{"k":"line\\nbreak"}'


def test_credential_json_round_trip():
    h = Harness()
    cred = h.credential()
    restored = Credential.from_json(cred.to_json())
    result = h.do_verify(restored, h.request())
    assert result.accepted


# ---------------------------------------------------------------------------
# Privacy architecture (P-13): no correlatable static identifier beyond what
# the verifier's relationship requires.
# ---------------------------------------------------------------------------

def test_credentials_for_different_audiences_do_not_share_correlatable_state():
    """Two credentials to two different verifiers share only issuer-chosen sub/
    agt values; the format adds no cross-verifier link of its own."""
    h = Harness()
    c1 = h.credential(audience="verifier:a.example.com")
    c2 = h.credential(audience="verifier:b.example.com")
    assert c1.nonce != c2.nonce  # fresh randomness per issuance


def test_signature_verifies_over_jcs_canonical_payload_via_published_key():
    """Independent re-derivation of step 5: using ONLY the published
    directory entry's PEM, a third party can verify the credential signature
    over the RFC 8785-canonicalized payload sans 'sig'."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    h = Harness()
    cred = h.credential()
    entry = h.directory.lookup(h.issuer.issuer_id)
    pem = serialization.load_pem_public_key(entry.public_key_pem)
    raw = pem.public_bytes(encoding=serialization.Encoding.Raw,
                           format=serialization.PublicFormat.Raw)
    pub = Ed25519PublicKey.from_public_bytes(raw)
    from rilavo.keys import b64url_decode
    pub.verify(b64url_decode(cred.fields["sig"]),
               canonicalize(cred.signing_payload()))
