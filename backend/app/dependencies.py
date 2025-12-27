"""Shared dependencies for the FastAPI application."""
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import get_settings

security = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    """Simple representation of an authenticated Firebase user."""

    uid: str
    email: Optional[str] = None
    role: str = "standard"


async def verify_firebase_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> AuthenticatedUser:
    """Validate Firebase ID token.

    This implementation intentionally keeps token verification lightweight for local
    development. In production, integrate the Firebase Admin SDK to verify the token
    signature, issuer, audience, and token revocation.
    """

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    token = credentials.credentials

    # Placeholder logic: accept any non-empty bearer token for now.
    # Replace with firebase_admin.auth.verify_id_token(token) in production.
    # Include custom claims (e.g., role) from the decoded token.
    role = "admin" if token.endswith("-admin") else "premium" if token.endswith("-pro") else "standard"
    uid = token[:32] if len(token) >= 6 else "demo-user"

    return AuthenticatedUser(uid=uid, email=None, role=role)


async def get_current_user(user: AuthenticatedUser = Depends(verify_firebase_token)) -> AuthenticatedUser:
    """Expose authenticated user dependency."""

    return user


async def get_rate_limit_identifier(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """Return identifier for rate limiting (user id when authenticated, else IP)."""

    if credentials and credentials.credentials:
        try:
            user = await verify_firebase_token(credentials)
            return user.uid
        except HTTPException:
            # Fallback to IP if the token is invalid
            pass

    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    return client_ip or "anonymous"
