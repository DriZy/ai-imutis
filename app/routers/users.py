"""User management and device/session tracking endpoints."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..dependencies import AuthenticatedUser, get_current_user
from ..models import DeviceSession as DeviceSessionModel, User
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


async def _get_or_create_user(db: AsyncSession, user: AuthenticatedUser) -> User:
    existing = await db.get(User, user.uid)
    if existing:
        return existing
    new_user = User(uid=user.uid, email=user.email, role=user.role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/auth/verify-token", response_model=VerifyTokenResponse)
async def verify_token(user: AuthenticatedUser = Depends(get_current_user)) -> VerifyTokenResponse:
    """Return token verification result (placeholder)."""

    return VerifyTokenResponse(uid=user.uid, role=user.role)


@router.get("/users/profile", response_model=UserProfile)
async def get_profile(
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """Return user profile metadata."""

    record = await _get_or_create_user(db, user)
    return UserProfile(
        uid=record.uid,
        email=record.email,
        role=record.role,
        display_name=record.display_name,
        language=record.language,
        notification_enabled=record.notification_enabled,
    )


@router.put("/users/profile", response_model=UserProfile)
async def update_profile(
    payload: UpdateUserProfileRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """Update profile fields."""

    record = await _get_or_create_user(db, user)
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    await db.commit()
    await db.refresh(record)
    return UserProfile(
        uid=record.uid,
        email=record.email,
        role=record.role,
        display_name=record.display_name,
        language=record.language,
        notification_enabled=record.notification_enabled,
    )


@router.delete("/users/account", response_model=MessageResponse)
async def delete_account(
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete user account (demo: mark as deleted)."""

    record = await db.get(User, user.uid)
    if record:
        await db.delete(record)
        await db.commit()
    return MessageResponse(message="Account deletion scheduled")


@router.post("/users/preferences", response_model=MessageResponse)
async def save_preferences(
    payload: UserPreferenceRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Persist user preferences."""

    record = await _get_or_create_user(db, user)
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    await db.commit()
    return MessageResponse(message="Preferences updated")


@router.get("/users/sessions", response_model=DeviceSessionList)
async def list_sessions(
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DeviceSessionList:
    """Return active device sessions for the authenticated user."""

    await _get_or_create_user(db, user)
    result = await db.execute(
        select(DeviceSessionModel).where(DeviceSessionModel.user_id == user.uid)
    )
    sessions = [
        DeviceSession(
            session_id=s.id,
            device_ip=s.device_ip,
            device_type=s.device_type,
            device_os=s.device_os,
            session_start=s.session_start,
            last_activity=s.last_activity,
            is_active=s.is_active,
            ip_rotation_detected=s.ip_rotation_detected,
        )
        for s in result.scalars().all()
    ]
    return DeviceSessionList(sessions=sessions)


@router.delete("/users/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Revoke a session by id."""

    await _get_or_create_user(db, user)
    session = await db.get(DeviceSessionModel, session_id)
    if not session or session.user_id != user.uid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    await db.delete(session)
    await db.commit()
    return MessageResponse(message="Session revoked")


@router.post("/users/locations/track", response_model=LocationTrackResponse)
async def track_location(
    payload: LocationTrackRequest,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LocationTrackResponse:
    """Record current location with device IP."""

    device_ip = getattr(request.state, "device_ip", request.client.host)
    await _get_or_create_user(db, user)

    session_record = DeviceSessionModel(
        user_id=user.uid,
        device_ip=device_ip,
        device_type=payload.activity_type,
        device_os=None,
        session_start=datetime.utcnow(),
        last_activity=datetime.utcnow(),
    )
    db.add(session_record)
    await db.commit()
    await db.refresh(session_record)

    return LocationTrackResponse(
        location_id=session_record.id,
        device_ip=device_ip,
        recorded_at=session_record.session_start,
    )
