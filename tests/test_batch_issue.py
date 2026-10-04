"""Batch issuance tests: partial success, nonce uniqueness, wire parity."""

from __future__ import annotations

from rilavo.api import Issuer, batch_issue, do_verify
from rilavo.credential import IssueRequest
from rilavo.errors import VerificationError
from rilavo.pop import Request, sign_request
from rilavo.testing import local_test_agent, offline_test_kit


class BatchHarness:
    def __init__(self):
        self.kit = offline_test_kit()
        self.agent_priv, self.agent_pub = local_test_agent()
        from rilavo.keys import b64url_encode, public_key_bytes
        self.agent_pub_b64 = b64url_encode(public_key_bytes(self.agent_pub))

    def make_requests(self, count: int, audience: str = None,
                      **field_overrides):
        aud = audience or "verifier:batch.example"
        reqs = []
        for i in range(count):
            kw = {
                "principal": f"principal-{i}",
                "agent": f"agent-{i}",
                "agent_public_key_b64": self.agent_pub_b64,
                "action_class": field_overrides.get("action_class", "data.read"),
                "audience": field_overrides.get("audience", aud),
            }
            reqs.append(IssueRequest(**kw))
        return reqs

    def verify_one(self, cred):
        sig, nonce = sign_request(self.agent_priv, "POST", "/x", cred.fields["act"])
        pop = Request(method="POST", path="/x",
                      requested_action=cred.fields["act"],
                      signature=sig, request_nonce=nonce)
        try:
            result = do_verify(
                verifier_id=cred.fields["aud"],
                credential=cred,
                request=pop,
                key_directory=self.kit.key_directory,
                revocation_log=self.kit.revocation_log,
            )
            return result
        except VerificationError as e:
            return type("R", (), {"accepted": False, "reason_code": e.reason_code})()


def test_batch_of_valid_requests_all_succeed():
    h = BatchHarness()
    issuer = Issuer(private_key=h.kit.issuer._private_key)
    reqs = h.make_requests(50)
    creds, statuses = batch_issue(issuer, reqs)
    assert len(creds) == 50
    assert all(s["ok"] for s in statuses)
    # nonces unique across batch:
    nonces = [c.fields["nonce"] for c in creds]
    assert len(nonces) == len(set(nonces))


def test_mixed_batch_partial_success():
    """One invalid agent key (empty b64) does not fail the whole batch.
    Empty string passes IssueRequest validation (it's a string) but fails
    at do_issue time when Ed25519PublicKey.from_public_bytes rejects it."""
    h = BatchHarness()
    issuer = Issuer(private_key=h.kit.issuer._private_key)
    good1 = IssueRequest(principal="good-1", agent="a",
                         agent_public_key_b64=h.agent_pub_b64,
                         action_class="data.read",
                         audience="verifier:batch.example")
    # This one is constructible (empty string passes IssueRequest validation)
    # but will fail at batch_issue time during key decoding:
    bad = IssueRequest(principal="bad", agent="a",
                       agent_public_key_b64="",
                       action_class="data.read",
                       audience="verifier:batch.example")
    creds, statuses = batch_issue(issuer, [good1, bad])
    assert len(statuses) == 2
    assert statuses[0]["ok"] is True
    assert statuses[1]["ok"] is False
    assert "error" in statuses[1]
    assert len(creds) == 1               # only the valid one issued


def test_empty_batch_clean_error():
    h = BatchHarness()
    issuer = Issuer(private_key=h.kit.issuer._private_key)
    creds, statuses = batch_issue(issuer, [])
    assert creds == [] and statuses == []


def test_every_credential_passes_do_verify_independently():
    h = BatchHarness()
    issuer = Issuer(private_key=h.kit.issuer._private_key)
    N = 10
    reqs = h.make_requests(N)
    creds, _ = batch_issue(issuer, reqs)
    assert len(creds) == N
    for cred in creds:
        sig, nonce = sign_request(h.agent_priv, "POST", "/data", "data.read")
        pop = Request(method="POST", path="/data",
                      requested_action="data.read",
                      signature=sig, request_nonce=nonce)
        result = do_verify(
            verifier_id=cred.fields["aud"], credential=cred, request=pop,
            key_directory=h.kit.key_directory,
            revocation_log=h.kit.revocation_log)
        assert result.accepted, f"credential {cred.fields['nonce']} failed verify"


def test_nonce_uniqueness_across_200_credential_batch():
    h = BatchHarness()
    issuer = Issuer(private_key=h.kit.issuer._private_key)
    reqs = h.make_requests(200)
    creds, _ = batch_issue(issuer, reqs)
    nonces = [c.fields["nonce"] for c in creds]
    assert len(set(nonces)) == 200


def test_wire_size_report_for_200_credential_batch():
    h = BatchHarness()
    issuer = Issuer(private_key=h.kit.issuer._private_key)
    reqs = h.make_requests(200)
    creds, _ = batch_issue(issuer, reqs)
    total_bytes = sum(len(c.to_json().encode()) for c in creds)
    print(f"\n200-credential batch response body: {total_bytes} bytes "
          f"(~{total_bytes // 200} B/credential)")
    assert total_bytes > 0
