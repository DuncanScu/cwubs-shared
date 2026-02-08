from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from log_config import get_logger

logger = get_logger(__name__)
security = HTTPBearer()


def get_jwt_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict:
    """
    FastAPI dependency that decodes the JWT token and returns the payload.

    This function assumes the JWT has already been verified by an API gateway.
    It simply decodes the token (without verification) and returns the payload.
    """
    token = credentials.credentials

    try:
        # Decode JWT without verification (gateway has already verified it)
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload

    except jwt.DecodeError as e:
        logger.warning("Failed to decode JWT token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT format",
        )


def get_current_clerk_id(
    payload: Annotated[dict, Depends(get_jwt_payload)],
) -> str:
    """
    FastAPI dependency that extracts the Clerk ID from a JWT token.

    This function assumes the JWT has already been verified by an API gateway.
    It simply decodes the token (without verification) and extracts the clerk_id from the 'sub' claim.

    Usage in routes:
        @router.get("/users/me")
        def get_current_user(clerk_id: str = Depends(get_current_clerk_id)):
            # clerk_id is the authenticated user's Clerk ID
            ...
    """
    # Extract the Clerk ID from the 'sub' claim
    clerk_id = payload.get("sub")
    if not clerk_id:
        logger.warning("JWT token missing 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT missing 'sub' claim",
        )

    logger.debug("Successfully extracted clerk_id from JWT", clerk_id=clerk_id)
    return clerk_id


