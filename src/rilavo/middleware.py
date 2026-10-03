"""Framework-agnostic verifier middleware (P-18 first surface).

WSGI and ASGI middleware classes that gate incoming requests on Rilavo
credential verification. Both flavors share identical semantics:

  - fail-closed: missing/malformed/invalid credential -> 401 + reason code
  - pass through on accept -> wrapped app handles the request normally
  - one nonce cache per middleware instance (replay defense)
  - issuer keys cached from the caller-supplied directory

Zero protocol change: this module only calls do_verify / authenticate; it
never modifies credential fields or verifier logic.
"""

from __future__ import annotations

import json
import threading
from typing import Any, Callable

from .api import VerifyResult, do_verify
from .compat import authenticate
from .credential import Credential
from .errors import VerificationError
from .keys import KeyDirectory
from .pop import Request as PopRequest
from .revocation import RevocationLog
from .verifier import NonceCache

CREDENTIAL_HEADER = "x-rilavo-credential"
POP_SIGNATURE_HEADER = "x-rilavo-pop-signature"
REQUEST_NONCE_HEADER = "x-rilavo-request-nonce"
ACTION_HEADER = "x-rilavo-action"


def _headers_lower(wsgi_environ: dict) -> dict:
    """Convert WSGI environ HTTP_* keys to lowercase header names."""
    out = {}
    for k, v in wsgi_environ.items():
        if k.startswith("HTTP_"):
            out[k[5:].replace("_", "-").lower()] = v
    return out


class _BaseMiddleware:
    """Shared verification state and logic for both WSGI and ASGI."""

    def __init__(self, *, audience: str,
                 key_directory: KeyDirectory,
                 revocation_log: RevocationLog | None = None,
                 nonce_cache: NonceCache | None = None) -> None:
        self.audience = audience
        self.directory = key_directory
        self.revocations = revocation_log if revocation_log is not None else RevocationLog()
        self.nonces = nonce_cache if nonce_cache is not None else NonceCache()

    def verify_from_headers(self, headers: dict,
                            method: str, path: str,
                            ) -> tuple[bool, str | None]:
        """Extract credential+PoP from headers, verify, return (ok, reason)."""
        cred_raw = headers.get(CREDENTIAL_HEADER)
        if not cred_raw:
            return False, "no_credentials"
        try:
            fields = json.loads(cred_raw)
            if not isinstance(fields, dict):
                return False, "malformed_credential"
        except (json.JSONDecodeError, ValueError):
            return False, "malformed_credential"

        sig = headers.get(POP_SIGNATURE_HEADER, "")
        nonce = headers.get(REQUEST_NONCE_HEADER, "")
        act = headers.get(ACTION_HEADER, "")

        try:
            result: VerifyResult = do_verify(
                verifier_id=self.audience,
                credential=Credential(fields=fields),
                request=PopRequest(method=method, path=path,
                                   requested_action=act,
                                   signature=sig, request_nonce=nonce),
                key_directory=self.directory,
                revocation_log=self.revocations,
                nonces=self.nonces,
            )
        except VerificationError as exc:
            return False, exc.reason_code
        if result.accepted:
            return True, None
        return False, result.reason_code


# --------------------------------------------------------------------------
# WSGI middleware
# --------------------------------------------------------------------------

class RilavoWSGIMiddleware:
    """WSGI middleware: gates requests on Rilavo credential verification.

    Usage:
        app = RilavoWSGIMiddleware(inner_app, audience="...", key_directory=dir)
    """

    def __init__(self, app: Callable, *, audience: str,
                 key_directory: KeyDirectory,
                 revocation_log: RevocationLog | None = None,
                 nonce_cache: NonceCache | None = None) -> None:
        self.app = app
        self._base = _BaseMiddleware(
            audience=audience, key_directory=key_directory,
            revocation_log=revocation_log, nonce_cache=nonce_cache)

    def __call__(self, environ: dict, start_response: Callable):
        headers = _headers_lower(environ)
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/")
        try:
            ok, reason = self._base.verify_from_headers(headers, method, path)
        except Exception:
            ok, reason = False, "internal_verification_error"
        if not ok:
            body = json.dumps({"error": reason}).encode()
            start_response("401 Unauthorized",
                           [("Content-Type", "application/json"),
                            ("Content-Length", str(len(body)))])
            return [body]
        return self.app(environ, start_response)


import json as _json_module
json = _json_module


# --------------------------------------------------------------------------
# ASGI middleware
# --------------------------------------------------------------------------

class RilavoASGIMiddleware:
    """ASGI middleware: identical semantics to RilavoWSGIMiddleware.

    Usage:
        app = RilavoASGIMiddleware(inner_app, audience="...", key_directory=dir)
    """

    def __init__(self, app: Callable, *, audience: str,
                 key_directory: KeyDirectory,
                 revocation_log: RevocationLog | None = None,
                 nonce_cache: NonceCache | None = None) -> None:
        self.app = app
        self._base = _BaseMiddleware(
            audience=audience, key_directory=key_directory,
            revocation_log=revocation_log, nonce_cache=nonce_cache)

    async def __call__(self, scope: dict, receive: Callable,
                       send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = {}
        for k, v in scope.get("headers", []):
            name = k.decode().lower()
            val = v.decode()
            # combine duplicate headers (last wins, matching HTTP spec)
            headers[name] = val
        method = scope.get("method", "GET")
        path = scope.get("path", "/")
        try:
            ok, reason = self._base.verify_from_headers(headers, method, path)
        except Exception:
            ok, reason = False, "internal_verification_error"
        if ok:
            await self.app(scope, receive, send)
            return
        body = json.dumps({"error": reason}).encode()
        await send({"type": "http.response.start",
                    "status": 401,
                    "headers": [[b"content-type", b"application/json"],
                                [b"content-length",
                                 str(len(body)).encode()]]})
        await send({"type": "http.response.body", "body": body})
