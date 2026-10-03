"""P-18 middleware tests: WSGI and ASGI flavors, identical semantics."""

from __future__ import annotations

import json

from rilavo.middleware import RilavoASGIMiddleware, RilavoWSGIMiddleware
from rilavo.testing import offline_test_kit, local_test_agent
from rilavo.pop import sign_request

V = "verifier:middleware-test.example"


class Harness:
    def __init__(self):
        self.kit = offline_test_kit()
        self.agent_priv, self.agent_pub = local_test_agent()
        from rilavo.keys import b64url_encode, public_key_bytes
        from rilavo.keys import b64url_encode as b64e
        self.agent_pub_b64 = b64e(public_key_bytes(self.agent_pub))
        self.cred_fields = None

    def issue(self):
        cred = self.kit.issue(
            principal="p",
            agent_public_key=self.agent_pub,
            action_class="data.read",
            audience=V)
        self.cred_fields = dict(cred.fields)
        return cred.fields

    def pop(self, method="POST", path="/data", act="data.read", nonce="n1"):
        sig, n = sign_request(self.agent_priv, method, path, act)
        return {
            "x-rilavo-pop-signature": sig,
            "x-rilavo-request-nonce": n,
            "x-rilavo-action": act,
        }

    def wsgi_mw(self):
        def app(environ, sr):
            sr("200 OK", [("Content-Type", "text/plain")])
            return b"APP_OK"
        return RilavoWSGIMiddleware(
            app,
            audience=V,
            key_directory=self.kit.key_directory,
            revocation_log=self.kit.revocation_log)

    def asgi_mw(self):
        return RilavoASGIMiddleware(
            _asgi_app_ok,
            audience=V,
            key_directory=self.kit.key_directory,
            revocation_log=self.kit.revocation_log)

    def env(self, headers=None, method="GET", path="/data"):
        e = {"REQUEST_METHOD": method, "PATH_INFO": path}
        for k, v in (headers or {}).items():
            e["HTTP_" + k.upper().replace("-", "_")] = v
        return e


async def _asgi_app_ok(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok"})


def _run_wsgi(mw, environ):
    captured = {}
    def sr(status, headers):
        captured["status"] = status
    body = mw(environ, sr)
    captured["body"] = body if isinstance(body, bytes) else b"".join(body)
    return captured


def _run_asgi(mw, scope):
    import asyncio
    sent = []
    async def receive():
        return {"type": "http.request"}
    async def send(msg):
        sent.append(msg)
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(mw(scope, receive, send))
    finally:
        loop.close()
    return sent


def test_wsgi_accept():
    h = Harness()
    mw = h.wsgi_mw()
    cred_fields = h.issue()
    sig, nonce = __import__("rilavo.pop", fromlist=["sign_request"]).sign_request(
        h.agent_priv, "GET", "/data", "data.read")
    hdrs = {
        "x-rilavo-credential": json.dumps(cred_fields),
        "x-rilavo-pop-signature": sig,
        "x-rilavo-request-nonce": nonce,
        "x-rilavo-action": "data.read",
    }
    r = _run_wsgi(mw, h.env(hdrs))
    assert r["status"] == "200 OK"
    assert r["body"] == b"APP_OK"


def test_wsgi_no_credentials():
    h = Harness()
    mw = h.wsgi_mw()
    r = _run_wsgi(mw, h.env())
    assert "401" in r["status"]
    assert json.loads(r["body"])["error"] == "no_credentials"


def test_wsgi_malformed_credential():
    h = Harness()
    mw = h.wsgi_mw()
    r = _run_wsgi(mw, h.env({"x-rilavo-credential": "{not-json}"}))
    assert "401" in r["status"]
    assert json.loads(r["body"])["error"] == "malformed_credential"


def test_asgi_no_credentials_rejected():
    h = Harness()
    mw = h.asgi_mw()
    scope = {"type": "http", "method": "GET", "path": "/x", "headers": []}
    sent = _run_asgi(mw, scope)
    assert sent[0]["status"] == 401


def test_asgi_accept():
    h = Harness()
    mw = h.asgi_mw()
    cred = h.issue()
    sig, nonce = __import__("rilavo.pop", fromlist=["sign_request"]).sign_request(
        h.agent_priv, "GET", "/data", "data.read")
    scope = {
        "type": "http", "method": "GET", "path": "/data",
        "headers": [
            [b"x-rilavo-credential", json.dumps(cred).encode()],
            [b"x-rilavo-pop-signature", sig.encode()],
            [b"x-rilavo-request-nonce", nonce.encode()],
            [b"x-rilavo-action", b"data.read"],
        ],
    }
    sent = _run_asgi(mw, scope)
    assert sent[0]["status"] == 200
