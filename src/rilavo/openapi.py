"""OpenAPI 3.1 specification generator for Rilavo service."""

from __future__ import annotations

import json
from typing import Any
from datetime import datetime

from .models.issue import (
    IssueCredentialRequest,
    IssueCredentialResponse,
    BatchIssueRequest,
    BatchIssueResponse,
)
from .models.verify import (
    VerifyRequest,
    VerifyResponse,
)
from .models.directory import (
    DirectoryEntry,
    DirectoryResponse,
)
from .models.errors import (
    ErrorResponse,
)
from .models.discovery import (
    DiscoveryResponse,
)


def generate_openapi_spec(
    version: str = "0.1.0",
    title: str = "Rilavo API",
    description: str = "Rilavo Protocol HTTP API - Stateless agent authorization credentials",
    server_url: str = "http://localhost:8090",
) -> dict[str, Any]:
    """Generate complete OpenAPI 3.1 specification."""

    return {
        "openapi": "3.1.0",
        "info": {
            "title": title,
            "version": version,
            "description": description,
            "contact": {
                "name": "Rilavo Contributors",
                "url": "https://github.com/rilavo/rilavo",
            },
            "license": {
                "name": "Apache-2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
            },
        },
        "servers": [
            {
                "url": server_url,
                "description": "Local development server",
            },
            {
                "url": "https://api.rilavo.org",
                "description": "Production server (example)",
            },
        ],
        "paths": _build_paths(),
        "components": _build_components(),
        "tags": [
            {"name": "Credentials", "description": "Credential issuance and management"},
            {"name": "Verification", "description": "Credential verification"},
            {"name": "Directory", "description": "Key directory operations"},
            {"name": "Discovery", "description": "Well-known discovery"},
            {"name": "Health", "description": "Health and monitoring"},
        ],
    }


def _build_paths() -> dict:
    """Build all API paths."""
    return {
        "/issue": {
            "post": {
                "tags": ["Credentials"],
                "summary": "Issue a new credential",
                "description": "Issues a new Rilavo credential for an agent. The credential is signed by the issuer and includes all authorization metadata.",
                "operationId": "issueCredential",
                "tags": ["Credentials"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/IssueCredentialRequest"},
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "Credential issued successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/IssueCredentialResponse"},
                            },
                        },
                    },
                    "400": {
                        "description": "Invalid request",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            },
                        },
                    },
                    "401": {
                        "description": "Unauthorized (invalid issuer key)",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            },
                        },
                    },
                    "500": {
                        "description": "Internal server error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            },
                        },
                    },
                },
            },
        },
        "/batch-issue": {
            "post": {
                "tags": ["Credentials"],
                "summary": "Issue multiple credentials in batch",
                "description": "Issues multiple credentials in a single request. Each credential is independently verifiable.",
                "operationId": "batchIssueCredentials",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/BatchIssueRequest"},
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "Batch issuance completed",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/BatchIssueResponse"},
                            },
                        },
                    },
                    "400": {
                        "description": "Invalid request",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            },
                        },
                    },
                },
            },
        },
        "/verify": {
            "post": {
                "tags": ["Verification"],
                "summary": "Verify a credential with Proof-of-Possession",
                "description": "Verifies a Rilavo credential and its Proof-of-Possession. All verification gates are checked: version, expiry, audience, delegation, signature, replay, revocation, and PoP.",
                "operationId": "verifyCredential",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/VerifyRequest"},
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "Verification result",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/VerifyResponse"},
                            },
                        },
                    },
                    "400": {
                        "description": "Invalid request",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            },
                        },
                    },
                    "401": {
                        "description": "Verification failed",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            },
                        },
                    },
                },
            },
        },
        "/directory": {
            "get": {
                "tags": ["Directory"],
                "summary": "Get key directory",
                "description": "Returns the published key directory with issuer public keys.",
                "operationId": "getDirectory",
                "responses": {
                    "200": {
                        "description": "Key directory",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/DirectoryResponse"},
                            },
                        },
                    },
                },
            },
        },
        "/.well-known/rilavo": {
            "get": {
                "tags": ["Discovery"],
                "summary": "Well-known discovery",
                "description": "Returns the well-known discovery document for this verifier.",
                "operationId": "getDiscovery",
                "responses": {
                    "200": {
                        "description": "Discovery document",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/DiscoveryResponse"},
                            },
                        },
                    },
                },
            },
        },
        "/revoke": {
            "post": {
                "tags": ["Credentials"],
                "summary": "Revoke a credential",
                "description": "Revokes a credential by its nonce. The revocation is recorded in the revocation log.",
                "operationId": "revokeCredential",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "nonce": {"type": "string", "description": "Credential nonce to revoke"},
                                    "reason": {"type": "string", "description": "Revocation reason"},
                                },
                                "required": ["nonce"],
                            },
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "Revocation recorded",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RevokeResponse"},
                            },
                        },
                    },
                    "400": {
                        "description": "Invalid request",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                            },
                        },
                    },
                },
            },
        },
        "/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Health check",
                "description": "Returns service health status.",
                "operationId": "healthCheck",
                "responses": {
                    "200": {
                        "description": "Service is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "enum": ["ok"]},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    }


def _build_components() -> dict:
    """Build OpenAPI components."""
    return {
        "schemas": {
            # Issue
            "IssueCredentialRequest": _schema_ref("IssueCredentialRequest"),
            "IssueCredentialResponse": _schema_ref("IssueCredentialResponse"),
            "BatchIssueRequest": _schema_ref("BatchIssueRequest"),
            "BatchIssueResponse": _schema_ref("BatchIssueResponse"),
            "CredentialFields": _schema_ref("CredentialFields"),
            "BatchIssueStatus": _schema_ref("BatchIssueStatus"),
            # Verify
            "VerifyRequest": _schema_ref("VerifyRequest"),
            "VerifyResponse": _schema_ref("VerifyResponse"),
            # Directory
            "DirectoryEntry": _schema_ref("DirectoryEntry"),
            "DirectoryResponse": _schema_ref("DirectoryResponse"),
            # Discovery
            "DiscoveryResponse": _schema_ref("DiscoveryResponse"),
            # Errors
            "ErrorResponse": _schema_ref("ErrorResponse"),
            "ErrorDetail": _schema_ref("ErrorDetail"),
            # Discovery
            "DiscoveryResponse": _schema_ref("DiscoveryResponse"),
            # Revoke
            "RevokeRequest": {
                "type": "object",
                "properties": {
                    "nonce": {"type": "string", "description": "Credential nonce to revoke"},
                    "reason": {"type": "string", "description": "Revocation reason"},
                },
                "required": ["nonce"],
            },
            "RevokeResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "nonce": {"type": "string"},
                },
                "required": ["success", "nonce"],
            },
            # Health
            "HealthResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["ok"]},
                },
            },
        },
        "securitySchemes": {
            "CredentialHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "x-rilavo-credential",
                "description": "Base64url encoded Rilavo credential",
            },
            "PoPSignature": {
                "type": "apiKey",
                "in": "header",
                "name": "x-rilavo-pop-signature",
                "description": "Proof-of-Possession signature (base64url)",
            },
            "PoPNonce": {
                "type": "apiKey",
                "in": "header",
                "name": "x-rilavo-request-nonce",
                "description": "Request nonce (base64url)",
            },
            "PoPAction": {
                "type": "apiKey",
                "in": "header",
                "name": "x-rilavo-action",
                "description": "Requested action class",
            },
        },
    }


def _schema_ref(name: str) -> dict:
    """Create a schema reference."""
    return {"$ref": f"#/components/schemas/{name}"}


def generate_openapi_json(
    version: str = "0.1.0",
    server_url: str = "http://localhost:8090",
) -> str:
    """Generate OpenAPI spec as JSON string."""
    spec = generate_openapi_spec(version=version, server_url=server_url)
    return json.dumps(spec, indent=2)


if __name__ == "__main__":
    # Generate and print spec
    import sys
    spec = generate_openapi_spec()
    print(json.dumps(spec, indent=2))
