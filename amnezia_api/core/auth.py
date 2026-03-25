from __future__ import annotations

from fastapi import Header, HTTPException, status

from amnezia_api.core.config import get_settings


def require_bearer_token(authorization: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
        )

    if authorization != f"Bearer {settings.api_token}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
