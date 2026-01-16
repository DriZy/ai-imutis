"""Shared dependencies for the FastAPI application."""
from dataclasses import dataclass
import json
from typing import Optional

import firebase_admin
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth, credentials as firebase_credentials

from .config import get_settings

security = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    """Representation of an authenticated Firebase user."""

    uid: str
    email: Optional[str] = None
    role: str = "standard"


def _get_firebase_app() -> firebase_admin.App:
    """Return initialized Firebase app or raise if misconfigured."""

    try:
        return firebase_admin.get_app()
    except ValueError:
        settings = get_settings()
        if settings.firebase_service_account_json:
            try:
                service_account_dict = json.loads(settings.firebase_service_account_json)
            except json.JSONDecodeError as exc:
                raise RuntimeError("Invalid FIREBASE_SERVICE_ACCOUNT_JSON") from exc
            cred = firebase_credentials.Certificate(service_account_dict)
        else:
            # Fall back to Application Default Credentials when available
            cred = firebase_credentials.ApplicationDefault()

        options = {"projectId": settings.firebase_project_id} if settings.firebase_project_id else None
        return firebase_admin.initialize_app(cred, options)


def _decode_firebase_token(token: str) -> AuthenticatedUser:
    """Decode and validate a raw Firebase ID token string."""

    try:
        decoded = firebase_auth.verify_id_token(token, app=_get_firebase_app(), check_revoked=True)
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ID token")
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except firebase_auth.RevokedIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")
    except firebase_auth.CertificateFetchError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth temporarily unavailable")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to verify token")

    uid = decoded.get("uid") or decoded.get("sub")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token payload")

    role = decoded.get("role") or decoded.get("claims", {}).get("role") or "standard"
    email = decoded.get("email")

    return AuthenticatedUser(uid=uid, email=email, role=role)


async def verify_token_string(token: str) -> AuthenticatedUser:
    """Public helper to validate a bearer token string."""

    return _decode_firebase_token(token)


async def verify_firebase_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> AuthenticatedUser:
    """Validate Firebase ID token using Firebase Admin SDK."""

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    token = credentials.credentials
    return _decode_firebase_token(token)


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
