"""User management and device/session tracking endpoints."""
from datetime import datetime
from typing import Dict
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request

from .. import data
from ..dependencies import AuthenticatedUser, get_current_user
from ..schemas.common import MessageResponse
from ..schemas.users import (
    DeviceSession,
    DeviceSessionList,
    LocationTrackRequest,
    LocationTrackResponse,
    UpdateUserProfileRequest,
    UserPreferenceRequest,
    UserProfile,
    VerifyTokenResponse,
)

router = APIRouter(prefix="/api", tags=["User"])

# In-memory user profiles for demo
_user_profiles: Dict[str, UserProfile] = {}


def _get_or_create_profile(user: AuthenticatedUser) -> UserProfile:
    if user.uid not in _user_profiles:
        _user_profiles[user.uid] = UserProfile(uid=user.uid, email=user.email, role=user.role)
    return _user_profiles[user.uid]


@router.post("/auth/verify-token", response_model=VerifyTokenResponse)
async def verify_token(user: AuthenticatedUser = Depends(get_current_user)) -> VerifyTokenResponse:
    """Return token verification result (placeholder)."""

    return VerifyTokenResponse(uid=user.uid, role=user.role)


@router.get("/users/profile", response_model=UserProfile)
async def get_profile(user: AuthenticatedUser = Depends(get_current_user)) -> UserProfile:
    """Return user profile metadata."""

    return _get_or_create_profile(user)


@router.put("/users/profile", response_model=UserProfile)
async def update_profile(
    payload: UpdateUserProfileRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> UserProfile:
    """Update profile fields."""

    profile = _get_or_create_profile(user)
    update_data = payload.dict(exclude_unset=True)
    updated = profile.copy(update=update_data)
    _user_profiles[user.uid] = updated
    return updated


@router.delete("/users/account", response_model=MessageResponse)
async def delete_account(user: AuthenticatedUser = Depends(get_current_user)) -> MessageResponse:
    """Delete user account (demo: mark as deleted)."""

    if user.uid in _user_profiles:
        del _user_profiles[user.uid]
    return MessageResponse(message="Account deletion scheduled")


@router.post("/users/preferences", response_model=MessageResponse)
async def save_preferences(
    payload: UserPreferenceRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> MessageResponse:
    """Persist user preferences (in-memory demo)."""

    profile = _get_or_create_profile(user)
    update_data = payload.dict(exclude_unset=True)
    updated = profile.copy(update=update_data)
    _user_profiles[user.uid] = updated
    return MessageResponse(message="Preferences updated")


@router.get("/users/sessions", response_model=DeviceSessionList)
async def list_sessions(user: AuthenticatedUser = Depends(get_current_user)) -> DeviceSessionList:
    """Return active device sessions for the authenticated user."""

    sessions = [DeviceSession(**s) for s in data.sessions]
    return DeviceSessionList(sessions=sessions)


@router.delete("/users/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
) -> MessageResponse:
    """Revoke a session by id."""

    before = len(data.sessions)
    data.sessions[:] = [s for s in data.sessions if s["session_id"] != session_id]
    if len(data.sessions) == before:
        raise HTTPException(status_code=404, detail="Session not found")
    return MessageResponse(message="Session revoked")


@router.post("/users/locations/track", response_model=LocationTrackResponse)
async def track_location(
    payload: LocationTrackRequest,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
) -> LocationTrackResponse:
    """Record current location with device IP."""

    device_ip = getattr(request.state, "device_ip", request.client.host)
    location_id = str(uuid.uuid4())
    return LocationTrackResponse(
        location_id=location_id,
        device_ip=device_ip,
        recorded_at=datetime.utcnow(),
    )
