"""FastAPI dependency factory for Rilavo agent credential verification."""

from __future__ import annotations

from typing import Callable

from fastapi import HTTPException, Request

from .middleware import _BaseMiddleware


def require_rilavo_agent(
    audience: str,
    key_directory,
    revocation_log=None,
) -> Callable:
    """Returns a FastAPI dependency that gates requests on credential checks."""
    base = _BaseMiddleware(
        audience=audience,
        key_directory=key_directory,
        revocation_log=revocation_log,
    )

    def dependency(request: Request) -> dict:
        cred_raw = request.headers.get("x-rilavo-credential", "")
        sig = request.headers.get("x-rilavo-pop-signature", "")
        nonce = request.headers.get("x-rilavo-request-nonce", "")
        act = request.headers.get("x-rilavo-action", "")
        method = request.method
        path = request.url.path

        ok, reason = base.verify_from_headers(
            {
                "x-rilavo-credential": cred_raw,
                "x-rilavo-pop-signature": sig,
                "x-rilavo-request-nonce": nonce,
                "x-rilavo-action": act,
            },
            method,
            path,
        )
        if not ok:
            raise HTTPException(status_code=401, detail={"error": reason})
        return {"accepted": True}

    return dependency
