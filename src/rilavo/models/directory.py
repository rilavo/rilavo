"""Pydantic models for key directory."""

from pydantic import BaseModel, Field


class DirectoryEntry(BaseModel):
    """Key directory entry."""

    issuer_id: str = Field(description="Issuer fingerprint")
    public_key_pem: str = Field(description="Issuer public key (PEM format)")
    valid_until: int = Field(description="Validity cutoff (Unix timestamp)")


class DirectoryResponse(BaseModel):
    """Directory response."""

    entries: list = Field(description="List of directory entries")
