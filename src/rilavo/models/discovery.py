"""Pydantic models for discovery."""

from typing import Optional
from pydantic import BaseModel, Field


class DiscoveryResponse(BaseModel):
    """Well-known discovery response."""

    issuer: str = Field(description="Issuer identifier")
    directory_url: str = Field(description="Key directory URL")
    revocation_url: str = Field(description="Revocation log URL")
    issuer_metadata_url: Optional[str] = Field(default=None, description="Issuer metadata URL")
    jwks_url: Optional[str] = Field(default=None, description="JWKS URL")
