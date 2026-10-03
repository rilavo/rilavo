"""Pydantic models for OpenAPI schema generation."""

from .issue import *
from .verify import *
from .directory import *
from .errors import *
from .discovery import *

__all__ = [
    # Issue
    "IssueCredentialRequest",
    "IssueCredentialResponse",
    "BatchIssueRequest",
    "BatchIssueResponse",
    # Verify
    "VerifyRequest",
    "VerifyResponse",
    # Directory
    "DirectoryEntry",
    "DirectoryResponse",
    # Revoke
    "RevokeRequest",
    "RevokeResponse",
    # Errors
    "ErrorResponse",
    "ErrorDetail",
    # Discovery
    "DiscoveryResponse",
]
