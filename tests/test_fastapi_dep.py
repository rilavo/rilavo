"""P2-B2: FastAPI dependency tests using synchronous TestClient."""

from __future__ import annotations

import json

from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from rilavo.fastapi import require_rilavo_agent
from rilavo.keys import b64url_encode, public_key_bytes
from rilavo.pop import sign_request
from rilavo.testing import local_test_agent, offline_test_kit

V = "verifier:fastapi-dep.example"
_kit = offline_test_kit()
_agent_priv, _agent_pub = local_test_agent()
_agent_pub_b64 = b64url_encode(public_key_bytes(_agent_pub))


def build_app() -> FastAPI:
    app = FastAPI()
    dep = require_rilavo_agent(
        audience=V,
        key_directory=_kit.key_directory,
        revocation_log=_kit.revocation_log,
    )

    @app.get("/data")
    def handler(request: Request, auth=Depends(dep)):
        return {"status": "ok"}

    return app


def test_accept():
    client = TestClient(build_app())
    cred = _kit.issue(
        principal="p", agent_public_key=_agent_pub,
        action_class="data.read", audience=V)
    sig, nonce = sign_request(_agent_priv, "GET", "/data", "data.read")
    r = client.get("/data", headers={
        "x-rilavo-credential": json.dumps(cred.fields),
        "x-rilavo-pop-signature": sig,
        "x-rilavo-request-nonce": nonce,
        "x-rilavo-action": "data.read",
    })
    assert r.status_code == 200


def test_no_credentials_401():
    client = TestClient(build_app())
    r = client.get("/data")
    assert r.status_code == 401


def test_malformed_credential_401():
    client = TestClient(build_app())
    r = client.get("/data", headers={"x-rilavo-credential": "{bad"})
    assert r.status_code == 401


def test_wrong_audience_401():
    client = TestClient(build_app())
    cred = _kit.issue(
        principal="p", agent="a", agent_public_key=_agent_pub,
        action_class="data.read",
        audience="verifier:someone-else.example")
    sig, nonce = sign_request(_agent_priv, "GET", "/data", "data.read")
    r = client.get("/data", headers={
        "x-rilavo-credential": json.dumps(cred.fields),
        "x-rilavo-pop-signature": sig,
        "x-rilavo-request-nonce": nonce,
        "x-rilavo-action": "data.read",
    })
    assert r.status_code == 401


def test_expired_401():
    client = TestClient(build_app())
    import time as time_mod

    past_iat = int(time_mod.time()) - 100000
    fields = {
        "iss": "rilavo:iss:test", "sub": "p", "agt": "a",
        "apk": "dGVzdA", "act": "data.read", "aud": V,
        "iat": past_iat, "exp": past_iat + 3600,
        "nonce": "old-n", "sig": "AAAA",
    }
    sig, nonce = sign_request(_agent_priv, "GET", "/data", "data.read")
    r = client.get("/data", headers={
        "x-rilavo-credential": json.dumps(fields),
        "x-rilavo-pop-signature": sig,
        "x-rilavo-request-nonce": nonce,
        "x-rilavo-action": "data.read",
    })
    assert r.status_code == 401
