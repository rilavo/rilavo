# FastAPI/Starlette Verifier Middleware Example

Complete FastAPI integration using `rilavo.middleware.VerifierMiddleware` for credential verification.

## Quick Start

```bash
cd examples/verifier_middleware/fastapi
pip install -r requirements.txt
python main.py
```

Server runs on `http://localhost:8000`.

## Usage

### 1. Install Dependencies

```bash
pip install rilavo fastapi uvicorn
```

### 2. Create Verifier Middleware

```python
# middleware/rilavo.py
from typing import Optional, List
from fastapi import Request, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from rilavo import verify_credential, NonceCache, CredentialFields
from rilavo.types import PopRequest, VerifyOptions, KeyDirectory, RevocationLog

class RilavoConfig:
    def __init__(
        self,
        audience: str,
        header_name: str = "x-rilavo-credential",
        public_paths: List[str] = None,
        issuer_directory: KeyDirectory = None,
        revocation_log: RevocationLog = None,
        nonce_cache: NonceCache = None,
    ):
        self.audience = audience
        self.header_name = header_name
        self.public_paths = public_paths or ["/health", "/public"]
        self.issuer_directory = issuer_directory
        self.revocation_log = revocation_log
        self.nonce_cache = nonce_cache

class RilavoMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config: RilavoConfig):
        super().__init__(app)
        self.config = config

    def is_public(self, path: str) -> bool:
        for p in self.config.public_paths:
            if path == p or path.startswith(p + "/"):
                return True
        return False

    async def dispatch(self, request: Request, call_next):
        # Skip public paths
        if self.is_public(request.url.path):
            return await call_next(request)

        # Get credential from header
        credential_b64url = request.headers.get("x-rilavo-credential")
        if not credential_b64url:
            return JSONResponse(
                status_code=401,
                content={"error": "no_credentials"}
            )

        # Decode credential
        try:
            import base64, json
            padding = '=' * (-len(credential_b64url) % 4)
            decoded = base64.urlsafe_b64decode(credential_b64url + padding)
            credential = json.loads(decoded)
        except Exception:
            return JSONResponse(
                status_code=401,
                content={"error": "malformed_credential"}
            )

        # Build PoP request from headers
        pop = {
            "method": request.method,
            "path": request.url.path,
            "requestedAction": request.headers.get("x-rilavo-action", "unspecified"),
            "signature": request.headers.get("x-rilavo-pop-signature", ""),
            "requestNonce": request.headers.get("x-rilavo-request-nonce", ""),
        }

        # Verify credential
        try:
            from rilavo import verify_credential, NonceCache

            opts = {
                "issuer_directory": self.config.issuer_directory or {
                    "lookup": lambda _: None,
                    "unreachable": False,
                },
                "revocation_log": self.config.revocation_log or {"isRevoked": lambda _: False},
                "nonce_cache": self.config.nonce_cache or NonceCache(),
                "verifier_audience": self.config.audience,
            }

            result = verify_credential(credential, pop, opts)

            if not result["accepted"]:
                return JSONResponse(
                    status_code=401,
                    content={"error": result["reasonCode"]}
                )
        except Exception as e:
            return JSONResponse(
                status_code=401,
                content={"error": "verification_failed"}
            )

        # Credential verified, attach to request state
        request.state.rilavo_credential = credential

        return await call_next(request)

# Dependency for accessing credential in routes
async def get_credential(request: Request):
    if not hasattr(request.state, "rilavo_credential"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.rilavo_credential
```

### 3. Usage in Routes

```python
# main.py
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware

from middleware.rilavo import RilavoMiddleware, RilavoConfig

app = FastAPI(title="My Rilavo Protected API")

# Configure Rilavo
rilavo_config = RilavoConfig(
    audience="myapp.example.com",
    public_paths=["/health", "/docs", "/openapi.json"],
    # issuer_directory=...,  # Add your issuer directory
    # revocation_log=...,    # Add revocation log
)

# Add middleware
app.add_middleware(RilavoMiddleware, config=rilavo_config)

# Public routes
@app.get("/health")
async def health():
    return {"status": "ok"}

# Protected routes
@app.get("/api/data")
async def get_data(credential: dict = Depends(get_credential)):
    return {
        "data": "sensitive data",
        "user": credential.get("sub")
    }

@app.post("/api/action")
async def perform_action(request: Request, credential: dict = Depends(get_credential)):
    # The agent must include PoP headers:
    # x-rilavo-method: POST
    # x-rilavo-path: /api/action
    # x-rilavo-action: data.write
    # x-rilavo-pop-signature: <base64url signature>
    # x-rilavo-request-nonce: <unique nonce>
    return {"success": True}
```

### 4. Issuer Directory

```python
class MyIssuerDirectory:
    def lookup(self, issuer_id: str):
        # Fetch from issuer's /directory endpoint
        # Cache the results
        known_issuers = {
            "did:example:issuer1": {
                "issuerId": "did:example:issuer1",
                "publicKeyPem": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEA...\n-----END PUBLIC KEY-----",
                "validUntil": 9999999999,
            }
        }
        return known_issuers.get(issuer_id)

    @property
    def unreachable(self):
        return False
```

## Client-Side: Agent Making Requests

```python
import httpx
from rilavo import issue_credential, pop_request_payload, b64url_encode
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import time

async def call_protected_api():
    # Load agent private key
    agent_priv = Ed25519PrivateKey.from_private_bytes(agent_seed)

    # Get credential from issuer
    credential = get_credential_from_issuer()

    # Create PoP
    nonce = "unique-nonce-" + str(int(time.time()))
    pop_payload = pop_request_payload("POST", "/api/action", "data.write", nonce)
    signature = agent_priv.sign(pop_payload)
    signature_b64url = b64url_encode(signature)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://myapp.example.com/api/action",
            json={"action": "write"},
            headers={
                "x-rilavo-credential": credential,
                "x-rilavo-method": "POST",
                "x-rilavo-path": "/api/action",
                "x-rilavo-action": "data.write",
                "x-rilavo-pop-signature": signature_b64url,
                "x-rilavo-request-nonce": nonce,
            }
        )

    return response.json()
```

## Production Considerations

1. **Issuer Directory**: Fetch from `https://{issuer}/.well-known/rilavo` and cache with TTL
2. **Revocation Log**: Use Redis with TTL matching credential expiry
3. **Nonce Cache**: Use Redis with sliding window expiration
4. **Rate Limiting**: Add rate limiting per credential/agent
5. **Logging**: Log verification results for audit trails
6. **Error Handling**: Distinguish between auth errors and server errors

## Running Tests

```bash
cd examples/verifier_middleware/fastapi
pip install -r requirements.txt
python -m pytest test_main.py -v
```
