"""
FastAPI/Starlette middleware for Rilavo credential verification.

Usage:
    pip install -r requirements.txt
    python main.py

    # Test with:
    curl -H "x-rilavo-credential: <cred>" \
         -H "x-rilavo-action: data.read" \
         -H "x-rilavo-pop-signature: <sig>" \
         -H "x-rilavo-request-nonce: <nonce>" \
         http://localhost:8000/protected/data
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from rilavo.compat import authenticate
from rilavo.api import do_issue
from rilavo.keys import KeyDirectory
from rilavo.pop import Request as PopRequest, sign_request
from rilavo.revocation import RevocationLog
from rilavo.verifier import NonceCache
from rilavo.testing import offline_test_kit, local_test_agent
from rilavo.credential import Credential
from cryptography.hazmat.primitives import serialization

# Configuration
VERIFIER_ID = "verifier:fastapi-example.com"

# Setup test keys (in production, load from secure storage)
kit = offline_test_kit()
issuer = kit.issuer
agent_priv, agent_pub = local_test_agent()

class VerifierMiddleware:
    """Holds verifier state and authenticates requests."""

    def __init__(self, bearer_validator=None):
        kit = offline_test_kit()
        self.kit = kit
        self.nonces = NonceCache()
        self.bearer_validator = bearer_validator

    def authenticate_headers(self, headers: dict, credential_json: str | None,
                             pop: dict | None) -> dict:
        credential = None
        pop_request = None
        if credential_json:
            import json as _json
            try:
                # Try to decode as base64url first
                import base64
                padded = credential_json + '=' * (-len(credential_json) % 4)
                cred_json = base64.urlsafe_b64decode(padded).decode()
                fields = _json.loads(cred_json)
            except Exception:
                # Fallback: try direct JSON
                try:
                    fields = _json.loads(credential_json)
                except Exception:
                    # Invalid credential format
                    return {"authenticated": False, "mechanism": None, "reason_code": "malformed_credential"}
            credential = Credential(fields=fields)
        if pop:
            pop_request = PopRequest(pop["method"], pop["path"],
                                  pop["requested_action"], pop["signature"],
                                  pop["request_nonce"])
        result = authenticate(
            bearer_token=headers.get("Authorization", "").removeprefix("Bearer ")
            or None,
            bearer_validator=self.bearer_validator,
            credential=credential, pop_request=pop_request,
            verifier_id=VERIFIER_ID, key_directory=self.kit.key_directory,
            revocation_log=self.kit.revocation_log, nonces=self.nonces)
        response = {"authenticated": result.authenticated,
                "mechanism": result.mechanism,
                "reason_code": result.reason_code}
        if credential is not None and result.authenticated:
            response["principal"] = credential.fields.get("sub")
            response["agent"] = credential.fields.get("agt")
            response["action_class"] = credential.fields.get("act")
        return response


# Create verifier middleware
verifier_middleware = VerifierMiddleware(bearer_validator=None)

# FastAPI app
app = FastAPI(title="Rilavo FastAPI Example", version="0.1.0")

# In-memory stores (use Redis/database in production)
nonce_cache = NonceCache()
revocation_log = RevocationLog()
issuer_directory = kit.key_directory


# Request/Response models
class IssueCredentialRequest(BaseModel):
    principal: str = "test-principal"
    agent: str = "test-agent"
    action_class: str = "data.read"


class SignPopRequest(BaseModel):
    method: str = "GET"
    path: str = "/protected/data"
    action: str = "data.read"


class CredentialResponse(BaseModel):
    credential: str  # base64url-encoded credential JSON


class PopResponse(BaseModel):
    method: str
    path: str
    action: str
    signature: str
    request_nonce: str


class VerifyResponse(BaseModel):
    authenticated: bool
    mechanism: Optional[str] = None
    reason_code: Optional[str] = None
    principal: Optional[str] = None
    agent: Optional[str] = None
    action_class: Optional[str] = None


# Exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


# Health check (public)
@app.get("/health")
async def health():
    return {"status": "ok", "verifier": VERIFIER_ID}


# Public info endpoint
@app.get("/public/info")
async def public_info():
    return {"public": True, "message": "No authentication required"}


# Admin: Issue test credential
@app.post("/admin/issue-test-credential", response_model=CredentialResponse)
async def issue_test_credential(req: IssueCredentialRequest):
    """Issue a test credential for development/testing."""
    cred = do_issue(
        issuer=issuer,
        principal=req.principal,
        agent=req.agent,
        agent_public_key=agent_pub,
        action_class=req.action_class,
        audience=VERIFIER_ID,
    )
    import json, base64
    cred_json = json.dumps(dict(cred.fields), separators=(',', ':'))
    cred_b64url = base64.urlsafe_b64encode(cred_json.encode()).decode().rstrip('=')
    return {"credential": cred_b64url}


# Admin: Sign PoP request
@app.post("/admin/sign-pop", response_model=PopResponse)
async def sign_pop(req: SignPopRequest):
    """Sign a proof-of-possession request for testing."""
    sig, nonce = sign_request(agent_priv, req.method, req.path, req.action)
    return {
        "method": req.method,
        "path": req.path,
        "action": req.action,
        "signature": sig,
        "request_nonce": nonce,
    }


# Protected endpoint - uses Rilavo verification
@app.get("/protected/data")
async def protected_data(request: Request):
    """Protected endpoint requiring valid Rilavo credential."""
    # Extract headers
    headers = dict(request.headers)
    credential_json = headers.get("x-rilavo-credential")
    pop_headers = {
        "method": request.method,
        "path": request.url.path,
        "requested_action": headers.get("x-rilavo-action", "unspecified.action"),
        "signature": headers.get("x-rilavo-pop-signature", ""),
        "request_nonce": headers.get("x-rilavo-request-nonce", ""),
    }

    # Verify using middleware
    result = verifier_middleware.authenticate_headers(
        headers=headers,
        credential_json=credential_json,
        pop=pop_headers if credential_json else None
    )

    if not result["authenticated"]:
        raise HTTPException(
            status_code=401,
            detail=result["reason_code"] or "unauthorized"
        )

    return {
        "data": "Sensitive data accessed successfully",
        "authenticated_as": {
            "principal": result.get("principal"),
            "agent": result.get("agent"),
            "action_class": result.get("action_class"),
        }
    }


# Alternative: Dependency injection style
async def verify_rilavo_credential(request: Request) -> Dict[str, Any]:
    """FastAPI dependency for Rilavo verification."""
    headers = dict(request.headers)
    credential_json = headers.get("x-rilavo-credential")
    pop_headers = {
        "method": request.method,
        "path": request.url.path,
        "requested_action": headers.get("x-rilavo-action", "unspecified.action"),
        "signature": headers.get("x-rilavo-pop-signature", ""),
        "request_nonce": headers.get("x-rilavo-request-nonce", ""),
    }

    result = verifier_middleware.authenticate_headers(
        headers=headers,
        credential_json=credential_json,
        pop=pop_headers if credential_json else None
    )

    if not result["authenticated"]:
        raise HTTPException(
            status_code=401,
            detail=result["reason_code"] or "unauthorized"
        )

    return result


@app.get("/protected/dependency-style")
async def protected_with_dependency(auth_result: Dict = Depends(verify_rilavo_credential)):
    """Protected endpoint using FastAPI dependency injection."""
    return {
        "data": "Accessed via dependency injection",
        "authenticated_as": {
            "principal": auth_result.get("principal"),
            "agent": auth_result.get("agent"),
            "action_class": auth_result.get("action_class"),
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
