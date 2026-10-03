"""Pydantic models for credential verification."""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    """Request to verify a credential (from HTTP headers)."""

    x_rilavo_credential: str = Field(
        description="Base64url encoded credential JSON",
        min_length=1,
    )
    x_rilavo_pop_signature: str = Field(
        description="PoP signature (base64url)",
        min_length=1,
    )
    x_rilavo_request_nonce: str = Field(
        description="Request nonce (base64url)",
        min_length=1,
    )
    x_rilavo_action: str = Field(
        description="Requested action class",
        min_length=1,
    )
    method: str = Field(
        description="HTTP method",
        pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$",
    )
    path: str = Field(
        description="Request path",
        min_length=1,
    )


class VerifyResponse(BaseModel):
    """Response from credential verification."""

    accepted: bool = Field(description="Whether verification succeeded")
    reason_code: Optional[str] = Field(
        default=None,
        description="Rejection reason code (null if accepted)",
    )
    principal: Optional[str] = Field(
        default=None,
        description="Credential principal (if accepted)",
    )
    action_class: Optional[str] = Field(
        default=None,
        description="Credential action class (if accepted)",
    )
    agent: Optional[str] = Field(
        default=None,
        description="Credential agent (if accepted)",
    )
