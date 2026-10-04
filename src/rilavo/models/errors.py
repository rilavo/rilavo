"""Pydantic models for error responses."""


from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail."""

    code: str = Field(description="Reason code")
    message: str = Field(description="Human-readable message")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(description="Reason code")
    detail: str | None = Field(default=None, description="Human-readable message")
