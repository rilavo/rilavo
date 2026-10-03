"""Pydantic models for error responses."""

from typing import Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail."""

    code: str = Field(description="Reason code")
    message: str = Field(description="Human-readable message")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(description="Reason code")
    detail: Optional[str] = Field(default=None, description="Human-readable message")
