"""Pydantic models for credential issuance."""

from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class IssueCredentialRequest(BaseModel):
    """Request to issue a new credential."""

    principal: Annotated[str, Field(
        description="Principal identifier (e.g., 'acme-corp:runner-04')",
        min_length=1,
        max_length=256,
    )]
    agent: Annotated[str, Field(
        description="Agent identifier (e.g., 'agent-runner-04')",
        min_length=1,
        max_length=256,
    )]
    agent_public_key_b64: Annotated[str, Field(
        description="Agent's Ed25519 public key (base64url encoded, no padding)",
        min_length=43,
        max_length=44,
    )]
    action_class: Annotated[str, Field(
        description="Exact action class (e.g., 'data.read')",
        min_length=1,
        max_length=128,
    )]
    audience: Annotated[str, Field(
        description="Audience identifier (e.g., 'verifier:api.example.com')",
        min_length=1,
        max_length=256,
    )]
    ttl_seconds: Annotated[int | None, Field(
        default=3600,
        ge=60,
        le=86400,
        description="Time-to-live in seconds (60-86400)",
    )] = 3600
    context: Annotated[str | None, Field(
        default=None,
        max_length=1024,
        description="Optional context data",
    )] = None

    @field_validator("agent_public_key_b64")
    @classmethod
    def validate_agent_public_key(cls, v: str) -> str:
        """Validate base64url encoded Ed25519 public key."""
        import base64
        try:
            # Add padding if needed
            padded = v + '=' * ((4 - len(v) % 4) % 4)
            decoded = base64.urlsafe_b64decode(padded)
            if len(decoded) != 32:
                raise ValueError("Ed25519 public key must be 32 bytes")
        except Exception as e:
            raise ValueError(f"Invalid base64url public key: {e}")
        return v


class CredentialFields(BaseModel):
    """Credential fields as returned by issuance."""

    iss: str = Field(description="Issuer fingerprint")
    sub: str = Field(description="Principal identifier")
    agt: str = Field(description="Agent identifier")
    apk: str = Field(description="Agent public key (base64url)")
    act: str = Field(description="Action class")
    aud: str = Field(description="Audience")
    iat: int = Field(description="Issued at (Unix timestamp)")
    exp: int = Field(description="Expires at (Unix timestamp)")
    nonce: str = Field(description="Issuance nonce")
    sig: str = Field(description="Issuer signature (base64url)")
    ver: int | None = Field(default=None, description="Credential version (v0 omitted)")


class IssueCredentialResponse(BaseModel):
    """Response from credential issuance."""

    fields: CredentialFields = Field(description="Issued credential fields")


class BatchIssueRequest(BaseModel):
    """Request to issue multiple credentials."""

    requests: list[IssueCredentialRequest] = Field(
        min_length=1,
        max_length=100,
        description="List of credential issuance requests",
    )


class BatchIssueStatus(BaseModel):
    """Status of a single batch issuance."""

    index: int = Field(description="Request index")
    success: bool = Field(description="Whether issuance succeeded")
    fields: CredentialFields | None = Field(default=None, description="Issued credential (if successful)")
    error: str | None = Field(default=None, description="Error message (if failed)")


class BatchIssueResponse(BaseModel):
    """Response from batch issuance."""

    statuses: list[BatchIssueStatus] = Field(description="Per-request statuses")
