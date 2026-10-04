"""HTTP service integration tests.

Exercises the deployed /issue, /verify, /revoke and /directory endpoints over
real HTTP. Protocol semantics are already covered by test_conformance.py;
these tests prove the deployment layer preserves them (P-19/P-31).
"""

from __future__ import annotations

import pytest

from rilavo.keys import b64url_encode, generate_keypair, public_key_bytes
from rilavo.pop import sign_request
from rilavo.service import RilavoService, get, post


@pytest.fixture(scope="module")
def svc():
    service = RilavoService().start()
    yield service
    service.stop()


@pytest.fixture()
def agent():
    priv, pub = generate_keypair()
    return priv, b64url_encode(public_key_bytes(pub))


def issue(svc, agent_pub_b64, audience, action_class="data.read", **kw):
    payload = {
        "principal": "acme-corp:runner-04",
        "agent": "agt_7d3e1c",
        "agent_public_key": agent_pub_b64,
        "action_class": action_class,
        "audience": audience,
    }
    payload.update(kw)
    return post(svc.url, "/issue", payload)


def verify(svc, cred, req):
    return post(svc.url, "/verify", {"credential": cred, "request": req})


def make_request(agent_priv, action="data.read"):
    sig, nonce = sign_request(agent_priv, "POST", "/x", action)
    return {"method": "POST", "path": "/x", "requested_action": action,
            "signature": sig, "request_nonce": nonce}


def test_health_and_directory(svc):
    status, body = get(svc.url, "/health")
    assert status == 200 and body["status"] == "ok"
    status, entry = get(svc.url, "/directory")
    assert status == 200
    assert entry["issuer_id"].startswith("rilavo:iss:")
    assert "BEGIN PUBLIC KEY" in entry["public_key_pem"]
    assert entry["verifier_id"] == svc.state.verifier_id


def test_issue_over_http_returns_credential(svc, agent):
    priv, pub_b64 = agent
    status, cred = issue(svc, pub_b64, svc.state.verifier_id)
    assert status == 201
    for field in ("iss", "sub", "agt", "apk", "act", "aud", "iat", "exp", "nonce", "sig"):
        assert field in cred
    assert cred["iss"] == svc.state.issuer.issuer_id


def test_verify_over_http_accepts_then_replays_rejected(svc, agent):
    priv, pub_b64 = agent
    _, cred = issue(svc, pub_b64, svc.state.verifier_id)
    req = make_request(priv)
    status, result = verify(svc, cred, req)
    assert status == 200 and result == {"accepted": True, "reason_code": "accept"}
    # Same nonce presented again through the same service -> replay_detected,
    # proving the service holds ONE process-wide NonceCache.
    _, replay = verify(svc, cred, req)
    assert replay == {"accepted": False, "reason_code": "replay_detected"}


def test_verify_over_http_rejects_audience_mismatch(svc, agent):
    priv, pub_b64 = agent
    _, cred = issue(svc, pub_b64, "verifier:somewhere-else.example.com")
    _, result = verify(svc, cred, make_request(priv))
    assert result["reason_code"] == "audience_mismatch"


def test_revoke_over_http_then_verify_rejected(svc, agent):
    priv, pub_b64 = agent
    _, cred = issue(svc, pub_b64, svc.state.verifier_id)
    status, rev = post(svc.url, "/revoke",
                       {"nonce": cred["nonce"], "revoked_by": "principal",
                        "reason_code": "user_request"})
    assert status == 200 and rev["revoked"] is True
    _, result = verify(svc, cred, make_request(priv))
    assert result["reason_code"] == "revoked"


def test_malformed_json_rejected_cleanly(svc):
    import json
    import urllib.request
    req = urllib.request.Request(svc.url + "/verify", data=b"{not json",
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    import urllib.error
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status, body = resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        status, body = exc.code, json.loads(exc.read())
    assert status == 400 and body["reason_code"] == "malformed_json"


def test_issue_rejects_ttl_over_maximum(svc, agent):
    priv, pub_b64 = agent
    status, body = issue(svc, pub_b64, svc.state.verifier_id, ttl_seconds=4 * 3600 + 1)
    assert status == 400


def test_verify_missing_request_fields_rejected_cleanly(svc, agent):
    priv, pub_b64 = agent
    _, cred = issue(svc, pub_b64, svc.state.verifier_id)
    status, body = verify(svc, cred, {"method": "POST"})
    assert status == 400 and "missing_field" in body["reason_code"]
