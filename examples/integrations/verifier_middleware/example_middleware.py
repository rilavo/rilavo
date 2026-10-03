"""Minimal verifier middleware — framework-agnostic (P-18 first surface).

`authenticate_request(headers) -> AuthResult` works with ANY framework: it
takes a plain headers dict and returns the adapter's accept/reject verdict
including WHICH mechanism authenticated. WSGI and ASGI adapters below show
the two-line bridge from real frameworks.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "rilavo-protocol" / "src"))

from rilavo.compat import authenticate                    # noqa: E402
from rilavo.credential import Credential                  # noqa: E402
from rilavo.keys import KeyDirectory                      # noqa: E402
from rilavo.pop import Request, sign_request             # noqa: E402
from rilavo.revocation import RevocationLog               # noqa: E402
from rilavo.testing import offline_test_kit, local_test_agent  # noqa: E402
from rilavo.verifier import NonceCache                    # noqa: E402

VERIFIER_ID = "verifier:middleware-demo.example"


class VerifierMiddleware:
    """Holds YOUR verifier state (key directory, revocation cache, ONE nonce
    cache per process) and authenticates requests by dispatching on what they
    carry: an OAuth bearer token or a Rilavo credential."""

    def __init__(self, bearer_validator=None):
        kit = offline_test_kit()          # demo stand-in for a fetched key
        self.kit = kit
        self.nonces = NonceCache()
        self.bearer_validator = bearer_validator

    def authenticate_headers(self, headers: dict, credential_json: str | None,
                             pop: dict | None) -> dict:
        credential = None
        pop_request = None
        if credential_json:
            import json as _json
            credential = __import__(
                "rilavo.credential", fromlist=["Credential"]).Credential(
                    fields=_json.loads(credential_json))
        if pop:
            pop_request = Request(pop["method"], pop["path"],
                                  pop["requested_action"], pop["signature"],
                                  pop["request_nonce"])
        result = authenticate(
            bearer_token=headers.get("Authorization", "").removeprefix("Bearer ")
            or None,
            bearer_validator=self.bearer_validator,
            credential=credential, pop_request=pop_request,
            verifier_id=VERIFIER_ID, key_directory=self.kit.key_directory,
            revocation_log=self.kit.revocation_log, nonces=self.nonces)
        return {"authenticated": result.authenticated,
                "mechanism": result.mechanism,
                "reason_code": result.reason_code}


# --- WSGI adapter sketch -----------------------------------------------------
def wsgi_app(environ, start_response, middleware: VerifierMiddleware):
    """Generic WSGI bridge: headers from environ; body/params app-specific."""
    headers = {k.title(): v for k, v in environ.items() if k.startswith("HTTP_")}
    outcome = middleware.authenticate_headers(headers, None, None)
    status = "200 OK" if outcome["authenticated"] else "401 Unauthorized"
    body = json_dumps(outcome).encode()
    start_response(status, [("Content-Type", "application/json"),
                            ("Content-Length", str(len(body)))])
    return [body]


def json_dumps(obj) -> str:
    import json
    return json.dumps(obj)


# --- ASGI adapter sketch -----------------------------------------------------
async def asgi_app(scope, receive, send, middleware: VerifierMiddleware):
    """Generic ASGI bridge (http scope only in this sketch)."""
    headers = {k.decode().title(): v.decode()
               for k, v in scope.get("headers", [])}
    outcome = middleware.authenticate_headers(headers, None, None)
    body = json_dumps(outcome).encode()
    await send({"type": "http.response.start", "status":
                200 if outcome["authenticated"] else 401,
                "headers": [(b"content-type", b"application/json")]})
    await send({"type": "http.response.body", "body": body})


def do_issue_demo(issuer, pub):
    from rilavo.api import do_issue
    return do_issue(issuer, principal="demo-principal", agent="agt_mw",
                    agent_public_key=pub, action_class="data.read",
                    audience=VERIFIER_ID)


if __name__ == "__main__":
    mw = VerifierMiddleware(bearer_validator=lambda t: {"sub": "legacy"} if t == "ok" else None)

    # OAuth path:
    print(mw.authenticate_headers({"Authorization": "Bearer ok"}, None, None))
    # Rilavo path:
    priv, pub = local_test_agent()
    cred = do_issue_demo(mw.kit.issuer, pub)
    sig, nonce = sign_request(priv, "POST", "/resource", "data.read")
    print(mw.authenticate_headers({}, cred.to_json(),
                                  {"method": "POST", "path": "/resource",
                                   "requested_action": "data.read",
                                   "signature": sig, "request_nonce": nonce}))

