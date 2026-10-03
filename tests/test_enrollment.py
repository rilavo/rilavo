"""P3-A3/B enrollment protocol tests."""
import hashlib
import time

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

from rilavo.enrollment import (
    EnrollmentRequest,
    EnrollmentAuthority,
    proof_of_possession,
    verify_enrollment_proof,
    is_renewal_due,
)
from rilavo.directory_signing import DirectorySigner, DirectoryPayload


def _make_key(seed=1):
    return Ed25519PrivateKey.from_private_bytes(bytes([seed % 256] * 32))


def _pub_raw(key):
    return key.public_key().public_bytes(
        encoding=Encoding.Raw, format=PublicFormat.Raw)


# Import Encoding/PublicFormat at module level:
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


NOW = int(time.time())
TTL = 7 * 86400  # 7 days


class TestEnrollmentProof:

    def test_valid_pop_roundtrip(self):
        key = _make_key(1)
        pub_raw = _pub_raw(key)
        ts = NOW
        sig = proof_of_possession(key, pub_raw, ts, TTL)
        ok, reason = verify_enrollment_proof(pub_raw, ts, TTL, sig)
        assert ok and reason == ""

    def test_tampered_pubkey_rejected(self):
        key = _make_key(1)
        pub_raw = _pub_raw(key)
        ts = NOW
        sig = proof_of_possession(key, pub_raw, ts, TTL)
        wrong_pub = bytes([0xFF] * 32)
        ok, reason = verify_enrollment_proof(wrong_pub, ts, TTL, sig)
        assert not ok and "proof" in reason or "failed" in reason

    def test_stale_timestamp_rejected(self):
        key = _make_key(2)
        pub_raw = _pub_raw(key)
        stale_ts = NOW - 301  # beyond 300s default skew
        sig = proof_of_possession(key, pub_raw, stale_ts, TTL)
        ok, reason = verify_enrollment_proof(
            pub_raw, stale_ts, TTL, sig,
            max_clock_skew=300)
        assert not ok and reason == "stale_timestamp"

    def test_excessive_ttl_rejected(self):
        key = _make_key(3)
        pub_raw = _pub_raw(key)
        excessive_ttl = 8 * 86400  # 8 days > 7-day max
        sig = proof_of_possession(key, pub_raw, NOW, excessive_ttl)
        ok, reason = verify_enrollment_proof(
            pub_raw, NOW, excessive_ttl, sig, max_ttl=604800)
        assert not ok and "ttl" in reason.lower()


class TestEnrollmentAuthority:

    def test_process_enrollment_issues_signed_entry(self):
        from rilavo.directory_signing import DirectorySigner

        signer = DirectorySigner()
        authority = EnrollmentAuthority(signer)
        agent_key = _make_key(10)
        pub_raw = _pub_raw(agent_key)
        ts = NOW
        pop_sig = proof_of_possession(agent_key, pub_raw, ts, TTL)

        ok, entry, reason = authority.process_enrollment(
            pub_raw, "hidden-machine-01", ts, TTL, pop_sig)

        assert ok and entry is not None
        # Verify the signed entry against the signer's public key:
        signer_pub = signer.public_key
        from rilavo.directory_signing import verify_signed_entry
        assert verify_signed_entry(entry, signer_pub) is True


class TestRenewal:

    def test_is_renewal_due_within_window(self):
        exp_soon = time.time() + 3600   # expires in 1 hour < 24h window
        assert is_renewal_due(exp_soon) is True

    def test_not_due_when_far_from_expiry(self):
        exp_far = time.time() + 30 * 86400   # 30 days away
        assert is_renewal_due(exp_far) is False
