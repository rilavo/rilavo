"""Clock-skew leeway tests (P-30 adjacent, ADOPTION_DEEP_WORK Phase 2 item 2).

leeway_seconds widens BOTH time-window checks symmetrically:
  accept iff  iat - leeway <= now < exp + leeway
Default leeway_seconds=0.0 preserves pre-leeway behavior exactly.
"""
from datetime import UTC

from rilavo.api import Issuer, do_verify
from rilavo.errors import EXPIRED, NOT_YET_VALID
from rilavo.keys import KeyDirectory, generate_keypair
from rilavo.pop import Request, sign_request
from rilavo.revocation import RevocationLog
from rilavo.verifier import NonceCache

V = "verifier:clock-skew.example"
NOW = 1_800_000_000  # fixed epoch for deterministic tests


class Harness:
    def __init__(self):
        self.issuer = Issuer()
        self.directory = KeyDirectory()
        self.issuer.register_into(self.directory)
        self.agent_priv, self.agent_pub = generate_keypair()

    def credential(self, iat=NOW - 60, ttl=3600):
        """Issue a credential backdated to `iat` with the given TTL."""
        from datetime import datetime

        from rilavo.credential import IssueRequest
        from rilavo.credential import issue as raw_issue
        from rilavo.keys import b64url_encode, public_key_bytes
        req = IssueRequest(
            principal="p", agent="a",
            agent_public_key_b64=b64url_encode(public_key_bytes(self.agent_pub)),
            action_class="data.read", audience=V, ttl_seconds=ttl)
        cred = raw_issue(self.issuer._private_key, self.issuer.issuer_id, req,
                         now=datetime.fromtimestamp(iat, tz=UTC))
        return cred

    def request(self):
        sig, nonce = sign_request(self.agent_priv, "POST", "/x", "data.read")
        return Request("POST", "/x", "data.read", sig, nonce)

    def result_for(self, cred, at, leeway=0.0):
        return do_verify(V, cred, self.request(), self.directory,
                         RevocationLog(), nonces=NonceCache(),
                         now=at, leeway_seconds=leeway)


def _fresh_cred_expired_by(seconds_ago, leeway_unused=None):
    """Credential whose exp is `seconds_ago` in the past relative to NOW."""
    h = Harness()
    exp = NOW - seconds_ago
    cred = h.credential(iat=exp - 3600, ttl=3600)
    return h, cred


def test_default_rejects_expired():
    """Regression guard: leeway=0 rejects expired exactly as before."""
    h, cred = _fresh_cred_expired_by(1)
    r = h.result_for(cred, at=NOW, leeway=0.0)
    assert not r.accepted
    assert r.reason_code == EXPIRED


def test_leeway_accepts_recently_expired():
    h, cred = _fresh_cred_expired_by(20)
    r = h.result_for(cred, at=NOW, leeway=30.0)
    assert r.accepted


def test_leeway_does_not_accept_before_iat_beyond_leeway():
    h = Harness()
    cred = h.credential(iat=NOW, ttl=3600)
    # 45s before issuance with only 30s leeway -> still not yet valid
    r = h.result_for(cred, at=NOW - 45, leeway=30.0)
    assert not r.accepted
    assert r.reason_code == NOT_YET_VALID


def test_leeway_allows_slightly_before_iat():
    h = Harness()
    cred = h.credential(iat=NOW, ttl=3600)
    # 20s before issuance with 30s leeway -> accepted
    r = h.result_for(cred, at=NOW - 20, leeway=30.0)
    assert r.accepted


def test_zero_leeway_rejects_before_iat():
    """Default behavior unchanged: any now < iat rejects."""
    h = Harness()
    cred = h.credential(iat=NOW, ttl=3600)
    r = h.result_for(cred, at=NOW - 1, leeway=0.0)
    assert not r.accepted
    assert r.reason_code == NOT_YET_VALID
