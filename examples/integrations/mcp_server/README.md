# MCP Server with Rilavo Authentication

Build an MCP (Model Context Protocol) server that requires Rilavo credentials for tool access.

## Overview

This example demonstrates how to build an MCP server that uses Rilavo credentials for authentication and authorization. Each tool call requires a valid Rilavo credential with proof-of-possession.

## Installation

```bash
pip install mcp rilavo
```

## Server Implementation

```python
# mcp_server.py
import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from rilavo import verify_credential, NonceCache, CredentialFields
from rilavo.types import PopRequest, VerifyOptions, KeyDirectory, RevocationLog

# Configuration
AUDIENCE = "mcp.example.com"
ISSUER_DIRECTORY = {}  # Your issuer directory
REVOCATION_LOG = {"isRevoked": lambda _: False}
NONCE_CACHE = NonceCache()

app = Server("rilavo-mcp-server")

# In-memory credential store (use Redis in production)
active_credentials: Dict[str, CredentialFields] = {}

# Tool definitions
TOOLS = [
    Tool(
        name="read_data",
        description="Read data from the database",
        inputSchema={
            "type": "object",
            "properties": {
                "resource_id": {"type": "string", "description": "Resource ID to read"}
            },
            "required": ["resource_id"]
        }
    ),
    Tool(
        name="write_data",
        description="Write data to the database",
        inputSchema={
            "type": "object",
            "properties": {
                "resource_id": {"type": "string", "description": "Resource ID to write"},
                "data": {"type": "object", "description": "Data to write"}
            },
            "required": ["resource_id", "data"]
        }
    ),
]

@app.list_tools()
async def list_tools() -> List[Tool]:
    return TOOLS

async def verify_mcp_credential(credential_b64url: str, pop: dict) -> CredentialFields:
    """Verify a Rilavo credential and return the parsed fields."""
    # Decode credential
    try:
        import base64, json
        padding = '=' * (-len(credential_b64url) % 4)
        decoded = base64.urlsafe_b64decode(credential_b64url + padding)
        credential = json.loads(decoded)
    except Exception:
        raise ValueError("malformed_credential")

    # Build PoP request
    pop_request = PopRequest(
        method=pop.get("method", "POST"),
        path=pop.get("path", "/mcp"),
        requestedAction=pop.get("action", "mcp.tool.call"),
        signature=pop.get("signature", ""),
        requestNonce=pop.get("nonce", ""),
    )

    # Verify
    opts = VerifyOptions(
        issuer_directory=ISSUER_DIRECTORY,
        revocation_log=REVOCATION_LOG,
        nonce_cache=NONCE_CACHE,
        verifier_audience=AUDIENCE,
    )

    result = verify_credential(credential, pop_request, opts)
    if not result.accepted:
        raise ValueError(result.reason_code)

    return credential

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    # In a real implementation, you'd get the credential from the request context
    # For this example, we'll simulate getting it from environment
    credential_b64url = getattr(call_tool, "_current_credential", None)
    pop = getattr(call_tool, "_current_pop", {})

    if not credential_b64url:
        return [TextContent(type="text", text="Error: No credential provided")]

    try:
        credential = await verify_mcp_credential(credential_b64url, pop)
    except ValueError as e:
        return [TextContent(type="text", text=f"Authentication failed: {e}")]

    # Check if credential has required action
    allowed_actions = credential.get("act", "")
    if name == "write_data" and "data.write" not in allowed_actions:
        return [TextContent(type="text", text="Error: Insufficient permissions for write")]

    # Execute tool
    if name == "read_data":
        resource_id = arguments.get("resource_id")
        # Simulate reading data
        return [TextContent(type="text", text=f"Data for {resource_id}: {{'key': 'value'}}")]

    elif name == "write_data":
        resource_id = arguments.get("resource_id")
        data = arguments.get("data")
        # Simulate writing data
        return [TextContent(type="text", text=f"Written to {resource_id}: {data}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]

# Middleware to extract credentials from request
async def extract_credential(request) -> tuple:
    """Extract credential and PoP from request headers."""
    # In a real implementation, this would come from the MCP transport
    # For stdio transport, you'd use a custom transport
    credential = request.headers.get("x-rilavo-credential")
    pop = {
        "method": request.headers.get("x-rilavo-method", "POST"),
        "path": request.headers.get("x-rilavo-path", "/mcp"),
        "action": request.headers.get("x-rilavo-action", "mcp.tool.call"),
        "signature": request.headers.get("x-rilavo-pop-signature"),
        "nonce": request.headers.get("x-rilavo-request-nonce"),
    }
    return credential, pop

if __name__ == "__main__":
    # Run with stdio transport
    from mcp.server.stdio import stdio_server
    asyncio.run(stdio_server(app))
```

## Client Implementation

```python
# mcp_client.py
import asyncio
import json
import base64
from mcp.client.stdio import stdio_client
from mcp.types import Tool
from rilavo import issue_credential, pop_request_payload, b64url_encode
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

async def call_mcp_tool():
    # Load agent private key
    agent_priv = Ed25519PrivateKey.from_private_bytes(agent_seed)

    # Get credential from issuer
    credential = get_credential_from_issuer()

    # Create PoP for the tool call
    nonce = "mcp-nonce-" + str(int(time.time()))
    pop_payload = pop_request_payload("POST", "/mcp", "mcp.tool.call", nonce)
    signature = agent_priv.sign(pop_payload)
    signature_b64url = b64url_encode(signature)

    # Prepare headers
    headers = {
        "x-rilavo-credential": credential,
        "x-rilavo-method": "POST",
        "x-rilavo-path": "/mcp",
        "x-rilavo-action": "mcp.tool.call",
        "x-rilavo-pop-signature": signature_b64url,
        "x-rilavo-request-nonce": nonce,
    }

    # Connect to MCP server
    async with stdio_client(["python", "mcp_server.py"]) as (read, write):
        async with Client(read, write) as client:
            # List tools
            tools = await client.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            # Call tool with credential headers
            result = await client.call_tool(
                "read_data",
                {"resource_id": "resource-123"},
                metadata=headers  # Pass credential headers
            )
            print("Result:", result)

if __name__ == "__main__":
    asyncio.run(call_mcp_tool())
```

## Transport Options

### stdio Transport (Development)
```bash
python mcp_server.py
```

### HTTP Transport (Production)
```python
from mcp.server.http import create_http_server
from fastapi import FastAPI

app = FastAPI()
# ... add MCP routes
```

## Credential Requirements

For MCP servers, credentials should include:
- `act`: "mcp.tool.call" or specific tool action
- `aud`: "mcp.example.com" (your MCP server audience)
- `dlg`: 0 (no delegation for tool calls)

## Security Considerations

1. **Credential Validation**: Always verify credentials on each tool call
2. **Nonce Management**: Use unique nonces per tool call
3. **Action Scoping**: Check `act` field in credential matches tool
4. **Rate Limiting**: Implement per-credential rate limiting
5. **Audit Logging**: Log all tool calls with credential info

## Running the Server

```bash
# Development
python mcp_server.py

# With custom transport
python mcp_server.py --transport http --port 8000
```

## Client Authentication Flow

1. Agent obtains credential from issuer
2. Agent connects to MCP server
3. For each tool call:
   a. Generate unique nonce
   b. Create PoP signature
   c. Include credential and PoP headers
   d. Call tool
4. Server verifies credential and PoP
5. Server executes tool if authorized
