"""API-key authentication for the chat endpoints."""

import os
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(provided: str | None = Security(API_KEY_HEADER)) -> None:
    """Allow the request only with an ``X-API-Key`` header matching the ``API_KEY`` env var."""
    expected = os.environ.get("API_KEY")
    if not expected:  # misconfigured server: refuse rather than run unauthenticated
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "API key is not configured")
    if provided is None or not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or missing API key",
            headers={"WWW-Authenticate": "API-Key"},
        )
